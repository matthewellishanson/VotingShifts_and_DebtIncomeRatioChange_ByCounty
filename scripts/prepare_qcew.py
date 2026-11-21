"""Build KS/MO county QCEW totals from an extracted directory or the supplied ZIP."""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PERIODS = [f'{y}-Q{q}' for y in (2024, 2025) for q in range(1, 5)] + ['2026-Q1']
METRICS = ['qtrly_estabs_count', 'month1_emplvl', 'month2_emplvl', 'month3_emplvl',
           'total_qtrly_wages', 'taxable_qtrly_wages', 'qtrly_contributions', 'avg_wkly_wage']

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

@contextmanager
def inputs(source):
    if source.is_file():
        with ZipFile(source) as z:
            yield [(n, lambda n=n: z.open(n)) for n in sorted(z.namelist()) if n.lower().endswith('.csv')]
    else:
        if not source.is_dir():
            raise ValueError(f'Source directory not found: {source}')
        yield [(p.relative_to(source).as_posix(), lambda p=p: p.open('rb')) for p in sorted(source.rglob('*.csv'))]

def normalize(r, member, line):
    flag = r['disclosure_code'].strip()
    if flag not in ('', 'N', '-'):
        raise ValueError(f'Unknown disclosure code: {flag!r}')
    area = r['area_fips']
    out = dict(area_fips=area, county_fips='' if area.endswith('000') else area,
               state='KS' if area[:2]=='20' else 'MO', area_title=r['area_title'],
               year=int(r['year']), quarter=int(r['qtr']), period=f"{r['year']}-Q{r['qtr']}",
               own_code=r['own_code'], own_title=r['own_title'], industry_code=r['industry_code'],
               agglvl_code=r['agglvl_code'], size_code=r['size_code'], disclosure_code=flag,
               data_status={'':'published', 'N':'suppressed', '-':'not_present'}[flag])
    for key in METRICS:
        # BLS publishes establishments for N cells; other N-cell values are zero-filled suppression.
        if flag=='-' or (flag=='N' and key!='qtrly_estabs_count'):
            out[key] = None
        else:
            value = Decimal(r[key])
            if not value.is_finite() or value < 0 or value != value.to_integral_value():
                raise ValueError(f'Invalid numeric {key}: {r[key]}')
            out[key] = int(value)
    out['quarter_avg_monthly_employment'] = (sum(out[k] for k in METRICS[1:4])/3) if flag=='' else None
    out.update(geographic_basis='place_of_work', wage_price_basis='nominal_USD',
               seasonal_adjustment='not_seasonally_adjusted', release_status='not_encoded_in_supplied_CSV',
               source_file=member, source_row=line)
    return out

def comparisons(rows):
    index = {(r['county_fips'],r['period']):r for r in rows}
    output = []
    measures = ['quarter_avg_monthly_employment','qtrly_estabs_count','avg_wkly_wage','total_qtrly_wages']
    for r in rows:
        base = index.get((r['county_fips'], f"{r['year']-1}-Q{r['quarter']}"))
        if not base:
            continue
        item = dict(county_fips=r['county_fips'], state=r['state'], area_title=r['area_title'],
                    baseline_period=base['period'], endpoint_period=r['period'])
        for key in measures:
            a,b = base[key], r[key]
            item[key+'_baseline'] = a
            item[key+'_endpoint'] = b
            item[key+'_difference'] = b-a if a is not None and b is not None else None
            item[key+'_pct_change'] = 100*(b/a-1) if a not in (None,0) and b is not None else None
        output.append(item)
    return output

