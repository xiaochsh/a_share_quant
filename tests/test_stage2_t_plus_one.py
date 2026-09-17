import unittest

from lessons.stage2_t_plus_one import simulate_t_plus_one


class TPlusOneTest(unittest.TestCase):
    def test_today_buy_becomes_sellable_next_trading_day(self):
        events = [
            {"date": "2026-09-18", "action": "buy", "requested_shares": 100},
            {"date": "2026-09-18", "action": "sell", "requested_shares": 100},
            {"date": "2026-09-21", "action": "sell", "requested_shares": 100},
        ]

        result = simulate_t_plus_one(events)

        self.assertEqual(result["executed_shares"].tolist(), [100, 0, 100])
        self.assertEqual(result["total_shares_after"].tolist(), [100, 100, 0])
        self.assertEqual(result["sellable_shares_after"].tolist(), [0, 0, 0])
        self.assertEqual(
            result["status"].tolist(),
            ["buy_filled", "blocked_t_plus_one", "sell_filled"],
        )


if __name__ == "__main__":
    unittest.main()
