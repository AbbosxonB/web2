const CACHE_NAME = 'unitest-v1';
const ASSETS = [
    '/',
    '/static/css/styles.css',
    '/static/img/logo.png'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS).catch(err => {
                console.error('Failed to cache assets:', err);
            });
        })
    );
});

self.addEventListener('fetch', (event) => {
    // For API requests, Network First, then specific handling
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request).catch(() => {
                return new Response(JSON.stringify({ error: 'Internet yo\'q' }), {
                    headers: { 'Content-Type': 'application/json' }
                });
            })
        );
        return;
    }

    // For other requests (HTML, CSS, JS), Stale-While-Revalidate or Network First
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(keys.map((key) => {
                if (key !== CACHE_NAME) {
                    return caches.delete(key);
                }
            }));
        })
    );
});
