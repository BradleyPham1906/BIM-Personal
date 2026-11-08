// e05_worker_fetch.js -- H47 (V172h, 2026-11-07): fetches made by a dedicated Web Worker that a controlled page
// created go through the page's service worker.
// Part 1 (probe worker): a controlled page makes (a) a same-origin worker from a script URL, (b) a blob: URL worker
//   made the way src/js/engine/ladybug/runtime.js makes its worker (new Worker(URL.createObjectURL(new Blob([text],
//   {type:'text/javascript'})))). Each worker fetch()es /BIM-Personal/__probe and importScripts() it; the probe
//   worker answers both itself when it sees them. Also the same from an uncontrolled page (control).
// Part 2 (the real app and the experiment worker): online, the Ladybug runtime is started (__a3dLbStart: Pyodide
//   and the wheels, 16 MB, fetched by the app's blob: worker); the experiment worker caches runtime/ cache-first.
//   Then the HTTP cache is cleared and the server stopped, the app reloaded offline, and the runtime started again.
// RUNS runs of each part (default 3).
'use strict';
var C = require('./_common.js');
var pw = require('playwright');
var RUNS = +process.env.RUNS || 3;

var WORKER_TEXT = 'onmessage=function(e){var u=e.data,r={};' +
  'try{importScripts(u+"?as=js&from=importScripts");r.importScripts=self.__probeResult||"no result";}catch(x){r.importScripts="ERR "+x.message;}' +
  'fetch(u+"?from=fetch").then(function(x){return x.text();}).then(function(t){r.fetch=t.indexOf("viaSW")>=0?JSON.parse(t):("network: "+t.slice(0,30));' +
  'r.location=String(self.location).slice(0,40);postMessage(r);},function(x){r.fetch="ERR "+x;postMessage(r);});};';

(async function () {
  var A = C.buildA();
  var S = await C.serve({ build: A, port: 8174 });
  S.override('/BIM-Personal/t.html', { body: C.page('') });
  S.override('/BIM-Personal/wk.js', { body: WORKER_TEXT });
  var browser = await pw.chromium.launch();
  var out = { chromium: browser.version(), probe: [], runtime: [] };
  var probeUrl = S.origin + '/BIM-Personal/__probe';

  for (var r = 0; r < RUNS; r++) {
    S.override('/BIM-Personal/sw.js', { body: C.probeSw('A') });
    var ctx = await browser.newContext();
    var p = await ctx.newPage();
    await p.goto(S.origin + '/BIM-Personal/t.html');
    var uncontrolled = await p.evaluate(runBoth, { url: probeUrl, text: WORKER_TEXT });
    await p.evaluate(function () { return window.__register('/BIM-Personal/sw.js'); });
    await p.evaluate(function () { return navigator.serviceWorker.ready.then(function () { return 1; }); });
    await p.reload();
    var controlled = await p.evaluate(runBoth, { url: probeUrl, text: WORKER_TEXT });
    var seen = await p.evaluate(function () {
      return window.__ask(navigator.serviceWorker.controller, { type: 'SEEN' }).then(function (x) {
        return x.seen.filter(function (s) { return /wk\.js|__probe/.test(s.url); }).map(function (s) { return s.url + ' dest=' + s.dest + ' mode=' + s.mode; });
      });
    });
    out.probe.push({ pageControlledAfterReload: true, uncontrolled: uncontrolled, controlled: controlled, swSaw: seen });
    await ctx.close();
    console.log('probe run ' + r + ': ' + JSON.stringify({ uncontrolled: uncontrolled, controlled: controlled }));
  }

  for (r = 0; r < RUNS; r++) {
    S.override('/BIM-Personal/sw.js', { body: C.appSw(A) });
    ctx = await browser.newContext();
    p = await ctx.newPage();
    var errs = [];
    p.on('pageerror', function (e) { errs.push(String(e.message).slice(0, 160)); });
    var run = {};
    await p.goto(S.origin + '/BIM-Personal/');
    await C.appReady(p);
    await p.evaluate(function () { return navigator.serviceWorker.register('sw.js').then(function () { return navigator.serviceWorker.ready; }).then(function () { return 1; }); });
    await p.reload();
    await C.appReady(p);
    run.base = await p.evaluate(function () { return window.__a3dLbBase(); });
    S.resetHits();
    var t0 = Date.now();
    run.online = await p.evaluate(function () { return window.__a3dLbStart(); }).catch(function (e) { return 'ERR ' + e.message; });
    run.onlineMs = Date.now() - t0;
    run.onlineRuntimeHits = S.count(/\/runtime\//);
    await C.sleep(1000);
    run.runtimeCacheEntries = await p.evaluate(function () {
      return caches.open('bim-runtime-v1').then(function (c) { return c.keys(); }).then(function (k) { return k.map(function (x) { return x.url.replace(/^.*\/runtime\//, ''); }); });
    });
    var cdp = await ctx.newCDPSession(p); await cdp.send('Network.clearBrowserCache'); await cdp.detach();
    await S.stop();
    await p.goto(S.origin + '/BIM-Personal/').catch(function (e) { run.offlineGoto = String(e.message).split('\n')[0]; });
    run.offlineApp = await C.appReady(p);
    t0 = Date.now();
    run.offline = await p.evaluate(function () { return window.__a3dLbStart(); }).catch(function (e) { return 'ERR ' + e.message; });
    run.offlineMs = Date.now() - t0;
    run.pageErrors = errs;
    await S.start();
    out.runtime.push(run);
    await ctx.close();
    console.log('runtime run ' + r + ': online ' + run.onlineMs + ' ms (' + run.onlineRuntimeHits + ' runtime hits, ' + run.runtimeCacheEntries.length +
      ' cached) ' + JSON.stringify(run.online).slice(0, 160) + ' | offline ' + run.offlineMs + ' ms ' + JSON.stringify(run.offline).slice(0, 200));
  }
  await browser.close();
  await S.stop();
  C.save('e05_worker_fetch', out);
})().catch(function (e) { console.error(e); process.exit(1); });

// in the page: run the probe from a script-URL worker and from a blob: worker
function runBoth(a) {
  function run(w) {
    return new Promise(function (res) {
      var done = false;
      w.onmessage = function (e) { done = true; w.terminate(); res(e.data); };
      w.onerror = function (e) { if (!done) res('worker error ' + (e.message || '')); };
      w.postMessage(a.url);
      setTimeout(function () { if (!done) res('timeout'); }, 5000);
    });
  }
  return run(new Worker('/BIM-Personal/wk.js')).then(function (x) {
    return run(new Worker(URL.createObjectURL(new Blob([a.text], { type: 'text/javascript' })))).then(function (y) {
      return { controlledPage: !!navigator.serviceWorker.controller, scriptUrlWorker: x, blobWorker: y };
    });
  });
}
