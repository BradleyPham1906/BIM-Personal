/* sw-probe.template.js -- EXPERIMENT ONLY (V172h, 2026-11-07). A minimal ES5 service worker that answers
   requests for any path ending in /__probe itself, with a JSON body naming its VERSION, the request's
   destination and mode and the client it came from, so a page or a worker can tell whether a fetch went
   through this worker. With FETCH false it has no fetch handler at all (the install-prompt test).
   Every other request under its scope goes to the network through respondWith(fetch()) (counted per URL in
   SEEN, read back by a 'SEEN' message). VERSION changes the bytes of the file between builds A and B. */
var VERSION = /*@VERSION*/null;
var FETCH = /*@FETCH*/null;
var SEEN = [];

self.addEventListener('install', function () {});
self.addEventListener('activate', function () {});
self.addEventListener('message', function (e) {
  var d = e.data || {};
  if (d.type === 'SKIP_WAITING') self.skipWaiting();
  if (d.type === 'VERSION' && e.ports && e.ports[0]) e.ports[0].postMessage({ version: VERSION });
  if (d.type === 'SEEN' && e.ports && e.ports[0]) e.ports[0].postMessage({ seen: SEEN.slice() });
});
if (FETCH) {
  self.addEventListener('fetch', function (e) {
    var req = e.request, url = new URL(req.url);
    SEEN.push({ url: url.pathname + url.search, dest: req.destination, mode: req.mode, client: e.clientId || '', res: e.resultingClientId || '' });
    if (/\/__probe$/.test(url.pathname)) {
      var body = JSON.stringify({ viaSW: true, version: VERSION, dest: req.destination, mode: req.mode, q: url.search });
      var isScript = req.destination === 'script' || req.destination === 'worker' || url.search.indexOf('as=js') >= 0;
      e.respondWith(new Response(isScript ? 'self.__probeResult=' + body + ';' : body,
        { headers: { 'content-type': isScript ? 'application/javascript' : 'application/json' } }));
      return;
    }
    if (url.origin === self.location.origin) e.respondWith(fetch(req));
  });
}
