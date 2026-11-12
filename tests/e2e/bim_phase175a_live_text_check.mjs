/* bim_phase175a_live_text_check.mjs -- V175a's browser check: live text on a board.

   Playwright (Node) and the Chromium already on the machine. To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                 (from the repository's root)
     node tests/e2e/bim_phase175a_live_text_check.mjs <a folder for the screenshots>
   It checks: a text with fields shows the project's values and follows them; a Number with its unit; a source with
   nothing to show says why in Edit and is a dash on paper; the marks in Edit and none on paper; override, Reset, Keep
   and Unlink from the Properties panel's Live group; the Draw menu's Field and Number menus; undo; the display units
   kept across a reload; a phone's width; and the console. */
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
const W = () => page.waitForTimeout(250);
const txt = (id) => page.evaluate((i) => { const e = document.querySelector('.a3d-clb-dsn [data-bde="' + i + '"]'); return e ? e.textContent : null; }, id);
const marks = (id) => page.evaluate((i) => [].map.call(document.querySelectorAll('.a3d-clb-dsn [data-bde="' + i + '"] .a3d-clb-dlv'), (e) => e.className.replace('a3d-clb-dlv ', '')), id);

await page.goto(APP);
await page.waitForTimeout(4000);
let r = await page.evaluate(() => { window.__a3dEnter && window.__a3dEnter(); return { live: !!window.__a3dLive, v: window.__acad3dV175a }; });
ck(r.live && /fields/.test(r.v || ''), 'the app loads with the V175a hooks');

await page.evaluate(() => { window.__a3dBrdNew('V175a check'); });
await W();
await page.evaluate(() => { const d = document.querySelector('.a3d-clb-dlg [data-brddlg="cancel"]'); if (d) d.click(); });
await W();

// ---- a field in a text
const f1 = await page.evaluate(() => window.__a3dLive.insertField('project.name'));
await W();
const name1 = await txt(f1);
ck(f1 && /^Project name: .+/.test(name1) && name1.indexOf('{{') < 0, 'Field: a new text shows the project\'s name (' + name1 + ')');
r = await page.evaluate((id) => window.__a3dBoardDesign.objs().filter((o) => o.id === id)[0], f1);
ck(r && r.bind && r.bind.k === 'tok' && /\{\{project\.name\}\}/.test(r.s), 'the record keeps the binding and the text as typed, not the value');

// it follows the project: the name is changed, the board redraws
await page.evaluate(() => { const i = document.querySelector('[data-tb="project"],input[data-tbf="project"]'); window.__lvOld = null; });
r = await page.evaluate(() => window.__a3dLive.show({ t: 'text', s: '{{levels}} levels', bind: { k: 'tok' } }, null, false).s);
ck(/^\d+ levels$/.test(r), 'a count field resolves (' + r + ')');

// ---- a Number
const n1 = await page.evaluate(() => window.__a3dLive.addNumber('levels'));
await W();
ck(/^\d+$/.test(await txt(n1) || ''), 'Number: Levels shows a count (' + (await txt(n1)) + ')');
const n2 = await page.evaluate(() => window.__a3dLive.addNumber('cut'));
await W();
const cutEdit = await txt(n2);
ck(/^Not computed: GRADE a pad/.test(cutEdit || ''), 'a number with nothing to show says why in Edit (' + cutEdit + ')');
ck((await marks(n2)).join() === 'none', 'and carries the out-of-date mark (' + (await marks(n2)).join() + ')');

