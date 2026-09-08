"""Day 7：对比有未来数据泄漏和无泄漏的均线回测。"""

from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parent.parent
df = pd.read_csv(root / "data/stock_day5_demo.csv", dtype={"code": str})
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["code", "date"])

df["ma5"] = df.groupby("code")["close"].transform(
    lambda prices: prices.rolling(5, min_periods=5).mean()
)
df["ma20"] = df.groupby("code")["close"].transform(
    lambda prices: prices.rolling(20, min_periods=20).mean()
)
valid = df["ma5"].notna() & df["ma20"].notna()
df["signal"] = (valid & (df["ma5"] > df["ma20"])).astype(int)

# 继续沿用 Day 6 的教学假设：开盘价等于上一交易日收盘价。
df["open"] = df.groupby("code")["close"].shift(1)
df["open"] = df["open"].fillna(df["close"])
df["open_to_close_return"] = df["close"] / df["open"] - 1

# 错误：收盘后才确定的 signal 被当成本日开盘时已经持有。
df["leaky_position"] = df["signal"]
df["leaky_return"] = df["leaky_position"] * df["open_to_close_return"]
df["leaky_equity"] = (1 + df["leaky_return"]).cumprod()

# 正确：本日持仓只能依据上一条交易记录收盘后的信号。
df["correct_position"] = df.groupby("code")["signal"].shift(
    1, fill_value=0
)
df["correct_return"] = df["correct_position"] * df["open_to_close_return"]
df["correct_equity"] = (1 + df["correct_return"]).cumprod()

columns = [
    "date",
    "open",
    "close",
    "signal",
    "leaky_position",
    "correct_position",
    "leaky_return",
    "correct_return",
    "leaky_equity",
    "correct_equity",
]
print(df[columns].tail(7).to_string(index=False))

output = root / "result/day7_leakage_comparison.csv"
output.parent.mkdir(parents=True, exist_ok=True)
df[columns].to_csv(output, index=False)

print(f"\n错误回测最终净值：{df['leaky_equity'].iloc[-1]:.6f}")
print(f"正确回测最终净值：{df['correct_equity'].iloc[-1]:.6f}")
print(
    "虚增收益率："
    f"{df['leaky_equity'].iloc[-1] / df['correct_equity'].iloc[-1] - 1:.2%}"
)
