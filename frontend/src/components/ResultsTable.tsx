import {
  debtLabel,
  formatDifference,
  formatMargin,
  getOfficeMetrics,
} from '../lib/data'
import type { CountyRecord, Office } from '../types'

interface ResultsTableProps {
  counties: CountyRecord[]
  office: Office
  selectedFips: string
  onSelect: (fips: string) => void
}

export function ResultsTable({
  counties,
  office,
  selectedFips,
  onSelect,
}: ResultsTableProps) {
  return (
    <section className="table-section panel" aria-labelledby="table-title">
      <div className="figure-heading">
        <div>
          <p className="eyebrow">Exact lookup</p>
          <h2 id="table-title">Search results ({counties.length})</h2>
        </div>
        <p className="figure-note">Select a row to link all views.</p>
      </div>
      <div className="table-scroll" tabIndex={0} aria-label="Scrollable county results">
        <table>
          <thead>
            <tr>
              <th scope="col">County</th>
              <th scope="col">Debt transition</th>
              <th scope="col">2024 president margin</th>
              <th scope="col">2026 {office === 'house' ? 'House' : office} margin</th>
              <th scope="col">Difference</th>
            </tr>
          </thead>
          <tbody>
            {counties.map((county) => {
              const metrics = getOfficeMetrics(county, office)
              return (
                <tr
                  key={county.county_fips}
                  className={selectedFips === county.county_fips ? 'is-selected' : ''}
                >
                  <th scope="row">
                    <button type="button" onClick={() => onSelect(county.county_fips)}>
                      {county.county_name}
                    </button>
                    <small>{county.county_fips}</small>
                  </th>
                  <td>{debtLabel(county)}</td>
                  <td>{formatMargin(county.president_2024_margin_pp)}</td>
                  <td>{formatMargin(metrics.margin)}</td>
                  <td className={metrics.difference === null ? 'is-unavailable' : ''}>
                    {formatDifference(metrics.difference)}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      {counties.length === 0 && (
        <p className="empty-state">No Kansas counties match this search.</p>
      )}
    </section>
  )
}
