# Reproducibility

## Execution order

1. Install the pinned environment.
2. Obtain credentialed MIMIC-IV and MIMIC-IV-Echo access.
3. Copy and edit `config/example_config.yaml` outside the repository.
4. Run `scripts/01_build_cohort.py`.
5. Apply native-valve exclusions as part of cohort construction.
6. Run `scripts/02_identify_first_severe_transition.py`.
7. Run `scripts/03_longitudinal_confirmation.py`.
8. Inspect longitudinal confirmation and parameter persistence aggregates.
9. Run `scripts/04_supportive_outcomes.py`.
10. Run `scripts/05_generate_manuscript_outputs.py` to write the complete aggregate JSON.

## Expected checkpoints

The final command stops with `PUBLIC_CODE_RECONCILIATION_FAIL` if these exact checkpoints are not met:

- 671 qualifying native-valve patients
- 150 first severe-range transitions
- 22 concordant transitions
- 62 evaluable follow-up examinations
- 26 confirmed transitions

Expected parameter, schema, and supportive outcome values are recorded in `results/aggregate_reference_outputs/expected_results.json`. A discrepancy should be investigated as a data-version, configuration, or migration issue. Scientific definitions must not be changed to force agreement.

The pipeline writes no row-level tables. Users should nevertheless keep the entire configured output directory outside the Git working tree.

