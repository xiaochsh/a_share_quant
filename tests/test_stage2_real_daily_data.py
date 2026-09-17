import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import requests

from lessons.stage2_real_daily_data import obtain_daily_data, prepare_daily_data


class RealDailyDataTest(unittest.TestCase):
    def test_prepares_valid_rows_and_reports_no_quality_problems(self):
        raw = pd.DataFrame(
            {
                "日期": ["2024-01-03", "2024-01-02"],
                "开盘": [10.2, 10.0],
                "收盘": [10.3, 10.1],
                "最高": [10.4, 10.2],
                "最低": [10.1, 9.9],
                "成交量": [1200, 1000],
                "成交额": [12360.0, 10100.0],
            }
        )

        data, report = prepare_daily_data(raw, symbol="000001", adjustment="none")

        self.assertEqual(data["date"].dt.strftime("%Y-%m-%d").tolist(), ["2024-01-02", "2024-01-03"])
        self.assertEqual(data["symbol"].tolist(), ["000001", "000001"])
        self.assertEqual(data["adjustment"].tolist(), ["none", "none"])
        self.assertEqual(data["source"].tolist(), ["AKShare/东方财富", "AKShare/东方财富"])
        self.assertEqual(report["row_count"], 2)
        self.assertEqual(report["duplicate_dates"], 0)
        self.assertEqual(report["missing_values"], 0)
        self.assertEqual(report["invalid_ohlc_rows"], 0)
        self.assertEqual(report["negative_volume_rows"], 0)
        self.assertEqual(report["negative_amount_rows"], 0)

    def test_reports_duplicate_missing_and_logically_invalid_rows(self):
        raw = pd.DataFrame(
            {
                "日期": ["2024-01-02", "2024-01-02"],
                "开盘": [10.0, 10.0],
                "收盘": [10.1, None],
                "最高": [10.2, 9.8],
                "最低": [9.9, 10.1],
                "成交量": [1000, -1],
                "成交额": [10100.0, -10.0],
            }
        )

        _, report = prepare_daily_data(raw, symbol="000001", adjustment="none")

        self.assertEqual(report["duplicate_dates"], 1)
        self.assertEqual(report["missing_values"], 1)
        self.assertEqual(report["invalid_ohlc_rows"], 1)
        self.assertEqual(report["negative_volume_rows"], 1)
        self.assertEqual(report["negative_amount_rows"], 1)

    def test_rejects_missing_required_source_columns(self):
        raw = pd.DataFrame({"日期": ["2024-01-02"], "收盘": [10.1]})

        with self.assertRaisesRegex(ValueError, "缺少必要字段"):
            prepare_daily_data(raw, symbol="000001", adjustment="none")

    def test_uses_checked_cache_when_network_request_fails(self):
        cached = pd.DataFrame(
            {
                "date": ["2024-01-02"],
                "symbol": ["000001"],
                "source": ["AKShare/东方财富"],
                "adjustment": ["none"],
                "open": [10.0],
                "high": [10.2],
                "low": [9.9],
                "close": [10.1],
                "volume": [1000],
                "amount": [10100.0],
            }
        )

        def failed_fetch():
            raise requests.ConnectionError("temporary network failure")

        with TemporaryDirectory() as directory:
            cache_path = Path(directory) / "daily.csv"
            cached.to_csv(cache_path, index=False)

            data, report, retrieval = obtain_daily_data(
                fetch=failed_fetch,
                cache_path=cache_path,
                symbol="000001",
                adjustment="none",
            )

        self.assertEqual(retrieval, "本地缓存（网络请求失败）")
        self.assertEqual(data["symbol"].tolist(), ["000001"])
        self.assertEqual(report["row_count"], 1)
        self.assertEqual(report["missing_values"], 0)


if __name__ == "__main__":
    unittest.main()
