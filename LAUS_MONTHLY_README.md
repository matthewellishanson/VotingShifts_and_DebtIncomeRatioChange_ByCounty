# BLS county monthly data: August 2025–September 2026

This uploaded ZIP contains actual 2026 monthly data, not an annual equivalent or forecast.
All 105 Kansas counties and 115 Missouri county equivalents are represented in each of 14 months.
October 2025 is unavailable for every KS/MO county; retain its blank observations.
September 2026 is marked preliminary. The workbook footer date is October 28, 2026.

## Install and run

The monthly source workbook and converted source table are integrated alongside the annual panel.
To rebuild the ignored prepared outputs in PowerShell from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_laus_monthly.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_laus_monthly.py -v
```

No Office subscription or additional Python packages are needed. Both Python scripts must remain
together in `scripts/`. The bundled `laus_xlsx_reader.py` reuses the annual converter's OOXML
reader/validation helpers under a separate filename, making this add-on independently runnable.
The adapter targets this supplied workbook layout and date window; review it before using a future rolling release.

## Files

| Path | Contents |
|---|---|
| `data/processed/laus_monthly/county_monthly_ks_mo.csv` | 3,080 county/month rows: 2,860 available plus 220 October 2025 placeholders |
| `data/processed/laus_monthly/county_same_month_change_2025_2026_ks_mo.csv` | 440 matched comparisons: August and September 2025 versus their respective 2026 months |
| `data/processed/laus_monthly/county_monthly_all_source_areas.csv` | All 45,094 national source-area/month rows, including Puerto Rico |
| `data/processed/laus_monthly/coverage_by_month.csv` | Coverage and missingness by state/month |
| `data/processed/laus_monthly/quality_report.md` | Validation results and limitations |
| `data/processed/laus_monthly/manifest.json` | Source hash, titles/footnotes, conversion hash, validation details |
| `data/raw/bls_laus_monthly/` | Unchanged extracted XLSX and national nine-column CSV |
| `data/archives/bls-laus-monthly-laucntycur14.zip` | Ignored immutable backup of the original ZIP; its only member is byte-identical to the tracked XLSX |

The original CSV retains dash missing-value markers and `p` labels in Period.
The normalized panels use `period` in YYYY-MM format, `preliminary` True/False and `data_status`.
Missing measures are blank, not zero. Rates are percentages at one decimal place, not fractions.
`county_fips` is a five-character string; `state_fips` and `county_fips_component` preserve the original parts.
Other fields include resident labor force, employed, unemployed, county name, LAUS code and source row.
`geographic_basis=place_of_residence`; counts measure residents, not workplace jobs.

## What to compare

Use September 2026 as the latest supplied pre-election snapshot, clearly marked preliminary.
Use the supplied August-to-August and September-to-September changes as initial descriptive measures.
All observations are **not seasonally adjusted**, so avoid interpreting January-to-September changes as pure trends.
Do not compare a September 2026 observation directly with a 2024 annual average and call it a matched election-period shift.

Unemployment-rate change is in percentage points: 3.0% to 3.8% = +0.8 points.
Employment/labor-force differences are changes in average persons, not jobs created or layoffs.
No changes are computed across the missing October observations. Do not interpolate October for publication.
Lower unemployment can coincide with a shrinking labor force; inspect employment and labor-force changes too.

You still need monthly 2024 data and January–July 2025 for a consistent longer baseline.
This workbook has no October/November 2026 observations or full-year 2026 average.
Keep the annual series separate; do not append monthly values into its annual `year` key.
For map/election joins, choose the comparison first and join by five-character county FIPS.
Correlations are descriptive; they cannot establish administration effects or individual voting motives.

## Git and next Codex task

The original ZIP is retained locally under `data/archives/` but is not committed because it contains only the byte-identical tracked XLSX. Its filename, SHA-256 and relationship to the extracted workbook are documented in `data/archives/README.md`.

Suggested staging, subject to your project's existing ignore rules:

```powershell
git add LAUS_MONTHLY_README.md scripts/prepare_laus_monthly.py scripts/laus_xlsx_reader.py tests/test_laus_monthly.py data/raw/bls_laus_monthly
git diff --cached --stat
```

Processed outputs can remain ignored and be regenerated. No commit or push is performed by the scripts.

Codex: Run the monthly converter and tests, inspect coverage/period/status fields, and add a research
option for September 2026 levels and matched August/September year-over-year changes. Preserve the
preliminary label, missing October 2025 and original nationwide data. Keep monthly and annual
panels separate. Obtain the missing 2024 monthly baseline in a later acquisition step before
presenting this as a 2024–2026 change measure. Do not alter election calculations or publish automatically.

Official source index: https://www.bls.gov/lau/tables.htm
