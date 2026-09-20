import importlib
import unittest


def load_functions():
    try:
        module = importlib.import_module("lessons.stage4_transaction_costs")
    except ModuleNotFoundError:
        return None, None
    return module.calculate_commission, module.calculate_trade_cash_flow


class TransactionCostsTest(unittest.TestCase):
    def test_applies_minimum_commission_to_actual_transaction_amount(self):
        calculate_commission, _ = load_functions()
        self.assertIsNotNone(calculate_commission, "交易成本教学脚本尚未实现")

        self.assertEqual(calculate_commission(10_000, rate=0.0003, minimum=5), 5)
        self.assertEqual(calculate_commission(20_000, rate=0.0003, minimum=5), 6)
        self.assertEqual(calculate_commission(0, rate=0.0003, minimum=5), 0)

    def test_embeds_slippage_in_price_and_applies_stamp_tax_only_to_sell(self):
        _, calculate = load_functions()
        self.assertIsNotNone(calculate, "交易现金流教学函数尚未实现")

        buy = calculate(
            "buy", 1000, 10.0, commission_rate=0.0,
            minimum_commission=0.0, stamp_tax_rate=0.0005,
            slippage_rate=0.001,
        )
        sell = calculate(
            "sell", 1000, 10.0, commission_rate=0.0,
            minimum_commission=0.0, stamp_tax_rate=0.0005,
            slippage_rate=0.001,
        )

        self.assertAlmostEqual(buy["execution_price"], 10.01)
        self.assertEqual(buy["stamp_tax"], 0.0)
        self.assertAlmostEqual(buy["cash_change"], -10_010.0)
        self.assertAlmostEqual(sell["execution_price"], 9.99)
        self.assertAlmostEqual(sell["stamp_tax"], 4.995)
        self.assertAlmostEqual(sell["cash_change"], 9_985.005)

    def test_uses_the_stamp_tax_rate_supplied_for_each_trade_date(self):
        _, calculate = load_functions()
        self.assertIsNotNone(calculate, "交易现金流教学函数尚未实现")

        old_rate = calculate("sell", 2000, 10.0, stamp_tax_rate=0.001)
        current_rate = calculate("sell", 2000, 10.0, stamp_tax_rate=0.0005)

        self.assertAlmostEqual(old_rate["stamp_tax"], 20.0)
        self.assertAlmostEqual(current_rate["stamp_tax"], 10.0)


if __name__ == "__main__":
    unittest.main()
