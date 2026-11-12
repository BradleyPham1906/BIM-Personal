/* bim_phase175b_board_objects_check.mjs -- V175b's browser check: schedules, single indicators and result charts.

   Playwright (Node) and the Chromium already on the machine. To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                 (from the repository's root)
     node tests/e2e/bim_phase175b_board_objects_check.mjs <a folder for the screenshots>
   It checks: the Draw menu's three entries and their menus; a rooms schedule drawn from the model, sorted from
   Properties, following the model; an areas-by-level schedule; Indicator with no site board worked out; a result
   chart with its histogram, out of date with Run again offered, then its layer removed; the two new numbers;
   nothing of Edit on paper; a phone's width; and the console. */
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
page.on('pageerror', (e) => errs.push('pageerror: ' + e.message + ' @ ' + String(e.stack).split('\n').slice(1, 4).join(' < ').replace(/http:[^ ]*html/g, '')));
const W = () => page.waitForTimeout(250);
const el = (id) => page.evaluate((i) => { const e = document.querySelector('.a3d-clb-dsn [data-bde="' + i + '"]'); return e ? { t: e.textContent, h: e.innerHTML, m: [].map.call(e.querySelectorAll('.a3d-clb-dlv'), (x) => x.className.replace('a3d-clb-dlv ', '')) } : null; }, id);
const menu = () => page.evaluate(() => { const m = document.getElementById('a3d-ltmenu'); return m ? [].map.call(m.querySelectorAll('[data-ltm]'), (x) => [x.textContent, x.getAttribute('data-ltm')]) : []; });
const pick = (v) => page.evaluate((v) => { const b = document.querySelector('#a3d-ltmenu [data-ltm="' + v + '"]'); if (b) b.click(); return !!b; }, v);
const toast = () => page.evaluate(() => [].map.call(document.querySelectorAll('.a3d-toast,#a3d-toast,[class*="toast"]'), (x) => x.textContent).join(' | '));

await page.goto(APP);
await page.waitForTimeout(4000);
let r = await page.evaluate(() => { window.__a3dEnter && window.__a3dEnter(); return { lb: !!window.__a3dLiveBoard, v: window.__acad3dV175b }; });
ck(r.lb && /sched/.test(r.v || ''), 'the app loads with the V175b hooks');
await page.evaluate(() => {
  const L = window.__a3dLive.keys ? null : null;
  window.__a3dTestSetObjs([{ id: 'r1', t: 'room', name: 'Office', area: 24.5, levelId: 'lvl-0', layer: 'layer-0', y: 0, pos: [0, 0, 0], pts: [[0, 0], [7, 0], [7, 3.5], [0, 3.5]] }, { id: 'r2', t: 'room', name: 'Store', area: 1200, levelId: 'lvl-0', layer: 'layer-0', y: 0, pos: [0, 0, 0], pts: [[10, 0], [50, 0], [50, 30], [10, 30]] }]);
  window.__a3dLive.bump();
  window.__a3dBrdNew('V175b check');
});
await W();
await page.evaluate(() => { const d = document.querySelector('.a3d-clb-dlg [data-brddlg="cancel"]'); if (d) d.click(); });
await W();

// ---- the Draw menu
r = await page.evaluate(async () => {
  const b = [].filter.call(document.querySelectorAll('button'), (x) => /^Draw/.test(x.textContent.trim()))[0];
  b.click(); await new Promise((q) => setTimeout(q, 200));
  const m = document.getElementById('a3d-ltmenu');
  return m ? [].map.call(m.querySelectorAll('[data-ltm]'), (x) => x.getAttribute('data-ltm')) : [];
});
ck(['lvsched', 'lvkpi', 'lvchart'].every((k) => r.indexOf(k) >= 0), 'the Draw menu has Schedule, Indicator and Result chart');
await pick('lvsched'); await page.waitForTimeout(300);
r = await menu();
ck(r.length === 2 && r[0][1] === 'rooms' && r[1][1] === 'levels', 'Schedule offers Rooms and Areas by level');
await pick('rooms'); await page.waitForTimeout(300);
let objs = await page.evaluate(() => window.__a3dBoardDesign.objs());
const sId = objs.filter((o) => o.t === 'sched')[0].id;
let S = await el(sId);
ck(S && /Rooms/.test(S.t) && /Office/.test(S.t) && /Store/.test(S.t) && /1,224\.5 m²/.test(S.t), 'a rooms schedule is drawn from the model, with its total');

