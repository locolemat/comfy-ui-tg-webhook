import aiofiles
import aiohttp
import asyncio
import os

from configuration.config import ADDRESSES

async def prompt_query(prompt, id, workflow):

    async with aiohttp.ClientSession() as session:
        response = await session.post(f"http://{ADDRESSES[0]}/prompt", 
                                      json=workflow.get_workflow(prompt=prompt, id=id, negative_prompt=""))
        print("Запрос сгенерирован", response.status)


async def get(id, file_type="png"):
    async with aiohttp.ClientSession() as session:
        response = await session.get(f"http://{ADDRESSES[0]}/view?filename={id}_00001{'_'*(file_type == 'png')}.{file_type}&subfolder=&type=output")
        status = response.status
        response.close()
        print(f'The status of the file request: {status}.')
        return status
    

async def upload_image(image, address = ADDRESSES[0]):
    data = aiohttp.FormData()
    with open(os.getcwd() + '/upload/' + image, 'rb') as f:
        data.add_field('file', f, filename=image, content_type='image/png')
        async with aiohttp.ClientSession() as session:
            response = await session.post(f'http://{address}/upload_image', data=data)
            response.close()
            return await response.text()


async def download(id, file_type="png"):
    await asyncio.sleep(1)
    folder = "photos"
    if file_type != "png":
        folder = "videos"
    async with aiohttp.ClientSession() as session:
        response = await session.get(f"http://{ADDRESSES[0]}/view?filename={id}_00001{'_'*(file_type == 'png')}.{file_type}&subfolder=&type=output")
        async with aiofiles.open(f'data//{folder}//{id}_new.{file_type}', 'wb') as target:
            async for chank in response.content.iter_chunked(64*1024):
                await target.write(chank)