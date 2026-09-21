"""第四阶段：从组合净资产计算每日收益、净值和累计收益。

示例假设研究期间没有外部存款或取款，组合净资产已经包含现金、
实际持仓市值和交易成本的影响。
"""

from pathlib import Path

import pandas as pd


def calculate_equity_curve(
    data: pd.DataFrame,
    net_asset_column: str = "net_asset",
) -> pd.DataFrame:
    """按日期计算组合每日收益、标准化净值和累计收益。"""
    result = data.copy()
    result["date"] = pd.to_datetime(result["date"])
    result[net_asset_column] = pd.to_numeric(result[net_asset_column])
    result = result.sort_values("date", kind="stable").reset_index(drop=True)

    if result[net_asset_column].le(0).any():
        raise ValueError("组合净资产必须大于 0")

    result["daily_return"] = result[net_asset_column].pct_change(
        fill_method=None
    )
    growth_factor = 1 + result["daily_return"].fillna(0.0)
    result["equity"] = growth_factor.cumprod()
    result["cumulative_return"] = result["equity"] - 1
    result["running_peak"] = result["equity"].cummax()
    result["drawdown"] = result["equity"] / result["running_peak"] - 1
    return result


def calculate_max_drawdown(equity_curve: pd.DataFrame) -> dict[str, object]:
    """返回最大回撤及对应的历史峰值日期和后续谷值日期。"""
    trough_index = equity_curve["drawdown"].idxmin()
    peak_index = equity_curve.loc[:trough_index, "equity"].idxmax()
    return {
        "max_drawdown": equity_curve.loc[trough_index, "drawdown"],
        "peak_date": equity_curve.loc[peak_index, "date"],
        "trough_date": equity_curve.loc[trough_index, "date"],
    }


def compare_with_benchmark(
    strategy_data: pd.DataFrame,
    benchmark_data: pd.DataFrame,
    strategy_value_column: str = "net_asset",
    benchmark_value_column: str = "benchmark_value",
) -> pd.DataFrame:
    """按共同日期对齐策略与基准，并比较标准化累计收益。"""
    strategy = strategy_data[["date", strategy_value_column]].copy()
    benchmark = benchmark_data[["date", benchmark_value_column]].copy()
    strategy["date"] = pd.to_datetime(strategy["date"])
    benchmark["date"] = pd.to_datetime(benchmark["date"])
    strategy[strategy_value_column] = pd.to_numeric(
        strategy[strategy_value_column]
    )
    benchmark[benchmark_value_column] = pd.to_numeric(
        benchmark[benchmark_value_column]
    )

    result = strategy.merge(benchmark, on="date", how="inner")
    result = result.sort_values("date", kind="stable").reset_index(drop=True)
    if result.empty:
        raise ValueError("策略与基准没有共同日期")
    if (
        result[strategy_value_column].le(0).any()
        or result[benchmark_value_column].le(0).any()
    ):
        raise ValueError("策略净资产和基准数值必须大于 0")

    result["strategy_equity"] = (
        result[strategy_value_column] / result[strategy_value_column].iloc[0]
    )
    result["benchmark_equity"] = (
        result[benchmark_value_column] / result[benchmark_value_column].iloc[0]
    )
    result["strategy_cumulative_return"] = result["strategy_equity"] - 1
    result["benchmark_cumulative_return"] = result["benchmark_equity"] - 1
    result["excess_cumulative_return"] = (
        result["strategy_cumulative_return"]
        - result["benchmark_cumulative_return"]
    )
    return result


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    sample = pd.DataFrame(
        {
            "date": ["2026-03-02", "2026-03-03", "2026-03-04", "2026-03-05"],
            "net_asset": [100_000.0, 110_000.0, 104_500.0, 106_590.0],
        }
    )
    result = calculate_equity_curve(sample)
    print(result.to_string(index=False))

    output = root / "result/stage4_portfolio_metrics.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False, date_format="%Y-%m-%d")
    print("\n结果已保存：", output)

    drawdown_sample = pd.DataFrame(
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
    drawdown_curve = calculate_equity_curve(drawdown_sample)
    drawdown_summary = calculate_max_drawdown(drawdown_curve)
    print("\n最大回撤示例：")
    print(drawdown_curve.to_string(index=False))
    print("最大回撤：", f"{drawdown_summary['max_drawdown']:.2%}")
    print("峰值日期：", drawdown_summary["peak_date"].date())
    print("谷值日期：", drawdown_summary["trough_date"].date())

    drawdown_output = root / "result/stage4_drawdown_example.csv"
    drawdown_curve.to_csv(drawdown_output, index=False, date_format="%Y-%m-%d")
    print("结果已保存：", drawdown_output)

    benchmark_sample = pd.DataFrame(
        {
            "date": ["2026-03-02", "2026-03-04", "2026-03-05"],
            "benchmark_value": [2000.0, 2160.0, 2200.0],
        }
    )
    strategy_benchmark_sample = pd.DataFrame(
        {
            "date": ["2026-03-02", "2026-03-03", "2026-03-04"],
            "net_asset": [100_000.0, 105_000.0, 112_000.0],
        }
    )
    benchmark_comparison = compare_with_benchmark(
        strategy_benchmark_sample, benchmark_sample
    )
    print("\n基准收益比较：")
    print(benchmark_comparison.to_string(index=False))

    benchmark_output = root / "result/stage4_benchmark_comparison.csv"
    benchmark_comparison.to_csv(
        benchmark_output, index=False, date_format="%Y-%m-%d"
    )
    print("结果已保存：", benchmark_output)


if __name__ == "__main__":
    main()
