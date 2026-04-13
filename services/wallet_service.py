from db import create_topup_order, get_user, get_user_topup_orders


def get_user_balance(user_id: int) -> float:
    row = get_user(user_id)
    if not row:
        return 0.0
    return float(row[3] or 0)


def build_topup_menu_text(user_id: int) -> str:
    balance = get_user_balance(user_id)
    return (
        f"👋 Good Morning\n\n"
        f"🏦 Account Balance: {balance:.2f} USDT\n"
        f"Please select the top-up amount:"
    )


def validate_custom_amount(text: str):
    try:
        amount = float((text or "").strip())
    except Exception:
        return None, "❌ Invalid amount"

    if amount <= 0:
        return None, "❌ Amount must be greater than 0"

    return amount, None


def create_user_topup_order(user_id: int, amount: float) -> int:
    return create_topup_order(user_id, amount)


def build_topup_created_text(order_id: int, amount: float, payment_address: str) -> str:
    return (
        f"✅ Top-up order created\n"
        f"Order ID: <code>{order_id}</code>\n"
        f"Amount: <b>{amount:.2f} USDT</b>\n"
        f"Address: <code>{payment_address}</code>"
    )


def build_topup_orders_text(user_id: int) -> str:
    rows = get_user_topup_orders(user_id)

    if not rows:
        return "📦 暂无充值订单"

    lines = ["📦 Top-up Orders", ""]

    for order_id, amount, status, created_at in rows[:20]:
        lines.append(f"• #{order_id} | {amount:.2f} USDT | {status}")

    return "\n".join(lines)
