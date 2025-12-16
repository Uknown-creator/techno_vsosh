import asyncio
import logging
from os import remove, path

from config import BOT_TOKEN

from aiogram import Bot, Dispatcher
from handlers import admin_func, materials_selecting, authorization, materials_posting

if path.exists("tmp.log"):
    remove("tmp.log")
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='tmp.log'
)


async def main():
    """
    Docstring for main
    """
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    dp.include_routers(admin_func.router, materials_selecting.router, materials_posting.router, authorization.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Hello, World!")
    asyncio.run(main())
