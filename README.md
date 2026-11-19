# Voting shifts and county household debt

An exploratory Kansas/Missouri project comparing county household debt-to-income **categories** with 2024 presidential and 2026 election margins. Start with Kansas governor and U.S. House comparisons; expand only after verifying the inputs.

**Current status:** the data organization and offline preparation pipeline work. A map/frontend is the next milestone. The supplied 2026 results are provisional and have not been independently checked against certified returns. This starter does not establish a relationship between debt and voting.

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

Use Python **3.12 or newer**. No third-party Python packages, Node, API keys, paid feeds or database are needed for this stage.

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

After editing `config/demo.json`, run `all` to refresh matching subsets. Start/end debt quarters are configurable within the supplied archive. Election years, state coverage, geography rules and supported source schemas are intentionally scoped; extending them requires adapter work, not simply changing a year label.

## 4. Where things belong

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
| `frontend/` | Next-stage implementation brief; no application yet | Track |

The ZIP already contains the original archives and selected source rows. Future Git clones will receive the tracked subsets, **not** the ignored original ZIPs. A clone can run `prepare` without archives. Keep the original downloads backed up if you want to rerun `import` or expand the scope. See `data/archives/README.md` for exact filenames.

## 5. The analysis in plain English

- **Debt:** default comparison is Q3 2024 (before the presidential election) to Q4 2025. A higher/lower/same category is observable; an exact ratio change is not. Switch the start quarter to Q4 for a same-quarter annual sensitivity check.
- **Voting:** margin = `100 * (Democratic votes - Republican votes) / all candidate votes`. Positive means Democratic advantage. A difference of +26 means 26 percentage points toward Democrats between the selected contests.
- **House:** sum votes across county–district portions before calculating county margins. These are presidential-to-House differences, not same-office House changes.
- **Offices:** governor, House and Senate stay separate. Missouri's missing governor/Senate comparison is unavailable, not zero.
- **Geography:** Cass, Clay, Jackson and Platte presidential comparisons are conservatively withheld while Kansas City's separate record is reconciled. This is a review hold, not a claim that all four county records are definitely wrong.
- **Status:** matching totals within an aggregator checks consistency, not accuracy or certification. The source marks the selected county rows unfinished. Preserve that information.
- **Inference:** this is exploratory county-level association, not proof that indebted people changed their votes or that debt caused a political shift.

Read [the project plan](docs/PROJECT_PLAN.md) for next steps and [methodology](docs/METHODOLOGY.md) for definitions. The compact [next Codex task](docs/NEXT_CODEX_TASK.md) can be pasted into a session opened in this local repository.

## 6. Before the first commit

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

No license for your own code is chosen here. Third-party data attribution/terms remain separate from any license you later select for the repository.
