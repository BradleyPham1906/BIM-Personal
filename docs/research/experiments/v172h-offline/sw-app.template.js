/* sw-app.template.js -- EXPERIMENT ONLY (V172h, 2026-11-07); not the app's worker and never deployed.
   A minimal hand-written ES5 service worker for the built app at /BIM-Personal/, made per build by _server.js
   (fromTemplate): each placeholder below is replaced by JSON when the server serves /BIM-Personal/sw.js.
   - install: precaches the page ('./') and the build's four `app/<name>?v=<hash>` files by their exact URLs,
     fetched with cache: 'reload' (past the HTTP cache), into the cache 'bim-app-<BUILD>'; records bytes and time
     in the cache 'bim-exp-meta' so the driver can read them; no skipWaiting unless SKIP is true or a page asks.
   - activate: deletes every 'bim-app-*' cache but its own; claims clients only if CLAIM is true.
   - fetch: GET requests of this origin under the scope only. Navigations: network first, then the precached page
     (the cache is not updated from the network, so the page and its four files always come from one build).
     runtime/: cache first, filled on first use, into 'bim-runtime-v1'. Everything else: the build's cache, then
     the network. Cross-origin requests are not touched (no respondWith), so they go to the network as without
     a worker. */
var BUILD = /*@BUILD*/null;
var PRECACHE = /*@PRECACHE*/null;
var SKIP = /*@SKIP*/null;
var CLAIM = /*@CLAIM*/null;
var APP_CACHE = 'bim-app-' + BUILD;
var RT_CACHE = 'bim-runtime-v1';

self.addEventListener('install', function (e) {
  var t0 = Date.now(), bytes = 0;
  e.waitUntil(caches.open(APP_CACHE).then(function (c) {
    return Promise.all(PRECACHE.map(function (u) {
      return fetch(new Request(u, { cache: 'reload' })).then(function (r) {
        if (!r.ok) throw new Error(u + ': HTTP ' + r.status);
        return r.clone().arrayBuffer().then(function (b) { bytes += b.byteLength; return c.put(u, r); });
      });
    }));
  }).then(function () {
    var stats = { build: BUILD, files: PRECACHE.length, bytes: bytes, ms: Date.now() - t0 };
    return caches.open('bim-exp-meta').then(function (m) {
      return m.put('install-' + BUILD, new Response(JSON.stringify(stats), { headers: { 'content-type': 'application/json' } }));
    });
  }).then(function () { if (SKIP) return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf('bim-app-') === 0 && k !== APP_CACHE; })
      .map(function (k) { return caches['delete'](k); }));
  }).then(function () { if (CLAIM) return self.clients.claim(); }));
});

self.addEventListener('message', function (e) {
  var d = e.data || {};
  if (d.type === 'SKIP_WAITING') self.skipWaiting();
  if (d.type === 'VERSION' && e.ports && e.ports[0]) e.ports[0].postMessage({ build: BUILD });
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  var scope = new URL(self.registration.scope).pathname;
  if (url.pathname.indexOf(scope) !== 0) return;
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).catch(function () {
      return caches.open(APP_CACHE).then(function (c) {
        return c.match(req, { ignoreSearch: true }).then(function (r) { return r || c.match('./'); });
      }).then(function (r) { return r || Response.error(); });
    }));
    return;
  }
  if (url.pathname.indexOf(scope + 'runtime/') === 0) {
    e.respondWith(caches.open(RT_CACHE).then(function (c) {
      return c.match(req).then(function (hit) {
        if (hit) return hit;
        return fetch(req).then(function (r) { if (r.ok) e.waitUntil(c.put(req, r.clone())); return r; });
      });
    }));
    return;
  }
  e.respondWith(caches.open(APP_CACHE).then(function (c) {
    return c.match(req).then(function (hit) { return hit || fetch(req); });
  }));
});
