"""第二阶段：演示停牌时目标持仓与实际持仓的差异。"""

from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parent.parent

# 全部日期都是市场交易日，但 DEMO 股票在其中两天停牌。
df = pd.DataFrame(
    {
        "date": pd.to_datetime(
            ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"]
        ),
        "market_open": [True, True, True, True, True],
        "is_suspended": [False, True, False, True, False],
        "target_position": [0, 1, 1, 0, 0],
    }
)

position = 0
positions_before = []
positions_after = []
trades = []

for row in df.itertuples():
    positions_before.append(position)

    # 停牌时无法调整仓位；可交易时才把实际持仓调整到目标持仓。
    if row.market_open and not row.is_suspended:
        new_position = row.target_position
    else:
        new_position = position

    trades.append(new_position - position)
    position = new_position
    positions_after.append(position)

df["position_before"] = positions_before
df["trade"] = trades
df["position_after"] = positions_after

print(df.to_string(index=False))

output = root / "result/stage2_suspension.csv"
output.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output, index=False)
print("\n结果已保存：", output)
