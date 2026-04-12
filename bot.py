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
async def auto_check_topups():
    while True:
        try:
            orders = get_topup_orders(status="pending", limit=50)
            txs = await get_usdt_in_transactions(PAYMENT_ADDRESS)
            parsed = [p for p in (parse_usdt_tx(tx) for tx in txs) if p]

            for order_id, user_id, amount, status, created_at in orders:
                amount = float(amount)

                for tx in parsed:
                    txid = tx.get("txid")
                    if not txid:
                        continue

                    if (
                        tx.get("to") == PAYMENT_ADDRESS
                        and abs(float(tx.get("amount", 0)) - amount) < AUTO_PAY_TOLERANCE
                    ):
                        if not claim_topup_tx(txid, order_id):
                            continue

                        _row, err = approve_topup_order(order_id)
                        if err:
                            continue

                        try:
                            await bot.send_message(
                                user_id,
                                f"✅ 充值到账\n💰 {fmt_num(amount)} USDT 已入账"
                            )
                        except Exception:
                            pass

                        print("TOPUP AUTO PAID:", order_id, txid)
                        break

        except Exception as e:
            print("TOPUP AUTO CHECK ERROR:", e)
            traceback.print_exc()

        await asyncio.sleep(AUTO_PAY_INTERVAL)
@dp.callback_query(lambda c: c.data == "menu:topup")
async def menu_topup(c: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="10 USDT", callback_data="topup:create:10"),
            InlineKeyboardButton(text="50 USDT", callback_data="topup:create:50"),
            InlineKeyboardButton(text="100 USDT", callback_data="topup:create:100"),
        ],
        [
            InlineKeyboardButton(text="200 USDT", callback_data="topup:create:200"),
            InlineKeyboardButton(text="500 USDT", callback_data="topup:create:500"),
            InlineKeyboardButton(text="1000 USDT", callback_data="topup:create:1000"),
        ],
    ])
    await c.message.answer("请选择充值金额：", reply_markup=kb)
    await c.answer()


@dp.callback_query(lambda c: c.data and c.data.startswith("topup:create:"))
async def create_topup_cb(c: types.CallbackQuery):
    amount = float(c.data.split(":")[2])
    order_id = create_topup_order(c.from_user.id, amount)
    await c.message.answer(
        f"✅ 充值订单已创建\n"
        f"订单号: <code>{order_id}</code>\n"
        f"金额: <b>{amount} USDT</b>\n"
        f"地址: <code>{PAYMENT_ADDRESS}</code>",
        parse_mode="HTML",
    )
    await c.answer()

if __name__ == "__main__":
    asyncio.run(main())
