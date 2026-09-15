# AS severe-transition validation

Public reproducibility code for **Durability of the First Severe-Range Echocardiographic Transition in Moderate Aortic Stenosis With Left Ventricular Dysfunction**.

The study asks: among adults with native-valve moderate aortic stenosis (AS) and left ventricular (LV) systolic dysfunction, how often is the first severe-range echocardiographic transition concordant at the index examination and subsequently confirmed on an evaluable follow-up echocardiogram? The repository implements the frozen cohort, transition, confirmation, and supportive outcome definitions. It does not contain MIMIC data or patient-level derivatives.

## Primary definitions

- **Moderate-AS qualifying TTE:** AVA >1.0 and ≤1.5 cm²; LVEF <50%; observed peak velocity <4.0 m/s; observed mean gradient <40 mmHg. Missing peak velocity or mean gradient is unavailable, not assumed normal.
- **First severe-range transition:** first later TTE with AVA ≤1.0 cm², peak velocity ≥4.0 m/s, or mean gradient ≥40 mmHg.
- **Same-study concordance:** at least two severe-range criteria, including peak velocity or mean gradient.
- **Longitudinal confirmation:** first evaluable TTE 30–365 days after the transition with at least one AVA, peak velocity, or mean-gradient value. A transition is confirmed when at least one observed parameter remains severe.

## Frozen aggregate results

- Native-valve qualifying cohort: **671**
- First severe-range transitions: **150**
- Same-study concordant: **22**
- Evaluable confirmation: **62**
- Confirmed: **26/62 (41.94%; 95% CI, 30.48–54.33)**
- Parameter persistence: AVA **23/46**; peak velocity **2/11**; mean gradient **1/9**
- Reporting schema: A **13/35**; B **13/27**

## Running the code

1. Obtain credentialed MIMIC-IV and MIMIC-IV-Echo access from PhysioNet.
2. Create an environment from `environment.yml` or install `requirements.txt`.
3. Copy `config/example_config.yaml` outside the repository and set local paths.
4. Run `python scripts/05_generate_manuscript_outputs.py --config /path/to/config.yaml`.

The configured output directory must be outside the repository. Only aggregate JSON is written. See `docs/REPRODUCIBILITY.md` for staged execution and checkpoints.

## Data and licence

The repository contains code, documentation, synthetic tests, and manually reviewed aggregate values only. See `DATA_POLICY.md`. The MIT licence covers repository code; it does not cover MIMIC-IV or MIMIC-IV-Echo data.

Release version: **1.0.0**. This is the manuscript submission release prepared for archival.

Authors: Mingming Zheng and Liang Liu. Corresponding author: Mingming Zheng.

## Citation and archive

- GitHub repository: https://github.com/wzwmm2006/as-severe-transition-validation
- Release: **v1.0.0**
- Zenodo DOI: [10.5281/zenodo.22762152](https://doi.org/10.5281/zenodo.22762152)

The Zenodo DOI identifies the archived software release. No journal article DOI has been assigned.
