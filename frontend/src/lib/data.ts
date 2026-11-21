import type { CountyRecord, Office, OfficeMetrics } from '../types'

export const OFFICE_LABELS: Record<Office, string> = {
  governor: '2026 governor',
  house: '2026 U.S. House',
  senate: '2026 U.S. Senate',
}

export const DEBT_LABELS = {
  higher_category: 'Moved to a higher category',
  same_category: 'Same reported category',
  lower_category: 'Moved to a lower category',
  unavailable: 'Debt transition unavailable',
} as const

export const DEBT_COLORS = {
  higher_category: '#7c4056',
  same_category: '#d3b86b',
  lower_category: '#267078',
} as const

export function getOfficeMetrics(
  county: CountyRecord,
  office: Office,
): OfficeMetrics {
  return {
    label: OFFICE_LABELS[office],
    shortLabel:
      office === 'house'
        ? 'House'
        : office[0].toUpperCase() + office.slice(1),
    margin: county[`${office}_2026_margin_pp`],
    difference: county[`${office}_2026_minus_president_2024_pp`],
    demVotes: county[`${office}_2026_dem_votes`],
    repVotes: county[`${office}_2026_rep_votes`],
    totalVotes: county[`${office}_2026_total_votes`],
    raceIds: county[`${office}_2026_race_ids`],
    sourceFinished: county[`${office}_2026_source_finished`],
  }
}

export function formatDifference(value: number | null): string {
  if (value === null) return 'Unavailable'
  const signed = `${value > 0 ? '+' : ''}${value.toFixed(1)} pp`
  if (value === 0) return `${signed} (no margin difference)`
  return `${signed} toward ${value > 0 ? 'Democrats' : 'Republicans'}`
}

export function formatMargin(value: number | null): string {
  if (value === null) return 'Unavailable'
  return `${value > 0 ? '+' : ''}${value.toFixed(1)} pp D-R`
}

export function formatRange(low: number | null, high: number | null): string {
  if (low === null) return 'Unavailable'
  return high === null ? `${low} or higher` : `${low}-${high}`
}

export function formatVotes(value: number | null): string {
  return value === null ? 'Unavailable' : value.toLocaleString('en-US')
}

export function debtLabel(county: CountyRecord): string {
  return county.debt_transition
    ? DEBT_LABELS[county.debt_transition]
    : DEBT_LABELS.unavailable
}

export function shiftColor(value: number | null, domain: number): string {
  if (value === null) return 'url(#missing-pattern)'
  const amount = Math.min(1, Math.abs(value) / Math.max(domain, 1))
  return value < 0
    ? mix('#f3ead8', '#9b4a35', amount)
    : mix('#f3ead8', '#176b70', amount)
}

function mix(start: string, end: string, amount: number): string {
  const startRgb = hexToRgb(start)
  const endRgb = hexToRgb(end)
  const channels = startRgb.map((channel, index) =>
    Math.round(channel + (endRgb[index] - channel) * amount),
  )
  return `rgb(${channels.join(', ')})`
}

function hexToRgb(hex: string): number[] {
  return [1, 3, 5].map((offset) =>
    Number.parseInt(hex.slice(offset, offset + 2), 16),
  )
}
