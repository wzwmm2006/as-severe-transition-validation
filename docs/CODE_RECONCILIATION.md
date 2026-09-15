# Public-code reconciliation

Date: 2026-09-15

The public aggregate-only pipeline was run against authorized local copies of MIMIC-IV-Echo v1.0.1 and linked MIMIC-IV hospital data. The configuration and execution output remained outside the repository.

| Checkpoint | Public code | Frozen reference | Status |
|---|---:|---:|---|
| Original qualifying cohort | 813 | 813 | Exact |
| Original first severe-range transition | 175 | 175 | Exact |
| Original evaluable confirmation | 77 | 77 | Exact |
| Original confirmed | 29 | 29 | Exact |
| Prior-valve exclusions | 142 | 142 | Exact |
| Native qualifying cohort | 671 | 671 | Exact |
| First severe-range transition | 150 | 150 | Exact |
| Same-study concordant | 22 | 22 | Exact |
| Evaluable confirmation | 62 | 62 | Exact |
| Confirmed | 26 | 26 | Exact |
| AVA persistence | 23/46 | 23/46 | Exact |
| Peak-velocity persistence | 2/11 | 2/11 | Exact |
| Mean-gradient persistence | 1/9 | 1/9 | Exact |
| Schema A | 13/35 | 13/35 | Exact |
| Schema B | 13/27 | 13/27 | Exact |
| Mortality, confirmed | 0.434615 | 0.434615 | Within 5×10⁻⁶ |
| Mortality, non-confirmed | 0.369408 | 0.369408 | Within 5×10⁻⁶ |
| Unadjusted mortality HR | 1.430064 | 1.430064 | Within 5×10⁻⁶ |
| Adjusted mortality HR | 1.096312 | 1.096312 | Within 5×10⁻⁶ |
| AVR/TAVR CIF, confirmed | 0.278846 | 0.278846 | Within 5×10⁻⁶ |
| AVR/TAVR CIF, non-confirmed | 0.060606 | 0.060606 | Within 5×10⁻⁶ |
| Principal-HF hospitalization, confirmed | 2 | 2 | Exact |
| Principal-HF hospitalization, non-confirmed | 5 | 5 | Exact |

Verdict: `PUBLIC_CODE_RECONCILIATION_PASS`.

No scientific threshold, cohort rule, confirmation window, outcome, or statistical method was changed during reconciliation.
