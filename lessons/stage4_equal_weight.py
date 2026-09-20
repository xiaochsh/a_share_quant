"""第四阶段：为目标股票分配等权目标仓位。"""

from pathlib import Path

import pandas as pd


def calculate_equal_weight_targets(
    data: pd.DataFrame,
    cash_weight: float = 0.0,
) -> pd.DataFrame:
    """把扣除预留现金后的资金在每个日期的入选股票间等分。"""
    if not 0 <= cash_weight < 1:
        raise ValueError("cash_weight 必须满足 0 <= cash_weight < 1")

    result = data.copy()
    result["date"] = pd.to_datetime(result["date"])
    result["selected"] = result["selected"].astype(bool)
    selected_count = result.groupby("date")["selected"].transform("sum")
    result["target_weight"] = 0.0
    selected = result["selected"] & selected_count.gt(0)
    result.loc[selected, "target_weight"] = (
        1 - cash_weight
    ) / selected_count.loc[selected]
    return result


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    sample = pd.DataFrame(
        {
            "date": ["2026-03-06"] * 4,
            "code": ["A", "B", "C", "D"],
            "selected": [True, True, True, False],
            "price": [10.0, 20.0, 50.0, 8.0],
        }
    )
    result = calculate_equal_weight_targets(sample, cash_weight=0.10)
    portfolio_value = 100_000
    result["target_value"] = result["target_weight"] * portfolio_value
    result["theoretical_shares"] = result["target_value"] / result["price"]
    print(result.to_string(index=False))

    output = root / "result/stage4_equal_weight.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False, date_format="%Y-%m-%d")
    print("\n结果已保存：", output)


if __name__ == "__main__":
    main()
