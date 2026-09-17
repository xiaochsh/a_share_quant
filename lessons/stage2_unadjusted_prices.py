"""第二阶段：观察不复权价格在除权日产生的机械跳变。

数据为虚构教学示例，仅用于比较价格收益与持仓市值收益。
"""

from pathlib import Path

import pandas as pd


def analyze_unadjusted_prices(rows: list[dict]) -> pd.DataFrame:
    """计算不复权价格收益和包含股数变化的持仓市值收益。"""
    df = pd.DataFrame(rows)
    df["raw_price_return"] = df["close"].pct_change()
    df["position_value"] = df["close"] * df["shares"]
    df["holding_value_return"] = df["position_value"].pct_change()
    return df


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    rows = [
        {
            "date": "2026-09-14",
            "event": "normal",
            "close": 19.50,
            "shares": 100,
        },
        {
            "date": "2026-09-15",
            "event": "before_ex_rights",
            "close": 20.00,
            "shares": 100,
        },
        {
            "date": "2026-09-16",
            "event": "10_for_10_ex_rights",
            "close": 10.10,
            "shares": 200,
        },
    ]

    result = analyze_unadjusted_prices(rows)
    print(result.to_string(index=False))

    output = root / "result/stage2_unadjusted_prices.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print("\n结果已保存：", output)


if __name__ == "__main__":
    main()
