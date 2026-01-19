import asyncio

import aiohttp

from learning.decorators import timer
from multi_thread_demo import urls


async def async_download_site(session: aiohttp.ClientSession, url: str):
    """模拟IO密集任务"""
    async with session.get(url) as response:
        content = await response.content.read()
        print(f"Read {len(content)} bytes from {url}")

@timer
async def async_download_sites():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(async_download_site(session, url))
            tasks.append(task)
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(async_download_sites())
