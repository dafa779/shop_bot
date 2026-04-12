from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from keyboards.wallet import topup_amounts_kb
from states import WalletFSM
from db import create_topup_order, get_user, get_user_topup_orders

router = Router()

PAYMENT_ADDRESS = "TSPpLmYuFXLi6GU1W4uyG6NKGbdWPw886U"


@router.callback_query(F.data == "menu:topup")
async def menu_topup(c: types.CallbackQuery):
    row = get_user(c.from_user.id)
    balance = row[3] if row else 0

    text = (
        f"👋 Good Morning\n\n"
        f"🏦 Account Balance: {balance:.2f}\n"
        f"Please select the top-up amount:"
    )
    await c.message.answer(text, reply_markup=topup_amounts_kb())
    await c.answer()


@router.callback_query(F.data.startswith("topup:"))
async def topup_select(c: types.CallbackQuery, state: FSMContext):
    value = c.data.split(":")[1]

    if value == "custom":
        await state.set_state(WalletFSM.waiting_custom_amount)
        await c.message.answer("💰 Please enter custom amount in USDT:")
        return await c.answer()

    amount = float(value)
    order_id = create_topup_order(c.from_user.id, amount)

    await c.message.answer(
        f"✅ Top-up order created\n"
        f"Order ID: <code>{order_id}</code>\n"
        f"Amount: <b>{amount:.2f} USDT</b>\n"
        f"Address: <code>{PAYMENT_ADDRESS}</code>",
        parse_mode="HTML",
    )
    await c.answer()


@router.message(WalletFSM.waiting_custom_amount)
async def topup_custom_amount(message: types.Message, state: FSMContext):
    try:
        amount = float((message.text or "").strip())
    except Exception:
        return await message.answer("❌ Invalid amount")

    if amount <= 0:
        return await message.answer("❌ Amount must be greater than 0")

    order_id = create_topup_order(message.from_user.id, amount)
    await state.clear()

    await message.answer(
        f"✅ Top-up order created\n"
        f"Order ID: <code>{order_id}</code>\n"
        f"Amount: <b>{amount:.2f} USDT</b>\n"
        f"Address: <code>{PAYMENT_ADDRESS}</code>",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "menu:orders")
async def menu_orders(c: types.CallbackQuery):
    rows = get_user_topup_orders(c.from_user.id)

    if not rows:
        await c.message.answer("📦 暂无充值订单")
        return await c.answer()

    lines = ["📦 Top-up Orders", ""]

    for order_id, amount, status, created_at in rows[:20]:
        lines.append(
            f"• #{order_id} | {amount:.2f} USDT | {status}"
        )

    await c.message.answer("\n".join(lines))
    await c.answer()


@router.callback_query(F.data == "menu:energy")
async def menu_energy(c: types.CallbackQuery):
    await c.message.answer("⚡ Energy Rental coming soon")
    await c.answer()


@router.callback_query(F.data == "menu:lang")
async def menu_lang(c: types.CallbackQuery):
    await c.message.answer("🌐 Language setting coming soon")
    await c.answer()


@router.callback_query(F.data == "menu:support")
async def menu_support(c: types.CallbackQuery):
    await c.message.answer("👨‍💻 联系客服: @support")
    await c.answer()


@router.callback_query(F.data == "menu:notice")
async def menu_notice(c: types.CallbackQuery):
    await c.message.answer(
        "NOTE:\n"
        "Please keep the account files you receive safe.\n"
        "We only keep your purchase records; the account files are automatically deleted from stock after delivery."
    )
    await c.answer()


@router.callback_query(F.data == "menu:vip")
async def menu_vip(c: types.CallbackQuery):
    await c.message.answer(
        "💎 Telegram Premium\n\n"
        "请选择操作：\n"
        "1. 为此账号开通\n"
        "2. 赠送他人会员\n"
        "3. 余额充值"
    )
    await c.answer()