// ---- sorted from Properties (a select, then a checkbox)
await page.evaluate((id) => window.__a3dBoardDesign.select([id]), sId); await W();
await page.selectOption('select[data-bdf="sk"]', 'area'); await W();
await page.check('input[data-bdf="sd"]'); await W();
objs = await page.evaluate(() => window.__a3dBoardDesign.objs());
S = await el(sId);
ck(objs.filter((o) => o.id === sId)[0].sk === 'area' && objs.filter((o) => o.id === sId)[0].sd === true, 'Sorted by and Descending in Properties are kept');
ck(S.t.indexOf('Store') < S.t.indexOf('Office'), 'the rows follow the sort');
await page.fill('input[data-bdf="ttl"]', 'Room list'); await page.keyboard.press('Tab'); await W();
ck(/^Room list/.test((await el(sId)).t), 'its title, typed and left with Tab, is applied');

// ---- it follows the model
await page.evaluate(() => {
  const L = window.__a3dBoardDesign.objs();
  window.__a3dTestSetObjs([{ id: 'r1', t: 'room', name: 'Office', area: 24.5, levelId: 'lvl-0', layer: 'layer-0', y: 0, pos: [0, 0, 0], pts: [[0, 0], [7, 0], [7, 3.5], [0, 3.5]] }]);
  window.__a3dLive.bump(); window.__a3dBoardDesign.select([]);
  window.__a3dLiveBoard.redraw();   /* as a model edit's save redraws the open board */
});
await W();
S = await el(sId);
ck(S && S.t.indexOf('Store') < 0 && /24\.5 m²/.test(S.t), 'a room removed from the model leaves the schedule (' + (S && S.t.slice(0, 80)) + ')');

// ---- areas by level
r = await page.evaluate(async () => { window.__a3dLiveBoard.schedMenu(); await new Promise((q) => setTimeout(q, 150)); const b = document.querySelector('#a3d-ltmenu [data-ltm="levels"]'); b.click(); await new Promise((q) => setTimeout(q, 300)); return window.__a3dBoardDesign.objs().filter((o) => o.t === 'sched' && o.src === 'levels').map((o) => o.id); });
S = await el(r[0]);
ck(S && /Areas by level/.test(S.t) && /Gross area/.test(S.t) && /Level/.test(S.t), 'an areas-by-level schedule is drawn');

// ---- an indicator, with no site board worked out
r = await page.evaluate(() => window.__a3dLiveBoard.kpiMenu());
const tt = await toast();
ck(r === false && /No indicators yet/.test(tt), 'Indicator says when no site board has indicators yet');
r = await page.evaluate(() => window.__a3dBoardDesign.add('kpi', { f: 'zn.kpis', lab: 'Lot area', w: 45, h: 26 }));
await W();
S = await el(r);
ck(S && /^Not computed: Zoning and yield indicators/.test(S.t) && S.m.indexOf('none') >= 0, 'an indicator with nothing to show says why, with its mark (' + (S && S.t) + ')');

// ---- a result chart
await page.evaluate(() => window.__a3dLiveBoard.addLayer({ id: 'res-chk-1', kind: 'sunhours', name: 'Sun hours, 2026-06-21', key: 'another-model', visible: true, opacity: 0.6,
  created: '2026-11-12 10:00', data: { x0: 0, z0: 0, cell: 1, nx: 4, nz: 2, ground: 0, cells: '0012..77', day: 12, date: '2026-06-21', min: 0, max: 12, sixPlus: 0.4 } }));
