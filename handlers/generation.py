import os
import time

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from configuration.localisation import LanguageModel, language
from keyboards.keyboards import greeting_keyboard, dimensions_keyboard
from workflows.controller import WorkflowTextToVideo
from states import states
from utils import utils
from client import client

router = Router()

@router.message(F.text, StateFilter(None), CommandStart())
async def greeting_reply(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=LanguageModel.with_context(template=language.greeting, context={"username":message.from_user.first_name,"tokens":10}),
        reply_markup=greeting_keyboard()
    )

@router.callback_query(F.data.startswith(language.button_generate_text_video), StateFilter(None))
async def text_to_image_dimensions(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    await call.message.answer(
        text = language.generate_dimensions,
        reply_markup=dimensions_keyboard()
    )

    await state.set_state(states.TextToVideo.choose_dimensions)

@router.callback_query(F.data.startswith('d'), StateFilter(states.TextToVideo.choose_dimensions))
async def text_to_image_prompt(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = call.data.split("_")[-1]
    await state.update_data(dimensions=data)

    await call.message.answer(
        text = language.prompt_invitation
    )
    await state.set_state(states.TextToVideo.choose_prompt)

@router.message(F.text, StateFilter(states.TextToVideo.choose_prompt))
async def text_to_video_generation(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        text = LanguageModel.with_context(template=language.pre_generation_message,
                                          context={"action": language.button_generate_text_image,
                                                   "dimensions": data["dimensions"],
                                                   "prompt": message.text})
    )

    await message.answer(
        text = language.generation_began
    )

    id = utils.generate_string(8)
    print(f"Query ID: {id}")

    await client.prompt_video(message.text, id, workflow=WorkflowTextToVideo())

    start_time = time.time()
    await utils.results_polling(status_func=client.get, download_func=client.download, id=id, file_type="mp4")
    print(f"It took {time.time() - start_time:.3f} seconds to finish. Mad bollocks.")
    
    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'videos')

    result = FSInputFile(os.path.join(result_path, f"{id}_new.mp4"), filename=f"{id}_new.mp4", chunk_size = 1024)

    await message.bot.send_video(message.chat.id, result, caption="Сгенерированное вами видео:")
    await state.clear()