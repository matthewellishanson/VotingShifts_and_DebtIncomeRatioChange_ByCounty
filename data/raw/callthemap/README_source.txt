2026 OFFICIAL ELECTION RESULTS, FROM CALL THE MAP
https://www.callthemap.com/results/data

Results as published 2026-11-18T21:33:46Z UTC. The counts are official: each state's election office, or civicAPI, which gathers the states' and counties' own counts, where an office cannot be read. Counts are unofficial until the state certifies them.

LICENSE
Licensed under Creative Commons Attribution 4.0 (CC BY 4.0): free to copy, share and adapt, commercially too, with credit to Call the Map (callthemap.com/results). The counts themselves are official public records from state and county election offices. Rows whose source is civicAPI must also credit civicAPI (civicapi.org), as its terms ask.
CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
Credit: Call the Map (callthemap.com/results). Where a row's source is civicAPI, also: civicAPI (civicapi.org), compiled from state and county election offices.

FILES
Every table is a CSV and a JSON file at https://www.callthemap.com/results/data/2026/<table>.csv or .json; one race's files are at races/<RACE_ID> and counties/<RACE_ID>, a state's legislature and measures at legislatures/<ST> and measures/<ST>, a race's precincts at precincts/<RACE_ID>. manifest.json lists every file with its rows, bytes, SHA-256 checksum and last update. all.zip holds every table whole in both formats and each race's precincts as CSV; their JSON is at precincts/<RACE_ID>.json.

RACES: Every race, by candidate
One row per candidate per race: the statewide (or district-wide) total. Senate, governor, House and every other statewide office on the results pages.

  race_id: The race: SEN-GA (Senate), GOV-GA (governor), GA-06 (House), AG-GA and similar (other statewide offices).
  state: Two-letter state code.
  office: Senate, Governor, House, or the statewide office's name.
  title: The race as the results pages title it.
  status: counting (still being counted, not called), called (Call the Map called a winner), final (the state certified the count).
  outcome: won: the race's winner (called, certified, or unopposed); leads: ahead in the count while counting; empty otherwise. In a race for several seats, every candidate in a seat.
  candidate: The candidate's name as the office prints it.
  party: D, R, I (independent), L, G, or O (other or none), as the office lists the candidate.
  votes: Votes counted for the candidate.
  share_pct: The candidate's share of all votes counted in the race, in percent.
  total_votes: All votes counted in the race.
  seats: Seats the contest fills (1 unless more).
  called_utc: When the race was called or certified, UTC; empty while counting.
  count_updated_utc: When the source last says it counted, UTC.
  source: Who counted: the state's election office, or civicAPI, which gathers the states' and counties' own counts. A civicAPI row must credit civicAPI.
  source_url: Where the count was read.
  source_read_utc: When Call the Map last read the source, UTC (ISO 8601).
  page_url: The race's results page.

COUNTIES: Every race, by county
One row per race per place: the county (or, for a House seat, the part of the county in the district; Connecticut's planning regions; Louisiana's parishes; Alaska's state house districts). The two candidates a race file compares (A and B, the Democrat and the Republican in a race between them) with their votes, and every other vote together.

  race_id: As in races.
  state: Two-letter state code.
  office: As in races.
  place_kind: county, parish, planning region (Connecticut), house district (Alaska) or district; with "part" (county part) for a House seat, each row the part of the place inside the district.
  fips: The place's five-digit county FIPS code (Alaska's house districts: 029 and the district number, after the state's 02).
  place: The place's name.
  candidate_a: Candidate A.
  party_a: Candidate A's party.
  votes_a: Candidate A's votes counted in the place.
  candidate_b: Candidate B.
  party_b: Candidate B's party.
  votes_b: Candidate B's votes counted in the place.
  votes_other: Every other vote counted in the place (other candidates and write-ins): total_votes minus A and B.
  total_votes: All votes counted in the place.
  finished: yes where the source marks the place as fully counted, no where it marks it as still counting, empty where it does not say.
  count_updated_utc: As in races.

LEGISLATURES: State legislatures, by district and candidate
One row per candidate per state legislative district on the 2026 ballot, as the state's results name them. A district that elects several members lists each.

  state: Two-letter state code.
  chamber: upper (the state senate) or lower (the house or assembly).
  district: The district as the office names it.
  contest: The contest's title as the office prints it.
  seats: Members the district elects in this contest.
  candidate: The candidate's name.
  party: As in races.
  votes: Votes counted for the candidate.
  share_pct: Share of all votes counted in the contest, in percent.
  leads: yes for the candidate (or candidates, where several seats are filled) ahead in the count; legislative seats are not called here.
  uncontested: yes where only one candidate ran for each seat.
  held_by_before: The party or parties that held the seat before the election, where known.
  total_votes: All votes counted in the contest.
  precincts_reporting: Precincts reporting, where the office says.
  precincts_total: Precincts in the district, where the office says.
  count_updated_utc: When the source last says it counted, UTC, where it says.
  source: Who counted: the state's election office, or civicAPI, which gathers the states' and counties' own counts. A civicAPI row must credit civicAPI.
  source_url: Where the count was read.
  source_read_utc: When Call the Map last read the source, UTC (ISO 8601).

MEASURES: Ballot measures
One row per statewide ballot measure: yes and no votes and where the count stands against the share the state requires.

  state: Two-letter state code.
  measure: The measure's title as the office prints it.
  yes_votes: Yes votes counted.
  no_votes: No votes counted.
  yes_share_pct: Yes as a share of yes and no, in percent.
  needs_pct: The yes share the measure needs to pass: 50 unless the state asks more (Florida's amendments, 60).
  on_the_count: passing or failing as counted so far, against needs_pct; empty with no votes.
  count_updated_utc: When the source last says it counted, UTC, where it says.
  source: Who counted: the state's election office, or civicAPI, which gathers the states' and counties' own counts. A civicAPI row must credit civicAPI.
  source_url: Where the count was read.
  source_read_utc: When Call the Map last read the source, UTC (ISO 8601).

MEASURE-COUNTIES: Ballot measures, by county
One row per measure, county and choice (Yes, No, or the choices the office prints).

  state: Two-letter state code.
  measure: As in measures.
  county: The county as the office names it.
  choice: Yes, No, or the office's own wording of the choice.
  votes: Votes counted for the choice in the county.

PRECINCTS: Precinct returns
One row per precinct, for the races whose official precinct returns the results pages map (a state that publishes precinct returns that join the precinct shapes by the office's own identifier, with 95% of the votes placed). Precincts that could not be placed are not listed; their votes stay in the county totals.

  race_id: As in races.
  state: Two-letter state code.
  precinct_id: The precinct: its county's FIPS code, a dash, and the 2024 precinct name or code.
  fips: The precinct's county FIPS code.
  precinct: The precinct's name or code.
  candidate_a: As in counties.
  votes_a: Candidate A's votes in the precinct.
  candidate_b: As in counties.
  votes_b: Candidate B's votes in the precinct.
  votes_other: Every other vote in the precinct.
  total_votes: All votes counted in the precinct.
  source: Who counted: the state's election office, or civicAPI, which gathers the states' and counties' own counts. A civicAPI row must credit civicAPI.
  source_url: Where the count was read.
  source_read_utc: When Call the Map last read the source, UTC (ISO 8601).

Questions and corrections: https://www.callthemap.com/about#contact
