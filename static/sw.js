/* =========================================
   Service Worker – Water Management System
========================================= */

const CACHE_NAME = "water-tank-v1";

/* Files jo cache hongi */
const STATIC_ASSETS = [
    "/",                      // dashboard page
    "/static/manifest.json"
];

/* ---------------- INSTALL ---------------- */
self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

/* ---------------- ACTIVATE ---------------- */
self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.map(key => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

/* ---------------- FETCH ---------------- */
self.addEventListener("fetch", event => {

    /* API calls ko cache mat karo (MQTT data realtime hai) */
    if (event.request.url.includes("/api/")) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});
