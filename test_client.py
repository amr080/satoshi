# test_client.py
import aiohttp
import asyncio

async def test_connection(url):
    async with aiohttp.ClientSession() as session:
        # Test main endpoint
        async with session.get(f"{url}/") as resp:
            print(f"Main endpoint status: {resp.status}")
            
        # Test health endpoint
        async with session.get(f"{url}/health") as resp:
            print(f"Health check status: {resp.status}")

if __name__ == "__main__":
    url = "https://satoshi-xyz.ondigitalocean.app"  # Replace with your URL
    asyncio.run(test_connection(url))
