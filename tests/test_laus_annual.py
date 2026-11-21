import shutil
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_laus_annual import average_period, fips_component, number, parse_workbook


class LausAnnualRules(unittest.TestCase):
    def test_fips_padding(self):
        self.assertEqual(fips_component("1", 2)+fips_component("1", 3), "01001")
        with self.assertRaises(ValueError):
            fips_component("1.0", 3)

    def test_missing_counts_not_zero(self):
        self.assertIsNone(number("N.A.", integer=True))
        self.assertEqual(number("0", integer=True), 0)
        with self.assertRaises(ValueError):
            number("12.5", integer=True)

    def test_rate_storage_artifacts_not_extra_precision(self):
        self.assertEqual(number("9.1999999999999993"), Decimal("9.2"))
        with self.assertRaises(ValueError):
            number("9.25")

    def test_2025_period_exception(self):
        self.assertEqual(average_period(2025, "20"), (11, "eleven_month_average_excluding_october", "2025-10"))
        self.assertEqual(average_period(2025, "29")[0], 11)
        self.assertEqual(average_period(2025, "72")[0], 12)
        self.assertEqual(average_period(2024, "20")[0], 12)

    def test_actual_2025_coverage_and_dc_handling(self):
        rows, converted, metadata = parse_workbook(ROOT / "data/raw/bls_laus_annual/xlsx/laucnty25.xlsx")
        self.assertEqual(sum(r["state"] == "KS" for r in rows), 105)
        self.assertEqual(sum(r["state"] == "MO" for r in rows), 115)
        self.assertTrue(all(r["averaging_months"] == 11 for r in rows if r["state"] in {"KS", "MO"}))
        self.assertEqual(next(r for r in rows if r["county_fips"] == "11001")["state"], "DC")

    def test_actual_2020_unavailable_preserved(self):
        rows, _, _ = parse_workbook(ROOT / "data/raw/bls_laus_annual/xlsx/laucnty20.xlsx")
        missing = [r for r in rows if r["data_status"] == "source_unavailable"]
        self.assertEqual(len(missing), 78)
        self.assertTrue(all(r["state"] == "PR" and r["labor_force"] is None for r in missing))

    def test_wrong_filename_year_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "laucnty24.xlsx"
            shutil.copyfile(ROOT / "data/raw/bls_laus_annual/xlsx/laucnty25.xlsx", target)
            with self.assertRaises(ValueError):
                parse_workbook(target)


if __name__ == "__main__":
    unittest.main()
