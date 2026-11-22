/* bim_phase256_layer_commands_check.mjs -- V256's browser check: LAYISO, LAYUNISO, LAYOFF, LAYFRZ, LAYERP,
   LAYON, LAYTHW and LAYMCUR as a user types them, on a line drawn with the mouse on each of three layers; each step
   is read back from the layers (__a3dLayers) and from the sketches the plan draws (__a3dSketchWorld).

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase256_layer_commands_check.mjs <a folder for the screenshots> */
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





const run = (c) => ev(`return window.__a3dRunCmd(${JSON.stringify(c)});`);
const layers = () => ev('return window.__a3dLayers();');
const byName = async (n) => (await layers()).find((l) => l.id === lid[n]);
const sks = () => ev('return window.__a3dSketchWorld();');
await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:3,ty:0,tz:0,dist:30});
  window.__a3dSnapSet({point:false,grid:true,ortho:false});`);
await sleep(600);
const lid = {}, RUN = Date.now().toString(36);
for (const [n, y] of [['A', 0], ['B', 2], ['C', 4]]) {
  /* a name of this run's own: a layer of that name may be left in the browser's storage by an earlier run */
  lid[n] = await ev(`return window.__a3dLayerNew({name:${JSON.stringify(n + '-' + RUN)},current:true});`);
  await run('poly'); await click([0, y]); await click([5, y]); await tap('Enter'); await tap('Escape');
}
let S = await sks();
ck(S.length === 3 && S.map((s) => s.layer).sort().join() === [lid.A, lid.B, lid.C].sort().join(), 'a line on each of A, B, C');
const onLayer = (n) => S.find((s) => s.layer === lid[n]).id;

await ev(`window.__a3dSelectFor([${JSON.stringify(onLayer('B'))}]);`); await run('layiso');
let A = await byName('A'), B = await byName('B'), Cc = await byName('C');
ck(A.visible === false && B.visible !== false && Cc.visible === false, 'LAYISO on a line of B: A and C off, B on');
ck((await ev('return window.__a3dActiveLayer();')) === lid.B, 'LAYISO makes B current, since C (current) went off');
await shot('v256-01-layiso');
await run('layuniso');
A = await byName('A'); Cc = await byName('C');
ck(A.visible !== false && Cc.visible !== false, 'LAYUNISO: A and C back on');

S = await sks();
await ev(`window.__a3dSelectFor([${JSON.stringify(S.find((s) => s.layer === lid.A).id)}]);`); await run('layoff');
ck((await byName('A')).visible === false, 'LAYOFF on a line of A turns A off');
await run('layerp');
ck((await byName('A')).visible !== false, 'LAYERP puts A back on');

await ev(`window.__a3dSelectFor([${JSON.stringify(S.find((s) => s.layer === lid.C).id)}]);`); await run('laymcur');
ck((await ev('return window.__a3dActiveLayer();')) === lid.C, 'LAYMCUR makes C current');
await ev(`window.__a3dSelectFor([${JSON.stringify(S.find((s) => s.layer === lid.A).id)}]);`); await run('layfrz');
ck((await byName('A')).frozen === true, 'LAYFRZ freezes A');
await ev(`window.__a3dSelectFor([${JSON.stringify(S.find((s) => s.layer === lid.C).id)}]);`); await run('layfrz');
ck(!(await byName('C')).frozen, 'LAYFRZ refuses the current layer, as AutoCAD does');
await run('laythw');
ck(!(await byName('A')).frozen, 'LAYTHW thaws A');
await ev(`window.__a3dLayerSet(${JSON.stringify(lid.B)},'visible',false);`); await run('layerp');
ck((await byName('B')).visible !== false, 'LAYERP also steps back over a change made in the Layer Properties Manager');
const real = errors.filter((e) => !/favicon\.ico/.test(e));
ck(real.length === 0, 'no console errors (' + real.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
