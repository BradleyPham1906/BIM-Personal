/* bim_phase249_object_snaps_check.mjs -- V249's browser check (D1, docs/research/research-cadcraft-gap.md): the
   running object snaps and polar tracking, driven by the page's own mouse and keys through the DevTools protocol.
   A line and a circle are drawn with the mouse, then LINE hovers MIDpoint, CENter, QUAdrant and PERpendicular,
   F10 turns polar tracking on, and OSNAP's dialog opens. __a3dOsnap only reads the hover and sets the modes.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase249_object_snaps_check.mjs <a folder for the screenshots> */
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

const KEYS = { Escape: ['Escape', 27], Enter: ['Enter', 13], F10: ['F10', 121] };
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

await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:5,ty:0,tz:0,dist:30});window.__a3dSnapSet({point:true,grid:false,ortho:false});
  window.__a3dOsnap.set({end:true,mid:true,cen:true,qua:true,int:true,per:true,tan:false,nea:false,node:true,polar:false});`);
await sleep(800);

// the drawn points land where the mouse lands, within a pixel or two, hence the 5 cm tolerances below
// a horizontal line (0,0)-(10,0), and a circle of radius 2 at (5,6), drawn with the mouse
await ev(`window.__a3dRunCmd('poly');`); await click([0, 0]); await click([10, 0]); await tap('Enter'); await tap('Escape'); await sleep(200);
await ev(`window.__a3dRunCmd('circle');`); await click([5, 6]); await click([7, 6]); await tap('Escape'); await sleep(200);
let n = await ev('return window.__a3dTestObjs?window.__a3dTestObjs().length:document.title;');
await shot('v249-01-drawn');

await ev(`window.__a3dRunCmd('line');`);
await move([5.05, 0.06]); let h = await hover();
ck(h && h.kind === 'mid' && Math.abs(h.x - 5) < 0.05 && Math.abs(h.z) < 0.05, 'MIDpoint of the line (' + JSON.stringify(h) + ')');
await shot('v249-02-midpoint');
await move([5.05, 6.05]); h = await hover();
ck(h && h.kind === 'cen' && Math.abs(h.x - 5) < 0.05 && Math.abs(h.z - 6) < 0.05, 'CENter of the circle (' + JSON.stringify(h) + ')');
await move([5.02, 8.04]); h = await hover();
ck(h && h.kind === 'qua' && Math.abs(h.x - 5) < 0.05 && Math.abs(h.z - 8) < 0.05, 'QUAdrant of the circle (' + JSON.stringify(h) + ')');
await click([2, 4]);
await move([2.05, 0.08]); h = await hover();
ck(h && h.kind === 'per' && Math.abs(h.x - 2) < 0.05 && Math.abs(h.z) < 0.05, 'PERpendicular from (2,4) to the line (' + JSON.stringify(h) + ')');
await shot('v249-03-perpendicular');

// polar tracking, by F10 as a user presses it
await tap('F10');
await move([6.1, 8.2]); h = await hover();
ck(h && typeof h.polar === 'number' && Math.abs(h.polar - 45) < 1e-6, 'polar tracking at 45 degrees (' + JSON.stringify(h) + ')');
await shot('v249-04-polar');
await tap('Escape');

ck(await ev('return window.__a3dOsnap.dialog();'), 'the OSNAP settings dialog opens with its snap boxes');
await shot('v249-05-dialog');
ck(errors.length === 0, 'no console errors (' + errors.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
