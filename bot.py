import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from token_reader import settings
from handlers import generation, user_settings

from configuration.localisation import language

bot = Bot(token=settings.bot_token.get_secret_value())

async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/start", description=language.start_command_desc),
        BotCommand(command="/model", description=language.model_command_desc),
        BotCommand(command="/generate", description=language.generate_command_desc),
    ]

    await bot.set_my_commands(bot_commands)

async def main():
    
    dp = Dispatcher()
    dp.include_router(generation.router)
    dp.include_router(user_settings.router)

    dp.startup.register(setup_bot_commands)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())