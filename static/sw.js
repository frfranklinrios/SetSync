// SetSync service worker — app-shell + offline fallback
// Bump CACHE_VERSION whenever the app shell changes so old caches are evicted.
const CACHE_VERSION = 'setsync-v1';
const STATIC_CACHE = CACHE_VERSION + '-static';
const RUNTIME_CACHE = CACHE_VERSION + '-runtime';

// App shell: small set of always-cached resources
const APP_SHELL = [
    '/static/style.css',
    '/static/logoSetSync.png',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/icons/apple-touch-icon.png',
    '/offline',
    '/manifest.webmanifest'
];

// ── INSTALL ──────────────────────────────────────────────
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(STATIC_CACHE).then((cache) =>
            // addAll fails atomically if any resource fails; use individual add to be resilient
            Promise.all(APP_SHELL.map((url) =>
                cache.add(new Request(url, { cache: 'reload' })).catch(() => null)
            ))
        ).then(() => self.skipWaiting())
    );
});

// ── ACTIVATE ─────────────────────────────────────────────
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys
                .filter((k) => k !== STATIC_CACHE && k !== RUNTIME_CACHE)
                .map((k) => caches.delete(k))
            )
        ).then(() => self.clients.claim())
    );
});

// ── FETCH ────────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = new URL(request.url);

    // Skip non-GET, cross-origin, auth flows, and anything that mutates state
    if (request.method !== 'GET') return;
    if (url.origin !== self.location.origin) return;
    if (url.pathname.startsWith('/auth/')) return;

    // Navigation (HTML page) → network-first, fallback to cache, then offline page
    if (request.mode === 'navigate' ||
        (request.headers.get('accept') || '').includes('text/html')) {
        event.respondWith(networkFirstHTML(request));
        return;
    }

    // Static assets → cache-first, populate runtime cache
    if (url.pathname.startsWith('/static/') ||
        url.pathname === '/manifest.webmanifest') {
        event.respondWith(cacheFirst(request));
        return;
    }

    // Everything else (API/JSON) → network, fall back to cache if available
    event.respondWith(networkFirstJSON(request));
});

async function networkFirstHTML(request) {
    try {
        const networkResp = await fetch(request);
        if (networkResp && networkResp.ok) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, networkResp.clone());
        }
        return networkResp;
    } catch (err) {
        const cached = await caches.match(request);
        if (cached) return cached;
        const offline = await caches.match('/offline');
        return offline || new Response('Offline', { status: 503, statusText: 'Offline' });
    }
}

async function cacheFirst(request) {
    const cached = await caches.match(request);
    if (cached) return cached;
    try {
        const resp = await fetch(request);
        if (resp && resp.ok) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, resp.clone());
        }
        return resp;
    } catch (err) {
        return new Response('', { status: 504, statusText: 'Offline asset' });
    }
}

async function networkFirstJSON(request) {
    try {
        const resp = await fetch(request);
        if (resp && resp.ok) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, resp.clone());
        }
        return resp;
    } catch (err) {
        const cached = await caches.match(request);
        if (cached) return cached;
        return new Response(JSON.stringify({ error: 'offline' }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

// Allow page to ask SW to update immediately
self.addEventListener('message', (event) => {
    if (event.data === 'skipWaiting') self.skipWaiting();
});
