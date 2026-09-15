"""Frozen cohort and transition definitions used by Paper C.

The functions are deliberately small and side-effect free so the same rules can
be tested with synthetic records and applied to authorized local data.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Iterable

FAMILIES = ("lvef", "lvef_upper", "biplane_lvef", "lvef_3d")
SEVERE_LIMITS = {"ava": 1.0, "vmax": 4.0, "mg": 40.0}
CONFIRMATION_MIN_DAYS = 30
CONFIRMATION_MAX_DAYS = 365


def is_moderate_baseline(exam: dict) -> bool:
    x = exam["x"]
    ava, lvef = x.get("ava"), x.get("lvef")
    if lvef is None or ava is None or not (lvef < 50 and 1.0 < ava <= 1.5):
        return False
    return (x.get("vmax") is None or x["vmax"] < 4.0) and (x.get("mg") is None or x["mg"] < 40.0)


def severe_flags(exam: dict) -> dict[str, bool]:
    x = exam["x"]
    return {
        "AVA": x.get("ava") is not None and x["ava"] <= 1.0,
        "Vmax": x.get("vmax") is not None and x["vmax"] >= 4.0,
        "MG": x.get("mg") is not None and x["mg"] >= 40.0,
    }


def evaluable(exam: dict) -> bool:
    return any(key in exam["x"] for key in ("ava", "vmax", "mg"))


def concordant(flags: dict[str, bool]) -> bool:
    return sum(flags.values()) >= 2 and (flags["Vmax"] or flags["MG"])


def first_baselines(exams_by_patient: dict[str, list[dict]]) -> dict[str, dict]:
    out = {}
    for patient, exams in exams_by_patient.items():
        for exam in exams:
            if exam.get("age") is not None and exam["age"] >= 18 and is_moderate_baseline(exam):
                out[patient] = exam
                break
    return out


def first_transitions(baselines: dict[str, dict], exams_by_patient: dict[str, list[dict]]) -> dict[str, tuple]:
    out = {}
    for patient, baseline in baselines.items():
        for exam in exams_by_patient[patient]:
            if exam["dt"] <= baseline["dt"]:
                continue
            flags = severe_flags(exam)
            if any(flags.values()):
                out[patient] = (baseline, exam, flags)
                break
    return out


def first_confirmations(transitions: dict[str, tuple], exams_by_patient: dict[str, list[dict]]) -> dict[str, tuple]:
    out = {}
    for patient, (_, index, flags) in transitions.items():
        for exam in exams_by_patient[patient]:
            days = (exam["dt"] - index["dt"]).days
            if days < CONFIRMATION_MIN_DAYS:
                continue
            if days > CONFIRMATION_MAX_DAYS:
                break
            if evaluable(exam):
                out[patient] = (index, exam, days, flags)
                break
    return out


def sort_exams(exams: Iterable[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for exam in exams:
        grouped[exam["patient_key"]].append(exam)
    for values in grouped.values():
        values.sort(key=lambda exam: (exam["dt"], exam["study_key"]))
    return dict(grouped)


def exclude_prior_valve(baselines: dict[str, dict], transitions: dict[str, tuple], procedures: dict[str, list[dict]]) -> set[str]:
    """Calendar-date native-valve rule; same-day procedures remain ambiguous."""
    excluded = set()
    for patient, baseline in baselines.items():
        index = transitions.get(patient, (None, None, None))[1]
        for procedure in procedures.get(patient, []):
            if procedure["class"] not in {"SAVR", "TAVR"} or procedure.get("dt") is None:
                continue
            day = procedure["dt"].date()
            if day < baseline["dt"].date() or (index is not None and baseline["dt"].date() <= day < index["dt"].date()):
                excluded.add(patient)
                break
    return excluded


def avr_class(code: str, version: str) -> str | None:
    code = code.strip().upper()
    if version == "9":
        if code in ("3505", "3506"):
            return "TAVR"
        if code in ("3521", "3522"):
            return "SAVR"
        return None
    if code.startswith("02RF0"):
        return "SAVR"
    if code.startswith("02RF3") or code.startswith("02RF4"):
        return "TAVR"
    if code.startswith("X2RF"):
        return "SAVR" if code.endswith("032") else "TAVR"
    return None

