// e02_idb_large_values.js -- Hypothesis 2 (2026-10-31).
// Tests: IndexedDB on one origin (http://localhost) accepts a single 50 MB and a single
// 200 MB value, as an ArrayBuffer (pseudo-random bytes, so nothing compresses) and as a JSON
// string (vertex-array-like text), and reading it back is byte-identical. Identity is checked
// by SHA-256 (crypto.subtle.digest) of the bytes before the put and after the get (strings
// hashed as their UTF-8 bytes via TextEncoder). Also records put and get wall times. A fresh
// browser context per run; 3 runs. Sizes are decimal MB (1 MB = 1,000,000 bytes / chars).
'use strict';
var pw = require('playwright');
var L = require('./_lib');

function pageTest(opts) {
  // ES5 with promises (the IndexedDB and subtle APIs are callback/promise based)
  function hex(buf) { var a = new Uint8Array(buf), s = ''; for (var i = 0; i < a.length; i++) { s += (a[i] < 16 ? '0' : '') + a[i].toString(16); } return s; }
  function sha(bytes) { return crypto.subtle.digest('SHA-256', bytes).then(hex); }
  function openDb() {
    return new Promise(function (res, rej) {
      var rq = indexedDB.open('e02', 1);
      rq.onupgradeneeded = function () { rq.result.createObjectStore('s'); };
      rq.onsuccess = function () { res(rq.result); };
      rq.onerror = function () { rej(rq.error); };
    });
  }
  function put(db, key, val) {
    return new Promise(function (res, rej) {
      var tx = db.transaction('s', 'readwrite');
      tx.objectStore('s').put(val, key);
      tx.oncomplete = function () { res(); };
      tx.onerror = function () { rej(tx.error); };
      tx.onabort = function () { rej(tx.error || new Error('abort')); };
    });
  }
  function get(db, key) {
    return new Promise(function (res, rej) {
      var rq = db.transaction('s', 'readonly').objectStore('s').get(key);
      rq.onsuccess = function () { res(rq.result); };
      rq.onerror = function () { rej(rq.error); };
    });
  }
  function makeBuffer(n) {
    var u = new Uint8Array(n), x = 2463534242;
    for (var i = 0; i < n; i++) { x ^= x << 13; x ^= x >>> 17; x ^= x << 5; u[i] = x & 255; }
    return u.buffer;
  }
  function makeJson(n) {
    // a JSON array of [x,y,z] vertices, cut to exactly n characters and closed so it stays valid
    var parts = [], len = 1, i = 0;
    while (len < n - 64) {
      var p = '[' + (i * 0.125).toFixed(3) + ',' + (i % 997 * 1.5).toFixed(3) + ',' + (i % 31).toFixed(1) + ']';
      parts.push(p); len += p.length + 1; i++;
    }
    var s = '[' + parts.join(',') + ']';
    while (s.length < n) { s = s.slice(0, -1) + ' ]'; }
    return s;
  }
  var kind = opts.kind, size = opts.size, db, hashIn, t0, out = { kind: kind, size: size };
  return openDb().then(function (d) {
    db = d;
    var v = kind === 'buffer' ? makeBuffer(size) : makeJson(size);
    out.inputLength = kind === 'buffer' ? v.byteLength : v.length;
    var bytes = kind === 'buffer' ? v : new TextEncoder().encode(v);
    return sha(bytes).then(function (h) {
      hashIn = h; t0 = performance.now();
      return put(db, kind + size, v);
    });
  }).then(function () {
    out.putMs = performance.now() - t0; t0 = performance.now();
    return get(db, kind + size);
  }).then(function (back) {
    out.getMs = performance.now() - t0;
    out.backType = Object.prototype.toString.call(back);
    out.backLength = kind === 'buffer' ? back.byteLength : back.length;
    var bytes = kind === 'buffer' ? back : new TextEncoder().encode(back);
    return sha(bytes);
  }).then(function (hashOut) {
    out.hashIn = hashIn; out.hashOut = hashOut; out.identical = hashIn === hashOut;
    return new Promise(function (res) {
      var tx = db.transaction('s', 'readwrite'); tx.objectStore('s').clear(); tx.oncomplete = function () { db.close(); res(out); };
    });
  }).catch(function (e) { out.error = { name: e && e.name, message: e && e.message }; try { db.close(); } catch (x) {} return out; });
}

(async function () {
  var srv = await L.startServer(0);
  var browser = await pw.chromium.launch();
  var out = { version: browser.version(), headless: true, origin: srv.origin, runs: [] };
  var cases = [['buffer', 50e6], ['json', 50e6], ['buffer', 200e6], ['json', 200e6]];
  for (var run = 0; run < 3; run++) {
    var ctx = await browser.newContext();
    var page = await ctx.newPage();
    await page.goto(srv.origin + '/');
    for (var c = 0; c < cases.length; c++) {
      var r = await page.evaluate(pageTest, { kind: cases[c][0], size: cases[c][1] });
      r.run = run; out.runs.push(r);
      console.log(JSON.stringify(r));
    }
    await ctx.close();
  }
  out.summary = {};
  cases.forEach(function (c) {
    var rs = out.runs.filter(function (r) { return r.kind === c[0] && r.size === c[1]; });
    out.summary[c[0] + '_' + c[1] / 1e6 + 'MB'] = {
      allIdentical: rs.every(function (r) { return r.identical; }),
      putMs: L.stats(rs.map(function (r) { return r.putMs; })),
      getMs: L.stats(rs.map(function (r) { return r.getMs; }))
    };
  });
  console.log(JSON.stringify(out.summary));
  L.save('e02', out);
  await browser.close(); srv.server.close();
})().catch(function (e) { console.error(e); process.exit(1); });
