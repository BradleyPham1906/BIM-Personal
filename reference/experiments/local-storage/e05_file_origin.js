// e05_file_origin.js -- Hypothesis 5 (2026-10-31).
// Tests, from file:// pages: (a) localStorage and IndexedDB both work; (b) two different
// file:// HTML files in different folders see the same localStorage and IndexedDB data (one
// shared origin) or not; (c) whether navigator.storage exists, and whether estimate(),
// persist() and persisted() work there; also location.origin, window.isSecureContext and
// whether crypto.subtle and CompressionStream are present. Page A is <scratch>/e05/a/one.html,
// page B is <scratch>/e05/b/deeper/two.html. A writes a localStorage key and an IndexedDB
// record; B (a different file, other folder) then reads both and writes its own; A reads B's.
// In a fresh browser context and in a persistent profile; 3 runs each.
'use strict';
var pw = require('playwright');
var fs = require('fs');
var path = require('path');
var L = require('./_lib');

function probe() {
  var out = {
    href: location.href, origin: location.origin, isSecureContext: window.isSecureContext,
    hasStorage: typeof navigator.storage !== 'undefined',
    hasEstimate: !!(navigator.storage && navigator.storage.estimate),
    hasPersist: !!(navigator.storage && navigator.storage.persist),
    hasSubtle: !!(window.crypto && crypto.subtle),
    hasCompressionStream: typeof CompressionStream !== 'undefined'
  };
  var chain = Promise.resolve();
  if (out.hasEstimate) chain = chain.then(function () { return navigator.storage.estimate().then(function (e) { out.estimate = { quota: e.quota, usage: e.usage }; }, function (e) { out.estimateError = e.name + ': ' + e.message; }); });
  if (out.hasPersist) chain = chain.then(function () { return navigator.storage.persist().then(function (r) { out.persist = r; }, function (e) { out.persistError = e.name + ': ' + e.message; }); });
  if (navigator.storage && navigator.storage.persisted) chain = chain.then(function () { return navigator.storage.persisted().then(function (r) { out.persisted = r; }, function (e) { out.persistedError = e.name + ': ' + e.message; }); });
  return chain.then(function () { return out; });
}

function writeAndRead(opts) {
  var me = opts.me, other = opts.other, out = { me: me };
  try { localStorage.setItem('from-' + me, me + '@' + Date.now()); out.lsWrite = true; } catch (e) { out.lsWrite = e.name; }
  try { out.lsSeesOther = localStorage.getItem('from-' + other); out.lsKeys = Object.keys(localStorage); } catch (e) { out.lsRead = e.name; }
  return new Promise(function (res) {
    var rq;
    try { rq = indexedDB.open('e05', 1); } catch (e) { out.idbOpen = e.name; res(out); return; }
    rq.onupgradeneeded = function () { rq.result.createObjectStore('s'); };
    rq.onerror = function () { out.idbOpen = rq.error && rq.error.name; res(out); };
    rq.onsuccess = function () {
      var db = rq.result, tx = db.transaction('s', 'readwrite'), st = tx.objectStore('s');
      st.put({ by: me, bytes: new Uint8Array([1, 2, 3]) }, 'from-' + me);
      var g = st.get('from-' + other);
      g.onsuccess = function () { out.idbSeesOther = g.result ? g.result.by : null; };
      tx.oncomplete = function () { out.idbWrite = true; db.close(); res(out); };
      tx.onabort = function () { out.idbWrite = tx.error && tx.error.name; res(out); };
    };
  });
}

(async function () {
  var root = path.join(L.SCRATCH, 'e05');
  fs.mkdirSync(path.join(root, 'a'), { recursive: true });
  fs.mkdirSync(path.join(root, 'b', 'deeper'), { recursive: true });
  var html = '<!doctype html><meta charset="utf-8"><title>e05</title><body>e05</body>';
  fs.writeFileSync(path.join(root, 'a', 'one.html'), html);
  fs.writeFileSync(path.join(root, 'b', 'deeper', 'two.html'), html);
  var urlA = 'file://' + path.join(root, 'a', 'one.html');
  var urlB = 'file://' + path.join(root, 'b', 'deeper', 'two.html');
  var out = { urlA: urlA, urlB: urlB, runs: [] };
  for (var run = 0; run < 3; run++) {
    for (var kind = 0; kind < 2; kind++) {
      var browser = null, ctx, dir = null;
      if (kind) { dir = L.tmpDir('e05-'); ctx = await pw.chromium.launchPersistentContext(dir); }
      else { browser = await pw.chromium.launch(); ctx = await browser.newContext(); }
      var r = { run: run, kind: kind ? 'persistent' : 'newContext', version: (browser || ctx.browser()).version() };
      var pa = await ctx.newPage(); await pa.goto(urlA);
      r.probeA = await pa.evaluate(probe);
      r.a1 = await pa.evaluate(writeAndRead, { me: 'A', other: 'B' });
      var pb = await ctx.newPage(); await pb.goto(urlB);
      r.probeB = await pb.evaluate(probe);
      r.b1 = await pb.evaluate(writeAndRead, { me: 'B', other: 'A' });
      r.a2 = await pa.evaluate(writeAndRead, { me: 'A', other: 'B' });
      out.runs.push(r); console.log(JSON.stringify(r));
      await ctx.close(); if (browser) await browser.close(); if (dir) L.rm(dir);
    }
  }
  L.save('e05', out);
  L.rm(root);
})().catch(function (e) { console.error(e); process.exit(1); });
