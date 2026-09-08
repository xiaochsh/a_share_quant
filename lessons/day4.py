import pandas as pd

# 读取CSV文件
df = pd.read_csv("data/stock_day4.csv")

# 查看前5行
print("前5行数据：")
print(df.head())

# 查看表格规模
print("\n行数和列数：")
print(df.shape)

# 查看每一列的数据类型
print("\n数据类型：")
print(df.dtypes)

# 将日期文本转换为Pandas的日期类型
df["date"] = pd.to_datetime(df["date"])

# 先按照股票代码排序，再按照日期排序
df = df.sort_values(["code", "date"])

print("\n排序后的日期和收盘价：")
print(df[["date", "code", "close"]])

print(
    df.iloc[0:5][["date", "code", "close"]]
)  # 查看第一行的日期、股票代码和收盘价

# 分别对每只股票计算收盘价涨跌幅
df["daily_return"] = df.groupby("code")["close"].pct_change()

# 转换成百分数，只用于展示
df["daily_return_pct"] = df["daily_return"] * 100

print("\n每日收盘收益率：")
print(df[["date", "close", "daily_return_pct"]])

# 检查每一列有多少个缺失值
print("\n各列缺失值数量：")
print(df.isna().sum())

# 检查“股票代码+日期”是否出现重复
duplicate_count = df.duplicated(subset=["code", "date"]).sum()

print("\n重复行情数量：")
print(duplicate_count)

# 检查价格关系是否明显异常
invalid_price = df[
    (df["high"] < df["low"])
    | (df["high"] < df["open"])
    | (df["high"] < df["close"])
    | (df["low"] > df["open"])
    | (df["low"] > df["close"])
]

print("\n价格关系异常的数据：")
print(invalid_price)

df.to_csv("result/stock_day4_result.csv", index=False)
