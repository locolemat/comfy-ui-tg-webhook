import aiofiles
import aiohttp
import asyncio

from configuration.config import ADDRESSES

async def prompt_video(prompt, id, workflow):

    async with aiohttp.ClientSession() as session:
        response = await session.post(f"http://{ADDRESSES[0]}/prompt", 
                                      json=workflow.get_workflow(prompt=prompt, id=id))
        print("Запрос сгенерирован", response.status)