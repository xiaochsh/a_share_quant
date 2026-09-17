# A 股量化学习笔记

本文汇总本项目学习过程中已经讲解的关键知识、常见错误和 Python/Pandas 用法。
学习顺序及尚未开始的内容以 [learning-roadmap.md](learning-roadmap.md) 为准，
当前掌握情况以 [progress.md](progress.md) 为准。

## 当前学习位置

- 第一阶段“股票与数据基础”已经完成。
- 第二阶段“A 股交易与数据特点”已经完成，包括真实 A 股日线数据的获取和检查。
- 正在学习第三阶段“因子入门”的第三个小任务：理解截面排名和未来收益。

## 股票日线数据

一行日线数据通常表示一只股票在一个交易日内的行情：

| 字段 | 通俗解释 |
| --- | --- |
| 股票代码 | 股票的标识，例如 `000001`；应按字符串保存，避免丢失开头的零 |
| 日期 | 该行行情对应的交易日 |
| 开盘价 | 当日开盘附近第一笔成交形成的价格 |
| 最高价 | 当日成交过的最高价格 |
| 最低价 | 当日成交过的最低价格 |
| 收盘价 | 当日收盘时形成的价格 |
| 成交量 | 当日成交的数量，必须确认数据源使用“股”还是“手” |
| 成交额 | 当日成交的金额，必须确认数据源的金额单位 |

OHLC 是开盘价、最高价、最低价和收盘价四个英文单词的首字母。基础逻辑关系为：

```text
最低价 ≤ 开盘价 ≤ 最高价
最低价 ≤ 收盘价 ≤ 最高价
```

通过这个检查只能发现明显错误，不能证明数据与交易所原始记录完全一致。

## 收益、净值和回撤

单日收益率表示价格相对上一交易日变化的比例：

```text
单日收益率 = 当日价格 / 上一交易日价格 - 1
```

累计收益不能简单相加，因为每天的收益作用在不同资金基数上。净值需要按时间连乘：

```text
净值 = (1 + 第一天收益) × (1 + 第二天收益) × ……
累计收益率 = 净值 - 1
```

例如先上涨 20%，再下跌 20%：

```text
1 × 1.2 × 0.8 = 0.96
```

最终亏损 4%，不是回到原点。

回撤表示净值从此前高点下跌了多少。最大回撤是整个研究区间内最严重的一次回撤，
用于描述策略曾经历的最大账面损失幅度。

## 均线

MA5 是最近 5 个交易日收盘价的平均值，MA20 是最近 20 个交易日收盘价的平均值。
这里的“日”指交易日，不是自然日。

严格的 MA5 需要 5 个有效价格，因此前 4 行是缺失值；严格的 MA20 前 19 行是缺失值。
这些缺失值不应填成 0，否则图中会产生虚假的价格跳变。
标准且需要统一比较的 MA5 应使用 `min_periods=5`。`min_periods=1` 可以用于允许不完整窗口的探索性展示，
但前 4 个结果分别只使用了 1～4 个有效价格，不能当作完整的 5 日均线。

均线使用更多历史价格时通常更平滑，但对新变化反应更慢。因此 MA20 通常比 MA5
更平滑、更滞后。改变图表横轴的显示方式只会改变视觉间距，不会改变均线数值。

## 策略、信号和持仓

- **策略**：根据数据作出投资决定的一组明确规则。
- **信号**：规则根据当前可知信息给出的目标，例如 `1` 表示希望持有，`0` 表示希望空仓。
- **目标持仓**：策略希望达到的仓位。
- **实际持仓**：考虑成交时点和交易限制后真正持有的仓位。
- **回测**：用历史数据模拟策略过去可能产生的结果。

信号不等于成交，也不等于实际持仓。连续三个信号都是 `1` 时，如果已经持仓，通常只是继续持有，
不需要每天重新买入。

## 信息时点和未来数据泄漏

当天最终收盘价只有在收盘后才能确定。使用当天收盘价生成信号后，不能假设自己已经在当天开盘成交，
更不能获得当天开盘到收盘的收益。这样做使用了当时尚不可知的信息，称为未来数据泄漏。

当前教学模型采用以下顺序：

1. 交易日收盘后，根据当天数据生成信号；
2. 下一交易日开盘时尝试执行；
3. 成交后才形成新的实际持仓；
4. 新持仓只承担成交之后的价格变化。

