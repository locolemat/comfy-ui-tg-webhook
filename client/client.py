import aiofiles
import aiohttp
import asyncio

from configuration.config import ADDRESSES
from workflows.controller import WorkflowTextToVideo

async def prompt_video(prompt, id):

    async with aiohttp.ClientSession() as session:
        response = await session.post(f"http://{ADDRESSES[0]}/prompt", 
                                      json=WorkflowTextToVideo().get_workflow(prompt=prompt, id=id))
        print("Запрос сгенерирован", response.status)