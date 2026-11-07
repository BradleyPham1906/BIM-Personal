// e15_old_builds.js -- V172f, hypotheses H25 to H27 (2026-11-02).
// Question: the site keeps every older build under /BIM-Personal/v/<version>/, on the same origin as the app
// (research-local-storage.md 4.9), and copies of older files open from file:// in Chromium share one store. What
// does an older build do to storage written by a newer one, and can a small script put before an older build's
// own code keep it from changing anything?
// Method: the kept builds (Phase/, now in git history) served over http from localhost, as the site serves them: V114 (one project,
// before V115's tabs), V172 (projects in localStorage, before V172d), V172d and V172e (the database for what
// localStorage refuses). Storage is seeded from a blank page of the same origin (the V115 rule), never by an init
// script; the one init script only watches the toast. Cases:
//   A  acad3dV1 holds a V172d pointer (no record): does V172 save over it, at start or at the first edit?
//   B  only a newer build's own key is there ('acad3dProjectsV2', a stand-in): what does each build write at
//      start, without an edit, and after one?
//   C  the database is at version 2 (V172d and V172e open version 1): what do V172d and V172e say and write?
//   D  the guard: the build's page with a script first in <head> that gives the page a copy of localStorage in
//      memory and a database that refuses; does the build start without page errors, read the stored project,
//      take an edit, and leave the real localStorage and IndexedDB exactly as they were?
'use strict';
var pw = require('playwright');
var fs = require('fs');
var path = require('path');
var L = require('./_lib');

