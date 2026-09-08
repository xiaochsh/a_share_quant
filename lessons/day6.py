"""Day 6：生成均线信号，并在简化假设下计算策略净值。"""

from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parent.parent
# 沿用 Day 5 的虚构教学数据。
df = pd.read_csv(root / "data/stock_day5_demo.csv", dtype={"code": str})
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["code", "date"])

df["ma5"] = df.groupby("code")["close"].transform(
    lambda prices: prices.rolling(window=5, min_periods=5).mean()
)
df["ma20"] = df.groupby("code")["close"].transform(
    lambda prices: prices.rolling(window=20, min_periods=20).mean()
)

# notna() 检查是否有有效数值；& 要求两个条件同时成立。
valid = df["ma5"].notna() & df["ma20"].notna()
# astype(int) 将 True 转为 1，False 转为 0。
# signal 是本行收盘后才可知的目标状态，不是本行的实际持仓。
df["signal"] = (valid & (df["ma5"] > df["ma20"])).astype(int)

# 每只股票内部向下移一行：本行开盘目标取自上一行收盘信号。
# 数据已按日期排序；本例交易记录完整，下一行对应下一交易日。
# fill_value=0 只填补移位新增的空位，表示每只股票起始目标为空仓。
# target_at_open 是执行目标，不代表订单已经成交。
df["target_at_open"] = df.groupby("code")["signal"].shift(1, fill_value=0)

# 教学假设：本日开盘价等于上一交易日收盘价，因此没有隔夜跳空。
# 每只股票第一行没有前收盘价，令其开盘价等于本行收盘价。
df["open"] = df.groupby("code")["close"].shift(1)
df["open"] = df["open"].fillna(df["close"])

# 教学假设：所有开盘目标都能立刻成交，所以实际持仓等于开盘目标。
df["position"] = df["target_at_open"]

# 空仓时 position=0，策略收益为 0；持仓时获得开盘到收盘的涨跌幅。
df["open_to_close_return"] = df["close"] / df["open"] - 1
df["strategy_return"] = df["position"] * df["open_to_close_return"]

# cumprod() 连乘每日资金增长倍数，初始净值设为 1.0。
df["equity"] = (1 + df["strategy_return"]).cumprod()
# 净值 1.0 对应累计收益 0；两者相差 1。
df["cumulative_return"] = df["equity"] - 1

columns = [
    "date",
    "code",
    "open",
    "close",
    "ma5",
    "ma20",
    "signal",
    "target_at_open",
    "position",
    "strategy_return",
    "equity",
    "cumulative_return",
]
print(df[columns].to_string(index=False))

output = root / "result/day6_signals.csv"
output.parent.mkdir(parents=True, exist_ok=True)
df[columns].to_csv(output, index=False)
print("\n信号已保存：", output)
print(f"最终净值：{df['equity'].iloc[-1]:.6f}")
print(f"累计收益率：{df['cumulative_return'].iloc[-1]:.2%}")
