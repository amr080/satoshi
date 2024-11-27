import base64
import asyncio
import zlib
import logging
from aiohttp import web
import uvloop
import os

# Setup uvloop for faster event loop
uvloop.install()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server code as a formatted string
q = """
import base64, asyncio, zlib, logging
from aiohttp import web

q = {0!r}

async def handle_connection(request):
    encoded = base64.b85encode(zlib.compress(q.format(q).encode(), level=9))
    logging.info(f"Connection from {request.remote}")
    return web.Response(body=encoded, headers={'Content-Type': 'application/octet-stream'})

app = web.Application()
app.router.add_get('/', handle_connection)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    web.run_app(app, port=port)
"""

# Precompute encoded and compressed server code
encoded_q = base64.b85encode(zlib.compress(q.format(q).encode(), level=9))

async def handle_connection(request):
    logger.info(f"Connection from {request.remote}")
    return web.Response(body=encoded_q, headers={'Content-Type': 'application/octet-stream'})

app = web.Application()
app.router.add_get('/', handle_connection)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    web.run_app(app, port=port)
