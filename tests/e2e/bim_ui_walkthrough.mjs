/* bim_ui_walkthrough.mjs -- step 5 of the owner's five after V194 (2026-11-13): screenshots of the interface's main
   states on a desktop, a tablet and a phone, for the interface review (docs/research/research-ui-pass.md). It checks
   nothing; it records what the page shows and the console's errors.

     python -m http.server 8765 --bind 127.0.0.1                        (from the repository's root)
     msedge --headless=new --remote-debugging-port=9336 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_ui_walkthrough.mjs <a folder for the screenshots> */
import fs from 'node:fs';
const PORT = +(process.env.CDP_PORT || 9336), APP = (process.env.APP_BASE || 'http://127.0.0.1:8765') + '/canvas_v10.html', OUT = process.argv[2] || '.';
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
await C.send('Runtime.enable'); await C.send('Page.enable');
async function ev(expr) {
  const r = await C.send('Runtime.evaluate', { expression: `(async()=>{${expr}})()`, awaitPromise: true, returnByValue: true });
  if (r.result.exceptionDetails) return { __err: (r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description || r.result.exceptionDetails.text).slice(0, 300) };
  return r.result.result.value;
}
async function shot(name) {
  const r = await C.send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.result.data, 'base64'));
  console.log('shot ' + name);
}
const W8 = (ms) => `await new Promise(r=>setTimeout(r,${ms || 400}));`;
async function size(w, h, mobile) {
  await C.send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: !!mobile });
  if (mobile) await C.send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
}
// a button by its visible text or title, clicked
const click = (txt) => ev(`const L=[...document.querySelectorAll('button,[role=button],.a3d-tab,a,[data-act],[data-cmd]')].filter(b=>b.offsetParent!==null);
  const b=L.find(b=>(b.title||'').trim()===${JSON.stringify(txt)}||(b.textContent||'').trim()===${JSON.stringify(txt)})||L.find(b=>(b.title||'').indexOf(${JSON.stringify(txt)})===0);
  if(!b)return 'none';b.click();` + W8(500) + `return (b.title||b.textContent||'').trim().slice(0,40);`);
const model = `window.__a3dTestSetObjs([]);
  window.__a3dWall([[0,0],[12,0]],0.3,3,'center',false);window.__a3dWall([[12,0],[12,8]],0.3,3,'center',false);
  window.__a3dWall([[12,8],[0,8]],0.3,3,'center',false);window.__a3dWall([[0,8],[0,0]],0.3,3,'center',false);
  window.__a3dColumnAt([6,4],0,0.4,0.4,3);window.__a3dRunCmd('3d');window.__a3dRunCmd('zoomextents');window.__a3dSelectFor([]);`;

for (const [dev, w, h, mob] of [['desk', 1500, 950, false], ['tab', 1024, 768, true], ['phone', 390, 844, true]]) {
  await size(w, h, mob);
  await C.send('Page.navigate', { url: APP });
  await sleep(5000);
  await shot(dev + '-01-start');
  await ev('window.__a3dEnter();' + W8(800));
  await shot(dev + '-02-empty');
  await ev(model + W8(800));
  await shot(dev + '-03-model');
  const ids = await ev('return (window.__a3dObjSnapshot?window.__a3dObjSnapshot():[]).map(o=>o.id).slice(0,1);');
  if (Array.isArray(ids) && ids.length) { await ev(`window.__a3dSelectFor(${JSON.stringify(ids)});` + W8(600)); await shot(dev + '-04-selected'); await ev('window.__a3dSelectFor([]);'); }
  await ev(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'k',ctrlKey:true,bubbles:true}));` + W8(600));
  await shot(dev + '-05-palette');
  await ev(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));` + W8(300));
  console.log('layers: ' + await click('Layers'));
  await shot(dev + '-06-layers');
  await ev(`window.__a3dSetPropTab&&window.__a3dSetPropTab('project');` + W8(400));
  await shot(dev + '-07-project');
  await ev(`window.__a3dRunCmd('2d');` + W8(800));
  await shot(dev + '-08-plan');
  await ev(`window.__a3dRunCmd('3d');window.__a3dAwEnter&&window.__a3dAwEnter();` + W8(1200));
  await shot(dev + '-09-analyze');
  await ev(`window.__a3dAwLeave&&window.__a3dAwLeave();` + W8(600));
  await ev(`const s=window.__a3dAddSheet('A101','Plans','A3-L');window.__a3dOpenSheetView(s);` + W8(1200));
  await shot(dev + '-10-sheet');
  await ev(`window.__a3dRunCmd('3d');` + W8(600));
  await ev(`await window.__a3dRendered(true);` + W8(3500));
  await shot(dev + '-11-rendered');
  await ev(`await window.__a3dRendered(false);` + W8(400));
}
const errs = C.ev.filter((e) => e.method === 'Runtime.exceptionThrown' || (e.method === 'Runtime.consoleAPICalled' && e.params.type === 'error'));
console.log('console errors: ' + errs.length);
errs.slice(0, 5).forEach((e) => console.log('  ' + JSON.stringify(e.params).slice(0, 300)));
C.ws.close();
