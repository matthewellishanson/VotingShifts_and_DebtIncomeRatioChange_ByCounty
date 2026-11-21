"""Convert the supplied BLS rolling 14-month county workbook, offline."""
import argparse
import re
from collections import Counter
from pathlib import Path
from laus_xlsx_reader import read_sheet, number, fips_component, sha, write_csv, write_json

ROOT = Path(__file__).resolve().parents[1]
MONTHS = {m: i for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(), 1)}
HEADERS = ['LAUS Code', 'State FIPS Code', 'County FIPS Code', 'County Name/State Abbreviation',
           'Period', 'Labor Force', 'Employed', 'Unemployed', 'Unemploy-ment Rate (%)']

def parse_period(text):
    match = re.fullmatch(r'([A-Z][a-z]{2})-(\d{2})( p)?', text.strip())
    if not match or match[1] not in MONTHS:
        raise ValueError(f'Unexpected monthly period: {text!r}')
    return f'20{match[2]}-{MONTHS[match[1]]:02}', bool(match[3])

def prepare(source, output, converted):
    sheet, sheetrows = read_sheet(source)
    headers = next(v for _, v in sheetrows if v.get('A') == 'LAUS Code')
    assert [headers.get(c, '') for c in 'ABCDEFGHI'] == HEADERS, 'Unexpected schema'
    notes = [{'row': i, 'cells': v} for i, v in sheetrows if v.get('A') != 'LAUS Code' and not v.get('A', '').startswith('CN')]
    assert any('October 28, 2026' in v.values() for _, v in sheetrows), 'Review source release date'
    rows, original, seen = [], [], set()
    alerts = []
    for rownum, v in sheetrows:
        code = v.get('A', '')
        if not code.startswith('CN'):
            continue
        sf, cf = fips_component(v['B'], 2), fips_component(v['C'], 3)
        fips = sf + cf
        assert re.fullmatch(r'CN\d{13}', code) and code[2:7] == fips
        period, preliminary = parse_period(v['E'])
        assert (fips, period) not in seen, 'Duplicate county/month'
        seen.add((fips, period))
        if ', ' in v['D']:
            county, state = v['D'].rsplit(', ', 1)
        else:
            assert sf == '11' and v['D'] == 'District of Columbia'
            county, state = v['D'], 'DC'
        missing = [v[c].strip() == '–' for c in 'FGHI']
        assert all(missing) or not any(missing), 'Partial missing row'
        if all(missing):
            assert period == '2025-10' and sf != '72', 'Unexpected unavailable period'
            lf = employed = unemployed = rate = None
        else:
            lf, employed, unemployed = [number(v[c], integer=True) for c in 'FGH']
            rate = number(v['I'])
            assert None not in (lf, employed, unemployed, rate)
            assert lf == employed + unemployed, 'Labor force identity failed'
            if lf and abs(float(rate) - 100 * unemployed / lf) > 0.10:
                alerts.append({'county_fips': fips, 'period': period})
        rows.append(dict(county_fips=fips, state=state, state_fips=sf,
                         county_fips_component=cf, county_name=county, laus_code=code,
                         period=period, year=int(period[:4]), month=int(period[5:]),
                         labor_force=lf, employed=employed, unemployed=unemployed,
                         unemployment_rate_pct=rate, preliminary=preliminary,
                         seasonal_adjustment='not_seasonally_adjusted', geographic_basis='place_of_residence',
                         data_status='unavailable_shutdown' if all(missing) else 'published_estimate',
                         source_file=source.name, source_sheet=sheet, source_row=rownum,
                         source_date='2026-10-28'))
        original.append({h: v.get(c, '') for c, h in zip('ABCDEFGHI', HEADERS)})
    rows.sort(key=lambda r: (r['period'], r['county_fips']))
    local = [r for r in rows if r['state'] in ('KS', 'MO')]
    periods = sorted({r['period'] for r in rows})
    assert periods == [f'2025-{m:02}' for m in range(8, 13)] + [f'2026-{m:02}' for m in range(1, 10)]
    coverage = []
    for period in periods:
        for state, count in [('KS', 105), ('MO', 115)]:
            group = [r for r in local if r['state'] == state and r['period'] == period]
            assert len(group) == count
            assert {r['county_fips'] for r in group} == {r['county_fips'] for r in local if r['state'] == state and r['period'] == periods[0]}
            missing_count = sum(r['labor_force'] is None for r in group)
            assert missing_count == (count if period == '2025-10' else 0)
            coverage.append(dict(period=period, state=state, county_rows=count,
                                 available_counties=count-missing_count, unavailable_counties=missing_count))
    write_csv(converted, original)
    write_csv(output/'county_monthly_all_source_areas.csv', rows)
    write_csv(output/'county_monthly_ks_mo.csv', local)
    write_csv(output/'coverage_by_month.csv', coverage)
    index = {(r['county_fips'], r['period']): r for r in local}
    comparisons = []
    for r in local:
        if r['period'] not in ('2026-08', '2026-09'):
            continue
        base = index[(r['county_fips'], '2025' + r['period'][4:])]
        item = dict(county_fips=r['county_fips'], county_name=r['county_name'], state=r['state'],
                    baseline_period=base['period'], endpoint_period=r['period'],
                    endpoint_preliminary=r['preliminary'], seasonal_adjustment=r['seasonal_adjustment'])
        for measure in ('labor_force', 'employed', 'unemployed', 'unemployment_rate_pct'):
            item[measure+'_baseline'] = base[measure]
            item[measure+'_endpoint'] = r[measure]
            label = 'unemployment_rate_difference_pp' if measure == 'unemployment_rate_pct' else measure+'_difference_persons'
            item[label] = r[measure] - base[measure]
        comparisons.append(item)
    write_csv(output/'county_same_month_change_2025_2026_ks_mo.csv', comparisons)
    meta = dict(source_file=source.name, source_sha256=sha(source), notes=notes,
                periods=periods, source_rows=len(rows), ks_mo_rows=len(local),
                national_unavailable_rows=sum(r['labor_force'] is None for r in rows),
                ks_mo_available_rows=sum(r['labor_force'] is not None for r in local),
                rate_count_alerts=alerts, converted_csv_sha256=sha(converted))
    write_json(output/'manifest.json', meta)
    report = f'''# Monthly LAUS quality report

- Source: {source.name}; footer date October 28, 2026.
- August 2025–September 2026: 14 months, {len(rows):,} national source-area/month rows.
- All 105 KS counties and 115 MO county equivalents in every month: {len(local):,} rows.
- KS/MO: 2,860 available observations; 220 unavailable October 2025 placeholders.
- National unavailable rows: {meta['national_unavailable_rows']:,}; preserved as blanks, never zero.
- September 2026 is preliminary. All monthly data are not seasonally adjusted.
- Unique FIPS/month, stable KS/MO geography, FIPS/LAUS agreement, labor-force identity checked.
- Rate/count rounding alerts: {len(alerts)}. Published rates preserved.
- 440 same-month comparisons: August and September 2025 versus 2026.

No 2024 monthly data, October/November 2026 or full-year 2026 averages are in this input.
Keep this panel separate from annual averages. Same-month differences limit seasonal mismatch,
but do not establish policy effects or explain individual voting behavior.
'''
    (output/'quality_report.md').write_text(report, encoding='utf-8')
    print(report)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'data/raw/bls_laus_monthly/laucntycur14.xlsx')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'data/processed/laus_monthly')
    args = parser.parse_args()
    prepare(args.source, args.output_dir, ROOT/'data/raw/bls_laus_monthly/laucntycur14.csv')
