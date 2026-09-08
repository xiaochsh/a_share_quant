"""Day 5：使用虚构教学数据计算并绘制 5 日和 20 日均线。"""

from pathlib import Path

import pandas as pd
import matplotlib

# 将图保存到文件，兼容没有图形桌面的 Linux 环境。
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent.parent
# DEMO 为虚构股票，价格仅用于手算核对，不是真实行情。
df = pd.read_csv(root / "data/stock_day5_demo.csv", dtype={"code": str})
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["code", "date"])

# 分别处理每只股票，避免把不同股票的价格放在一起求平均。
# rolling(5) 每次取最近 5 条记录；mean() 计算它们的平均值。
# min_periods=5 表示必须有完整的 5 条记录才计算。
df["ma5"] = df.groupby("code")["close"].transform(
    lambda prices: prices.rolling(window=5, min_periods=5).mean()
)

# 保留前面的历史行，使用完整数据计算 MA20。
df["ma20"] = df.groupby("code")["close"].transform(
    lambda prices: prices.rolling(window=20, min_periods=20).mean()
)

print(df[["date", "code", "close", "ma5", "ma20"]].to_string(index=False))
print("\n均线缺失值数量：")
print(df[["ma5", "ma20"]].isna().sum())

# 只绘制虚构股票 DEMO，避免将不同股票连成一条线。
stock = df[df["code"] == "DEMO"]
# 用记录序号定位数据点；日期只作为刻度标签。
x = range(len(stock))
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x, stock["close"], label="Close", color="#2563eb", marker=".")
ax.plot(x, stock["ma5"], label="MA5", color="#d97706", marker=".")
ax.plot(x, stock["ma20"], label="MA20", color="#15803d", marker=".")
# 每隔 4 条记录显示日期，避免标签重叠；所有数据点仍参与绘图。
ticks = list(range(0, len(stock), 1))
labels = stock["date"].iloc[ticks].dt.strftime("%Y-%m-%d")
ax.set_xticks(ticks)
ax.set_xticklabels(labels, rotation=35, ha="right")
ax.set_title("DEMO: Close, MA5 and MA20 (synthetic data)")
ax.set_xlabel("Date (equally spaced trading records)")
ax.set_ylabel("Price")
ax.legend()
ax.grid(alpha=0.25)
fig.tight_layout()

output = root / "result/day5_ma_trading.png"
output.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(output, dpi=150)
plt.close(fig)
print("\n图表已保存：", output)
