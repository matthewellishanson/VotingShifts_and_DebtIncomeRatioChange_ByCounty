import { useEffect, useState } from 'react'
import { DEBT_COLORS, formatDifference, getOfficeMetrics } from '../lib/data'
import type { CountyRecord, DebtTransition, Office } from '../types'

interface DotPlotProps {
  counties: CountyRecord[]
  office: Office
  selectedFips: string
  onSelect: (fips: string) => void
}

const groups: Array<{ key: Exclude<DebtTransition, null>; label: string }> = [
  { key: 'higher_category', label: 'Higher category' },
  { key: 'same_category', label: 'Same reported category' },
  { key: 'lower_category', label: 'Lower category' },
]

export function DotPlot({
  counties,
  office,
  selectedFips,
  onSelect,
}: DotPlotProps) {
  const isNarrow = useNarrowLayout()
  const available = counties
    .map((county) => ({ county, value: getOfficeMetrics(county, office).difference }))
    .filter(
      (item): item is { county: CountyRecord; value: number } => item.value !== null,
    )
  const unavailable = counties.length - available.length
  const max = Math.max(10, ...available.map(({ value }) => Math.abs(value)))
  const domain = Math.ceil(max / 5) * 5
  const width = isNarrow ? 500 : 820
  const height = 330
  const left = isNarrow ? 126 : 154
  const right = isNarrow ? 14 : 24
  const top = 44
  const rowHeight = 78
  const plotWidth = width - left - right
  const scaleX = (value: number) => left + ((value + domain) / (domain * 2)) * plotWidth
  const ticks = [-domain, -domain / 2, 0, domain / 2, domain]

  return (
    <figure className="dot-figure panel" aria-labelledby="dot-title">
      <div className="figure-heading">
        <div>
          <p className="eyebrow">County distribution</p>
          <h2 id="dot-title">Margin differences within each debt-transition group</h2>
        </div>
        <p className="figure-note">Each dot is one equally weighted county.</p>
      </div>
      <svg
        className="dot-plot"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-labelledby="dot-title dot-description"
      >
        <desc id="dot-description">
          A grouped dot plot showing county-level 2026 office minus 2024 presidential
          Democratic-minus-Republican margin differences. Positive values are toward
          Democrats. The accompanying table provides every exact value.
        </desc>
        {ticks.map((tick) => {
          const x = scaleX(tick)
          return (
            <g key={tick}>
              <line className={tick === 0 ? 'zero-line' : 'grid-line'} x1={x} x2={x} y1={top - 14} y2={top + rowHeight * 3 - 28} />
              <text className="axis-label" x={x} y={height - 24} textAnchor="middle">
                {tick > 0 ? '+' : ''}{tick}
              </text>
            </g>
          )
        })}
        {groups.map((group, groupIndex) => {
          const items = available
            .filter(({ county }) => county.debt_transition === group.key)
            .sort((a, b) => a.value - b.value)
          const baseY = top + groupIndex * rowHeight + 26
          const positions = packDots(items.map(({ value }) => scaleX(value)), baseY)
          return (
            <g key={group.key}>
              <text className="group-label" x={left - 14} y={baseY + 4} textAnchor="end">
                {isNarrow && group.key === 'same_category' ? 'Same category' : group.label}
              </text>
              <text className="group-count" x={left - 14} y={baseY + 20} textAnchor="end">
                n={items.length}
              </text>
              {items.map(({ county, value }, index) => (
                <circle
                  key={county.county_fips}
                  cx={positions[index][0]}
                  cy={positions[index][1]}
                  r={selectedFips === county.county_fips ? 6.5 : 4.25}
                  fill={DEBT_COLORS[group.key]}
                  className={`county-dot${selectedFips === county.county_fips ? ' is-selected' : ''}`}
                  role="button"
                  tabIndex={0}
                  aria-pressed={selectedFips === county.county_fips}
                  aria-label={`${county.county_name} County: ${formatDifference(value)}`}
                  onClick={() => onSelect(county.county_fips)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault()
                      onSelect(county.county_fips)
                    }
                  }}
                >
                  <title>{`${county.county_name} County — ${formatDifference(value)}`}</title>
                </circle>
              ))}
            </g>
          )
        })}
        <text className="axis-title" x={left + plotWidth / 2} y={height - 4} textAnchor="middle">
          2026 office margin minus 2024 presidential margin (percentage points)
        </text>
      </svg>
      <p className="chart-footnote">
        Positive values move toward Democrats in the observed margins; negative values
        move toward Republicans. {unavailable > 0 ? `${unavailable} unavailable counties are not drawn as zeros.` : 'All 105 counties have an available value for this office.'}
      </p>
    </figure>
  )
}

function useNarrowLayout(): boolean {
  const [isNarrow, setIsNarrow] = useState(() => window.innerWidth < 640)
  useEffect(() => {
    const update = () => setIsNarrow(window.innerWidth < 640)
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [])
  return isNarrow
}

function packDots(xs: number[], baseY: number): Array<[number, number]> {
  const placed: Array<[number, number]> = []
  const offsets = [0, -10, 10, -20, 20, -30, 30]
  for (const x of xs) {
    const offset =
      offsets.find((candidate) =>
        placed.every(([placedX, placedY]) =>
          Math.hypot(x - placedX, baseY + candidate - placedY) >= 9,
        ),
      ) ?? 0
    placed.push([x, baseY + offset])
  }
  return placed
}
