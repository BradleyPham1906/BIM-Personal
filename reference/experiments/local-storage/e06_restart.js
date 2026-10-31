// e06_restart.js -- Hypothesis 6 (2026-10-31).
// Tests: data survives a browser restart with launchPersistentContext: write, close the
// browser, relaunch on the same user-data-dir, read. Written: a localStorage key (1 MiB string)
// and an IndexedDB record (a 10,000,000-byte pseudo-random ArrayBuffer, SHA-256 kept) on
// http://localhost:<fixed port> (the port is part of the origin, so it is the same both
// times), and the same on a file:// page. Read after relaunch: the key's length, the record's
// hash, estimate().usage. Also a control: an incognito-like browser.newContext() closed and a
// new one made in the same browser must NOT see the data. 3 runs, each on a new user-data-dir.
'use strict';
var pw = require('playwright');
var fs = require('fs');
var path = require('path');
var L = require('./_lib');

function writeAll() {
  function hex(b) { var a = new Uint8Array(b), s = ''; for (var i = 0; i < a.length; i++) s += (a[i] < 16 ? '0' : '') + a[i].toString(16); return s; }
  localStorage.setItem('e06', new Array(1024 * 1024 + 1).join('z'));
  var u = new Uint8Array(10e6), x = 362436069;
  for (var i = 0; i < u.length; i++) { x ^= x << 13; x ^= x >>> 17; x ^= x << 5; u[i] = x & 255; }
  return crypto.subtle.digest('SHA-256', u).then(hex).then(function (h) {
    return new Promise(function (res, rej) {
      var rq = indexedDB.open('e06', 1);
      rq.onupgradeneeded = function () { rq.result.createObjectStore('s'); };
      rq.onsuccess = function () {
        var db = rq.result, tx = db.transaction('s', 'readwrite');
        tx.objectStore('s').put(u.buffer, 'blob10');
        tx.oncomplete = function () { db.close(); res(h); };
        tx.onabort = function () { rej(tx.error); };
      };
    });
  });
}

function readAll() {
  function hex(b) { var a = new Uint8Array(b), s = ''; for (var i = 0; i < a.length; i++) s += (a[i] < 16 ? '0' : '') + a[i].toString(16); return s; }
  var out = { lsLen: (localStorage.getItem('e06') || '').length };
  return new Promise(function (res) {
    var rq = indexedDB.open('e06', 1);
    rq.onupgradeneeded = function () { rq.result.createObjectStore('s'); out.idbWasNew = true; };
    rq.onsuccess = function () {
      var db = rq.result, g = db.transaction('s').objectStore('s').get('blob10');
      g.onsuccess = function () { db.close(); res(g.result); };
    };
  }).then(function (buf) {
    if (!buf) { out.idbHash = null; return out; }
    return crypto.subtle.digest('SHA-256', buf).then(function (d) { out.idbHash = hex(d); return out; });
  }).then(function () { return navigator.storage.estimate(); }).then(function (e) { out.usage = e.usage; return out; });
}

(async function () {
  var srv = await L.startServer(47317);
  var fdir = path.join(L.SCRATCH, 'e06pages'); fs.mkdirSync(fdir, { recursive: true });
  fs.writeFileSync(path.join(fdir, 'p.html'), '<!doctype html><meta charset="utf-8"><title>e06</title>e06');
  var urls = { http: srv.origin + '/', file: 'file://' + path.join(fdir, 'p.html') };
  var out = { urls: urls, runs: [] };
  for (var run = 0; run < 3; run++) {
    var dir = L.tmpDir('e06-');
    var r = { run: run, written: {}, afterRestart: {} };
    var ctx = await pw.chromium.launchPersistentContext(dir);
    r.version = ctx.browser().version();
    var page = ctx.pages()[0] || await ctx.newPage();
    for (var k in urls) { await page.goto(urls[k]); r.written[k] = await page.evaluate(writeAll); }
    await ctx.close();
    var ctx2 = await pw.chromium.launchPersistentContext(dir);
    var page2 = ctx2.pages()[0] || await ctx2.newPage();
    for (k in urls) {
      await page2.goto(urls[k]);
      var got = await page2.evaluate(readAll);
      got.hashMatches = got.idbHash === r.written[k];
      r.afterRestart[k] = got;
    }
    await ctx2.close(); L.rm(dir);
    // control: incognito-like contexts do not keep data
    var browser = await pw.chromium.launch();
    var c1 = await browser.newContext(); var p1 = await c1.newPage(); await p1.goto(urls.http); await p1.evaluate(writeAll); await c1.close();
    var c2 = await browser.newContext(); var p2 = await c2.newPage(); await p2.goto(urls.http); r.controlNewContext = await p2.evaluate(readAll);
    await browser.close();
    out.runs.push(r); console.log(JSON.stringify(r));
  }
  L.save('e06', out);
  L.rm(fdir); srv.server.close();
})().catch(function (e) { console.error(e); process.exit(1); });
