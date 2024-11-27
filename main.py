# main.py
from aiohttp import web
import zlib, json, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store logs in memory
logs = []

replication_code = b"""
#!/usr/bin/env python3
from aiohttp import web
import zlib, json
from datetime import datetime

logs = []

async def handle(request):
   logs.append({"time": datetime.utcnow().isoformat(), "ip": request.remote})
   return web.Response(body=PAYLOAD, headers={'Content-Type': 'application/python'})

async def health(request):
   return web.Response(text="OK")

async def get_logs(request):
   return web.json_response(logs)

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/health', health) 
app.router.add_get('/logs', get_logs)

if __name__ == '__main__':
   web.run_app(app, port=8080)
"""

async def handle(request):
   logs.append({"time": datetime.utcnow().isoformat(), "ip": request.remote})
   payload = replication_code.replace(b'PAYLOAD', repr(replication_code).encode())
   return web.Response(body=payload, headers={'Content-Type': 'application/python'})

async def health(request):
   return web.Response(text="OK")

async def get_logs(request):
   return web.json_response(logs)

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/health', health)
app.router.add_get('/logs', get_logs)

if __name__ == '__main__':
   web.run_app(app, port=8080)