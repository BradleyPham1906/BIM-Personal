// e03_storage_estimate.js -- Hypothesis 3 (2026-10-31).
// Tests: navigator.storage.estimate() reports quota and usage; usage rises by roughly the
// stored size after writing 100 MB (one 100,000,000-byte pseudo-random ArrayBuffer) to
// IndexedDB; and the quota differs between a persistent profile (launchPersistentContext with a
// temporary user-data-dir) and a fresh incognito-like context (browser.newContext()). Also
// records usageDetails, the usage after deleting the record, and whether a 4 MiB localStorage
// write moves usage at all. 3 runs of each context kind, in the default headless shell and in
// the full Chromium binary (channel 'chromium', new headless mode). Also records the disk's
// size and free space (os-level, from statfs) for comparison with the quota.
'use strict';
var pw = require('playwright');
var fs = require('fs');
var L = require('./_lib');

function pageTest() {
  function est() { return navigator.storage.estimate().then(function (e) { return { quota: e.quota, usage: e.usage, usageDetails: e.usageDetails || null }; }); }
  function openDb() { return new Promise(function (res, rej) { var rq = indexedDB.open('e03', 1); rq.onupgradeneeded = function () { rq.result.createObjectStore('s'); }; rq.onsuccess = function () { res(rq.result); }; rq.onerror = function () { rej(rq.error); }; }); }
  function tx(db, fn) { return new Promise(function (res, rej) { var t = db.transaction('s', 'readwrite'); fn(t.objectStore('s')); t.oncomplete = res; t.onabort = function () { rej(t.error); }; }); }
  var out = {}, db;
  return est().then(function (e) { out.before = e; return openDb(); }).then(function (d) {
    db = d;
    var u = new Uint8Array(100e6), x = 123456789;
    for (var i = 0; i < u.length; i++) { x ^= x << 13; x ^= x >>> 17; x ^= x << 5; u[i] = x & 255; }
    return tx(db, function (s) { s.put(u.buffer, 'big'); });
  }).then(est).then(function (e) {
    out.afterIdb100MB = e; out.deltaIdb = e.usage - out.before.usage;
    localStorage.setItem('ls', new Array(4 * 1024 * 1024 + 1).join('a'));
    return est();
  }).then(function (e) {
    out.afterLs4MiB = e; out.deltaLs = e.usage - out.afterIdb100MB.usage;
    localStorage.clear();
    return tx(db, function (s) { s.delete('big'); });
  }).then(est).then(function (e) { out.afterDelete = e; db.close(); return out; });
}

(async function () {
  var srv = await L.startServer(0);
  var sf = fs.statfsSync(L.SCRATCH);
  var out = { disk: { totalBytes: sf.blocks * sf.bsize, freeBytes: sf.bavail * sf.bsize }, runs: [] };
  var channels = [undefined, 'chromium'];
  for (var c = 0; c < channels.length; c++) {
    var opt = channels[c] ? { channel: channels[c] } : {};
    for (var run = 0; run < 3; run++) {
      // persistent profile
      var dir = L.tmpDir('e03-profile-');
      var pctx = await pw.chromium.launchPersistentContext(dir, opt);
      var pg = pctx.pages()[0] || await pctx.newPage();
      await pg.goto(srv.origin + '/');
      var r1 = await pg.evaluate(pageTest);
      r1.kind = 'persistent'; r1.channel = channels[c] || 'default'; r1.run = run; r1.version = pctx.browser() ? pctx.browser().version() : null;
      out.runs.push(r1); console.log(JSON.stringify(r1));
      await pctx.close(); L.rm(dir);
      // incognito-like
      var browser = await pw.chromium.launch(opt);
      var ctx = await browser.newContext();
      var page = await ctx.newPage();
      await page.goto(srv.origin + '/');
      var r2 = await page.evaluate(pageTest);
      r2.kind = 'newContext'; r2.channel = channels[c] || 'default'; r2.run = run; r2.version = browser.version();
      out.runs.push(r2); console.log(JSON.stringify(r2));
      await browser.close();
    }
  }
  out.summary = {};
  ['default', 'chromium'].forEach(function (ch) {
    ['persistent', 'newContext'].forEach(function (k) {
      var rs = out.runs.filter(function (r) { return r.channel === ch && r.kind === k; });
      out.summary[ch + '/' + k] = {
        quota: L.stats(rs.map(function (r) { return r.before.quota; })),
        usageBefore: L.stats(rs.map(function (r) { return r.before.usage; })),
        deltaIdb: L.stats(rs.map(function (r) { return r.deltaIdb; })),
        deltaLs: L.stats(rs.map(function (r) { return r.deltaLs; })),
        usageAfterDelete: L.stats(rs.map(function (r) { return r.afterDelete.usage; }))
      };
    });
  });
  console.log(JSON.stringify(out.summary, null, 1));
  console.log(JSON.stringify(out.disk));
  L.save('e03', out);
  srv.server.close();
})().catch(function (e) { console.error(e); process.exit(1); });