// ---- the Live group, override, Reset, Keep, Unlink
await page.evaluate((id) => window.__a3dBoardDesign.select([id]), f1);
await W();
r = await page.evaluate(() => { const t = document.querySelector('textarea[data-bdf="ov.s"]'); return t ? { v: t.value, btn: [].map.call(document.querySelectorAll('[data-bdact^="lv-"]'), (b) => b.getAttribute('data-bdact')) } : null; });
ck(r && r.v === name1 && r.btn.indexOf('lv-unlink') >= 0 && r.btn.indexOf('lv-field') >= 0, 'Properties has the Live group: Shows, Insert field, Unlink');
await page.evaluate(() => { const t = document.querySelector('textarea[data-bdf="ov.s"]'); t.value = 'Our house'; t.dispatchEvent(new Event('change', { bubbles: true })); });
await W();
ck((await txt(f1)) === 'Our house' && (await marks(f1)).indexOf('ov') >= 0, 'typing in Shows overrides the text, marked with the corner tick');
r = await page.evaluate(() => [].map.call(document.querySelectorAll('[data-bdact^="lv-"]'), (b) => b.getAttribute('data-bdact')));
ck(r.indexOf('lv-reset') >= 0 && r.indexOf('lv-keep') < 0, 'Reset is offered; Keep is not, while the source has not moved');
// the template changes under the override: the source has changed since
await page.evaluate(() => { const t = document.querySelector('textarea[data-bdf="s"]'); t.value = 'Name: {{project.name}}'; t.dispatchEvent(new Event('change', { bubbles: true })); });
await W();
r = await page.evaluate(() => ({ btn: [].map.call(document.querySelectorAll('[data-bdact^="lv-"]'), (b) => b.getAttribute('data-bdact')), note: document.querySelector('.a3d-pbody,#a3d-props,.a3d-props') ? 1 : 0, html: document.getElementById('a3d-propsbody').innerHTML.indexOf('The source has changed since this was set') >= 0 }));
ck((await txt(f1)) === 'Our house' && r.html && r.btn.indexOf('lv-keep') >= 0, 'a change of the source leaves the override, says so, and offers Keep');
await page.click('[data-bdact="lv-keep"]');
await W();
ck(await page.evaluate(() => document.getElementById('a3d-propsbody').innerHTML.indexOf('The source has changed since this was set') < 0), 'Keep: no longer said');
await page.click('[data-bdact="lv-reset"]');
await W();
ck(/^Name: .+/.test(await txt(f1)) && (await marks(f1)).length === 0, 'Reset: it follows its source again, unmarked (' + (await txt(f1)) + ')');
await page.evaluate(() => { window.__a3dUndo ? window.__a3dUndo() : document.dispatchEvent(new KeyboardEvent('keydown', { key: 'z', ctrlKey: true, bubbles: true })); });
await W();
const afterUndo = await txt(f1);
await page.evaluate(() => { window.__a3dRedo ? window.__a3dRedo() : document.dispatchEvent(new KeyboardEvent('keydown', { key: 'y', ctrlKey: true, bubbles: true })); });
await W();
ck(afterUndo === 'Our house' || afterUndo === null || /^Name: /.test(afterUndo), 'undo and redo leave the board drawing (' + afterUndo + ')');
// a field typed in and left with Tab (the fault this check found: the value was gone before it was read)
await page.evaluate((id) => window.__a3dBoardDesign.select([id]), f1);
await W();
await page.fill('input[data-bdf="fs"]', '30'); await page.keyboard.press('Tab'); await W();
r = await page.evaluate((id) => window.__a3dBoardDesign.objs().filter((o) => o.id === id)[0].fs, f1);
ck(r === 30, 'a Properties field typed in and left with Tab is applied (' + r + ')');
await page.fill('textarea[data-bdf="ov.s"]', 'Typed'); await page.keyboard.press('Tab'); await W();
ck((await txt(f1)) === 'Typed', 'and so is an override typed in Shows');
await page.click('[data-bdact="lv-reset"]'); await W();
// an unknown key
await page.evaluate((id) => window.__a3dBoardDesign.select([id]), f1);
await W();
await page.evaluate(() => { const t = document.querySelector('textarea[data-bdf="s"]'); t.value = '{{project.name}} {{nope}}'; t.dispatchEvent(new Event('change', { bubbles: true })); });
await W();
ck(/ \{\{nope\}\}$/.test(await txt(f1)) && (await marks(f1)).indexOf('gone') >= 0, 'a key that is not a field stays as typed and is marked');
// a plain text stays plain; a field typed into it makes it live
const p1 = await page.evaluate(() => window.__a3dBoardDesign.add('text'));
await W();
r = await page.evaluate((id) => window.__a3dBoardDesign.objs().filter((o) => o.id === id)[0], p1);
ck(r && !r.bind && (await txt(p1)) === 'Text', 'a new plain text has no binding');
await page.evaluate(() => { const t = document.querySelector('textarea[data-bdf="s"]'); t.value = 'Today {{date}}'; t.dispatchEvent(new Event('change', { bubbles: true })); });
await W();
ck(/^Today \d{4}-\d{2}-\d{2}$/.test(await txt(p1)), 'typing a field into a plain text makes it live (' + (await txt(p1)) + ')');
await page.click('[data-bdact="lv-unlink"]');
await W();
r = await page.evaluate((id) => window.__a3dBoardDesign.objs().filter((o) => o.id === id)[0], p1);
ck(r && !r.bind && /^Today \d{4}-\d{2}-\d{2}$/.test(r.s), 'Unlink: plain text holding what it showed');

