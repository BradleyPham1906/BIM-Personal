/* bim_phase251_dxf_import_check.mjs -- V251's browser check (D7, docs/research/research-cadcraft-gap.md): a DXF with
   a block inserted twice (once turned, once mirrored), a nested block, a dimension's block, TEXT, MTEXT, an ELLIPSE,
   a SPLINE and a CIRCLE goes through the app's own importer (__a3dImportDXF, the code a picked file reaches), and the
   drawing is read back and photographed.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase251_dxf_import_check.mjs <a folder for the screenshots> */
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



const dxf = (pairs) => pairs.map(([c, v]) => `${c}\n${v}`).join('\n') + '\n0\nEOF\n';
const FILE = dxf([
  [0, 'SECTION'], [2, 'HEADER'], [9, '$INSUNITS'], [70, 6], [0, 'ENDSEC'],
  [0, 'SECTION'], [2, 'TABLES'], [0, 'TABLE'], [2, 'LAYER'],
  [0, 'LAYER'], [2, 'DOORS'], [62, 1], [70, 0], [0, 'LAYER'], [2, 'NOTES'], [62, 2], [70, 0], [0, 'ENDTAB'], [0, 'ENDSEC'],
  [0, 'SECTION'], [2, 'BLOCKS'],
  [0, 'BLOCK'], [8, '0'], [2, 'LEAF'], [10, 0], [20, 0],
  [0, 'LINE'], [8, '0'], [10, 0], [20, 0], [11, 0], [21, 0.9],
  [0, 'ARC'], [8, '0'], [10, 0], [20, 0], [40, 0.9], [50, 0], [51, 90], [0, 'ENDBLK'],
  [0, 'BLOCK'], [8, '0'], [2, 'DOOR'], [10, 0], [20, 0],
  [0, 'INSERT'], [8, '0'], [2, 'LEAF'], [10, 0], [20, 0],
  [0, 'LINE'], [8, '0'], [10, -0.1], [20, 0], [11, 1.0], [21, 0], [0, 'ENDBLK'],
  [0, 'BLOCK'], [8, '0'], [2, '*D1'], [10, 0], [20, 0],
  [0, 'LINE'], [8, '0'], [10, 0], [20, -2], [11, 6], [21, -2],
  [0, 'MTEXT'], [8, '0'], [10, 3], [20, -1.8], [40, 0.25], [1, '{\\fArial;6000}'], [0, 'ENDBLK'],
  [0, 'ENDSEC'],
  [0, 'SECTION'], [2, 'ENTITIES'],
  [0, 'LWPOLYLINE'], [8, '0'], [90, 4], [70, 1], [10, 0], [20, 0], [10, 6], [20, 0], [10, 6], [20, 4], [10, 0], [20, 4],
  [0, 'INSERT'], [8, 'DOORS'], [2, 'DOOR'], [10, 2], [20, 0],
  [0, 'INSERT'], [8, 'DOORS'], [2, 'DOOR'], [10, 6], [20, 2], [50, 90], [41, -1], [42, 1],
  [0, 'DIMENSION'], [8, 'DOORS'], [2, '*D1'], [70, 32],
  [0, 'TEXT'], [8, 'NOTES'], [10, 1], [20, 3], [40, 0.3], [1, 'Kitchen'],
  [0, 'MTEXT'], [8, 'NOTES'], [10, 3.5], [20, 3], [40, 0.25], [1, 'Store\\Pnorth'],
  [0, 'ELLIPSE'], [8, '0'], [10, 3], [20, 2], [11, 1], [21, 0], [40, 0.5], [41, 0], [42, 6.283185307179586],
  [0, 'SPLINE'], [8, '0'], [70, 8], [71, 2], [40, 0], [40, 0], [40, 0], [40, 1], [40, 1], [40, 1],
  [10, 0], [20, 5], [10, 3], [20, 7], [10, 6], [20, 5],
  [0, 'CIRCLE'], [8, '0'], [10, 5], [20, 3], [40, 0.4],
  [0, 'ENDSEC'],
]);
await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');`);
await sleep(500);
await ev(`window.__a3dImportDXF(${JSON.stringify(FILE)},'v251.dxf');`);
const toast = await ev(`const t=document.getElementById('a3d-toast');return t?t.textContent:'';`);
await sleep(800);
const S = await ev('return window.__a3dSketchWorld();');
const T = await ev(`return window.__a3dObjects().filter(o=>o.t==='text').map(o=>o.name);`);
const texts = await ev(`return window.__a3dObjects().filter(o=>o.t==='text').length;`);

// expected sketches: room outline 1; per door: leaf line, leaf arc, threshold line = 3, twice = 6; dimension line 1;
// ellipse 1; spline 1; circle 1 -> 11. Texts: dimension value, Kitchen, Store north -> 3.
ck(S.length === 11, 'eleven drawn objects (' + S.length + ')');
ck(texts === 3, 'three texts: the dimension value, TEXT and MTEXT (' + texts + ')');
const circ = S.find((s) => s.pts.length === 2 && s.closed && s.bulges);
ck(!!circ, 'the CIRCLE arrives as two arcs, not a polygon');
// the mirrored, turned door: scale (-1, 1), then turn 90 degrees, then move to (6, 2): the leaf's end (0, 0.9) lands at
// (5.1, 2) in DXF, which is (5.1, -2) in the model (north is -z)
const leafs = S.filter((s) => s.pts.length === 2 && !s.closed && !s.bulges && Math.abs(Math.hypot(s.pts[1][0] - s.pts[0][0], s.pts[1][1] - s.pts[0][1]) - 0.9) < 1e-6);
ck(leafs.length === 2, 'both door leaves, each 0.9 m (' + leafs.length + ')');
const turned = leafs.find((s) => s.pts.some((p) => Math.abs(p[0] - 6) < 1e-6 && Math.abs(p[1] + 2) < 1e-6));
ck(!!turned && turned.pts.some((p) => Math.abs(p[0] - 5.1) < 1e-6 && Math.abs(p[1] + 2) < 1e-6), 'the mirrored, turned door is where AutoCAD puts it (' + JSON.stringify(turned && turned.pts) + ')');
ck(/block insert/.test(toast), 'the import notice counts the blocks (' + toast.slice(0, 160) + ')');
await ev(`window.__a3dRunCmd('zoomFit');`); await sleep(600);
await shot('v251-01-imported');
ck(errors.length === 0, 'no console errors (' + errors.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
