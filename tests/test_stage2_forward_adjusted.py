import unittest

from lessons.stage2_forward_adjusted import calculate_forward_adjusted


class ForwardAdjustedTest(unittest.TestCase):
    def test_latest_price_is_kept_and_earlier_prices_are_adjusted(self):
        rows = [
            {"date": "2026-09-14", "close": 19.50, "adjustment_factor": 1.0},
            {"date": "2026-09-15", "close": 20.00, "adjustment_factor": 1.0},
            {"date": "2026-09-16", "close": 10.10, "adjustment_factor": 2.0},
        ]

        result = calculate_forward_adjusted(rows)

        self.assertEqual(result["qfq_close"].tolist(), [9.75, 10.0, 10.1])
        self.assertAlmostEqual(result.loc[2, "raw_price_return"], -0.495)
        self.assertAlmostEqual(result.loc[2, "qfq_return"], 0.01)
        self.assertEqual(result.loc[2, "qfq_close"], result.loc[2, "close"])


if __name__ == "__main__":
    unittest.main()
