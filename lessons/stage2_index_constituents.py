"""第二阶段：按历史生效日期查询指数成分股。

数据为虚构教学示例，不代表任何真实指数的成分名单。
"""

from pathlib import Path

import pandas as pd


def constituents_on_date(rows: list[dict], query_date: str) -> pd.DataFrame:
    """返回指定日期已经生效且尚未失效的指数成分股。"""
    df = pd.DataFrame(rows)
    df["effective_from"] = pd.to_datetime(df["effective_from"])
    df["effective_to"] = pd.to_datetime(df["effective_to"])
    date = pd.Timestamp(query_date)

    is_effective = (df["effective_from"] <= date) & (
        df["effective_to"].isna() | (date < df["effective_to"])
    )
    return df.loc[is_effective].reset_index(drop=True)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    rows = [
        {
            "code": "600001",
            "effective_from": "2026-01-01",
            "effective_to": None,
        },
        {
            "code": "000002",
            "effective_from": "2026-01-01",
            "effective_to": "2026-09-15",
        },
        {
            "code": "300003",
            "effective_from": "2026-09-15",
            "effective_to": None,
        },
    ]

    snapshots = []
    for query_date in ["2026-09-14", "2026-09-16"]:
        snapshot = constituents_on_date(rows, query_date)
        snapshot.insert(0, "query_date", query_date)
        snapshots.append(snapshot)

    result = pd.concat(snapshots, ignore_index=True)
    print(result.to_string(index=False))

    output = root / "result/stage2_index_constituents.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print("\n结果已保存：", output)


if __name__ == "__main__":
    main()
