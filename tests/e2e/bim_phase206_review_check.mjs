/* bim_phase206_review_check.mjs -- V206's browser check: the Review view (io/thatopen-review.js) and the import through
   That Open (io/thatopen-runtime.js), driven through the page as a person would, on the committed fixture
   tests/fixtures/ifc/v177_wall_ifcos.ifc (the app's own IFC save: one wall on one storey).
     node tests/e2e/bim_phase206_review_check.mjs [http|file] [screenshot dir]
   Uses the Playwright and Chromium preinstalled in the container (/opt/node-tools, /opt/pw-browsers). */
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const mode = process.argv[2] || 'http', shots = process.argv[3] || '';
const FIX = path.join(root, 'tests/fixtures/ifc/v177_wall_ifcos.ifc'), GUID = '3fUx7AAmz4fPtpAGQY2IfE';
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json' };
const srv = http.createServer((q, r) => { const p = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); });
await new Promise((r) => srv.listen(0, '127.0.0.1', r));
const url = mode === 'file' ? 'file://' + path.join(root, 'canvas_v10.html') : 'http://127.0.0.1:' + srv.address().port + '/canvas_v10.html';
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
let pass = 0, fail = 0;
const ck = (ok, msg) => { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + msg); };
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
const errs = []; page.on('pageerror', (e) => errs.push(String(e).slice(0, 300)));
page.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 300)); });
console.log('V206 check, ' + mode + ', Chromium ' + browser.version());
await page.goto(url);
await page.waitForFunction(() => window.__acad3dV206 && window.__a3dRunCmd, null, { timeout: 60000 });
ck(/review/.test(await page.evaluate(() => window.__acad3dV206)), 'the V206 marker');
await page.evaluate(() => { window.__a3dEnter(); window.__a3dTestSetObjs([]); });
const status = () => page.locator('.a3d-rvw-status').textContent();

// REVIEW opens the view and loads That Open on demand
ck(await page.evaluate(() => !window.BIMTOE), 'That Open is not loaded before it is asked for');
await page.evaluate(() => window.__a3dRunCmd('review'));
await page.waitForSelector('.a3d-review');
await page.waitForFunction(() => /Select/.test(document.querySelector('.a3d-rvw-status').textContent), null, { timeout: 60000 });
ck(await page.evaluate(() => !!(window.BIMTOE && window.BIMWEBIFC && window.BIMTHREE)), 'REVIEW loads That Open, web-ifc and the app\'s three.js');
ck(await page.locator('.a3d-rvw-bar [data-rvwmode="select"].on').count() === 1, 'the view opens in Select');

// two files at once: the fixture twice, federated
await page.setInputFiles('[data-rvwfile]', [FIX, FIX]);
await page.waitForFunction(() => /2 models under review/.test(document.querySelector('.a3d-rvw-status').textContent), null, { timeout: 60000 });
const tree = await page.locator('.a3d-rvw-tree').innerText();
ck((tree.match(/v177_wall_ifcos\.ifc/g) || []).length === 2 && /IfcWall\s*1/.test(tree), 'the tree: both models, a storey, IfcWall 1 (' + tree.replace(/\s+/g, ' ').slice(0, 160) + ')');
const ink = await page.evaluate(() => { const c = document.querySelector('.a3d-rvw-view canvas'); return c ? [c.width, c.height] : null; });
ck(ink && ink[0] > 300 && ink[1] > 200, 'the model is drawn in a canvas of its own (' + ink + ')');
if (shots) await page.screenshot({ path: path.join(shots, 'review-desktop-' + mode + '.png') });

// a class in the tree selects its elements, and the data shows: class, GlobalId, storey, property sets
await page.locator('[data-rvwsel]').first().click();
await page.waitForFunction((g) => document.querySelector('.a3d-rvw-props') && document.querySelector('.a3d-rvw-props').textContent.indexOf(g) >= 0, GUID, { timeout: 20000 });
const props = await page.locator('.a3d-rvw-props').innerText();
ck(/IfcWall/.test(props) && props.indexOf(GUID) >= 0 && /Contained in/.test(props), 'selecting shows the IFC data with the GlobalId (' + props.replace(/\s+/g, ' ').slice(0, 140) + ')');
if (shots) await page.screenshot({ path: path.join(shots, 'review-selected-' + mode + '.png') });

// hide, show all
await page.click('[data-rvw="hide"]');
await page.waitForTimeout(500);
let hidden = await page.evaluate(async () => { const R = window.__a3dReview(); const v = await R.hider.getVisibilityMap(false); return Object.values(v).reduce((n, a) => n + a.length, 0); });
ck(hidden >= 1, 'Hide hides the selection (' + hidden + ' hidden)');
await page.click('[data-rvw="show"]');
await page.waitForTimeout(500);
hidden = await page.evaluate(async () => { const R = window.__a3dReview(); const v = await R.hider.getVisibilityMap(false); return Object.values(v).reduce((n, a) => n + a.length, 0); });
ck(hidden === 0, 'Show all shows everything again');

