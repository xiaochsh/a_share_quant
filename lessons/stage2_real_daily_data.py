"""第二阶段：获取并检查一只股票的真实 A 股日线数据。

数据通过 AKShare 的 ``stock_zh_a_hist`` 接口获取，来源为东方财富。
本课固定获取平安银行（000001）2024 年第一季度的不复权日线数据。
"""

from pathlib import Path
from typing import Callable

import pandas as pd
import requests


REQUIRED_SOURCE_COLUMNS = ["日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额"]
OUTPUT_COLUMNS = [
    "date",
    "symbol",
    "source",
    "adjustment",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
]


def prepare_daily_data(
    raw: pd.DataFrame, symbol: str, adjustment: str
) -> tuple[pd.DataFrame, dict[str, int]]:
    """统一字段并返回基础质量检查结果，不静默删除异常记录。"""
    missing_columns = [column for column in REQUIRED_SOURCE_COLUMNS if column not in raw.columns]
    if missing_columns:
        raise ValueError("缺少必要字段：" + "、".join(missing_columns))
    if raw.empty:
        raise ValueError("接口返回空数据，请检查股票代码、日期范围或网络连接")

    data = raw[REQUIRED_SOURCE_COLUMNS].rename(
        columns={
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
        }
    )
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    numeric_columns = ["open", "high", "low", "close", "volume", "amount"]
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="coerce")
    data.insert(1, "symbol", symbol)
    data.insert(2, "source", "AKShare/东方财富")
    data.insert(3, "adjustment", adjustment)
    data = data[OUTPUT_COLUMNS].sort_values("date", kind="stable").reset_index(drop=True)

    return inspect_daily_data(data)


def inspect_daily_data(data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """检查已经统一字段的日线数据，并保留异常记录供人工判断。"""
    missing_columns = [column for column in OUTPUT_COLUMNS if column not in data.columns]
    if missing_columns:
        raise ValueError("缓存缺少必要字段：" + "、".join(missing_columns))
    if data.empty:
        raise ValueError("日线数据为空")

    data = data[OUTPUT_COLUMNS].copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    numeric_columns = ["open", "high", "low", "close", "volume", "amount"]
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="coerce")
    data = data.sort_values("date", kind="stable").reset_index(drop=True)

    invalid_ohlc = (
        (data["low"] > data["open"])
        | (data["low"] > data["close"])
        | (data["high"] < data["open"])
        | (data["high"] < data["close"])
        | (data["low"] > data["high"])
    )
    checked_columns = ["date", *numeric_columns]
    report = {
        "row_count": len(data),
        "duplicate_dates": int(data["date"].duplicated().sum()),
        "missing_values": int(data[checked_columns].isna().sum().sum()),
        "invalid_ohlc_rows": int(invalid_ohlc.sum()),
        "negative_volume_rows": int((data["volume"] < 0).sum()),
        "negative_amount_rows": int((data["amount"] < 0).sum()),
    }
    return data, report


def obtain_daily_data(
    fetch: Callable[[], pd.DataFrame],
    cache_path: Path,
    symbol: str,
    adjustment: str,
) -> tuple[pd.DataFrame, dict[str, int], str]:
    """优先下载数据；网络失败时使用已存在且能通过检查的缓存。"""
    try:
        raw = fetch()
        data, report = prepare_daily_data(raw, symbol=symbol, adjustment=adjustment)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(cache_path, index=False, date_format="%Y-%m-%d")
        return data, report, "网络下载"
    except requests.RequestException as error:
        if not cache_path.is_file():
            raise RuntimeError("网络请求失败，并且没有可用的本地缓存") from error

        cached = pd.read_csv(cache_path, dtype={"symbol": str})
        data, report = inspect_daily_data(cached)
        if set(data["symbol"]) != {symbol} or set(data["adjustment"]) != {adjustment}:
            raise ValueError("本地缓存的股票代码或复权口径与本次请求不一致") from error
        return data, report, "本地缓存（网络请求失败）"


def main() -> None:
    import akshare as ak

    root = Path(__file__).resolve().parent.parent
    symbol = "000001"
    start_date = "20240102"
    end_date = "20240329"
    adjustment = "none"
    output = root / "data/real/stage2_000001_daily_unadjusted_2024q1.csv"

    data, report, retrieval = obtain_daily_data(
        fetch=lambda: ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="",
        ),
        cache_path=output,
        symbol=symbol,
        adjustment=adjustment,
    )

    print("数据来源：AKShare/东方财富")
    print("本次读取方式：", retrieval)
    print("股票代码：", symbol)
    print("复权口径：不复权")
    print("日期范围：", data["date"].min().date(), "至", data["date"].max().date())
    print("质量检查：")
    for name, value in report.items():
        print(f"  {name}: {value}")
    print("前 5 行：")
    print(data.head().to_string(index=False))
    print("数据已保存：", output)


if __name__ == "__main__":
    main()
