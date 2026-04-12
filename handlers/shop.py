from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from db import get_categories, get_products_by_category, get_product, create_order
from keyboards.shop import categories_kb, products_kb, product_action_kb
from keyboards.main import main_menu_kb
from states import ShopFSM

router = Router()

@router.callback_query(F.data == "menu:home")
async def menu_home(c: types.CallbackQuery):
    await c.message.answer("🏠 Main Menu", reply_markup=main_menu_kb())
    await c.answer()

@router.callback_query(F.data == "menu:shop")
async def menu_shop(c: types.CallbackQuery):
    rows = get_categories()
    await c.message.answer("🛒 请选择分类：", reply_markup=categories_kb(rows))
    await c.answer()

@router.callback_query(F.data.startswith("shop:cat:"))
async def shop_category(c: types.CallbackQuery):
    category_id = int(c.data.split(":")[2])
    rows = get_products_by_category(category_id)
    await c.message.answer("📦 请选择商品：", reply_markup=products_kb(rows))
    await c.answer()

@router.callback_query(F.data.startswith("shop:product:"))
async def shop_product(c: types.CallbackQuery):
    product_id = int(c.data.split(":")[2])
    row = get_product(product_id)
    if not row:
        return await c.answer("商品不存在", show_alert=True)

    _, _, title, price, stock, description = row
    text = (
        f"✅ You are purchasing: <b>{title}</b>\n\n"
        f"💰 Price: <b>{price:.2f} USDT</b>\n"
        f"📦 Stock: <b>{stock}</b>\n\n"
        f"⚠️ {description or 'Please test with small quantity first.'}"
    )
    await c.message.answer(text, parse_mode="HTML", reply_markup=product_action_kb(product_id))
    await c.answer()

@router.callback_query(F.data.startswith("shop:buy:"))
async def shop_buy(c: types.CallbackQuery, state: FSMContext):
    product_id = int(c.data.split(":")[2])
    await state.set_state(ShopFSM.waiting_quantity)
    await state.update_data(product_id=product_id)
    await c.message.answer("🛒 Please enter the quantity to purchase, e.g.: 10")
    await c.answer()

@router.message(ShopFSM.waiting_quantity)
async def shop_quantity(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        return await message.answer("❌ Please enter a valid number")

    qty = int(message.text)
    data = await state.get_data()
    product_id = data["product_id"]
    row = get_product(product_id)
    if not row:
        await state.clear()
        return await message.answer("❌ 商品不存在")

    _, _, title, price, stock, _ = row
    if qty <= 0 or qty > stock:
        return await message.answer("❌ Quantity exceeds stock")

    order_id = create_order(message.from_user.id, product_id, qty, price * qty)
    await state.clear()
    await message.answer(
        f"✅ Order created\n"
        f"Order ID: <code>{order_id}</code>\n"
        f"Product: <b>{title}</b>\n"
        f"Quantity: <b>{qty}</b>\n"
        f"Amount: <b>{price * qty:.2f} USDT</b>",
        parse_mode="HTML",
    )

