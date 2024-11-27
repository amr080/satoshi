# main.py
from aiohttp import web
import zlib
import logging
import json
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Self-replicating server code as bytes
replication_code = b"""
from aiohttp import web
import zlib

async def handle(request):
    return web.Response(text="I am a replica, running on port 8080")

app = web.Application()
app.router.add_get('/', handle)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)
"""

compressed_payload = zlib.compress(replication_code, level=1)

async def handle(request):
    """Send the compressed replication code to client"""
    return web.Response(
        body=compressed_payload,
        headers={'Content-Type': 'application/octet-stream'}
    )

async def health(request):
    return web.Response(text='OK')

@web.middleware
async def metrics_middleware(request, handler):
    start = datetime.utcnow()
    response = await handler(request)
    duration = (datetime.utcnow() - start).total_seconds()
    logger.info(json.dumps({
        'ip': request.remote,
        'duration': duration,
        'status': response.status,
        'path': request.path
    }))
    return response

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/health', health)
app.middlewares.append(metrics_middleware)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    web.run_app(
        app,
        host='0.0.0.0',
        port=port
    )