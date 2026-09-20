import importlib
import unittest

import pandas as pd


def load_functions():
    try:
        module = importlib.import_module("lessons.stage4_periodic_rebalance")
    except ModuleNotFoundError:
        return None, None
    return module.schedule_rebalance_targets, module.calculate_weight_adjustments


class PeriodicRebalanceTest(unittest.TestCase):
    def test_schedules_close_targets_for_next_trading_day(self):
        schedule, _ = load_functions()
        self.assertIsNotNone(schedule, "定期调仓教学脚本尚未实现")
        targets = pd.DataFrame(
            {
                "signal_date": ["2026-01-09"],
                "code": ["A"],
                "target_weight": [0.5],
            }
        )
        calendar = pd.to_datetime(["2026-01-09", "2026-01-12", "2026-01-13"])

        result = schedule(targets, calendar)

        self.assertEqual(result.loc[0, "execution_date"], pd.Timestamp("2026-01-12"))

    def test_calculates_orders_from_target_minus_actual_weight(self):
        _, calculate = load_functions()
        self.assertIsNotNone(calculate, "调仓差额教学函数尚未实现")
        current = pd.DataFrame(
            {"code": ["A", "B"], "actual_weight": [0.55, 0.45]}
        )
        target = pd.DataFrame(
            {"code": ["A", "C"], "target_weight": [0.50, 0.50]}
        )

        result = calculate(current, target).set_index("code")

        self.assertAlmostEqual(result.loc["A", "weight_change"], -0.05)
        self.assertAlmostEqual(result.loc["B", "weight_change"], -0.45)
        self.assertAlmostEqual(result.loc["C", "weight_change"], 0.50)
        self.assertEqual(result.loc["A", "side"], "卖出")
        self.assertEqual(result.loc["C", "side"], "买入")


if __name__ == "__main__":
    unittest.main()
