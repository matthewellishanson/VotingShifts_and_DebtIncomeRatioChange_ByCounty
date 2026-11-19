# Methods and limits

## Debt data

Use `area_fips` as a five-character county identifier. The attached source contains `year`, `qtr`, `low`, `high`, through 2025 Q4. The bounds are published categories; a blank upper bound means open-ended, not missing/zero debt.

Default window: 2024 Q3 → 2025 Q4. This uses a pre-election quarterly baseline; it is not a November-to-December monthly change. Sensitivity window: 2024 Q4 → 2025 Q4. Document which window produced each chart.

Compare the category lower bounds to classify a move to a higher or lower category. Equal bounds mean **same reported category**, not unchanged debt. No midpoints, exact growth rate, percentage-point debt change, or ratio to electoral change is estimated. Category steps have unequal widths.

The measure is aggregate household debt relative to aggregate income in an area, not a mean/median of individual household ratios. The Fed's published methodology excludes student loans, uses credit-panel debt and BLS income, and is not a debt-service-payment burden measure. Debt increases need not mean financial distress; debt can also rise with mortgage borrowing and asset ownership.

## Elections

Let D/R be Democratic/Republican candidate votes and T all candidate votes, including other candidates/write-ins:

`margin_pp = 100 * (D - R) / T`

`cross_office_difference_pp = margin_2026_office - margin_2024_president`

Positive difference means movement toward Democrats in the observed margins. The result is a percentage-point difference, not a percent increase. For example: R+20 → D+6 gives +26 points.

Keep House, Senate and governor separate. For U.S. House, sum candidate votes across each county's district portions before computing the countywide margin. Do not average the margins, average districts equally, add votes across different offices, or assign a districtwide result to every county. Reject duplicate race/county records.

The adapter withholds a margin for non-D/R pairs or zero-vote major-party sides; manually review such contests. If expanding to fusion-party, ranked-choice, top-two or other formats, implement and document appropriate treatment first.

The supplied MEDSL KS/MO 2024 observations are TOTAL-mode rows. This scoped adapter rejects mixed modes rather than silently adding component modes and totals. Candidate sums and denominator consistency are checked. Check new source schemas before swapping files.

## Geographic limitations

The MEDSL attachment contains 105 KS county units and 116 MO reporting units, including synthetic FIPS `36000` for Kansas City. The Fed data have 115 MO county equivalents. Do not treat 36000 as a real county or simply discard its votes and call the remaining data complete.

Conservatively hold the presidential baseline and all derived presidential comparison fields for Cass (29037), Clay (29047), Jackson (29095) and Platte (29165), pending official county-by-county reconciliation. This broad hold is precautionary: establish the actual reporting coverage before deciding which counties need corrections. Retain observed input totals for auditing but do not display them as validated full-county baselines.

Prefer official county totals/crosswalks. Never divide Kansas City ballots by population proportions as though that reconstructs actual returns. St. Louis city is a county equivalent and is retained separately.

## Status and lineage

The supplied Call the Map archive contains 2026 races marked called, with selected county rows marked finished=no. A called race is not certified. Export provisional/unverified status until you independently reconcile to certified returns. County totals reconciling to race totals within the same source do not verify the original counts.

Keep original ZIPs, source documentation and SHA-256 hashes. Source subsets retain original columns/values; raw files are filtered, not corrected. Changes to source snapshots require a new recorded provenance review. Source times are retained in raw race/counties files; missing source times are not inferred.

## Statistical interpretation

Use descriptive distributions first. Counties are not independent samples of individual voters; neighboring places share conditions. Results depend on turnout, candidates, incumbency, demographic composition and the different offices/electorates being compared. Equal county weights describe counties; weights based on votes/population answer different questions. Do not conflate them.

Do not infer that debt caused electoral shifts, that indebted individuals switched parties, or that category movement measures the amount of economic distress. If quantitative modeling is later justified, specify controls, weighting, spatial dependence, sensitivity checks and uncertainty before interpreting coefficients.
