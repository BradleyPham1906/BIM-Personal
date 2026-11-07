// e02_precache.js -- H31, H37 and the precache's cost (V172h, 2026-11-07).
// H31: the build's four `app/<name>?v=<hash>` URLs are precached by their exact URLs; cache.match finds them
//      with the query, not without it (unless ignoreSearch); a new build's worker deletes the old build's cache
//      on activate and keeps the runtime cache.
// H37: navigator.storage.estimate() (and usageDetails) before the worker, after the precache, after the 16 MB
//      runtime is fetched through the worker, and after an IndexedDB write: caches and IndexedDB in one usage.
// Cost: bytes and time of the precache on a first visit (from the worker's own count), server bytes.
// Each run: a fresh persistent profile (a temporary user-data-dir, so storage is on disk as for a real user).
'use strict';
var C = require('./_common.js');
var pw = require('playwright');
var fs = require('fs'), path = require('path'), os = require('os');
var RUNS = +process.env.RUNS || 3;

var RT = ['MANIFEST.json', 'pyodide/0.29.5/pyodide.js', 'pyodide/0.29.5/pyodide.asm.js', 'pyodide/0.29.5/pyodide.asm.wasm',
  'pyodide/0.29.5/python_stdlib.zip', 'pyodide/0.29.5/pyodide-lock.json',
  'pyodide/0.29.5/numpy-2.2.5-cp313-cp313-pyemscripten_2025_0_wasm32.whl', 'wheels/ladybug_geometry-1.35.7-py3-none-any.whl',
  'wheels/ladybug_core-0.44.63-py3-none-any.whl', 'wheels/ladybug_comfort-0.19.13-py3-none-any.whl',
  'wheels/click-8.3.3-py3-none-any.whl', 'wheels/ladybug_radiance-0.2.12-py3-none-any.whl', 'radiance/gendaymtx.wasm'];

function est(p) {
  return p.evaluate(function () {
    return navigator.storage.estimate().then(function (e) { return { usage: e.usage, quota: e.quota, details: e.usageDetails || null }; });
  });
}

