/* bim_phase258_dimensions_check.mjs -- V258's browser check (D4): a linear dimension drawn with the mouse, then
   DIMBASELINE, DIMCONTINUE and DIMORDINATE typed as a user types them and picked on snapped grid points, and
   DIMSTYLE's dialog changing the precision, the arrows and the text height; the dimensions are read back
   (__a3dDims) and photographed.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase258_dimensions_check.mjs <a folder for the screenshots> */
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
const dims = () => ev(`return window.__a3dDimsAll();`);
await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:5,ty:0,tz:-2,dist:28});
  window.__a3dSnapSet({point:false,grid:true,ortho:false});`);
await sleep(600);
await run('bimDims'); await click([0, 0]); await click([2, 0]); await click([0, -1]);
let D = await dims();
ck(D.length === 1 && Math.abs(D[0].length - 2) < 1e-6, 'a linear dimension of 2 m');
await run('dimbase'); await click([5, 0]); await click([7, 0]); await tap('Enter');
D = await dims();
ck(D.length === 3 && Math.abs(D[1].length - 5) < 1e-6 && Math.abs(D[2].length - 7) < 1e-6, 'DIMBASELINE: 5 m and 7 m from the first point (' + D.map((d) => d.length).join(', ') + ')');
ck(Math.abs(Math.abs(D[2].d1[1]) - Math.abs(D[1].d1[1]) - 0.6) < 1e-6, 'each baseline one 0.6 m spacing further out');
await ev(`window.__a3dSelectFor([${JSON.stringify(D[0].id)}]);`);
await run('dimcont'); await click([4, 0]); await click([9, 0]); await tap('Enter');
D = await dims();
const cont = D.slice(3);
ck(cont.length === 2 && Math.abs(cont[0].length - 2) < 1e-6 && Math.abs(cont[1].length - 5) < 1e-6 && Math.abs(cont[0].d1[1] - D[0].d1[1]) < 1e-9,
  'DIMCONTINUE: 2 m then 5 m on the first dimension\'s line (' + cont.map((d) => d.length).join(', ') + ')');
await run('dimord'); await click([3, 2]); await click([6, 2]); await tap('Escape');
D = await dims();
const ord = D.find((d) => d.dimKind === 'ordinate');
ck(ord && ord.axis === 'y' && Math.abs(ord.value - 2) < 1e-6, 'DIMORDINATE: Y 2 (' + JSON.stringify(ord && { axis: ord.axis, value: ord.value }) + ')');
await shot('v258-01-dims');
// DIMSTYLE: three decimals, arrows, 0.25 m text
await run('dimstyle');
ck(true === await ev(`const p=document.querySelector('.a3d-dlg [data-a3dds="precision"]');if(!p)return false;const d=p.closest('.a3d-dlg');p.value='3';
  d.querySelector('[data-a3dds="arrow"]').value='arrow';d.querySelector('[data-a3dds="textHeight"]').value='0.25';
  d.querySelector('[data-a3dlg="ok"]').click();return true;`), 'the DIMSTYLE dialog takes precision, arrows and text height');
const stl = await ev('return window.__a3dDimStyle();');
ck(stl.precision === 3 && stl.arrow === 'arrow' && stl.textHeight === 0.25, 'the style is kept (' + JSON.stringify(stl) + ')');
const dxf = await ev('return window.__a3dBuildDXF().text;');
ck(/\n1\r?\n2\.000 m\r?\n/.test(dxf), 'the DXF export writes the dimensions in the style\'s precision');
await shot('v258-02-styled');
const real = errors.filter((e) => !/favicon\.ico/.test(e));
ck(real.length === 0, 'no console errors (' + real.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
