# Annual county labor-force source review

## Coverage verified in the supplied files

There are 18 workbooks, `laucnty08.xlsx` through `laucnty25.xlsx`. The suffix identifies the year (e.g. 13 = 2013), not the month or version. Each workbook has one worksheet headed Labor Force Data by County, followed by a nine-column table and source notes/footer dates.

All 105 KS counties and all 115 MO county equivalents occur once in every supplied year, with the same five-digit IDs and complete labor measures: 3,960 unique county/year rows. St. Louis city (29510) is distinct from St. Louis County (29189). There is no synthetic Kansas City row in this BLS panel; do not change the separate election data's geographic holds on that basis.

All source areas are retained in both individual national CSV conversions and a combined panel. The total is 57,962 source-area/year records. Source area counts vary: 3,218 in 2008–2009; 3,220 in 2010–2019; 3,221 in 2020–2025. These include Puerto Rico municipios and the District of Columbia. Do not interpret these counts as a fixed contemporaneous Census county universe. Expansion beyond KS/MO requires checking boundary/code changes across years. The parser preserves source geography rather than imputing a modern crosswalk.

## Critical period limitation

The 2025 workbook's own footnote states that all counties outside Puerto Rico use 11-month averages excluding October 2025 because data were not collected during the federal government shutdown. Puerto Rico uses 12 months. BLS's official annual-revisions page independently documents this difference and says the 11-month averages are not strictly comparable to prior annual averages.

The output carries averaging-month counts and excluded-month/period flags. The 2024–2025 comparison CSV exposes the differing periods on every row. It is a descriptive source comparison, not a fully matched measure. A matched comparison requires the underlying monthly observations. Do not invent October or derive it from these summaries.

The attached files do not include 2026, so they cannot measure the complete 2024-election-to-2026-midterm period. They are useful historical context and an early endpoint, not a finished election-period explanatory variable.

## Units and interpretation

- Labor force, employed and unemployed are average numbers of resident persons, not total unique people during the year.
- Unemployment rate is percent of the civilian labor force, not percent of all adults or all residents.
- These are place-of-residence LAUS measures. They differ from QCEW/CES workplace payroll jobs and cannot identify industry-specific job changes from these files alone.
- Annual averages are retained as source aggregates; no monthly values or seasonal adjustments are manufactured.
- Published unemployment rates are retained rather than replaced by ratios reconstructed from rounded person counts. The source XLSX stores some one-decimal values as binary floating-point artifacts; the CSV export normalizes these to one decimal place.
- A rise of 3.0% → 3.8% is +0.8 percentage points, not +0.8 percent. Population/age denominators are required for participation or employment/population rates, and are not present here.
- A statewide aggregate, if separately calculated, should use summed unemployed divided by summed labor force, not an equal-county mean. Label any county-derived aggregate distinctly and check against official state series before publishing.

## Conversion and validation

The script reads zipped Office Open XML with Python's standard library, supporting the supplied shared-string, inline-string and ordinary numeric cells. It preserves cell addresses, original workbooks and source metadata, rejects formulas/Excel errors/unexpected headers, confirms title/row years, normalizes FIPS widths, checks LAUS code/FIPS agreement, and rejects duplicate counties.

Every available source row reconciles labor force = employed + unemployed. A separate consistency check flags published rates differing by more than 0.10 pp from rates reconstructed from rounded counts; such alerts do not overwrite source rates. KS/MO completeness and stable county sets are checked for every year.

In 2020, Puerto Rico's 78 county-equivalent rows have N.A. labor measures. The converter retains them as unavailable, not zero; the normalized panel has blank measures and source_unavailable status. They do not affect the KS/MO panel.

Titles, footer dates and notes are preserved in workbook_metadata.json and the prepared manifest. Footer dates describe these source snapshots, not observation dates. Data are revised by BLS; no vintage-comparability guarantee beyond the supplied snapshots is claimed.

## Next data acquisition

Use BLS county monthly LAUS series for the 2024/2026 election-period comparison. Obtain the same months in both years, retain source/revision dates, flag missing October 2025 and preliminary observations, and inspect labor force and resident employment alongside the unemployment rate. Use historical annual data to contextualize changes without claiming a causal effect from a county correlation.

Official explanation: https://www.bls.gov/lau/launews1.htm
County data entry point: https://www.bls.gov/lau/tables.htm
