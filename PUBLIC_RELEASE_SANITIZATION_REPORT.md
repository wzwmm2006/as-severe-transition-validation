# Public release sanitization report

Audit scope: files staged or eligible for staging in this new repository and the complete local Git object history. Audit date: 2026-09-15.

## Restricted data files found

0. No MIMIC source file, extract, row-level table, cache, database, notebook, screenshot, or log is present.

## Identifiers found

Identifiers in committed data: 0. The strings `subject_id`, `hadm_id`, and MIMIC time-column names occur only in Python source and documentation where they specify the input schema required to join authorized local tables. No identifier values are embedded in code, tests, documentation, or aggregate outputs. Synthetic tests use the literal key `synthetic`.

## Credentials found

0. No `.env`, token, API key, password, credential, or PhysioNet certificate is present.

## Local paths found

0 unsafe absolute paths. The public example uses `/path/to/...` placeholders only. The local reconciliation configuration is stored outside the repository and is not eligible for staging.

## Patient-level outputs found

0. The public pipeline retains linkage keys and dates in memory and writes one aggregate JSON file to a user-configured directory outside the repository.

## Remediation performed

- Installed a deny-by-default `.gitignore` before any analysis code was staged.
- Used JSON rather than CSV for the manually reviewed aggregate reference output.
- Removed patient-specific diagnostic output and row-level export functions from the public pipeline.
- Used artificial records only in unit tests.
- Kept the real-data configuration and reconciliation output outside the repository.
- Inspected tracked paths, all reachable Git objects, and repository integrity with `git fsck`; restricted data have never entered the local Git history.
- Validated `CITATION.cff` against CFF schema version 1.2.0.

## Final verdict

`PUBLIC_RELEASE_SANITIZATION_PASS`

- restricted data files: 0
- patient-level outputs: 0
- identifiers in committed data: 0
- credentials: 0
- unsafe absolute paths: 0
