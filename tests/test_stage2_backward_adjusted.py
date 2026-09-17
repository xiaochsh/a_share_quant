import unittest

from lessons.stage2_backward_adjusted import calculate_adjusted_prices


class BackwardAdjustedTest(unittest.TestCase):
    def test_qfq_and_hfq_have_different_levels_but_same_returns(self):
        rows = [
            {"date": "2026-09-14", "close": 19.50, "adjustment_factor": 1.0},
            {"date": "2026-09-15", "close": 20.00, "adjustment_factor": 1.0},
            {"date": "2026-09-16", "close": 10.10, "adjustment_factor": 2.0},
        ]

        result = calculate_adjusted_prices(rows)

        self.assertEqual(result["qfq_close"].tolist(), [9.75, 10.0, 10.1])
        self.assertEqual(result["hfq_close"].tolist(), [19.5, 20.0, 20.2])
        self.assertAlmostEqual(result.loc[2, "qfq_return"], 0.01)
        self.assertAlmostEqual(result.loc[2, "hfq_return"], 0.01)
        self.assertEqual(result.loc[0, "hfq_close"], result.loc[0, "close"])


if __name__ == "__main__":
    unittest.main()
