// e04_update.js -- H44, H45, H46 (V172h, 2026-11-07): how a new worker (build B, byte-different sw.js) reaches tabs.
// The probe worker (no skipWaiting of its own) is served at /BIM-Personal/sw.js; pages are /BIM-Personal/t.html
// with exp.js. Each scenario runs in a fresh context; RUNS runs each (default 5).
//   one-tab:  A controls one tab; B deployed; reload (finds B: updatefound, B waits); reload again; then the tab
//             navigates away (to /Other/) and back; then the tab is closed and a new one opened.
//   two-tabs: A controls two tabs; B deployed; tab 1 reloads twice; tab 2 is closed; tab 1 reloads; tab 1 closed,
//             a new tab opened.
//   message:  (H45) one tab with unsaved work (window.__dirty) and B waiting: __applyUpdate() must hold; when clean,
//             it posts SKIP_WAITING; controllerchange reloads once; the reload count is checked 3 s later (no loop).
//             A second tab with unsaved work open at the same time: what happens to it.
//   hits:     (H46) sw.js server hits on 5 navigations 4 s apart, within the 600 s max-age, with updateViaCache default
//             and 'all'; each hit is put down to the last navigation started before it.
// Time from navigation to updatefound is the page's performance.now() at updatefound (0 = the navigation's start).
'use strict';
var C = require('./_common.js');
var pw = require('playwright');
var RUNS = +process.env.RUNS || 5;

function st(p) { return p.evaluate(function () { return window.__state(); }); }
async function until(p, fn, ms) {
  var t0 = Date.now(), s;
  while (Date.now() - t0 < (ms || 10000)) { s = await st(p); if (fn(s)) return s; await C.sleep(100); }
  return s;
}
function v(x) { return x && x.version ? x.version : x; }
function short(s) { return { controller: v(s.controller), active: v(s.active), waiting: v(s.waiting), installing: s.installing, reloads: s.reloads, cc: s.cc }; }

