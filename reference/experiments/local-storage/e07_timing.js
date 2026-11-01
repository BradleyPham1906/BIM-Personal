// e07_timing.js -- Hypothesis 7 (2026-10-31).
// Tests: how long localStorage.setItem / getItem of a ~4 MB JSON string blocks the main thread,
// against IndexedDB put / get of the same string and of 4 MB and 40 MB ArrayBuffers; and how
// long JSON.stringify (and JSON.parse) of a realistic ~4 MB CAD-like object takes.
// All times are measured in the page with performance.now(). For the synchronous calls
// (stringify, parse, setItem, getItem) the call's duration IS the main-thread block. For
// IndexedDB, three numbers: the synchronous put()/get() call itself (structured clone happens
// here for put), the time to oncomplete / onsuccess, and the longest gap seen by a
// MessageChannel ticker running during the operation (the main thread's longest stall).
// localStorage getItem is measured warm (same page, just written), after a page reload, and
// cold: the first getItem after the browser is closed and relaunched on the same profile, when
// Chromium has to load the origin's whole storage area from disk. The CAD-like object: 4,600
// elements, each with an id, type, layer, a property bag and a vertex array of doubles.
// 5 runs, each on a new persistent profile (launchPersistentContext, temporary user-data-dir).
'use strict';
var pw = require('playwright');
var L = require('./_lib');

function buildAndMeasure() {
  // ---- the realistic object ----
  function model() {
    var els = [], types = ['wall', 'slab', 'column', 'beam', 'door', 'window', 'roof'], i, j;
    var seed = 7;
    function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
    for (i = 0; i < 4600; i++) {
      var v = [];
      for (j = 0; j < 96; j++) v.push(Math.round(rnd() * 100000) / 1000);
      els.push({ id: 'el-' + i, type: types[i % types.length], layer: 'L' + (i % 12), level: i % 5,
        props: { material: 'concrete-c30', fireRating: 'REI ' + (60 + i % 3 * 30), thickness: 0.2 + (i % 4) * 0.05, name: 'Element ' + i, tags: ['a', 'b'] },
        verts: v, faces: [0, 1, 2, 2, 3, 0, 4, 5, 6, 6, 7, 4] });
    }
    return { version: 170, units: 'm', site: { lat: 40.0, lon: -75.1 }, elements: els };
  }
  function ticker() {
    var ch = new MessageChannel(), last = performance.now(), maxGap = 0, on = true;
    ch.port1.onmessage = function () { var t = performance.now(); if (t - last > maxGap) maxGap = t - last; last = t; if (on) ch.port2.postMessage(0); };
    ch.port2.postMessage(0);
    return { stop: function () { on = false; var t = performance.now(); if (t - last > maxGap) maxGap = t - last; return maxGap; } };
  }
  function openDb() { return new Promise(function (res) { var rq = indexedDB.open('e07', 1); rq.onupgradeneeded = function () { rq.result.createObjectStore('s'); }; rq.onsuccess = function () { res(rq.result); }; }); }
  function idbPut(db, key, val) {
    return new Promise(function (res) {
      var tk = ticker(), t0 = performance.now();
      var tx = db.transaction('s', 'readwrite');
      tx.objectStore('s').put(val, key);
      var tCall = performance.now() - t0;
      tx.oncomplete = function () { res({ callMs: tCall, completeMs: performance.now() - t0, maxGapMs: tk.stop() }); };
    });
  }
  function idbGet(db, key) {
    return new Promise(function (res) {
      var tk = ticker(), t0 = performance.now();
      var rq = db.transaction('s').objectStore('s').get(key);
      var tCall = performance.now() - t0;
      rq.onsuccess = function () { var t = performance.now() - t0; res({ callMs: tCall, successMs: t, maxGapMs: tk.stop(), len: rq.result.byteLength || rq.result.length }); };
    });
  }
  var out = {}, t0, m = model();
  t0 = performance.now(); var s = JSON.stringify(m); out.stringifyMs = performance.now() - t0;
  out.jsonChars = s.length;
  t0 = performance.now(); JSON.parse(s); out.parseMs = performance.now() - t0;
  localStorage.clear();
  t0 = performance.now(); localStorage.setItem('model', s); out.lsSetMs = performance.now() - t0;
  t0 = performance.now(); var back = localStorage.getItem('model'); out.lsGetWarmMs = performance.now() - t0;
  out.lsRoundTripEqual = back === s;
  var ab4 = new Uint8Array(4e6), ab40 = new Uint8Array(40e6), k;
  for (k = 0; k < ab4.length; k++) ab4[k] = k * 31 & 255;
  for (k = 0; k < ab40.length; k++) ab40[k] = k * 17 & 255;
  var db;
  return openDb().then(function (d) { db = d; return idbPut(db, 'str', s); })
    .then(function (r) { out.idbPutStr = r; return idbGet(db, 'str'); })
    .then(function (r) { out.idbGetStr = r; return idbPut(db, 'ab4', ab4.buffer); })
    .then(function (r) { out.idbPutAb4 = r; return idbGet(db, 'ab4'); })
    .then(function (r) { out.idbGetAb4 = r; return idbPut(db, 'ab40', ab40.buffer); })
    .then(function (r) { out.idbPutAb40 = r; return idbGet(db, 'ab40'); })
    .then(function (r) { out.idbGetAb40 = r; db.close(); return out; });
}

