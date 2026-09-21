import importlib
import unittest

import pandas as pd


def load_calculator():
    try:
        module = importlib.import_module("lessons.stage4_portfolio_metrics")
    except ModuleNotFoundError:
        return None
    return module.calculate_equity_curve


def load_max_drawdown_calculator():
    try:
        module = importlib.import_module("lessons.stage4_portfolio_metrics")
        return module.calculate_max_drawdown
    except (ModuleNotFoundError, AttributeError):
        return None


def load_benchmark_comparator():
    try:
        module = importlib.import_module("lessons.stage4_portfolio_metrics")
        return module.compare_with_benchmark
    except (ModuleNotFoundError, AttributeError):
        return None


class PortfolioMetricsTest(unittest.TestCase):
    def test_calculates_daily_return_equity_and_cumulative_return_in_date_order(self):
        calculate = load_calculator()
        self.assertIsNotNone(calculate, "组合指标教学脚本尚未实现")
        data = pd.DataFrame(
            {
                "date": [
                    "2026-03-04",
                    "2026-03-02",
                    "2026-03-05",
                    "2026-03-03",
                ],
                "net_asset": [104_500.0, 100_000.0, 106_590.0, 110_000.0],
            }
        )

        result = calculate(data)

        self.assertEqual(
            result["date"].tolist(),
            list(pd.to_datetime(["2026-03-02", "2026-03-03", "2026-03-04", "2026-03-05"])),
        )
        self.assertTrue(pd.isna(result.loc[0, "daily_return"]))
        self.assertAlmostEqual(result.loc[1, "daily_return"], 0.10)
        self.assertAlmostEqual(result.loc[2, "daily_return"], -0.05)
        self.assertAlmostEqual(result.loc[3, "daily_return"], 0.02)
        self.assertAlmostEqual(result.loc[0, "equity"], 1.0)
        self.assertAlmostEqual(result.loc[3, "equity"], 1.0659)
        self.assertAlmostEqual(result.loc[3, "cumulative_return"], 0.0659)

    def test_rejects_non_positive_net_assets(self):
        calculate = load_calculator()
        self.assertIsNotNone(calculate, "组合指标教学脚本尚未实现")
        data = pd.DataFrame(
            {"date": ["2026-03-02"], "net_asset": [0.0]}
        )

        with self.assertRaises(ValueError):
            calculate(data)

    def test_calculates_running_drawdown_and_peak_to_trough_dates(self):
        calculate = load_calculator()
        calculate_max_drawdown = load_max_drawdown_calculator()
        self.assertIsNotNone(calculate_max_drawdown, "最大回撤函数尚未实现")
        data = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    [
                        "2026-03-02",
                        "2026-03-03",
                        "2026-03-04",
                        "2026-03-05",
                        "2026-03-06",
                        "2026-03-09",
                    ]
                ),
                "net_asset": [100_000, 120_000, 108_000, 115_000, 90_000, 110_000],
            }
        )

        curve = calculate(data)
        summary = calculate_max_drawdown(curve)

        self.assertAlmostEqual(curve.loc[4, "running_peak"], 1.20)
        self.assertAlmostEqual(curve.loc[4, "drawdown"], -0.25)
        self.assertAlmostEqual(summary["max_drawdown"], -0.25)
        self.assertEqual(summary["peak_date"], pd.Timestamp("2026-03-03"))
        self.assertEqual(summary["trough_date"], pd.Timestamp("2026-03-06"))

    def test_aligns_common_dates_and_calculates_excess_cumulative_return(self):
        compare = load_benchmark_comparator()
        self.assertIsNotNone(compare, "基准收益比较函数尚未实现")
        strategy = pd.DataFrame(
            {
                "date": ["2026-03-02", "2026-03-03", "2026-03-04"],
                "net_asset": [100_000.0, 105_000.0, 112_000.0],
            }
        )
        benchmark = pd.DataFrame(
            {
                "date": ["2026-03-02", "2026-03-04", "2026-03-05"],
                "benchmark_value": [2000.0, 2160.0, 2200.0],
            }
        )

        result = compare(strategy, benchmark)

        self.assertEqual(
            result["date"].tolist(),
            list(pd.to_datetime(["2026-03-02", "2026-03-04"])),
        )
        self.assertAlmostEqual(result.loc[1, "strategy_equity"], 1.12)
        self.assertAlmostEqual(result.loc[1, "benchmark_equity"], 1.08)
        self.assertAlmostEqual(result.loc[1, "strategy_cumulative_return"], 0.12)
        self.assertAlmostEqual(result.loc[1, "benchmark_cumulative_return"], 0.08)
        self.assertAlmostEqual(result.loc[1, "excess_cumulative_return"], 0.04)

    def test_rejects_strategy_and_benchmark_without_common_dates(self):
        compare = load_benchmark_comparator()
        self.assertIsNotNone(compare, "基准收益比较函数尚未实现")
        strategy = pd.DataFrame(
            {"date": ["2026-03-02"], "net_asset": [100_000.0]}
        )
        benchmark = pd.DataFrame(
            {"date": ["2026-03-03"], "benchmark_value": [2000.0]}
        )

        with self.assertRaises(ValueError):
            compare(strategy, benchmark)


if __name__ == "__main__":
    unittest.main()
