"""第三阶段：按日期计算普通 IC 和 Rank IC。

示例数据为虚构数据，只用于理解相关方向、有效样本配对和 NaN。
"""

from pathlib import Path

import pandas as pd


def calculate_daily_ic(
    data: pd.DataFrame,
    factor_column: str = "momentum_20d",
    future_return_column: str = "future_return_5d",
) -> pd.DataFrame:
    """使用同日有效配对分别计算 Pearson IC 和 Rank IC。"""
    result = data.copy()
    result["date"] = pd.to_datetime(result["date"])
    result[factor_column] = pd.to_numeric(result[factor_column])
    result[future_return_column] = pd.to_numeric(result[future_return_column])

    rows: list[dict[str, object]] = []
    for date, same_day in result.groupby("date", sort=True):
        valid = same_day[[factor_column, future_return_column]].dropna()
        pearson_ic = float("nan")
        rank_ic = float("nan")
        if (
            len(valid) >= 2
            and valid[factor_column].nunique() >= 2
            and valid[future_return_column].nunique() >= 2
        ):
            pearson_ic = valid[factor_column].corr(valid[future_return_column])
            factor_rank = valid[factor_column].rank(method="average")
            return_rank = valid[future_return_column].rank(method="average")
            rank_ic = factor_rank.corr(return_rank)
        rows.append(
            {
                "date": date,
                "valid_pair_count": len(valid),
                "pearson_ic": pearson_ic,
                "rank_ic": rank_ic,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    sample = pd.DataFrame(
        {
            "date": ["2026-03-02"] * 5 + ["2026-03-03"] * 5,
            "code": ["A", "B", "C", "D", "E"] * 2,
            "momentum_20d": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
            "future_return_5d": [0.01, 0.02, 0.04, 0.03, 0.05, 0.05, 0.04, 0.03, 0.02, float("nan")],
        }
    )
    result = calculate_daily_ic(sample)
    print(result.to_string(index=False))

    output = root / "result/stage3_ic.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False, date_format="%Y-%m-%d")
    print("\n结果已保存：", output)


if __name__ == "__main__":
    main()
