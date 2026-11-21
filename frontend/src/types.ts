export type Office = 'governor' | 'house' | 'senate'
export type MapView = 'shift' | 'debt'
export type DebtTransition =
  | 'higher_category'
  | 'same_category'
  | 'lower_category'
  | null

export interface CountyRecord {
  state: string
  county_fips: string
  county_name: string
  debt_start_period: string
  debt_end_period: string
  debt_start_low: number | null
  debt_start_high: number | null
  debt_end_low: number | null
  debt_end_high: number | null
  debt_transition: DebtTransition
  president_2024_dem_votes: number | null
  president_2024_rep_votes: number | null
  president_2024_total_votes: number | null
  president_2024_margin_pp: number | null
  president_source_version: string
  president_geography_status: string
  comparison_year: number
  results_status: string
  house_2026_dem_votes: number | null
  house_2026_rep_votes: number | null
  house_2026_total_votes: number | null
  house_2026_margin_pp: number | null
  house_2026_minus_president_2024_pp: number | null
  house_2026_race_ids: string
  house_2026_source_finished: boolean | null
  governor_2026_dem_votes: number | null
  governor_2026_rep_votes: number | null
  governor_2026_total_votes: number | null
  governor_2026_margin_pp: number | null
  governor_2026_minus_president_2024_pp: number | null
  governor_2026_race_ids: string
  governor_2026_source_finished: boolean | null
  senate_2026_dem_votes: number | null
  senate_2026_rep_votes: number | null
  senate_2026_total_votes: number | null
  senate_2026_margin_pp: number | null
  senate_2026_minus_president_2024_pp: number | null
  senate_2026_race_ids: string
  senate_2026_source_finished: boolean | null
}

export interface DemoData {
  metadata: {
    pipeline_status: string
    county_rows: number
    limitations: string[]
    [key: string]: unknown
  }
  counties: CountyRecord[]
}

export type Position = [number, number]
export type PolygonCoordinates = Position[][]

export interface CountyFeature {
  type: 'Feature'
  properties: {
    county_fips: string
    county_name: string
    county_label: string
    state: string
  }
  geometry:
    | { type: 'Polygon'; coordinates: PolygonCoordinates }
    | { type: 'MultiPolygon'; coordinates: PolygonCoordinates[] }
}

export interface GeometryData {
  type: 'FeatureCollection'
  metadata: {
    source: string
    source_url: string
    source_page: string
    vintage: number
    scale: string
    retrieved: string
    archive_sha256: string
    scope: string
  }
  features: CountyFeature[]
}

export interface OfficeMetrics {
  label: string
  shortLabel: string
  margin: number | null
  difference: number | null
  demVotes: number | null
  repVotes: number | null
  totalVotes: number | null
  raceIds: string
  sourceFinished: boolean | null
}

export interface ViewState {
  office: Office
  mapView: MapView
  county: string
  query: string
}