检查泄漏时应重点观察信号从 `0→1` 或 `1→0` 的转换行。信号长时间不变时，
只看某一行可能无法发现时序错误。

## 隔夜收益、日内收益和交易费用

- 买入日开盘前没有持仓，因此不获得上一收盘到买入开盘之间的隔夜收益。
- 卖出日开盘前仍有持仓，因此需要承担上一收盘到卖出开盘之间的隔夜涨跌。
- 开盘卖出后不再承担当日开盘到收盘的日内涨跌。

交易费用由仓位变化产生。仓位不变时不重复扣费；仓位从 `0.3` 调整到 `0.8`，换手比例是 `0.5`。
费用应在交易发生时从当时净值中扣除，之后的收益作用在扣费后的资金上。

## A 股交易日与数据缺口

工作日不一定是 A 股交易日，周末调休形成的工作日也可能休市。行情日期跨过周末或节假日，
不代表数据缺失。判断缺失必须与对应市场的交易日历核对。

`shift(1)` 取的是当前表格中的上一条记录。只有数据完整并且按股票、日期正确排序时，
它才可能代表上一交易日；如果数据漏了一行，`shift(1)` 不会自动发现。

## 停牌、涨跌停和成交

停牌时没有正常连续交易：

- 想买入但停牌时，目标持仓不能立即变成实际持仓；
- 已持有股票想卖出但停牌时，实际持仓仍然存在；
- 缺少某日行情不能单独证明停牌，也可能是数据缺失。

价格触及涨停或跌停不代表订单一定无法成交。是否成交还取决于订单方向、是否存在对手方、
排队顺序和可成交数量。仅凭日线 OHLC 数据通常无法确认某一笔具体订单是否成交。

## T+1

普通 A 股股票在 T 日买入后，总持仓立即增加，但当日可卖数量不增加。通常要到下一交易日，
这些股票才可以卖出。下一日指下一交易日，遇到周末或休市日要继续顺延。

回测中应区分：

- `position`：总持仓；
- `sellable_position`：当前可卖持仓。

否则可能错误地卖出当天刚买入的股票。

## 不复权、前复权和后复权

除权会让不复权价格发生机械跳变。直接对不复权收盘价计算收益，可能把送股、分红等产生的价格调整
误认为投资亏损。

- **不复权**：保留历史真实成交价格，但跨除权日不能直接用价格变化计算持有收益。
- **前复权**：保留较新价格的基准，调整更早的历史价格。
- **后复权**：保留较早价格的基准，调整除权日及之后的价格。

复权价格是根据复权因子计算出来的研究价格，不一定是当时真实成交价。前复权和后复权的数值可以不同；
当两组价格只相差固定倍数时，按比例计算得到的收益率相同。

## 股票池、幸存者偏差和指数成分股

股票池只是允许参与后续筛选和评分的候选集合，不等于策略信号，也不等于实际持仓。

如果回测过去时只保留今天仍然上市的股票，会提前删除后来退市或表现较差的股票，造成幸存者偏差。
历史回测必须保留股票在当时仍可投资期间的数据，因为当时无法知道它未来会退市。

指数成分股也会随时间调整。回测某个历史日期时，必须使用当时已经生效的成分名单，
不能使用今天或未来日期的名单。指数成分股可以作为股票池起点，但策略不必全部买入。

## 真实数据的基础检查

获取真实数据时，应同时记录：

- 数据来源；
- 股票代码；
- 查询日期范围；
- 不复权、前复权或后复权口径；
- 字段及单位说明。

下载成功不代表数据可以直接回测。当前脚本检查空数据、必要字段、日期排序、重复日期、缺失值、
OHLC 关系、负成交量和负成交额。对于固定历史区间，网络失败时可以读取已经保存且重新通过检查的缓存；
没有缓存时应明确报错。

## 因子入门

因子是在同一个时间点，按照同一套规则给股票计算的数值，用于比较和排序。因子定义至少要说明：

- 使用什么数据以及怎样计算；
- 数据在什么时间已经可以知道；
- 因子值越大越优，还是越小越优。

因子值只是评分依据，不等于买卖信号，也不等于实际持仓。完整过程是：

