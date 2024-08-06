import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from token_reader import settings
from handlers import generation, user_settings

from configuration.localisation import language
from server_queue.server_queue import Queue

bot = Bot(token=settings.bot_token.get_secret_value(),
          default=DefaultBotProperties(
              parse_mode=ParseMode.HTML
          ))

async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/start", description=language.start_command_desc),
        BotCommand(command="/model", description=language.model_command_desc),
        BotCommand(command="/generate", description=language.generate_command_desc),
    ]

    await bot.set_my_commands(bot_commands)

async def main():
    print(f'The length of the Queue is currently {Queue.get_queue_length()}')
    Queue.add_new_queue_item(prompt='a', negative_prompt='a', workflow='a', dimensions='a', user_id='a')
    print(f'The length of the Queue is currently {Queue.get_queue_length()}')
    row = Queue.delete_queue_item(1)
    print(row)
    print(row.prompt)
    dp = Dispatcher()
    dp.include_router(generation.router)
    dp.include_router(user_settings.router)

    dp.startup.register(setup_bot_commands)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())