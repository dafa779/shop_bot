from aiogram import Router, types, F
from db import get_user_orders

router = Router()

@router.callback_query(F.data == "menu:orders")
async def menu_orders(c: types.CallbackQuery):
    rows = get_user_orders(c.from_user.id)
    if not rows:
        await c.message.answer("📦 暂无订单")
        return await c.answer()

    lines = ["📦 订单记录", ""]
    for order_id, title, qty, amount, status, created_at in rows[:20]:
        lines.append(
            f"• #{order_id} | {title or '-'}\n"
            f"  Qty: {qty} | {amount:.2f} USDT | {status}"
        )
    await c.message.answer("\n".join(lines))
    await c.answer()

