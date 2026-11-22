/* bim_phase250_modify_check.mjs -- V250's browser check (D2, docs/research/research-cadcraft-gap.md): MOVE, COPY,
   STRETCH, EXPLODE, JOIN, OVERKILL, DRAWORDER and MATCHPROP, typed as a user types them on the command line and
   driven by the page's own mouse and keys. Points are clicked on snapped corners, so the results are exact.
   __a3dSketchWorld only reads the sketches; __a3dSelectFor sets the selection a user would click.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase250_modify_check.mjs <a folder for the screenshots> */
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


const sks = () => ev('return window.__a3dSketchWorld();');
const run = (c) => ev(`return window.__a3dRunCmd(${JSON.stringify(c)});`);
const sel = (ids) => ev(`window.__a3dSelectFor(${JSON.stringify(ids)});`);
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:8,ty:0,tz:0,dist:40});
  window.__a3dSnapSet({point:true,grid:true,ortho:false});`);
await sleep(800);

// a 4 x 3 rectangle drawn as four LINE-style segments with a polyline each, so JOIN has work to do
async function seg(a, b) { await run('poly'); await click(a); await click(b); await tap('Enter'); await tap('Escape'); await sleep(150); }
await seg([0, 0], [4, 0]); await seg([4, 0], [4, 3]); await seg([4, 3], [0, 3]); await seg([0, 3], [0, 0]);
let S = await sks();
ck(S.length === 4, 'four segments drawn (' + S.length + ')');

// JOIN: the four into one closed polyline
await sel(S.map((s) => s.id)); await run('join'); S = await sks();
ck(S.length === 1 && S[0].closed && S[0].pts.length === 4, 'JOIN makes one closed polyline (' + JSON.stringify(S) + ')');
const rect = S[0].id;

// MOVE by base point and second point, both on snapped grid nodes
await sel([rect]); await run('moveTool'); await click([0, 0]); await click([6, 0]); S = await sks();
ck(S.length === 1 && same(S[0].pts.slice().sort(), [[6, 0], [10, 0], [10, 3], [6, 3]].sort()), 'MOVE by 6 m (' + JSON.stringify(S[0].pts) + ')');
await shot('v250-01-moved');

// COPY twice, then Esc
await sel([rect]); await run('copyTool'); await click([6, 0]); await click([6, 5]); await click([6, 10]); await tap('Escape'); S = await sks();
ck(S.length === 3, 'COPY repeats: two copies (' + S.length + ')');

// STRETCH: a window around the right edge of the first rectangle, pulled 2 m right
await ev(`window.__a3dSelectFor([]);`);
await run('stretch'); await click([9, -1]); await click([11, 4]); await click([10, 0]); await click([12, 0]);
S = await sks(); const st = S.find((s) => s.id === rect);
ck(st && same(st.pts.slice().sort(), [[6, 0], [12, 0], [12, 3], [6, 3]].sort()), 'STRETCH widens the rectangle to 6 m (' + JSON.stringify(st && st.pts) + ')');
await shot('v250-02-stretched');

// EXPLODE the stretched one into four lines
await sel([rect]); await run('explode'); S = await sks();
ck(S.length === 6 && S.filter((s) => !s.closed && s.pts.length === 2).length === 4, 'EXPLODE gives four lines (' + S.length + ' sketches)');

// OVERKILL: a copy laid exactly on top of one rectangle is deleted
const keep = S.filter((s) => s.closed)[0];
await sel([keep.id]); await run('copyTool'); await click([0, 0]); await click([0, 0]); await tap('Escape');
let n0 = (await sks()).length;
await ev(`window.__a3dSelectFor([]);`); await run('overkill'); S = await sks();
ck(n0 === 7 && S.length === 6, 'OVERKILL deletes the duplicate (' + n0 + ' to ' + S.length + ')');

// DRAWORDER: send a line to the back
const ln = S.filter((s) => !s.closed)[2].id;
await sel([ln]); await run('draworder');
ck(await ev(`const b=[...document.querySelectorAll('[data-a3dlg="back"]')];if(!b.length)return false;b[0].click();return true;`), 'the DRAWORDER dialog offers Send to back');
S = await sks(); ck(S[0].id === ln, 'the line is drawn first, under the rest');

// MATCHPROP: the colour of one line onto a rectangle
await ev(`const o=window.__a3dSketchWorld()[0];window.__a3dSketchSetProps(o.id,{col:'#ff3300'});`);
const src = S[0], dst = S.filter((s) => s.closed)[0];
await ev(`window.__a3dSelectFor([${JSON.stringify(src.id)}]);`);
await run('matchprop');
await click([dst.pts[0][0] + 0.0, dst.pts[0][1] + 1.5]);
await tap('Escape');
S = await sks(); const d2 = S.find((s) => s.id === dst.id), s2 = S.find((s) => s.id === src.id);
ck(d2 && s2 && d2.col === '#ff3300' && d2.col === s2.col && d2.layer === s2.layer, 'MATCHPROP copies colour and layer (' + JSON.stringify([s2 && s2.col, d2 && d2.col]) + ')');
await shot('v250-03-done');

ck(errors.length === 0, 'no console errors (' + errors.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
