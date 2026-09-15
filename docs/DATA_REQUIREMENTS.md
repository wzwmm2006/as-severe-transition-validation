# Data requirements

Authorized users need MIMIC-IV-Echo v1.0.1 `structured-measurement.csv.gz` and the linked MIMIC-IV hospital tables `patients.csv.gz`, `admissions.csv.gz`, and `procedures_icd.csv.gz`. The input paths are configured locally and must remain outside this repository.

Required echo fields include the examination identifier, patient linkage identifier, examination datetime, test type, measurement name, and result. Required hospital fields include age anchors, sex, date of death, admission discharge/death times, ICD procedure code/version, and procedure date.

Restricted identifiers are used only in memory to link authorized tables. They are never written by the public pipeline.