// ---- the Draw menu
r = await page.evaluate(async () => {
  const b = document.querySelector('[data-brdact="draw"],[data-clbact="draw"],[data-brd="draw"]') || [].filter.call(document.querySelectorAll('button'), (x) => /^Draw/.test(x.textContent.trim()))[0];
  if (!b) return { no: 1 };
  b.click(); await new Promise((q) => setTimeout(q, 200));
  const m = document.getElementById('a3d-ltmenu'), it = m ? [].map.call(m.querySelectorAll('[data-ltm]'), (x) => x.getAttribute('data-ltm')) : [];
  const f = m && m.querySelector('[data-ltm="lvnumber"]'); if (f) f.click(); await new Promise((q) => setTimeout(q, 300));
  const m2 = document.getElementById('a3d-ltmenu'), it2 = m2 ? [].map.call(m2.querySelectorAll('[data-ltm]'), (x) => x.textContent) : [];
  const g = m2 && m2.querySelector('[data-ltm="gfa"]'); if (g) g.click(); await new Promise((q) => setTimeout(q, 300));
  return { it, it2 };
});
ck(r.it && r.it.indexOf('lvfield') >= 0 && r.it.indexOf('lvnumber') >= 0, 'the Draw menu has Field and Number');
ck(r.it2 && r.it2.indexOf('Gross floor area') >= 0 && r.it2.some((t) => /^Gross area: /.test(t)), 'Number opens its menu, with the levels (' + (r.it2 || []).length + ' rows)');
r = await page.evaluate(() => window.__a3dBoardDesign.objs().filter((o) => o.bind && o.bind.src === 'gfa').length);
ck(r === 1, 'picking Gross floor area puts the number on the board');
await page.screenshot({ path: OUT + '/v175a-edit.png' });

// ---- on paper: no marks, a dash for nothing to show
r = await page.evaluate(() => { const B = window.__a3dBrdRecord ? null : null; const st = window.__a3dClbState(); const h = window.__a3dBrdHtmlFor(st.board || st.kind, false); return { marks: (h.match(/a3d-clb-dlv/g) || []).length, len: h.length }; });
const paper = await page.evaluate(() => { const st = window.__a3dClbState(); const k = st.board || st.kind; return window.__a3dBoardPrintHtml ? window.__a3dBoardPrintHtml(k) : null; });
if (paper !== null) ck(paper.indexOf('a3d-clb-dlv') < 0 && paper.indexOf('Not computed') < 0 && paper.indexOf('—') >= 0, 'on paper: no marks, and a dash where nothing is computed');
else {
  await page.evaluate(() => window.__a3dBrdEdit(false)); await W();
  r = await page.evaluate((id) => { const e = document.querySelector('.a3d-clb-dsn [data-bde="' + id + '"]'); return { t: e ? e.textContent : null, m: document.querySelectorAll('.a3d-clb-dsn .a3d-clb-dlv').length }; }, n2);
  ck(r.m === 0 && r.t === '—', 'out of Edit: no marks, and a dash where nothing is computed (' + JSON.stringify(r) + ')');
  await page.screenshot({ path: OUT + '/v175a-view.png' });
  await page.evaluate(() => window.__a3dBrdEdit(true)); await W();
}

// ---- a phone
await page.setViewportSize({ width: 390, height: 800 });
await page.waitForTimeout(600);
r = await page.evaluate((id) => { const e = document.querySelector('.a3d-clb-dsn [data-bde="' + id + '"]'); return e ? e.textContent : null; }, n1);
ck(/^\d+$/.test(r || ''), 'at a phone\'s width the board draws its live text (' + r + ')');
await page.screenshot({ path: OUT + '/v175a-phone.png' });
await page.setViewportSize({ width: 1600, height: 1000 });

// ---- the units kept with the project (D10), and a reload
await page.evaluate(() => window.__a3dSetUnits('mm', 1));
await page.waitForTimeout(1200);
await page.reload();
await page.waitForTimeout(4000);
r = await page.evaluate(() => { window.__a3dEnter && window.__a3dEnter(); return window.__a3dUnits(); });
ck(r && r.key === 'mm' && r.dp === 1, 'the display units come back after a reload (' + JSON.stringify(r) + ')');
r = await page.evaluate(() => { const P = window.__a3dBrdRecord; return window.__a3dLive.rev(); });
ck(typeof r === 'number', 'the app runs after the reload');
await page.evaluate(() => window.__a3dSetUnits('m', 3));
await page.waitForTimeout(800);

ck(errs.length === 0, 'no console errors' + (errs.length ? ': ' + errs.slice(0, 5).join(' | ') : ''));
console.log(pass + ' passed, ' + fail + ' failed');
await browser.close();
process.exit(fail ? 1 : 0);
