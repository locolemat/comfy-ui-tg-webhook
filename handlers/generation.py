import os

from random import choice

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from configuration.localisation import LanguageModel, language
from keyboards import dimensions_keyboard, greeting_keyboard
from workflows.controller import WorkflowTextToVideo, WorkflowTextToImage, WorkflowImageToVideo, WORKFLOW_MAPPING
from server_queue import Queue, Server


from model import create_session, create_session_queue

from users import User

from states import states
from utils import utils
from client import client


router = Router()

greeting_buttons_text = {'i2v':language.button_generate_image_video, 't2v': language.button_generate_text_video, 't2i': language.button_generate_text_image}
async def unclog_queue():
    for server in Server.get_all_servers():
        await server.server_polling()


# @router.message(F.text, Command('armageddon'))
# async def unleash_gallery(message: Message, state: FSMContext):
#     tgid = message.from_user.id

#     upload_directory = os.path.join(os.path.dirname(__file__), '..', 'data', 'upload', 'gallery')
#     files_to_send = os.listdir(upload_directory)

#     with open('file_ids.txt', 'a') as f:
#         for file in files_to_send:
#             photo = FSInputFile(os.path.join(upload_directory, file), filename=f"{file}_new.png", chunk_size = 1024)
#             uploaded_file = await message.bot.send_photo(chat_id=tgid, photo=photo)
#             file_id = uploaded_file.photo[0].file_id
#             f.write(f'{file}:{file_id}\n')


@router.message(F.text, CommandStart())
async def greeting_reply(message: Message, state: FSMContext):
    await state.clear()
    
    tgid = message.from_user.id
    queue_info = ""
    session = create_session()

    user = User.return_user_if_exists(tgid=tgid, session=session)

    if user is None:
        username = message.from_user.first_name
        balance = 10
        preferred_model = "anithing_v11Pruned.safetensors"
        preferred_video_model = "SVD/svd_xt.safetensors"
        user = User(username=username, tgid=tgid, balance=balance, preferred_model=preferred_model, preferred_video_model=preferred_video_model)
        session.add(user)
        session.commit()


    else:
        username = user.username
        balance = user.balance

        queue_size = Queue.get_users_queue_length(user_id = user.tgid)
        processed_queue_request = Queue.get_users_processed_request(user_id = user.tgid)

        if processed_queue_request:
            start_time = processed_queue_request.begin_time
            server_eta = Server.find_server_by_address(session=session, address=processed_queue_request.server_address).eta

            queue_info += LanguageModel.with_context(template = language.greeting_current_request,
                                                     context={"eta": utils.calculate_request_eta(start=start_time, server_eta=server_eta)})

        if queue_size - 1 > 0:
            queue_info += LanguageModel.with_context(template = language.greeting_queue_size,
                                                     context={"queue_size": queue_size - 1})

    session.close()

    await message.answer(
        text=LanguageModel.with_emojis(
                                    LanguageModel.with_context(template=language.greeting, 
                                       context={"username":username,"tokens":balance, "queue_info": queue_info}
                                       )),
        reply_markup=greeting_keyboard()
    )

    await unclog_queue()


@router.callback_query(F.data.in_(greeting_buttons_text.keys()), StateFilter(None))
async def text_to_video_dimensions(call: CallbackQuery, state: FSMContext):
    await call.message.bot.edit_message_text(
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        text = language.generate_dimensions,
        reply_markup=dimensions_keyboard()
    )

    if call.data == 't2v':
        await state.set_state(states.TextToVideo.choose_dimensions)
    elif call.data == 't2i':
        await state.set_state(states.TextToImage.choose_dimensions)
    elif call.data == 'i2v':
        await state.set_state(states.ImageToVideo.choose_dimensions)

    await state.update_data(action=greeting_buttons_text.get(call.data))
    await unclog_queue()


@router.callback_query(states.ImageToVideo.choose_dimensions, F.data.startswith('d'))
async def image_to_video_prompt(call: CallbackQuery, state: FSMContext):
    data = call.data.split("_")[-1]
    await state.update_data(dimensions=data)

    await call.message.bot.edit_message_text(
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        text = language.video_prompt_invitation
    )

    await state.set_state(states.ImageToVideo.choose_prompt)
    await state.update_data(workflow="i2v")
    await unclog_queue()


