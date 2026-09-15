"""Aggregate-only reporting and frozen checkpoint validation."""
import json
from pathlib import Path


def write_aggregate_json(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")


def assert_checkpoints(result: dict, expected: dict) -> None:
    keys = (
        "native_qualifying_n", "first_severe_transition_n",
        "same_study_concordant_n", "confirmation_evaluable_n",
        "confirmation_confirmed_n",
    )
    mismatches = {key: (result.get(key), expected[key]) for key in keys if result.get(key) != expected[key]}
    if mismatches:
        raise RuntimeError(f"PUBLIC_CODE_RECONCILIATION_FAIL: {mismatches}")
    exact_nested = ("parameter_persistence", "reporting_schema")
    for key in exact_nested:
        if result.get(key) != expected[key]:
            raise RuntimeError(f"PUBLIC_CODE_RECONCILIATION_FAIL: {key}: {result.get(key)} != {expected[key]}")
    tolerances = {
        "confirmation_rate": 5e-5,
        "confirmation_ci95": 5e-6,
    }
    for key, tolerance in tolerances.items():
        observed, reference = result[key], expected[key]
        values = zip(observed, reference) if isinstance(reference, list) else [(observed, reference)]
        if any(abs(a - b) > tolerance for a, b in values):
            raise RuntimeError(f"PUBLIC_CODE_RECONCILIATION_FAIL: {key}: {observed} != {reference}")
    for key, reference in expected["supportive_outcomes_12_month"].items():
        observed = result["supportive_outcomes_12_month"].get(key)
        if observed is None or abs(observed - reference) > 5e-6:
            raise RuntimeError(f"PUBLIC_CODE_RECONCILIATION_FAIL: {key}: {observed} != {reference}")
