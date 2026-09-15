from _common import arguments, emit
from pipeline import cohort

args=arguments("Estimate longitudinal confirmation at first evaluable follow-up")
result=cohort(args.config)["result"]
emit({k:result[k] for k in ("confirmation_evaluable_n","confirmation_confirmed_n","confirmation_rate","confirmation_ci95","parameter_persistence","reporting_schema")})

