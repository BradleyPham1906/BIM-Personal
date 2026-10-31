// e12_files_install_surface.js -- files-and-install hypotheses (2026-10-31).
// Tests, in this Chromium (chromium-1243 headless shell, Playwright 1.63.0), what the note
// reference/research-local-storage/files-and-install.md claims from the documents:
//   H-F1  the File System Access pickers exist on http://localhost but are refused on file://
//         (the spec rejects an opaque origin) and in a cross-origin iframe (SecurityError);
//         without a user gesture they throw SecurityError.
//   H-F2  a service worker cannot be registered from file://; on http(s) it registers for a
//         scope under its script's path and is refused for a scope above it.
//   H-F3  the origin private file system (navigator.storage.getDirectory) works on localhost;
//         on file:// it is refused. A 64 MiB write through createWritable (main thread) and
//         createSyncAccessHandle (dedicated worker) is timed against IndexedDB put of a Blob.
//   H-F4  an OPFS FileSystemFileHandle survives a round trip through IndexedDB (structured
//         clone) and can be read after it.
//   H-F5  CompressionStream('gzip') exists on file:// and http, and shrinks a BIM-like JSON.
//   H-F6  <a download> with a blob: URL saves a 64 MiB file, on localhost and on file://.
// Method: fresh browser context per origin; timings 3 runs; results saved by _lib.save.
// Run: node e12_files_install_surface.js  (nothing installed; page code is ES5).
'use strict';
var pw = require('playwright');
var fs = require('fs');
var path = require('path');
var L = require('./_lib');

var MiB = 1024 * 1024;
var SIZE = (parseInt(process.env.E10_MIB, 10) || 64) * MiB;

var WORKER_JS = [
  'onmessage = function (ev) {',
  '  var n = ev.data.size, t0 = performance.now();',
  '  navigator.storage.getDirectory().then(function (root) {',
  '    return root.getFileHandle("w.bin", { create: true });',
  '  }).then(function (fh) { return fh.createSyncAccessHandle(); }).then(function (ah) {',
  '    var chunk = new Uint8Array(4 * 1024 * 1024), off = 0;',
  '    for (var i = 0; i < chunk.length; i++) chunk[i] = i & 255;',
  '    ah.truncate(0);',
  '    while (off < n) { off += ah.write(chunk, { at: off }); }',
  '    ah.flush(); var size = ah.getSize(); ah.close();',
  '    postMessage({ ok: true, ms: performance.now() - t0, size: size });',
  '  }).catch(function (e) { postMessage({ ok: false, name: e.name, message: e.message }); });',
  '};'
].join('\n');

var SW_JS = 'self.addEventListener("fetch", function () {});';

var PAGE = '<!doctype html><html><head><meta charset="utf-8"><title>e10</title></head>' +
  '<body><button id="b">save</button><a id="dl">dl</a></body></html>';

function surface() {
  // page side, ES5: what exists, and what the no-gesture call throws
  var r = {
    href: location.href, origin: String(self.origin), isSecureContext: self.isSecureContext,
    showOpenFilePicker: typeof window.showOpenFilePicker, showSaveFilePicker: typeof window.showSaveFilePicker,
    showDirectoryPicker: typeof window.showDirectoryPicker,
    serviceWorker: typeof navigator.serviceWorker, storageGetDirectory: !!(navigator.storage && navigator.storage.getDirectory),
    CompressionStream: typeof CompressionStream, launchQueue: typeof window.launchQueue
  };
  var p = r.showSaveFilePicker === 'function' ? window.showSaveFilePicker().then(function () { return 'resolved'; },
    function (e) { return e.name + ': ' + e.message; }) : Promise.resolve('absent');
  return p.then(function (noGesture) { r.saveNoGesture = noGesture; return r; });
}

function swTry(scope) {
  if (!navigator.serviceWorker) return Promise.resolve('navigator.serviceWorker absent');
  var opts = scope ? { scope: scope } : undefined;
  return navigator.serviceWorker.register('sw/sw.js', opts).then(function (reg) {
    var s = reg.scope; return reg.unregister().then(function () { return 'registered scope=' + s; });
  }, function (e) { return e.name + ': ' + e.message; });
}