(async function () {
  var A = C.buildA();
  var S = await C.serve({ build: A });
  S.override('/BIM-Personal/t.html', { body: C.page('') });
  var fs = require('fs'), path = require('path');
  var other = path.join(C.SCRATCH, 'other');
  fs.mkdirSync(other, { recursive: true });
  fs.writeFileSync(path.join(other, 'index.html'), C.page(''));
  S.other = other;
  var T = S.origin + '/BIM-Personal/t.html';
  var browser = await pw.chromium.launch();
  var out = { chromium: browser.version(), oneTab: [], twoTabs: [], message: [], hits: [] };

  async function setupA(ctx, opts) {
    S.override('/BIM-Personal/sw.js', { body: C.probeSw('A') });
    var p = await ctx.newPage();
    await p.goto(T);
    await p.evaluate(function (o) { return window.__register('/BIM-Personal/sw.js', o); }, opts || {});
    await p.evaluate(function () { return navigator.serviceWorker.ready.then(function () { return 1; }); });
    await p.reload();
    await until(p, function (s) { return v(s.controller) === 'A'; });
    return p;
  }
  function deployB() { S.override('/BIM-Personal/sw.js', { body: C.probeSw('B') }); }

  for (var r = 0; r < RUNS; r++) {
    // ---- one tab
    var ctx = await browser.newContext(), run = { steps: {} };
    var p = await setupA(ctx);
    deployB();
    await p.reload();
    var s = await until(p, function (x) { return v(x.waiting) === 'B'; });
    run.updatefoundMs = await p.evaluate(function () { return window.__updatefoundAt ? Math.round(window.__updatefoundAt) : null; });
    run.installedMs = await p.evaluate(function () { return window.__installedAt ? Math.round(window.__installedAt) : null; });
    run.steps.afterFirstReload = short(s);
    await p.reload(); await C.sleep(800);
    run.steps.afterSecondReload = short(await st(p));
    await p.goto(S.origin + '/Other/'); await C.sleep(800);
    await p.goto(T); await C.sleep(800);
    run.steps.afterAwayAndBack = short(await st(p));
    await p.close();
    await C.sleep(500);
    var p2 = await ctx.newPage(); await p2.goto(T);
    run.steps.afterCloseNewTab = short(await until(p2, function (x) { return v(x.controller) === 'B'; }, 5000));
    out.oneTab.push(run);
    await ctx.close();

    // ---- two tabs
    ctx = await browser.newContext(); run = { steps: {} };
    var t1 = await setupA(ctx);
    var t2 = await ctx.newPage(); await t2.goto(T);
    await until(t2, function (x) { return v(x.controller) === 'A'; });
    deployB();
    await t1.reload();
    run.steps.t1Reload1 = short(await until(t1, function (x) { return v(x.waiting) === 'B'; }));
    await t1.reload(); await C.sleep(800);
    run.steps.t1Reload2 = short(await st(t1));
    run.steps.t2Meanwhile = short(await st(t2));
    await t2.close(); await C.sleep(500);
    await t1.reload(); await C.sleep(800);
    run.steps.t1ReloadAfterT2Closed = short(await st(t1));
    await t1.close(); await C.sleep(500);
    var t3 = await ctx.newPage(); await t3.goto(T);
    run.steps.newTabAfterAllClosed = short(await until(t3, function (x) { return v(x.controller) === 'B'; }, 5000));
    out.twoTabs.push(run);
    await ctx.close();

    // ---- H45: messaging the waiting worker, held while dirty, one reload, no loop; a second, dirty tab
    ctx = await browser.newContext(); run = {};
    var m1 = await setupA(ctx);
    var m2 = await ctx.newPage(); await m2.goto(T);
    await until(m2, function (x) { return v(x.controller) === 'A'; });
    await m2.evaluate(function () { window.__dirty = true; });
    deployB();
    await m1.reload();
    await until(m1, function (x) { return v(x.waiting) === 'B'; });
    await m1.evaluate(function () { window.__dirty = true; });
    run.whileDirty = await m1.evaluate(function () { return window.__applyUpdate(); });
    await C.sleep(800);
    run.afterHeld = short(await st(m1));
    await m1.evaluate(function () { window.__dirty = false; });
    var tAsk = Date.now();
    run.whenClean = await m1.evaluate(function () { return window.__applyUpdate(); });
    await m1.waitForEvent('load', { timeout: 10000 }).catch(function () {});
    run.askToReloadMs = Date.now() - tAsk;
    var after = await until(m1, function (x) { return v(x.controller) === 'B'; }, 5000);
    run.afterApply = short(after);
    await C.sleep(3000);
    run.after3s = short(await st(m1));
    var s2 = await st(m2);
    run.dirtyTab = short(s2);
    run.dirtyTabLog = s2.log.filter(function (l) { return /controllerchange/.test(l); });
    run.dirtyTabStillDirty = await m2.evaluate(function () { return window.__dirty; });
    run.dirtyTabProbe = await m2.evaluate(function () { return window.__probe('dirty-tab'); });
    out.message.push(run);
    await ctx.close();

    // ---- H46: sw.js hits on navigations inside the 600 s max-age
    var modes = [{}, { updateViaCache: 'all' }], hrun = {};
    for (var k = 0; k < modes.length; k++) {
      ctx = await browser.newContext();
      var hp = await setupA(ctx, modes[k]);
      await C.sleep(4000);
      S.resetHits();
      var navTimes = [];
      for (var n = 0; n < 5; n++) { navTimes.push(Date.now()); await hp.goto(T); await C.sleep(4000); }
      var hits = S.swHeaders.map(function (h) {
        var i = navTimes.length - 1; while (i > 0 && navTimes[i] > h.t) i--;
        return { afterNav: i + 1, msAfterNavStart: h.t - navTimes[i], cacheControl: h.headers['cache-control'] || null,
          ifNoneMatch: !!h.headers['if-none-match'], sw: h.headers['service-worker'] || null };
      });
      hrun[modes[k].updateViaCache || 'default(imports)'] = {
        updateViaCache: (await st(hp)).updateViaCache, navigations: 5, swHits: S.count(/\/sw\.js/), detail: hits
      };
      await ctx.close();
    }
    out.hits.push(hrun);
    console.log('run ' + r + ': updatefound ' + out.oneTab[r].updatefoundMs + ' ms; one tab ' + JSON.stringify(out.oneTab[r].steps) +
      '\n  two tabs ' + JSON.stringify(out.twoTabs[r].steps) + '\n  message ' + JSON.stringify(out.message[r]) + '\n  hits ' +
      JSON.stringify(Object.keys(hrun).map(function (q) { return q + ': ' + hrun[q].swHits + ' ' + hrun[q].updateViaCache; })));
  }
  await browser.close();
  await S.stop();
  C.save('e04_update', out);
})().catch(function (e) { console.error(e); process.exit(1); });
