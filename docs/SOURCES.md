# Source register

This starter uses the user-supplied archives, not a fresh live download. The archive hashes in `data/source_manifest.json` identify the exact bytes. All URLs below are source/citation entry points, not automatic download dependencies.

| Input | Original member(s) used | Scope retained | Status/attribution |
|---|---|---|---|
| Fed household-debt ZIP | household-debt-by-county.csv and .txt | KS/MO, all quarters in 2024 and 2025 | Published category bounds, not exact values; credit Federal Reserve Board / FRBNY CCP–Equifax / BLS as applicable |
| MEDSL Dataverse ZIP | countypres_2000-2024.csv; codebook; sources-president.csv | KS/MO presidential 2024 rows; documentation preserved | Uploaded rows have version 20260225; supplied codebook date differs. Retain both and cite the actual Dataverse release on publication |
| Call the Map ZIP | counties.csv; races.csv; README.txt | KS/MO House, Governor, Senate; race metadata | Supplied README snapshot 2026-11-18T21:33:46Z; CC BY 4.0; credit Call the Map and civicAPI wherever identified by race metadata. Provisional/unverified |

## Entry points

- Fed overview: https://www.federalreserve.gov/releases/z1/dataviz/household_debt/
- Fed methodology: https://www.federalreserve.gov/econres/notes/feds-notes/household-debt-to-income-ratios-in-the-enhanced-financial-accounts-20180109.html
- MEDSL county presidential returns: https://doi.org/10.7910/DVN/VOQCHQ
- MEDSL 2024 precinct collection (future House input): https://github.com/MEDSL/2024-elections-official
- Call the Map downloads: https://www.callthemap.com/results/data
- Call the Map credit link: https://www.callthemap.com/results
- civicAPI: https://civicapi.org
- Official Kansas verification: https://www.sos.ks.gov/elections/election-results.html
- Official Missouri verification: https://www.sos.mo.gov/elections/s_default/results

## Still needed

1. Certified 2026 verification or replacement snapshots; record each authoritative source URL and retrieval date.
2. Official geographic reconciliation for separate Kansas City 2024 returns.
3. County boundary file for the map, with source, vintage, geographic coverage and license/attribution recorded here. No geometry is bundled.
4. 2024 House data if same-office House comparisons become a requirement. The uploaded Dataverse ZIP has presidential returns only.
5. Formal publication citation/license review for the actual MEDSL dataset version; do not infer terms from the CSV extension.

## New-source checklist

Keep the original download; record its SHA-256; inspect headers and reporting units; distinguish TOTAL from component voting modes; preserve source timestamps; reconcile totals; check FIPS; record coverage/missingness; document certification and terms; then update the adapter and decision log.