function opfsAndIdb(size) {
  // page side: OPFS createWritable timing, IDB Blob put timing, handle round trip through IDB
  var out = {};
  function idbOpen() {
    return new Promise(function (res, rej) {
      var q = indexedDB.open('e10', 1);
      q.onupgradeneeded = function () { q.result.createObjectStore('s'); };
      q.onsuccess = function () { res(q.result); }; q.onerror = function () { rej(q.error); };
    });
  }
  function idbPut(db, k, v) {
    return new Promise(function (res, rej) {
      var tx = db.transaction('s', 'readwrite'); tx.objectStore('s').put(v, k);
      tx.oncomplete = function () { res(); }; tx.onerror = function () { rej(tx.error); }; tx.onabort = function () { rej(tx.error); };
    });
  }
  function idbGet(db, k) {
    return new Promise(function (res, rej) {
      var q = db.transaction('s', 'readonly').objectStore('s').get(k);
      q.onsuccess = function () { res(q.result); }; q.onerror = function () { rej(q.error); };
    });
  }
  var bytes = new Uint8Array(size); for (var i = 0; i < size; i += 4096) bytes[i] = i & 255;
  var blob = new Blob([bytes]);
  if (!navigator.storage || !navigator.storage.getDirectory) return Promise.resolve({ opfs: 'absent' });
  var root, fh, t0;
  return navigator.storage.getDirectory().then(function (r) { root = r; return root.getFileHandle('m.bin', { create: true }); })
    .then(function (h) { fh = h; t0 = performance.now(); return fh.createWritable(); })
    .then(function (w) { return w.write(blob).then(function () { return w.close(); }); })
    .then(function () { out.opfsWritableMs = performance.now() - t0; return fh.getFile(); })
    .then(function (f) { out.opfsFileSize = f.size; return idbOpen(); })
    .then(function (db) {
      t0 = performance.now();
      return idbPut(db, 'blob', blob).then(function () {
        out.idbBlobPutMs = performance.now() - t0;
        return idbPut(db, 'handle', fh);
      }).then(function () { return idbGet(db, 'handle'); }).then(function (h2) {
        out.handleRoundTrip = { kind: h2.kind, name: h2.name, isFileSystemFileHandle: h2 instanceof FileSystemFileHandle };
        return h2.isSameEntry(fh).then(function (same) { out.handleRoundTrip.isSameEntry = same; return h2.getFile(); });
      }).then(function (f2) { out.handleRoundTrip.readSize = f2.size; db.close(); });
    })
    .then(function () { return navigator.storage.estimate(); })
    .then(function (e) { out.estimate = { usage: e.usage, quota: e.quota, usageDetails: e.usageDetails || null };
      return navigator.storage.persisted(); })
    .then(function (p) { out.persistedBefore = p; return navigator.storage.persist(); })
    .then(function (p) { out.persistResult = p; return root.removeEntry('m.bin'); })
    .then(function () { return new Promise(function (res) { var q = indexedDB.deleteDatabase('e10'); q.onsuccess = q.onerror = function () { res(); }; }); })
    .then(function () { return out; }, function (e) { out.error = e.name + ': ' + e.message; return out; });
}

function gzipTest() {
  // page side: a BIM-like JSON (elements with ids, types, coordinates), gzip ratio and time
  if (typeof CompressionStream !== 'function') return Promise.resolve({ CompressionStream: 'absent' });
  var els = [];
  for (var i = 0; i < 60000; i++) {
    els.push({ id: 'el' + i, type: i % 3 ? 'wall' : 'slab', level: 'L' + (i % 12), layer: 'A-WALL',
      pts: [[i * 0.25, (i % 97) * 1.5, 0], [i * 0.25 + 4.2, (i % 97) * 1.5, 0]], h: 3.2, t: 0.2, mat: 'concrete' });
  }
  var json = JSON.stringify({ v: 170, elements: els });
  var input = new TextEncoder().encode(json);
  var t0 = performance.now();
  var cs = new CompressionStream('gzip');
  var stream = new Blob([input]).stream().pipeThrough(cs);
  return new Response(stream).arrayBuffer().then(function (buf) {
    var ms = performance.now() - t0;
    var t1 = performance.now();
    var back = new Blob([buf]).stream().pipeThrough(new DecompressionStream('gzip'));
    return new Response(back).text().then(function (txt) {
      return { jsonBytes: input.length, gzipBytes: buf.byteLength, ratio: buf.byteLength / input.length,
        gzipMs: ms, gunzipMs: performance.now() - t1, roundTripEqual: txt === json };
    });
  });
}

