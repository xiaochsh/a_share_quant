import importlib
import unittest

import pandas as pd


def load_calculator():
    try:
        module = importlib.import_module("lessons.stage4_equal_weight")
    except ModuleNotFoundError:
        return None
    return module.calculate_equal_weight_targets


class EqualWeightTest(unittest.TestCase):
    def test_allocates_investable_weight_equally_to_selected_stocks(self):
        calculate = load_calculator()
        self.assertIsNotNone(calculate, "等权持仓教学脚本尚未实现")
        data = pd.DataFrame(
            {
                "date": ["2026-01-05"] * 4,
                "code": ["A", "B", "C", "D"],
                "selected": [True, True, True, False],
            }
        )

        result = calculate(data, cash_weight=0.10)
        weights = result.set_index("code")["target_weight"]

        self.assertAlmostEqual(weights["A"], 0.30)
        self.assertAlmostEqual(weights["B"], 0.30)
        self.assertAlmostEqual(weights["C"], 0.30)
        self.assertEqual(weights["D"], 0.0)
        self.assertAlmostEqual(result["target_weight"].sum(), 0.90)

    def test_rejects_invalid_cash_weight(self):
        calculate = load_calculator()
        self.assertIsNotNone(calculate, "等权持仓教学脚本尚未实现")
        data = pd.DataFrame(
            {"date": ["2026-01-05"], "code": ["A"], "selected": [True]}
        )

        with self.assertRaises(ValueError):
            calculate(data, cash_weight=1.0)


if __name__ == "__main__":
    unittest.main()