(async function () {
  var A = C.buildA(), B = C.buildB();
  var S = await C.serve({ build: A });
  var idA = C.buildId(A), idB = C.buildId(B);
  var out = { chromium: null, buildA: idA, buildB: idB, urlsA: C.srv.appUrls(A), runs: [] };
  for (var r = 0; r < RUNS; r++) {
    S.setBuild(A);
    S.override('/BIM-Personal/sw.js', { body: C.appSw(A) });
    var dir = (fs.mkdirSync(path.join(C.SCRATCH, 'profiles'), { recursive: true }), fs.mkdtempSync(path.join(C.SCRATCH, 'profiles', 'e02-')));
    var ctx = await pw.chromium.launchPersistentContext(dir);
    out.chromium = ctx.browser() ? ctx.browser().version() : out.chromium;
    var p = ctx.pages()[0] || await ctx.newPage();
    var run = {};
    S.resetHits();
    await p.goto(S.origin + '/BIM-Personal/');
    run.boot = await C.appReady(p);
    await C.sleep(1500);
    run.est0 = await est(p);
    var b0 = S.bytesOut;
    var t0 = Date.now();
    run.reg = await p.evaluate(function () { return window.navigator.serviceWorker.register('sw.js').then(function (g) { return g.scope; }); });
    await p.evaluate(function () { return navigator.serviceWorker.ready.then(function () { return 1; }); });
    run.readyMs = Date.now() - t0;
    run.serverBytesDuringInstall = S.bytesOut - b0;
    run.install = await p.evaluate(function (id) {
      return caches.open('bim-exp-meta').then(function (m) { return m.match('install-' + id); }).then(function (x) { return x ? x.json() : null; });
    }, idA);
    run.keys = await p.evaluate(function () { return caches.keys(); });
    run.match = await p.evaluate(function (a) {
      return caches.open('bim-app-' + a.id).then(function (c) {
        return c.keys().then(function (ks) {
          var u = a.urls[3], bare = u.split('?')[0];
          return Promise.all([c.match(u), c.match(bare), c.match(bare, { ignoreSearch: true }), c.match(u.replace(/v=[0-9a-f]+/, 'v=000000000000')),
            caches.match(u)]).then(function (m) {
            return { entries: ks.map(function (k) { return k.url.replace(location.origin, ''); }), withQuery: !!m[0], withoutQuery: !!m[1],
              withoutQueryIgnoreSearch: !!m[2], otherHash: !!m[3], cachesMatchTopLevel: !!m[4] };
          });
        });
      });
    }, { id: idA, urls: out.urlsA });
    await C.sleep(500);
    run.est1 = await est(p);
    // the 16 MB runtime through the worker: the page must be controlled, so reload first (no clients.claim)
    await p.reload();
    await C.appReady(p);
    run.controlledAfterReload = await p.evaluate(function () { return !!navigator.serviceWorker.controller; });
    var t1 = Date.now();
    run.runtimeBytes = await p.evaluate(function (files) {
      return Promise.all(files.map(function (f) {
        return fetch('runtime/' + f).then(function (x) { return x.arrayBuffer(); }).then(function (b) { return b.byteLength; });
      })).then(function (a) { return a.reduce(function (s, x) { return s + x; }, 0); });
    }, RT);
    run.runtimeFetchMs = Date.now() - t1;
    await C.sleep(1500);
    run.runtimeCached = await p.evaluate(function () { return caches.open('bim-runtime-v1').then(function (c) { return c.keys(); }).then(function (k) { return k.length; }); });
    run.est2 = await est(p);
    // a 10 MB IndexedDB value in the same origin, to see both counted in one usage
    await p.evaluate(function () {
      return new Promise(function (res) {
        var o = indexedDB.open('v172h-e02', 1);
        o.onupgradeneeded = function () { o.result.createObjectStore('s'); };
        o.onsuccess = function () {
          var tx = o.result.transaction('s', 'readwrite'), a = new Uint8Array(10 * 1024 * 1024);
          for (var i = 0; i < a.length; i += 4096) a[i] = (i * 7) & 255;
          tx.objectStore('s').put(a.buffer, 'k'); tx.oncomplete = function () { o.result.close(); res(1); };
        };
      });
    });
    await C.sleep(500);
    run.est3 = await est(p);
    // build B: its worker activates (skipWaiting for this test) and deletes the old build's cache, not the runtime's
    S.setBuild(B);
    S.override('/BIM-Personal/sw.js', { body: C.appSw(B, { skip: true }) });
    run.updateTo = idB;
    await p.evaluate(function () { return navigator.serviceWorker.getRegistration().then(function (g) { return g.update(); }); });
    var t2 = Date.now(), keysB = null;
    while (Date.now() - t2 < 15000) {
      keysB = await p.evaluate(function () { return caches.keys(); });
      if (keysB.indexOf('bim-app-' + idA) < 0 && keysB.indexOf('bim-app-' + idB) >= 0) break;
      await C.sleep(100);
    }
    run.keysAfterB = keysB;
    run.oldDeletedMs = Date.now() - t2;
    run.est4 = await est(p);
    out.runs.push(run);
    await ctx.close();
    fs.rmSync(dir, { recursive: true, force: true });
    console.log('run ' + r + ': install ' + JSON.stringify(run.install) + ' ready ' + run.readyMs + ' ms; usage ' +
      [run.est0.usage, run.est1.usage, run.est2.usage, run.est3.usage, run.est4.usage].join(' / '));
  }
  await S.stop();
  C.save('e02_precache', out);
  console.log(JSON.stringify(out.runs[0].match, null, 1), JSON.stringify(out.runs[0].keysAfterB));
  console.log(JSON.stringify([out.runs[0].est1.details, out.runs[0].est2.details, out.runs[0].est3.details, out.runs[0].est4.details]));
})().catch(function (e) { console.error(e); process.exit(1); });
