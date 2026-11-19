# Project plan

## Question

Did Kansas counties that moved into higher household debt-to-income categories show different 2024-to-2026 electoral margin differences from counties in the same or lower categories? Extend the comparison to Missouri where county geography can be reconciled.

The answer is allowed to be no clear association. Do not choose a headline before checking the data.

## Milestones

| Stage | Work | Done when |
|---|---|---|
| 0 — Foundation (included) | Organize three source archives; retain small KS/MO source subsets; prepare repeatable CSV/JSON; document analytical rules | Tests and preparation pass; quality report documents outstanding holds |
| 1 — Verify sources | Compare 2026 counts to certified official results as available; resolve Kansas City/MO reporting; check source snapshot timing and missing races | Reviewed source ledger and a recorded verification decision for each published dataset |
| 2 — Explore | Kansas first; summarize electoral differences by debt transition; inspect outliers and small counties; compare Q3 and Q4 baselines | Descriptive table and chart support an honest takeaway, including no relationship if applicable |
| 3 — Build a demo | County map, office selector, debt toggle, linked table/detail panel and grouped dot plot | All 105 KS counties accounted for; missing/held states visible; sources and provisional status visible on mobile |
| 4 — Extend | Missouri with four unresolved counties unavailable until fixed; later wider geography with explicit crosswalks | No unmatched records silently dropped; coverage report accompanies export |
| 5 — Publish | Final verification, accessible text/table, methodology and attribution; choose domain/host | Results and geography are reviewed; public language matches evidence |

## Keep the first implementation small

- Use static generated JSON, React/Vite and a two-dimensional SVG county map.
- No live API, database, FastAPI service, commercial feed or streaming infrastructure is required here.
- Do not build a map of debt-change divided by voting-change.
- Keep government source verification and backend development as separate tasks.
- A national source file is not proof that all reporting units correspond to Census counties.

## Suggested working rhythm

1. Read the last decision-log entry and quality report.
2. Pick one milestone task small enough for the session.
3. Make edits in scripts/config/frontend; keep source snapshots unchanged.
4. Run the tests and pipeline after analytical changes.
5. Inspect actual outputs and data-quality holds.
6. Log what changed, what remains uncertain, and the next concrete task.
7. Review `git diff`, commit the useful change, and push when ready.

## Next concrete task

Verify the supplied Kansas governor snapshot against official county results. Record source dates, certification status, totals, differences and whether further updates are needed. A functioning parser is not verification of an unfamiliar aggregator's numbers.

For a parallel development task, build the explicitly provisional static demo from the generated JSON, preserving all flags. See NEXT_CODEX_TASK.md.
