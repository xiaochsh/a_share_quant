"""第三阶段：按股票计算 20 日动量因子。

示例价格为虚构的复权价格，只用于理解计算窗口，不代表真实行情。
"""

from pathlib import Path

import pandas as pd


def calculate_momentum(data: pd.DataFrame, periods: int = 20) -> pd.DataFrame:
    """计算当前复权收盘价相对指定交易记录之前的收益率。"""
    result = data.copy()
    result["date"] = pd.to_datetime(result["date"])
    result["adjusted_close"] = pd.to_numeric(result["adjusted_close"])
    result = result.sort_values(["code", "date"], kind="stable").reset_index(
        drop=True
    )

    factor_name = f"momentum_{periods}d"
    result[factor_name] = result.groupby("code")["adjusted_close"].pct_change(
        periods=periods,
        fill_method=None,
    )
    return result


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    dates = pd.bdate_range("2026-01-05", periods=25)
    sample = pd.concat(
        [
            pd.DataFrame(
                {
                    "date": dates,
                    "code": "000001",
                    "adjusted_close": [100 + offset for offset in range(25)],
                }
            ),
            pd.DataFrame(
                {
                    "date": dates,
                    "code": "000002",
                    "adjusted_close": [100 - offset for offset in range(25)],
                }
            ),
        ],
        ignore_index=True,
    )

    result = calculate_momentum(sample, periods=20)
    columns = ["date", "code", "adjusted_close", "momentum_20d"]
    print(result.groupby("code", group_keys=False).tail(6)[columns].to_string(index=False))
    print("\n每只股票的有效 20 日动量数量：")
    print(result.groupby("code")["momentum_20d"].count().to_string())

    output = root / "result/stage3_momentum_factor.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result[columns].to_csv(output, index=False, date_format="%Y-%m-%d")
    print("\n结果已保存：", output)


if __name__ == "__main__":
    main()
