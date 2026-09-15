"""Aggregate-only public execution of the frozen Paper C analysis."""
from __future__ import annotations

import csv, gzip, json, math, re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from cohort.logic import (avr_class, concordant, exclude_prior_valve, first_baselines,
                          first_confirmations, first_transitions, severe_flags, sort_exams)
from outcomes.definitions import competing_event, is_principal_hf
from reporting.aggregate import assert_checkpoints, write_aggregate_json
from statistics.estimators import aalen_johansen, cox_efron, km_survival, wilson


def numeric(value):
    match = re.search(r"[-+]?\d+(?:\.\d+)?", (value or "").strip())
    return float(match.group()) if match else None


def rows(path):
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle)


def resolve(config_path):
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    hospital = Path(config["mimic_iv_path"])
    if (hospital / "hosp").is_dir():
        hospital = hospital / "hosp"
    echo = Path(config["mimic_iv_echo_path"])
    return config, hospital, echo


def load(config_path):
    config, hospital, echo = resolve(config_path)
    patient_table = {r["subject_id"]: r for r in rows(hospital / "patients.csv.gz")}
    exams = {}
    for r in rows(echo / "structured-measurement.csv.gz"):
        if (r.get("test_type") or "").lower() != "tte":
            continue
        key = r["measurement_id"]
        exam = exams.setdefault(key, {"study_key": key, "patient_key": r["subject_id"],
                                     "dt": datetime.fromisoformat(r["measurement_datetime"]), "x": {}})
        measure, value = r["measurement"], numeric(r.get("result"))
        if measure == "av_area_continuity": exam["x"]["ava"] = value
        elif measure == "av_pk_vel": exam["x"]["vmax"] = value
        elif measure == "av_mean_grad": exam["x"]["mg"] = value
        elif measure == "lvef" and value is not None: exam["x"]["lvef"] = value
        elif measure == "height_cm": exam["schema"] = "A"
        elif measure == "gender": exam["schema"] = "B"
    for exam in exams.values():
        patient = patient_table.get(exam["patient_key"])
        exam["age"] = None if patient is None else int(patient["anchor_age"]) + exam["dt"].year - int(patient["anchor_year"])
    return config, hospital, patient_table, exams, sort_exams(exams.values())


def cohort(config_path):
    config, hospital, patients, exams, by_patient = load(config_path)
    baseline_all = first_baselines(by_patient)
    transition_all = first_transitions(baseline_all, by_patient)
    confirmation_all = first_confirmations(transition_all, by_patient)
    procedures = defaultdict(list)
    for r in rows(hospital / "procedures_icd.csv.gz"):
        if r["subject_id"] not in baseline_all:
            continue
        kind = avr_class(r["icd_code"], r["icd_version"])
        if kind:
            procedures[r["subject_id"]].append({"dt": datetime.fromisoformat(r["chartdate"]) if r["chartdate"] else None,
                                                 "class": kind})
    excluded = exclude_prior_valve(baseline_all, transition_all, procedures)
    native_exams = {key: value for key, value in by_patient.items() if key not in excluded}
    baseline = first_baselines(native_exams)
    transitions = first_transitions(baseline, native_exams)
    confirmations = first_confirmations(transitions, native_exams)
    confirmed = {key for key, value in confirmations.items() if any(severe_flags(value[1]).values())}
    result = {
        "adult_eligible_tte_n": sum(e["age"] is not None and e["age"] >= 18 for e in exams.values()),
        "original_qualifying_n": len(baseline_all),
        "original_first_severe_transition_n": len(transition_all),
        "original_confirmation_evaluable_n": len(confirmation_all),
        "original_confirmation_confirmed_n": sum(any(severe_flags(value[1]).values()) for value in confirmation_all.values()),
        "prior_valve_excluded_n": len(excluded),
        "native_qualifying_n": len(baseline),
        "native_with_subsequent_tte_n": sum(any(e["dt"] > b["dt"] for e in native_exams[key]) for key, b in baseline.items()),
        "first_severe_transition_n": len(transitions),
        "same_study_concordant_n": sum(concordant(value[2]) for value in transitions.values()),
        "confirmation_evaluable_n": len(confirmations),
        "confirmation_confirmed_n": len(confirmed),
        "confirmation_rate": len(confirmed) / len(confirmations),
    }
    result["confirmation_ci95"] = list(wilson(len(confirmed), len(confirmations)))
    persistence = {}
    for flag, field in (("AVA", "ava"), ("Vmax", "vmax"), ("MG", "mg")):
        eligible = [value for value in confirmations.values() if value[3][flag] and value[1]["x"].get(field) is not None]
        persistence["mean_gradient" if field == "mg" else field] = [sum(severe_flags(value[1])[flag] for value in eligible), len(eligible)]
    result["parameter_persistence"] = persistence
    result["reporting_schema"] = {}
    for schema in ("A", "B"):
        group = [value for value in confirmations.values() if value[1].get("schema") == schema]
        result["reporting_schema"][schema] = [sum(any(severe_flags(value[1]).values()) for value in group), len(group)]
    state = {"config": config, "hospital": hospital, "patients": patients, "procedures": procedures,
             "baseline": baseline, "transitions": transitions, "confirmations": confirmations,
             "confirmed": confirmed, "result": result}
    return state


