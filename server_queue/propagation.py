import time
import os

from bot import bot

from server_queue.server_queue import Server, QueueItem, create_session
from configuration.localisation import LanguageModel, language

from aiogram.types import FSInputFile

from utils import utils
from client import client

async def process_queue_result_text(queue_item: QueueItem, server: Server):
    print("BEGAN PROPAGATING EVENT")
    await bot.send_message(
        chat_id=queue_item.user_id(),
        text = LanguageModel.with_context(
            template=language.queue_is_up,
            context={"prompt": queue_item.prompt()}
                                        )
    )
    workflow = queue_item.workflow()
    file_type = workflow.file_type
    folder = workflow.folder

    session = create_session()
    server = session.get(Server, server.id)
    server.busy = True
    session.commit()

    await bot.send_message(
        chat_id=queue_item.user_id(),
        text = language.generation_began
    )

    id = utils.generate_string(10)
    print(f"Query ID: {id}")

    print('Propagation: make a query')

    await client.prompt_query(prompt=queue_item.prompt(), address=server.address, id=id, workflow=workflow())

    start_time = time.time()

    print('Propagation: start polling')
    await utils.results_polling(address=server.address(), status_func=client.get, download_func=client.download, id=id, file_type=file_type)
    print(f"It took {time.time() - start_time:.3f} seconds to finish. Mad bollocks.")
    
    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', folder)

    result = FSInputFile(os.path.join(result_path, f"{id}_new.{file_type}"), filename=f"{id}_new.{file_type}", chunk_size = 1024)

    if folder == "videos":
        await bot.send_video(queue_item.user_id(), result, caption=language.video_ready)
    elif folder == "photos":
        await bot.send_photo(queue_item.user_id(), result, caption=language.picture_ready)


    server.busy = False
    session.commit()
    session.close()


async def process_queue_result_image(queue_item: QueueItem, server: Server):
    print("BEGAN PROPAGATING EVENT")

    session = create_session()
    server = session.get(Server, server.id)
    server.busy = True
    session.commit()

    await bot.send_message(
        chat_id=queue_item.user_id(),
        text = LanguageModel.with_context(
            template=language.queue_is_up,
            context={"prompt": queue_item.prompt()}
                                        )
    )

    workflow = queue_item.workflow()
    file_type = workflow.file_type
    folder = workflow.folder
    print('Propagation: image upload')

    await client.upload_image(address=server.address, image_path=queue_item.prompt())

    print('Propagation: make a query')
    await client.prompt_query(address=server.address, prompt=os.path.basename(queue_item.prompt()), id = id, workflow=workflow())

    start_time = time.time()
    print('Propagation: start polling')
    await utils.results_polling(address=server.address, status_func=client.get, download_func=client.download, id=id, file_type=file_type)
    print(f"It took {time.time() - start_time:.3f} seconds to finish. Mad bollocks.")

    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', folder)

    result = FSInputFile(os.path.join(result_path, f"{id}_new.{file_type}"), filename=f"{id}_new.{file_type}", chunk_size = 1024)

    await bot.send_video(queue_item.user_id(), result, caption=language.video_ready)

    server.busy = False
    session.commit()
    session.close()