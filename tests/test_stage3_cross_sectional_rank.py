import unittest

import pandas as pd


def load_calculator():
    try:
        from lessons.stage3_cross_sectional_rank import (
            calculate_rank_and_future_return,
        )
    except ModuleNotFoundError:
        return None
    return calculate_rank_and_future_return


class CrossSectionalRankTest(unittest.TestCase):
    def test_ranks_valid_factor_values_within_each_date(self):
        calculate = load_calculator()
        self.assertIsNotNone(calculate, "截面排名教学脚本尚未实现")
        data = pd.DataFrame(
            {
                "date": [
                    "2026-02-02",
                    "2026-02-02",
                    "2026-02-02",
                    "2026-02-03",
                    "2026-02-03",
                    "2026-02-03",
                ],
                "code": ["A", "B", "C", "A", "B", "C"],
                "adjusted_close": [100.0, 100.0, 100.0, 101.0, 99.0, 103.0],
                "momentum_20d": [0.08, -0.02, 0.03, 0.01, 0.04, float("nan")],
            }
        )

        result = calculate(data, future_periods=1)
        ranks = result.pivot(index="date", columns="code", values="factor_rank")

        self.assertEqual(ranks.loc[pd.Timestamp("2026-02-02"), "A"], 1.0)
        self.assertEqual(ranks.loc[pd.Timestamp("2026-02-02"), "C"], 2.0)
        self.assertEqual(ranks.loc[pd.Timestamp("2026-02-02"), "B"], 3.0)
        self.assertEqual(ranks.loc[pd.Timestamp("2026-02-03"), "B"], 1.0)
        self.assertEqual(ranks.loc[pd.Timestamp("2026-02-03"), "A"], 2.0)
        self.assertTrue(pd.isna(ranks.loc[pd.Timestamp("2026-02-03"), "C"]))

    def test_calculates_future_return_within_each_stock_and_leaves_tail_missing(self):
        calculate = load_calculator()
        self.assertIsNotNone(calculate, "未来收益教学脚本尚未实现")
        data = pd.DataFrame(
            {
                "date": [
                    "2026-02-03",
                    "2026-02-02",
                    "2026-02-03",
                    "2026-02-02",
                ],
                "code": ["B", "A", "A", "B"],
                "adjusted_close": [90.0, 100.0, 110.0, 100.0],
                "momentum_20d": [0.02, 0.03, 0.04, 0.01],
            }
        )

        result = calculate(data, future_periods=1)
        rows = result.set_index(["code", "date"])

        self.assertAlmostEqual(
            rows.loc[("A", pd.Timestamp("2026-02-02")), "future_return_1d"],
            0.10,
        )
        self.assertAlmostEqual(
            rows.loc[("B", pd.Timestamp("2026-02-02")), "future_return_1d"],
            -0.10,
        )
        self.assertTrue(
            pd.isna(
                rows.loc[("A", pd.Timestamp("2026-02-03")), "future_return_1d"]
            )
        )
        self.assertTrue(
            pd.isna(
                rows.loc[("B", pd.Timestamp("2026-02-03")), "future_return_1d"]
            )
        )


if __name__ == "__main__":
    unittest.main()
