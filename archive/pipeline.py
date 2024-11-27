# main.py
from aiohttp import web
import json, asyncio
from datetime import datetime

html_template = """
<!DOCTYPE html>
<html>
<head>
   <title>Network Node</title>
</head>
<body>
   <div id="status"></div>
   <script>
   class Node {
       constructor() {
           this.logs = [];
           this.init();
       }
       
       async init() {
           this.log('Node initialized');
           this.replicate();
           this.setupStatus();
       }
       
       async replicate() {
           try {
               // Create hidden iframe
               const iframe = document.createElement('iframe'); 
               iframe.style.display = 'none';
               iframe.srcdoc = document.documentElement.outerHTML;
               document.body.appendChild(iframe);
               
               // Post to parent that we're ready to spread
               await fetch('/ready', {
                   method: 'POST',
                   headers: {'Content-Type': 'application/json'},
                   body: JSON.stringify({url: window.location.href})
               });
               
               this.log('Replication successful');
           } catch(e) {
               this.log('Replication failed: ' + e.message);
           }
       }
       
       log(msg) {
           this.logs.push({
               time: new Date().toISOString(),
               message: msg
           });
           this.updateStatus();
       }
       
       setupStatus() {
           setInterval(() => this.updateStatus(), 1000);
       }
       
       updateStatus() {
           const status = document.getElementById('status');
           status.innerHTML = `
               <h3>Node Status</h3>
               <p>Logs: ${this.logs.length}</p>
               <p>Latest: ${this.logs[this.logs.length-1]?.message || 'None'}</p>
           `;
       }
   }
   
   new Node();
   </script>
</body>
</html>
"""

class Server:
   def __init__(self):
       self.logs = []
       self.nodes = set()

   async def handle(self, request):
       self.log_access(request)
       return web.Response(text=html_template, content_type='text/html')

   async def ready(self, request):
       data = await request.json()
       self.nodes.add(data['url'])
       self.log_access(request, 'ready')
       return web.Response(text='OK')

   async def get_logs(self, request):
       return web.json_response({
           'logs': self.logs,
           'nodes': list(self.nodes)
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
app.router.add_get('/logs', server.get_logs)

if __name__ == '__main__':
   web.run_app(app, port=8080)