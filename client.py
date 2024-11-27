import aiohttp
import asyncio
import base64
import zlib
import os

async def connect():
    url = os.getenv('SERVER_URL', 'http://localhost:8080')
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.read()
            decoded = zlib.decompress(base64.b85decode(data)).decode()
            print(f"Received: {decoded[:100]}...")

if __name__ == "__main__":
    asyncio.run(connect())
