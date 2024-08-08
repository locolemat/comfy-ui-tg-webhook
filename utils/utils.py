import string
import random
import asyncio
import time

def generate_string(length):
    all_symbols = string.ascii_uppercase + string.digits
    result = ''.join(random.choice(all_symbols) for _ in range(length))
    return result

def get_dimensions(dimensions):
    dimensions = list(map(int, dimensions.split(':')))

    if dimensions[0] == dimensions[1]:
        return dict(width=512, height=512)
    elif dimensions[0] > dimensions[1]:
        return dict(width=768, height=512)
    else:
        return dict(width=512, height=768)


def calculate_request_eta(start, server_eta):
    current = time.time()
    t = server_eta - (current - start)
    return f"{t:.2f}" if t > 0 else "5"

async def results_polling(address, status_func, download_func, id, file_type):
    t = True
    while t:
        status = await status_func(id, address, file_type)
        if status == 200:
            t = False
            await download_func(id, address, file_type)
        await asyncio.sleep(0.5)
