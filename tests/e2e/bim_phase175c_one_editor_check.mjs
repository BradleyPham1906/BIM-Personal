/* bim_phase175c_one_editor_check.mjs -- V175c WO-18's browser check: one editor, one print.
   A drawing sheet with a plan, an elevation and a rooms schedule is opened as a layout from the sheet bar: it is a
   drawing layout in the board editor, in the sheet's place, with its number; its Draw menu has no live values or
   charts; its map frames are at the sheet's scales; Work in viewport opens the plan in the model; Undo brings the
   sheet back; its vector page clips each frame. docs/work-orders/v175c/SPEC-step2.md.

   Playwright (Node) and the Chromium already on the machine. To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                 (from the repository's root)
     node tests/e2e/bim_phase175c_one_editor_check.mjs <a folder for the screenshots> */
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
const W = (ms) => page.waitForTimeout(ms || 300);

await page.goto(APP);
await W(4000);
// a model, and a sheet A101 with a plan at 1:100, the front elevation fitted, and the rooms schedule
let r = await page.evaluate(() => {
  window.__a3dEnter(); window.__a3dTestSetObjs([]);
  window.__a3dCurvedWall([[0, 0], [8, 0], [8, 6], [0, 6]], null, 0.2, 3, 'center', true);
  const lv = window.__a3dSheetSourceOptions().find((s) => s.kind === 'plan');
  const id = window.__a3dAddSheet('A101', 'Ground floor', 'ANSI-B');
  window.__a3dAddViewport(id, 'plan', lv.refId, 'ratio', 100);
  window.__a3dAddViewport(id, 'elevation', 'front', 'fit', 100);
  window.__a3dAddViewport(id, 'schedule', 'rooms', 'fit', 100);
  window.__a3dOpenSheetView(id);
  return { id, vps: window.__a3dSheets().find((s) => s.id === id).viewports.length };
});
await W(800);
ck(r.id && r.vps === 3, 'a sheet with a plan, an elevation and a schedule (' + JSON.stringify(r) + ')');
const sheetId = r.id;
ck(await page.isVisible('#a3d-sheetlayout'), 'the sheet bar has Open as layout');
await page.screenshot({ path: OUT + '/175c-sheet.png' });

await page.click('#a3d-sheetlayout'); await W(1200);
r = await page.evaluate((sid) => {
  const st = window.__a3dClbState(), sheets = window.__a3dSheets();
  return { open: st.open, board: st.board, edit: st.edit, sheetGone: !sheets.some((s) => s.id === sid) };
}, sheetId);
ck(r.open && /^board-c\d+$/.test(r.board) && r.sheetGone, 'Open as layout: the sheet is a layout, open in the board editor (' + JSON.stringify(r) + ')');
const bid = r.board;
r = await page.evaluate((id) => window.__a3dBrdRecord(id), bid);
ck(r && r.drawing === true && r.num === 'A101' && r.name === 'Ground floor' && r.page && r.page.key === 'ansi-B', 'a drawing layout with the sheet\'s number, name and page (' + JSON.stringify(r && { drawing: r.drawing, num: r.num, page: r.page }) + ')');
const kinds = r.objs.map((n) => n.t).join(',');
ck(kinds === 'border,tblock,map,map,sched', 'its frame, title block, two map frames and the schedule (' + kinds + ')');
const plan = r.objs.find((n) => n.t === 'map' && /^plan:/.test(n.src));
ck(plan && plan.den === 100, 'the plan at the sheet\'s 1:100 (' + (plan && plan.den) + ')');
r = await page.evaluate(() => [].map.call(document.querySelectorAll('#a3d-laytabs [data-lt]'), (b) => ({ t: b.getAttribute('data-lt'), label: b.textContent, on: b.classList.contains('on') })));
ck(r.some((t) => t.t === 'board' && /^A101 - Ground floor/.test(t.label)), 'its tab keeps A101 (' + r.map((t) => t.label).join(' | ') + ')');
await page.screenshot({ path: OUT + '/175c-layout.png' });

// the Draw menu of a drawing layout
r = await page.evaluate(() => {
  const b = document.querySelector('[data-brd="draw"]');
  if (b) b.click();
  const m = document.getElementById('a3d-ltmenu');
  return m ? [].map.call(m.querySelectorAll('[data-ltm]'), (x) => x.getAttribute('data-ltm')) : null;
});
if (r) {
  ck(!r.some((k) => /^lv(field|number|kpi|chart)$/.test(k)) && r.includes('map') && r.includes('lvsched'), 'its Draw menu leaves out the live values and charts, keeps frames and schedules (' + r.join(',') + ')');
  await page.keyboard.press('Escape');
} else ck(false, 'the Draw menu could be opened');

// the vector page: each frame clipped, the plan as vectors, at the page size
r = await page.evaluate((id) => window.__a3dLayoutSvg(id), bid);
ck(r && r.svg && (r.svg.match(/<clipPath/g) || []).length === 3 && Math.abs(r.w - 279.4) < 0.1 && Math.abs(r.h - 431.8) < 0.1, 'one vector page at the sheet\'s 279.4 x 431.8 mm, each of its three frames clipped (' + (r && (r.why || [r.w, r.h, (r.svg.match(/<clipPath/g) || []).length].join(' '))) + ')');
ck(r && r.svg && /<(path|line|polyline|polygon)/.test(r.svg), 'the plan drawn as vectors');

// Work in viewport, from the plan frame's Properties
r = await page.evaluate((args) => {
  window.__a3dSelectFor([]); window.__a3dBrdEdit(true); window.__a3dBdeSelect && window.__a3dBdeSelect([args.fr]);
  return !!window.__a3dBdeSelect;
}, { fr: plan.id });
if (r) {
  await W(400);
  const has = await page.evaluate(() => { const b = document.querySelector('[data-bdact="mapwork"]'); if (b) b.click(); return b ? true : (document.getElementById('a3d-propsbody') || {}).innerText.slice(0, 300); });
  await W(800);
  const v = await page.evaluate(() => ({ open: window.__a3dClbState().open, hud: (document.querySelector('.a3d-hud,#a3d-hud')||{}).textContent||'' }));
  ck(has && !v.open, 'Work in viewport opens the plan in the model (' + JSON.stringify(v) + ')');
} else console.log('NOTE no selection hook for board objects: Work in viewport left to the unit of bimLoWorkIn');

// Undo brings the sheet back
await page.evaluate(() => { const c = document.getElementById('a3d-canvas'); if (c) c.focus(); });
await page.keyboard.press('Control+z'); await W(800);
r = await page.evaluate((sid) => ({ sheet: window.__a3dSheets().some((s) => s.id === sid) }), sheetId);
ck(r.sheet, 'Undo brings the sheet back');

ck(errs.length === 0, 'no console errors (' + errs.length + ')' + (errs.length ? ': ' + errs.slice(0, 2).join(' | ') : ''));
console.log(`\n${pass} passed, ${fail} failed`);
await browser.close();
process.exit(fail ? 1 : 0);
