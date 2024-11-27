# main.py
from aiohttp import web
import json
from datetime import datetime

standalone_code = b"""
#!/usr/bin/env python3
import os, subprocess, json
from datetime import datetime

# Auto-install dependencies
try:
   from aiohttp import web
except ImportError:
   subprocess.check_call(['pip', 'install', 'aiohttp'])
   from aiohttp import web

# In-memory logs
logs = []

async def handle(request):
   logs.append({
       'time': datetime.utcnow().isoformat(),
       'ip': request.remote,
       'type': 'replication'
   })
   return web.Response(
       body=PAYLOAD,
       headers={
           'Content-Type': 'text/x-python',
           'Content-Disposition': 'attachment; filename=replica.py'
       }
   )

async def health(request):
   return web.Response(text='OK')

async def get_logs(request):
   return web.json_response(logs)

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/health', health)
app.router.add_get('/logs', get_logs)

if __name__ == '__main__':
   port = 8080
   print(f'Replica server running on port {port}')
   web.run_app(app, port=port)
"""

# Track logs for main server
logs = []

async def handle(request):
   logs.append({
       'time': datetime.utcnow().isoformat(),
       'ip': request.remote,
       'type': 'replication'
   })
   payload = standalone_code.replace(b'PAYLOAD', repr(standalone_code).encode())
   return web.Response(
       body=payload,
       headers={
           'Content-Type': 'text/x-python',
           'Content-Disposition': 'attachment; filename=replica.py'
       }
   )

async def health(request):
   return web.Response(text='OK')

async def get_logs(request):
   return web.json_response(logs)

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/health', health)
app.router.add_get('/logs', get_logs)

if __name__ == '__main__':
   web.run_app(app, port=8080)