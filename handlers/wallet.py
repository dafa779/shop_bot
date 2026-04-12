from aiogram import Router, types, F

router = Router()

@router.callback_query(F.data == "menu:topup")
async def menu_topup(c: types.CallbackQuery):
    await c.message.answer(
        "💰 Please select the top-up amount:\n\n"
        "10 / 50 / 100 / 200 / 500 / 1000 USDT"
    )
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
        "We only keep your purchase records; files are automatically removed from stock after delivery."
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

