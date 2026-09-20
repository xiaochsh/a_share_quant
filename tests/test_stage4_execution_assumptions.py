import importlib
import unittest

import pandas as pd


def load_functions():
    try:
        module = importlib.import_module("lessons.stage4_execution_assumptions")
    except ModuleNotFoundError:
        return None, None
    return module.audit_event_timing, module.simulate_next_day_execution


class ExecutionAssumptionsTest(unittest.TestCase):
    def test_flags_decisions_or_executions_that_break_time_order(self):
        audit, _ = load_functions()
        self.assertIsNotNone(audit, "成交假设教学脚本尚未实现")
        events = pd.DataFrame(
            {
                "case": ["正确", "提前决策", "提前成交"],
                "data_available_at": [
                    "2026-03-06 15:00",
                    "2026-03-06 15:00",
                    "2026-03-06 15:00",
                ],
                "decision_at": [
                    "2026-03-06 15:05",
                    "2026-03-06 09:25",
                    "2026-03-06 15:05",
                ],
                "execution_at": [
                    "2026-03-09 09:30",
                    "2026-03-09 09:30",
                    "2026-03-06 09:30",
                ],
            }
        )

        result = audit(events).set_index("case")

        self.assertTrue(result.loc["正确", "timing_valid"])
        self.assertFalse(result.loc["提前决策", "timing_valid"])
        self.assertFalse(result.loc["提前成交", "timing_valid"])

    def test_executes_tradable_target_on_next_trading_day(self):
        _, simulate = load_functions()
        self.assertIsNotNone(simulate, "下一交易日执行函数尚未实现")
        targets = pd.DataFrame(
            {
                "signal_date": ["2026-03-06"],
                "code": ["A"],
                "target_weight": [0.5],
                "actual_weight_before": [0.0],
                "can_trade": [True],
            }
        )
        calendar = pd.to_datetime(["2026-03-06", "2026-03-09"])

        result = simulate(targets, calendar).iloc[0]

        self.assertEqual(result["execution_date"], pd.Timestamp("2026-03-09"))
        self.assertTrue(result["filled"])
        self.assertEqual(result["actual_weight_after"], 0.5)

    def test_keeps_actual_weight_when_stock_cannot_trade(self):
        _, simulate = load_functions()
        self.assertIsNotNone(simulate, "成交限制函数尚未实现")
        targets = pd.DataFrame(
            {
                "signal_date": ["2026-03-06"],
                "code": ["B"],
                "target_weight": [0.0],
                "actual_weight_before": [0.4],
                "can_trade": [False],
            }
        )
        calendar = pd.to_datetime(["2026-03-06", "2026-03-09"])

        result = simulate(targets, calendar).iloc[0]

        self.assertFalse(result["filled"])
        self.assertEqual(result["actual_weight_after"], 0.4)


if __name__ == "__main__":
    unittest.main()
