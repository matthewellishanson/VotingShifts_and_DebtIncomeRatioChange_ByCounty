# Project instructions for coding assistants

Read README.md, docs/PROJECT_PLAN.md, docs/METHODOLOGY.md and reports/quality_report.md (if generated) first.

- The current deliverable is an offline KS/MO research pipeline. Preserve simple commands and Python standard-library-only operation unless a task actually requires dependencies.
- Original archives are immutable, local backups. Source subsets and their documentation are versioned. Change input snapshots only deliberately; record hashes and preserve attribution.
- All 2026 inputs are provisional/unverified. Do not call them certified because a race is marked called, won, or fully reported.
- County FIPS are strings. Kansas City synthetic 36000 is not a county. Withhold the four configured MO baselines until official geographic reconciliation; do not allocate ballots by population shares.
- Debt observations are ranges. Same category does not mean zero change. Never compute an exact debt-change ratio, pretend category steps are equally spaced, or fill an open-ended bin with an invented midpoint.
- Use Democratic-minus-Republican percentage-point margins with all candidate votes as denominator. Sum House county-part votes before calculating margins. Keep offices separate.
- No 2024 House input is included. Do not invent same-office 2024–2026 House comparisons.
- Research may find no relationship. Do not write a conclusion about debt causing electoral changes from these county aggregates.
- Generated data are rebuilt, not edited. Keep geography/data-quality flags in every frontend export. Do not convert missing observations to zeros.
- Run `python -m unittest discover -s tests -v` and `python scripts/run.py all` after pipeline edits. Check the report and inspect changed data before proposing publication.
- No deployment, provider subscription or backend is needed for the present stage. Avoid expanding this into the 2028 live-results infrastructure without a task requiring it.
