"""第四阶段：从历史时点股票池中按因子选择目标股票。"""

from pathlib import Path

import pandas as pd


def select_factor_stocks(
    data: pd.DataFrame,
    factor_column: str = "momentum_20d",
    selection_count: int = 2,
    higher_is_better: bool = True,
) -> pd.DataFrame:
    """先筛选当日股票池，再按因子和股票代码生成目标名单。"""
    if selection_count < 1:
        raise ValueError("selection_count 必须大于等于 1")

    result = data.copy()
    result["date"] = pd.to_datetime(result["date"])
    result["code"] = result["code"].astype(str)
    result[factor_column] = pd.to_numeric(result[factor_column])
    result["eligible"] = result["eligible"].astype(bool)
    result["selection_rank"] = float("nan")
    result["selected"] = False

    candidates = result.loc[result["eligible"] & result[factor_column].notna()]
    for _, same_day in candidates.groupby("date", sort=True):
        ordered = same_day.sort_values(
            [factor_column, "code"],
            ascending=[not higher_is_better, True],
            kind="stable",
        )
        ranks = pd.Series(range(1, len(ordered) + 1), index=ordered.index)
        result.loc[ordered.index, "selection_rank"] = ranks
        result.loc[ordered.index[:selection_count], "selected"] = True
    return result.sort_values(["date", "selection_rank", "code"], na_position="last").reset_index(drop=True)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    sample = pd.DataFrame(
        {
            "date": ["2026-03-06"] * 5,
            "code": ["A", "B", "C", "D", "E"],
            "momentum_20d": [0.08, -0.02, 0.03, 0.50, float("nan")],
            "eligible": [True, True, True, False, True],
        }
    )
    result = select_factor_stocks(sample)
    print(result.to_string(index=False))

    output = root / "result/stage4_factor_selection.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False, date_format="%Y-%m-%d")
    print("\n结果已保存：", output)


if __name__ == "__main__":
    main()
