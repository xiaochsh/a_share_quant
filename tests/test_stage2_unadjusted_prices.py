import unittest

from lessons.stage2_unadjusted_prices import analyze_unadjusted_prices


class UnadjustedPricesTest(unittest.TestCase):
    def test_ex_rights_price_drop_is_not_the_holding_return(self):
        rows = [
            {"date": "2026-09-14", "close": 19.50, "shares": 100},
            {"date": "2026-09-15", "close": 20.00, "shares": 100},
            {"date": "2026-09-16", "close": 10.10, "shares": 200},
        ]

        result = analyze_unadjusted_prices(rows)

        self.assertAlmostEqual(result.loc[2, "raw_price_return"], -0.495)
        self.assertEqual(result["position_value"].tolist(), [1950.0, 2000.0, 2020.0])
        self.assertAlmostEqual(result.loc[2, "holding_value_return"], 0.01)


if __name__ == "__main__":
    unittest.main()
