import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from db import init_db, seed_sample_data
from handlers import start, shop, profile, orders, wallet

async def main():
    init_db()
    seed_sample_data()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(link_preview_is_disabled=True),
    )
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(shop.router)
    dp.include_router(profile.router)
    dp.include_router(orders.router)
    dp.include_router(wallet.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
