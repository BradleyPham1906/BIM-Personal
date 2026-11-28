// e03 (V206 WO-09): the app's own IFC import, through That Open and through cc-ifc, on V196's 13 files, compared class
// by class (bimTorCompare), with GlobalIds, storeys, property sets, triangles and the model's box.
//   node run.mjs <dir of the 13 files> [file|http]
// Drives canvas_v10.html (the build) in Chromium; over http from the repository's root, or from file://.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url)), root = path.resolve(here, '../../../../..');
const dir = process.argv[2], mode = process.argv[3] || 'http';
const files = fs.readdirSync(dir).filter((f) => f.endsWith('.ifc')).sort((a, b) => fs.statSync(path.join(dir, a)).size - fs.statSync(path.join(dir, b)).size);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.wasm': 'application/wasm' };
const srv = http.createServer((q, r) => { const p = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); });
await new Promise((r) => srv.listen(0, '127.0.0.1', r));
const url = mode === 'file' ? 'file://' + path.join(root, 'canvas_v10.html') : 'http://127.0.0.1:' + srv.address().port + '/canvas_v10.html';
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--js-flags=--max-old-space-size=6144'] });
console.log('e03 ' + new Date().toISOString().slice(0, 10) + ', Chromium ' + browser.version() + ', ' + mode + ', ' + url.replace(/:\d+\//, ':<port>/'));
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
const errs = []; page.on('pageerror', (e) => errs.push(String(e).slice(0, 300)));
await page.goto(url); await page.waitForFunction(() => window.__acad3dV206 && window.__a3dToe, null, { timeout: 60000 });
await page.evaluate(() => { window.__a3dEnter(); });
let agree = 0;
for (const f of files) {
  const b64 = fs.readFileSync(path.join(dir, f)).toString('base64');
  const one = async (eng) => page.evaluate(async ([b, n, e]) => {
    window.__a3dTestSetObjs([]); window.__a3dToe.use(e);
    const bin = atob(b), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
    const t0 = performance.now(); let R;
    try { R = await window.__a3dIfc.importBuffer(u, n); } catch (x) { return { error: String(x && x.message || x).slice(0, 300) }; }
    const S = window.__a3dToe.summary(R.ids); S.ms = Math.round(performance.now() - t0); S.engine = R.engine; S.n = R.ids.length; S.levels = R.levels;
    S.cut = R.cut; S.stages = R.stages; S.readMs = R.readMs; S.coord = R.coord ? [R.coord[12], R.coord[13], R.coord[14]].map((x) => Math.round(x * 1000) / 1000) : null;
    window.__a3dTestSetObjs([]); return S;
  }, [b64, f, eng]);
  // ENGINE_ORDER=cc-first runs cc-ifc first, so the app's first-paint costs fall on it (they are not the reader's)
  let A, B;
  if (process.env.ENGINE_ORDER === 'cc-first') { B = await one('cc-ifc'); A = await one('thatopen'); }
  else { A = await one('thatopen'); B = await one('cc-ifc'); }
  const C = A.byClass && B.byClass ? await page.evaluate(([a, b]) => window.__a3dToe.compare(a, b), [A.byClass, B.byClass]) : null;
  const boxOk = A.box && B.box && A.box.every((v, i) => Math.abs(v - B.box[i]) <= 0.01);
  const ok = C && C.diff.length === 0 && boxOk && A.guids === A.n;
  if (ok) agree++;
  console.log(JSON.stringify({ file: f, bytes: fs.statSync(path.join(dir, f)).size, agree: !!ok,
    thatopen: A.error || { engine: A.engine, stages: A.stages, readMs: A.readMs, n: A.n, guids: A.guids, bad: A.bad, storeys: A.storeys, levels: A.levels, psets: A.psets, tris: A.tris, box: A.box, coord: A.coord, ms: A.ms, cut: A.cut },
    ccifc: B.error || { engine: B.engine, readMs: B.readMs, n: B.n, guids: B.guids, storeys: B.storeys, levels: B.levels, psets: B.psets, tris: B.tris, box: B.box, coord: B.coord, ms: B.ms, cut: B.cut },
    classesSame: C && C.same.length, classDiff: C && C.diff }));
}
console.log('agree on ' + agree + ' of ' + files.length + '; page errors: ' + (errs.length ? errs.join(' | ') : 'none'));
await browser.close(); srv.close();
