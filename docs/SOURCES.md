# Source register

This starter uses the user-supplied archives, not a fresh live download. The archive hashes in `data/source_manifest.json` identify the exact bytes. All URLs below are source/citation entry points, not automatic download dependencies.

| Input | Original member(s) used | Scope retained | Status/attribution |
|---|---|---|---|
| Fed household-debt ZIP | household-debt-by-county.csv and .txt | KS/MO, all quarters in 2024 and 2025 | Published category bounds, not exact values; credit Federal Reserve Board / FRBNY CCP–Equifax / BLS as applicable |
| MEDSL Dataverse ZIP | countypres_2000-2024.csv; codebook; sources-president.csv | KS/MO presidential 2024 rows; documentation preserved | Uploaded rows have version 20260225; supplied codebook date differs. Retain both and cite the actual Dataverse release on publication |
| Call the Map ZIP | counties.csv; races.csv; README.txt | KS/MO House, Governor, Senate; race metadata | Supplied README snapshot 2026-11-18T21:33:46Z; CC BY 4.0; credit Call the Map and civicAPI wherever identified by race metadata. Provisional/unverified |
| Census cartographic boundary KML ZIP | cb_2024_us_county_500k.kml | Kansas county features selected by STATEFP=20 | U.S. Census Bureau 2024 Cartographic Boundary Files, 1:500,000; downloaded 2026-11-18; archive/subset hashes in `data/raw/census/geometry_manifest.json`. U.S. government works generally are not copyright-protected in the United States; cite Census. Boundaries are generalized for small-scale thematic mapping, not legal or area/perimeter analysis. |
| BLS LAUS annual workbooks | `laucnty08.xlsx`–`laucnty25.xlsx` | National county tables; normalized KS/MO panel covers 2008–2025 | Supplied snapshots; workbook/footer dates and hashes are in `data/raw/bls_laus_annual/csv/workbook_metadata.json`. The 2025 KS/MO figures are 11-month averages excluding October, not full-year annual averages. |
| BLS LAUS rolling monthly workbook | `laucntycur14.xlsx` | August 2025–September 2026; all KS/MO county equivalents | Supplied snapshot dated 2026-10-28; September 2026 is preliminary and October 2025 is unavailable. The workbook and converted-table hashes are recorded by the generated monthly manifest. |
| BLS QCEW area CSVs | 666 KS/MO county/state area files | 2024 Q1–2026 Q1 | Supplied snapshot; all files are preserved because no equivalent immutable archive is present. Per-file hashes are regenerated in `data/processed/qcew/source_inventory.csv`. The supplied CSVs do not encode preliminary/final release status. |

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
- Census 2024 cartographic boundary files: https://www.census.gov/geographies/mapping-files/2024/geo/carto-boundary-file.html
- Census cartographic boundary description/limits: https://www.census.gov/programs-surveys/geography/technical-documentation/naming-convention/cartographic-boundary-file.html
- Census citation guidance: https://www.census.gov/about/policies/citation.html
- BLS LAUS county tables: https://www.bls.gov/lau/tables.htm
- BLS LAUS annual revisions and the 2025 October caveat: https://www.bls.gov/lau/launews1.htm
- BLS QCEW downloadable-file layouts: https://www.bls.gov/cew/about-data/downloadable-file-layouts/quarterly/naics-based-quarterly-layout.htm

## Still needed

1. Certified 2026 verification or replacement snapshots; record each authoritative source URL and retrieval date.
2. Official geographic reconciliation for separate Kansas City 2024 returns.
3. 2024 House data if same-office House comparisons become a requirement. The uploaded Dataverse ZIP has presidential returns only.
4. Formal publication citation/license review for the actual MEDSL dataset version; do not infer terms from the CSV extension.

## New-source checklist

Keep the original download; record its SHA-256; inspect headers and reporting units; distinguish TOTAL from component voting modes; preserve source timestamps; reconcile totals; check FIPS; record coverage/missingness; document certification and terms; then update the adapter and decision log.
