import unittest

import pandas as pd

from lessons.stage3_momentum_factor import calculate_momentum


class MomentumFactorTest(unittest.TestCase):
    def test_calculates_20_record_momentum_within_each_stock(self):
        dates = pd.bdate_range("2026-01-05", periods=21)
        rising = pd.DataFrame(
            {
                "date": dates,
                "code": "000001",
                "adjusted_close": [100 + offset for offset in range(21)],
            }
        )
        falling = pd.DataFrame(
            {
                "date": dates,
                "code": "000002",
                "adjusted_close": [100 - offset for offset in range(21)],
            }
        )
        unsorted = pd.concat(
            [falling.iloc[::-1], rising.iloc[::-1]], ignore_index=True
        )

        result = calculate_momentum(unsorted, periods=20)

        rising_result = result.loc[result["code"] == "000001"]
        falling_result = result.loc[result["code"] == "000002"]
        self.assertTrue(rising_result["momentum_20d"].iloc[:20].isna().all())
        self.assertTrue(falling_result["momentum_20d"].iloc[:20].isna().all())
        self.assertAlmostEqual(rising_result["momentum_20d"].iloc[20], 0.20)
        self.assertAlmostEqual(falling_result["momentum_20d"].iloc[20], -0.20)


if __name__ == "__main__":
    unittest.main()
