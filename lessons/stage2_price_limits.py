"""第二阶段：演示涨跌停价格边界与订单能否成交的区别。

数据和成交条件均为虚构教学示例，不代表真实市场撮合结果。
"""

from pathlib import Path

import pandas as pd


def simulate_position(rows: list[dict]) -> pd.DataFrame:
    """根据目标仓位和简化的对手方条件，生成实际持仓变化。"""
    df = pd.DataFrame(rows)
    position = 0
    positions_before = []
    positions_after = []
    trades = []
    fill_statuses = []

    for row in df.itertuples():
        positions_before.append(position)

        if row.target_position == position:
            new_position = position
            fill_status = "no_trade_needed"
        elif not row.has_opposing_liquidity:
            new_position = position
            if row.target_position > position:
                fill_status = "blocked_no_seller"
            else:
                fill_status = "blocked_no_buyer"
        else:
            new_position = row.target_position
            fill_status = "filled"

        trades.append(new_position - position)
        position = new_position
        positions_after.append(position)
        fill_statuses.append(fill_status)

    df["position_before"] = positions_before
    df["trade"] = trades
    df["position_after"] = positions_after
    df["fill_status"] = fill_statuses
    return df


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    rows = [
        {
            "date": "2026-09-14",
            "price_state": "normal",
            "has_opposing_liquidity": True,
            "target_position": 0,
        },
        {
            "date": "2026-09-15",
            "price_state": "limit_up",
            "has_opposing_liquidity": False,
            "target_position": 1,
        },
        {
            "date": "2026-09-16",
            "price_state": "limit_up",
            "has_opposing_liquidity": True,
            "target_position": 1,
        },
        {
            "date": "2026-09-17",
            "price_state": "limit_down",
            "has_opposing_liquidity": False,
            "target_position": 0,
        },
        {
            "date": "2026-09-18",
            "price_state": "limit_down",
            "has_opposing_liquidity": True,
            "target_position": 0,
        },
    ]

    result = simulate_position(rows)
    print(result.to_string(index=False))

    output = root / "result/stage2_price_limits.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print("\n结果已保存：", output)


if __name__ == "__main__":
    main()
