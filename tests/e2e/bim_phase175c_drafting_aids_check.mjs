/* bim_phase175c_drafting_aids_check.mjs -- V175c's quick fixes (docs/research/research-one-paper-space.md, D3):
   Snap, Grid and Ortho stay in the status bar on a sheet and apply when a viewport is moved or sized; the board's
   Edit bar no longer has its own copies; the Tech/Pres pill says Technical style / Presentation style.

   Playwright (Node) and the Chromium already on the machine. To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                 (from the repository's root)
     node tests/e2e/bim_phase175c_drafting_aids_check.mjs <a folder for the screenshots> */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const APP = 'http://127.0.0.1:8765/canvas_v10.html', OUT = process.argv[2] || '.';
let pass = 0, fail = 0;
const ck = (ok, msg) => { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + msg); };
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
const errs = [];
page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
const W = (ms) => page.waitForTimeout(ms || 250);

await page.goto(APP);
await W(4000);
await page.evaluate(() => { window.__a3dEnter && window.__a3dEnter(); });
let r = await page.evaluate(() => { const p = document.getElementById('a3d-present'); return p ? p.textContent : null; });
ck(r === 'Technical style', 'the pill says Technical style (' + r + ')');
await page.click('#a3d-present'); await W();
r = await page.evaluate(() => document.getElementById('a3d-present').textContent);
ck(r === 'Presentation style', 'and Presentation style when on (' + r + ')');
await page.click('#a3d-present'); await W();

// ---- a sheet with a viewport
const ids = await page.evaluate(() => {
  const sid = window.__a3dAddSheet('A101', 'Check', 'A3-L');
  const o = window.__a3dSheetSourceOptions().filter((s) => s.kind === 'plan')[0];
  const vid = window.__a3dAddViewport(sid, o.kind, o.refId, 'fit', 100);
  window.__a3dSetViewportRect(sid, vid, 40, 40, 120, 80);
  window.__a3dOpenSheetView(sid);
  return { sid, vid };
});
await W(600);
r = await page.evaluate(() => { const g = document.getElementById('a3d-snapgrp'); return { on: window.__a3dSheetSpace().onSheet, shown: !!(g && g.offsetParent !== null) }; });
ck(r.on && r.shown, 'on a sheet, the status bar still shows Snap, Grid and Ortho');

const vp = () => page.evaluate((i) => window.__a3dSheets().filter((s) => s.id === i.sid)[0].viewports.filter((v) => v.id === i.vid)[0], ids);
async function drag(fromMM, dxMM, dyMM) {
  const b = await page.evaluate(() => { const c = document.querySelector('#a3d-sheetview canvas') || document.querySelector('canvas.a3d-sheetcv'); const q = c.getBoundingClientRect(); return { l: q.left, t: q.top, w: q.width, h: q.height, cw: c.width, ch: c.height }; });
  const s = await page.evaluate((i) => window.__a3dSheets().filter((x) => x.id === i.sid)[0], ids);
  const px = (mm) => [b.l + mm[0] * 3.0 * b.w / b.cw, b.t + mm[1] * 3.0 * b.h / b.ch];
  const a = px(fromMM), z = px([fromMM[0] + dxMM, fromMM[1] + dyMM]);
  await page.mouse.move(a[0], a[1]); await page.mouse.down();
  await page.mouse.move((a[0] + z[0]) / 2, (a[1] + z[1]) / 2, { steps: 4 });
  await page.mouse.move(z[0], z[1], { steps: 4 }); await page.mouse.up(); await W();
  return s;
}
// Grid: whole millimetres
await page.evaluate(() => window.__a3dSnapSet({ point: false, grid: true, ortho: false }));
await drag([100, 80], 13.4, 7.6);
let v = await vp();
ck(Number.isInteger(v.x) && Number.isInteger(v.y) && v.x !== 40, 'Grid: a moved viewport lands on whole millimetres (' + v.x + ', ' + v.y + ')');
// Ortho: straight across
const y0 = v.y;
await page.evaluate(() => window.__a3dSnapSet({ point: false, grid: false, ortho: true }));
await drag([v.x + 60, v.y + 40], 20, 6);
v = await vp();
ck(v.y === y0, 'Ortho: a mostly-across drag moves it straight across (y ' + y0 + ' -> ' + v.y + ')');
// Snap: its middle to the paper's middle
await page.evaluate(() => window.__a3dSnapSet({ point: true, grid: false, ortho: false }));
const S = await page.evaluate((i) => window.__a3dSheets().filter((x) => x.id === i.sid)[0], ids);
const want = S.w / 2 - v.w / 2, dxs = want - v.x + 1.6;
await drag([v.x + 60, v.y + 40], dxs, 0.3);
v = await vp();
ck(Math.abs(v.x + v.w / 2 - S.w / 2) < 0.01, 'Snap: its middle meets the paper\'s middle (' + (v.x + v.w / 2).toFixed(2) + ' of ' + S.w / 2 + ')');
// all off: free
await page.evaluate(() => window.__a3dSnapSet({ point: false, grid: false, ortho: false }));
await drag([v.x + 60, v.y + 40], 7.3, 5.1);
const v2 = await vp();
ck(!Number.isInteger(v2.x) || !Number.isInteger(v2.y), 'all off: it moves freely (' + v2.x + ', ' + v2.y + ')');
await page.screenshot({ path: OUT + '/v175c-sheet.png' });

// ---- the board's bar has no copies
await page.evaluate(() => { window.__a3dBrdNew('V175c'); });
await W(400);
await page.evaluate(() => { const d = document.querySelector('.a3d-clb-dlg [data-brddlg="cancel"]'); if (d) d.click(); });
await W();
r = await page.evaluate(() => ({ copies: document.querySelectorAll('[data-brdsnap]').length, edit: !!document.querySelector('[data-brd="draw"]') }));
ck(r.edit && r.copies === 0, 'a board in Edit has no Snap, Grid and Ortho of its own');

// ---- a phone: the status bar still fits
await page.setViewportSize({ width: 390, height: 800 }); await W(600);
r = await page.evaluate(() => { const b = document.getElementById('a3d-statusbar'); return b ? { sw: b.scrollWidth, cw: b.clientWidth, doc: document.documentElement.scrollWidth } : null; });
ck(r && r.doc <= 390, 'at a phone\'s width the page does not scroll sideways (' + JSON.stringify(r) + ')');
await page.screenshot({ path: OUT + '/v175c-phone.png' });

ck(errs.length === 0, 'no console errors' + (errs.length ? ': ' + errs.slice(0, 4).join(' | ') : ''));
console.log(pass + ' passed, ' + fail + ' failed');
await browser.close();
process.exit(fail ? 1 : 0);
