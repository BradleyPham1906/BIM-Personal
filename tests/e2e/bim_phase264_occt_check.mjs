/* bim_phase264_occt_check.mjs -- V264's browser check (docs/research/research-occt-library.md): the solid tools on
   OpenCASCADE in a real page, loading the pinned runtime on first use. Rectangles drawn with the mouse; EXTRUDE,
   FILLETEDGE, SHELL, SOLIDUNION, REVOLVE (its axis clicked), LOFT and EXPORTSTEP typed as a user types them, their
   dialogs filled; the exported STEP picked again through Import. Read back through __a3dOcct (volumes of the solids'
   B-reps, measured by OpenCASCADE) and photographed.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase264_occt_check.mjs <a folder for the screenshots> */
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











import path from 'node:path';
const run = (c) => ev(`return window.__a3dRunCmd(${JSON.stringify(c)});`);
const dlg = (vals) => ev(`const f=[...document.querySelectorAll('.a3d-dlg [data-a3doc]')];if(!f.length)return false;const d=f[0].closest('.a3d-dlg');
  for(const e of f){const k=e.getAttribute('data-a3doc');if(${JSON.stringify(vals)}[k]!==undefined)e.value=${JSON.stringify(vals)}[k];}d.querySelector('[data-a3dlg="ok"]').click();return true;`);
