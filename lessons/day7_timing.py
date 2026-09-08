"""Day 7：拆分隔夜收益与日内收益，检查开盘成交时序。"""

from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parent.parent

# 三天虚构数据：第 1 天收盘产生买入信号，第 2 天收盘产生卖出信号。
df = pd.DataFrame(
    {
        "date": pd.to_datetime(["2026-09-07", "2026-09-08", "2026-09-09"]),
        "open": [10.0, 11.0, 9.0],
        "close": [10.0, 12.0, 8.5],
        "signal": [1, 0, 0],
    }
)

# 今日开盘目标来自上一交易日收盘信号。
df["target_at_open"] = df["signal"].shift(1, fill_value=0)

# 假设开盘目标都能成交。开盘后的持仓等于目标；开盘前仍是昨日持仓。
df["position_after_open"] = df["target_at_open"]
df["position_before_open"] = df["position_after_open"].shift(1, fill_value=0)

print(
    df[
        [
            "date",
            "open",
            "close",
            "signal",
            "position_before_open",
            "position_after_open",
        ]
    ].to_string(index=False)
)

previous_close = df["close"].shift(1)
df["overnight_asset_return"] = df["open"] / previous_close - 1
df["overnight_asset_return"] = df["overnight_asset_return"].fillna(0)
df["intraday_asset_return"] = df["close"] / df["open"] - 1

# 隔夜收益由开盘前持仓决定；日内收益由开盘成交后的持仓决定。
df["overnight_strategy_return"] = (
    df["position_before_open"] * df["overnight_asset_return"]
)
df["intraday_strategy_return"] = (
    df["position_after_open"] * df["intraday_asset_return"]
)

df["daily_growth"] = (1 + df["overnight_strategy_return"]) * (
    1 + df["intraday_strategy_return"]
)
df["equity"] = df["daily_growth"].cumprod()

# 简化费用模型：每次交易按成交仓位的 0.1% 扣费。
# 这只是教学费率，不代表现实账户的固定收费标准。
fee_rate = 0.001
df["turnover"] = (df["position_after_open"] - df["position_before_open"]).abs()
df["cost_rate"] = df["turnover"] * fee_rate

# 先承担隔夜涨跌，在开盘调整仓位并扣费，再承担成交后的日内涨跌。
df["net_daily_growth"] = (
    (1 + df["overnight_strategy_return"])
    * (1 - df["cost_rate"])
    * (1 + df["intraday_strategy_return"])
)
df["equity_after_cost"] = df["net_daily_growth"].cumprod()

print(df.to_string(index=False))

output = root / "result/day7_timing.csv"
output.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output, index=False)
print(f"\n最终净值：{df['equity'].iloc[-1]:.6f}")
print(f"扣费后最终净值：{df['equity_after_cost'].iloc[-1]:.6f}")
