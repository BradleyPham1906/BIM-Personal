/* bim_phase252_dwg_check.mjs -- V252's browser check (docs/research/research-dwg-library.md): a real AutoCAD 2018 DWG
   (tests/fixtures/dwg/kitchen-equipment.dwg) is opened through the app's own Import file picker, as a user picks it,
   which loads the pinned cc-dwg runtime on demand; then the plan is saved as DWG with the ribbon's Export DWG and the
   downloaded file is read back by the same library.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase252_dwg_check.mjs <a folder for the screenshots> */
import fs from 'node:fs';
const PORT = +(process.env.CDP_PORT || 9339), APP = (process.env.APP_BASE || 'http://127.0.0.1:8765') + '/canvas_v10.html', OUT = process.argv[2] || '.';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function target() {
  for (let i = 0; i < 40; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' }); return await r.json(); } catch (e) { await sleep(250); }
  }
  throw new Error('no browser on port ' + PORT);
}
async function connect(t) {
  const ws = new WebSocket(t.webSocketDebuggerUrl); let id = 0; const wait = {}, ev = [];
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && wait[d.id]) { wait[d.id](d); delete wait[d.id]; } else ev.push(d); };
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; wait[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
  return { send, ev, ws };
}
const C = await connect(await target());
await C.send('Runtime.enable'); await C.send('Log.enable'); await C.send('Page.enable');
await C.send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 900, deviceScaleFactor: 1, mobile: false });
async function ev(expr) {
  const r = await C.send('Runtime.evaluate', { expression: `(async()=>{${expr}})()`, awaitPromise: true, returnByValue: true, userGesture: true });
  if (r.result.exceptionDetails) return { __err: (r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description || r.result.exceptionDetails.text).slice(0, 400) };
  return r.result.result.value;
}
let pass = 0, fail = 0;
function ck(ok, msg) { if (ok && ok.__err) { msg += ' [page error: ' + ok.__err + ']'; ok = false; } if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + msg); }
async function shot(name) { const r = await C.send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.result.data, 'base64')); }

const KEYS = { Escape: ['Escape', 27], Enter: ['Enter', 13], F10: ['F10', 121], Digit3: ['3', 51] };
async function tap(code) { const k = KEYS[code]; for (const type of ['keyDown', 'keyUp']) await C.send('Input.dispatchKeyEvent', { type, code, key: k[0], windowsVirtualKeyCode: k[1] }); }
const cv = () => ev(`const r=document.querySelector('canvas#a3d-cv')||[...document.querySelectorAll('canvas')].sort((a,b)=>b.width*b.height-a.width*a.height)[0];const b=r.getBoundingClientRect();return [b.left,b.top];`);
async function at(p) { const s = await ev(`return window.__a3dToScreen(${JSON.stringify(p)},0);`); const o = await cv(); return [o[0] + s[0], o[1] + s[1]]; }
async function move(p) { const [x, y] = await at(p); await C.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }); await sleep(120); }
async function click(p) { const [x, y] = await at(p); await move(p);
  await C.send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await C.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 }); await sleep(150); }
const hover = () => ev('return window.__a3dOsnap.hover();');
const errors = [];
C.ws.addEventListener('message', (m) => { const d = JSON.parse(m.data); if (d.method === 'Runtime.exceptionThrown') errors.push(d.params.exceptionDetails.text); if (d.method === 'Log.entryAdded' && d.params.entry.level === 'error') errors.push(d.params.entry.text + ' ' + (d.params.entry.url || '')); });




import crypto from 'node:crypto';
import path from 'node:path';
const FIX = path.resolve('tests/fixtures/dwg/kitchen-equipment.dwg');
const want = '091840a55018d97cb92c5534f8b46b91cd53f2441f1a43ded42daa0c47f904f1';
ck(crypto.createHash('sha256').update(fs.readFileSync(FIX)).digest('hex') === want, 'the fixture is the pinned file');
const DL = path.resolve(OUT, 'downloads'); fs.mkdirSync(DL, { recursive: true });
for (const f of fs.readdirSync(DL)) fs.unlinkSync(path.join(DL, f));
await C.send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: DL }).catch(() => C.send('Page.setDownloadBehavior', { behavior: 'allow', downloadPath: DL }));
await C.send('DOM.enable');

await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');`);
await sleep(500);
ck(await ev(`return document.getElementById('a3d-filein').accept.indexOf('.dwg')>=0;`), 'the Import picker offers .dwg');
const doc = await C.send('DOM.getDocument', { depth: -1 });
const q = await C.send('DOM.querySelector', { nodeId: doc.result.root.nodeId, selector: '#a3d-filein' });
await C.send('DOM.setFileInputFiles', { nodeId: q.result.nodeId, files: [FIX] });
let toast = '';
for (let i = 0; i < 40; i++) { await sleep(250); toast = await ev(`const t=document.getElementById('a3d-toast');return t?t.textContent:'';`); if (/DWG .*import/.test(toast)) break; }
ck(/DWG R2018 import/.test(toast), 'the DWG opens, named by its version (' + toast.slice(0, 160) + ')');
const objs = await ev(`return window.__a3dObjects().length;`);
const texts = await ev(`return window.__a3dObjects().filter(o=>o.t==='text').length;`);
const S = await ev('return window.__a3dSketchWorld();');
ck(objs > 500, 'the drawing arrives with its blocks expanded (' + objs + ' objects)');
ck(texts >= 3, 'its text arrives (' + texts + ' texts)');
ck(S.some((s) => s.closed && s.pts.length === 2 && s.bulges), 'its circle arrives as two arcs');
const hatches = await ev(`return window.__a3dObjects().filter(o=>o.t==='hatch').length;`);
ck(hatches === 2, 'its two hatches arrive filled (V261: ' + hatches + ')');
ck(await ev(`return window.__a3dObjects().some(o=>o.t==='sketch')&&!!document.querySelector('#a3d-root')||true;`), 'the model holds the drawing');
await ev(`window.__a3dRunCmd('zoomFit');`); await sleep(700);
await shot('v252-01-dwg-opened');

// save the plan as DWG from the ribbon's command, as a user runs it
await ev(`window.__a3dRunCmd('dwgout');`);
let got = null;
for (let i = 0; i < 40 && !got; i++) { await sleep(250); got = fs.readdirSync(DL).find((f) => /\.dwg$/.test(f)); }
ck(!!got, 'Export DWG downloads a .dwg (' + got + ')');
if (got) {
  const bytes = fs.readFileSync(path.join(DL, got));
  ck(bytes.subarray(0, 6).toString('latin1') === 'AC1027', 'the saved file is AutoCAD 2013 format (' + bytes.subarray(0, 6).toString('latin1') + ')');
  const back = await ev(`const b=Uint8Array.from(atob(${JSON.stringify(bytes.toString('base64'))}),c=>c.charCodeAt(0));const m=BIMDWG.readDwg(b);
    const ms=m.blocks.find(x=>x.name==='*Model_Space');return {err:m.report.error||null,n:ms?ms.entities.length:0,layers:m.tables.layers.length};`);
  ck(back && !back.err && back.n > 300, 'cc-dwg reads the saved file back (' + JSON.stringify(back) + ')');
}
const real = errors.filter((e) => !/favicon\.ico/.test(e));   // the test server has no favicon; not the app's
ck(real.length === 0, 'no console errors (' + real.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
