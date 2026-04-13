from db import (
    get_categories,
    get_products_by_category,
    get_product,
    purchase_product,
)


def fetch_categories():
    return get_categories()


def fetch_products_by_category(category_id: int):
    return get_products_by_category(category_id)


def fetch_product(product_id: int):
    row = get_product(product_id)
    if not row:
        return None

    product_id, category_id, title, price, stock, description = row
    return {
        "id": product_id,
        "category_id": category_id,
        "title": title,
        "price": float(price),
        "stock": int(stock),
        "description": description or "",
    }


def build_product_text(product: dict) -> str:
    return (
        f"✅ You are purchasing: <b>{product['title']}</b>\n\n"
        f"💰 Price: <b>{product['price']:.2f} USDT</b>\n"
        f"📦 Stock: <b>{product['stock']}</b>\n\n"
        f"⚠️ {product['description'] or 'Please test with small quantity first.'}"
    )


def validate_quantity_text(text: str):
    if not text or not text.isdigit():
        return None, "❌ Please enter a valid number"

    qty = int(text)
    if qty <= 0:
        return None, "❌ Quantity must be greater than 0"

    return qty, None


def create_product_order(user_id: int, product_id: int, qty: int):
    return purchase_product(user_id, product_id, qty)


def build_order_success_text(order: dict) -> str:
    return (
        f"✅ Order created\n"
        f"Order ID: <code>{order['order_id']}</code>\n"
        f"Product: <b>{order['title']}</b>\n"
        f"Quantity: <b>{order['qty']}</b>\n"
        f"Amount: <b>{order['amount']:.2f} USDT</b>\n"
        f"Status: <b>{order['status']}</b>"
    )
