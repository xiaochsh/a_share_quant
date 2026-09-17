"""第二阶段：用简化复权因子理解前复权价格。

数据为虚构教学示例。真实项目应使用可靠数据源提供的复权因子。
"""

from pathlib import Path

import pandas as pd


def calculate_forward_adjusted(rows: list[dict]) -> pd.DataFrame:
    """以最后一条记录的复权因子为基准计算前复权收盘价。"""
    df = pd.DataFrame(rows)
    latest_factor = df["adjustment_factor"].iloc[-1]
    df["qfq_close"] = df["close"] * df["adjustment_factor"] / latest_factor
    df["raw_price_return"] = df["close"].pct_change()
    df["qfq_return"] = df["qfq_close"].pct_change()
    return df


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    rows = [
        {
            "date": "2026-09-14",
            "event": "normal",
            "close": 19.50,
            "adjustment_factor": 1.0,
        },
        {
            "date": "2026-09-15",
            "event": "before_ex_rights",
            "close": 20.00,
            "adjustment_factor": 1.0,
        },
        {
            "date": "2026-09-16",
            "event": "10_for_10_ex_rights",
            "close": 10.10,
            "adjustment_factor": 2.0,
        },
    ]

    result = calculate_forward_adjusted(rows)
    print(result.to_string(index=False))

    output = root / "result/stage2_forward_adjusted.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print("\n结果已保存：", output)


if __name__ == "__main__":
    main()
