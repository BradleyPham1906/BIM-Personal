/* ================= __acad3dV172h: the way back (the owner's Q7) =================
   A service worker that removes itself. Kept ready, never published unless the app's worker misbehaves: then
   `python3 tools/build_site.py` with BIM_SW_REMOVE=1 in the environment publishes this file as sw.js. Every browser
   that has the app's worker fetches sw.js at its next visit (H46), installs this one, which takes over at once, deletes
   the app's caches (only those named BIM-Personal/, never another Pages project's), unregisters, and reloads the app's
   open tabs from the network. Excalidraw and tldraw keep a file like this (part 15.3). ES5. */
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (ev) {
  ev.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf('BIM-Personal/') === 0; })
      .map(function (k) { return caches.delete(k); }));
  }).then(function () {
    return self.registration.unregister();
  }).then(function () {
    return self.clients.matchAll({ type: 'window' });
  }).then(function (list) {
    list.forEach(function (c) { if (c.navigate) c.navigate(c.url); });
  }));
});