var ROOT = path.resolve(__dirname, '../../../..');
// The pre-phase backups were removed with Phase/ on 2026-11-07 (PR #65); they are read from git history at
// 9dc7b87, the last commit that had them, into the scratch folder.
var KEPT = '9dc7b87';
var cp = require('child_process');
function fromGit(name) {
  var out = path.join(L.SCRATCH, 'e15-' + name.replace(/\//g, '_'));
  if (!fs.existsSync(out)) fs.writeFileSync(out, cp.execFileSync('git', ['-C', ROOT, 'show', KEPT + ':' + name], { maxBuffer: 1 << 28 }));
  return out;
}
var BUILDS = {
  v114: fromGit('Phase/canvas_v10.html.bak_phase115_pre'),
  v172: fromGit('Phase/canvas_v10.html.bak_phase172d_pre'),
  v172d: fromGit('Phase/canvas_v10.html.bak_phase172e_pre'),
  v172e: fromGit('canvas_v10.html')   // V172e: the build at 9dc7b87 itself
};

// the guard, ES5: a copy of localStorage in memory for the page's life; IndexedDB answers every open with an error
var GUARD = '<script>(function(){try{' +
  'var real=window.localStorage,mem={},i,k;' +
  'try{for(i=0;i<real.length;i++){k=real.key(i);if(k!==null)mem[k]=real.getItem(k);}}catch(e0){}' +
  'function has(k){return Object.prototype.hasOwnProperty.call(mem,k);}' +
  'var fake={getItem:function(k){k=String(k);return has(k)?mem[k]:null;},' +
  ' setItem:function(k,v){mem[String(k)]=String(v);},removeItem:function(k){delete mem[String(k)];},' +
  ' clear:function(){mem={};},key:function(n){var ks=Object.keys(mem);return n>=0&&n<ks.length?ks[n]:null;}};' +
  'Object.defineProperty(fake,"length",{get:function(){return Object.keys(mem).length;}});' +
  'Object.defineProperty(window,"localStorage",{configurable:true,get:function(){return fake;}});' +
  'var refuse={open:function(){var r={result:null,error:null,onsuccess:null,onerror:null,onupgradeneeded:null,onblocked:null};' +
  ' setTimeout(function(){r.error=new Error("This older version keeps nothing in this browser");if(r.onerror)r.onerror({target:r});},0);return r;},' +
  ' deleteDatabase:function(){var r={};setTimeout(function(){if(r.onerror)r.onerror({target:r});},0);return r;}};' +
  'Object.defineProperty(window,"indexedDB",{configurable:true,get:function(){return refuse;}});' +
  'window.__guarded=(window.localStorage===fake)&&(window.indexedDB===refuse);' +
  '}catch(e){window.__guardError=String(e);}})();</script>';

function guarded(file) {
  var t = fs.readFileSync(file, 'utf8');
  var at = t.indexOf('<head>');
  if (at < 0 || at > 1000) throw new Error('no <head> near the start of ' + file);
  return t.slice(0, at + 6) + GUARD + t.slice(at + 6);
}

var POINTER = JSON.stringify({ idb: 1, docId: 'doc-real', titleBlock: { project: 'Real' }, count: 5, saved: 1 });
var LIST = JSON.stringify({ v: 1, active: 'doc-real', open: ['doc-real'], docs: [{ id: 'doc-real', name: 'Real', objs: 5, saved: 1 }] });

(async function () {
  var dir = L.tmpDir('e15-');
  var routes = {};
  Object.keys(BUILDS).forEach(function (k) {
    routes['/old/' + k] = { file: BUILDS[k] };
    var g = path.join(dir, k + '.html');
    fs.writeFileSync(g, guarded(BUILDS[k]));
    routes['/guard/' + k] = { file: g };
  });
  var srv = await L.startServer(0, routes);
  var browser = await pw.chromium.launch();
  var out = { version: browser.version(), date: new Date().toISOString(), cases: {} };

  async function fresh() {
    var ctx = await browser.newContext({ viewport: { width: 1500, height: 950 } });
    var p = await ctx.newPage();
    p.__errs = [];
    p.on('pageerror', function (e) { p.__errs.push(String(e).slice(0, 160)); });
    await p.addInitScript("(function(){window.__toasts=[];new MutationObserver(function(){var t=document.getElementById('a3d-toast');" +
      "if(t&&t.textContent&&window.__toasts[window.__toasts.length-1]!==t.textContent)window.__toasts.push(t.textContent);})" +
      ".observe(document,{subtree:true,childList:true,characterData:true});})();");
    await p.goto(srv.origin + '/blank');
    return { ctx: ctx, p: p };
  }
  async function dump(p) {
    await p.goto(srv.origin + '/blank');
    return await p.evaluate(function () {
      var o = {}, i, k; for (i = 0; i < localStorage.length; i++) { k = localStorage.key(i); o[k] = localStorage.getItem(k); }
      return (indexedDB.databases ? indexedDB.databases() : Promise.resolve([])).then(function (d) { return { ls: o, dbs: d.map(function (x) { return x.name + '@' + x.version; }) }; });
    });
  }
  function short(ls) {
    var o = {};
    Object.keys(ls).sort().forEach(function (k) {
      var v = ls[k]; var j = null; try { j = JSON.parse(v); } catch (e) {}
      o[k] = j && typeof j === 'object' ? (j.idb === 1 ? 'pointer(' + j.docId + ')' : Array.isArray(j.objs) ? 'record(' + j.objs.length + ' objs, docId ' + j.docId + ')' : Array.isArray(j.docs) ? 'list(' + j.docs.length + ', active ' + j.active + ')' : 'json ' + v.length) : 'text ' + String(v).length;
    });
    return o;
  }
  async function openBuild(p, url) {
    await p.goto(url);
    for (var i = 0; i < 80; i++) { if (await p.evaluate(function () { return !!window.__a3dOn; })) break; await p.waitForTimeout(100); }
    await p.waitForTimeout(1500);
  }
  async function wall(p) {
    var id = await p.evaluate(function () { return window.__a3dWall ? window.__a3dWall([[0, 0], [4, 0]], 0.3, 3, 'center', false) : 'no __a3dWall'; });
    await p.waitForTimeout(1200);
    return id;
  }

  // A: a V172d pointer in acad3dV1, opened by V172
  var A = await fresh();
  await A.p.evaluate(function (a) { localStorage.clear(); localStorage.setItem('acad3dV1', a.ptr); localStorage.setItem('acad3dDocsV1', a.list); }, { ptr: POINTER, list: LIST });
  await openBuild(A.p, srv.origin + '/old/v172');
  var objsA = await A.p.evaluate(function () { return window.__a3dObjects ? window.__a3dObjects().length : null; });
  var afterStart = short((await dump(A.p)).ls);
  await openBuild(A.p, srv.origin + '/old/v172');
  var w = await wall(A.p);
  out.cases.A = { objsOnScreen: objsA, afterStart: afterStart, wall: w, afterEdit: short((await dump(A.p)).ls), errors: A.p.__errs };
  console.log('A ' + JSON.stringify(out.cases.A));
  await A.ctx.close();

  // B: only a newer build's own key
  var builds = ['v114', 'v172', 'v172d', 'v172e'];
  out.cases.B = {};
  for (var b = 0; b < builds.length; b++) {
    var B = await fresh();
    await B.p.evaluate(function () { localStorage.clear(); localStorage.setItem('acad3dProjectsV2', '{"v":2}'); localStorage.setItem('acad3dTheme', 'dark'); });
    await openBuild(B.p, srv.origin + '/old/' + builds[b]);
    var s1 = short((await dump(B.p)).ls);
    await openBuild(B.p, srv.origin + '/old/' + builds[b]);
    var w2 = await wall(B.p);
    var s2 = short((await dump(B.p)).ls);
    out.cases.B[builds[b]] = { atStart: s1, wall: w2, afterEdit: s2, errors: B.p.__errs };
    console.log('B ' + builds[b] + ' ' + JSON.stringify(out.cases.B[builds[b]]));
    await B.ctx.close();
  }

  // C: the database at version 2, a pointer in acad3dV1, opened by V172d and V172e
  out.cases.C = {};
  var cb = ['v172d', 'v172e'];
  for (var c = 0; c < cb.length; c++) {
    var C = await fresh();
    await C.p.evaluate(function (a) {
      localStorage.clear(); localStorage.setItem('acad3dV1', a.ptr); localStorage.setItem('acad3dDocsV1', a.list);
      return new Promise(function (res) {
        var r = indexedDB.open('BIM-Personal', 2);
        r.onupgradeneeded = function () { r.result.createObjectStore('projects'); };
        r.onsuccess = function () { var db = r.result, t = db.transaction('projects', 'readwrite');
          t.objectStore('projects').put({ rec: '{"objs":[]}', saved: 1, v: 1 }, 'doc-real'); t.oncomplete = function () { db.close(); res(true); }; };
      });
    }, { ptr: POINTER, list: LIST });
    await openBuild(C.p, srv.origin + '/old/' + cb[c]);
    var toasts = await C.p.evaluate(function () { return window.__toasts; });
    var w3 = await wall(C.p);
    var toasts2 = await C.p.evaluate(function () { return window.__toasts; });
    var d3 = await dump(C.p);
    out.cases.C[cb[c]] = { toastsAtStart: toasts, wall: w3, toastsAfterEdit: toasts2, after: short(d3.ls), dbs: d3.dbs, errors: C.p.__errs };
    console.log('C ' + cb[c] + ' ' + JSON.stringify(out.cases.C[cb[c]]));
    await C.ctx.close();
  }

  // D: the guard
  out.cases.D = {};
  for (var d = 0; d < builds.length; d++) {
    var D = await fresh();
    var legacy = null;
    // a small project with one wall, saved by V172 itself, so the record is in that build's own format
    await openBuild(D.p, srv.origin + '/old/v172');
    await wall(D.p);
    var before = await dump(D.p);
    await openBuild(D.p, srv.origin + '/guard/' + builds[d]);
    var g = await D.p.evaluate(function () { return { guarded: window.__guarded, error: window.__guardError || null, objs: window.__a3dObjects ? window.__a3dObjects().length : null }; });
    var w4 = await wall(D.p);
    var g2 = await D.p.evaluate(function () { return { objs: window.__a3dObjects ? window.__a3dObjects().length : null, inMemory: localStorage.getItem('acad3dV1') ? localStorage.getItem('acad3dV1').length : null }; });
    var after = await dump(D.p);
    var same = JSON.stringify(before.ls) === JSON.stringify(after.ls) && JSON.stringify(before.dbs) === JSON.stringify(after.dbs);
    out.cases.D[builds[d]] = { guard: g, wall: w4, afterEdit: g2, realStorageUnchanged: same, dbsBefore: before.dbs, dbsAfter: after.dbs, errors: D.p.__errs };
    console.log('D ' + builds[d] + ' ' + JSON.stringify(out.cases.D[builds[d]]));
    await D.ctx.close();
  }
  await browser.close();
  srv.server.close();
  L.rm(dir);
  L.save('e15_old_builds', out);
})();
