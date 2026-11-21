# Checkpoint audit

Audited 2026-11-21 before adding sources. The review covered Git status (tracked, untracked and ignored), repository instructions, all changed code/data/docs, source lineage, generated outputs and the static frontend.

## Inventory and organization

| Group | Reviewed changed/untracked files | Size | Decision |
|---|---:|---:|---|
| Source data and manifest | 714 | 446.15 MiB | Track exact raw bytes and hashes |
| Preparation scripts | 5 | 0.06 MiB | Track |
| Tests | 3 | 0.01 MiB | Track |
| Documentation/configuration (including this report) | 12 | about 0.06 MiB | Track |
| Frontend source/config/lockfile | 23 | 0.15 MiB | Track separately |
| Unrelated or uncertain non-ignored items | 0 | 0 | None found |

The complete `data/raw/` inventory is 715 files / 446.03 MiB. QCEW accounts for 666 files / 432.00 MiB; LAUS annual 37 files / 7.89 MiB; LAUS monthly 2 files / 5.71 MiB; Census geometry 2 files / 0.24 MiB. The largest intended Git file is 4.10 MB, so no individual file needs Git LFS, although the QCEW snapshot is a substantial aggregate commit.

LAUS files had been unpacked one directory too deep. Scripts, tests, guides, raw inputs and generated outputs were moved to their documented root paths. Raw inputs now remain under `data/raw/`, rebuildable panels under ignored `data/processed/`, code under `scripts/`, and tests under `tests/`. The generic `lib/` ignore rule was fixed so `frontend/src/lib/` is versioned. Raw paths use Git's `binary` attribute so checkout cannot normalize or text-diff hash-verified source bytes.

No QCEW archive equivalent to the 666 supplied CSVs exists locally, so the unique snapshot will be tracked. The monthly LAUS ZIP is an ignored immutable backup whose sole member is byte-identical to the tracked XLSX; both hashes are documented in `data/archives/README.md`. No archive/extracted duplicate pair is staged. No credentials or credential-like project files were found. Virtual environments, Node dependencies, caches and generated frontend/data/report outputs remain ignored.

## Validation

- `python scripts/prepare_laus_annual.py`: 3,960 KS/MO county-year records, 2008–2025; 105 KS and 115 MO county equivalents in all 18 years.
- `python scripts/prepare_laus_monthly.py`: 3,080 county-month records; 2,860 available and 220 unavailable October 2025 placeholders; all 220 September 2026 rows remain preliminary.
- `python scripts/prepare_qcew.py`: 1,980 county totals, 9,900 ownership records, 1,100 year-over-year comparisons and 18 statewide records; 105 KS and 115 MO county equivalents in each of nine quarters.
- Hash reconciliation: 666/666 QCEW files, 18/18 annual workbooks and all converted annual/monthly source tables matched their inventories. The core pipeline also verified all 715 raw-file hashes.
- `python scripts/run.py all`: passed; 220 election/debt rows and all 14 selected race totals reconciled. Four Missouri presidential baselines remain withheld and all 2026 results remain provisional/unverified.
- `python -m unittest discover -s tests -v`: 22 tests passed.
- `python scripts/prepare_frontend.py`: 105 Kansas data rows matched 105 Census features.
- `npm test`: 6 tests passed. `npm run build`: passed. The frontend preserves null/unavailable states, data-quality fields and provisional language.

Missing LAUS values remain blank/status-coded rather than zero. QCEW suppression handling remains intact; the selected county totals and ownership records are disclosed, while suppressed detailed source cells are never treated as observed zero. The annual 2025 11-month/excluded-October caveat, monthly September 2026 preliminary label and QCEW unknown release status remain explicit.

## Tracked and ignored

Track source snapshots because a Git commit plus SHA-256 inventory is the exact recovery route. Track source-preserving LAUS conversions for the documented national tables, preparation code/tests, provenance, Census subset and frontend source. Ignore only rebuildable outputs and local machine state: 6,757 files / 188.13 MiB at audit time, comprising archives, `data/processed/`, generated reports/frontend data/build output, `.venv`, `node_modules`, bytecode and build caches. Ignored original archives remain local backups; their tracked subsets and hashes support ordinary preparation without them.

## Limitations and next task

The 2026 election snapshot is not independently verified or certified; Missouri/Kansas City geography is unresolved; QCEW release status is not encoded; QCEW stops at 2026 Q1; monthly LAUS lacks a matched 2024 baseline and October 2025; annual 2025 is not a full-year comparable average. These data support descriptive county aggregates only, not causal claims.

Before analysis/publication, verify the supplied Kansas governor results against official county returns and retain the Missouri holds. The next data acquisition should obtain an exact, dated and hashed 2024 monthly county LAUS baseline (and any required matched 2025 months) without replacing or revising this checkpoint silently.
