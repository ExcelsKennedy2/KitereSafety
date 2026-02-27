self.addEventListener("message", event => {
    if (event.data === "SKIP_WAITING") {
        self.skipWaiting();
    }
});

const CACHE_NAME = "kiteresafety-v1";
const urlsToCache = [
    "/",
    "/static/css/bootstrap.min.css",
    "/static/js/bootstrap.bundle.min.js",
];

self.addEventListener("install", event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});