import importlib
import unittest

import pandas as pd


def load_functions():
    try:
        module = importlib.import_module("lessons.stage3_quintile_analysis")
    except ModuleNotFoundError:
        return None, None
    return module.assign_quintiles, module.calculate_quintile_returns


class QuintileAnalysisTest(unittest.TestCase):
    def test_assigns_nearly_equal_groups_using_factor_then_code(self):
        assign, _ = load_functions()
        self.assertIsNotNone(assign, "五分组教学脚本尚未实现")
        data = pd.DataFrame(
            {
                "date": ["2026-01-05"] * 7,
                "code": ["G", "F", "E", "D", "C", "B", "A"],
                "factor": [3.0, 3.0, 2.0, 2.0, 1.0, 1.0, 1.0],
                "future_return": [0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01],
            }
        )

        result = assign(data, "factor")
        counts = result["quintile"].value_counts().sort_index()
        groups = result.set_index("code")["quintile"]

        self.assertLessEqual(counts.max() - counts.min(), 1)
        self.assertEqual(groups["A"], "G1")
        self.assertEqual(groups["G"], "G5")
        self.assertLess(int(groups["A"][1:]), int(groups["C"][1:]))

    def test_reports_original_valid_and_missing_counts(self):
        assign, summarize = load_functions()
        self.assertIsNotNone(summarize, "五分组收益汇总尚未实现")
        data = pd.DataFrame(
            {
                "date": ["2026-01-05"] * 5,
                "code": ["A", "B", "C", "D", "E"],
                "factor": [1, 2, 3, 4, 5],
                "future_return": [0.01, float("nan"), 0.03, 0.04, 0.05],
            }
        )

        grouped = assign(data, "factor")
        result = summarize(grouped, "future_return")
        g2 = result.loc[result["quintile"] == "G2"].iloc[0]

        self.assertEqual(g2["original_count"], 1)
        self.assertEqual(g2["valid_return_count"], 0)
        self.assertEqual(g2["missing_return_count"], 1)
        self.assertTrue(pd.isna(g2["mean_future_return"]))


if __name__ == "__main__":
    unittest.main()
