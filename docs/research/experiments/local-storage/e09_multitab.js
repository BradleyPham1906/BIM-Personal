// e09_multitab.js -- Hypothesis 9 (2026-10-31).
// Tests: two pages (tabs) of one origin, one browser context. Page A opens database 'e09' at
// version 1 and keeps it open. Page B opens it at version 2. Expected: A receives a
// 'versionchange' event (oldVersion 1, newVersion 2); if A does not close, B receives 'blocked'
// and its open waits; once A closes, B gets 'upgradeneeded' then 'success'. Variant 2: A closes
// its connection inside its versionchange handler (the recommended practice); then B should
// not see 'blocked'. Every event is logged with its page, type, versions and a timestamp
// (performance.timeOrigin + performance.now(), so the two pages share one clock). In variant 1
// A closes 500 ms after its versionchange, to see B unblock. Also: does an 'onclose' fire on
// A's connection when it is closed by A itself (it should not; it fires only on abnormal close).
// 3 runs of each variant, each in a fresh context.
'use strict';
var pw = require('playwright');
var L = require('./_lib');

function openA(opts) {
  window.__log = [];
  function now() { return Math.round((performance.timeOrigin + performance.now()) * 10) / 10; }
  return new Promise(function (res) {
    var rq = indexedDB.open('e09', 1);
    rq.onupgradeneeded = function () { rq.result.createObjectStore('s'); window.__log.push({ p: 'A', ev: 'upgradeneeded', t: now() }); };
    rq.onsuccess = function () {
      var db = rq.result; window.__log.push({ p: 'A', ev: 'success', v: db.version, t: now() });
      db.onversionchange = function (e) {
        window.__log.push({ p: 'A', ev: 'versionchange', oldVersion: e.oldVersion, newVersion: e.newVersion, t: now() });
        if (opts.closeAtOnce) { db.close(); window.__log.push({ p: 'A', ev: 'closed-by-handler', t: now() }); }
        else setTimeout(function () { db.close(); window.__log.push({ p: 'A', ev: 'closed-after-500ms', t: now() }); }, 500);
      };
      db.onclose = function () { window.__log.push({ p: 'A', ev: 'close-event', t: now() }); };
      res('A open');
    };
  });
}

function openB() {
  var log = [];
  function now() { return Math.round((performance.timeOrigin + performance.now()) * 10) / 10; }
  return new Promise(function (res) {
    var rq = indexedDB.open('e09', 2);
    rq.onblocked = function (e) { log.push({ p: 'B', ev: 'blocked', oldVersion: e.oldVersion, newVersion: e.newVersion, t: now() }); };
    rq.onupgradeneeded = function (e) { log.push({ p: 'B', ev: 'upgradeneeded', oldVersion: e.oldVersion, newVersion: e.newVersion, t: now() }); };
    rq.onsuccess = function () { log.push({ p: 'B', ev: 'success', v: rq.result.version, t: now() }); rq.result.close(); res(log); };
    rq.onerror = function () { log.push({ p: 'B', ev: 'error', name: rq.error && rq.error.name, t: now() }); res(log); };
  });
}

(async function () {
  var srv = await L.startServer(0);
  var browser = await pw.chromium.launch();
  var out = { version: browser.version(), runs: [] };
  var variants = [{ name: 'A-does-not-close-at-once', closeAtOnce: false }, { name: 'A-closes-in-versionchange', closeAtOnce: true }];
  for (var v = 0; v < variants.length; v++) {
    for (var run = 0; run < 3; run++) {
      var ctx = await browser.newContext();
      var a = await ctx.newPage(); await a.goto(srv.origin + '/a');
      var b = await ctx.newPage(); await b.goto(srv.origin + '/b');
      await a.evaluate(openA, { closeAtOnce: variants[v].closeAtOnce });
      var bLog = await b.evaluate(openB);
      await a.waitForTimeout(100);
      var aLog = await a.evaluate(function () { return window.__log; });
      var all = aLog.concat(bLog).sort(function (x, y) { return x.t - y.t; });
      var t0 = all[0].t;
      var seq = all.map(function (e) { var c = Object.assign({}, e); c.t = Math.round((e.t - t0) * 10) / 10; return c; });
      var r = { variant: variants[v].name, run: run, events: seq };
      out.runs.push(r); console.log(JSON.stringify(r));
      await ctx.close();
    }
  }
  L.save('e09', out);
  await browser.close(); srv.server.close();
})().catch(function (e) { console.error(e); process.exit(1); });
