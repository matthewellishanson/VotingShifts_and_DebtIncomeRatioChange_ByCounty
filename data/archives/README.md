# Original downloads (local, ignored)

The starter includes these unmodified ZIP bytes under normalized names:

| Original upload | Stored filename |
|---|---|
| household-debt(1).zip | household-debt.zip |
| dataverse_files.zip | dataverse_files.zip |
| callthemap-results-2026-all.zip | callthemap-results-2026-all.zip |

`python scripts/run.py import` reads only named members; it does not extract arbitrary paths. The archives keep the national data for later scope expansion. Only selected source rows and accompanying documentation are tracked in Git. Do not edit raw subsets by hand: correct source problems through explicit adapters or reviewed replacement snapshots.

If an archive is missing, restore it here from your original download. Do not rename a different dataset to match these filenames. Review `data/source_manifest.json` hashes when changing snapshots. No automated downloading is implemented.

The ignored local archive `bls-laus-monthly-laucntycur14.zip` is an immutable backup of the supplied monthly LAUS package (2,583,550 bytes; SHA-256 `7f1a4aafefce4345b88362bdf4b0b557bd92b3acf4509f40770a5c22955a5a1c`). Its sole member, `laucntycur14.xlsx`, is byte-identical to the tracked `data/raw/bls_laus_monthly/laucntycur14.xlsx` (SHA-256 `02e29161a7757648028d578040e1a18a80eaf8662d5d93288a2f1055fab30a81`). The archive stays ignored to avoid committing both compressed and extracted copies.

The frontend boundary snapshot uses the separately downloaded, ignored Census archive `cb_2024_us_county_500k.zip`. `python scripts/prepare_frontend.py --import-geometry` checks its pinned SHA-256, rebuilds the tracked Kansas-only GeoJSON subset, records its hash, and prepares the frontend. The ordinary `python scripts/prepare_frontend.py` command never changes the versioned geometry snapshot.
