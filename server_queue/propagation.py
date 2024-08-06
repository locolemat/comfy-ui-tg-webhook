import time
import os

from bot import bot

from model import create_session_queue

from server_queue import Server, Queue
from configuration.localisation import LanguageModel, language
from users import User

from workflows.controller import WORKFLOW_MAPPING, WorkflowTextToVideo, WorkflowTextToImage, WorkflowImageToVideo, Workflow

from aiogram.types import FSInputFile


from utils import utils
from client import client


async def wake_queue():
    await queue_work(starting_id = 1)


async def queue_work(starting_id: int):
    if Queue.get_queue_length() > 0:
        
        queue_item = Queue.get_queue_item_by_id(starting_id)
        workflow = WORKFLOW_MAPPING.get(queue_item.workflow)

        if workflow.requires_image_upload:
            await process_queue_result_image(queue_item=queue_item, workflow=workflow)
        else:
            await process_queue_result_text(queue_item=queue_item, workflow=workflow)


async def process_queue_result_text(queue_item: Queue, workflow: Workflow):
    print("BEGAN PROPAGATING EVENT")
    session = create_session_queue()
    server = Server.find_available_for_text(session) if workflow == WorkflowTextToImage else Server.find_available_for_video(session)
    session.close()

    if server:
        await bot.send_message(
            chat_id=queue_item.user_id,
            text = LanguageModel.with_context(
                template=language.queue_is_up,
                context={"prompt": queue_item.prompt}
                                        )
        )
        file_type = workflow.file_type
        folder = workflow.folder

        dimensions = utils.get_dimensions(queue_item.dimensions)

        session = create_session_queue()
        server = session.get(Server, server.id)
        user = User.return_user_if_exists(session=session, tgid=queue_item.user_id)

        model = user.preferred_model
        video_model = user.preferred_video_model

        await bot.send_message(
            chat_id=queue_item.user_id,
            text = language.generation_began
        )

        id = utils.generate_string(10)
        print(f"Query ID: {id}")

        print('Propagation: make a query')

        await client.prompt_query(prompt=LanguageModel.translate_to_english(queue_item.prompt), negative_prompt=queue_item.negative_prompt, address=server.address, id=id, workflow=workflow, width=dimensions["width"], height=dimensions["height"], frames=0, model=model, video_model=video_model)

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
        Queue.delete_queue_item(queue_item.id)
        session.commit()
        session.close()
        await queue_work(starting_id=1)
    else:
        await queue_work(queue_item.id + 1)

    


async def process_queue_result_image(queue_item: Queue, workflow: Workflow):
    print("BEGAN PROPAGATING EVENT")
    session = create_session_queue()
    server = Server.find_available_for_video(session)
    session.close()

    if server:
        session = create_session_queue()
        server = session.get(Server, server.id)

        await bot.send_message(
            chat_id=queue_item.user_id,
            text = LanguageModel.with_context(
                template=language.queue_is_up,
                context={"prompt": queue_item.prompt}
                                            )
        )

        dimensions = utils.get_dimensions(queue_item.dimensions)

        workflow = queue_item.workflow
        file_type = workflow.file_type
        folder = workflow.folder
        print('Propagation: image upload')
        
        UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'upload')
        image_name = f"{queue_item.upload_image_name}_up.png"
        photo_path = os.path.join(UPLOAD_FOLDER, image_name)

        await client.upload_image(address=server.address, image_path=photo_path)

        print('Propagation: make a query')
        await client.prompt_query(address=server.address, prompt=os.path.basename(queue_item.prompt), id = id, workflow=workflow, width=dimensions["width"], height=dimensions["height"], frames=0)

        start_time = time.time()
        print('Propagation: start polling')
        await utils.results_polling(address=server.address, status_func=client.get, download_func=client.download, id=id, file_type=file_type)
        print(f"It took {time.time() - start_time:.3f} seconds to finish. Mad bollocks.")

        result_path = os.path.join(os.path.dirname(__file__), '..', 'data', folder)

        result = FSInputFile(os.path.join(result_path, f"{id}_new.{file_type}"), filename=f"{id}_new.{file_type}", chunk_size = 1024)

        await bot.send_video(queue_item.user_id, result, caption=language.video_ready)

        server.busy = False
        session.commit()
        session.close()
    else:
        await queue_work(queue_item.id + 1)