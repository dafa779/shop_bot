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

