"""第二阶段：用当日已知状态生成一个简化股票池。

数据为虚构教学示例，不代表真实股票状态或选股建议。
"""

from pathlib import Path

import pandas as pd


def build_stock_pool(rows: list[dict]) -> pd.DataFrame:
    """标记每只股票是否满足本课的全部股票池规则。"""
    df = pd.DataFrame(rows)

    def exclusion_reason(row: pd.Series) -> str:
        if not row["is_listed"]:
            return "not_listed"
        if row["is_suspended"]:
            return "suspended"
        if row["is_risk_warning"]:
            return "risk_warning"
        if not row["has_enough_history"]:
            return "insufficient_history"
        return "eligible"

    df["exclusion_reason"] = df.apply(exclusion_reason, axis=1)
    df["in_pool"] = df["exclusion_reason"].eq("eligible")
    return df


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    rows = [
        {
            "date": "2026-09-16",
            "code": "600001",
            "is_listed": True,
            "is_suspended": False,
            "is_risk_warning": False,
            "has_enough_history": True,
        },
        {
            "date": "2026-09-16",
            "code": "000002",
            "is_listed": True,
            "is_suspended": True,
            "is_risk_warning": False,
            "has_enough_history": True,
        },
        {
            "date": "2026-09-16",
            "code": "300003",
            "is_listed": True,
            "is_suspended": False,
            "is_risk_warning": True,
            "has_enough_history": True,
        },
        {
            "date": "2026-09-16",
            "code": "688004",
            "is_listed": False,
            "is_suspended": False,
            "is_risk_warning": False,
            "has_enough_history": False,
        },
        {
            "date": "2026-09-16",
            "code": "600005",
            "is_listed": True,
            "is_suspended": False,
            "is_risk_warning": False,
            "has_enough_history": False,
        },
    ]

    result = build_stock_pool(rows)
    print(result.to_string(index=False))
    print("\n股票池代码：", result.loc[result["in_pool"], "code"].tolist())

    output = root / "result/stage2_stock_pool.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print("结果已保存：", output)


if __name__ == "__main__":
    main()
