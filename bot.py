import asyncio
from aiogram import Bot, Dispatcher

from token_reader import settings
from handlers import generation, user_settings

bot = Bot(token=settings.bot_token.get_secret_value())

async def main():
    
    dp = Dispatcher()
    dp.include_router(generation.router)
    dp.include_router(user_settings.router)

    await bot.delete_webhook(drop_pending_updates=True)
    # await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())