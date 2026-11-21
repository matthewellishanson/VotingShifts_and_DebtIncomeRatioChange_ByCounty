# Voting shifts and county household debt

An exploratory Kansas/Missouri project comparing county household debt-to-income **categories** with 2024 presidential and 2026 election margins. Start with Kansas governor and U.S. House comparisons; expand only after verifying the inputs.

**Current status:** the data organization and offline preparation pipeline work, and `frontend/` contains a static provisional Kansas research demo. The supplied 2026 results are provisional and have not been independently checked against certified returns. This project does not establish a relationship between debt and voting.

## 1. Put this starter into the existing repository

Extract the starter ZIP into a temporary folder. Copy its **contents** into:

`C:\Users\mehan\code\VotingShifts_and_DebtIncomeRatioChange_ByCounty`

Allow the included README.md to replace your one-sentence README. Keep the existing `.git` directory and Python `.gitignore`; the starter contains no `.git` directory. If you have added other work since requesting this starter, inspect overlapping filenames before replacing them.

In VS Code, open that repository folder, then open a **PowerShell** terminal. Run:

```powershell
Set-Location 'C:\Users\mehan\code\VotingShifts_and_DebtIncomeRatioChange_ByCounty'
Get-Content .\GITIGNORE_ADDITIONS.txt | Add-Content .\.gitignore
```

Append the ignore additions once. This preserves your existing Python ignore template.

## 2. First-time Python setup

Use Python **3.12 or newer**. The research pipeline remains Python standard-library-only. Node is required only for the separate static frontend; no API keys, paid feeds, database, deployment provider or backend are needed.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe scripts\run.py all
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

If 3.12 is not installed, `py -0p` lists available interpreters. Substitute an installed version >=3.12 in the first command. If `py` is unavailable but `python --version` reports >=3.12, use `python -m venv .venv` instead.

These commands deliberately use the environment's executable directly: no activation or PowerShell execution-policy change is needed. Nothing is downloaded by the pipeline.

Expected result: **220 county rows**, internally reconciled totals for **14 selected 2026 races**, and a readable report at `reports/quality_report.md`. Four Missouri counties have withheld presidential comparison margins, and the separate Kansas City reporting unit is retained in raw input and reported as unresolved.

## 3. Returning in a later work session

```powershell
Set-Location 'C:\Users\mehan\code\VotingShifts_and_DebtIncomeRatioChange_ByCounty'
.\.venv\Scripts\python.exe scripts\run.py all
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
code reports\quality_report.md
```

Read the report before inspecting results. Open `data/processed/county_demo.csv` in VS Code or a spreadsheet; use `county_demo.json` as the future frontend input. CSV blanks and JSON `null` mean unavailable/withheld, not zero. Spreadsheet software may strip leading zeros from FIPS: import that column as text.

Command reference:

| Command after the Python executable | Purpose |
|---|---|
| `scripts/run.py import` | Rebuild source subsets from the three original archives; record hashes |
| `scripts/run.py prepare` | Validate existing subsets and regenerate county outputs/report |
| `scripts/run.py all` | Both steps; recommended routine command |
| `-m unittest discover -s tests -v` | Verify margin signs, vote aggregation, mode handling and other core rules |

### QCEW county-quarter panel

See the [QCEW guide](QCEW_README.md) for coverage, fields and interpretation. Rebuild and test the standard-library-only panel from the local files under `data/raw/qcew/` with:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_qcew.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_qcew.py -v
```

### LAUS annual and monthly panels

The annual LAUS snapshot covers 2008–2025; the 2025 KS/MO observations are 11-month averages that exclude October and are not strictly comparable with earlier full-year averages. The separate monthly snapshot covers August 2025–September 2026, preserves 220 unavailable October 2025 county rows, and marks September 2026 preliminary. Rebuild both panels with:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_laus_annual.py
.\.venv\Scripts\python.exe scripts\prepare_laus_monthly.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_laus*.py" -v
```

Read [the annual guide](LAUS_ANNUAL_README.md), [monthly guide](LAUS_MONTHLY_README.md), and generated quality reports under `data/processed/laus_*/` before analysis. Keep annual averages, monthly resident labor-force observations, and QCEW workplace-job observations as separate panels.

After editing `config/demo.json`, run `all` to refresh matching subsets. Start/end debt quarters are configurable within the supplied archive. Election years, state coverage, geography rules and supported source schemas are intentionally scoped; extending them requires adapter work, not simply changing a year label.

## 4. Prepare, test, build and run the Kansas frontend on Windows

Use Node.js **20.19 or newer** (Node 22.12+ or 24 also works). The tested project environment used Python 3.12.10, Node 24.14.1 and npm 11.11.0. In a new PowerShell terminal after completing the Python setup above:

```powershell
Set-Location 'C:\Users\mehan\code\VotingShifts_and_DebtIncomeRatioChange_ByCounty'
.\.venv\Scripts\python.exe scripts\run.py prepare
.\.venv\Scripts\python.exe scripts\prepare_frontend.py
Set-Location .\frontend
npm ci
npm test
npm run build
npm run dev -- --host 127.0.0.1
```

Open the local URL printed by Vite, normally `http://127.0.0.1:5173/`. Stop the development server with `Ctrl+C`.

To inspect the production build after `npm run build`:

```powershell
npm run preview -- --host 127.0.0.1
```

