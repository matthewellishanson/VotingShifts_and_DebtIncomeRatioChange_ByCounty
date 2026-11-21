# KS/MO QCEW review and county panel

Your `data/raw/qcew/` placement is appropriate. Retain the original CSVs there unchanged.
Filtering the downloaded files to KS/MO is sufficient for this demo; no other state is required
to calculate these county indicators. The uploaded subset cannot restore excluded states later:
retain the original nationwide downloads elsewhere if you still have them, or redownload when expanding.

## Verified coverage

- 666 CSVs: 222 areas in each of 2024, 2025 and 2026.
- 105 KS counties, 115 MO county equivalents, plus both statewide totals.
- 2024 Q1–Q4, 2025 Q1–Q4 and 2026 Q1: nine quarters.
- 1,444,577 source rows checked, all using the same schema.
- All 1,980 county-quarter total-covered observations are disclosed.
- Federal, state, local-government and private totals also disclosed in every county-quarter.
- County FIPS match the existing LAUS panel's 220 county equivalents exactly.

Consolidation is useful now. It selects BLS's already-published all-industry totals,
not a sum across overlapping NAICS and ownership categories. Keep industry detail raw until
there is a defined sector question; no source rows have been deleted or rewritten.

## Install and run

The scripts and documentation are integrated into the repository. Input paths are
`data/raw/qcew/2024/ByArea/...csv`, and similarly for 2025/2026.
The script searches recursively, so another enclosing folder is also supported.

```powershell
.\.venv\Scripts\python.exe scripts\prepare_qcew.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_qcew.py -v
```

Only Python's standard library is used. No installation, Excel, API key or network connection required.
The script can also read the original ZIP directly:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_qcew.py --source data\raw\qcew.zip
```

Use either extracted inputs or the ZIP. Avoid duplicate CSV copies under the source directory;
the script rejects duplicate selected area/quarter/ownership keys. It expects the supplied
2024 Q1–2026 Q1 window; update validation deliberately when adding later quarters.

## Prepared files under data/processed/qcew/

| File | Purpose |
|---|---|
| `county_quarterly_totals_ks_mo.csv` | Main county panel, 1,980 records; all-industry, total covered |
| `county_quarterly_ownership_ks_mo.csv` | 9,900 records: total covered plus federal/state/local/private, kept as distinct categories |
| `statewide_quarterly_totals_ks_mo.csv` | 18 records, excluded from county maps |
| `county_same_quarter_yoy_ks_mo.csv` | 1,100 county comparisons: each 2025 quarter versus 2024, plus Q1 2026 versus Q1 2025 |
| `coverage_by_quarter.csv` | State/quarter coverage checks |
| `source_inventory.csv` | Original member paths, SHA-256 hashes, row counts and periods for all 666 inputs |
| `manifest.json`, `quality_report.md` | Schema, disclosure counts, provenance and limitations |

When the ZIP input mode is used, the manifest records its hash. Directory-mode source paths refer
to the preserved repository snapshot. Rebuilding regenerates local lineage.
No preliminary/final release status is encoded in these quarterly CSVs, so the output explicitly
marks that status unknown. Verify the release metadata before publication.

## Measures and interpretation

| Field | Meaning |
|---|---|
| `county_fips` | Five-character join key; blank on the separate statewide panel |
| `period` | YYYY-Qn; filter to the desired quarter before joining election records |
| `month1_emplvl`–`month3_emplvl` | Covered payroll jobs in each month's reference pay period |
| `quarter_avg_monthly_employment` | Mean of those three monthly job counts; can be fractional |
| `qtrly_estabs_count` | Establishments, not necessarily firms or new business openings |
| `avg_wkly_wage` | Published average weekly wage in nominal dollars, not median or hourly wages |
| `total_qtrly_wages` | Quarterly nominal payroll, not resident household income |
| `own_code`, `industry_code`, `agglvl_code`, `size_code` | Original classification keys retained to identify the selection |
| `disclosure_code`, `data_status` | Disclosure/absence status, retained even though selected totals are disclosed |
| `source_file`, `source_row` | Traceback to original CSV |

Published total selection: `own_code=0`, `industry_code=10`, `size_code=0`,
`agglvl_code=70` for counties and `50` for states. Ownership categories must not be added
to total covered. Do not sum a state's total together with its county rows, or mix NAICS
parents with their children. Prefer published statewide totals for state comparisons.

All observations are not seasonally adjusted. Start with matched-quarter comparisons:
Q1 2026 versus Q1 2025 is a suitable initial year-over-year measure. Q1 2026 versus Q1 2024
is also available from the panel when a two-year comparison is desired. Q4 2024 versus Q1 2026
mixes seasonal conditions and is not a clean change since the election.

Employment and wage differences are descriptive, not evidence of a specific administration's effects.
QCEW measures covered workplace jobs, while LAUS measures resident people. Do not subtract the
two and label the difference unemployment. Commuting matters substantially around Kansas City.
QCEW omits self-employment and does not fully capture farm-owner income or farm financial distress.
Average wages change with the mix of jobs, bonuses and other compensation; wage growth is not
automatically the raise experienced by a typical worker. Real wage analysis requires an explicit
inflation adjustment; this add-on does not manufacture a county inflation index.

## Suppression and later industry work

The detailed source contains 796,798 N-coded rows (suppressed) and 20,291 dash-coded rows
(cells not present for that quarter). They are not actual zero employment/wages.
For N-coded rows, BLS still discloses establishment counts, but other suppressed measures
are zero-filled in raw files. The adapter preserves establishment counts and blanks suppressed
employment/wage fields. Dash-coded selected cells would be blank throughout.
Location-quotient and over-the-year disclosure flags are separate; a later detailed adapter must
respect those independently. This panel computes its own comparisons from disclosed endpoints.

Defer industry aggregation, inflation adjustment, a combined financial-strain score and electoral
modeling until the other sources have been reviewed. The existing source subset is sufficient
to proceed to the marketplace datasets now; QCEW does not need more downloading for this step.
Later quarters would bring the labor-demand measures closer to election day, but are not supplied here.

## Git and Codex handoff

```powershell
git add QCEW_README.md scripts/prepare_qcew.py tests/test_qcew.py
git diff --cached --stat
```

Keep processed outputs reproducible under the project's existing ignore rules. The raw folder is
about 453 MB in total. In this checkpoint it is the only immutable local copy of the supplied KS/MO
snapshot: no equivalent QCEW ZIP is present in `data/archives/`, and a future BLS download could be
revised. Track the 666 CSVs and their hashes despite the aggregate size. Do not add a duplicate archive
later unless there is a documented preservation reason. No Git actions run automatically.

Codex: Read this file, rebuild from `data/raw/qcew`, run tests and inspect the quality report.
Keep the 220-county quarterly panel separate from LAUS monthly/annual data, retain classifications
and disclosure handling, and add Q1 2025–Q1 2026 employment and nominal wage changes to research
options. Do not join nine quarters directly to one-row-per-county election data without choosing a
comparison. Do not infer causal policy effects or present Q1 as election-eve conditions.

Official definitions and layouts:
- https://www.bls.gov/cew/about-data/downloadable-file-layouts/quarterly/naics-based-quarterly-layout.htm
- https://www.bls.gov/cew/questions-and-answers.htm
- https://www.bls.gov/opub/hom/cew/concepts.htm
