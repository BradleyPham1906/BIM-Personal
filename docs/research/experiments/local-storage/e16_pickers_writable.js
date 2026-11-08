// e16_pickers_writable.js -- V172g, hypotheses H29 to H32 (2026-11-07).
// (a) Which `types[].accept` extensions and MIME keys Chromium's showSaveFilePicker and
//     showOpenFilePicker accept. Each call is made from a real click (user activation), over http
//     and from file://. A rejected option throws TypeError before any dialog; an accepted one
//     reaches the dialog, which headless Chromium cannot show, so it ends in AbortError. Without
//     a click the call must fail with SecurityError (activation), checked once per page.
// (b) What a FileSystemWritableFileStream does to the file before close(), on abort(), and with
//     keepExistingData false (the default) when the new content is shorter; whether getFile()
//     .lastModified changes after a write. Measured on an origin-private (OPFS) file, the only
//     writable handle headless Chromium can get without a dialog; that the same holds for a file
//     the user picked rests on the specification (the swap file), not on this run.
// (c) A file handle stored in IndexedDB and read back after the browser restarts (persistent
//     profile): isSameEntry, the name, queryPermission({mode:'readwrite'}).
// 5 runs of (b), 3 of (c). Run: node e16_pickers_writable.js
'use strict';
var pw = require('playwright');
var fs = require('fs');
var path = require('path');
var L = require('./_lib');

var EXTS = ['.json', '.acad3d.json', '.gz', '.json.gz', '.acad3d.json.gz', 'json', '.abcdefghijklmno', '.abcdefghijklmnop',
  '.abcdefghijklmnopq', '.a b', '.a-b', '.a_b', '.a+b', '.', '..json', '.json.'];
var MIMES = ['application/json', 'application/gzip', 'application/octet-stream', 'application/x-acad3d+json', 'json', '*/*'];

var PAGE = '<!doctype html><html><head><meta charset="utf-8"><title>e16</title></head><body>' +
  '<button id="b" style="width:200px;height:60px">go</button><script>' +
  'window.__job=null;window.__res=null;' +
  'document.getElementById("b").addEventListener("click",function(){var j=window.__job;window.__res=null;' +
  'try{var p=window[j.fn](j.opts);p.then(function(){window.__res="resolved";},function(e){window.__res=e.name+": "+e.message;});}' +
  'catch(e){window.__res="sync "+e.name+": "+e.message;}});' +
  '</script></body></html>';

async function pickerMatrix(page) {
  var out = { noActivation: null, ext: {}, mime: {} };
  // Playwright's evaluate() runs with a user gesture, so the call without activation waits 6 s
  // first: Chromium's transient activation lasts 5 s (HTML: "transient activation duration").
  out.noActivation = await page.evaluate(function () {
    return new Promise(function (r) { setTimeout(r, 6000); }).then(function () { return window.showSaveFilePicker({}); })
      .then(function () { return 'resolved'; }, function (e) { return e.name + ': ' + e.message; });
  });
  async function one(fn, opts) {
    await page.evaluate(function (j) { window.__job = j; }, { fn: fn, opts: opts });
    await page.click('#b');
    for (var i = 0; i < 100; i++) {
      var r = await page.evaluate(function () { return window.__res; });
      if (r) return r;
      await new Promise(function (res) { setTimeout(res, 20); });
    }
    return 'no answer in 2 s';
  }
  for (var e = 0; e < EXTS.length; e++) {
    var x = EXTS[e];
    out.ext[x] = {
      save: await one('showSaveFilePicker', { types: [{ description: 'Project', accept: { 'application/json': [x] } }] }),
      open: await one('showOpenFilePicker', { types: [{ description: 'Project', accept: { 'application/json': [x] } }] })
    };
  }
  for (var m = 0; m < MIMES.length; m++) {
    out.mime[MIMES[m]] = await one('showSaveFilePicker', { types: [{ description: 'Project', accept: (function () { var a = {}; a[MIMES[m]] = ['.json']; return a; })() }] });
  }
  out.suggestedNameGz = await one('showSaveFilePicker', { suggestedName: 'House.acad3d.json.gz', types: [{ accept: { 'application/gzip': ['.gz'] } }] });
  out.idOption = await one('showSaveFilePicker', { id: 'acad3d-projects', suggestedName: 'House.acad3d.json' });
  out.badId = await one('showSaveFilePicker', { id: 'bad id with spaces' });
  return out;
}

