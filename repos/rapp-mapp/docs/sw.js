// RAPPDEX service worker.
//
// A dex you can only read with signal is not a dex you carry. Everything is
// precached on install, so it opens on a plane, in a basement, or on a phone
// with no bars — which is the whole point of it being installable.
const CACHE = 'rappdex-v2';
const SHELL = ['./', './index.html', './mapp.json', './manifest.webmanifest', './icon-192.png', './icon-512.png'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  // Drop old versions so a stale dex never outlives a deploy.
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  // Network-first so a fresh map wins when there is signal; cache is the
  // fallback, never the default, so the dex is current whenever it can be.
  event.respondWith(
    fetch(event.request)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(event.request, copy));
        return res;
      })
      .catch(() => caches.match(event.request).then((hit) => hit || caches.match('./index.html'))),
  );
});
