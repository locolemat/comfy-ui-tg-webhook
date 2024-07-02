from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from configuration.localisation import LanguageModel, language

from keyboards import generation_keyboard, choose_model_keyboard, confirm_model_keyboard

from model import create_session

from users import User

router = Router()

model_description_localisation = {
    "anithing_v11Pruned.safetensors": language.model_anithing_desc,
    "dreamshaper_8.safetensors": language.model_dreamshaper_desc,
    "epicrealism_naturalSinRC1VAE.safetensors": language.model_epicrealism_desc,
    "photon_v1.safetensors": language.model_photon_desc,
    "realvisxlV40_v40LightningBakedvae.safetensors": language.model_realvisxl_desc
}


@router.message(Command('generate'), StateFilter(None))
async def begin_generation_command(message: Message, state: FSMContext):
    await message.delete()

    await message.answer(
        text=language.generate_begin_msg,
        reply_markup=generation_keyboard()
    )

@router.callback_query(F.data=="generate", StateFilter(None))
async def begin_generation(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    await call.message.answer(
        text=language.generate_begin_msg,
        reply_markup=generation_keyboard()
    )


@router.message(Command('model'), StateFilter(None))
async def choose_model_command(message: Message, state: FSMContext):
    await message.delete()

    await message.answer(
        text=language.model_choice_desc,
        reply_markup=choose_model_keyboard()
    )

@router.callback_query(F.data=="choose_model", StateFilter(None))
async def choose_model(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    await call.message.answer(
        text=language.model_choice_desc,
        reply_markup=choose_model_keyboard()
    )


@router.callback_query(F.data.startswith('model:'), StateFilter(None))
async def display_model_details(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    model_name = call.data.split(':')[-1]

    description_text = model_description_localisation.get(model_name)

    await call.message.answer(
        text = description_text,
        reply_markup=confirm_model_keyboard(model_name=model_name)
    )


@router.callback_query(F.data.startswith('confirm_model:'), StateFilter(None))
async def confirm_model_choice_message(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    model_name = call.data.split(':')[-1]

    tgid = call.message.chat.id

    session = create_session()
    user = User.return_user_if_exists(tgid=tgid, session=session)

    user.preferred_model = model_name
    session.commit()
    session.close()


    await call.message.answer(
        text=LanguageModel.with_context(template=language.model_confirmed_msg, context={"model":model_name}),
    )
    