function writable() {
  function text(h) { return h.getFile().then(function (f) { return f.text().then(function (t) { return { text: t, size: f.size, lastModified: f.lastModified }; }); }); }
  var name = 'e16-' + Math.random().toString(36).slice(2) + '.acad3d.json', root, h, out = {};
  return navigator.storage.getDirectory().then(function (r) { root = r; return root.getFileHandle(name, { create: true }); })
    .then(function (fh) { h = fh; return h.createWritable(); })
    .then(function (w) { return w.write('ORIGINAL-CONTENT-0123456789').then(function () { return w.close(); }); })
    .then(function () { return text(h); }).then(function (t) { out.afterFirstClose = t; return new Promise(function (r) { setTimeout(r, 30); }); })
    .then(function () { return h.createWritable(); })
    .then(function (w) {
      return w.write('NEW').then(function () { return text(h); }).then(function (t) { out.beforeCloseWhileWriting = t.text; return w.abort(); });
    })
    .then(function () { return text(h); }).then(function (t) { out.afterAbort = t.text; })
    .then(function () { return h.createWritable(); })
    .then(function (w) { return w.write('SHORT').then(function () { return w.close(); }); })
    .then(function () { return text(h); }).then(function (t) { out.afterShortWriteDefault = t.text; out.lastModifiedChanged = t.lastModified !== out.afterFirstClose.lastModified; })
    .then(function () { return h.createWritable({ keepExistingData: true }); })
    .then(function (w) { return w.write('AB').then(function () { return w.close(); }); })
    .then(function () { return text(h); }).then(function (t) { out.afterKeepExisting = t.text; })
    .then(function () { return h.createWritable(); })
    .then(function (w) {
      // two writers at once on one file
      return h.createWritable().then(function (w2) {
        return w.write('FIRST').then(function () { return w2.write('SECOND'); })
          .then(function () { return w.close(); }).then(function () { return w2.close(); })
          .then(function () { return text(h); }).then(function (t) { out.twoWritersLastCloseWins = t.text; });
      }, function (e) { out.secondWriter = e.name + ': ' + e.message; return w.close(); });
    })
    .then(function () { return root.removeEntry(name); })
    .then(function () { return out; }, function (e) { out.error = e.name + ': ' + e.message; return out; });
}

function storeHandle() {
  return navigator.storage.getDirectory().then(function (root) { return root.getFileHandle('kept.acad3d.json', { create: true }); })
    .then(function (h) {
      return new Promise(function (res, rej) {
        var rq = indexedDB.open('e16', 1);
        rq.onupgradeneeded = function () { rq.result.createObjectStore('h'); };
        rq.onsuccess = function () {
          var db = rq.result, tx = db.transaction('h', 'readwrite');
          tx.objectStore('h').put(h, 'file'); tx.oncomplete = function () { db.close(); res('stored'); }; tx.onerror = function () { rej(tx.error); };
        };
        rq.onerror = function () { rej(rq.error); };
      });
    });
}
function readHandle() {
  return new Promise(function (res, rej) {
    var rq = indexedDB.open('e16', 1);
    rq.onupgradeneeded = function () { rq.result.createObjectStore('h'); };
    rq.onsuccess = function () {
      var db = rq.result, g = db.transaction('h').objectStore('h').get('file');
      g.onsuccess = function () { db.close(); res(g.result); }; g.onerror = function () { rej(g.error); };
    };
  }).then(function (h) {
    if (!h) return { found: false };
    return navigator.storage.getDirectory().then(function (root) { return root.getFileHandle('kept.acad3d.json'); })
      .then(function (fresh) { return Promise.all([h.isSameEntry(fresh), h.queryPermission({ mode: 'readwrite' })]); })
      .then(function (a) { return { found: true, kind: h.kind, name: h.name, ctor: h.constructor.name, isSameEntry: a[0], queryPermission: a[1] }; });
  }).catch(function (e) { return { error: e.name + ': ' + e.message }; });
}

(async function () {
  var srv = await L.startServer(0, { '/p.html': { body: PAGE } });
  var dir = L.tmpDir('e16-');
  var filePage = path.join(dir, 'p.html');
  fs.writeFileSync(filePage, PAGE);
  var browser = await pw.chromium.launch();
  var out = { version: browser.version(), pickers: {}, writable: [], handle: [] };
  var targets = { http: srv.origin + '/p.html', file: 'file://' + filePage };
  for (var k in targets) {
    var ctx = await browser.newContext(); var page = await ctx.newPage();
    await page.goto(targets[k]);
    out.pickers[k] = await pickerMatrix(page);
    await ctx.close();
  }
  console.log(JSON.stringify(out.pickers, null, 1));
  for (var run = 0; run < 5; run++) {
    var c2 = await browser.newContext(); var p2 = await c2.newPage();
    await p2.goto(srv.origin + '/p.html');
    out.writable.push(await p2.evaluate(writable));
    await c2.close();
  }
  console.log('writable runs:', JSON.stringify(out.writable[0]));
  console.log('all writable runs identical:', out.writable.every(function (r) { return JSON.stringify(Object.assign({}, r, { afterFirstClose: r.afterFirstClose && r.afterFirstClose.text })) === JSON.stringify(Object.assign({}, out.writable[0], { afterFirstClose: out.writable[0].afterFirstClose && out.writable[0].afterFirstClose.text })); }));
  await browser.close();
  for (var r3 = 0; r3 < 3; r3++) {
    var prof = L.tmpDir('e16-prof-');
    var pc = await pw.chromium.launchPersistentContext(prof);
    var pp = pc.pages()[0] || await pc.newPage();
    await pp.goto(srv.origin + '/p.html');
    var stored = await pp.evaluate(storeHandle);
    await pc.close();
    pc = await pw.chromium.launchPersistentContext(prof);
    pp = pc.pages()[0] || await pc.newPage();
    await pp.goto(srv.origin + '/p.html');
    var back = await pp.evaluate(readHandle);
    out.handle.push({ stored: stored, afterRestart: back });
    await pc.close(); L.rm(prof);
  }
  console.log('handle after restart:', JSON.stringify(out.handle));
  L.save('e16', out);
  srv.server.close(); L.rm(dir);
})().catch(function (e) { console.error(e); process.exit(1); });
