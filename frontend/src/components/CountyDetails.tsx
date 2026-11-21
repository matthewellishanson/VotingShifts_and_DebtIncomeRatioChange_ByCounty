import {
  debtLabel,
  formatDifference,
  formatMargin,
  formatRange,
  getOfficeMetrics,
} from '../lib/data'
import type { CountyRecord, Office } from '../types'

interface CountyDetailsProps {
  county: CountyRecord | null
  office: Office
}

export function CountyDetails({ county, office }: CountyDetailsProps) {
  if (!county) {
    return (
      <aside className="detail-panel panel" aria-live="polite">
        <p className="eyebrow">County details</p>
        <h2>Select a county</h2>
        <p>Use the map, dot plot, search, or results table to inspect exact values.</p>
      </aside>
    )
  }
  const metrics = getOfficeMetrics(county, office)
  return (
    <aside className="detail-panel panel" aria-live="polite" aria-labelledby="detail-title">
      <p className="eyebrow">County details · FIPS {county.county_fips}</p>
      <h2 id="detail-title">{county.county_name} County</h2>
      <div className="detail-lede">
        <strong>{formatDifference(metrics.difference)}</strong>
        <span>{metrics.label} versus 2024 president</span>
      </div>
      <dl className="metric-list">
        <div>
          <dt>2024 presidential margin</dt>
          <dd>{formatMargin(county.president_2024_margin_pp)}</dd>
        </div>
        <div>
          <dt>{metrics.label} margin</dt>
          <dd>{formatMargin(metrics.margin)}</dd>
        </div>
        <div>
          <dt>2024 all-candidate votes</dt>
          <dd>{formatNumber(county.president_2024_total_votes)}</dd>
        </div>
        <div>
          <dt>2026 all-candidate votes</dt>
          <dd>{formatNumber(metrics.totalVotes)}</dd>
        </div>
      </dl>
      <div className="debt-detail">
        <h3>Household debt-to-income category</h3>
        <p><strong>{debtLabel(county)}</strong></p>
        <p>
          {county.debt_start_period}: {formatRange(county.debt_start_low, county.debt_start_high)}
          <span aria-hidden="true"> → </span>
          <span className="sr-only"> to </span>
          {county.debt_end_period}: {formatRange(county.debt_end_low, county.debt_end_high)}
        </p>
        <small>Published source ranges; an open upper bound remains open. No midpoint or exact debt change is inferred.</small>
      </div>
      <div className="status-detail">
        <span className="status-chip">Provisional / unverified</span>
        <p>
          2026 source county status: {metrics.sourceFinished === true ? 'marked finished' : 'not marked finished'}.
          This is not certification. Race ID{metrics.raceIds.includes(';') ? 's' : ''}: {metrics.raceIds || 'unavailable'}.
        </p>
      </div>
    </aside>
  )
}

function formatNumber(value: number | null): string {
  return value === null ? 'Unavailable' : new Intl.NumberFormat('en-US').format(value)
}
