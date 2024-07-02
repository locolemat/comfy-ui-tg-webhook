from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from configuration.localisation import LanguageModel, language

from keyboards import greeting_keyboard

from model import create_session

from user import User
from states import states

router = Router()

@router.message(F.text, CommandStart())
async def greeting_reply(message: Message, state: FSMContext):
    await state.clear()
    
    tgid = message.from_user.id

    session = create_session()

    user = User.check_if_user_exists(tgid=tgid)

    if user is None:
        username = message.from_user.first_name
        balance = 10
        user = User(username=username, tgid=tgid, balance=balance)
        session.add(user)
        session.commit()

    else:
        username = user.username
        balance = user.balance

    session.close()

    await message.answer(
        text=LanguageModel.with_context(template=language.greeting, context={"username":username,"tokens":balance}),
        reply_markup=greeting_keyboard()
    )