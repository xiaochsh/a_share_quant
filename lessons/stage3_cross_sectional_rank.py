"""第三阶段：计算同日截面排名和未来收益。

示例数据为虚构的复权价格，只用于理解排名范围和时间方向。
"""

from pathlib import Path

import pandas as pd

from lessons.stage3_momentum_factor import calculate_momentum


def calculate_rank_and_future_return(
    data: pd.DataFrame,
    factor_column: str = "momentum_20d",
    future_periods: int = 5,
) -> pd.DataFrame:
    """按日期对因子降序排名，并按股票计算未来收益。"""
    result = data.copy()
    result["date"] = pd.to_datetime(result["date"])
    result["adjusted_close"] = pd.to_numeric(result["adjusted_close"])
    result[factor_column] = pd.to_numeric(result[factor_column])
    result = result.sort_values(["code", "date"], kind="stable").reset_index(
        drop=True
    )

    future_column = f"future_return_{future_periods}d"
    future_close = result.groupby("code")["adjusted_close"].shift(-future_periods)
    result[future_column] = future_close / result["adjusted_close"] - 1

    result["factor_rank"] = result.groupby("date")[factor_column].rank(
        method="min",
        ascending=False,
        na_option="keep",
    )
    return result


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    dates = pd.bdate_range("2026-01-05", periods=31)
    sample = pd.concat(
        [
            pd.DataFrame(
                {
                    "date": dates,
                    "code": "A",
                    "adjusted_close": [100 + offset for offset in range(31)],
                }
            ),
            pd.DataFrame(
                {
                    "date": dates,
                    "code": "B",
                    "adjusted_close": [100 + 2 * offset for offset in range(31)],
                }
            ),
            pd.DataFrame(
                {
                    "date": dates,
                    "code": "C",
                    "adjusted_close": [100 - offset for offset in range(31)],
                }
            ),
        ],
        ignore_index=True,
    )

    with_momentum = calculate_momentum(sample, periods=20)
    result = calculate_rank_and_future_return(with_momentum, future_periods=5)
    columns = [
        "date",
        "code",
        "adjusted_close",
        "momentum_20d",
        "factor_rank",
        "future_return_5d",
    ]
    comparable = result.loc[
        result["momentum_20d"].notna() & result["future_return_5d"].notna(),
        columns,
    ].sort_values(["date", "factor_rank"])

    print("同时具有因子值和未来收益的记录：")
    print(comparable.to_string(index=False))

    output = root / "result/stage3_cross_sectional_rank.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result[columns].to_csv(output, index=False, date_format="%Y-%m-%d")
    print("\n结果已保存：", output)


if __name__ == "__main__":
    main()
