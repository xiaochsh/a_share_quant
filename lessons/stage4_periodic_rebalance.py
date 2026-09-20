"""第四阶段：安排定期调仓的执行日期并计算权重调整。"""

from pathlib import Path

import pandas as pd


def schedule_rebalance_targets(
    targets: pd.DataFrame,
    trading_calendar: pd.DatetimeIndex,
) -> pd.DataFrame:
    """把收盘后产生的目标安排到日历中的下一交易日执行。"""
    result = targets.copy()
    result["signal_date"] = pd.to_datetime(result["signal_date"])
    calendar = pd.DatetimeIndex(pd.to_datetime(trading_calendar)).sort_values().unique()

    def next_trading_day(signal_date: pd.Timestamp) -> pd.Timestamp:
        position = calendar.searchsorted(signal_date, side="right")
        if position >= len(calendar):
            return pd.NaT
        return calendar[position]

    result["execution_date"] = result["signal_date"].map(next_trading_day)
    return result


def calculate_weight_adjustments(
    current_weights: pd.DataFrame,
    target_weights: pd.DataFrame,
) -> pd.DataFrame:
    """用目标权重减实际权重，正数买入、负数卖出。"""
    result = current_weights.merge(target_weights, on="code", how="outer")
    result[["actual_weight", "target_weight"]] = result[
        ["actual_weight", "target_weight"]
    ].fillna(0.0)
    result["weight_change"] = result["target_weight"] - result["actual_weight"]
    result["side"] = "保持"
    result.loc[result["weight_change"] > 0, "side"] = "买入"
    result.loc[result["weight_change"] < 0, "side"] = "卖出"
    return result.sort_values("code", kind="stable").reset_index(drop=True)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    targets = pd.DataFrame(
        {
            "signal_date": ["2026-03-06", "2026-03-06"],
            "code": ["A", "C"],
            "target_weight": [0.50, 0.50],
        }
    )
    calendar = pd.to_datetime(["2026-03-06", "2026-03-09", "2026-03-10"])
    scheduled = schedule_rebalance_targets(targets, calendar)
    current = pd.DataFrame(
        {"code": ["A", "B"], "actual_weight": [0.55, 0.45]}
    )
    orders = calculate_weight_adjustments(
        current, targets[["code", "target_weight"]]
    )
    print("执行安排：")
    print(scheduled.to_string(index=False))
    print("\n权重调整：")
    print(orders.to_string(index=False))

    schedule_output = root / "result/stage4_rebalance_schedule.csv"
    orders_output = root / "result/stage4_rebalance_orders.csv"
    schedule_output.parent.mkdir(parents=True, exist_ok=True)
    scheduled.to_csv(schedule_output, index=False, date_format="%Y-%m-%d")
    orders.to_csv(orders_output, index=False)
    print("\n结果已保存：", schedule_output)
    print("结果已保存：", orders_output)


if __name__ == "__main__":
    main()
