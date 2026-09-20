import importlib
import unittest

import pandas as pd


def load_calculator():
    try:
        module = importlib.import_module("lessons.stage3_ic")
    except ModuleNotFoundError:
        return None
    return module.calculate_daily_ic


class DailyIcTest(unittest.TestCase):
    def test_calculates_pearson_and_rank_ic_from_valid_pairs(self):
        calculate = load_calculator()
        self.assertIsNotNone(calculate, "IC 教学脚本尚未实现")
        data = pd.DataFrame(
            {
                "date": ["2026-01-05"] * 4,
                "code": ["A", "B", "C", "D"],
                "factor": [1.0, 2.0, 3.0, 4.0],
                "future_return": [0.01, 0.03, 0.02, float("nan")],
            }
        )

        result = calculate(data, "factor", "future_return").iloc[0]

        self.assertEqual(result["valid_pair_count"], 3)
        self.assertAlmostEqual(result["pearson_ic"], 0.5)
        self.assertAlmostEqual(result["rank_ic"], 0.5)

    def test_returns_nan_when_factor_has_no_cross_sectional_difference(self):
        calculate = load_calculator()
        self.assertIsNotNone(calculate, "IC 教学脚本尚未实现")
        data = pd.DataFrame(
            {
                "date": ["2026-01-05"] * 3,
                "code": ["A", "B", "C"],
                "factor": [1.0, 1.0, 1.0],
                "future_return": [0.01, 0.02, 0.03],
            }
        )

        result = calculate(data, "factor", "future_return").iloc[0]

        self.assertTrue(pd.isna(result["pearson_ic"]))
        self.assertTrue(pd.isna(result["rank_ic"]))


if __name__ == "__main__":
    unittest.main()
