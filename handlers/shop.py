from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from keyboards.shop import categories_kb, products_kb, product_action_kb
from keyboards.main import main_menu_kb
from services.shop_service import (
    fetch_categories,
    fetch_products_by_category,
    fetch_product,
    build_product_text,
    validate_quantity,
    create_product_order,
    build_order_success_text,
)
from states import ShopFSM

router = Router()


@router.callback_query(F.data == "menu:home")
async def menu_home(c: types.CallbackQuery):
    await c.message.answer("🏠 Main Menu", reply_markup=main_menu_kb())
    await c.answer()


@router.callback_query(F.data == "menu:shop")
async def menu_shop(c: types.CallbackQuery):
    rows = fetch_categories()

    if not rows:
        await c.message.answer("❌ No categories available")
        await c.answer()
        return

    await c.message.answer(
        "🛒 请选择分类：",
        reply_markup=categories_kb(rows)
    )
    await c.answer()


@router.callback_query(F.data.startswith("shop:cat:"))
async def shop_category(c: types.CallbackQuery):
    try:
        category_id = int(c.data.split(":")[2])
    except (IndexError, ValueError):
        await c.answer("❌ Invalid category", show_alert=True)
        return

    rows = fetch_products_by_category(category_id)

    if not rows:
        await c.message.answer("❌ No products found in this category")
        await c.answer()
        return

    await c.message.answer(
        "📦 请选择商品：",
        reply_markup=products_kb(rows)
    )
    await c.answer()


@router.callback_query(F.data.startswith("shop:product:"))
async def shop_product(c: types.CallbackQuery):
    try:
        product_id = int(c.data.split(":")[2])
    except (IndexError, ValueError):
        await c.answer("❌ Invalid product", show_alert=True)
        return

    product = fetch_product(product_id)
    if not product:
        await c.answer("商品不存在", show_alert=True)
        return

    await c.message.answer(
        build_product_text(product),
        parse_mode="HTML",
        reply_markup=product_action_kb(product_id)
    )
    await c.answer()


@router.callback_query(F.data.startswith("shop:buy:"))
async def shop_buy(c: types.CallbackQuery, state: FSMContext):
    try:
        product_id = int(c.data.split(":")[2])
    except (IndexError, ValueError):
        await c.answer("❌ Invalid product", show_alert=True)
        return

    product = fetch_product(product_id)
    if not product:
        await c.answer("商品不存在", show_alert=True)
        return

    await state.set_state(ShopFSM.waiting_quantity)
    await state.update_data(product_id=product_id)

    await c.message.answer("🛒 Please enter the quantity to purchase, e.g.: 10")
    await c.answer()


@router.message(ShopFSM.waiting_quantity)
async def shop_quantity(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❌ Please enter a valid number")
        return

    qty = int(message.text)

    data = await state.get_data()
    product_id = data.get("product_id")

    if not product_id:
        await state.clear()
        await message.answer("❌ Session expired, please try again")
        return

    product = fetch_product(product_id)
    if not product:
        await state.clear()
        await message.answer("❌ 商品不存在")
        return

    ok, error_text = validate_quantity(product, qty)
    if not ok:
        await message.answer(error_text)
        return

    order = create_product_order(message.from_user.id, product, qty)

    await state.clear()
    await message.answer(
        build_order_success_text(order),
        parse_mode="HTML"
    )
