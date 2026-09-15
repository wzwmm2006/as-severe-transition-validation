# Data policy

MIMIC-IV and MIMIC-IV-Echo are credentialed-access datasets distributed through PhysioNet. This public repository contains no source data and no patient-level derived data. Users must obtain access independently, complete the required training, and comply with the applicable PhysioNet data-use agreement. The authors do not redistribute restricted data.

All patient-level extracts and intermediate outputs must be written outside this repository. The example configuration deliberately points to placeholder locations. Aggregate files may be committed only when they contain no identifiers, dates, row-level records, or small-cell information and have been manually reviewed.

The MIT licence applies only to repository code and documentation. It does not apply to MIMIC-IV or MIMIC-IV-Echo.

## Files that must never be committed

- Source or extracted MIMIC files
- Patient-, admission-, stay-, examination-, procedure-, or event-level records
- `*.csv`, `*.tsv`, `*.parquet`, `*.feather`, `*.pkl`, `*.pickle`
- `*.db`, `*.sqlite`, `*.sqlite3`, `*.duckdb`
- Raw extracts, cached data, temporary outputs, and logs containing identifiers
- `.env`, credentials, access tokens, API keys, or data-use certificates
- Screenshots or notebooks containing patient-level values or dates

The `.gitignore` blocks these formats by default. A safe aggregate file should use JSON or Markdown and must be reviewed before staging.