@router.callback_query(states.TextToImage.choose_dimensions, F.data.startswith('d'))
async def text_to_image_prompt(call: CallbackQuery, state: FSMContext):
    data = call.data.split("_")[-1]
    await state.update_data(dimensions=data)
    
    await call.message.bot.edit_message_text(
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        text = language.prompt_invitation
    )


    await state.set_state(states.TextToImage.choose_prompt)
    await state.update_data(workflow="t2i")
    await unclog_queue()


@router.callback_query(states.TextToVideo.choose_dimensions, F.data.startswith('d'))
async def text_to_video_prompt(call: CallbackQuery, state: FSMContext):
    data = call.data.split("_")[-1]
    await state.update_data(dimensions=data)

    # await call.message.bot.edit_message_text(
    #     message_id=call.message.message_id,
    #     chat_id=call.message.chat.id,
    #     text = language.video_length_prompt
    # )

    await call.message.bot.edit_message_text(
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        text = language.prompt_invitation
    )

    await state.set_state(states.TextToVideo.choose_prompt)
    await state.update_data(workflow="t2v")
    await unclog_queue()

@router.message(F.text, states.TextToVideo.choose_length)
async def choose_length(message: Message, state: FSMContext):
    length = 3

    if message.text.split()[0].isdigit():
        length = int(message.text)
    
    if length < 2:
        length = 2
    elif length > 10:
        length = 10

    await message.answer(
        text = language.prompt_invitation
    )

    await state.update_data(length=length)
    await state.set_state(states.TextToVideo.choose_prompt)
    await unclog_queue()

@router.message(F.text, states.ImageToVideo.choose_length)
async def choose_length_i2v(message: Message, state: FSMContext):
    length = 3

    if message.text.split()[0].isdigit():
        length = int(message.text)
    
    if length < 2:
        length = 2
    elif length > 10:
        length = 10

    await message.answer(
        text = language.video_prompt_invitation
    )

    await state.update_data(length=length)
    await state.set_state(states.ImageToVideo.choose_prompt)
    await unclog_queue()


@router.message(F.text, states.TextToImage.choose_prompt)
async def t2i_negative_prompt(message: Message, state: FSMContext):
    prompt = message.text
    await state.update_data(prompt = prompt)

    await message.answer(
        text = language.negative_prompt_invitation
    )

    await state.set_state(states.TextToImage.choose_negative_prompt)
    await unclog_queue()

@router.message(F.text, states.TextToVideo.choose_prompt)
async def t2v_negative_prompt(message: Message, state: FSMContext):
    prompt = message.text
    await state.update_data(prompt = prompt)

    await message.answer(
        text = language.negative_prompt_invitation
    )

    await state.set_state(states.TextToVideo.choose_negative_prompt)
    await unclog_queue()

