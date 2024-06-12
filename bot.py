import asyncio
from aiogram import Bot, Dispatcher
from token_reader import settings

async def main():
    bot = Bot(token=settings.bot_token.get_secret_value())
    dp = Dispatcher()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())