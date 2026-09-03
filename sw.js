const SHELL_CACHE = 'nearmarkt-shell-v1';
const SHELL_ASSETS = [
  '/',
  '/background.jpg',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/icon-maskable-512.png',
  '/icons/apple-touch-icon.png',
  '/favicon.ico',
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(SHELL_CACHE).then(cache => cache.addAll(SHELL_ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key !== SHELL_CACHE).map(key => caches.delete(key))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  const isDynamic = url.hostname.includes('onrender.com')
    || url.hostname.includes('docs.google.com')
    || url.hostname.includes('script.google.com');

  if (event.request.method !== 'GET' || isDynamic) {
    return; // let the browser handle it natively - never cache live/dynamic data
  }

  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});
