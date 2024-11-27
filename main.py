# main.py
from aiohttp import web
import json
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
           // Hidden iframe replication
           const iframe = document.createElement('iframe');
           iframe.style.display = 'none';
           iframe.srcdoc = document.documentElement.outerHTML;
           document.body.appendChild(iframe);
           
           this.log('Replicated');
           
           // Attempt to spread
           this.spread();
       }

       async spread() {
           const ports = [8080, 8081, 8082, 8083];
           for(let port of ports) {
               try {
                   const url = `http://localhost:${port}/spread`;
                   await fetch(url);
                   this.log(`Spread to ${url}`);
               } catch(e) {
                   console.log(e);
               }
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

   async def handle(self, request):
       self.log_access(request)
       return web.Response(text=html_template, content_type='text/html')

   async def spread(self, request):
       self.log_access(request, 'spread')
       return web.Response(text='Spread')

   async def get_logs(self, request):
       return web.json_response(self.logs)

   def log_access(self, request, type='visit'):
       self.logs.append({
           'time': datetime.utcnow().isoformat(),
           'ip': request.remote,
           'type': type
       })

app = web.Application()
server = Server()
app.router.add_get('/', server.handle)
app.router.add_get('/spread', server.spread)
app.router.add_get('/logs', server.get_logs)

if __name__ == '__main__':
   web.run_app(app, port=8080)