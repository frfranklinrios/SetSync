// SetSync service worker — app-shell + offline fallback
// Bump CACHE_VERSION whenever the app shell changes so old caches are evicted.
const CACHE_VERSION = 'setsync-v9';
const STATIC_CACHE = CACHE_VERSION + '-static';
const RUNTIME_CACHE = CACHE_VERSION + '-runtime';

const APP_SHELL = [
    '/static/logoSetSync.png',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/icons/apple-touch-icon.png',
    '/static/js/theme.js',
    '/offline',
    '/manifest.webmanifest'
];

const NO_CACHE_PATHS = ['/auth/', '/sw.js'];

function shouldSkip(request, url) {
    if (request.method !== 'GET') return true;
    if (url.origin !== self.location.origin) return true;
    for (const p of NO_CACHE_PATHS) {
        if (url.pathname.startsWith(p)) return true;
    }
    return false;
}

function isNavigation(request) {
    return request.mode === 'navigate'
        || (request.headers.get('accept') || '').includes('text/html');
}

function isCacheableResponse(response) {
    if (!response || !response.ok) return false;
    if (response.type === 'opaqueredirect') return false;
    if (response.redirected) return false;
    return true;
}

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(STATIC_CACHE).then((cache) =>
            Promise.all(APP_SHELL.map((url) =>
                cache.add(new Request(url, { cache: 'reload' })).catch(() => null)
            ))
        ).then(() => self.skipWaiting())
    );
});

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

self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = new URL(request.url);
    if (shouldSkip(request, url)) return;

    if (isNavigation(request)) {
        event.respondWith(networkFirstHTML(request));
        return;
    }

    if (url.pathname.startsWith('/static/') || url.pathname === '/manifest.webmanifest') {
        event.respondWith(cacheFirst(request));
        return;
    }

    event.respondWith(networkFirstJSON(request));
});

async function networkFirstHTML(request) {
    try {
        const networkResp = await fetch(request);
        if (isCacheableResponse(networkResp)) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, networkResp.clone());
        }
        return networkResp;
    } catch (err) {
        const cached = await caches.match(request);
        if (cached) return cached;
        const offline = await caches.match('/offline');
        return offline || new Response('Offline', {
            status: 503,
            statusText: 'Offline',
            headers: { 'Content-Type': 'text/plain; charset=utf-8' }
        });
    }
}

async function cacheFirst(request) {
    const cached = await caches.match(request);
    if (cached) return cached;
    try {
        const resp = await fetch(request);
        if (isCacheableResponse(resp)) {
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
        if (isCacheableResponse(resp)) {
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

self.addEventListener('message', (event) => {
    if (event.data === 'skipWaiting') self.skipWaiting();
});