function coldGet() {
  var t0 = performance.now(); var v = localStorage.getItem('model'); var t = performance.now() - t0;
  return { lsGetColdMs: t, len: v ? v.length : 0 };
}

(async function () {
  var srv = await L.startServer(47318);
  var out = { headless: true, runs: [] };
  for (var run = 0; run < 5; run++) {
    var dir = L.tmpDir('e07-');
    var ctx = await pw.chromium.launchPersistentContext(dir);
    out.version = ctx.browser().version();
    var page = ctx.pages()[0] || await ctx.newPage();
    await page.goto(srv.origin + '/');
    var r = await page.evaluate(buildAndMeasure);
    await page.reload();
    r.lsGetAfterReloadMs = (await page.evaluate(coldGet)).lsGetColdMs;
    await ctx.close();
    var ctx2 = await pw.chromium.launchPersistentContext(dir);
    var page2 = ctx2.pages()[0] || await ctx2.newPage();
    await page2.goto(srv.origin + '/');
    Object.assign(r, await page2.evaluate(coldGet));
    await ctx2.close(); L.rm(dir);
    r.run = run; out.runs.push(r); console.log(JSON.stringify(r));
  }
  function col(f) { return L.stats(out.runs.map(f)); }
  out.summary = {
    jsonChars: col(function (r) { return r.jsonChars; }),
    stringifyMs: col(function (r) { return r.stringifyMs; }), parseMs: col(function (r) { return r.parseMs; }),
    lsSetMs: col(function (r) { return r.lsSetMs; }), lsGetWarmMs: col(function (r) { return r.lsGetWarmMs; }), lsGetAfterReloadMs: col(function (r) { return r.lsGetAfterReloadMs; }), lsGetColdMs: col(function (r) { return r.lsGetColdMs; })
  };
  ['idbPutStr', 'idbGetStr', 'idbPutAb4', 'idbGetAb4', 'idbPutAb40', 'idbGetAb40'].forEach(function (k) {
    out.summary[k + '.callMs'] = col(function (r) { return r[k].callMs; });
    out.summary[k + '.doneMs'] = col(function (r) { return r[k].completeMs || r[k].successMs; });
    out.summary[k + '.maxGapMs'] = col(function (r) { return r[k].maxGapMs; });
  });
  Object.keys(out.summary).forEach(function (k) { var s = out.summary[k]; console.log(k, JSON.stringify(s.raw), 'mean', s.mean, 'spread', s.spread); });
  L.save('e07', out);
  srv.server.close();
})().catch(function (e) { console.error(e); process.exit(1); });