```text
原始数据 → 因子值 → 股票排序 → 策略选择 → 买卖信号 → 尝试成交 → 实际持仓
```

如果因子使用当天收盘价，只能在收盘后计算，并用于之后的交易，不能假设当天已经提前成交。
例如因子值为 A=`0.08`、B=`-0.02`、C=`0.03`，并规定数值越大越优时，排序为 A、C、B。

### 20 日动量

本项目把 20 日动量明确定义为当前收盘价相对 20 个交易记录之前收盘价的收益率：

```text
20 日动量 = 当前收盘价 / 20 个交易记录之前的收盘价 - 1
```

“相隔 20 个交易记录”需要首尾共 21 个收盘价，因此每只股票的前 20 行没有有效的 20 日动量。
价格序列必须先按股票分组并按日期排序。跨越除权日时，应使用口径一致的复权价格，避免把机械价格跳变误认为动量。

```python
df["momentum_20d"] = (
    df.groupby("code")["adjusted_close"]
    .pct_change(periods=20, fill_method=None)
)
```

`periods=20` 表示与同一只股票向前第 20 条记录比较；`fill_method=None` 表示遇到缺失价格时不自动向前填充。
若每只股票有 `N` 行完整价格，有效 20 日动量数量为 `N - 20`。例如 25 行产生 5 个有效值，
40 行产生 20 个有效值。

### 截面排名和未来收益

**截面**可以通俗理解为把时间停在某一个日期，同时观察许多只股票。截面排名只比较同一日期、
同一股票池中的股票，不能把一只股票今天的因子值和另一只股票昨天的因子值混在一起排名。

排名方向必须由因子的含义决定。例如规定“20 日动量越大越优”时，同一天 A=`8%`、B=`-2%`、
C=`3%`，从优到劣的顺序是 A、C、B。本项目在这个例子中把最优股票记为第 1 名。

**未来收益**是从因子日期向后观察一段时间的价格变化。本项目先用下面的定义学习：

```text
未来 N 日收益 = 第 t+N 条记录的收盘价 / 第 t 条记录的收盘价 - 1
```

20 日动量在日期 `t` 向后看历史价格，是该日的因子；未来 N 日收益从日期 `t` 向前看之后的价格，
要等未来数据出现后才能知道。它用于检验因子评分较高的股票后来是否表现较好，不能作为日期 `t`
选股时已经知道的输入，否则会引入未来数据泄漏。因为每只股票最后 N 条记录没有足够的未来价格，
它们的未来 N 日收益应保留为缺失值。

因子使用日期 `t` 的最终收盘价时，要到收盘后才完成计算。研究表中可以把日期 `t` 的因子与从
该收盘价开始计算的未来收益对齐，用来评价因子；实际回测仍须根据可知时点，在后续交易时段执行。

对应的 Pandas 计算分成两个方向：

```python
future_close = df.groupby("code")["adjusted_close"].shift(-5)
df["future_return_5d"] = future_close / df["adjusted_close"] - 1

df["factor_rank"] = df.groupby("date")["momentum_20d"].rank(
    method="min",
    ascending=False,
    na_option="keep",
)
```

`groupby("code")` 保证未来价格来自同一只股票；`shift(-5)` 把同组中向后第 5 条记录的价格移动到
当前行。`groupby("date")` 保证每个日期单独排名；`ascending=False` 表示数值越大排名越靠前；
`na_option="keep"` 保留无效因子的缺失排名。`method="min"` 表示因子值相同时共享较靠前的名次。

### IC（学习中）

IC 是信息系数（Information Coefficient）的简称，用于衡量同一个日期中，股票的因子值与其后续未来收益
是否存在同向或反向关系。它本质上是一种相关系数：相关系数是描述两组数值是否经常一起升高或一组升高、
另一组降低的数字，取值范围为 `-1` 到 `1`。

- IC 为正：因子值较高的股票，未来收益通常也较高，方向符合“因子越大越优”的预期；
- IC 为负：因子值较高的股票，未来收益通常较低，因子方向可能与预期相反；
- IC 接近 0：这一天的因子高低与未来收益高低没有明显关系。

IC 按日期分别计算，只使用同一天中因子值和未来收益都有效的股票。IC 是因子排序能力的统计指标，
不是收益率；例如 IC 为 `0.3` 不表示策略赚了 `30%`，也不能保证每只高分股票都会上涨。

