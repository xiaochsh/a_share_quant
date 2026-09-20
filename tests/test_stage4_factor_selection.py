import importlib
import unittest

import pandas as pd


def load_selector():
    try:
        module = importlib.import_module("lessons.stage4_factor_selection")
    except ModuleNotFoundError:
        return None
    return module.select_factor_stocks


class FactorSelectionTest(unittest.TestCase):
    def test_selects_top_factors_only_from_historical_stock_pool(self):
        select = load_selector()
        self.assertIsNotNone(select, "因子选股教学脚本尚未实现")
        data = pd.DataFrame(
            {
                "date": ["2026-01-05"] * 5,
                "code": ["A", "B", "C", "D", "E"],
                "factor": [0.08, -0.02, 0.03, 0.50, float("nan")],
                "eligible": [True, True, True, False, True],
            }
        )

        result = select(data, "factor", selection_count=2)
        selected = result.loc[result["selected"], "code"].tolist()

        self.assertEqual(selected, ["A", "C"])
        self.assertTrue(pd.isna(result.loc[result["code"] == "D", "selection_rank"]).iloc[0])


if __name__ == "__main__":
    unittest.main()
