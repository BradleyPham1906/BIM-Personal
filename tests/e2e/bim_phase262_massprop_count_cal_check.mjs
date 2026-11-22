/* bim_phase262_massprop_count_cal_check.mjs -- V262's browser check: MASSPROP of a rectangle drawn with the mouse,
   COUNT after two inserts of a block, and QUICKCALC's dialog, each typed as a user types it and read back from
   its read-out.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase262_massprop_count_cal_check.mjs <a folder for the screenshots> */
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
const readout = () => ev(`const d=document.querySelector('[data-a3dinq]');if(!d)return null;const o={};d.querySelectorAll('[data-a3dinqv]').forEach(e=>o[e.getAttribute('data-a3dinqv')]=e.textContent);return o;`);
await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:4,ty:0,tz:-1,dist:24});
  window.__a3dSnapSet({point:false,grid:true,ortho:false});`);
await sleep(600);
await run('rect'); await click([0, 0]); await click([4, 2]);
const id = (await ev('return window.__a3dSketchWorld();'))[0].id;
await ev(`window.__a3dSelectFor([${JSON.stringify(id)}]);`); await run('massprop');
let R = await readout();
ck(R && /^8(\.0+)? m/.test(R.Area) && /^X 2(\.0+)?\s+Y -?1(\.0+)?$/.test(R.Centroid) && /^10\.66/.test(R['Iyy (about centroid)']), 'MASSPROP: area 8, centroid, Iyy 10.667 (' + JSON.stringify(R) + ')');
await shot('v262-01-massprop');
await ev(`const b=document.querySelector('[data-a3dinq] [data-a3dlg]');if(b)b.click();`);
const blk = await ev(`return window.__a3dBlockSave('BOX',[${JSON.stringify(id)}]);`);
await ev(`window.__a3dBlockInsert(${JSON.stringify(blk)},10,0);window.__a3dBlockInsert(${JSON.stringify(blk)},16,0);`);
await run('countblocks'); R = await readout();
ck(R && R.BOX === '2' && R['Total inserts'] === '2', 'COUNT: two inserts of BOX (' + JSON.stringify(R) + ')');
await ev(`const b=document.querySelector('[data-a3dinq] [data-a3dlg]');if(b)b.click();`);
await run('cal');
const res = await ev(`const x=document.querySelector('.a3d-dlg [data-a3dcal="x"]');if(!x)return null;const d=x.closest('.a3d-dlg');x.value='(3.2+4.8)*2^2/sqrt(16)';
  d.querySelector('[data-a3dlg="ok"]').click();return d.querySelector('[data-a3dcal="r"]').textContent;`);
ck(res === '8', 'QUICKCALC: (3.2+4.8)*2^2/sqrt(16) = 8 (' + res + ')');
const real = errors.filter((e) => !/favicon\.ico/.test(e));
ck(real.length === 0, 'no console errors (' + real.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
