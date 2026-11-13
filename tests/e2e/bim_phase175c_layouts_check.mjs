/* bim_phase175c_layouts_check.mjs -- V175c step 1's browser check: one list of layouts.
   Every drawing sheet and board has a tab beside Model, numbered in one series; + Layout (the tabs' + and the
   Presentation panel's) makes a drawing sheet, a board or a site analysis board; a board's tab opens it and its
   double-click renumbers it; numbers used twice are said in the panel. docs/work-orders/v175c/SPEC.md.

   Playwright (Node) and the Chromium already on the machine. To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                 (from the repository's root)
     node tests/e2e/bim_phase175c_layouts_check.mjs <a folder for the screenshots> */
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
const tabs = () => page.evaluate(() => [].map.call(document.querySelectorAll('#a3d-laytabs [data-lt]'), (b) => ({ t: b.getAttribute('data-lt'), id: b.getAttribute('data-ltsheet'), label: b.textContent, on: b.classList.contains('on') })));
const menu = () => page.evaluate(() => { const m = document.getElementById('a3d-ltmenu'); return m ? [].map.call(m.querySelectorAll('[data-ltm]'), (x) => [x.textContent, x.getAttribute('data-ltm')]) : []; });
const pick = (v) => page.evaluate((v) => { const b = document.querySelector('#a3d-ltmenu [data-ltm="' + v + '"]'); if (b) b.click(); return !!b; }, v);

await page.goto(APP);
await W(4000);
await page.evaluate(() => { window.__a3dEnter && window.__a3dEnter(); });

// ---- + at the end of the tabs: + Layout's menu
await page.click('#a3d-laytabs [data-lt="new"]'); await W();
let r = await menu();
ck(['sheet', 'new', 'climate', 'zoning', 'access'].every((k) => r.some((x) => x[1] === k)), 'the tabs\' + opens + Layout: Drawing sheet, Board, the three site boards (' + r.map((x) => x[0]).join(' | ') + ')');
await pick('sheet'); await W(600);
let T = await tabs();
const s1 = T.filter((x) => x.t === 'sheet')[0];
ck(s1 && /^A101 - /.test(s1.label) && s1.on, 'Drawing sheet: a sheet A101, its tab on');

// ---- a board from the panel's + Layout
await page.evaluate(() => { const b = document.querySelector('#a3d-rail [data-tab="presentation"],[data-tab="presentation"]'); if (b) b.click(); });
await W();
r = await page.evaluate(() => ({ lay: !!document.querySelector('[data-prpact="layout"]'), page: !!document.querySelector('[data-prpact="new"]'), board: !!document.querySelector('[data-prpact="board"]') }));
ck(r.lay && !r.page && !r.board, 'the Presentation panel has one + Layout, no + Page or + Board');
await page.click('[data-prpact="layout"]'); await W();
await pick('new'); await W(800);
await page.evaluate(() => { const d = document.querySelector('.a3d-clb-dlg [data-brddlg="cancel"]'); if (d) d.click(); }); await W();
T = await tabs();
const b1 = T.filter((x) => x.t === 'board')[0];
ck(b1 && /^A102 - /.test(b1.label) && b1.on, 'Board: a board numbered A102 in the same series, with its tab, on while it is open (' + (b1 && b1.label) + ')');
ck(T[0].t === 'model' && T[T.length - 1].t === 'new', 'Model first, + last');

// ---- a sheet's tab, then the board's tab
await page.click('#a3d-laytabs [data-lt="sheet"]'); await W(600);
r = await page.evaluate(() => window.__a3dSheetSpace().onSheet);
ck(r, 'a sheet\'s tab opens the sheet');
await page.click('#a3d-laytabs [data-lt="board"]'); await W(600);
r = await page.evaluate(() => window.__a3dClbState());
ck(r.open && r.board === b1.id || (r.open && /board/.test(r.board || '')), 'a board\'s tab opens the board (' + JSON.stringify({ open: r.open, board: r.board }) + ')');
T = await tabs();
ck(T.filter((x) => x.on).length === 1 && T.filter((x) => x.on)[0].t === 'board', 'only the open board\'s tab is on');

// ---- renumber the board by double-click, then a duplicate is said
await page.dblclick('#a3d-laytabs [data-lt="board"]'); await W();
await page.fill('#a3d-laytabs input[data-ltrename]', 'A101'); await page.keyboard.press('Enter'); await W(500);
T = await tabs();
ck(T.filter((x) => x.t === 'board')[0].label.indexOf('A101') === 0, 'double-click renumbers the board (' + T.filter((x) => x.t === 'board')[0].label + ')');
r = await page.evaluate(() => { const d = document.querySelector('.a3d-prpdup'); return d ? d.textContent : ''; });
ck(/A101/.test(r), 'a number used twice is said in the panel (' + r + ')');
await page.dblclick('#a3d-laytabs [data-lt="board"]'); await W();
await page.fill('#a3d-laytabs input[data-ltrename]', 'bad<'); await page.keyboard.press('Enter'); await W(400);
T = await tabs();
ck(T.filter((x) => x.t === 'board')[0].label.indexOf('A101') === 0, 'a number that is not good changes nothing');
await page.evaluate(() => window.__a3dUndo && window.__a3dUndo()); await W(400);
await page.dblclick('#a3d-laytabs [data-lt="board"]'); await W();
await page.fill('#a3d-laytabs input[data-ltrename]', 'B201'); await page.keyboard.press('Enter'); await W(500);
r = await page.evaluate(() => document.querySelectorAll('.a3d-prpdup').length);
ck(r === 0, 'renumbered apart, nothing is said');

// ---- a board's tab right-click: Renumber and the board's own menu
await page.click('#a3d-laytabs [data-lt="board"]', { button: 'right' }); await W();
r = await menu();
ck(r[0] && r[0][1] === 'renum' && r.some((x) => x[1] === 'present'), 'a board\'s tab menu: Renumber, then the board\'s own');
await page.keyboard.press('Escape'); await page.evaluate(() => { const m = document.getElementById('a3d-ltmenu'); if (m) m.remove(); });

// ---- a site analysis board from + Layout
await page.click('#a3d-laytabs [data-lt="new"]'); await W();
await pick('climate'); await W(800);
T = await tabs();
ck(T.some((x) => x.t === 'board' && /Climate and risk/.test(x.label) && /^A10\d - /.test(x.label)), 'a site analysis board gets the next number and its tab (' + T.map((x) => x.label).join(' | ') + ')');
await page.screenshot({ path: OUT + '/v175c-layouts.png' });

// ---- a phone
await page.setViewportSize({ width: 390, height: 800 }); await W(600);
r = await page.evaluate(() => document.documentElement.scrollWidth);
ck(r <= 390, 'at a phone\'s width the page does not scroll sideways (' + r + ')');
await page.screenshot({ path: OUT + '/v175c-layouts-phone.png' });

ck(errs.length === 0, 'no console errors' + (errs.length ? ': ' + errs.slice(0, 4).join(' | ') : ''));
console.log(pass + ' passed, ' + fail + ' failed');
await browser.close();
process.exit(fail ? 1 : 0);
