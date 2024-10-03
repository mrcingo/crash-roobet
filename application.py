import asyncio

from src.firebase import DATABASE

from src.browser import _Page
from src.roobet import Crash


async def main():
    async with _Page('https://roobet.com/crash') as page:
        async with Crash(page) as crash:
            async for crash_point in crash:
                DATABASE.push(crash_point)

if __name__ == '__main__':
    asyncio.run(main())
