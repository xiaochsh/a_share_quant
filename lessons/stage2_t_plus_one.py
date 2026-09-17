"""第二阶段：演示普通 A 股股票的 T+1 卖出限制。

数据为虚构教学示例，不连接券商，也不进行真实交易。
"""

from pathlib import Path

import pandas as pd


def simulate_t_plus_one(events: list[dict]) -> pd.DataFrame:
    """按时间顺序模拟总持仓与可卖数量的变化。"""
    df = pd.DataFrame(events)
    total_shares = 0
    sellable_shares = 0
    current_date = None
    records = []

    for event in df.itertuples(index=False):
        if event.date != current_date:
            # 进入下一条实际交易日记录时，之前买入并保留的股票变为可卖。
            sellable_shares = total_shares
            current_date = event.date

        total_before = total_shares
        sellable_before = sellable_shares

        if event.action == "buy":
            executed_shares = event.requested_shares
            total_shares += executed_shares
            status = "buy_filled"
        elif event.action == "sell" and event.requested_shares <= sellable_shares:
            executed_shares = event.requested_shares
            total_shares -= executed_shares
            sellable_shares -= executed_shares
            status = "sell_filled"
        elif event.action == "sell":
            executed_shares = 0
            status = "blocked_t_plus_one"
        else:
            raise ValueError(f"未知交易动作：{event.action}")

        records.append(
            {
                "total_shares_before": total_before,
                "sellable_shares_before": sellable_before,
                "executed_shares": executed_shares,
                "total_shares_after": total_shares,
                "sellable_shares_after": sellable_shares,
                "status": status,
            }
        )

    return pd.concat([df, pd.DataFrame(records)], axis=1)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    events = [
        {
            "date": "2026-09-18",
            "time": "10:00",
            "action": "buy",
            "requested_shares": 100,
        },
        {
            "date": "2026-09-18",
            "time": "14:00",
            "action": "sell",
            "requested_shares": 100,
        },
        {
            "date": "2026-09-21",
            "time": "09:30",
            "action": "sell",
            "requested_shares": 100,
        },
    ]

    result = simulate_t_plus_one(events)
    print(result.to_string(index=False))

    output = root / "result/stage2_t_plus_one.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print("\n结果已保存：", output)


if __name__ == "__main__":
    main()
