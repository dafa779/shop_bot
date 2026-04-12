import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from db import init_db, seed_sample_data
from handlers import start, shop, profile, orders, wallet
    get_topup_orders,
    approve_topup_order,
    mark_topup_order_rejected,
    claim_topup_tx,
    create_topup_order,
    get_user_topup_orders,

def topup_admin_kb(order_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ 确认到账", callback_data=f"topup:approve:{order_id}"),
            InlineKeyboardButton(text="❌ 拒绝", callback_data=f"topup:reject:{order_id}"),
        ]
    ])

async def main():
    init_db()
    seed_sample_data()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(link_preview_is_disabled=True),
    )
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(shop.router)
    dp.include_router(profile.router)
    dp.include_router(orders.router)
    dp.include_router(wallet.router)

    await dp.start_polling(bot)
@dp.message(lambda m: m.text in ("充值订单", "topup orders"))
async def topup_orders_cmd(m: types.Message):
    if not can_use_manage_panel(m.from_user.id):
        return await m.reply("❌ 无权限")

    rows = get_topup_orders(status="pending", limit=20)
    if not rows:
        return await m.reply("暂无待处理充值订单")

    for order_id, user_id, amount, status, created_at in rows:
        await m.reply(
            f"💰 充值订单\n"
            f"订单号: <code>{order_id}</code>\n"
            f"用户: <code>{user_id}</code>\n"
            f"金额: <b>{amount} USDT</b>\n"
            f"状态: {status}\n"
            f"时间: {fmt_ts(created_at)}",
            parse_mode="HTML",
            reply_markup=topup_admin_kb(order_id),
        )


@dp.callback_query(lambda c: c.data and c.data.startswith("topup:approve:"))
async def topup_approve_cb(c: types.CallbackQuery):
    if not c.from_user or not can_use_manage_panel(c.from_user.id):
        return await c.answer("无权限", show_alert=True)

    order_id = int(c.data.split(":")[2])
    row, err = approve_topup_order(order_id)
    if err:
        return await c.answer(err, show_alert=True)

    await c.message.answer(f"✅ 充值订单 {order_id} 已确认到账")
    await c.answer("已到账")


@dp.callback_query(lambda c: c.data and c.data.startswith("topup:reject:"))
async def topup_reject_cb(c: types.CallbackQuery):
    if not c.from_user or not can_use_manage_panel(c.from_user.id):
        return await c.answer("无权限", show_alert=True)

    order_id = int(c.data.split(":")[2])
    mark_topup_order_rejected(order_id)
    await c.message.answer(f"❌ 充值订单 {order_id} 已拒绝")
    await c.answer("已拒绝")

if __name__ == "__main__":
    asyncio.run(main())
