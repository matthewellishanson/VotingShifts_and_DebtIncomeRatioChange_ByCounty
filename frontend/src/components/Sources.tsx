import type { GeometryData } from '../types'

export function Sources({ geometry }: { geometry: GeometryData }) {
  return (
    <section className="sources panel" aria-labelledby="sources-title">
      <p className="eyebrow">Methods and lineage</p>
      <h2 id="sources-title">Sources, periods, and limits</h2>
      <div className="source-grid">
        <article>
          <h3>Household debt categories</h3>
          <p>
            Federal Reserve Board household debt-to-income category ranges,
            <strong> 2024 Q3 through 2025 Q4</strong>. Ranges are displayed as
            published; same category does not mean zero change.
          </p>
          <a href="https://www.federalreserve.gov/releases/z1/dataviz/household_debt/">Fed data overview</a>
          <a href="https://www.federalreserve.gov/econres/notes/feds-notes/household-debt-to-income-ratios-in-the-enhanced-financial-accounts-20180109.html">Fed methodology</a>
        </article>
        <article>
          <h3>2024 presidential returns</h3>
          <p>
            MIT Election Data and Science Lab county presidential returns,
            year 2024; source row version <strong>20260225</strong>. Dataset-version
            citation and terms still require publication review.
          </p>
          <a href="https://doi.org/10.7910/DVN/VOQCHQ">MEDSL Dataverse record</a>
        </article>
        <article>
          <h3>2026 comparison offices</h3>
          <p>
            Call the Map snapshot published <strong>2026-11-18 21:33:46 UTC</strong>;
            CC BY 4.0. Every included county/part row is not marked finished=yes.
            Counts are provisional and have not been independently verified.
          </p>
          <a href="https://www.callthemap.com/results/data">Call the Map downloads</a>
          <a href="https://civicapi.org">civicAPI attribution</a>
        </article>
        <article>
          <h3>County boundaries</h3>
          <p>
            {geometry.metadata.source}, <strong>{geometry.metadata.vintage}</strong>,
            {' '}{geometry.metadata.scale}; Kansas subset retrieved {geometry.metadata.retrieved}.
            Cartographic boundaries are simplified for thematic/web mapping and
            are not for legal or area/perimeter analysis. U.S. government works
            generally are not copyright-protected in the United States; Census
            is cited as the source.
          </p>
          <a href={geometry.metadata.source_page}>Census boundary source page</a>
        </article>
      </div>
      <div className="method-callout">
        <strong>Margin definition:</strong>{' '}
        100 × (Democratic votes − Republican votes) ÷ all candidate votes.
        The displayed difference is the selected 2026 office margin minus the
        2024 presidential margin, in percentage points. Offices remain separate.
        The House option is president-to-House, not a same-office change; no 2024
        House input is included.
      </div>
      <p>
        This exploratory county-level comparison does not show that household debt
        caused electoral change or that indebted individuals changed their votes.
        Source verification is separate from parser correctness and internal-total checks.
      </p>
    </section>
  )
}
