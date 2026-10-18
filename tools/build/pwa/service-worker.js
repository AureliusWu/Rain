/* Offline delivery layer for the official Ren'Py WebAssembly runtime. */
'use strict';
const BUILD = /* BUILD_CONFIG */;
const SCOPE = new URL('./', self.location.href);
const PREFIX = `rain-pwa:${SCOPE.pathname}:`;
const CACHE = PREFIX + BUILD.revision;
const MARKER = new URL('__rain_complete__', SCOPE).href;
const FILES = new Map(BUILD.files.map(file => [new URL(file.path, SCOPE).href, file]));
const TOTAL_BYTES = BUILD.files.reduce((sum, file) => sum + file.bytes, 0);
let progress = {completedFiles: 0, totalFiles: FILES.size, verifiedBytes: 0, totalBytes: TOTAL_BYTES, failed: false};
async function reportProgress() {
    const clients = await self.clients.matchAll({type: 'window', includeUncontrolled: true});
    for (const client of clients) {
        const url = new URL(client.url);
        if (url.origin === SCOPE.origin && url.pathname.startsWith(SCOPE.pathname))
            client.postMessage({type: 'RAIN_OFFLINE_PROGRESS', revision: BUILD.revision, ...progress});
    }
}
const hex = bytes => Array.from(new Uint8Array(bytes), byte => byte.toString(16).padStart(2, '0')).join('');

self.addEventListener('install', event => event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    if (!await cache.match(MARKER)) {
        progress = {...progress, completedFiles: 0, verifiedBytes: 0, failed: false};
        try {
            await reportProgress();
            for (const [url, file] of FILES) {
                const response = await fetch(new Request(url, {cache: 'reload', credentials: 'same-origin'}));
                if (!response.ok || response.type === 'opaque') throw new Error(`Cannot cache ${file.path}`);
                const bytes = await response.clone().arrayBuffer();
                if (bytes.byteLength !== file.bytes || hex(await crypto.subtle.digest('SHA-256', bytes)) !== file.sha256)
                    throw new Error(`Build changed while downloading ${file.path}`);
                await cache.put(url, response);
                progress.completedFiles++; progress.verifiedBytes += bytes.byteLength;
                await reportProgress();
            }
            await cache.put(MARKER, new Response(JSON.stringify({revision: BUILD.revision, files: FILES.size})));
        } catch (error) {
            await caches.delete(CACHE);
            progress.failed = true; await reportProgress();
            throw error;
        }
    }
    // Keep a running client on its complete old build. The new worker waits
    // until every old window closes, then activates this complete build.
})()));

self.addEventListener('activate', event => event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    if (!await cache.match(MARKER)) throw new Error('Incomplete offline build');
    for (const key of await caches.keys()) if (key.startsWith(PREFIX) && key !== CACHE) await caches.delete(key);
    await self.clients.claim();
})()));

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;
    const url = new URL(event.request.url);
    if (url.origin !== SCOPE.origin || !url.pathname.startsWith(SCOPE.pathname)) return;
    url.search = ''; url.hash = '';
    const path = url.href;
    const isEntry = url.pathname === SCOPE.pathname || event.request.mode === 'navigate';
    if (!FILES.has(path) && !isEntry) return;
    event.respondWith((async () => {
        const cache = await caches.open(CACHE);
        const cached = await cache.match(FILES.has(path) ? path : new URL('index.html', SCOPE).href);
        return cached || fetch(event.request);
    })());
});

self.addEventListener('message', event => {
    if (event.data?.type !== 'RAIN_OFFLINE_STATUS') return;
    event.waitUntil((async () => {
        const cache = await caches.open(CACHE);
        const ready = Boolean(await cache.match(MARKER));
        event.ports[0]?.postMessage({ready, revision: BUILD.revision, files: FILES.size, ...progress, ...(ready ? {completedFiles: FILES.size, verifiedBytes: TOTAL_BYTES, failed: false} : {})});
    })());
});
