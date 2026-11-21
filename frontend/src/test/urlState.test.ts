import { describe, expect, it } from 'vitest'
import { readViewState, writeViewState } from '../lib/urlState'

const counties = new Set(['20001', '20173'])

describe('shareable view state', () => {
  it('normalizes unknown values and invalid county ids', () => {
    expect(readViewState('?office=mayor&view=globe&county=36000', counties)).toEqual({
      office: 'governor',
      mapView: 'shift',
      county: '',
      query: '',
    })
  })

  it('writes stable ids while omitting defaults', () => {
    expect(
      writeViewState({
        office: 'senate',
        mapView: 'debt',
        county: '20173',
        query: 'Sedgwick',
      }),
    ).toBe('?office=senate&view=debt&county=20173&q=Sedgwick')
  })
})
