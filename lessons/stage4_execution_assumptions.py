"""第四阶段：检查未来数据泄漏和错误成交假设。

示例数据均为虚构数据，只用于演示信息、决策、成交的时间顺序，
以及目标持仓如何经过可交易性检查后成为实际持仓。
"""

from pathlib import Path

import pandas as pd


def audit_event_timing(events: pd.DataFrame) -> pd.DataFrame:
    """检查数据可知、策略决策和订单成交是否保持正确顺序。"""
    result = events.copy()
    time_columns = ["data_available_at", "decision_at", "execution_at"]
    for column in time_columns:
        result[column] = pd.to_datetime(result[column])

    data_known_before_decision = (
        result["data_available_at"] <= result["decision_at"]
    )
    decision_before_execution = result["decision_at"] <= result["execution_at"]
    result["timing_valid"] = data_known_before_decision & decision_before_execution

    result["timing_issue"] = "时间顺序正确"
    result.loc[~data_known_before_decision, "timing_issue"] = "决策使用了尚不可知的数据"
    result.loc[
        data_known_before_decision & ~decision_before_execution,
        "timing_issue",
    ] = "成交时间早于决策时间"
    return result


def simulate_next_day_execution(
    targets: pd.DataFrame,
    trading_calendar: pd.DatetimeIndex,
) -> pd.DataFrame:
    """把收盘目标安排到下一交易日，并只在可交易时更新实际权重。"""
    result = targets.copy()
    result["signal_date"] = pd.to_datetime(result["signal_date"])
    result["can_trade"] = result["can_trade"].astype(bool)
    calendar = pd.DatetimeIndex(pd.to_datetime(trading_calendar)).sort_values().unique()

    def next_trading_day(signal_date: pd.Timestamp) -> pd.Timestamp:
        position = calendar.searchsorted(signal_date, side="right")
        if position >= len(calendar):
            return pd.NaT
        return calendar[position]

    result["execution_date"] = result["signal_date"].map(next_trading_day)
    result["filled"] = result["execution_date"].notna() & result["can_trade"]
    result["actual_weight_after"] = result["actual_weight_before"]
    result.loc[result["filled"], "actual_weight_after"] = result.loc[
        result["filled"], "target_weight"
    ]
    return result


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    timing_cases = pd.DataFrame(
        {
            "case": ["正确流程", "错误：提前使用收盘数据", "错误：成交早于决策"],
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
    audit = audit_event_timing(timing_cases)

    targets = pd.DataFrame(
        {
            "signal_date": ["2026-03-06", "2026-03-06"],
            "code": ["A", "B"],
            "target_weight": [0.50, 0.00],
            "actual_weight_before": [0.00, 0.40],
            "can_trade": [True, False],
        }
    )
    calendar = pd.to_datetime(["2026-03-06", "2026-03-09", "2026-03-10"])
    executions = simulate_next_day_execution(targets, calendar)

    print("时间顺序检查：")
    print(audit.to_string(index=False))
    print("\n下一交易日成交检查：")
    print(executions.to_string(index=False))

    audit_output = root / "result/stage4_timing_audit.csv"
    execution_output = root / "result/stage4_execution_assumptions.csv"
    audit_output.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(audit_output, index=False, date_format="%Y-%m-%d %H:%M")
    executions.to_csv(execution_output, index=False, date_format="%Y-%m-%d")
    print("\n结果已保存：", audit_output)
    print("结果已保存：", execution_output)


if __name__ == "__main__":
    main()
