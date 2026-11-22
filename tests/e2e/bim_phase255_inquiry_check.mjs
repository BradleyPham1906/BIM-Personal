/* bim_phase255_inquiry_check.mjs -- V255's browser check (D8, docs/research/research-cadcraft-gap.md): DIST, ID,
   AREA (picked points, then a selected circle) and LIST, typed as a user types them; the points are picked with the
   page's own mouse on snapped grid points; the answers are read from the read-out window, and nothing is added to
   the drawing.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase255_inquiry_check.mjs <a folder for the screenshots> */
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
function ck(ok, msg) { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + msg); }
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




const run = (c) => ev(`return window.__a3dRunCmd(${JSON.stringify(c)});`);
const readout = () => ev(`const d=document.querySelector('[data-a3dinq]');if(!d)return null;const o={};d.querySelectorAll('[data-a3dinqv]').forEach(e=>o[e.getAttribute('data-a3dinqv')]=e.textContent);return o;`);
const close = () => ev(`const b=document.querySelector('[data-a3dinq] [data-a3dlg]');if(b)b.click();`);
const count = () => ev('return window.__a3dObjects().length;');
await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:3,ty:0,tz:0,dist:30});
  window.__a3dSnapSet({point:false,grid:true,ortho:false});`);
await sleep(800);
await run('inqdist'); await click([0, 0]); await click([3, 4]);
let R = await readout();
ck(R && /^5(\.0+)? m$/.test(R.Distance) && /^53\.13/.test(R['Angle in plan']), 'DIST: 5 m at 53.13 degrees (' + JSON.stringify(R) + ')');
await shot('v255-01-dist'); await close();
await run('inqid'); await click([2, 1]);
R = await readout();
ck(R && /X 2\.000\s+Y 1\.000/.test(R.Point), 'ID: the point (' + JSON.stringify(R) + ')'); await close();
await run('inqarea'); await click([0, 0]); await click([4, 0]); await click([4, 3]); await click([0, 3]); await tap('Enter');
R = await readout();
ck(R && /^12(\.0+)? m²$/.test(R.Area) && /^14/.test(R.Perimeter), 'AREA of picked points: 12 m2, perimeter 14 (' + JSON.stringify(R) + ')'); await close();
ck(await count() === 0, 'nothing was added to the drawing');
// a circle of radius 2, then AREA and LIST of it selected
await run('circle'); await click([10, 0]); await click([12, 0]);
const cid = (await ev('return window.__a3dSketchWorld();'))[0].id;
await ev(`window.__a3dSelectFor([${JSON.stringify(cid)}]);`);
await run('inqarea'); R = await readout();
ck(R && Math.abs(parseFloat(R['Total area']) - 4 * Math.PI) < 0.01, 'AREA of a selected circle: 4 pi (' + JSON.stringify(R) + ')'); await close();
await run('inqlist'); R = await readout();
ck(R && R.Type === 'Circle' && Math.abs(parseFloat(R.Perimeter) - 4 * Math.PI) < 0.01, 'LIST of the circle (' + JSON.stringify(R) + ')');
await shot('v255-02-list');
const real = errors.filter((e) => !/favicon\.ico/.test(e));
ck(real.length === 0, 'no console errors (' + real.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
