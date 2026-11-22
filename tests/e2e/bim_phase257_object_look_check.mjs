/* bim_phase257_object_look_check.mjs -- V257's browser check (D5): a line drawn with the mouse is given its own
   colour, linetype and lineweight in the Properties panel, as a user picks them (the panel's own selects, changed
   and dispatched); the plan draws it so (__a3dLastLook), the DXF export writes it, MATCHPROP copies it, and
   ByLayer clears it.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase257_object_look_check.mjs <a folder for the screenshots> */
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
const sks = () => ev('return window.__a3dSketchWorld();');
const look = (id) => ev(`window.__a3dTestPaint();return window.__a3dLastLook(${JSON.stringify(id)});`);
const pick = (f, v) => ev(`const s=document.querySelector('#a3d-propsbody [data-propf="${f}"]');if(!s)return false;s.value=${JSON.stringify(v)};
  s.dispatchEvent(new Event('change',{bubbles:true}));return true;`);
await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:3,ty:0,tz:0,dist:30});
  window.__a3dSnapSet({point:false,grid:true,ortho:false});`);
await sleep(600);
for (const y of [0, 2]) { await run('poly'); await click([0, y]); await click([5, y]); await tap('Enter'); await tap('Escape'); }
let S = await sks();
const a = S[0].id, b = S[1].id;
const layerLook = await look(a);
await ev(`window.__a3dSelectFor([${JSON.stringify(a)}]);window.__a3dRefreshProps&&window.__a3dRefreshProps();`);
await click([2.5, 0]); await sleep(300);
ck(await pick('objcolor-mode', 'own'), 'Properties offers Color: ByLayer or its own');
ck(await pick('objcolor', '#ff8800'), 'the colour picker is shown for its own colour');
ck(await pick('objlinetype', 'CENTER'), 'Properties offers the linetypes');
ck(await pick('objlineweight', '0.5'), 'Properties offers the lineweights');
let L = await look(a);
ck(L && L.color === '#ff8800' && L.linetype === 'CENTER' && L.dash.length === 4, 'the plan draws it orange, CENTER (' + JSON.stringify(L) + ')');
ck(L.width > layerLook.width, 'and heavier than its layer\'s default (' + L.width + ' > ' + layerLook.width + ')');
await shot('v257-01-own-look');
const dxf = await ev('return window.__a3dBuildDXF().text;');
ck(/\n420\r?\n16746496\r?\n/.test(dxf) && /\n6\r?\nCENTER\r?\n/.test(dxf) && /\n370\r?\n50\r?\n/.test(dxf), 'the DXF export writes its 420, 6 and 370');
// MATCHPROP onto the other line
await ev(`window.__a3dSelectFor([${JSON.stringify(a)}]);`); await run('matchprop'); await click([2.5, 2]); await tap('Escape');
L = await look(b);
ck(L && L.color === '#ff8800' && L.linetype === 'CENTER', 'MATCHPROP copies them to the other line');
// back to ByLayer
await ev(`window.__a3dSelectFor([]);`); await click([2.5, 0]); await sleep(300);
await pick('objcolor-mode', 'bylayer'); await pick('objlinetype', 'ByLayer'); await pick('objlineweight', 'ByLayer');
L = await look(a);
ck(L && L.color === layerLook.color && L.linetype === layerLook.linetype && L.width === layerLook.width, 'ByLayer gives it the layer\'s look again');
const real = errors.filter((e) => !/favicon\.ico/.test(e));
ck(real.length === 0, 'no console errors (' + real.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
