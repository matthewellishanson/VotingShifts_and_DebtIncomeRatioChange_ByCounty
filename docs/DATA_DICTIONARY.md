# Prepared output dictionary

`county_demo.json` has `metadata` and `counties`. The CSV contains the same county fields. Full-precision numeric margins are retained for analysis; round only at display time.

| Field/family | Meaning |
|---|---|
| state, county_fips, county_name | State abbreviation, five-character county ID, source name |
| debt_start_period, debt_end_period | Configured year/quarter, e.g. 2024Q3 |
| debt_start_low/high, debt_end_low/high | Published ratio category bounds; null high is open-ended |
| debt_transition | higher_category, same_category, lower_category; never an exact change |
| president_2024_dem/rep/total_votes | Source vote totals, retained for audit even when geographic baseline held |
| president_2024_margin_pp | D-minus-R all-vote margin; null where geography unresolved |
| president_source_version | MEDSL row version |
| president_geography_status | matched or needs_reconciliation; matched is a join status, not independent certification |
| comparison_year | 2026 for this adapter |
| results_status | provisional_unverified |
| house_2026_* | County votes summed across House county–district portions |
| governor_2026_*, senate_2026_* | County results for these separate offices, where present |
| *_dem_votes, *_rep_votes, *_total_votes | Observed candidate/all-vote totals |
| *_margin_pp | Observed D-minus-R margin; null for unsupported/absent pairings |
| *_minus_president_2024_pp | Cross-office 2026 margin minus 2024 presidential margin; positive toward Democrats |
| *_race_ids | Source race IDs; semicolon-separated when a county crosses House districts |
| *_source_finished | Source county completion flag aggregated across parts; not certification |

CSV represents nulls as blanks. JSON uses null. Missing offices have null measures and empty race IDs. Do not substitute zeros. Publication must display sources, periods, geographic holds and provisional status alongside values.