The build output is `frontend/dist/` and is ignored. `package-lock.json` is versioned; use `npm ci`, not an unpinned install, for repeatable setup. The interaction checks cover the 105-county default, search/table/detail linking, office and map-mode changes, and URL state validation. The demo remains static and offline after dependencies are installed.

## 5. Where things belong

| Path | Purpose | Git policy |
|---|---|---|
| `data/archives/` | Original national ZIPs, unchanged except a simpler Fed filename | Local backup; ignored |
| `data/raw/fed/` | Exact source rows for KS/MO, 2024–2025, plus dictionary | Track |
| `data/raw/medsl/` | 2024 KS/MO presidential rows, including unresolved Kansas City; codebook/source list | Track |
| `data/raw/callthemap/` | KS/MO House, governor and Senate rows, race metadata, source dictionary | Track |
| `data/source_manifest.json` | Archive/subset SHA-256 hashes and extraction scope | Track |
| `data/processed/` | Rebuildable CSV/JSON with one row per county | Ignore |
| `reports/` | Rebuildable quality report | Generated reports ignored |
| `src/voting_debt/` | Preparation and validation logic | Track |
| `scripts/run.py` | Single command entry point | Track |
| `config/demo.json` | Geography, expected counts and debt quarters | Track |
| `tests/` | Tests of meaningful analytical rules | Track |
| `docs/` | Plan, methods, source register, decision log and next Codex task | Track |
| `frontend/` | React/Vite/TypeScript static demo; generated `public/data` and `dist` are ignored | Track source and lockfile |
| `data/raw/census/` | Versioned Kansas boundary subset and geometry provenance/hashes | Track |
| `data/raw/bls_laus_annual/` | Original annual workbooks, converted source tables and workbook hash inventory | Track |
| `data/raw/bls_laus_monthly/` | Monthly workbook and converted source table; redundant source ZIP kept under ignored archives | Track |
| `data/raw/qcew/` | Supplied KS/MO area CSV snapshots; no equivalent immutable archive is present locally | Track despite aggregate size; preserve per-file hashes |

The ZIP already contains the original archives and selected source rows. Future Git clones will receive the tracked subsets, **not** the ignored original ZIPs. A clone can run `prepare` without archives. Keep the original downloads backed up if you want to rerun `import` or expand the scope. See `data/archives/README.md` for exact filenames.

## 6. The analysis in plain English

- **Debt:** default comparison is Q3 2024 (before the presidential election) to Q4 2025. A higher/lower/same category is observable; an exact ratio change is not. Switch the start quarter to Q4 for a same-quarter annual sensitivity check.
- **Voting:** margin = `100 * (Democratic votes - Republican votes) / all candidate votes`. Positive means Democratic advantage. A difference of +26 means 26 percentage points toward Democrats between the selected contests.
- **House:** sum votes across county–district portions before calculating county margins. These are presidential-to-House differences, not same-office House changes.
- **Offices:** governor, House and Senate stay separate. Missouri's missing governor/Senate comparison is unavailable, not zero.
- **Geography:** Cass, Clay, Jackson and Platte presidential comparisons are conservatively withheld while Kansas City's separate record is reconciled. This is a review hold, not a claim that all four county records are definitely wrong.
- **Status:** matching totals within an aggregator checks consistency, not accuracy or certification. The source marks the selected county rows unfinished. Preserve that information.
- **Inference:** this is exploratory county-level association, not proof that indebted people changed their votes or that debt caused a political shift.

Read [the project plan](docs/PROJECT_PLAN.md) for next steps and [methodology](docs/METHODOLOGY.md) for definitions. The compact [next Codex task](docs/NEXT_CODEX_TASK.md) can be pasted into a session opened in this local repository.

## 7. Before the first commit

```powershell
git status --short
git check-ignore data/archives/household-debt.zip
git add README.md AGENTS.md .gitattributes .gitignore GITIGNORE_ADDITIONS.txt config src scripts tests docs frontend data/raw data/source_manifest.json data/archives/README.md data/processed/README.md reports/README.md
git diff --cached --stat
git commit -m "Set up county voting and debt research pipeline"
git push
```

Run the commit/push commands when you are satisfied with the staged files. No automatic commit, push or deployment is performed by this starter.

## Sources and attribution

- Federal Reserve Board, [Household Debt](https://www.federalreserve.gov/releases/z1/dataviz/household_debt/). Source ranges retained; original methodology linked in `docs/SOURCES.md`.
- MIT Election Data and Science Lab, [County Presidential Election Returns 2000–2024](https://doi.org/10.7910/DVN/VOQCHQ). Preserve supplied codebook/source list and use the Dataverse version's citation/terms when publishing.
- [Call the Map](https://www.callthemap.com/results), 2026 results snapshot supplied by the user; CC BY 4.0. Where source metadata identifies civicAPI, also credit **civicAPI (https://civicapi.org), compiled from state and county election offices**. Included source documentation governs attribution.
- U.S. Census Bureau, [2024 Cartographic Boundary Files](https://www.census.gov/geographies/mapping-files/2024/geo/carto-boundary-file.html), 1:500,000 Kansas county subset. Cite Census; the generalized boundaries are for small-scale thematic mapping, not legal boundary determination or area/perimeter analysis.

No license for your own code is chosen here. Third-party data attribution/terms remain separate from any license you later select for the repository.
