from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from configuration.localisation import LanguageModel, language

from keyboards import generation_keyboard, greeting_keyboard, choose_model_keyboard

from model import create_session

from users import User
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
        preferred_model = "anithing_v11Pruned.safetensors"
        user = User(username=username, tgid=tgid, balance=balance, preferred_model=preferred_model)
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


@router.callback_query(Command('generate'), StateFilter(None))
@router.callback_query(F.data=="generate", StateFilter(None))
async def begin_generation(call: CallbackQuery, state: FSMContext):

    await call.message.answer(
        text=language.generate_begin_msg,
        reply_markup=generation_keyboard()
    )


@router.callback_query(Command('model'), StateFilter(None))
@router.callback_query(F.data=="choose_model", StateFilter(None))
async def choose_model(call: CallbackQuery, state: FSMContext):

    await call.message.answer(
        text=language.model_choice_desc,
        reply_markup=choose_model_keyboard()
    )