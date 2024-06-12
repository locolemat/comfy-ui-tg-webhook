from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from configuration.localisation import LanguageModel, language
from keyboards.keyboards import greeting_keyboard

router = Router()

@router.message(CommandStart())
async def greeting_reply(message: Message):
    await message.answer(
        text=LanguageModel.with_context(template=language.greeting, context={"username":message.from_user.first_name,"tokens":10}),
        reply_markup=greeting_keyboard()
    )