const solids = () => ev('return window.__a3dOcct.solids();');
async function waitFor(fn, ms) { for (let t = 0; t < ms; t += 250) { const v = await fn(); if (v) return v; await sleep(250); } return null; }
const DL = path.resolve(OUT, 'downloads'); fs.mkdirSync(DL, { recursive: true });
for (const f of fs.readdirSync(DL)) fs.unlinkSync(path.join(DL, f));
await C.send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: DL });
await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:6,ty:0,tz:-1,dist:30});
  window.__a3dSnapSet({point:false,grid:true,ortho:false});`);
await sleep(600);
await run('rect'); await click([0, 0]); await click([2, 2]);
let S = await ev('return window.__a3dSketchWorld();');
await ev(`window.__a3dSelectFor([${JSON.stringify(S[0].id)}]);`);
await run('occtextrude');
ck(true === await dlg({ h: '3' }), 'EXTRUDE asks for the height');
let V = await waitFor(async () => { const s = await solids(); return s && s.length ? s : null; }, 60000);
ck(V && V.length === 1 && Math.abs(V[0].volume - 12) < 1e-6, 'EXTRUDE: a 2 x 2 x 3 solid, 12 m3, OpenCASCADE loaded on first use (' + JSON.stringify(V) + ')');
const box = V[0].id;
await ev(`window.__a3dSelectFor([${JSON.stringify(box)}]);`); await run('filletedge');
ck(true === await dlg({ r: '0.2', set: 'vertical' }), 'FILLETEDGE asks for a radius and the edges');
await sleep(800); V = await solids();
const want = 12 - 4 * (0.04 - Math.PI * 0.01) * 3;
ck(Math.abs(V[0].volume - want) < 1e-5, 'FILLETEDGE: the four vertical edges rounded (' + V[0].volume.toFixed(6) + ' = ' + want.toFixed(6) + ')');
await ev(`window.__a3dSelectFor([${JSON.stringify(box)}]);`); await run('occtshell');
ck(true === await dlg({ t: '0.1' }), 'SHELL asks for the wall thickness');
await sleep(800); V = await solids();
ck(V[0].volume < want - 5 && V[0].volume > 1, 'SHELL: hollowed, the top open (' + V[0].volume.toFixed(3) + ' m3)');
await ev(`window.__a3dRunCmd('3d');`); await sleep(500); await shot('v264-01-filleted-shelled');
await ev(`window.__a3dRunCmd('2d');window.__a3dSelectFor([]);`); await sleep(300);
// two overlapping boxes, joined (nothing selected: a sketch drawn with a solid selected goes on its top face)
await run('rect'); await click([4, 0]); await click([6, 2]); await ev(`window.__a3dSelectFor([]);`); await run('rect'); await click([5, 1]); await click([7, 3]);
S = (await ev('return window.__a3dSketchWorld();')).filter((s) => s.pts.some((p) => p[0] >= 4));
await ev(`window.__a3dSelectFor(${JSON.stringify(S.map((s) => s.id))});`); await run('occtextrude'); await dlg({ h: '1' });
await sleep(800); V = await solids();
const pair = V.filter((v) => v.id !== box).map((v) => v.id);
await ev(`window.__a3dSelectFor(${JSON.stringify(pair)});`); await run('solidunion'); await sleep(800);
V = await solids();
const u = V.find((v) => v.id === pair[0]);
ck(V.length === 2 && u && Math.abs(u.volume - 7) < 1e-6, 'SOLIDUNION: two 2 x 2 x 1 boxes overlapping by 1 x 1 make 7 m3 (' + (u && u.volume) + ')');
// REVOLVE a 1 x 1 square about an axis 1 m from it
await ev(`window.__a3dSelectFor([]);`); await run('rect'); await click([10, 0]); await click([11, 1]);
S = (await ev('return window.__a3dSketchWorld();')).filter((s) => s.pts.some((p) => p[0] >= 10));
await ev(`window.__a3dSelectFor([${JSON.stringify(S[0].id)}]);`); await run('occtrevolve'); await click([9, 0]); await click([9, 5]);
ck(true === await dlg({ deg: '360' }), 'REVOLVE asks for the angle after the axis is clicked');
await sleep(800); V = await solids();
const ring = V.find((v) => Math.abs(v.volume - Math.PI * 3) < 1e-4);
ck(!!ring, 'REVOLVE: a ring of 3 pi m3 (' + V.map((v) => v.volume.toFixed(4)) + ')');
// LOFT between a square on the plan and one 3 m up
await ev(`window.__a3dSelectFor([]);`); await run('rect'); await click([14, 0]); await click([16, 2]); await ev(`window.__a3dSelectFor([]);`); await run('rect'); await click([14.5, 0.5]); await click([15.5, 1.5]);
S = (await ev('return window.__a3dSketchWorld();')).filter((s) => s.pts.some((p) => p[0] >= 14));
await ev(`window.__a3dSketchSetProps(${JSON.stringify(S[1].id)},{y:3});window.__a3dSelectFor(${JSON.stringify(S.map((s) => s.id))});`);
await run('occtloft'); await sleep(1500); V = await solids();
const lo = V.find((v) => Math.abs(v.volume - 3 * (4 + 2 + 1) / 3) < 0.01);   // a smooth loft is a B-spline: 7 to about 0.02 %
ck(!!lo, 'LOFT: a frustum of 7 m3 between a 2 m and a 1 m square 3 m apart (' + V.map((v) => v.volume.toFixed(4)) + ')');
await ev(`window.__a3dRunCmd('3d');window.__a3dRunCmd('zoomFit');`); await sleep(700); await shot('v264-02-solids');
// EXPORTSTEP all, then Import it back
await ev(`window.__a3dSelectFor([]);`); await run('exportstep');
let got = await waitFor(async () => fs.readdirSync(DL).find((f) => /\.step$/.test(f)), 20000);
ck(!!got, 'EXPORTSTEP downloads a .step (' + got + ')');
if (got) {
  const txt = fs.readFileSync(path.join(DL, got), 'latin1');
  ck(/^ISO-10303-21;/.test(txt), 'it is a STEP file (ISO-10303-21)');
  const n0 = (await solids()).length;
  await C.send('DOM.enable');
  const doc = await C.send('DOM.getDocument', { depth: -1 });
  const q = await C.send('DOM.querySelector', { nodeId: doc.result.root.nodeId, selector: '#a3d-filein' });
  await C.send('DOM.setFileInputFiles', { nodeId: q.result.nodeId, files: [path.join(DL, got)] });
  V = await waitFor(async () => { const s = await solids(); return s.length > n0 ? s : null; }, 20000);
  ck(V && V.length === n0 + 1, 'the STEP picked through Import comes back as a solid');
}
// the solids in 3D, as the ribbon's 3D view shows them
await ev(`window.__a3dSelectFor([]);window.__a3dRunAct('v:iso');`); await sleep(400);
await ev(`window.__a3dRunCmd('zoomFit');`); await sleep(900); await shot('v264-03-solids-3d');
const real = errors.filter((e) => !/favicon\.ico/.test(e));
ck(real.length === 0, 'no console errors (' + real.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
