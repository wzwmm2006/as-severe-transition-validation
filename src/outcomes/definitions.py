"""Outcome code definitions retained from the frozen supportive analysis."""


def is_principal_hf(code: str, version: str, sequence: str) -> bool:
    code = code.strip().upper()
    return sequence.strip() == "1" and ((version == "9" and code.startswith("428")) or
                                         (version == "10" and code.startswith("I50")))


def competing_event(valve_days, death_days, censor_days):
    """Return (time, cause): 1 valve intervention, 2 death, 0 censoring."""
    if valve_days is not None and valve_days <= censor_days and (death_days is None or valve_days <= death_days):
        return valve_days, 1
    if death_days is not None and death_days <= censor_days:
        return death_days, 2
    return max(censor_days, 0), 0