function blobDownloadSetup(size) {
  var bytes = new Uint8Array(size);
  var url = URL.createObjectURL(new Blob([bytes], { type: 'application/octet-stream' }));
  var a = document.getElementById('dl'); a.href = url; a.download = 'project.bim';
  return url.slice(0, 5);
}

function timed(fn) { var t = Date.now(); return fn().then(function (v) { return { v: v, ms: Date.now() - t }; }); }

function main() {
  var dir = L.tmpDir('e10-');
  var pageFile = path.join(dir, 'index.html');
  fs.writeFileSync(pageFile, PAGE);
  fs.mkdirSync(path.join(dir, 'sw'));
  fs.writeFileSync(path.join(dir, 'sw', 'sw.js'), SW_JS);
  var routes = {
    '/app/index.html': { body: PAGE },
    '/app/sw/sw.js': { type: 'text/javascript', body: SW_JS },
    '/app/w.js': { type: 'text/javascript', body: WORKER_JS },
    '/frame.html': { body: '<!doctype html><title>outer</title><iframe id="f"></iframe>' }
  };
  var results = { date: '2026-10-31', browser: null, file: {}, http: {}, iframe: {}, timings: {} };
  var browser, srv;
  return L.startServer(0, routes).then(function (s) {
    srv = s;
    return pw.chromium.launch({ headless: true, args: ['--disable-dev-shm-usage'] });
  }).then(function (b) {
    browser = b; results.browser = b.version();
    // ---- file://
    return browser.newContext({ acceptDownloads: true });
  }).then(function (ctx) {
    return ctx.newPage().then(function (page) {
      return page.goto('file://' + pageFile).then(function () { return page.evaluate(surface); })
        .then(function (r) { results.file.surface = r; return page.evaluate(swTry, null); })
        .then(function (r) { results.file.serviceWorkerRegister = r;
          return page.evaluate('navigator.storage && navigator.storage.getDirectory ? navigator.storage.getDirectory().then(function(){return "ok"},function(e){return e.name+": "+e.message}) : "absent"'); })
        .then(function (r) { results.file.opfsGetDirectory = r;
          // with a gesture: does the picker call reach the opaque-origin check?
          return page.evaluate('document.getElementById("b").onclick=function(){window.__r=window.showSaveFilePicker?window.showSaveFilePicker().then(function(){return "resolved"},function(e){return e.name+": "+e.message}):Promise.resolve("absent")}; 1'); })
        .then(function () { return page.click('#b'); })
        .then(function () { return page.evaluate('Promise.race([window.__r, new Promise(function(r){setTimeout(function(){r("pending after 3 s")},3000)})])'); })
        .then(function (r) { results.file.saveWithGesture = r; return page.evaluate(gzipTest); })
        .then(function (r) { results.file.gzip = r; return page.evaluate(blobDownloadSetup, 8 * MiB); })
        .then(function () { return Promise.all([page.waitForEvent('download', { timeout: 15000 }), page.click('#dl')]); })
        .then(function (d) { return d[0].path().then(function (p) { results.file.blobDownload8MiB = { suggested: d[0].suggestedFilename(), bytes: fs.statSync(p).size }; }); },
          function (e) { results.file.blobDownload8MiB = 'failed: ' + e.message; });
    }).then(function () { return ctx.close(); });
  }).then(function () {
    // ---- http://localhost (a secure context). A persistent (on-disk) profile: in an
    // off-the-record context (browser.newContext), reading a FileSystemFileHandle back out of
    // IndexedDB closed the whole browser in chromium-1243 (headless shell and full Chromium
    // alike, 2026-10-31); in a persistent profile the same steps pass. Recorded in the note.
    results.http.profile = 'persistent (launchPersistentContext)';
    return pw.chromium.launchPersistentContext(L.tmpDir('e10ud-'), { headless: true, acceptDownloads: true });
  }).then(function (ctx) {
    var base = srv.origin + '/app/index.html';
    return ctx.newPage().then(function (page) {
      return page.goto(base).then(function () { return page.evaluate(surface); })
        .then(function (r) { results.http.surface = r; return page.evaluate(swTry, null); })
        .then(function (r) { results.http.swDefaultScope = r; return page.evaluate(swTry, '/app/sw/deeper/'); })
        .then(function (r) { results.http.swScopeUnderScript = r; return page.evaluate(swTry, '/app/'); })
        .then(function (r) { results.http.swScopeAboveScript = r;
          return page.evaluate('document.getElementById("b").onclick=function(){window.__r=window.showSaveFilePicker().then(function(){return "resolved"},function(e){return e.name+": "+e.message})}; 1'); })
        .then(function () { return page.click('#b'); })
        .then(function () { return page.evaluate('Promise.race([window.__r, new Promise(function(r){setTimeout(function(){r("pending after 3 s")},3000)})])'); })
        .then(function (r) { results.http.saveWithGesture = r; return page.evaluate(gzipTest); })
        .then(function (r) { results.http.gzip = r;
          var runs = { opfsWritableMs: [], idbBlobPutMs: [], workerSyncMs: [] }, last = null, k = 0;
          function one() {
            return page.evaluate(opfsAndIdb, SIZE).then(function (o) {
              last = o; runs.opfsWritableMs.push(o.opfsWritableMs); runs.idbBlobPutMs.push(o.idbBlobPutMs);
              return page.evaluate('new Promise(function(res){var w=new Worker("w.js");w.onmessage=function(e){w.terminate();res(e.data)};w.postMessage({size:' + SIZE + '})})');
            }).then(function (w) { runs.workerSyncMs.push(w.ok ? w.ms : NaN); last.worker = w;
              return page.evaluate('navigator.storage.getDirectory().then(function(r){return r.removeEntry("w.bin")}).then(function(){return 1},function(){return 0})'); });
          }
          function loop() { if (k++ >= 3) return Promise.resolve(); return one().then(loop); }
          return loop().then(function () {
            results.http.opfsIdbLastRun = last;
            results.timings = { sizeMiB: SIZE / MiB, opfsWritableMs: L.stats(runs.opfsWritableMs),
              idbBlobPutMs: L.stats(runs.idbBlobPutMs), workerSyncAccessMs: L.stats(runs.workerSyncMs) };
          });
        })
        .then(function () { return page.evaluate(blobDownloadSetup, SIZE); })
        .then(function () { return Promise.all([page.waitForEvent('download', { timeout: 30000 }), page.click('#dl')]); })
        .then(function (d) { return d[0].path().then(function (p) { results.http.blobDownload64MiB = { suggested: d[0].suggestedFilename(), bytes: fs.statSync(p).size }; }); },
          function (e) { results.http.blobDownload64MiB = 'failed: ' + e.message; });
    }).then(function () { return ctx.close(); });
  }).then(function () {
    // ---- cross-origin iframe: top on 127.0.0.1, frame on localhost
    return browser.newContext();
  }).then(function (ctx) {
    var port = srv.port;
    return ctx.newPage().then(function (page) {
      return page.goto('http://127.0.0.1:' + port + '/frame.html')
        .then(function () { return page.evaluate('new Promise(function(res){var f=document.getElementById("f");f.onload=function(){res(1)};f.src="http://localhost:' + port + '/app/index.html"})'); })
        .then(function () {
          var fr = page.frames().filter(function (f) { return f.url().indexOf('localhost') >= 0; })[0];
          return fr.evaluate('document.getElementById("b").onclick=function(){window.__r=window.showSaveFilePicker().then(function(){return "resolved"},function(e){return e.name+": "+e.message})}; 1')
            .then(function () { return fr.click('#b'); })
            .then(function () { return fr.evaluate('Promise.race([window.__r, new Promise(function(r){setTimeout(function(){r("pending after 3 s")},3000)})])'); })
            .then(function (r) { results.iframe.saveWithGestureCrossOrigin = r;
              return fr.evaluate('navigator.storage.getDirectory().then(function(){return "ok"},function(e){return e.name+": "+e.message})'); })
            .then(function (r) { results.iframe.opfsCrossOrigin = r; });
        });
    }).then(function () { return ctx.close(); });
  }).then(function () {
    L.save('e12_files_install_surface', results);
    console.log(JSON.stringify(results, null, 2));
  }).catch(function (e) {
    console.error('FAILED', e && e.message);
    console.error(JSON.stringify(results, null, 1));
    process.exitCode = 1;
  })
    .then(function () { if (browser) return browser.close(); })
    .then(function () { if (srv) srv.server.close(); L.rm(dir); });
}

main();
