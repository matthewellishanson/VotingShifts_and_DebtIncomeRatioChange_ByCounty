import { useMemo } from 'react'
import {
  DEBT_COLORS,
  debtLabel,
  formatDifference,
  getOfficeMetrics,
  shiftColor,
} from '../lib/data'
import { createProjection, featurePath } from '../lib/geometry'
import type {
  CountyRecord,
  GeometryData,
  MapView,
  Office,
} from '../types'

interface CountyMapProps {
  counties: CountyRecord[]
  geometry: GeometryData
  office: Office
  mapView: MapView
  selectedFips: string
  onSelect: (fips: string) => void
}

export function CountyMap({
  counties,
  geometry,
  office,
  mapView,
  selectedFips,
  onSelect,
}: CountyMapProps) {
  const countyByFips = useMemo(
    () => new Map(counties.map((county) => [county.county_fips, county])),
    [counties],
  )
  const projection = useMemo(() => createProjection(geometry), [geometry])
  const values = counties
    .map((county) => getOfficeMetrics(county, office).difference)
    .filter((value): value is number => value !== null)
  const domain = Math.max(10, ...values.map((value) => Math.abs(value)))
  const mapTitle =
    mapView === 'shift'
      ? `${getOfficeMetrics(counties[0], office).shortLabel} minus 2024 presidential margin, percentage points`
      : 'Household debt-to-income category transition, 2024 Q3 to 2025 Q4'

  return (
    <figure className="map-figure panel" aria-labelledby="map-title">
      <div className="figure-heading">
        <div>
          <p className="eyebrow">County map</p>
          <h2 id="map-title">{mapTitle}</h2>
        </div>
        <p className="figure-note">Select a county for exact values.</p>
      </div>
      <svg
        className="county-map"
        viewBox={`0 0 ${projection.width} ${projection.height}`}
        role="img"
        aria-labelledby="map-title map-description"
      >
        <desc id="map-description">
          A thematic map of all 105 Kansas counties. Every county is also listed
          in the searchable results table below.
        </desc>
        <defs>
          <pattern
            id="missing-pattern"
            width="8"
            height="8"
            patternUnits="userSpaceOnUse"
            patternTransform="rotate(45)"
          >
            <rect width="8" height="8" fill="#ece8df" />
            <line x1="0" y1="0" x2="0" y2="8" stroke="#8c877d" strokeWidth="2" />
          </pattern>
        </defs>
        <g aria-label="Kansas counties">
          {geometry.features.map((feature, index) => {
            const fips = feature.properties.county_fips
            const county = countyByFips.get(fips)
            if (!county) return null
            const metrics = getOfficeMetrics(county, office)
            const fill =
              mapView === 'shift'
                ? shiftColor(metrics.difference, domain)
                : county.debt_transition
                  ? DEBT_COLORS[county.debt_transition]
                  : 'url(#missing-pattern)'
            const label =
              mapView === 'shift'
                ? formatDifference(metrics.difference)
                : debtLabel(county)
            return (
              <path
                key={fips}
                d={featurePath(geometry, index, projection)}
                fill={fill}
                fillRule="evenodd"
                className={`county-shape${selectedFips === fips ? ' is-selected' : ''}`}
                vectorEffect="non-scaling-stroke"
                role="button"
                tabIndex={0}
                aria-pressed={selectedFips === fips}
                aria-label={`${county.county_name} County: ${label}`}
                onClick={() => onSelect(fips)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault()
                    onSelect(fips)
                  }
                }}
              >
                <title>{`${county.county_name} County — ${label}`}</title>
              </path>
            )
          })}
        </g>
      </svg>
      {mapView === 'shift' ? (
        <ShiftLegend domain={domain} />
      ) : (
        <DebtLegend />
      )}
    </figure>
  )
}

function ShiftLegend({ domain }: { domain: number }) {
  const rounded = Math.ceil(domain / 5) * 5
  return (
    <div className="map-key" aria-label="Electoral margin-difference color key">
      <span>More Republican</span>
      <span className="gradient-key" aria-hidden="true" />
      <span>More Democratic</span>
      <small>−{rounded} to +{rounded} percentage points; hatch = unavailable</small>
    </div>
  )
}

function DebtLegend() {
  return (
    <div className="categorical-key" aria-label="Debt transition color key">
      {(['higher_category', 'same_category', 'lower_category'] as const).map(
        (transition) => (
          <span key={transition}>
            <i style={{ background: DEBT_COLORS[transition] }} aria-hidden="true" />
            {transition === 'higher_category'
              ? 'Higher category'
              : transition === 'same_category'
                ? 'Same reported category'
                : 'Lower category'}
          </span>
        ),
      )}
      <small>Category movement only; same category does not mean zero debt change.</small>
    </div>
  )
}
