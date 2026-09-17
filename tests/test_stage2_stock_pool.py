import unittest

from lessons.stage2_stock_pool import build_stock_pool


class StockPoolTest(unittest.TestCase):
    def test_only_stocks_meeting_all_rules_enter_pool(self):
        rows = [
            {"code": "600001", "is_listed": True, "is_suspended": False, "is_risk_warning": False, "has_enough_history": True},
            {"code": "000002", "is_listed": True, "is_suspended": True, "is_risk_warning": False, "has_enough_history": True},
            {"code": "300003", "is_listed": True, "is_suspended": False, "is_risk_warning": True, "has_enough_history": True},
            {"code": "688004", "is_listed": False, "is_suspended": False, "is_risk_warning": False, "has_enough_history": False},
            {"code": "600005", "is_listed": True, "is_suspended": False, "is_risk_warning": False, "has_enough_history": False},
        ]

        result = build_stock_pool(rows)

        self.assertEqual(result.loc[result["in_pool"], "code"].tolist(), ["600001"])
        self.assertEqual(
            result["exclusion_reason"].tolist(),
            ["eligible", "suspended", "risk_warning", "not_listed", "insufficient_history"],
        )


if __name__ == "__main__":
    unittest.main()
