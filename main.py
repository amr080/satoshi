import base64
import asyncio
import zlib
import logging
from aiohttp import web
import uvloop
import os
import json
from datetime import datetime

# Install uvloop for faster event loop
uvloop.install()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Server code as a formatted string
q = """
import base64, asyncio, zlib, logging
from aiohttp import web
import uvloop, os

uvloop.install()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

q = {0!r}

async def handle(request):
    return web.Response(
        body=encoded_q,
        headers={
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/octet-stream'
        }
    )

app = web.Application(client_max_size=1024**2, keepalive_timeout=75)
app.router.add_get('/', handle)

@web.middleware
async def metrics_middleware(request, handler):
    start = datetime.utcnow()
    response = await handler(request)
    duration = (datetime.utcnow() - start).total_seconds()
    logger.info(json.dumps({
        'ip': request.remote,
        'duration': duration,
        'status': response.status
    }))
    return response

app.middlewares.append(metrics_middleware)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    web.run_app(app, host='0.0.0.0', port=port, backlog=2048)
"""

# Precompute encoded and compressed server code
encoded_q = base64.b85encode(zlib.compress(q.format(q).encode(), level=9))

async def handle(request):
    return web.Response(
        body=encoded_q,
        headers={
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/octet-stream'
        }
    )

app = web.Application(client_max_size=1024**2, keepalive_timeout=75)
app.router.add_get('/', handle)

@web.middleware
async def metrics_middleware(request, handler):
    start = datetime.utcnow()
    response = await handler(request)
    duration = (datetime.utcnow() - start).total_seconds()
    logger.info(json.dumps({
        'ip': request.remote,
        'duration': duration,
        'status': response.status
    }))
    return response

app.middlewares.append(metrics_middleware)

def run_server(port):
    asyncio.run(async_server(port))

async def async_server(port):
    server = await web._run_app(app, host='0.0.0.0', port=port, backlog=2048)
    await server

if __name__ == "__main__":
    cpu_count = os.cpu_count()
    ports = range(8080, 8080 + cpu_count)
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        executor.map(run_server, ports)
