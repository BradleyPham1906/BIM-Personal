/* exp.js -- EXPERIMENT ONLY (V172h, 2026-11-07): the helpers every experiment page loads (ES5).
   It never registers a worker by itself; the driver calls window.__register(). It logs the registration's
   events (updatefound, the new worker's states, controllerchange) with performance.now() times, and on
   controllerchange reloads the page once, unless window.__dirty (unsaved work) is true or __autoReload is false;
   the reload count is kept in sessionStorage so a reload loop would show as a growing count. */
(function () {
  var log = window.__log = [];
  function L(s) { log.push(Math.round(performance.now()) + ' ' + s); }
  window.__L = L;
  window.__dirty = false;
  var reloading = false;
  function reloads() { try { return +(sessionStorage.getItem('reloads') || 0); } catch (e) { return -1; } }
  if (!('serviceWorker' in navigator)) { L('no serviceWorker'); return; }
  L('controller at start: ' + (navigator.serviceWorker.controller ? 'yes' : 'no'));
  navigator.serviceWorker.addEventListener('controllerchange', function () {
    L('controllerchange');
    window.__ccCount = (window.__ccCount || 0) + 1;
    if (window.__autoReload === false) return;
    if (window.__dirty) { L('controllerchange while dirty: not reloading'); return; }
    if (reloading) return;
    reloading = true;
    try { sessionStorage.setItem('reloads', String(reloads() + 1)); } catch (e) {}
    location.reload();
  });
  function watch(reg) {
    if (reg.__watched) return;
    reg.__watched = true;
    L('registration seen: installing=' + !!reg.installing + ' waiting=' + !!reg.waiting + ' active=' + !!reg.active);
    reg.addEventListener('updatefound', function () {
      window.__updatefoundAt = performance.now();
      L('updatefound');
      var w = reg.installing;
      if (w) w.addEventListener('statechange', function () {
        L('new worker ' + w.state);
        if (w.state === 'installed') window.__installedAt = performance.now();
      });
    });
  }
  window.__register = function (url, opts) {
    return navigator.serviceWorker.register(url, opts || {}).then(function (reg) { watch(reg); return reg.scope; },
      function (e) { return 'ERR ' + e.name + ': ' + e.message; });
  };
  navigator.serviceWorker.getRegistration().then(function (reg) { if (reg) watch(reg); });
  window.__ask = function (w, msg) {
    return new Promise(function (res) {
      if (!w) { res(null); return; }
      var ch = new MessageChannel();
      ch.port1.onmessage = function (e) { res(e.data); };
      w.postMessage(msg, [ch.port2]);
      setTimeout(function () { res('timeout'); }, 3000);
    });
  };
  window.__state = function () {
    return navigator.serviceWorker.getRegistration().then(function (reg) {
      var c = navigator.serviceWorker.controller;
      return Promise.all([window.__ask(c, { type: 'VERSION' }), reg ? window.__ask(reg.active, { type: 'VERSION' }) : null,
        reg ? window.__ask(reg.waiting, { type: 'VERSION' }) : null]).then(function (v) {
        return { controller: v[0], active: v[1], waiting: v[2], installing: !!(reg && reg.installing), scope: reg ? reg.scope : null,
          updateViaCache: reg ? reg.updateViaCache : null, reloads: reloads(), cc: window.__ccCount || 0, log: log.slice() };
      });
    });
  };
  window.__applyUpdate = function () {
    if (window.__dirty) return Promise.resolve('held: unsaved work');
    return navigator.serviceWorker.getRegistration().then(function (reg) {
      if (!reg || !reg.waiting) return 'no waiting worker';
      reg.waiting.postMessage({ type: 'SKIP_WAITING' });
      return 'asked';
    });
  };
  window.__probe = function (from) {
    return fetch('/BIM-Personal/__probe?from=' + (from || 'page')).then(function (r) { return r.text(); }).then(function (t) {
      try { return JSON.parse(t); } catch (e) { return { viaSW: false, body: t.slice(0, 40) }; }
    }, function (e) { return 'ERR ' + e; });
  };
})();
