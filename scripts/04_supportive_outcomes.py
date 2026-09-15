from _common import arguments, emit
from pipeline import cohort, supportive_outcomes

args=arguments("Generate aggregate supportive mortality and AVR/TAVR outcomes")
result=supportive_outcomes(cohort(args.config))["result"]
emit(result["supportive_outcomes_12_month"])

