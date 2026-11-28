/* bim_phase308_design_check.mjs -- V308's browser check: DESIGN (bim/bimcraft-design.js) on BimCraft's authoring core
   (runtime/bimcraft), driven through the page as a person would: clicks on BimCraft's own plan view.
     node tests/e2e/bim_phase308_design_check.mjs [http|file] [screenshot dir]
   Uses the Playwright and Chromium preinstalled in the container (/opt/node-tools, /opt/pw-browsers). */
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const mode = process.argv[2] || 'http', shots = process.argv[3] || '';
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.wasm': 'application/wasm' };
const srv = http.createServer((q, r) => { const p = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); });
await new Promise((r) => srv.listen(0, '127.0.0.1', r));
const url = mode === 'file' ? 'file://' + path.join(root, 'canvas_v10.html') : 'http://127.0.0.1:' + srv.address().port + '/canvas_v10.html';
const browser = await chromium.launch();
let pass = 0, fail = 0;
const ck = (ok, msg) => { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + msg); };
const page = await browser.newPage({ viewport: { width: 1400, height: 900 }, acceptDownloads: true });
const errs = []; page.on('pageerror', (e) => errs.push(String(e).slice(0, 300)));
page.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 300)); });
console.log('V308 check, ' + mode + ', Chromium ' + browser.version());
await page.goto(url);
await page.waitForFunction(() => window.__acad3dV308 && window.__a3dRunCmd, null, { timeout: 60000 });
await page.evaluate(() => { window.__a3dEnter(); window.__a3dTestSetObjs([]); });
const status = () => page.locator('.a3d-design .a3d-rvw-status').textContent();
const snap = () => page.evaluate(() => { const D = window.__a3dDesign(), s = D.C.modelOps.snapshotModel(D.ed);
  return { walls: s.walls.length, types: s.walls.map((w) => w.typeKey), doors: s.openings.filter((o) => o.kind === 'door').map((o) => o.mark),
    windows: s.openings.filter((o) => o.kind === 'window').map((o) => o.mark), rooms: s.derived.spaces.length, floors: s.derived.floors.length, roofs: s.derived.roofs.length }; });
// a click on the plan at plan millimetres, through BimCraft's own view (toScreen)
const at = async (x, y) => { const p = await page.evaluate(([x, y]) => { const D = window.__a3dDesign(), s = D.pv.toScreen([x, y]), r = D.pv.canvas.getBoundingClientRect(); return { x: r.left + s.x, y: r.top + s.y }; }, [x, y]); return p; };
const click = async (x, y) => { const p = await at(x, y); await page.mouse.click(p.x, p.y); await page.waitForTimeout(120); };

ck(await page.evaluate(() => !window.BIMCRAFT), 'BimCraft\'s core is not loaded before DESIGN');
await page.evaluate(() => window.__a3dRunCmd('design'));
await page.waitForFunction(() => window.__a3dDesign().ed && document.querySelector('.a3d-design [data-dsntool="wall"].on'), null, { timeout: 60000 });
ck(await page.evaluate((m) => !!(window.BIMCRAFT && window.BIMCRAFT.modelOps && (m === 'file' || window.BIMIFC)), mode), 'DESIGN loads BimCraft\'s core (and over http the app\'s IFC runtime for Manifold), and opens on the Wall tool');
const lv = await page.evaluate(() => [...document.querySelectorAll('[data-dsnlevel] option')].map((o) => o.textContent));
ck(lv.length >= 1, 'the building starts on the app\'s levels (' + lv.join(', ') + ')');

// walls: a 10 x 7 m ring of ext-300, then a 100 mm partition; zoom so the plan fits
await page.evaluate(() => { const D = window.__a3dDesign(); D.pv.cx = 5000; D.pv.cy = 3500; D.pv.scale = 0.06; D.pv.render(); });
for (const [x, y] of [[0, 0], [10000, 0], [10000, 7000], [0, 7000], [0, 0]]) await click(x, y);
await page.keyboard.press('Enter');
await page.waitForTimeout(300);
let s = await snap();
ck(s.walls === 4 && s.types.every((t) => t === 'ext-300'), 'four ext-300 walls drawn by clicks, closed into a ring (' + JSON.stringify(s) + ')');
await page.selectOption('[data-dsntype="wall"]', 'int-100');
await click(5000, 0); await click(5000, 7000); await page.keyboard.press('Enter'); await page.waitForTimeout(300);
s = await snap();
ck(s.walls >= 5 && s.types.includes('int-100'), 'a 100 mm partition (' + s.walls + ' wall pieces)');
// a door and a window clicked on walls
await page.click('[data-dsntool="door"]'); await click(2500, 40);
await page.click('[data-dsntool="window"]'); await click(7500, 7000);
s = await snap();
ck(s.doors.length === 1 && s.windows.length === 1, 'a door and a window placed by a click on their walls, marked ' + s.doors.concat(s.windows).join(', '));
// a floor in the west room, a roof, a section line
await page.click('[data-dsntool="floor"]'); await click(2500, 3500);
await page.click('[data-dsntool="roof"]'); await click(2500, 3500);
await page.click('[data-dsntool="section"]'); await click(2500, 1000); await click(2500, 6000);   // inside the fitted plan
s = await snap();
ck(s.floors === 1 && s.rooms >= 1 && s.roofs === 1, 'a floor (its room counted) and a roof (' + JSON.stringify({ floors: s.floors, rooms: s.rooms, roofs: s.roofs }) + ')');
ck(/Section A placed/.test(await status()), 'section line A placed (' + (await status()) + ')');
// BimCraft's plan scene: cut wall pieces, the door's swing and the window's symbol, the room labelled
const sc = await page.evaluate(() => { const sc = window.__a3dDesign().pv.scene;
  return { walls: sc.walls.length, pieces: sc.walls.reduce((n, w) => n + (w.pieces || []).length, 0), symbols: sc.symbols.length,
    arcs: sc.symbols.reduce((n, x) => n + ((x.arcs || []).length), 0), rooms: (sc.rooms || []).map((r) => r.label.join(' ')) }; });
