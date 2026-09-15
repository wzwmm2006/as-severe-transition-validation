from _common import arguments, emit
from pipeline import cohort

args=arguments("Build the frozen native-valve moderate-AS cohort")
result=cohort(args.config)["result"]
emit({k:result[k] for k in ("adult_eligible_tte_n","native_qualifying_n","native_with_subsequent_tte_n")})

