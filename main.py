# main.py
from aiohttp import web
import base64, zlib, logging, json, os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Self-replicating server code
q = """
from aiohttp import web
import base64, zlib, logging, json, os
from datetime import datetime

q = {0!r}
encoded_q = base64.b85encode(zlib.compress(q.format(q).encode(), level=9))

async def handle(request):
    logger.info(json.dumps({{'ip': request.remote, 'type': 'replication_request'}}))
    return web.Response(
        body=encoded_q,
        headers={{
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/octet-stream',
            'Server': 'Satoshi/1.0'
        }}
    )

async def health(request):
    return web.Response(text='OK')

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/health', health)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    web.run_app(app, host='0.0.0.0', port=port)
"""

# Pre-compute encoded version
encoded_q = base64.b85encode(zlib.compress(q.format(q).encode(), level=9))

async def handle(request):
    logger.info(json.dumps({
        'ip': request.remote,
        'type': 'replication_request',
        'timestamp': datetime.utcnow().isoformat()
    }))
    return web.Response(
        body=encoded_q,
        headers={
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/octet-stream',
            'Server': 'Satoshi/1.0'
        }
    )

async def health(request):
    return web.Response(text='OK')

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/health', health)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    web.run_app(app, 
        host='0.0.0.0', 
        port=port,
        access_log_format='%t %a "%r" %s %b "%{User-Agent}i" %D'
    )
