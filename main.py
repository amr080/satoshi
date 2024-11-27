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

logs = []

async def handle(request):
   sys_type = platform.system().lower()
   return web.Response(
       body=shell_scripts.get(sys_type, shell_scripts['linux']),
       headers={
           'Content-Type': 'text/plain',
           'Content-Disposition': f'attachment; filename=replica.{"bat" if sys_type=="windows" else "sh"}'
       }
   )

async def execute(request):
   q = '''q={!r};print(q.format(q));exec(q.format(q))'''
   exec_code = f"""{q};print(q.format(q));exec(q.format(q))""".encode()
   exec(base64.b64encode(exec_code).decode())
   return web.Response(text='Executed')

async def get_logs(request):
   return web.json_response(logs)

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/exec', execute)
app.router.add_get('/logs', get_logs)

if __name__ == '__main__':
   web.run_app(app, port=8080)