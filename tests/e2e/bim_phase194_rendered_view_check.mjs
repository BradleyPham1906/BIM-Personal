/* bim_phase194_rendered_view_check.mjs -- V194's own browser check (docs/work-orders/v194/TASKS.md, T-06): the
   rendered view on a few drawn elements, then Save image, a selection, a layer turned off, plan view and RENDER off;
   and T-07's looks (a window glass, a steel column metal) as the picture is built.

   It drives any Chromium through the DevTools protocol with Node's own WebSocket, no dependencies, as
   bim_phase198_rendered_map_check.mjs does. To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9335 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase194_rendered_view_check.mjs <a folder for the screenshots> */
import fs from 'node:fs';
const PORT = +(process.env.CDP_PORT || 9335), APP = (process.env.APP_BASE || 'http://127.0.0.1:8765') + '/canvas_v10.html', OUT = process.argv[2] || '.';
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
  const r = await C.send('Runtime.evaluate', { expression: `(async()=>{${expr}})()`, awaitPromise: true, returnByValue: true });
  if (r.result.exceptionDetails) return { __err: (r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description || r.result.exceptionDetails.text).slice(0, 400) };
  return r.result.result.value;
}
let pass = 0, fail = 0;
function ck(ok, msg) { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + msg); }
async function shot(name) { const r = await C.send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.result.data, 'base64')); }
const W8 = (ms) => `await new Promise(r=>setTimeout(r,${ms || 250}));`;
// until the rendered view has a picture with at least n passes (or the time is up); its state
async function passes(n, ms) {
  return ev(`const t0=Date.now();let s;for(;;){s=window.__a3dRendered();if((s.done>=${n}&&s.state!=='loading')||s.err||Date.now()-t0>${ms || 20000})break;` + W8(200) + `}return s;`);
}
// the rendered canvas's pixels: how many differ from its first pixel (a blank picture is all one colour)
const VARIED = `const c=document.getElementById('a3d-rvcanvas');if(!c)return -1;const o=document.createElement('canvas');o.width=c.width;o.height=c.height;
  const x=o.getContext('2d');x.drawImage(c,0,0);const d=x.getImageData(0,0,o.width,o.height).data;let n=0;
  for(let i=0;i<d.length;i+=4*97)if(Math.abs(d[i]-d[0])+Math.abs(d[i+1]-d[1])+Math.abs(d[i+2]-d[2])>24)n++;return n;`;

await C.send('Page.navigate', { url: APP });
await sleep(5000);
let r = await ev('return window.__acad3dV194||null;');
ck(r && /rendered/.test(r), 'the V194 marker (' + r + ')');

