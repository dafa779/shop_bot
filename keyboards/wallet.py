from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def topup_amounts_kb():
    amounts = [10, 50, 100, 200, 500, 1000, 2000, 5000]
    rows = []
    row = []
    for amount in amounts:
        row.append(InlineKeyboardButton(text=f"{amount} USDT", callback_data=f"topup:{amount}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([
        InlineKeyboardButton(text="💰 Custom Amount", callback_data="topup:custom"),
        InlineKeyboardButton(text="↩️ Back", callback_data="menu:home"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

