# Original downloads (local, ignored)

The starter includes these unmodified ZIP bytes under normalized names:

| Original upload | Stored filename |
|---|---|
| household-debt(1).zip | household-debt.zip |
| dataverse_files.zip | dataverse_files.zip |
| callthemap-results-2026-all.zip | callthemap-results-2026-all.zip |

`python scripts/run.py import` reads only named members; it does not extract arbitrary paths. The archives keep the national data for later scope expansion. Only selected source rows and accompanying documentation are tracked in Git. Do not edit raw subsets by hand: correct source problems through explicit adapters or reviewed replacement snapshots.

If an archive is missing, restore it here from your original download. Do not rename a different dataset to match these filenames. Review `data/source_manifest.json` hashes when changing snapshots. No automated downloading is implemented.
