"""第四阶段：计算佣金、印花税、滑点和交易现金流。

费率均为教学参数，不连接真实券商，也不代表任何账户的实际收费。
"""

from pathlib import Path

import pandas as pd


def calculate_commission(
    transaction_amount: float,
    rate: float = 0.0003,
    minimum: float = 5.0,
) -> float:
    """按实际成交金额计算佣金；未成交时不收最低佣金。"""
    if transaction_amount <= 0:
        return 0.0
    return round(max(transaction_amount * rate, minimum), 2)


def calculate_trade_cash_flow(
    side: str,
    quantity: float,
    reference_price: float,
    commission_rate: float = 0.0003,
    minimum_commission: float = 5.0,
    stamp_tax_rate: float = 0.0005,
    slippage_rate: float = 0.0,
) -> dict[str, float | str]:
    """把滑点放入成交价，再按成交金额计算费用和现金变化。"""
    normalized_side = side.lower()
    if normalized_side not in {"buy", "sell"}:
        raise ValueError("side 必须是 'buy' 或 'sell'")
    if quantity < 0 or reference_price < 0:
        raise ValueError("quantity 和 reference_price 不能为负数")

    direction = 1 if normalized_side == "buy" else -1
    execution_price = reference_price * (1 + direction * slippage_rate)
    transaction_amount = quantity * execution_price
    commission = calculate_commission(
        transaction_amount, commission_rate, minimum_commission
    )
    stamp_tax = (
        transaction_amount * stamp_tax_rate
        if normalized_side == "sell"
        else 0.0
    )
    if normalized_side == "buy":
        cash_change = -(transaction_amount + commission + stamp_tax)
    else:
        cash_change = transaction_amount - commission - stamp_tax

    return {
        "side": normalized_side,
        "quantity": quantity,
        "reference_price": reference_price,
        "execution_price": execution_price,
        "transaction_amount": transaction_amount,
        "commission": commission,
        "stamp_tax": stamp_tax,
        "cash_change": cash_change,
    }


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    trades = [
        {
            "trade_date": "2026-03-09",
            **calculate_trade_cash_flow(
                "buy", 1000, 10.0, stamp_tax_rate=0.0005, slippage_rate=0.001
            ),
        },
        {
            "trade_date": "2026-03-20",
            **calculate_trade_cash_flow(
                "sell", 1000, 10.0, stamp_tax_rate=0.0005, slippage_rate=0.001
            ),
        },
    ]
    result = pd.DataFrame(trades)
    print(result.to_string(index=False))

    output = root / "result/stage4_transaction_costs.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False, date_format="%Y-%m-%d")
    print("\n结果已保存：", output)


if __name__ == "__main__":
    main()
