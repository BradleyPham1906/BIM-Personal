// V172h browser check (2026-11-08, the owner's "you"): the built Pages site on the experiments' Pages stand-in
// (_server.js), Chromium 153 headless. node docs/research/experiments/v172h-offline/browser_check.js; builds go to the
// scratch folder named in SCR below (change it to any empty folder). 21 checks.
'use strict';
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const REPO = '/home/user/BIM-Personal';
const SCR = '/tmp/claude-0/-home-user-BIM-Personal/7ef9ec21-7e6e-54c5-bca1-4bc8d65ed6b9/scratchpad';
const SRV = require(REPO + '/docs/research/experiments/v172h-offline/_server.js');
const A = path.join(SCR, 'chk-A'), B = path.join(SCR, 'chk-B');
const results = []; const ok = (name, cond, info) => { results.push([cond ? 'PASS' : 'FAIL', name, info === undefined ? '' : JSON.stringify(info)]); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function build() {
  for (const d of [A, B]) fs.rmSync(d, { recursive: true, force: true });
  execFileSync('python3', ['tools/build_site.py', A], { cwd: REPO });
  fs.cpSync(A, B, { recursive: true });
  const sw = path.join(B, 'sw.js');
  fs.writeFileSync(sw, fs.readFileSync(sw, 'utf8').replace(/var BIM_SW_BUILD = '([0-9a-f]+)';/, "var BIM_SW_BUILD = '$1b';"));
}
async function boot(pg) {
  for (let i = 0; i < 100; i++) {
    const m = await pg.evaluate(() => window.__a3dStore ? window.__a3dStore().mode : null).catch(() => null);
    if (m) break; await sleep(100);
  }
  await sleep(800);
}
const off = (pg) => pg.evaluate(() => window.__a3dOffline ? window.__a3dOffline() : null).catch(() => null);
const objs = (pg) => pg.evaluate(() => window.__a3dObjs ? window.__a3dObjs().length : (window.A3D ? -1 : -2)).catch(() => null);
async function edit(pg, i) {
  await pg.evaluate((i) => { window.__a3dAddPoint(i, 0, i); window.__a3dTitleBlockSet(window.__a3dTitleBlockGet()); }, i);
}

(async () => {
  build();
  const S = SRV.create({ build: A }); await S.start();
  const url = S.origin + '/BIM-Personal/';
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  const errors = [];
  const watch = (pg, tag) => {
    pg.on('pageerror', (e) => errors.push(tag + ' pageerror: ' + e.message));
    pg.on('console', (m) => { if (m.type() === 'error') errors.push(tag + ' console: ' + m.text()); });
  };
  const toasts = [];
  await ctx.exposeBinding('__chkToast', (_s, t) => toasts.push(t));
  await ctx.addInitScript(() => {
    new MutationObserver(() => { const t = document.getElementById('a3d-toast'); if (t && t.textContent && t.textContent !== window.__lastT) { window.__lastT = t.textContent; window.__chkToast(t.textContent); } })
      .observe(document, { subtree: true, childList: true, characterData: true });
  });

  // 1. first visit: registers, takes over, says it once
  const p1 = await ctx.newPage(); watch(p1, 'p1');
  await p1.goto(url); await boot(p1);
  let st;
  for (let i = 0; i < 50; i++) { st = await off(p1); if (st && st.controlled) break; await sleep(100); }
  ok('first visit: worker registered and in control', st && st.registered && st.controlled, st);
  ok('first visit: "Ready to work offline" said', toasts.some((t) => /Ready to work offline/.test(t)), toasts);
  const caches1 = await p1.evaluate(async () => (await caches.keys()));
  ok('the app cache is named BIM-Personal/app/<build>', caches1.some((k) => /^BIM-Personal\/app\/[0-9a-f]{16}$/.test(k)), caches1);
  const keys = await p1.evaluate(async () => { const k = (await caches.keys()).find((x) => x.indexOf('BIM-Personal/app/') === 0); return (await (await caches.open(k)).keys()).map((r) => r.url.replace(location.origin, '')); });
  ok('precached: the page and four ?v= bundles', keys.length === 5 && keys.filter((u) => /\/app\/[^?]+\?v=/.test(u)).length === 4, keys);
  const man = await p1.evaluate(async () => { const r = await fetch(document.querySelector('link[rel=manifest]').href); return r.json(); });
  ok('the manifest is served and linked', man && man.id === '/BIM-Personal/' && man.display === 'standalone', man && man.id);

  // 2. an edit saved, then a reload says nothing again
  await edit(p1, 1); await sleep(700);
  const n1 = await p1.evaluate(() => window.__a3dStore().dirty);
  ok('the edit reached the database', n1 === false, n1);
  toasts.length = 0;
  await p1.reload(); await boot(p1);
  ok('second visit: "Ready to work offline" not said again', !toasts.some((t) => /Ready to work offline/.test(t)), toasts);

  // 3. offline, two ways
  await ctx.setOffline(true);
  await p1.reload(); await boot(p1);
  st = await off(p1);
  const pts = await p1.evaluate(() => document.title).catch(() => null);
  ok('offline (emulated): the app opens, controlled', st && st.controlled, st);
  await edit(p1, 2); await sleep(700);
  ok('offline: an edit is saved', (await p1.evaluate(() => window.__a3dStore().dirty)) === false);
  await ctx.setOffline(false);
  await S.stop();
  await p1.reload(); await boot(p1);
  st = await off(p1);
  ok('offline (server stopped): the app opens, controlled', st && st.controlled, st);
  await S.start();

  // 4. a new build: one tab reloaded does not switch; the bar shows
  S.setBuild(B);
  await p1.reload(); await boot(p1);
  for (let i = 0; i < 60; i++) { st = await off(p1); if (st && st.waiting) break; await sleep(100); }
  ok('new build found: waiting, the bar shown', st && st.waiting && st.bar, st);
  const bt = await p1.evaluate(() => { const b = document.getElementById('a3d-sw-bar'); return b ? [b.textContent, [...b.querySelectorAll('button')].map((x) => x.getBoundingClientRect().height)] : null; });
  ok('the bar: text, Reload and Later', bt && /new version/.test(bt[0]) && bt[1].length === 2, bt);
  await p1.reload(); await boot(p1);
  st = await off(p1);
  ok('a reload alone does not let the new build in (H44)', st && st.waiting, st);

  // 5. a second tab mid-save holds it; it goes in once saved; both tabs reload once
  const p2 = await ctx.newPage(); watch(p2, 'p2');
  await p2.goto(url); await boot(p2);
  let loads1 = 0, loads2 = 0;
  p1.on('load', () => loads1++); p2.on('load', () => loads2++);
  const cachesBefore = await p1.evaluate(async () => (await caches.keys()).filter((k) => k.indexOf('BIM-Personal/app/') === 0));
  await p2.evaluate(() => { window.__a3dAddPoint(9, 0, 9); window.__a3dTitleBlockSet(window.__a3dTitleBlockGet()); });
  const unsaved2 = (await off(p2)).unsaved;
  await p1.evaluate(() => window.__a3dOfflineApply());
  await sleep(600);
  const barText = await p1.evaluate(() => { const b = document.getElementById('a3d-sw-bar'); return b ? b.textContent : null; }).catch(() => null);
  ok('tab 2 had unsaved work when asked', unsaved2 === true, unsaved2);
  ok('the bar waits while a tab saves', barText && /Saving changes/.test(barText), barText);
  for (let i = 0; i < 60; i++) { if (loads1 >= 1 && loads2 >= 1) break; await sleep(100); }
  await sleep(1500); await boot(p1); await boot(p2);
  ok('both tabs reloaded once', loads1 === 1 && loads2 === 1, { loads1, loads2 });
  const c1 = await off(p1), c2 = await off(p2);
  ok('after: no worker waiting, the bar gone', c1 && !c1.waiting && !c1.bar && c2 && !c2.waiting, { c1, c2 });
  const cachesAfter = await p1.evaluate(async () => (await caches.keys()).filter((k) => k.indexOf('BIM-Personal/app/') === 0));
  ok('the old build\'s cache deleted, the new one kept', cachesAfter.length === 1 && /b$/.test(cachesAfter[0]) && cachesBefore.some((k) => !/b$/.test(k)), { cachesBefore, cachesAfter });
  ok('tab 2\'s edit was kept', (await p2.evaluate(() => window.__a3dStore().dirty)) === false);

  // 6. the one-file build registers nothing
  const p3 = await ctx.newPage(); watch(p3, 'p3');
  await p3.goto(S.origin + '/BIM-Personal/canvas_v10.html'); await boot(p3);
  st = await off(p3);
  ok('canvas_v10.html: no worker registered by it', st && st.registered === false, st);

  ok('no page or console errors', errors.length === 0, errors.slice(0, 8));
  await browser.close(); await S.stop();
  for (const r of results) console.log(r.join(' | '));
  console.log(results.filter((r) => r[0] === 'PASS').length + ' of ' + results.length + ' passed');
})().catch((e) => { console.error('CHECK CRASHED', e); process.exit(1); });
