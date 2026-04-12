from aiogram import Router, types
from aiogram.filters import CommandStart
from db import upsert_user, get_user
from keyboards.main import main_menu_kb

router = Router()

BANNER = "https://dummyimage.com/900x300/6d28d9/ffffff&text=TGRRBot"

@router.message(CommandStart())
async def start_cmd(message: types.Message):
    upsert_user(
        user_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name or "",
    )
    row = get_user(message.from_user.id)
    _, username, full_name, balance, created_at = row

    caption = (
        f"👋 Good Morning, <b>{full_name or 'User'}</b>\n"
        f"👤 ID: <code>{message.from_user.id}</code>\n\n"
        f"🏦 USDT: <b>{balance:.2f}</b>\n"
        f"💸 Total Spent: <b>0.00</b>\n"
        f"✅ Total Purchased: <b>0</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 订单通知群组: @TGtttc"
    )
    await message.answer_photo(BANNER, caption=caption, parse_mode="HTML", reply_markup=main_menu_kb())
