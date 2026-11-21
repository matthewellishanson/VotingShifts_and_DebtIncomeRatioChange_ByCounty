import csv
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from prepare_qcew import normalize, METRICS, comparisons

class QcewTests(unittest.TestCase):
    def test_suppressed_zero_is_not_observed_zero(self):
        row=dict(area_fips='20001', area_title='Allen County, Kansas', year='2026', qtr='1',
                 own_code='1',own_title='Federal Government',industry_code='10',
                 agglvl_code='71',size_code='0',disclosure_code='N',
                 **{k:'0' for k in METRICS})
        row['qtrly_estabs_count']='4'
        r=normalize(row,'test.csv',2)
        self.assertEqual(r['qtrly_estabs_count'],4)
        self.assertIsNone(r['month1_emplvl'])
        self.assertIsNone(r['avg_wkly_wage'])
        self.assertIsNone(r['quarter_avg_monthly_employment'])
        row['disclosure_code']=''
        self.assertEqual(normalize(row,'test.csv',2)['month1_emplvl'],0)
        row['disclosure_code']='-'
        self.assertIsNone(normalize(row,'test.csv',2)['qtrly_estabs_count'])

    def test_prepared_totals_coverage(self):
        with (ROOT/'data/processed/qcew/county_quarterly_totals_ks_mo.csv').open() as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),1980)
        self.assertEqual(len({(r['county_fips'],r['period']) for r in rows}),1980)
        for p in {r['period'] for r in rows}:
            group=[r for r in rows if r['period']==p]
            self.assertEqual(sum(r['state']=='KS' for r in group),105)
            self.assertEqual(sum(r['state']=='MO' for r in group),115)
        for r in rows:
            self.assertEqual(r['own_code'],'0')
            self.assertEqual(r['agglvl_code'],'70')
            self.assertEqual(r['disclosure_code'],'')
            self.assertEqual(len(r['county_fips']),5)
            self.assertAlmostEqual(float(r['quarter_avg_monthly_employment']),
                sum(int(r[k]) for k in METRICS[1:4])/3)

    def test_yoy_matches_quarters_and_handles_zero(self):
        rows=[]
        for year,value in [(2025,0),(2026,10)]:
            rows.append(dict(county_fips='20001',state='KS',area_title='Allen',
                period=f'{year}-Q1',year=year,quarter=1,quarter_avg_monthly_employment=value,
                qtrly_estabs_count=value,avg_wkly_wage=value,total_qtrly_wages=value))
        result=comparisons(rows)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['avg_wkly_wage_difference'],10)
        self.assertIsNone(result[0]['avg_wkly_wage_pct_change'])

if __name__=='__main__':
    unittest.main()