def supportive_outcomes(state):
    hospital, patients = state["hospital"], state["patients"]
    confirmations, confirmed = state["confirmations"], state["confirmed"]
    landmark = {key: value[1]["dt"] for key, value in confirmations.items()}
    admissions, last_discharge = defaultdict(list), {}
    for r in rows(hospital / "admissions.csv.gz"):
        key = r["subject_id"]
        if key not in state["baseline"]: continue
        item = {"admission_key": r["hadm_id"],
                "admit": datetime.fromisoformat(r["admittime"]) if r["admittime"] else None,
                "discharge": datetime.fromisoformat(r["dischtime"]) if r["dischtime"] else None,
                "death": datetime.fromisoformat(r["deathtime"]) if r.get("deathtime") else None}
        admissions[key].append(item)
        if item["discharge"] and (key not in last_discharge or item["discharge"] > last_discharge[key]):
            last_discharge[key] = item["discharge"]
    procedure_dates = defaultdict(list)
    for r in rows(hospital / "procedures_icd.csv.gz"):
        key = r["subject_id"]
        if key in landmark and avr_class(r["icd_code"], r["icd_version"]) and r["chartdate"]:
            procedure_dates[key].append(datetime.fromisoformat(r["chartdate"]))
    principal_hf = defaultdict(set)
    for r in rows(hospital / "diagnoses_icd.csv.gz"):
        key, code, version = r["subject_id"], r["icd_code"].strip().upper(), r["icd_version"]
        if key in landmark and is_principal_hf(code, version, r["seq_num"]):
            principal_hf[key].add(r["hadm_id"])

    def death_date(key):
        registry = patients[key].get("dod", "")
        candidates = [datetime.fromisoformat(registry)] if registry else []
        candidates += [r["death"] for r in admissions.get(key, []) if r["death"]]
        return min(candidates, default=None)

    mortality, competing = [], []
    for key, start in landmark.items():
        death, discharge = death_date(key), last_discharge.get(key)
        ascertainment = discharge + timedelta(days=365) if discharge else None
        cap = min([start + timedelta(days=365)] + ([ascertainment] if ascertainment else []))
        cap_days = (cap - start).days
        death_days = (death - start).days if death else None
        event = int(death_days is not None and death_days <= cap_days)
        mortality.append({"group": int(key in confirmed), "time": death_days if event else max(cap_days, 0), "event": event,
                          "age": int(patients[key]["anchor_age"]) + start.year - int(patients[key]["anchor_year"]),
                          "male": int(patients[key]["gender"] == "M")})
        valve = min((d for d in procedure_dates.get(key, []) if d > start), default=None)
        valve_days = (valve - start).days if valve else None
        time, cause = competing_event(valve_days, death_days, cap_days)
        competing.append({"group": int(key in confirmed), "time": time, "cause": cause})
    output = {}
    for label, code in (("confirmed", 1), ("non_confirmed", 0)):
        group = [r for r in mortality if r["group"] == code]
        survival, _ = km_survival([r["time"] for r in group], [r["event"] for r in group])
        output["mortality_" + label] = 1 - survival
        cr = [r for r in competing if r["group"] == code]
        output["avr_tavr_cif_" + label] = aalen_johansen([r["time"] for r in cr], [r["cause"] for r in cr])
        members = confirmed if code == 1 else set(landmark) - confirmed
        output["hf_principal_" + label] = sum(any(a["admission_key"] in principal_hf[key] and a["admit"] and a["admit"] > landmark[key]
                                                       for a in admissions.get(key, [])) for key in members)
    times=[r["time"] for r in mortality]; events=[r["event"] for r in mortality]
    beta=cox_efron(times,events,[[r["group"]] for r in mortality])[0]
    adjusted=cox_efron(times,events,[[r["group"],r["age"],r["male"]] for r in mortality])[0]
    output["mortality_unadjusted_hr"] = math.exp(beta)
    output["mortality_adjusted_hr"] = math.exp(adjusted)
    state["result"]["supportive_outcomes_12_month"] = output
    return state


def run(config_path):
    state = supportive_outcomes(cohort(config_path))
    repository = Path(__file__).resolve().parents[1]
    expected = json.loads((repository / "results/aggregate_reference_outputs/expected_results.json").read_text())
    assert_checkpoints(state["result"], expected)
    output_directory = Path(state["config"]["output_path"]).resolve()
    if repository.resolve() == output_directory or repository.resolve() in output_directory.parents:
        raise RuntimeError("output_path must be outside the public repository")
    destination = output_directory / "aggregate_results.json"
    write_aggregate_json(destination, state["result"])
    return state["result"]
