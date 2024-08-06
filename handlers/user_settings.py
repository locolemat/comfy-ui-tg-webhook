from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from configuration.localisation import LanguageModel, language
from configuration.gallery import gallery
from configuration.gen_models import image_models, video_models

from keyboards import (generation_keyboard, 
                       choose_model_keyboard, 
                       confirm_model_keyboard,
                       choose_video_model_keyboard,
                       confirm_video_model_keyboard)

from model import create_session

from users import User

router = Router()


@router.message(Command('generate'), StateFilter(None))
async def begin_generation_command(message: Message, state: FSMContext):
    await message.delete()

    await message.answer(
        text=language.generate_begin_msg,
        reply_markup=generation_keyboard()
    )

@router.callback_query(F.data=="generate", StateFilter(None))
async def begin_generation(call: CallbackQuery, state: FSMContext):
    await call.message.bot.edit_message_text(
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        text=language.generate_begin_msg,
        reply_markup=generation_keyboard()
    )


@router.message(Command('model'), StateFilter(None))
async def choose_model_command(message: Message, state: FSMContext):
    await message.delete()

    tgid = message.chat.id

    session = create_session()
    user = User.return_user_if_exists(tgid=tgid, session=session)
    model = user.preferred_model
    session.close()

    await message.answer(
        text=LanguageModel.with_context(template=language.model_choice_desc, context={"model": image_models.get(model).name_text}),
        reply_markup=choose_model_keyboard()
    )


@router.callback_query(F.data=="choose_model", StateFilter(None))
async def choose_model(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    tgid = call.message.chat.id

    session = create_session()
    user = User.return_user_if_exists(tgid=tgid, session=session)
    model = user.preferred_model
    session.close()

    await call.message.answer(
        text=LanguageModel.with_context(template=language.model_choice_desc, context={"model": image_models.get(model).name_text}),
        reply_markup=choose_model_keyboard()
    )


@router.callback_query(F.data=="choose_video_model", StateFilter(None))
async def choose_video_model(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    tgid = call.message.chat.id
    
    session = create_session()
    user = User.return_user_if_exists(tgid=tgid, session=session)
    model = user.preferred_video_model
    session.close()

    await call.message.answer(
        text=LanguageModel.with_context(template=language.choose_video_model_desc, context={"model": video_models.get(model).name_text}),
        reply_markup=choose_video_model_keyboard()
    )


@router.callback_query(F.data.startswith('model:'), StateFilter(None))
async def display_model_details(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    model_name = call.data.split(':')[-1]

    model_gallery = gallery.mappings.get(image_models.get(model_name).name_text.lower())

    description_text = image_models.get(model_name).desc_text

    print(f'DEBUG DISPLAY MODEL: {model_name}, {model_gallery}')
    if model_gallery:
        await call.message.bot.send_photo(
            chat_id=call.message.chat.id,
            photo = model_gallery,
            caption = description_text,
            reply_markup=confirm_model_keyboard(model_name=model_name)
        )


@router.callback_query(F.data.startswith('v_model:'), StateFilter(None))
async def display_video_model_details(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    model_name = call.data.split(':')[-1]

    await call.message.answer(
        text=video_models.get(model_name).desc_text,
        reply_markup=confirm_video_model_keyboard(model_name=model_name)
    )


@router.callback_query(F.data.startswith('confirm_model:'), StateFilter(None))
async def confirm_model_choice_message(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    model_name = call.data.split(':')[-1]
    model_gallery = image_models[model_name].name_text.lower()

    tgid = call.message.chat.id

    session = create_session()
    user = User.return_user_if_exists(tgid=tgid, session=session)

    user.preferred_model = model_name
    session.commit()
    session.close()


    await call.message.answer(
        text=LanguageModel.with_context(template=language.model_confirmed_msg, context={"model":model_gallery}),
    )
    

@router.callback_query(F.data.startswith('confirm_v_model:'), StateFilter(None))
async def confirm_video_model_choice_message(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    model_name = call.data.split(':')[-1]
    model_gallery = video_models[model_name].name_text

    tgid = call.message.chat.id

    session = create_session()
    user = User.return_user_if_exists(tgid=tgid, session=session)

    user.preferred_video_model = model_name
    session.commit()
    session.close()


    await call.message.answer(
        text=LanguageModel.with_context(template=language.model_confirmed_msg, context={"model":model_gallery}),
    )