ck(sc.symbols === 2 && sc.arcs >= 1 && sc.pieces > sc.walls, 'the live plan: walls cut round the openings, the door\'s swing arc, the window\'s symbol (' + JSON.stringify(sc) + ')');
ck(sc.rooms.length >= 1 && /m2/.test(sc.rooms[0]) && !/model\./.test(sc.rooms.join()), 'the room labelled with its area (' + sc.rooms.join('; ') + ')');
if (shots) await page.screenshot({ path: path.join(shots, 'design-' + mode + '.png') });
// undo and redo the last change
await page.click('[data-dsn="undo"]'); const und = await page.evaluate(() => window.BIMCRAFT.resSheets.readSectionLines(new window.BIMCRAFT.modelWrite.ModelWriter(window.BIMCRAFT.ifc, window.__a3dDesign().ed.api, window.__a3dDesign().ed.mid)).length);
await page.click('[data-dsn="redo"]'); const red = await page.evaluate(() => window.BIMCRAFT.resSheets.readSectionLines(new window.BIMCRAFT.modelWrite.ModelWriter(window.BIMCRAFT.ifc, window.__a3dDesign().ed.api, window.__a3dDesign().ed.mid)).length);
ck(und === 0 && red === 1, 'Undo takes the section line away, Redo puts it back');
// the drawing set and the plan, as PDFs
let dl = page.waitForEvent('download', { timeout: 60000 });
await page.click('[data-dsn="set"]');
let d = await dl, pdf = fs.readFileSync(await d.path());
const pages = (pdf.toString('latin1').match(/\/Type \/Page\b/g) || []).length;
ck(pdf.subarray(0, 5).toString() === '%PDF-' && pages >= 4 && /Drawing set: \d+ sheets/.test(await status()), 'the drawing set as one PDF: ' + pages + ' pages (' + (await status()) + ')');
dl = page.waitForEvent('download', { timeout: 30000 });
await page.click('[data-dsn="plan"]');
d = await dl; pdf = fs.readFileSync(await d.path());
ck(pdf.subarray(0, 5).toString() === '%PDF-' && /plan\.pdf$/.test(d.suggestedFilename()), 'the level\'s plan as a PDF (' + d.suggestedFilename() + ', ' + pdf.length + ' bytes)');
// Send to model: the building comes in through the app's IFC import with its GlobalIds; a second send replaces it
await page.click('[data-dsn="send"]');
await page.waitForFunction(() => /In the model: \d+/.test(document.querySelector('.a3d-design .a3d-rvw-status').textContent), null, { timeout: 60000 });
const in1 = await page.evaluate(() => window.__a3dIfcEdit.list ? window.__a3dIfcEdit.list().length : 0);
const n1 = await page.evaluate(() => window.__a3dToe.summary(window.__a3dIfcEdit.list().map((x) => x.id)));
await page.evaluate(() => { const st = document.querySelector('.a3d-design .a3d-rvw-status'); window.__dsnLog = [];
  new MutationObserver(() => window.__dsnLog.push(st.textContent)).observe(st, { childList: true, characterData: true, subtree: true }); });
await page.click('[data-dsn="send"]');
await page.waitForFunction(() => { const L = window.__dsnLog, i = L.findIndex((t) => /replacing the \d+ elements/.test(t)); return i >= 0 && L.slice(i).some((t) => /In the model: \d+/.test(t)); }, null, { timeout: 60000 });
const in2 = await page.evaluate(() => window.__a3dIfcEdit.list().length);
ck(in1 >= 6 && in2 === in1, 'Send to model: ' + in1 + ' elements offered for Make editable, the walls by class (' + JSON.stringify(n1.byClass) + '); a second send replaces them (' + in2 + ')');
// phone width
await page.setViewportSize({ width: 390, height: 844 }); await page.waitForTimeout(400);
const lay = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth - window.innerWidth, canvas: document.querySelector('.a3d-dsn-plan canvas').getBoundingClientRect().height }));
ck(lay.scroll <= 0 && lay.canvas > 150, 'on a phone the plan stays usable, no sideways scroll (' + JSON.stringify(lay) + ')');
if (shots) await page.screenshot({ path: path.join(shots, 'design-phone-' + mode + '.png') });
await page.setViewportSize({ width: 1400, height: 900 });
await page.keyboard.press('Escape'); await page.keyboard.press('Escape');
ck(await page.locator('.a3d-design').count() === 0, 'Escape leaves the tool, then closes Design');
ck(errs.length === 0, 'no page or console errors' + (errs.length ? ': ' + errs.join(' | ') : ''));
console.log(pass + ' passed, ' + fail + ' failed');
await browser.close(); srv.close();
process.exit(fail ? 1 : 0);