// Section: a double-click on the wall's face cuts there; the status counts with bimTorClip
await page.click('[data-rvwmode="clip"]');
const box = await page.locator('.a3d-rvw-view').boundingBox();
let hit = null;
for (const [fx, fy] of [[0.5, 0.5], [0.45, 0.55], [0.55, 0.45], [0.5, 0.6], [0.4, 0.5]]) {
  await page.mouse.dblclick(box.x + box.width * fx, box.y + box.height * fy);
  await page.waitForTimeout(600);
  hit = await page.evaluate(() => window.__a3dReview().clip.list.size);
  if (hit) break;
}
ck(hit >= 1 && /Section: 1 plane; \d+ of \d+ elements have their placement point/.test(await status()), 'Section: a plane on the face (' + (await status()) + ')');
await page.click('[data-rvw="clear"]');
ck(await page.evaluate(() => window.__a3dReview().clip.list.size) === 0, 'Clear removes the planes');

// Length: two double-clicks on the model
await page.click('[data-rvwmode="length"]');
let len = 0;
for (const pts of [[[0.42, 0.5], [0.58, 0.5]], [[0.45, 0.45], [0.55, 0.55]], [[0.4, 0.55], [0.6, 0.55]]]) {
  for (const [fx, fy] of pts) { await page.mouse.dblclick(box.x + box.width * fx, box.y + box.height * fy); await page.waitForTimeout(400); }
  len = await page.evaluate(() => window.__a3dReview().len.list.size);
  if (len) break;
}
ck(len >= 1 && /Length: (0\.0*[1-9]|[1-9])/.test(await status()), 'Length: measured on the model (' + (await status()) + ')');
await page.keyboard.press('Escape');
ck(await page.locator('[data-rvwmode="select"].on').count() === 1, 'Escape goes back to Select');

// phone width: the bar wraps, the tree goes under the view, nothing overflows
await page.setViewportSize({ width: 390, height: 844 });
await page.waitForTimeout(500);
const lay = await page.evaluate(() => { const v = document.querySelector('.a3d-rvw-view').getBoundingClientRect(), s = document.querySelector('.a3d-rvw-side').getBoundingClientRect();
  return { scroll: document.documentElement.scrollWidth - window.innerWidth, under: s.top >= v.bottom - 1, viewH: v.height, sideBottom: s.bottom, h: window.innerHeight }; });
ck(lay.scroll <= 0 && lay.under && lay.viewH > 200 && lay.sideBottom <= lay.h, 'on a phone the data goes under the view, no sideways scroll (' + JSON.stringify(lay) + ')');
if (shots) await page.screenshot({ path: path.join(shots, 'review-phone-' + mode + '.png') });
await page.setViewportSize({ width: 1400, height: 900 });

// Import: the selected model into the editable model, through That Open, under its GlobalId; the view closes
await page.locator('[data-rvwsel]').first().click();
await page.waitForTimeout(300);
await page.click('[data-rvw="import"]');
await page.waitForFunction(() => !document.querySelector('.a3d-review'), null, { timeout: 10000 });
const got = await page.waitForFunction((g) => { const s = window.__a3dIfcEdit && window.__a3dIfcEdit.list && window.__a3dIfcEdit.list();
  return s && s.length ? s : null; }, GUID, { timeout: 60000 }).then((h) => h.jsonValue()).catch(() => null);
ck(got && got.some((x) => x.guid === GUID && x.type === 'wall'), 'Import brings the wall in under its GlobalId, offered for Make editable (' + JSON.stringify(got) + ')');

// Make editable on a wall That Open read: the app's own wall stands where the imported one stood (the shift, e02)
const ed = await page.evaluate((g) => { const L = window.__a3dIfcEdit.list(), w = L.find((x) => x.guid === g && !x.why);
  if (!w) return { none: L };
  const b0 = window.__a3dIfcEdit.info(w.id).box, id = window.__a3dIfcEdit.make(w.id);
  return { b0, b1: id ? window.__a3dIfcEdit.info(id).box : null }; }, GUID);
const same = (a, b) => a && b && a.every((v, i) => Math.abs(v - b[i]) < 0.03);
ck(same(ed.b0, ed.b1), 'Make editable on That Open\'s import: in its place (' + JSON.stringify(ed) + ')');

// REVIEW again opens and closes cleanly
await page.evaluate(() => window.__a3dRunCmd('review'));
await page.waitForSelector('.a3d-review');
await page.keyboard.press('Escape');
ck(await page.locator('.a3d-review').count() === 0, 'Escape closes the view');
ck(errs.length === 0, 'no page or console errors' + (errs.length ? ': ' + errs.join(' | ') : ''));
console.log(pass + ' passed, ' + fail + ' failed');
await browser.close(); srv.close();
process.exit(fail ? 1 : 0);
