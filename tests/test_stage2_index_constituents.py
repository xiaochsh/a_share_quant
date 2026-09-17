import unittest

from lessons.stage2_index_constituents import constituents_on_date


class IndexConstituentsTest(unittest.TestCase):
    def test_constituents_follow_historical_effective_dates(self):
        rows = [
            {"code": "600001", "effective_from": "2026-01-01", "effective_to": None},
            {"code": "000002", "effective_from": "2026-01-01", "effective_to": "2026-09-15"},
            {"code": "300003", "effective_from": "2026-09-15", "effective_to": None},
        ]

        before_change = constituents_on_date(rows, "2026-09-14")
        after_change = constituents_on_date(rows, "2026-09-16")

        self.assertEqual(before_change["code"].tolist(), ["600001", "000002"])
        self.assertEqual(after_change["code"].tolist(), ["600001", "300003"])


if __name__ == "__main__":
    unittest.main()
