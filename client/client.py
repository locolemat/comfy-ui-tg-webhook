import aiofiles
import aiohttp
import asyncio
import os

from random import randint

import json


async def prompt_query(prompt, address, id, width, height, workflow, frames=None):

    async with aiohttp.ClientSession() as session:
        response = await session.post(f"http://{address}/prompt", 
                                      json=workflow.get_workflow(prompt=prompt, id=id, negative_prompt="", width=width, height=height, frames=frames, seed=randint(1, 1_000_000_000)))
        print("Запрос сгенерирован", response.status)
        response.close()


async def get(id, address, file_type="png"):
    async with aiohttp.ClientSession() as session:
        response = await session.get(f"http://{address}/view?filename={id}_00001{'_'*(file_type == 'png')}.{file_type}&subfolder=&type=output")
        status = response.status
        response.close()
        # print(f'The status of the file request: {status}.')
        return status
    

async def upload_image(image_path, address):
    data = aiohttp.FormData()
    with open(image_path, 'rb') as f:
        data.add_field('image', f, filename=os.path.basename(image_path), content_type='image/png')
        async with aiohttp.ClientSession() as session:
            response = await session.post(f'http://{address}/upload/image', data=data)
            status = response.text
            response.close()
            return status
            


async def download(id, address, file_type="png"):
    folder = "photos"
    if file_type != "png":
        folder = "videos"
        await asyncio.sleep(2)
    else:
        await asyncio.sleep(1)

    async with aiohttp.ClientSession() as session:
        response = await session.get(f"http://{address}/view?filename={id}_00001{'_'*(file_type == 'png')}.{file_type}&subfolder=&type=output")
        async with aiofiles.open(f'data//{folder}//{id}_new.{file_type}', 'wb') as target:
            async for chank in response.content.iter_chunked(64*1024):
                await target.write(chank)
        response.close()