/* bim_phase260_attributes_check.mjs -- V260's browser check: ATTDEF typed as a user types it, its dialog filled and
   its point clicked; a rectangle drawn with the mouse; both saved as a block (__a3dBlockSave, the BLOCK dialog's
   own call) and inserted twice (__a3dBlockInsert, the library's own call); each insert asks for its value in a
   dialog; ATTEDIT changes one insert's value from a selected member of it; LIST names the block.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase260_attributes_check.mjs <a folder for the screenshots> */
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
const texts = () => ev(`return window.__a3dTextObjs();`);
const fillDlg = (vals) => ev(`const f=[...document.querySelectorAll('.a3d-dlg [data-a3dav]')];if(!f.length)return false;const d=f[0].closest('.a3d-dlg');
  ${JSON.stringify(vals)}.forEach((v,i)=>{if(f[i])f[i].value=v;});d.querySelector('[data-a3dlg="ok"]').click();return true;`);
await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:4,ty:0,tz:-1,dist:24});
  window.__a3dSnapSet({point:false,grid:true,ortho:false});`);
await sleep(600);
await run('attdef');
ck(true === await ev(`const t=document.querySelector('.a3d-dlg [data-a3dad="tag"]');if(!t)return false;const d=t.closest('.a3d-dlg');t.value='mark';
  d.querySelector('[data-a3dad="prompt"]').value='Door mark';d.querySelector('[data-a3dad="def"]').value='D1';d.querySelector('[data-a3dlg="ok"]').click();return true;`), 'ATTDEF\'s dialog takes a tag, a prompt and a default');
await click([0.5, 0.5]);
let T = await texts();
ck(T.length === 1 && T[0].attdef && T[0].attdef.tag === 'MARK' && T[0].text === 'MARK', 'the definition is placed, drawn as its tag');
await run('rect'); await click([0, 0]); await click([2, 1]);
const ids = await ev('return window.__a3dObjects().map(o=>o.id);');
const blk = await ev(`return window.__a3dBlockSave('DOOR TAG',${JSON.stringify(ids)});`);
ck(!!blk, 'BLOCK saves the definition and the rectangle as "DOOR TAG"');
await ev(`window.__a3dTestSetObjs([]);`);
await ev(`window.__a3dBlockInsert(${JSON.stringify(blk)},5,0);`);
ck(true === await fillDlg(['D7']), 'the insert asks for its attribute in a dialog');
await ev(`window.__a3dBlockInsert(${JSON.stringify(blk)},10,0);`);
ck(true === await fillDlg(['D8']), 'the second insert asks too');
T = await texts();
ck(T.length === 2 && T.map((t) => t.text).sort().join() === 'D7,D8' && T.every((t) => t.attrib && t.attrib.tag === 'MARK' && !t.attdef), 'two attributes, D7 and D8 (' + JSON.stringify(T.map((t) => [t.text, t.attrib])) + ')');
// ATTEDIT from the second insert's rectangle
const rect2 = await ev(`return window.__a3dSketchWorld().find(s=>s.pts.some(p=>Math.abs(p[0]-10)<1.5)).id;`);
await ev(`window.__a3dSelectFor([${JSON.stringify(rect2)}]);`); await run('attedit');
ck(true === await fillDlg(['D9']), 'ATTEDIT from a selected member of the insert');
T = await texts();
ck(T.map((t) => t.text).sort().join() === 'D7,D9', 'only that insert\'s attribute changes (' + T.map((t) => t.text) + ')');
await run('inqlist');
const R = await ev(`const o={};document.querySelectorAll('[data-a3dinq] [data-a3dinqv]').forEach(e=>o[e.getAttribute('data-a3dinqv')]=e.textContent);return o;`);
ck(R.Block === 'DOOR TAG', 'LIST names the block (' + JSON.stringify(R) + ')');
await shot('v260-01-attributes');
const real = errors.filter((e) => !/favicon\.ico/.test(e));
ck(real.length === 0, 'no console errors (' + real.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
