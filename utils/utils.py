import string
import random
import asyncio

def generate_string(length):
    all_symbols = string.ascii_uppercase + string.digits
    result = ''.join(random.choice(all_symbols) for _ in range(length))
    return result

async def results_polling(address, status_func, download_func, id, file_type):
    t = True
    while t:
        status = await status_func(id, address, file_type)
        if status == 200:
            t = False
            await download_func(id, address, file_type)
        await asyncio.sleep(0.5)
