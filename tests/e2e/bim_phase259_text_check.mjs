/* bim_phase259_text_check.mjs -- V259's browser check (D4): MTEXT typed as a user types it, placed with the mouse,
   its dialog filled with two lines, a height and a rotation; then STYLE's dialog changing the font. The text is
   read back (__a3dObjects, __a3dTextStyle) and photographed.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase259_text_check.mjs <a folder for the screenshots> */
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
await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:3,ty:0,tz:-1,dist:16});
  window.__a3dSnapSet({point:false,grid:true,ortho:false});`);
await sleep(600);
await run('text'); await click([1, 0]); await sleep(200);
ck(true === await ev(`const t=document.querySelector('.a3d-dlg textarea[data-a3dp="txt"]');if(!t)return false;const d=t.closest('.a3d-dlg');t.value='LIVING ROOM\\n24 m2';
  d.querySelector('[data-a3dp="h"]').value='0.5';d.querySelector('[data-a3dp="rot"]').value='15';
  d.querySelector('[data-a3dlg="ok"]').click();return true;`), 'MTEXT\'s dialog takes two lines, a height and a rotation');
const T = await ev(`return JSON.parse(JSON.stringify(window.__a3dTextObjs()));`);
ck(T.length === 1 && T[0].text === 'LIVING ROOM\n24 m2' && T[0].height === 0.5 && T[0].rot === 15, 'the text keeps them (' + JSON.stringify(T) + ')');
await shot('v259-01-text');
await run('textstyle');
ck(true === await ev(`const s=document.querySelector('.a3d-dlg [data-a3dts="font"]');if(!s)return false;const d=s.closest('.a3d-dlg');s.value='"Courier New",Courier,monospace';
  d.querySelector('[data-a3dts="height"]').value='0.35';d.querySelector('[data-a3dlg="ok"]').click();return true;`), 'STYLE\'s dialog takes a font and a height');
const st = await ev('return window.__a3dTextStyle();');
ck(st.font.indexOf('Courier') >= 0 && st.height === 0.35, 'the text style is kept (' + JSON.stringify(st) + ')');
await run('text'); await click([1, -3]); await sleep(200);
ck(await ev(`return document.querySelector('.a3d-dlg textarea[data-a3dp="txt"]').closest('.a3d-dlg').querySelector('[data-a3dp="h"]').value;`) === '0.35', 'new text starts at the style\'s height');
await tap('Escape');
await shot('v259-02-style');
const real = errors.filter((e) => !/favicon\.ico/.test(e));
ck(real.length === 0, 'no console errors (' + real.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
