# BLS county labor-force data: annual CSV add-on

All 18 uploaded workbooks are converted and organized. **Every supplied year contains all 105 Kansas counties and 115 Missouri county equivalents, with complete labor measures.** The series covers **2008–2025**. These are annual averages, except that 2025 KS/MO observations are **11-month averages excluding October**, not full-year averages. No 2026 observations or monthly detail were supplied.

## Install and run

The source workbooks and converted source tables are integrated into the repository. Rebuild the ignored prepared outputs in PowerShell from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_laus_annual.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_laus_annual.py -v
```

No Excel subscription, Node, pandas, openpyxl, API key or new package installation is required. The standard-library script reads the supplied one-sheet XLSX format directly. It rejects unexpected headers, formulas or altered layouts; it is not a general Excel converter.

## Files to use

| Path | Purpose |
|---|---|
| `data/processed/laus_annual/county_annual_ks_mo.csv` | **Main panel: 3,960 rows**, 220 county equivalents × 18 years |
| `data/processed/laus_annual/county_annual_all_source_areas.csv` | Combined normalized panel of **57,962 source-area/year rows**, including areas outside KS/MO and Puerto Rico |
| `data/processed/laus_annual/county_comparison_2024_2025_caveated.csv` | 220 descriptive endpoint comparisons, explicitly flagged 12-month versus 11-month averages |
| `data/processed/laus_annual/coverage_by_year.csv` | County counts and missing-measure checks for each state/year |
| `data/processed/laus_annual/quality_report.md` | Read this before analysis |
| `data/processed/laus_annual/manifest.json` | Detailed input hashes, source titles/dates, footnotes and validation results |
| `data/raw/bls_laus_annual/csv/laucnty08.csv` through `laucnty25.csv` | Individual nationwide converted tables with the original nine column names, useful for later expansion |
| `data/raw/bls_laus_annual/csv/workbook_metadata.json` | Source titles, worksheet names, footer notes and XLSX/converted CSV hashes |
| `data/raw/bls_laus_annual/xlsx/` | All 18 untouched original workbooks |

## Important columns in the normalized panel

| Field | Meaning |
|---|---|
| state, state_fips | State abbreviation and two-character FIPS |
| county_fips | Five-character county-equivalent ID, built from state plus county component |
| county_fips_component | Original three-character county component; not unique nationwide |
| county_name, laus_code | Source geographic name and LAUS area identifier |
| year | Observation year, not source release year |
| labor_force | Average number of resident people employed or unemployed and seeking work under LAUS definitions |
| employed, unemployed | Average resident persons; not payroll jobs, layoffs or cumulative yearly totals |
| unemployment_rate_pct | Published rate in percent, normalized to one decimal place |
| averaging_months | 12 ordinarily; 11 for 2025 outside Puerto Rico |
| period_type, excluded_month | Explicit 2025 caveat (`2025-10` excluded) |
| geographic_basis | place_of_residence |
| seasonal_adjustment | not_seasonally_adjusted |
| data_status | published_estimate or source_unavailable |
| source_file, source_sheet, source_row, source_date_text | Traceback to original workbook and its footer date |

CSV blanks mean unavailable, not zero. The original nine-column converted CSVs preserve source `N.A.` markers; normalized panels use blanks plus status fields. No missing KS/MO values exist in the supplied data. National data retain 78 unavailable Puerto Rico observations for 2020.

Values such as `4.0999999999999996` in XLSX numeric storage are converted to the published `4.1`, not treated as high-precision estimates. Original XLSX bytes remain unchanged. No formulas or charting are added.

## How to use this for the project

1. Use the 2008–2024 series for historical context and pretrend exploration.
2. Retain 2025 as a clearly labeled **11-month average excluding October**.
3. Use the 2024–2025 comparison file only as a caveated descriptive comparison, not a matched full-year estimate of administration effects.
4. Next acquire monthly county LAUS data covering 2024, 2025 and available pre-election months of 2026. Compare matched months/windows and carry missing October 2025 explicitly. Do not reconstruct it from annual averages.
5. Join election data by `county_fips`, choosing the intended year/comparison first. Never directly join all 18 years onto a one-row-per-county election table without a year filter.
6. Preserve existing Missouri election-geography holds; complete BLS data do not resolve the separate Kansas City election-source issue.

`unemployment_rate_difference_pp` uses percentage points: 3.0% → 3.8% is +0.8 pp. Falling unemployment alone is not proof of improvement; inspect employment and labor-force changes too. Do not calculate labor-force participation or employment/population rates without appropriate population denominators.

## Storage and Git

Keep both original workbooks and converted nationwide CSVs. Together, the XLSX inputs are about 4.2 MB; Git LFS is unnecessary at this size. Converted source tables are regenerated, not hand-edited. Suggested staging:

```powershell
git add LAUS_ANNUAL_README.md scripts/prepare_laus_annual.py tests/test_laus_annual.py docs/LAUS_ANNUAL_NOTES.md data/raw/bls_laus_annual
git diff --cached --stat
```

Review before committing/pushing. Your existing ignore rule likely excludes `data/processed/`; those outputs are reproducible. No automatic Git actions are performed.

For alternate output folders:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_laus_annual.py --output-dir data\processed\laus_annual_review
```

## Codex integration task

Read LAUS_ANNUAL_README.md and docs/LAUS_ANNUAL_NOTES.md. Run the annual preparation script and tests. Integrate the county/year panel into research workflows while preserving `averaging_months`, `period_type`, missingness and lineage. Retain all national source tables for expansion. Do not fabricate 2026 values, monthly observations, participation rates or a full-year 2025 average. If visualizing the 2024–2025 difference, visibly label its 12-versus-11-month limitation and do not present it as the final 2024–2026 labor-market proxy. Acquire matched monthly observations as a separate task. Do not alter existing election/debt/mortgage calculations or automatically publish findings.

## Official sources

- BLS tables and county downloads: https://www.bls.gov/lau/tables.htm
- Annual revision and 2025 missing-October explanation: https://www.bls.gov/lau/launews1.htm
- LAUS definitions/methods: https://www.bls.gov/lau/laufaq.htm

The workbooks supplied here are snapshots. Their footer dates and hashes identify these inputs; future BLS downloads may revise historical observations.
