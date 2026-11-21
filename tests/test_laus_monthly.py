import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from prepare_laus_monthly import parse_period

class MonthlyDataChecks(unittest.TestCase):
    def test_period_and_preliminary(self):
        self.assertEqual(parse_period('Sep-26 p'), ('2026-09', True))
        self.assertEqual(parse_period('Aug-25'), ('2025-08', False))
        with self.assertRaises(ValueError):
            parse_period('2025 annual')

    def test_prepared_panel_and_missingness(self):
        with (ROOT/'data/processed/laus_monthly/county_monthly_ks_mo.csv').open() as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 3080)
        self.assertEqual(len({(r['county_fips'], r['period']) for r in rows}), 3080)
        for period in {r['period'] for r in rows}:
            group = [r for r in rows if r['period'] == period]
            self.assertEqual(sum(r['state']=='KS' for r in group), 105)
            self.assertEqual(sum(r['state']=='MO' for r in group), 115)
            for r in group:
                self.assertEqual(len(r['county_fips']), 5)
                self.assertEqual(r['labor_force']=='', period=='2025-10')
                self.assertEqual(r['preliminary']=='True', period=='2026-09')

    def test_comparisons_match_month(self):
        from decimal import Decimal
        with (ROOT/'data/processed/laus_monthly/county_same_month_change_2025_2026_ks_mo.csv').open() as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 440)
        for r in rows:
            self.assertEqual(r['baseline_period'][5:], r['endpoint_period'][5:])
            self.assertEqual(r['baseline_period'][:4], '2025')
            self.assertEqual(r['endpoint_period'][:4], '2026')
            self.assertEqual(Decimal(r['unemployment_rate_difference_pp']),
                             Decimal(r['unemployment_rate_pct_endpoint'])-Decimal(r['unemployment_rate_pct_baseline']))

if __name__ == '__main__':
    unittest.main()
