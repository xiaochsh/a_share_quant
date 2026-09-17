"""第二阶段：观察交易记录与自然日间隔。

数据是虚构教学数据，只用于理解日期间隔，不代表官方 A 股交易日历。
"""

from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parent.parent
df = pd.read_csv(root / "data/stage1_moving_average_sample.csv", dtype={"code": str})
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["code", "date"])

# shift(1) 取得同一只股票的上一条交易记录，不是简单减去一个自然日。
df["previous_record_date"] = df.groupby("code")["date"].shift(1)
df["calendar_gap_days"] = (df["date"] - df["previous_record_date"]).dt.days

columns = ["previous_record_date", "date", "calendar_gap_days"]
print("相邻记录相隔超过 1 个自然日的位置：")
print(df.loc[df["calendar_gap_days"] > 1, columns].to_string(index=False))

print("\n说明：这些行在教学数据中仍是相邻交易记录。")
print("真实数据是否缺失，必须与对应市场的官方交易日历核对。")
