import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from voting_debt.pipeline import margin, transition, fips, president_totals, comparison_totals


class DataRules(unittest.TestCase):
    def test_shift_sign_and_units(self):
        self.assertEqual(margin(40, 60, 100), -20)
        self.assertEqual(margin(53, 47, 100) - margin(40, 60, 100), 26)

    def test_all_vote_denominator(self):
        self.assertEqual(margin(45, 40, 100), 5)
        self.assertIsNone(margin(0, 0, 0))

    def test_unknown_debt_change_not_zero(self):
        self.assertEqual(transition({"low": "1.19"}, {"low": "1.19"}), "same_category")
        self.assertEqual(transition({"low": "1.19"}, {"low": "1.37"}), "higher_category")

    def test_fips_strings(self):
        self.assertEqual(fips("1001"), "01001")
        with self.assertRaises(ValueError):
            fips("1001.0")

    def house_row(self, race, d, r, t):
        return {"state": "KS", "office": "House", "fips": "20091", "race_id": race,
                "place_kind": "county part", "party_a": "D", "party_b": "R",
                "votes_a": str(d), "votes_b": str(r), "votes_other": str(t-d-r),
                "total_votes": str(t), "finished": "no"}

    def test_house_parts_sum_votes_not_margins(self):
        rows = [self.house_row("KS-02", 8, 2, 10), self.house_row("KS-03", 30, 60, 90)]
        result = comparison_totals(rows)[("KS", "House", "20091")]
        self.assertEqual(result["margin"], -24)
        self.assertFalse(result["finished"])

    def test_duplicate_parts_fail(self):
        row = self.house_row("KS-03", 2, 3, 5)
        with self.assertRaises(ValueError):
            comparison_totals([row, row])

    def test_non_dem_rep_pair_withholds_margin(self):
        row = self.house_row("KS-03", 2, 3, 5)
        row["party_a"] = "I"
        self.assertIsNone(comparison_totals([row])[("KS", "House", "20091")]["margin"])

    def test_vote_arithmetic_fails(self):
        row = self.house_row("KS-03", 2, 3, 5)
        row["votes_other"] = "1"
        with self.assertRaises(ValueError):
            comparison_totals([row])

    def test_mixed_president_modes_fail(self):
        rows = [{"county_fips": "20001", "mode": x} for x in ("TOTAL", "MAIL")]
        with self.assertRaises(ValueError):
            president_totals(rows)


if __name__ == "__main__":
    unittest.main()
