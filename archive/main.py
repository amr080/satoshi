# main.py
from aiohttp import web
import json, base64
from datetime import datetime

standalone_code = b"""
#!/usr/bin/env python3
# Auto-executing replica server
import os, subprocess, json, base64
from datetime import datetime

# Auto-install & import
try:
   from aiohttp import web
except ImportError:
   subprocess.check_call(['pip', 'install', 'aiohttp'])
   from aiohttp import web

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

async def execute(request):
   code = base64.b64decode(EXEC_PAYLOAD)
   exec(code)
   return web.Response(text='Executed')

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/health', health)
app.router.add_get('/logs', get_logs)
app.router.add_get('/exec', execute)

if __name__ == '__main__':
   os.chmod(__file__, 0o755)  # Make executable
   port = 8080
   print(f'Replica active on port {port}')
   web.run_app(app, port=port)
"""

exec_code = b"""
print("Replica activated")
"""

logs = []

async def handle(request):
   logs.append({
       'time': datetime.utcnow().isoformat(),
       'ip': request.remote,
       'type': 'replication'
   })
   payload = standalone_code.replace(b'PAYLOAD', repr(standalone_code).encode())
   payload = payload.replace(b'EXEC_PAYLOAD', repr(base64.b64encode(exec_code)).encode())
   return web.Response(
       body=payload,
       headers={
           'Content-Type': 'text/x-python',
           'Content-Disposition': 'attachment; filename=replica.py'
       }
   )

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/health', lambda r: web.Response(text='OK'))
app.router.add_get('/logs', lambda r: web.json_response(logs))

if __name__ == '__main__':
   web.run_app(app, port=8080)