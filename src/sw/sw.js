/* ================= __acad3dV172h: the app's service worker (installable and offline) =================
   docs/research/research-local-storage.md, part 15 (option C; the owner's Q1-Q7, 2026-11-08). tools/build_pwa.py writes
   this file into the Pages site as sw.js, with the three values below filled in for the build, so every build's sw.js
   is byte-different and reaches its users (the browser checks sw.js at every visit, H46). ES5, no dependency.
   - The page and its four bundles come from one precache made when this worker installs, so a tab never runs a page of
     one build with the bundles of another (part 15.4). The bundles are cached by their exact ?v= addresses (H42).
   - The Ladybug runtime is cached the first time an analysis fetches it, in a cache of its own kept across builds
     (Q3); its wheels are still checked by SHA-256 in the Ladybug worker.
   - Everything else (the guide, the one-file build, other sites: tiles may not be cached, H52) goes to the network.
   - A new build waits until the page says no tab has unsaved work (Q1, Q4): it takes over only on a 'skip' message. */
var BIM_SW_BUILD = 'dev';
var BIM_SW_SHELL = [];
var BIM_SW_RUNTIME = 'none';
var BIM_SW_PREFIX = 'BIM-Personal/';
var BIM_SW_APP = BIM_SW_PREFIX + 'app/' + BIM_SW_BUILD;
var BIM_SW_RT = BIM_SW_PREFIX + 'runtime/' + BIM_SW_RUNTIME;

/* which of the worker's caches answers a request: 'page', 'app', 'runtime', or null for the network */
function bimSwRoute(url, scope, method, mode) {
  if (method !== 'GET' || typeof url !== 'string' || url.indexOf(scope) !== 0) return null;
  var path = url.slice(scope.length).replace(/[?#].*$/, '');
  if (mode === 'navigate') return (path === '' || path === 'index.html') ? 'page' : null;
  if (/^app\/[^\/]+$/.test(path)) return 'app';
  if (/^runtime\//.test(path)) return 'runtime';
  return null;
}
/* an answer worth keeping: a whole 2xx, and never an HTML page for a script or a stylesheet (draw.io's guard) */
function bimSwUsable(res, url) {
  if (!res || !res.ok || res.status === 206 || res.type === 'opaque') return false;
  if (/\.(js|css)(\?|$)/.test(String(url))) {
    var ct = String((res.headers && res.headers.get('content-type')) || '');
    if (/text\/html/i.test(ct)) return false;
  }
  return true;
}
/* the page must name exactly the bundles this worker caches, or the cache would hold two builds */
function bimSwPageMatches(html, shell) {
  for (var i = 0; i < shell.length; i++) {
    if (shell[i] !== 'index.html' && String(html).indexOf(shell[i]) < 0) return false;
  }
  return true;
}

if (typeof self !== 'undefined' && self.addEventListener && typeof caches !== 'undefined') {
  self.addEventListener('install', function (ev) {
    ev.waitUntil(caches.open(BIM_SW_APP).then(function (c) {
      return Promise.all(BIM_SW_SHELL.map(function (u) {
        /* the page is asked past the HTTP cache (Pages keeps it 600 s); the bundles' addresses are their content */
        return fetch(new Request(u, { cache: u === 'index.html' ? 'no-cache' : 'default' })).then(function (res) {
          if (!bimSwUsable(res, u)) throw new Error('[BIM] ' + u + ' answered ' + res.status + ': not cached');
          if (u !== 'index.html') return c.put(u, res);
          return res.clone().text().then(function (html) {
            if (!bimSwPageMatches(html, BIM_SW_SHELL)) throw new Error('[BIM] index.html is not this build\'s page: not cached');
            return c.put(u, res);
          });
        });
      }));
    }));
  });
  self.addEventListener('activate', function (ev) {
    ev.waitUntil(caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) {
        if (k.indexOf(BIM_SW_PREFIX + 'app/') === 0) return k !== BIM_SW_APP;
        if (k.indexOf(BIM_SW_PREFIX + 'runtime/') === 0) return k !== BIM_SW_RT;
        return false;   /* another Pages project's caches share this origin (H48): never ours to delete */
      }).map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); }));
  });
  self.addEventListener('fetch', function (ev) {
    var r = ev.request, scope = self.registration.scope, kind = bimSwRoute(r.url, scope, r.method, r.mode);
    if (!kind) return;
    if (kind === 'page' || kind === 'app') {
      ev.respondWith(caches.open(BIM_SW_APP).then(function (c) {
        return c.match(kind === 'page' ? scope + 'index.html' : r);
      }).then(function (hit) { return hit || fetch(r); }, function () { return fetch(r); }));
      return;
    }
    ev.respondWith(caches.open(BIM_SW_RT).then(function (c) {
      return c.match(r).then(function (hit) {
        if (hit) return hit;
        return fetch(r).then(function (res) {
          if (bimSwUsable(res, r.url)) c.put(r, res.clone()).then(null, function () {});
          return res;
        });
      });
    }, function () { return fetch(r); }));
  });
  self.addEventListener('message', function (ev) {
    if (ev.data && ev.data.t === 'skip') self.skipWaiting();
  });
}