@router.message(F.text, states.TextToImage.choose_negative_prompt)        
@router.message(F.text, states.TextToVideo.choose_negative_prompt)
async def from_text_generation(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    workflow = data["workflow"]
    prompt = data["prompt"]
    negative_prompt = message.text
    dimensions = data["dimensions"]
    file_type = WORKFLOW_MAPPING[workflow].file_type
    folder = WORKFLOW_MAPPING[workflow].folder

    # session = create_session()
    # server = Server.find_available(session) if workflow == WorkflowTextToImage else Server.find_available_for_video(session)
    # session.close()

    session = create_session()
    if WORKFLOW_MAPPING[workflow] == WorkflowTextToImage:
        server_address = choice(list(Server.find_available_for_text(session))).address
    else:
        server_address = choice(list(Server.find_available_for_video(session))).address
    user = User.return_user_if_exists(tgid = message.chat.id, session=session)
    session.close()
    
    Queue.add_new_queue_item(prompt=prompt, negative_prompt=negative_prompt, workflow=workflow, dimensions=dimensions, user_id=user.tgid, upload_image_name="", server_address=server_address)
    await state.clear()
    await unclog_queue()
    # DEPRECATED:
    # if server:

    #     server_id = server.id   
        
    #     session = create_session()
    #     server = session.get(Server, server_id)
    #     server.busy = True
    #     session.commit()

    #     await message.answer(
    #         text = LanguageModel.with_context(template=language.pre_generation_message,
    #                                         context={"action": data["action"],
    #                                                 "dimensions": data["dimensions"],
    #                                                 "prompt": prompt})
    #     )

    #     dimensions = utils.get_dimensions(data["dimensions"])

    #     await message.answer(
    #         text = language.generation_began
    #     )

    #     id = utils.generate_string(10)
    #     print(f"Query ID: {id}")

    #     await client.prompt_query(prompt=LanguageModel.translate_to_english(prompt), negative_prompt=negative_prompt, address=server.address, id=id, workflow=workflow(), width=dimensions["width"], height=dimensions["height"], frames=length*12, model=model, video_model=video_model)

    #     start_time = time.time()
    #     await utils.results_polling(address=server.address, status_func=client.get, download_func=client.download, id=id, file_type=file_type)
    #     print(f"It took {time.time() - start_time:.3f} seconds to finish. Mad bollocks.")
        
    #     result_path = os.path.join(os.path.dirname(__file__), '..', 'data', folder)

    #     result = FSInputFile(os.path.join(result_path, f"{id}_new.{file_type}"), filename=f"{id}_new.{file_type}", chunk_size = 1024)

    #     if folder == "videos":
    #         await message.bot.send_video(message.chat.id, result, caption=language.video_ready)
    #     elif folder == "photos":
    #         await message.answer_photo(result, caption=language.picture_ready)
    #     await state.clear()


    #     session.close()

    #     session = create_session()
    #     server = session.get(Server, server_id)
    #     server.busy = False
        
    #     queue_item = QUEUE.advance_queue()

    #     if queue_item:
    #         await process_queue_result(queue_item=queue_item, server=server)

    #     session.commit()
    #     session.close()

    # else:
    #     queue_item = QueueItem(prompt=prompt, negative_prompt=negative_prompt, workflow=workflow, dimensions=data["dimensions"], user_id=message.chat.id, length=length)
    #     QUEUE.add_to_queue(queue_item=queue_item)
    #     position = QUEUE.get_length()
    #     await message.answer(
    #         text=LanguageModel.with_context(template=language.queue_added, context={"position": position})
    #     )


@router.message(F.photo, states.ImageToVideo.choose_prompt)
async def from_image_generation(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    
    workflow = data["workflow"]
    file_type = WORKFLOW_MAPPING[workflow].file_type
    folder = WORKFLOW_MAPPING[workflow].folder
    dimensions = data["dimensions"]

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'upload')
    photo_id = message.photo[-1].file_id

    id = utils.generate_string(10)
    image_name = f"{id}_up.png"
    photo_path = os.path.join(UPLOAD_FOLDER, image_name)
    await message.bot.download(file=photo_id, destination=photo_path)
    

    session = create_session()
    server_address = choice(list(Server.find_available_for_video(session))).address
    user = User.return_user_if_exists(tgid = message.chat.id, session=session)
    session.close()

    Queue.add_new_queue_item(prompt="", negative_prompt="", workflow=workflow, dimensions=dimensions, user_id=user.tgid, upload_image_name=photo_path, server_address=server_address)

    await state.clear()
    await unclog_queue()
    # DEPRECATED:
    # if server:
    #     server_id = server.id   
        
    #     session = create_session()
    #     server = session.get(Server, server_id)
    #     server.busy = True
    #     session.commit()

    #     dimensions = utils.get_dimensions(data["dimensions"])
    #     await client.upload_image(address=server.address, image_path=photo_path)

    #     await client.prompt_query(address=server.address, prompt=image_name, id = id, workflow=workflow(), width=dimensions["width"], height=dimensions["height"], frames=length*12)

    #     start_time = time.time()
    #     await utils.results_polling(address=server.address, status_func=client.get, download_func=client.download, id=id, file_type=file_type)
    #     print(f"It took {time.time() - start_time:.3f} seconds to finish. Mad bollocks.")

    #     result_path = os.path.join(os.path.dirname(__file__), '..', 'data', folder)

    #     result = FSInputFile(os.path.join(result_path, f"{id}_new.{file_type}"), filename=f"{id}_new.{file_type}", chunk_size = 1024)

    #     await message.bot.send_video(message.chat.id, result, caption=language.video_ready)

    #     await state.clear()

    #     session.close()

    #     session = create_session()
    #     server = session.get(Server, server_id)
    #     server.busy = False
        

    #     queue_item = QUEUE.advance_queue()
    #     if queue_item:
    #         await process_queue_result(queue_item=queue_item, server=server)

    #     session.commit()
    #     session.close()

    # else:
    #     queue_item = QueueItem(prompt=photo_path, workflow=workflow, dimensions=data["dimensions"], user_id=message.chat.id, length=length)
    #     QUEUE.add_to_queue(queue_item=queue_item)
    #     position = QUEUE.get_length()
    #     await message.answer(
    #         text=LanguageModel.with_context(template=language.queue_added, context={"position": position})
    #     )





