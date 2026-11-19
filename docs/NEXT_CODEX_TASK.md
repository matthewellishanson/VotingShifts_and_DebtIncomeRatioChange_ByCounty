# Next Codex task: provisional Kansas research demo

Paste the task below into Codex while it is opened in the local VotingShifts_and_DebtIncomeRatioChange_ByCounty repository.

---

Read AGENTS.md, README.md and docs/PROJECT_PLAN.md, METHODOLOGY.md, SOURCES.md, DATA_DICTIONARY.md and DECISION_LOG.md. Inspect the existing files before editing. Use the existing Python environment if present, otherwise create .venv with Python >=3.12. Run scripts/run.py all and the unittest suite; read reports/quality_report.md. Do not silently repair source counts or change analytical definitions.

Implement a small static React/Vite/TypeScript frontend in frontend/. Use generated data/processed/county_demo.json through an explicit reproducible copy/export step, preserving metadata and nulls. Keep Node dependency setup isolated in frontend and commit its lockfile. Add exact Windows setup/build/run instructions to the root README after testing them as far as the environment permits.

Start with Kansas (105 counties). Default to 2024 presidential versus 2026 gubernatorial all-vote margin difference. Offer House and Senate as separate selectors. Offer a debt-category-transition map toggle. Add a searchable linked results table, click/tap county details and a grouped dot plot of electoral differences by debt-transition group. Display exact source ranges, periods, source links and provisional/unverified status. Retain missing-data states; do not draw withheld values as zeros. Keep an explicit all-vote margin definition and cross-office comparison label.

Acquire an appropriate simplified county geometry file from an authoritative source, record source/license/vintage in docs/SOURCES.md and validate FIPS/counts before use. Use an SVG thematic map with accessible table alternative, keyboard selection and a mobile reading order that shows the results/meaning before controls. Preserve state/office/county/view selections in the URL. Avoid a slippy map, video streaming, backend or complex deployment in this milestone.

A Missouri view may be added after Kansas works, but must show the four unresolved counties as unavailable for presidential comparisons. Do not allocate synthetic Kansas City votes or infer missing governor/Senate data. No 2024 House comparison is available in the current attachments.

Provide an explicit prepare-data command, production build, meaningful interaction checks and a short handoff saying what works and what source verification remains. Keep source verification separate from parser correctness. Do not publish or invent an editorial conclusion about debt causing voting shifts.
