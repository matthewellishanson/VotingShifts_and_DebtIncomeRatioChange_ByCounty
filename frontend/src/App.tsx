import { useEffect, useMemo, useState } from 'react'
import { CountyDetails } from './components/CountyDetails'
import { CountyMap } from './components/CountyMap'
import { DotPlot } from './components/DotPlot'
import { ResultsTable } from './components/ResultsTable'
import { Sources } from './components/Sources'
import { getOfficeMetrics } from './lib/data'
import { readViewState, writeViewState } from './lib/urlState'
import type {
  CountyRecord,
  DemoData,
  GeometryData,
  MapView,
  Office,
  ViewState,
} from './types'

interface LoadedData {
  demo: DemoData
  geometry: GeometryData
  counties: CountyRecord[]
}

const DEFAULT_STATE: ViewState = {
  office: 'governor',
  mapView: 'shift',
  county: '',
  query: '',
}

export default function App() {
  const [loaded, setLoaded] = useState<LoadedData | null>(null)
  const [error, setError] = useState('')
  const [viewState, setViewState] = useState<ViewState>(DEFAULT_STATE)
  const [copyStatus, setCopyStatus] = useState('Copy view link')

  useEffect(() => {
    let active = true
    Promise.all([
      fetch('/data/county_demo.json').then(checkResponse).then((response) => response.json()),
      fetch('/data/ks_counties.json').then(checkResponse).then((response) => response.json()),
    ])
      .then(([demo, geometry]: [DemoData, GeometryData]) => {
        if (!active) return
        const counties = demo.counties
          .filter((county) => county.state === 'KS')
          .sort((a, b) => a.county_name.localeCompare(b.county_name))
        const countyIds = new Set(counties.map((county) => county.county_fips))
        const geometryIds = new Set(
          geometry.features.map((feature) => feature.properties.county_fips),
        )
        if (
          counties.length !== 105 ||
          geometry.features.length !== 105 ||
          [...countyIds].some((fips) => !geometryIds.has(fips))
        ) {
          throw new Error('Prepared Kansas data and geometry do not contain the same 105 counties.')
        }
        setLoaded({ demo, geometry, counties })
        setViewState(readViewState(window.location.search, countyIds))
      })
      .catch((caught: unknown) => {
        if (active) setError(caught instanceof Error ? caught.message : 'Could not load prepared data.')
      })
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!loaded) return
    const countyIds = new Set(loaded.counties.map((county) => county.county_fips))
    const onPopState = () => setViewState(readViewState(window.location.search, countyIds))
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [loaded])

  const updateView = (
    patch: Partial<ViewState>,
    historyMode: 'push' | 'replace' = 'push',
  ) => {
    const next = { ...viewState, ...patch }
    setViewState(next)
    const url = `${window.location.pathname}${writeViewState(next)}${window.location.hash}`
    window.history[historyMode === 'push' ? 'pushState' : 'replaceState']({}, '', url)
  }

  const filteredCounties = useMemo(() => {
    if (!loaded) return []
    const query = viewState.query.trim().toLocaleLowerCase('en-US')
    if (!query) return loaded.counties
    return loaded.counties.filter(
      (county) =>
        county.county_name.toLocaleLowerCase('en-US').includes(query) ||
        county.county_fips.includes(query),
    )
  }, [loaded, viewState.query])

  if (error) {
    return (
      <main id="main" className="app-shell">
        <section className="load-state" role="alert">
          <h1>Prepared data could not be loaded</h1>
          <p>{error}</p>
          <p>Run the root prepare-data command, then restart the Vite server.</p>
        </section>
      </main>
    )
  }
  if (!loaded) {
    return <main id="main" className="load-state" aria-busy="true">Loading the validated Kansas snapshot…</main>
  }

  const selectedCounty =
    loaded.counties.find((county) => county.county_fips === viewState.county) ?? null
  const unavailable = loaded.counties.filter(
    (county) => getOfficeMetrics(county, viewState.office).difference === null,
  ).length
  const counts = countTransitions(loaded.counties)

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopyStatus('Link copied')
    } catch {
      setCopyStatus('Copy unavailable')
    }
    window.setTimeout(() => setCopyStatus('Copy view link'), 1800)
  }

  return (
    <>
      <header className="site-header">
        <a className="brand" href="./" aria-label="Kansas county research demo home">
          <span>KS</span> County research demo
        </a>
        <span className="status-chip">Provisional / unverified</span>
      </header>
      <main id="main" className="app-shell">
        <section className="hero" aria-labelledby="page-title">
          <p className="eyebrow">Kansas · 105 counties · exploratory comparison</p>
          <h1 id="page-title">How county margins differ across debt-category transitions</h1>
          <p className="hero-summary">
            The default view compares the 2026 gubernatorial margin with the 2024
            presidential margin. It describes county aggregates and does not establish
            that household debt caused electoral change.
          </p>
          <div className="coverage-strip" aria-label="Current view coverage">
            <span><strong>105</strong> counties matched</span>
            <span><strong>{counts.higher_category}</strong> higher category</span>
            <span><strong>{counts.same_category}</strong> same reported category</span>
            <span><strong>{counts.lower_category}</strong> lower category</span>
            <span><strong>{unavailable}</strong> unavailable comparisons</span>
          </div>
        </section>

        <section className="controls panel" aria-label="View controls">
          <div className="control-group">
            <label htmlFor="office">Comparison office</label>
            <select
              id="office"
              value={viewState.office}
              onChange={(event) => updateView({ office: event.target.value as Office })}
            >
              <option value="governor">2026 governor vs. 2024 president</option>
              <option value="house">2026 U.S. House vs. 2024 president</option>
              <option value="senate">2026 U.S. Senate vs. 2024 president</option>
            </select>
          </div>
          <fieldset className="segmented-control">
            <legend>Map color</legend>
            {([
              ['shift', 'Electoral difference'],
              ['debt', 'Debt transition'],
            ] as Array<[MapView, string]>).map(([value, label]) => (
              <label key={value}>
                <input
                  type="radio"
                  name="map-view"
                  value={value}
                  checked={viewState.mapView === value}
                  onChange={() => updateView({ mapView: value })}
                />
                <span>{label}</span>
              </label>
            ))}
          </fieldset>
          <div className="control-group search-control">
            <label htmlFor="county-search">Search county or FIPS</label>
            <input
              id="county-search"
              type="search"
              value={viewState.query}
              placeholder="e.g. Sedgwick or 20173"
              onChange={(event) => updateView({ query: event.target.value }, 'replace')}
            />
          </div>
          <button className="secondary-button" type="button" onClick={copyLink}>
            {copyStatus}
          </button>
          <p className="active-summary">
            Active view: {viewState.office === 'house' ? 'U.S. House' : viewState.office} ·{' '}
            {viewState.mapView === 'shift' ? 'electoral difference map' : 'debt transition map'}
            {selectedCounty ? ` · ${selectedCounty.county_name} County selected` : ''}
          </p>
        </section>

        <section className="primary-grid" aria-label="Map and selected county details">
          <CountyMap
            counties={loaded.counties}
            geometry={loaded.geometry}
            office={viewState.office}
            mapView={viewState.mapView}
            selectedFips={viewState.county}
            onSelect={(county) => updateView({ county })}
          />
          <CountyDetails county={selectedCounty} office={viewState.office} />
        </section>

        <DotPlot
          counties={loaded.counties}
          office={viewState.office}
          selectedFips={viewState.county}
          onSelect={(county) => updateView({ county })}
        />

        <ResultsTable
          counties={filteredCounties}
          office={viewState.office}
          selectedFips={viewState.county}
          onSelect={(county) => updateView({ county })}
        />

        <Sources geometry={loaded.geometry} />
      </main>
      <footer>
        Offline static research demo · No live feed, backend, or publication claim
      </footer>
    </>
  )
}

async function checkResponse(response: Response): Promise<Response> {
  if (!response.ok) throw new Error(`Data request failed (${response.status}).`)
  return response
}

function countTransitions(counties: CountyRecord[]) {
  return counties.reduce(
    (counts, county) => {
      if (county.debt_transition) counts[county.debt_transition] += 1
      return counts
    },
    { higher_category: 0, same_category: 0, lower_category: 0 },
  )
}
