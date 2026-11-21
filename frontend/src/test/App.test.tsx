import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import demo from '../../public/data/county_demo.json'
import geometry from '../../public/data/ks_counties.json'
import App from '../App'

describe('coordinated Kansas research view', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/')
    vi.stubGlobal(
      'fetch',
      vi.fn((url: string) =>
        Promise.resolve(
          new Response(JSON.stringify(url.includes('county_demo') ? demo : geometry), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          }),
        ),
      ),
    )
    render(<App />)
  })

  afterEach(() => vi.unstubAllGlobals())

  it('loads the 105-county default governor comparison', async () => {
    expect(
      await screen.findByRole('heading', {
        name: /How county margins differ across debt-category transitions/i,
      }),
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Comparison office')).toHaveValue('governor')
    expect(screen.getByLabelText('Current view coverage')).toHaveTextContent('105 counties matched')
    expect(screen.getByRole('heading', { name: 'Search results (105)' })).toBeInTheDocument()
    expect(screen.getAllByText('Provisional / unverified').length).toBeGreaterThan(0)
  })

  it('filters the table, selects a county, and preserves selection in the URL', async () => {
    const user = userEvent.setup()
    await screen.findByRole('heading', { name: 'Search results (105)' })
    await user.type(screen.getByLabelText('Search county or FIPS'), 'Sedgwick')
    const section = screen.getByRole('heading', { name: 'Search results (1)' }).closest('section')!
    await user.click(within(section).getByRole('button', { name: 'SEDGWICK' }))
    expect(screen.getByRole('heading', { name: 'SEDGWICK County' })).toBeInTheDocument()
    expect(window.location.search).toContain('county=20173')
    expect(window.location.search).toContain('q=Sedgwick')
  })

  it('supports keyboard county selection from the SVG map', async () => {
    const user = userEvent.setup()
    await screen.findByRole('heading', { name: 'Search results (105)' })
    const map = screen.getByLabelText('Kansas counties')
    const allen = within(map).getByRole('button', { name: /^ALLEN County:/ })
    allen.focus()
    await user.keyboard('{Enter}')
    expect(screen.getByRole('heading', { name: 'ALLEN County' })).toBeInTheDocument()
    expect(window.location.search).toContain('county=20001')
  })

  it('changes office and debt-map mode without losing the analytical labels', async () => {
    const user = userEvent.setup()
    await screen.findByRole('heading', { name: 'Search results (105)' })
    await user.selectOptions(screen.getByLabelText('Comparison office'), 'house')
    await user.click(screen.getByLabelText('Debt transition'))
    expect(screen.getByText(/Active view: U.S. House.*debt transition map/)).toBeInTheDocument()
    expect(screen.getByText('Category movement only; same category does not mean zero debt change.')).toBeInTheDocument()
    expect(window.location.search).toContain('office=house')
    expect(window.location.search).toContain('view=debt')
  })
})