## Python 基础用法

### 使用 `Path` 处理路径

```python
from pathlib import Path

root = Path(__file__).resolve().parent.parent
input_path = root / "data/stock.csv"
```

`/` 在这里用于拼接路径，能够兼容 Linux 和 Windows。不要手工拼接 `/` 或 `\\`。

### 函数与类型提示

```python
def calculate_return(price: float, previous_price: float) -> float:
    return price / previous_price - 1
```

类型提示说明参数和返回值的预期类型，方便阅读和检查；Python 默认不会仅凭类型提示自动阻止错误类型。

### 列表和字典

```python
columns = ["date", "code", "close"]
row = {"date": "2024-01-02", "code": "000001", "close": 9.21}
```

列表适合保存有顺序的一组值，字典适合保存“名称—值”对应关系。

### 异常处理

```python
try:
    data = fetch_data()
except requests.RequestException as error:
    raise RuntimeError("网络请求失败") from error
```

只捕获预计能够处理的异常。`raise ... from error` 会保留原始错误原因，方便排查。

## Pandas 用法速查

### 读取 CSV

```python
df = pd.read_csv("data/stock.csv", dtype={"code": str})
```

股票代码应指定为字符串，否则 `000001` 可能被读取成整数 `1`。

### 创建 DataFrame

```python
df = pd.DataFrame(
    {
        "date": ["2024-01-02", "2024-01-03"],
        "close": [10.0, 10.2],
    }
)
```

### 转换日期

```python
df["date"] = pd.to_datetime(
    df["date"],
    format="%Y-%m-%d",
    errors="coerce",
)
```

`errors="coerce"` 会把无法解析的值转换成 `NaT`，之后可以统一统计。其他选项是：

- `raise`：遇到错误立即抛出异常，也是默认值；
- `ignore`：无法转换时保留原输入，容易留下混合类型，通常不用于清洗后的研究数据。

### 转换数值

```python
numeric_columns = ["open", "high", "low", "close"]
df[numeric_columns] = df[numeric_columns].apply(
    pd.to_numeric,
    errors="coerce",
)
```

`apply()` 把 `pd.to_numeric` 依次应用到选中的每一列。无法转换的值会变成 `NaN`。

### 选择和新增列

```python
prices = df[["date", "code", "close"]]
df["daily_return"] = df["close"].pct_change()
df.insert(1, "source", "AKShare/东方财富")
```

`df[[...]]` 选择多列；给 `df["列名"]` 赋值可新增或覆盖列；`insert()` 可以指定新列位置。

### 排序

```python
df = df.sort_values(
    ["code", "date"],
    ascending=[True, True],
    na_position="last",
)
```

单列排序时可以通过 `kind` 选择算法：`quicksort`、`mergesort`、`heapsort` 或 `stable`。
`mergesort` 和 `stable` 会保留相同排序值原有的相对顺序。

```python
df = df.sort_values("date", kind="stable", ignore_index=True)
```

`ignore_index=True` 会把排序后的索引重新编号为 `0, 1, 2...`，等价于继续调用
`reset_index(drop=True)`。

### 按股票分组

```python
df["daily_return"] = df.groupby("code")["close"].pct_change()
```

先按股票代码分组，再在每只股票内部计算收益，避免把一只股票的最后价格和另一只股票的第一价格连接起来。

### 滚动计算均线

```python
df["ma5"] = df.groupby("code")["close"].transform(
    lambda prices: prices.rolling(window=5, min_periods=5).mean()
)
```

- `window=5`：每次使用最近 5 条记录；
- `min_periods=5`：至少有 5 个有效值才计算；
- `transform()`：让结果保持与原 DataFrame 相同的行数和索引。

### 移动数据

```python
df["target_at_open"] = (
    df.groupby("code")["signal"].shift(1, fill_value=0)
)
```

`shift(1)` 把同组数值向下移动一行。它移动的是记录，不是给日期增加一天。

### 单日收益和累计净值

```python
df["daily_return"] = df.groupby("code")["close"].pct_change()
df["equity"] = (1 + df["strategy_return"]).cumprod()
df["cumulative_return"] = df["equity"] - 1
```

