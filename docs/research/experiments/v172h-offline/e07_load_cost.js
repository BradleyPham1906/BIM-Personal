// e07_load_cost.js -- the worker's cost on the app's loads (V172h, 2026-11-07).
// Per run, a fresh context, the real app at /BIM-Personal/:
//   no worker:   first load; repeat load (goto again, Pages' 600 s HTTP cache fresh); repeat after the HTTP cache is
//                cleared (CDP Network.clearBrowserCache: everything fetched again).
//   with worker: first load, then register and wait for ready (the precache); repeat load (now controlled);
//                repeat after the HTTP cache is cleared (the page from the network, the four files from the worker);
//                offline load (server stopped, HTTP cache cleared).
// For each load: the navigation entry's domContentLoadedEventEnd and loadEventEnd (ms from the navigation's start),
// the driver's time from goto to the store open, bytes the server sent, and per app file its transferSize and
// whether a worker handled it (workerStart > 0). RUNS runs (default 7).
'use strict';
var C = require('./_common.js');
var pw = require('playwright');
var RUNS = +process.env.RUNS || 7;

async function load(p, S, label) {
  var b0 = S.bytesOut, t0 = Date.now(), r = { label: label };
  try { await p.goto(S.origin + '/BIM-Personal/'); } catch (e) { r.error = String(e.message).split('\n')[0]; return r; }
  var rd = await C.appReady(p);
  r.toStoreMs = Date.now() - t0; r.mode = rd.mode;
  var nav = await p.evaluate(function () {
    var n = performance.getEntriesByType('navigation')[0];
    var res = performance.getEntriesByType('resource').filter(function (x) { return /\/app\//.test(x.name); }).map(function (x) {
      return { f: x.name.replace(/^.*\/app\//, ''), transfer: x.transferSize, viaWorker: x.workerStart > 0, dur: Math.round(x.duration) };
    });
    return { dcl: Math.round(n.domContentLoadedEventEnd), load: Math.round(n.loadEventEnd), navTransfer: n.transferSize, navViaWorker: n.workerStart > 0, res: res };
  });
  r.dcl = nav.dcl; r.load = nav.load; r.navTransfer = nav.navTransfer; r.navViaWorker = nav.navViaWorker; r.res = nav.res;
  r.serverBytes = S.bytesOut - b0;
  return r;
}
async function clearHttp(p) { var c = await p.context().newCDPSession(p); await c.send('Network.clearBrowserCache'); await c.detach(); }

(async function () {
  var A = C.buildA();
  var S = await C.serve({ build: A, port: 8175 });
  S.override('/BIM-Personal/sw.js', { body: C.appSw(A) });
  var browser = await pw.chromium.launch();
  var out = { chromium: browser.version(), runs: [] };
  for (var r = 0; r < RUNS; r++) {
    var run = { noWorker: [], withWorker: [] };
    var ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
    var p = await ctx.newPage();
    run.noWorker.push(await load(p, S, 'first'));
    run.noWorker.push(await load(p, S, 'repeat'));
    await clearHttp(p);
    run.noWorker.push(await load(p, S, 'repeat, HTTP cache cleared'));
    await ctx.close();

    ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
    p = await ctx.newPage();
    run.withWorker.push(await load(p, S, 'first'));
    var b0 = S.bytesOut, t0 = Date.now();
    await p.evaluate(function () { return navigator.serviceWorker.register('sw.js').then(function () { return navigator.serviceWorker.ready; }).then(function () { return 1; }); });
    run.precache = { ms: Date.now() - t0, serverBytes: S.bytesOut - b0 };
    run.withWorker.push(await load(p, S, 'repeat'));
    await clearHttp(p);
    run.withWorker.push(await load(p, S, 'repeat, HTTP cache cleared'));
    await clearHttp(p);
    await S.stop();
    run.withWorker.push(await load(p, S, 'offline (server stopped, HTTP cache cleared)'));
    await S.start();
    await ctx.close();
    out.runs.push(run);
    console.log('run ' + r + ': no worker ' + run.noWorker.map(function (x) { return x.label + ' load=' + x.load + ' store=' + x.toStoreMs + ' bytes=' + x.serverBytes; }).join('; ') +
      '\n  worker ' + run.withWorker.map(function (x) { return x.label + ' load=' + x.load + ' store=' + x.toStoreMs + ' bytes=' + x.serverBytes + (x.error ? ' ' + x.error : ''); }).join('; ') +
      '\n  precache ' + JSON.stringify(run.precache));
  }
  await browser.close();
  await S.stop();
  C.save('e07_load_cost', out);
})().catch(function (e) { console.error(e); process.exit(1); });
