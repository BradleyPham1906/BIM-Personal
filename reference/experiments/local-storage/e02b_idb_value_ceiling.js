// e02b_idb_value_ceiling.js -- follow-up to Hypothesis 2 (2026-10-31).
// e02 found that a single 200 MB ArrayBuffer or string put fails in this Chromium with
// UnknownError "The serialized keys and/or value are too large (... max=133169152 bytes)".
// This script tests: (a) the exact ceiling, by binary search on an ArrayBuffer's byteLength
// (to 1 KiB); (b) whether a 200 MB Blob (which IndexedDB stores by reference, outside the
// serialized message) is accepted and reads back byte-identical (SHA-256); (c) whether 200 MB
// stored as 4 records of 50 MB in one transaction is accepted and reads back identical;
// (d) whether a string of U+4E00 characters hits the ceiling at half the character count
// (two bytes per character). Runs in the default headless shell and, once, in the full
// Chromium binary in headless mode (channel 'chromium') to see whether the ceiling differs.
// 3 runs in the shell, 1 in channel 'chromium'.
'use strict';
var pw = require('playwright');
var L = require('./_lib');

function pageTest() {
  function hex(buf) { var a = new Uint8Array(buf), s = ''; for (var i = 0; i < a.length; i++) { s += (a[i] < 16 ? '0' : '') + a[i].toString(16); } return s; }
  function sha(b) { return crypto.subtle.digest('SHA-256', b).then(hex); }
  function openDb() { return new Promise(function (res, rej) { var rq = indexedDB.open('e02b', 1); rq.onupgradeneeded = function () { rq.result.createObjectStore('s'); }; rq.onsuccess = function () { res(rq.result); }; rq.onerror = function () { rej(rq.error); }; }); }
  function putMany(db, pairs) {
    return new Promise(function (res) {
      var tx = db.transaction('s', 'readwrite'), st = tx.objectStore('s'), err = null;
      try { for (var i = 0; i < pairs.length; i++) st.put(pairs[i][1], pairs[i][0]); } catch (e) { err = { name: e.name, message: e.message }; }
      tx.oncomplete = function () { res({ ok: !err, err: err }); };
      tx.onabort = function () { res({ ok: false, err: err || { name: tx.error && tx.error.name, message: tx.error && tx.error.message } }); };
    });
  }
  function get(db, k) { return new Promise(function (res, rej) { var rq = db.transaction('s').objectStore('s').get(k); rq.onsuccess = function () { res(rq.result); }; rq.onerror = function () { rej(rq.error); }; }); }
  function clear(db) { return new Promise(function (res) { var tx = db.transaction('s', 'readwrite'); tx.objectStore('s').clear(); tx.oncomplete = res; }); }
  function rnd(n, seed) { var u = new Uint8Array(n), x = seed; for (var i = 0; i < n; i++) { x ^= x << 13; x ^= x >>> 17; x ^= x << 5; u[i] = x & 255; } return u; }
  var db, out = {};
  return openDb().then(function (d) {
    db = d;
    var big = new ArrayBuffer(140 * 1024 * 1024);
    var lo = 100 * 1024 * 1024, hi = 140 * 1024 * 1024; // lo known ok, hi known too large
    function step() {
      if (hi - lo <= 1024) { return Promise.resolve(lo); }
      var mid = Math.floor((lo + hi) / 2);
      return putMany(db, [['probe', big.slice(0, mid)]]).then(function (r) { if (r.ok) lo = mid; else { hi = mid; out.ceilingError = r.err; } return clear(db).then(step); });
    }
    return step();
  }).then(function (maxOk) {
    out.maxArrayBufferBytesOk = maxOk;
    // (d) CJK string ceiling: 66,000,000 chars of U+4E00 = 132 MB if 2 bytes/char
    var s1 = new Array(66000001).join('一');
    return putMany(db, [['cjk66M', s1]]).then(function (r) { out.cjk66Mchars = r; return clear(db); }).then(function () {
      var s2 = new Array(67000001).join('一');
      return putMany(db, [['cjk67M', s2]]);
    }).then(function (r) { out.cjk67Mchars = r; return clear(db); });
  }).then(function () {
    // (b) a 200 MB Blob
    var bytes = rnd(200e6, 88172645);
    return sha(bytes).then(function (hIn) {
      var blob = new Blob([bytes]); var t0 = performance.now();
      return putMany(db, [['blob', blob]]).then(function (r) {
        out.blob200 = { put: r, putMs: performance.now() - t0 };
        t0 = performance.now();
        return get(db, 'blob');
      }).then(function (b) {
        out.blob200.backType = Object.prototype.toString.call(b); out.blob200.backSize = b && b.size;
        return b.arrayBuffer();
      }).then(function (ab) {
        out.blob200.getAndReadMs = performance.now() - t0;
        return sha(ab);
      }).then(function (hOut) { out.blob200.identical = hOut === hIn; out.blob200.hash = hIn; return clear(db); });
    });
  }).then(function () {
    // (c) 200 MB as 4 x 50 MB ArrayBuffers in one transaction
    var parts = [], pairs = [];
    for (var i = 0; i < 4; i++) { parts.push(rnd(50e6, 1000 + i)); pairs.push(['part' + i, parts[i].buffer]); }
    var whole = new Uint8Array(200e6); for (i = 0; i < 4; i++) whole.set(parts[i], i * 50e6);
    return sha(whole).then(function (hIn) {
      var t0 = performance.now();
      return putMany(db, pairs).then(function (r) {
        out.chunks4x50 = { put: r, putMs: performance.now() - t0 }; t0 = performance.now();
        return Promise.all([0, 1, 2, 3].map(function (j) { return get(db, 'part' + j); }));
      }).then(function (backs) {
        out.chunks4x50.getMs = performance.now() - t0;
        var w = new Uint8Array(200e6); for (var j = 0; j < 4; j++) w.set(new Uint8Array(backs[j]), j * 50e6);
        return sha(w);
      }).then(function (hOut) { out.chunks4x50.identical = hOut === hIn; return clear(db); });
    });
  }).then(function () { db.close(); return out; })
    .catch(function (e) { out.error = { name: e && e.name, message: e && e.message }; return out; });
}

(async function () {
  var srv = await L.startServer(0);
  var out = { runs: [] };
  var plans = [{ channel: undefined, runs: 3 }, { channel: 'chromium', runs: 1 }];
  for (var p = 0; p < plans.length; p++) {
    var browser = await pw.chromium.launch(plans[p].channel ? { channel: plans[p].channel } : {});
    for (var run = 0; run < plans[p].runs; run++) {
      var ctx = await browser.newContext();
      var page = await ctx.newPage();
      await page.goto(srv.origin + '/');
      var r = await page.evaluate(pageTest);
      r.run = run; r.channel = plans[p].channel || 'default (chromium-headless-shell)'; r.version = browser.version();
      out.runs.push(r);
      console.log(JSON.stringify(r));
      await ctx.close();
    }
    await browser.close();
  }
  L.save('e02b', out);
  srv.server.close();
})().catch(function (e) { console.error(e); process.exit(1); });
