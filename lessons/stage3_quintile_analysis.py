"""第三阶段：同日按因子五分组并汇总未来收益。

示例数据为虚构数据。并列因子使用股票代码作为固定次级排序规则，
不会根据未来收益决定组别。
"""

from pathlib import Path

import pandas as pd


def assign_quintiles(
    data: pd.DataFrame,
    factor_column: str = "momentum_20d",
    groups: int = 5,
) -> pd.DataFrame:
    """在每个日期内按因子升序分成数量尽量接近的组。"""
    if groups < 1:
        raise ValueError("groups 必须大于等于 1")

    result = data.copy()
    result["date"] = pd.to_datetime(result["date"])
    result[factor_column] = pd.to_numeric(result[factor_column])
    result["code"] = result["code"].astype(str)
    result["quintile"] = pd.Series(pd.NA, index=result.index, dtype="string")

    valid = result.loc[result[factor_column].notna()]
    for _, same_day in valid.groupby("date", sort=True):
        ordered = same_day.sort_values(
            [factor_column, "code"], ascending=[True, True], kind="stable"
        )
        count = len(ordered)
        group_number = pd.Series(
            [position * groups // count + 1 for position in range(count)],
            index=ordered.index,
        )
        result.loc[ordered.index, "quintile"] = group_number.map(
            lambda number: f"G{number}"
        )
    return result


def calculate_quintile_returns(
    grouped_data: pd.DataFrame,
    future_return_column: str = "future_return_5d",
) -> pd.DataFrame:
    """汇总每个日期、每组的原始数量和有效未来收益。"""
    data = grouped_data.copy()
    data[future_return_column] = pd.to_numeric(data[future_return_column])
    valid_groups = data.loc[data["quintile"].notna()].copy()

    result = (
        valid_groups.groupby(["date", "quintile"], observed=True)
        .agg(
            original_count=("code", "size"),
            valid_return_count=(future_return_column, "count"),
            mean_future_return=(future_return_column, "mean"),
        )
        .reset_index()
    )
    result["missing_return_count"] = (
        result["original_count"] - result["valid_return_count"]
    )
    return result.sort_values(["date", "quintile"], kind="stable").reset_index(
        drop=True
    )


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    sample = pd.DataFrame(
        {
            "date": ["2026-03-02"] * 7,
            "code": list("ABCDEFG"),
            "momentum_20d": [-0.04, -0.01, 0.02, 0.02, 0.05, 0.08, 0.12],
            "future_return_5d": [-0.03, -0.01, 0.00, float("nan"), 0.02, 0.04, 0.06],
        }
    )
    grouped = assign_quintiles(sample)
    summary = calculate_quintile_returns(grouped)
    print("分组明细：")
    print(grouped.to_string(index=False))
    print("\n分组收益汇总：")
    print(summary.to_string(index=False))

    detail_output = root / "result/stage3_quintile_assignments.csv"
    summary_output = root / "result/stage3_quintile_returns.csv"
    detail_output.parent.mkdir(parents=True, exist_ok=True)
    grouped.to_csv(detail_output, index=False, date_format="%Y-%m-%d")
    summary.to_csv(summary_output, index=False, date_format="%Y-%m-%d")
    print("\n结果已保存：", detail_output)
    print("结果已保存：", summary_output)


if __name__ == "__main__":
    main()
