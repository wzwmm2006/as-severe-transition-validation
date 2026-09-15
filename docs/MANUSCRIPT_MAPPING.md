# Manuscript-to-code mapping

| Manuscript result | Code location | Entry point |
|---|---|---|
| Native qualifying cohort (671) | `src/cohort/logic.py`, `src/pipeline.py` | `scripts/01_build_cohort.py` |
| First severe transition (150) and concordance (22) | `src/cohort/logic.py` | `scripts/02_identify_first_severe_transition.py` |
| Confirmed 26/62 and Wilson CI | `src/cohort/logic.py`, `src/statistics/estimators.py` | `scripts/03_longitudinal_confirmation.py` |
| Parameter persistence and schema estimates | `src/pipeline.py` | `scripts/03_longitudinal_confirmation.py` |
| Mortality KM/Cox estimates | `src/pipeline.py`, `src/statistics/estimators.py` | `scripts/04_supportive_outcomes.py` |
| AVR/TAVR cumulative incidence | `src/statistics/estimators.py` | `scripts/04_supportive_outcomes.py` |
| Aggregate manuscript checkpoints | `src/reporting/aggregate.py` | `scripts/05_generate_manuscript_outputs.py` |
| Original-cohort sensitivity (29/77) | `src/pipeline.py` | `scripts/05_generate_manuscript_outputs.py` |
| Principal-HF hospitalization (2/26 and 5/36) | `src/pipeline.py`, `src/outcomes/definitions.py` | `scripts/04_supportive_outcomes.py` |
