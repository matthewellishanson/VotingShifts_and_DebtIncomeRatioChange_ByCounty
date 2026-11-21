import type { MapView, Office, ViewState } from '../types'

const offices: Office[] = ['governor', 'house', 'senate']
const mapViews: MapView[] = ['shift', 'debt']

export function readViewState(
  search: string,
  countyIds: Set<string>,
): ViewState {
  const params = new URLSearchParams(search)
  const office = params.get('office') as Office | null
  const mapView = params.get('view') as MapView | null
  const county = params.get('county') ?? ''
  return {
    office: office && offices.includes(office) ? office : 'governor',
    mapView: mapView && mapViews.includes(mapView) ? mapView : 'shift',
    county: countyIds.has(county) ? county : '',
    query: (params.get('q') ?? '').slice(0, 80),
  }
}

export function writeViewState(state: ViewState): string {
  const params = new URLSearchParams()
  if (state.office !== 'governor') params.set('office', state.office)
  if (state.mapView !== 'shift') params.set('view', state.mapView)
  if (state.county) params.set('county', state.county)
  if (state.query) params.set('q', state.query)
  const value = params.toString()
  return value ? `?${value}` : window.location.pathname
}