`pct_change()` 计算相邻记录的比例变化；`cumprod()` 从上到下累计连乘。

### 布尔条件筛选

```python
valid = (df["low"] <= df["open"]) & (df["open"] <= df["high"])
bad_rows = df.loc[~valid]
```

- `&` 表示“并且”；
- `|` 表示“或者”；
- `~` 表示取反；
- 每个比较条件要用括号包围；
- `.loc[...]` 按条件选择行或列。

### 检查缺失值和重复值

```python
missing_count = int(df.isna().sum().sum())
duplicate_dates = int(df["date"].duplicated().sum())
```

`isna()` 标记缺失值，`duplicated()` 标记重复值。转换失败产生的 `NaN` 或 `NaT` 也能被 `isna()` 找到。

### 按位置取值

```python
first_close = df["close"].iloc[0]
last_equity = df["equity"].iloc[-1]
```

`iloc` 按行列位置访问；`-1` 表示最后一个位置。

### 合并数据

```python
result = pd.concat(frames, ignore_index=True)
```

`concat()` 可以把多个 DataFrame 按行或列连接。按行连接时使用 `ignore_index=True`，
可生成连续的新索引。

### 输出 CSV

```python
df.to_csv(
    "result/output.csv",
    index=False,
    date_format="%Y-%m-%d",
)
```

`index=False` 避免把 DataFrame 行索引额外写入 CSV；`date_format` 统一日期格式。

## 回测前检查清单

1. 股票代码是否按字符串读取，前导零是否保留？
2. 数据是否按股票代码和日期排序？
3. 日期是否重复，必要字段是否存在，数值是否缺失？
4. 日期缺口是否与交易日历核对，而不是直接认定停牌？
5. 价格是未复权、前复权还是后复权？
6. 成交量和成交额的单位是什么？
7. 信号使用的数据在当时是否已经可知？
8. 信号在哪个时点执行，订单是否一定能够成交？
9. 是否处理停牌、涨跌停、T+1 和交易费用？
10. 股票池和指数成分名单是否使用历史时点数据？

## 教学脚本索引

| 内容 | 脚本 |
| --- | --- |
| 读取和检查日线数据 | [`lessons/stage1_stock_data_basics.py`](../lessons/stage1_stock_data_basics.py) |
| MA5、MA20 和绘图 | [`lessons/stage1_moving_averages.py`](../lessons/stage1_moving_averages.py) |
| 均线信号、持仓、收益和净值 | [`lessons/stage1_moving_average_backtest.py`](../lessons/stage1_moving_average_backtest.py) |
| 未来数据泄漏 | [`lessons/stage1_lookahead_bias.py`](../lessons/stage1_lookahead_bias.py) |
| 成交时序和交易费用 | [`lessons/stage1_execution_timing_costs.py`](../lessons/stage1_execution_timing_costs.py) |
| 交易日 | [`lessons/stage2_trading_days.py`](../lessons/stage2_trading_days.py) |
| 停牌 | [`lessons/stage2_suspension.py`](../lessons/stage2_suspension.py) |
| 涨跌停 | [`lessons/stage2_price_limits.py`](../lessons/stage2_price_limits.py) |
| T+1 | [`lessons/stage2_t_plus_one.py`](../lessons/stage2_t_plus_one.py) |
| 不复权数据 | [`lessons/stage2_unadjusted_prices.py`](../lessons/stage2_unadjusted_prices.py) |
| 前复权 | [`lessons/stage2_forward_adjusted.py`](../lessons/stage2_forward_adjusted.py) |
| 后复权 | [`lessons/stage2_backward_adjusted.py`](../lessons/stage2_backward_adjusted.py) |
| 股票池和幸存者偏差 | [`lessons/stage2_stock_pool.py`](../lessons/stage2_stock_pool.py) |
| 指数成分股 | [`lessons/stage2_index_constituents.py`](../lessons/stage2_index_constituents.py) |
| 真实 A 股日线数据 | [`lessons/stage2_real_daily_data.py`](../lessons/stage2_real_daily_data.py) |
| 20 日动量因子 | [`lessons/stage3_momentum_factor.py`](../lessons/stage3_momentum_factor.py) |
| 截面排名和未来收益 | [`lessons/stage3_cross_sectional_rank.py`](../lessons/stage3_cross_sectional_rank.py) |
