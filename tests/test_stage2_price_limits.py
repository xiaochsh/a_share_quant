import unittest

from lessons.stage2_price_limits import simulate_position


class PriceLimitTest(unittest.TestCase):
    def test_limit_price_does_not_by_itself_determine_fill(self):
        rows = [
            {
                "price_state": "normal",
                "has_opposing_liquidity": True,
                "target_position": 0,
            },
            {
                "price_state": "limit_up",
                "has_opposing_liquidity": False,
                "target_position": 1,
            },
            {
                "price_state": "limit_up",
                "has_opposing_liquidity": True,
                "target_position": 1,
            },
            {
                "price_state": "limit_down",
                "has_opposing_liquidity": False,
                "target_position": 0,
            },
            {
                "price_state": "limit_down",
                "has_opposing_liquidity": True,
                "target_position": 0,
            },
        ]

        result = simulate_position(rows)

        self.assertEqual(result["position_before"].tolist(), [0, 0, 0, 1, 1])
        self.assertEqual(result["trade"].tolist(), [0, 0, 1, 0, -1])
        self.assertEqual(result["position_after"].tolist(), [0, 0, 1, 1, 0])
        self.assertEqual(
            result["fill_status"].tolist(),
            [
                "no_trade_needed",
                "blocked_no_seller",
                "filled",
                "blocked_no_buyer",
                "filled",
            ],
        )


if __name__ == "__main__":
    unittest.main()
