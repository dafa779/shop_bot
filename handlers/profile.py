from aiogram import Router, types, F
from db import get_user

router = Router()


@router.callback_query(F.data == "menu:profile")
async def menu_profile(c: types.CallbackQuery):
    row = get_user(c.from_user.id)

    if not row:
        await c.message.answer("❌ User not found")
        await c.answer()
        return

    user_id, username, full_name, balance, created_at = row

    text = (
        f"👤 <b>Profile</b>\n\n"
        f"🆔 User ID: <code>{user_id}</code>\n"
        f"👤 Name: <b>{full_name or '-'}</b>\n"
        f"📛 Username: <b>@{username}</b>\n" if username else
        f"👤 <b>Profile</b>\n\n"
        f"🆔 User ID: <code>{user_id}</code>\n"
        f"👤 Name: <b>{full_name or '-'}</b>\n"
    )

    text += f"💰 Balance: <b>{float(balance or 0):.2f} USDT</b>"

    await c.message.answer(text, parse_mode="HTML")
    await c.answer()
