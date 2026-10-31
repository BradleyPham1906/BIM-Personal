// e11_app_boot_storage.js -- the app's own storage at boot (2026-10-31).
// Tests: does BIM-Personal's built file canvas_v10.html, opened over http (served from
// localhost) and from file:// (the repository's copy, read only), write localStorage at boot,
// and which keys, with what sizes; listed after the load event and again 5 s later. Also lists
// IndexedDB databases (indexedDB.databases()), sessionStorage keys, estimate().usage, uncaught
// page errors and failed requests (the app may ask for remote data; this environment's network
// is not part of the test). Size = key length + value length in UTF-16 code units, the unit
// localStorage's quota counts (e01). A fresh context per run; 3 runs per origin kind.
// Nothing in the repository is modified: the file is only read.
'use strict';
var pw = require('playwright');
var path = require('path');
var L = require('./_lib');

var APP = path.resolve(__dirname, '..', '..', '..', 'canvas_v10.html');

function snapshot() {
  var ls = [], ss = [], i, k, total = 0;
  for (i = 0; i < localStorage.length; i++) { k = localStorage.key(i); var v = localStorage.getItem(k) || ''; ls.push({ key: k, units: k.length + v.length, head: v.slice(0, 60) }); total += k.length + v.length; }
  for (i = 0; i < sessionStorage.length; i++) { k = sessionStorage.key(i); ss.push({ key: k, units: k.length + (sessionStorage.getItem(k) || '').length }); }
  ls.sort(function (a, b) { return b.units - a.units; });
  var dbs = indexedDB.databases ? indexedDB.databases() : Promise.resolve('no databases()');
  return Promise.all([dbs, navigator.storage && navigator.storage.estimate ? navigator.storage.estimate() : null]).then(function (r) {
    return { localStorage: ls, localStorageTotalUnits: total, sessionStorage: ss, idbDatabases: r[0], usage: r[1] && r[1].usage };
  });
}

(async function () {
  var srv = await L.startServer(0, { '/canvas_v10.html': { file: APP } });
  var browser = await pw.chromium.launch();
  var out = { version: browser.version(), app: APP, runs: [] };
  var urls = { http: srv.origin + '/canvas_v10.html', file: 'file://' + APP };
  for (var kind in urls) {
    for (var run = 0; run < 3; run++) {
      var ctx = await browser.newContext();
      var page = await ctx.newPage();
      var errors = [], failed = [];
      page.on('pageerror', function (e) { errors.push(String(e.message).slice(0, 160)); });
      page.on('requestfailed', function (rq) { failed.push(rq.url().slice(0, 100)); });
      var t0 = Date.now();
      await page.goto(urls[kind], { waitUntil: 'load', timeout: 60000 });
      var r = { kind: kind, run: run, loadMs: Date.now() - t0 };
      r.afterLoad = await page.evaluate(snapshot);
      await page.waitForTimeout(5000);
      r.after5s = await page.evaluate(snapshot);
      r.pageErrors = errors; r.failedRequests = failed.length; r.failedSample = failed.slice(0, 5);
      out.runs.push(r);
      console.log(JSON.stringify({ kind: kind, run: run, loadMs: r.loadMs,
        afterLoad: r.afterLoad.localStorage.map(function (x) { return x.key + ':' + x.units; }), afterLoadTotal: r.afterLoad.localStorageTotalUnits,
        after5s: r.after5s.localStorage.map(function (x) { return x.key + ':' + x.units; }), after5sTotal: r.after5s.localStorageTotalUnits,
        session: r.after5s.sessionStorage, idb: r.after5s.idbDatabases, usage: r.after5s.usage, errors: errors.length, failed: failed.length }));
      await ctx.close();
    }
  }
  L.save('e11', out);
  await browser.close(); srv.server.close();
})().catch(function (e) { console.error(e); process.exit(1); });