// a few elements: a wall with a window in it, a steel column on a layer of its own, a concrete column
r = await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('3d');window.__a3dSelectFor([]);
  const w=window.__a3dCurvedWall([[0,0],[8,0]],null,0.3,3,'center',false);
  const win=window.__a3dWindowAt(w,[4,0],1.6,1.4,0.9);
  const ly=window.__a3dLayerNew({name:'Steel '+Date.now()});
  window.__a3dSetLayer(ly);const st=window.__a3dColumnAt([2,3],0,0.3,0.3,3);
  const L=window.__a3dLayers();window.__a3dSetLayer(L[0].id);const cc=window.__a3dColumnAt([6,3],0,0.4,0.4,3);
  return {w,win,ly,st,cc};`);
ck(r && r.w && r.win && r.st && r.cc && r.ly, 'drawn: a wall, a window in it, two columns, a layer (' + JSON.stringify(r) + ')');
const ids = r;
// the steel column's material, set as Properties sets it (the library's steel card)
r = await ev(`const c=window.__a3dMaterialCards().find(c=>/steel/i.test(c.name));return c?{name:c.name,ok:window.__a3dSetMaterial('${ids.st}',c.name)}:null;`);
ck(r && r.ok, 'the column takes the library\'s steel (' + JSON.stringify(r) + ')');
r = await ev(`const p=window.__a3dRvMap.plan(false);return p.looks;`);
ck(r && r[ids.win] === 'glass' && r[ids.st] === 'metal' && !r[ids.cc] && !r[ids.w], 'T-07: the window is glass, the steel column metal, the rest matte (' + JSON.stringify(r) + ')');

// on: a picture of the model
await ev(`window.__a3dCamSet({pitch:0.45,yaw:0.8,dist:22});` + W8(300));
r = await ev(`const s=await window.__a3dRendered(true);return s;`);
ck(r && r.on === true && !r.err, 'the rendered view is on (' + JSON.stringify(r && { on: r.on, state: r.state, err: r.err }) + ')');
r = await passes(8);
ck(r && r.done >= 8 && !r.err, 'it draws its passes (' + JSON.stringify(r && { state: r.state, done: r.done, err: r.err, text: r.text }) + ')');
const varied = await ev(VARIED);
ck(varied > 50, 'the picture is not blank (' + varied + ' samples differ)');
await shot('194-rendered');

// Save image takes the rendered picture
r = await ev(`const v=window.__a3dViewportImage();return {engine:v.engine,w:v.w,h:v.h,len:v.url.length};`);
ck(r && r.engine === 'rendered' && r.len > 5000, 'Save image takes the rendered picture (' + JSON.stringify(r) + ')');

// a selection redraws it
let sigs = await ev(`return window.__a3dRvMap.plan(false).items.map(i=>i.sig).join('|');`);
await ev(`window.__a3dSelectFor(['${ids.w}']);` + W8(400));
let sigs2 = await ev(`return window.__a3dRvMap.plan(false).items.map(i=>i.sig).join('|');`);
r = await passes(4);
ck(sigs2 !== sigs && r && !r.err && r.done >= 4, 'a selection changes the picture and it is drawn again (' + (r && r.done) + ' passes)');
await shot('194-selected');
await ev(`window.__a3dSelectFor([]);` + W8(300));

// a layer turned off leaves its objects out
sigs = await ev(`return window.__a3dRvMap.plan(false).items.map(i=>i.sig).join('|');`);
r = await ev(`return window.__a3dLayerSet('${ids.ly}','visible',false);`);
await ev(W8(400));
sigs2 = await ev(`return window.__a3dRvMap.plan(false).items.map(i=>i.sig).join('|');`);
r = await passes(4);
ck(sigs2 !== sigs && r && !r.err, 'the steel layer off: its column leaves the picture (' + (r && r.done) + ' passes)');
await shot('194-layer-off');
await ev(`window.__a3dLayerSet('${ids.ly}','visible',true);` + W8(300));

// plan view
await ev(`window.__a3dFlat(true);window.__a3dCamSet({dist:30});` + W8(500));
r = await passes(4);
ck(r && r.on && !r.err && r.done >= 4, 'in plan view it draws (' + JSON.stringify(r && { done: r.done, err: r.err }) + ')');
ck((await ev(VARIED)) > 20, 'the plan picture is not blank');
await shot('194-plan');
await ev(`window.__a3dFlat(false);` + W8(300));

// RENDER off
r = await ev(`return await window.__a3dRendered(false);`);
ck(r && r.on === false, 'RENDER off (' + JSON.stringify(r && { on: r.on, state: r.state }) + ')');
r = await ev(`const v=window.__a3dViewportImage();return v.engine;`);
ck(r !== 'rendered', 'Save image is back on the shaded view (' + r + ')');

const errs = C.ev.filter((e) => (e.method === 'Runtime.exceptionThrown') || (e.method === 'Runtime.consoleAPICalled' && e.params.type === 'error') ||
  (e.method === 'Runtime.consoleAPICalled' && e.params.type === 'warning' && /\[BIM\] Rendered/.test(JSON.stringify(e.params.args))));
ck(errs.length === 0, 'no console errors, no rendered-view warnings (' + errs.length + ')' + (errs.length ? ': ' + JSON.stringify(errs[0]).slice(0, 400) : ''));
console.log(`\n${pass} passed, ${fail} failed`);
C.ws.close();
process.exit(fail ? 1 : 0);
