import os
import time

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from configuration.localisation import LanguageModel, language
from keyboards.keyboards import greeting_keyboard, dimensions_keyboard
from workflows.controller import WorkflowTextToVideo, WorkflowTextToImage, WorkflowImageToVideo

from server_queue.server_queue import QueueItem
from server_queue.server_queue import Server, QUEUE
from server_queue.propagation import process_queue_result

from model import create_session

from users import User

from states import states
from utils import utils
from client import client


router = Router()

greeting_buttons_text = {
    language.button_generate_text_image,
    language.button_generate_text_video,
    language.button_generate_image_video
}


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


@router.callback_query(F.data.in_(greeting_buttons_text), StateFilter(None))
async def text_to_video_dimensions(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    await call.message.answer(
        text = language.generate_dimensions,
        reply_markup=dimensions_keyboard()
    )

    if call.data == language.button_generate_text_video:
        await state.set_state(states.TextToVideo.choose_dimensions)
    elif call.data == language.button_generate_text_image:
        await state.set_state(states.TextToImage.choose_dimensions)
    elif call.data == language.button_generate_image_video:
        await state.set_state(states.ImageToVideo.choose_dimensions)

    await state.update_data(action=call.data)


@router.callback_query(states.ImageToVideo.choose_dimensions, F.data.startswith('d'))
async def image_to_video_prompt(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = call.data.split("_")[-1]
    await state.update_data(dimensions=data)

    await call.message.answer(
        text = language.video_prompt_invitation
    )

    await state.set_state(states.ImageToVideo.choose_prompt)
    await state.update_data(workflow=WorkflowImageToVideo)


@router.callback_query(states.TextToImage.choose_dimensions, F.data.startswith('d'))
async def text_to_image_prompt(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = call.data.split("_")[-1]
    await state.update_data(dimensions=data)
    
    await call.message.answer(
        text = language.video_length_prompt
    )


    await state.set_state(states.TextToImage.choose_length)
    await state.update_data(workflow=WorkflowTextToImage)


@router.message(F.text, states.TextToImage.choose_length)
async def choose_length(message: Message, state: FSMContext):
    length = 3

    if message.text.split()[0].isdigit():
        length = int(message.text)
    
    if length < 2:
        length = 2
    elif length > 20:
        length = 20

    await message.answer(
        text = language.prompt_invitation
    )

    await state.update_data(length=length)
    await state.set_state(states.TextToImage.choose_prompt)


@router.callback_query(states.TextToVideo.choose_dimensions, F.data.startswith('d'))
async def text_to_video_prompt(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = call.data.split("_")[-1]
    await state.update_data(dimensions=data)

    await call.message.answer(
        text = language.prompt_invitation
    )


    await state.set_state(states.TextToVideo.choose_prompt)
    await state.update_data(workflow=WorkflowTextToVideo)
        

@router.message(F.text, states.TextToImage.choose_prompt)        
@router.message(F.text, states.TextToVideo.choose_prompt)
async def from_text_generation(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    workflow = data["workflow"]
    file_type = workflow.file_type
    folder = workflow.folder
    
    length = data.get("length")

    session = create_session()
    server = Server.find_available(session)

    if server:

        server.busy = True
        session.commit()

        await message.answer(
            text = LanguageModel.with_context(template=language.pre_generation_message,
                                            context={"action": data["action"],
                                                    "dimensions": data["dimensions"],
                                                    "prompt": message.text})
        )

        dimensions = utils.get_dimensions(data["dimensions"])

        await message.answer(
            text = language.generation_began
        )

        id = utils.generate_string(10)
        print(f"Query ID: {id}")

        await client.prompt_query(prompt=message.text, address=server.address, id=id, workflow=workflow(), width=dimensions["width"], height=dimensions["height"], frames=length*6)

        start_time = time.time()
        await utils.results_polling(address=server.address, status_func=client.get, download_func=client.download, id=id, file_type=file_type)
        print(f"It took {time.time() - start_time:.3f} seconds to finish. Mad bollocks.")
        
        result_path = os.path.join(os.path.dirname(__file__), '..', 'data', folder)

        result = FSInputFile(os.path.join(result_path, f"{id}_new.{file_type}"), filename=f"{id}_new.{file_type}", chunk_size = 1024)

        if folder == "videos":
            await message.bot.send_video(message.chat.id, result, caption=language.video_ready)
        elif folder == "photos":
            await message.answer_photo(result, caption=language.picture_ready)
        await state.clear()

        server.busy = True
        session.commit()

        queue_item = QUEUE.advance_queue()

        if queue_item:
            await process_queue_result(queue_item=queue_item, server=server)

    else:
        queue_item = QueueItem(prompt=message.text, workflow=workflow, dimensions=data["dimensions"], user_id=message.chat.id)
        QUEUE.add_to_queue(queue_item=queue_item)
        position = QUEUE.get_length()
        await message.answer(
            text=LanguageModel.with_context(template=language.queue_added, context={"position": position})
        )

    session.close()

@router.message(F.photo, states.ImageToVideo.choose_prompt)
async def from_image_generation(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    
    workflow = data["workflow"]
    file_type = workflow.file_type
    folder = workflow.folder

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'upload')
    photo_id = message.photo[-1].file_id

    id = utils.generate_string(10)
    image_name = f"{id}_up.png"
    photo_path = os.path.join(UPLOAD_FOLDER, image_name)
    await message.bot.download(file=photo_id, destination=photo_path)
    
    session = create_session()
    server = Server.find_available(session)

    if server:
        server.busy = True
        session.commit()

        dimensions = utils.get_dimensions(data["dimensions"])
        await client.upload_image(address=server.address, image_path=photo_path)

        await client.prompt_query(address=server.address, prompt=image_name, id = id, workflow=workflow(), width=dimensions["width"], height=dimensions["height"])

        start_time = time.time()
        await utils.results_polling(address=server.address, status_func=client.get, download_func=client.download, id=id, file_type=file_type)
        print(f"It took {time.time() - start_time:.3f} seconds to finish. Mad bollocks.")

        result_path = os.path.join(os.path.dirname(__file__), '..', 'data', folder)

        result = FSInputFile(os.path.join(result_path, f"{id}_new.{file_type}"), filename=f"{id}_new.{file_type}", chunk_size = 1024)

        await message.bot.send_video(message.chat.id, result, caption=language.video_ready)

        server.busy = False
        session.commit()

        await state.clear()

        queue_item = QUEUE.advance_queue()
        if queue_item:
            await process_queue_result(queue_item=queue_item, server=server)

    else:
        queue_item = QueueItem(prompt=photo_path, workflow=workflow, dimensions=data["dimensions"], user_id=message.chat.id)
        QUEUE.add_to_queue(queue_item=queue_item)
        position = QUEUE.get_length()
        await message.answer(
            text=LanguageModel.with_context(template=language.queue_added, context={"position": position})
        )

    session.close()




