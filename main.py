import asyncio
import logging
import argparse
import os

from config import BOT_TOKEN

from aiogram import Bot, Dispatcher
from handlers import questions, admin_func

if os.path.exists("tmp.log"):
    os.remove("tmp.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='tmp.log'
)


# TODO: admin list, admin functional(making news from admins, showing errors and logging info)
# TODO: debug functional

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(questions.router, admin_func.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Hello, World!")
    asyncio.run(main())
