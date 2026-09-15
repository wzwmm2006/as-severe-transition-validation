from _common import arguments, emit
from pipeline import cohort

args=arguments("Identify each patient's first severe-range transition")
result=cohort(args.config)["result"]
emit({k:result[k] for k in ("native_qualifying_n","first_severe_transition_n","same_study_concordant_n")})

