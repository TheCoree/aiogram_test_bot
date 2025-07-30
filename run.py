import asyncio
import logging

from config import settings
from aiogram import Bot, Dispatcher

from app.database.models import async_main
from app.handlers import router

async def main():
    await async_main()
    bot = Bot(token=settings.bot_token)
    dp =  Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Ctrl+C pressed')