await page.evaluate(() => window.__a3dLiveBoard.chartMenu()); await page.waitForTimeout(200);
r = await menu();
ck(r.some((x) => x[1] === 'res-chk-1'), 'Result chart lists the result layers');
await pick('res-chk-1'); await page.waitForTimeout(300);
objs = await page.evaluate(() => window.__a3dBoardDesign.objs());
const cId = objs.filter((o) => o.t === 'rchart')[0].id;
S = await el(cId);
ck(S && (S.h.match(/<rect /g) || []).length === 4 && /Hours of direct sun/.test(S.t), 'a Sun hours chart draws its histogram');
ck(S.m.indexOf('stale') >= 0, 'out of date, it carries the amber mark');
await page.evaluate((id) => window.__a3dBoardDesign.select([id]), cId); await W();
r = await page.evaluate(() => !!document.querySelector('[data-bdact="lv-resrun"]') && document.getElementById('a3d-propsbody').innerHTML.indexOf('Out of date: the model has changed since') >= 0);
ck(r, 'Properties says why, and offers Run again');

// ---- the two numbers
r = await page.evaluate(() => window.__a3dLive.addNumber('sun.sixplus')); await W();
S = await el(r);
ck(S && S.t === '40 %' && S.m.indexOf('stale') >= 0, 'the share of ground with 6 h of sun: 40 %, marked out of date (' + (S && S.t) + ')');
r = await page.evaluate(() => window.__a3dLive.addNumber('solar.roofkwh')); await W();
S = await el(r);
ck(S && /^Not computed: run Solar/.test(S.t), 'the roofs\' solar yield says to run Solar first');
await page.evaluate(() => {   /* each put in its own place, for the picture */
  const D = window.__a3dBoardDesign, P = { sched: [[20, 20], [190, 20]], kpi: [[20, 110]], rchart: [[80, 110]], text: [[190, 90], [190, 110], [20, 140]] }, n = {};
  D.objs().forEach((o) => { const L = P[o.t]; const i = n[o.t] = (n[o.t] || 0); if (L && L[i]) D.set(o.id, { x: L[i][0], y: L[i][1] }); n[o.t]++; });
  D.select([]);
});
await page.waitForTimeout(400);
await page.screenshot({ path: OUT + '/v175b-edit.png' });

// ---- the layer removed
await page.evaluate(() => { window.__a3dLiveBoard.addLayer({ id: 'res-tmp-0', kind: 'rain', name: 'x', key: '', visible: true, data: null }); });
await page.evaluate(() => { const L = window.__a3dBoardDesign; });
r = await page.evaluate((id) => { const A = window.__a3dLiveBoard.state({ t: 'rchart', res: 'res-none-9', nm: 'Sun hours, 2026-06-21' }); return A.why[0]; }, cId);
ck(r === 'Source removed: Sun hours, 2026-06-21', 'a chart whose layer is gone says what it showed');

// ---- off Edit: no marks, a dash for nothing to show
await page.evaluate(() => window.__a3dBrdEdit(false)); await W();
r = await page.evaluate(() => ({ m: document.querySelectorAll('.a3d-clb-dsn .a3d-clb-dlv').length, dash: [].some.call(document.querySelectorAll('.a3d-clb-dsn .a3d-clb-dlbx'), (x) => x.textContent === '—') }));
ck(r.m === 0 && r.dash, 'out of Edit: no marks, and a dash where there is nothing to show');
await page.screenshot({ path: OUT + '/v175b-view.png' });

// ---- a phone
await page.setViewportSize({ width: 390, height: 800 }); await page.waitForTimeout(600);
S = await el(sId);
ck(S && /Office/.test(S.t), 'at a phone\'s width the schedule is drawn');
await page.screenshot({ path: OUT + '/v175b-phone.png' });

ck(errs.length === 0, 'no console errors' + (errs.length ? ': ' + errs.slice(0, 5).join(' | ') : ''));
console.log(pass + ' passed, ' + fail + ' failed');
await browser.close();
process.exit(fail ? 1 : 0);