def prepare(source, output):
    inventory, ownership, statewide = [], [], []
    all_count = 0
    flags = Counter()
    schema = None
    seen = set()
    with inputs(source) as members:
        for name, opener in members:
            count, selected, periods, areas = 0, 0, set(), set()
            digest = hashlib.sha256()
            with opener() as stream:
                raw = stream.read()
            digest.update(raw)
            reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''))
            if schema is None:
                schema = reader.fieldnames
            if reader.fieldnames != schema or not set(METRICS+['area_fips','own_code','industry_code','agglvl_code','size_code','year','qtr','disclosure_code']).issubset(schema):
                raise ValueError(f'Unexpected CSV schema: {name}')
            for line, r in enumerate(reader, 2):
                count += 1
                area = r['area_fips']
                if not re.fullmatch(r'(20|29)\d{3}',area):
                    raise ValueError(f'Non KS/MO area in input: {area}')
                period = f"{r['year']}-Q{r['qtr']}"
                if period not in PERIODS:
                    raise ValueError(f'Unexpected input period: {period}')
                areas.add(area); periods.add(period)
                flags[r['disclosure_code'].strip()] += 1
                if r['industry_code']!='10' or r['size_code']!='0':
                    continue
                key = (area, period, r['own_code'])
                if key in seen:
                    raise ValueError(f'Duplicate all-industry key: {key}')
                seen.add(key)
                item = normalize(r,name,line)
                if area.endswith('000'):
                    if r['own_code']=='0':
                        if r['agglvl_code']!='50': raise ValueError('State aggregation code mismatch')
                        statewide.append(item)
                else:
                    if r['own_code']=='0' and r['agglvl_code']!='70':
                        raise ValueError('County aggregation code mismatch')
                    ownership.append(item)
                selected += 1
            if len(areas)!=1:
                raise ValueError(f'Expected one area per input CSV: {name}')
            all_count += count
            inventory.append(dict(source_file=name, sha256=digest.hexdigest(), source_rows=count,
                                  area_fips=next(iter(areas)), periods=';'.join(sorted(periods)),
                                  selected_all_industry_rows=selected))
    ownership.sort(key=lambda r:(r['period'],r['county_fips'],r['own_code']))
    main = [r for r in ownership if r['own_code']=='0']
    coverage=[]
    reference={}
    for period in PERIODS:
        for state, expected in [('KS',105),('MO',115)]:
            group=[r for r in main if r['period']==period and r['state']==state]
            ids={r['county_fips'] for r in group}
            if len(group)!=expected or len(ids)!=expected:
                raise ValueError(f'Incomplete county coverage: {period}/{state}: {len(group)}')
            if state in reference and ids!=reference[state]:
                raise ValueError('County geography changed')
            reference[state]=ids
            if any(r['disclosure_code'] for r in group):
                raise ValueError('Suppressed all-industry county total; review before continuing')
            coverage.append(dict(period=period,state=state,county_count=len(group),suppressed_totals=0))
    if len(statewide)!=18:
        raise ValueError('Expected two statewide totals in nine quarters')
    write_csv(output/'county_quarterly_totals_ks_mo.csv',main)
    write_csv(output/'county_quarterly_ownership_ks_mo.csv',ownership)
    write_csv(output/'statewide_quarterly_totals_ks_mo.csv',sorted(statewide,key=lambda r:(r['period'],r['state'])))
    write_csv(output/'county_same_quarter_yoy_ks_mo.csv',comparisons(main))
    write_csv(output/'coverage_by_quarter.csv',coverage)
    write_csv(output/'source_inventory.csv',inventory)
    meta=dict(input_source=str(source),input_csv_files=len(inventory),source_rows=all_count,
              source_disclosure_counts=dict(flags),county_total_rows=len(main),county_ownership_rows=len(ownership),
              statewide_rows=len(statewide),schema=schema,
              release_status='Not encoded in supplied CSV; verify release metadata before publication',
              national_coverage='KS/MO-only inputs; excluded national files cannot be reconstructed')
    if source.is_file():
        meta['source_zip_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    output.mkdir(parents=True,exist_ok=True)
    (output/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    report=f'''# QCEW quality report

- {len(inventory):,} source CSVs; {all_count:,} source rows reviewed.
- All 220 KS/MO county equivalents in each of nine quarters: 2024 Q1–2026 Q1.
- {len(main):,} county/quarter total-covered records, all disclosed.
- {len(ownership):,} county/quarter/ownership records; categories overlap with total covered and must not be added together.
- 18 statewide total-covered records, separate from counties.
- {len(comparisons(main)):,} same-quarter year-over-year county comparisons.
- Source N rows: {flags['N']:,}; absent-cell dash rows: {flags['-']:,}.
- Selected suppressed values are blanked; establishment counts retained for N cells per BLS rules.
- Unique all-industry area/quarter/ownership keys and stable county coverage validated.
- All source CSVs have the same schema. Per-file SHA-256 hashes and row references retained.

Source quarterly CSVs do not encode preliminary/final release status. No release status is inferred.
Employment counts covered workplace jobs, not resident people or unemployment.
Wages are nominal averages, not median pay, household income, hourly rates or purchasing power.
No 2026 Q2/Q3 observations are supplied. Do not represent Q1 as election-eve conditions.
Industry-level aggregation, inflation adjustment and causal attribution are deferred.
'''
    (output/'quality_report.md').write_text(report,encoding='utf-8')
    print(report)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=ROOT/'data/raw/qcew')
    p.add_argument('--output-dir',type=Path,default=ROOT/'data/processed/qcew')
    args=p.parse_args()
    prepare(args.source,args.output_dir)
