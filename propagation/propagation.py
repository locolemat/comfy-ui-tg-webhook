import time
import os

from bot import bot

from model import create_session

from server_queue import Queue
from configuration.localisation import LanguageModel, language
from users import User

from workflows.controller import WORKFLOW_MAPPING, WorkflowTextToVideo, WorkflowTextToImage, WorkflowImageToVideo, Workflow

from aiogram.types import FSInputFile


from utils import utils
from client import client


async def wake_queue():
    await queue_work()


async def queue_work(queue_item, workflow, server):
    workflow = WORKFLOW_MAPPING[workflow]
    if workflow.requires_image_upload:
        await process_queue_result_image(queue_item=queue_item, workflow=workflow, server=server)
    else:
        await process_queue_result_text(queue_item=queue_item, workflow=workflow, server=server)


async def process_queue_result_text(queue_item: Queue, workflow: Workflow, server):
    print("BEGAN PROPAGATING EVENT")
    await bot.send_message(
        chat_id=queue_item.user_id,
        text = LanguageModel.with_context(
            template=language.queue_is_up,
            context={"prompt": queue_item.prompt, "eta": f"{server.eta:.2f}"}
                                    )
    )
    file_type = workflow.file_type
    folder = workflow.folder

    dimensions = utils.get_dimensions(queue_item.dimensions)

    session = create_session()
    user = User.return_user_if_exists(session=session, tgid=queue_item.user_id)
    session.close()

    model = user.preferred_model
    video_model = user.preferred_video_model

    id = utils.generate_string(10)
    print(f"Query ID: {id}")

    print('Propagation: make a query')

    await client.prompt_query(prompt=LanguageModel.translate_to_english(queue_item.prompt), negative_prompt=queue_item.negative_prompt, address=server.address, id=id, workflow=workflow(), width=dimensions["width"], height=dimensions["height"], frames=0, model=model, video_model=video_model)

    start_time = time.time()

    print('Propagation: start polling')
    await utils.results_polling(address=server.address, status_func=client.get, download_func=client.download, id=id, file_type=file_type)
    print(f"It took {time.time() - start_time:.3f} seconds to finish. Mad bollocks.")
    
    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', folder)

    result = FSInputFile(os.path.join(result_path, f"{id}_new.{file_type}"), filename=f"{id}_new.{file_type}", chunk_size = 1024)

    if folder == "videos":
        await bot.send_video(queue_item.user_id, result, caption=language.video_ready)
    elif folder == "photos":
        await bot.send_photo(queue_item.user_id, result, caption=language.picture_ready)

    server.busy = False
    server.update_server_eta(time.time() - start_time)
    Queue.delete_queue_item(queue_item.id)


async def process_queue_result_image(queue_item: Queue, workflow: Workflow, server):
    print("BEGAN PROPAGATING EVENT")
    

    await bot.send_message(
        chat_id=queue_item.user_id,
        text = LanguageModel.with_context(
            template=language.queue_is_up,
            context={"prompt": queue_item.prompt, "eta": f"{server.eta:.2f}"}
                                        )
    )

    dimensions = utils.get_dimensions(queue_item.dimensions)

    session = create_session()
    user = User.return_user_if_exists(session=session, tgid=queue_item.user_id)
    session.close()

    model = user.preferred_model
    video_model = user.preferred_video_model
    file_type = workflow.file_type
    folder = workflow.folder
    print('Propagation: image upload')
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'upload')
    photo_path = os.path.join(UPLOAD_FOLDER, queue_item.upload_image_name)

    await client.upload_image(address=server.address, image_path=photo_path)

    id = queue_item.upload_image_name.split('/')[-1].split('_')[0]

    print('Propagation: make a query')
    await client.prompt_query(address=server.address, prompt=os.path.basename(queue_item.prompt), id = id, workflow=workflow(), width=dimensions["width"], height=dimensions["height"], frames=0, model=model, video_model=video_model)

    start_time = time.time()
    print('Propagation: start polling')
    await utils.results_polling(address=server.address, status_func=client.get, download_func=client.download, id=id, file_type=file_type)
    print(f"It took {time.time() - start_time:.3f} seconds to finish. Mad bollocks.")

    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', folder)

    result = FSInputFile(os.path.join(result_path, f"{id}_new.{file_type}"), filename=f"{id}_new.{file_type}", chunk_size = 1024)

    await bot.send_video(queue_item.user_id, result, caption=language.video_ready)

    server.busy = False
    server.eta = (server.eta + time.time()) / 2
    Queue.delete_queue_item(queue_item.id)