// e03_offline_app.js -- H32 (V172h, 2026-11-07): after one online visit with the experiment worker installed,
// the real built app opens with no network, its project (saved before going offline) reads back from IndexedDB,
// and an edit saves. Two ways of being offline:
//   'emulated': Playwright's context.setOffline(true) (Chromium's network emulation), server still up;
//   'stopped':  the server stopped (connection refused), browser online.
// Each offline visit is made with the HTTP cache as the online visit left it (Pages' max-age=600 still fresh)
// and after clearing the HTTP cache through CDP (Network.clearBrowserCache, which leaves Cache Storage alone):
// the state of a visit more than 600 s later, when the HTTP cache can no longer answer by itself.
// Control: the same steps with no worker registered (expected: the page does not open offline).
// Records: time from goto to the store open, the walls read back and saved, page errors, console errors and
// failed requests (with their hosts). RUNS fresh contexts (default 3).
'use strict';
var C = require('./_common.js');
var pw = require('playwright');
var RUNS = +process.env.RUNS || 3;

function host(u) { try { return new URL(u).host; } catch (e) { return u.slice(0, 40); } }

async function offlineVisit(p, S, how, wallId, pid, log, clear) {
  log.length = 0;
  if (clear) { var cdp = await p.context().newCDPSession(p); await cdp.send('Network.clearBrowserCache'); await cdp.detach(); }
  if (how === 'emulated') await p.context().setOffline(true); else await S.stop();
  var t0 = Date.now(), res = { how: how + (clear ? '+httpCacheCleared' : '+httpCacheFresh') };
  try { await p.goto(S.origin + '/BIM-Personal/', { timeout: 15000 }); res.opened = true; }
  catch (e) { res.opened = false; res.gotoError = String(e.message).split('\n')[0]; }
  res.url = p.url();
  if (res.opened) {
    var rd = await C.appReady(p, 20000);
    res.storeMode = rd.mode; res.readyMs = Date.now() - t0;
    await C.sleep(1500);
    res.controlled = await p.evaluate(function () { return !!navigator.serviceWorker.controller; }).catch(function () { return null; });
    res.activeProject = await p.evaluate(function () { return window.__a3dDocs ? window.__a3dDocs.active() : null; }).catch(function () { return null; });
    res.sameProject = res.activeProject === pid;
    res.wallOnScreen = await p.evaluate(function (id) { return window.__a3dObjects().some(function (o) { return o.id === id; }); }, wallId).catch(function () { return null; });
    var w2 = await p.evaluate(function () { return window.__a3dWall([[0, 6], [5, 6]], 0.2, 3, 'center', false); }).catch(function (e) { return 'ERR ' + e.message; });
    res.newWall = w2 && w2.id ? w2.id : w2;
    await C.sleep(1500);
    res.newWallStored = await p.evaluate(function (a) {
      return window.__a3dStoredGet(a.pid).then(function (v) { return !!(v && v.rec && v.rec.indexOf(a.id) >= 0); });
    }, { pid: pid, id: res.newWall }).catch(function (e) { return 'ERR ' + e.message; });
    res.store = await p.evaluate(function () { return window.__a3dStore(); }).catch(function () { return null; });
  }
  res.pageErrors = log.filter(function (x) { return x.k === 'pageerror'; }).map(function (x) { return x.m; });
  res.consoleErrors = log.filter(function (x) { return x.k === 'console'; }).map(function (x) { return x.m; });
  res.failedHosts = {};
  log.filter(function (x) { return x.k === 'requestfailed'; }).forEach(function (x) {
    var h = host(x.m); res.failedHosts[h] = (res.failedHosts[h] || 0) + 1;
  });
  res.failedSameOrigin = log.filter(function (x) { return x.k === 'requestfailed' && x.m.indexOf(S.origin) === 0; }).map(function (x) { return x.m.replace(S.origin, '') + ' ' + x.e; });
  if (how === 'emulated') await p.context().setOffline(false); else await S.start();
  return res;
}

(async function () {
  var A = C.buildA();
  var S = await C.serve({ build: A, port: 8173 });
  S.override('/BIM-Personal/sw.js', { body: C.appSw(A) });
  var browser = await pw.chromium.launch();
  var out = { chromium: browser.version(), runs: [] };
  for (var r = 0; r < RUNS; r++) {
    for (var withSw = 1; withSw >= 0; withSw--) {
      var ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
      var p = await ctx.newPage();
      var log = [];
      p.on('pageerror', function (e) { log.push({ k: 'pageerror', m: String(e.message).slice(0, 200) }); });
      p.on('console', function (m) { if (m.type() === 'error') log.push({ k: 'console', m: m.text().slice(0, 200) }); });
      p.on('requestfailed', function (q) { log.push({ k: 'requestfailed', m: q.url(), e: (q.failure() || {}).errorText }); });
      var run = { worker: !!withSw };
      await p.goto(S.origin + '/BIM-Personal/');
      run.online = await C.appReady(p);
      if (withSw) {
        await p.evaluate(function () { return navigator.serviceWorker.register('sw.js').then(function () { return navigator.serviceWorker.ready; }).then(function () { return 1; }); });
      }
      var w = await p.evaluate(function () { return window.__a3dWall([[0, 0], [4, 0]], 0.3, 3, 'center', false); });
      run.wallId = w && w.id ? w.id : w;
      await C.sleep(1500);
      run.pid = await p.evaluate(function () { return window.__a3dDocs.active(); });
      run.storedOnline = await p.evaluate(function (a) {
        return window.__a3dStoredGet(a.pid).then(function (v) { return !!(v && v.rec && v.rec.indexOf(a.id) >= 0); });
      }, { pid: run.pid, id: run.wallId });
      run.onlineErrors = log.slice();
      run.offline = [];
      run.offline.push(await offlineVisit(p, S, 'emulated', run.wallId, run.pid, log, false));
      run.offline.push(await offlineVisit(p, S, 'emulated', run.wallId, run.pid, log, true));
      run.offline.push(await offlineVisit(p, S, 'stopped', run.wallId, run.pid, log, true));
      out.runs.push(run);
      await ctx.close();
      console.log('run ' + r + (withSw ? ' with' : ' without') + ' worker: ' + run.offline.map(function (o) {
        return o.how + ' opened=' + o.opened + ' ready=' + o.readyMs + 'ms mode=' + o.storeMode + ' controlled=' + o.controlled +
          ' wall=' + o.wallOnScreen + ' saved=' + o.newWallStored + ' pageErr=' + (o.pageErrors || []).length +
          ' consoleErr=' + (o.consoleErrors || []).length + ' failed=' + JSON.stringify(o.failedHosts) + (o.gotoError ? ' ' + o.gotoError : '');
      }).join(' | '));
    }
  }
  await browser.close();
  await S.stop();
  C.save('e03_offline_app', out);
})().catch(function (e) { console.error(e); process.exit(1); });
