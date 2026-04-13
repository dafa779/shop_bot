from db import get_categories, get_products_by_category, get_product, create_order


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
        "price": price,
        "stock": stock,
        "description": description,
    }


def build_product_text(product: dict) -> str:
    return (
        f"✅ You are purchasing: <b>{product['title']}</b>\n\n"
        f"💰 Price: <b>{product['price']:.2f} USDT</b>\n"
        f"📦 Stock: <b>{product['stock']}</b>\n\n"
        f"⚠️ {product['description'] or 'Please test with small quantity first.'}"
    )


def validate_quantity(product: dict, qty: int):
    if qty <= 0:
        return False, "❌ Quantity must be greater than 0"

    if qty > product["stock"]:
        return False, "❌ Quantity exceeds stock"

    return True, None


def create_product_order(user_id: int, product: dict, qty: int):
    total_amount = product["price"] * qty
    order_id = create_order(user_id, product["id"], qty, total_amount)

    return {
        "order_id": order_id,
        "title": product["title"],
        "qty": qty,
        "amount": total_amount,
    }


def build_order_success_text(order: dict) -> str:
    return (
        f"✅ Order created\n"
        f"Order ID: <code>{order['order_id']}</code>\n"
        f"Product: <b>{order['title']}</b>\n"
        f"Quantity: <b>{order['qty']}</b>\n"
        f"Amount: <b>{order['amount']:.2f} USDT</b>"
    )
