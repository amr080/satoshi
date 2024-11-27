# main.py
from aiohttp import web
import json, base64, platform
from datetime import datetime

# HTML template with proper JavaScript
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Replica</title>
</head>
<body>
    <script>
    async function replicate() {
        const response = await fetch('/exec');
        const code = await response.text();
        const cleaned = code.replace(/[!r]/g, '');  // Clean syntax
        new Function(cleaned)();  // Safer than eval
    }
    replicate();
    </script>
</body>
</html>
"""

logs = []

async def handle(request):
    logs.append({'time': datetime.utcnow().isoformat(), 'ip': request.remote})
    return web.Response(text=html_template, content_type='text/html')

async def execute(request):
    replication_code = """
    console.log('Replicating...');
    // Your replication logic here
    const newWindow = window.open('', '_blank');
    newWindow.document.write(document.documentElement.outerHTML);
    """
    return web.Response(text=replication_code, content_type='application/javascript')

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/exec', execute)
app.router.add_get('/logs', lambda r: web.json_response(logs))

if __name__ == '__main__':
    web.run_app(app, port=8080)