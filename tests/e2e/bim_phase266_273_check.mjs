/* bim_phase266_273_check.mjs -- the browser check of the FreeCAD gaps closed in V266 to V273 and V190's import
   (docs/research/research-freecad-gap.md): each new interface driven as a user drives it, with the mouse, the keys,
   the dialogs and the Properties panel, and read back through the test hooks (hooks-freecad.js and the older ones).
     V266 an edge picked with the mouse and filleted; a solid turned by ROTATE still a solid; THICKNESS, DRAFTANGLE,
          SOLIDPATTERN, SWEEP
     V267 DCRADIUS on a circle      V268 MATERIALS: a new card, assigned, exported as .FCMat
     V269 SPREADSHEET: a cell bound to a solid's elevation      V190 a LAS cloud imported, drawn, ground to surface
     V271 an STL soup repaired and made a solid      V272 VIEWBASE      V273 JOINT (a hinge) and BOM

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase266_273_check.mjs <a folder for the screenshots> */
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
// fill the open dialog's fields (by their data attribute) and press one of its buttons
const fill = (attr, vals, button) => ev(`const d=[...document.querySelectorAll('.a3d-dlg')].pop();if(!d)return false;const V=${JSON.stringify(vals)};
  for(const e of d.querySelectorAll('[${attr}]')){const k=e.getAttribute('${attr}');if(V[k]===undefined)continue;
    if(e.type==='checkbox')e.checked=!!V[k];else e.value=V[k];e.dispatchEvent(new Event('change',{bubbles:true}));}
  ${button ? `const b=d.querySelector(${JSON.stringify(button)});if(!b)return 'no button';b.click();` : ''}return true;`);
const press = (sel) => ev(`const d=[...document.querySelectorAll('.a3d-dlg')].pop();const b=d&&d.querySelector(${JSON.stringify(sel)});if(!b)return false;b.click();return true;`);
const solids = () => ev('return window.__a3dOcct.solids();');
const snap = (id) => ev(`return window.__a3dObjSnapshot(${JSON.stringify(id)});`);
async function waitFor(fn, ms) { for (let t = 0; t < ms; t += 250) { const v = await fn(); if (v) return v; await sleep(250); } return null; }
async function clickScreen(xy) { const o = await cv(); const x = o[0] + xy[0], y = o[1] + xy[1];
  await C.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }); await sleep(100);
  await C.send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await C.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 }); await sleep(150); }
const near = (a, b, e) => Math.abs(a - b) <= e;
// a rectangle drawn with the mouse and extruded; returns the new solid
async function boxAt(x0, z0, x1, z1, h) {
  const before = (await solids()).map((v) => v.id);
  await ev(`window.__a3dRunCmd('2d');window.__a3dSelectFor([]);window.__a3dCamSet({tx:${(x0 + x1) / 2},ty:0,tz:${(z0 + z1) / 2},dist:18});`); await sleep(300);
  await run('rect'); await click([x0, z0]); await click([x1, z1]);
  const all = await ev('return window.__a3dSketchWorld();');
  const at = (s, x, z) => s.pts.some((p) => Math.abs(p[0] - x) < 1e-6 && Math.abs(p[1] - z) < 1e-6);
  const S = all.filter((s) => at(s, x0, z0) && at(s, x1, z1));
  if (!S.length) { console.log('no rectangle at', x0, z0, JSON.stringify(all.slice(-2).map((s) => s.pts)), JSON.stringify(await ev('return window.__a3dSketchState?window.__a3dSketchState():null;'))); await shot('debug-rect'); }
  await ev(`window.__a3dSelectFor([${JSON.stringify(S[S.length - 1].id)}]);`);
  await run('occtextrude'); await fill('data-a3doc', { h: String(h) }, '[data-a3dlg="ok"]');
  return waitFor(async () => (await solids()).find((v) => before.indexOf(v.id) < 0), 60000);
}
const bounds = (o) => { const b = [1e9, 1e9, 1e9, -1e9, -1e9, -1e9]; const q = o.pos || [0, 0, 0];
  for (const v of o.mesh.v) for (let k = 0; k < 3; k++) { b[k] = Math.min(b[k], v[k] + q[k]); b[k + 3] = Math.max(b[k + 3], v[k] + q[k]); } return b; };
const DL = path.resolve(OUT, 'downloads'); fs.mkdirSync(DL, { recursive: true });
for (const f of fs.readdirSync(DL)) fs.unlinkSync(path.join(DL, f));
await C.send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: DL });
await C.send('DOM.enable');
async function pickFile(file) {
  const doc = await C.send('DOM.getDocument', { depth: -1 });
  const q = await C.send('DOM.querySelector', { nodeId: doc.result.root.nodeId, selector: '#a3d-filein' });
  await C.send('DOM.setFileInputFiles', { nodeId: q.result.nodeId, files: [file] });
}
await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:12,ty:0,tz:-3,dist:42});
  window.__a3dSnapSet({point:false,grid:true,ortho:false});`);
await sleep(600);

// ---- V266: an edge picked with the mouse ----
const A = await boxAt(0, 0, 2, 2, 3);
ck(A && near(A.volume, 12, 1e-6), 'a 2 x 2 x 3 box extruded (' + (A && A.volume) + ')');
await ev(`window.__a3dSelectFor([${JSON.stringify(A.id)}]);window.__a3dRunAct('v:iso');`); await sleep(300);
await ev(`window.__a3dRunCmd('zoomFit');`); await sleep(500);
await ev(`window.__a3dSelectFor([${JSON.stringify(A.id)}]);`);
await run('filletedge');
ck(true === await fill('data-a3doc', { r: '0.2', set: 'pick' }, '[data-a3dlg="ok"]'), 'FILLETEDGE offers picking the edges');
let EP = await waitFor(() => ev('return window.__a3dEdgePick();'), 20000);
ck(EP && EP.edges.length === 12, 'the box\'s 12 edges are drawn to pick from (' + (EP && EP.edges.length) + ')');
// the upright edge at the plan's (2, 2), the corner nearest the eye in the iso view
const k = EP.edges.findIndex((e) => near(e.a[0], 2, 1e-6) && near(e.a[2], 2, 1e-6) && near(e.b[0], 2, 1e-6) && near(e.b[2], 2, 1e-6));
await clickScreen(EP.edges[k].screen);
EP = await ev('return window.__a3dEdgePick();');
ck(EP && EP.picked.length === 1 && EP.picked[0] === k, 'a click on the upright edge picks it, and only it (' + JSON.stringify(EP && EP.picked) + ', wanted ' + k + ')');
await shot('v266-01-edge-picked');
await tap('Enter'); await sleep(1200);
let V = await solids(), a = V.find((v) => v.id === A.id);
ck(a && near(a.volume, 12 - 0.04 * (1 - Math.PI / 4) * 3, 1e-6), 'Enter fillets that one edge (' + (a && a.volume) + ')');
// ROTATE (a mesh tool) and the solid stays a solid
await ev(`window.__a3dRunCmd('2d');window.__a3dSelectFor([${JSON.stringify(A.id)}]);window.__a3dCamSet({tx:1,ty:0,tz:1,dist:18});`); await sleep(300);
await run('rotate'); await click([1, 1]);
ck(true === await fill('data-a3dp', { ang: '90' }, '[data-a3dlg="ok"]'), 'ROTATE asks for the angle');
await sleep(400);
await ev(`window.__a3dSelectFor([${JSON.stringify(A.id)}]);`); await run('filletedge');
await fill('data-a3doc', { r: '0.1', set: 'top' }, '[data-a3dlg="ok"]'); await sleep(1200);
a = (await solids()).find((v) => v.id === A.id);
ck(a && a.volume < 12 - 0.04 * (1 - Math.PI / 4) * 3 - 1e-3 && a.volume > 11, 'turned by ROTATE, it is still a solid: its top edges fillet (' + (a && a.volume) + ')');
// THICKNESS, DRAFTANGLE, SOLIDPATTERN
const B = await boxAt(4, 0, 6, 2, 2);
await ev(`window.__a3dSelectFor([${JSON.stringify(B.id)}]);`); await run('occtthickness');
await fill('data-a3doc', { t: '0.1', open: 'both' }, '[data-a3dlg="ok"]'); await sleep(1000);
let b = (await solids()).find((v) => v.id === B.id);
ck(b && near(b.volume, 8 - 1.8 * 1.8 * 2, 1e-6), 'THICKNESS open top and bottom: a tube (' + (b && b.volume) + ')');
const Cc = await boxAt(8, 0, 10, 1, 3);
await ev(`window.__a3dSelectFor([${JSON.stringify(Cc.id)}]);`); await run('occtdraft');
await fill('data-a3doc', { deg: '5' }, '[data-a3dlg="ok"]'); await sleep(1000);
const kd = 2 * 3 * Math.tan(5 * Math.PI / 180), want = 3 / 6 * (2 + 4 * (2 - kd / 2) * (1 - kd / 2) + (2 - kd) * (1 - kd));
let c2 = (await solids()).find((v) => v.id === Cc.id);
ck(c2 && near(c2.volume, want, 1e-6), 'DRAFTANGLE 5 degrees: the sides lean in (' + (c2 && c2.volume) + ' = ' + want + ')');
const D = await boxAt(12, 0, 13, 1, 1);
await ev(`window.__a3dSelectFor([${JSON.stringify(D.id)}]);`); await run('occtpattern');
await fill('data-a3doc', { type: 'linear', count: '3', dx: '2', dz: '0', dy: '0' }, '[data-a3dlg="ok"]'); await sleep(1000);
let d2 = (await solids()).find((v) => v.id === D.id);
ck(d2 && near(d2.volume, 3, 1e-6), 'SOLIDPATTERN: three in a row, joined (' + (d2 && d2.volume) + ')');
// SWEEP: a section and an open path
await ev(`window.__a3dRunCmd('2d');window.__a3dSelectFor([]);window.__a3dCamSet({tx:20,ty:0,tz:5,dist:18});`); await sleep(300);
await run('rect'); await click([18, 3]); await click([19, 4]); await ev(`window.__a3dSelectFor([]);`);
await run('poly'); await click([18, 6]); await click([23, 6]); await tap('Enter'); await sleep(200);
let SK = (await ev('return window.__a3dSketchWorld();')).filter((s) => s.pts.some((p) => p[0] >= 17.9 && p[1] >= 2.9));
const n0 = (await solids()).length;
await ev(`window.__a3dSelectFor(${JSON.stringify(SK.map((s) => s.id))});`); await run('occtsweep');
V = await waitFor(async () => { const s = await solids(); return s.length > n0 ? s : null; }, 10000);
const sw = V && V[V.length - 1];
ck(sw && near(sw.volume, 1 * 5, 1e-6), 'SWEEP: a 1 m square section along the 5 m path (' + (sw && sw.volume) + '; ' + JSON.stringify(SK.map((x) => [x.closed, x.pts.length])) + ' ' +
  (await ev(`const t=document.getElementById('a3d-toast');return t?t.textContent:'';`)) + ')');
await ev(`window.__a3dSelectFor([]);window.__a3dRunAct('v:iso');`); await sleep(300); await ev(`window.__a3dRunCmd('zoomFit');`); await sleep(700);
await shot('v266-02-solid-tools');

// ---- V267: a radius that drives a circle ----
await ev(`window.__a3dRunCmd('2d');window.__a3dSelectFor([]);window.__a3dCamSet({tx:0,ty:0,tz:8,dist:14});`); await sleep(300);
await run('circle'); await click([0, 8]); await click([1, 8]);
SK = (await ev('return window.__a3dSketchWorld();')).filter((s) => s.pts.length === 2 && s.pts.some((p) => p[1] > 7));
const circ = SK[SK.length - 1];
await ev(`window.__a3dSelectFor([${JSON.stringify(circ.id)}]);`); await run('dcradius');
await click(circ.pts[0]); await click(circ.pts[1]);
ck(true === await fill('data-a3dp', { v: '1.5' }, '[data-a3dlg="ok"]'), 'DCRADIUS: the arc\'s two ends clicked, the radius asked for');
await sleep(300);
const c3 = await snap(circ.id);
const ch = Math.hypot(c3.pts[1][0] - c3.pts[0][0], c3.pts[1][1] - c3.pts[0][1]), bb = Math.abs(c3.bulges[0]);
ck(c3.constraints && c3.constraints.length === 1 && near(ch * (1 + bb * bb) / (4 * bb), 1.5, 1e-3), 'the circle\'s radius is now 1.5 (' + (ch * (1 + bb * bb) / (4 * bb)).toFixed(4) + ')');

// ---- V268: a material card ----
await ev(`window.__a3dSelectFor([${JSON.stringify(B.id)}]);`); await run('materials');
await press('[data-a3dmbact="new"]'); await sleep(200);
await fill('data-a3dmb', { name: 'Oak test', density: '650', conductivity: '0.13', youngsModulus: '11' }, '[data-a3dmbact="save"]'); await sleep(200);
await press('[data-a3dmbact="assign"]'); await sleep(200);
const cards = await ev('return window.__a3dMatCards();');
const oak = cards.find((c) => c.name === 'Oak test');
ck(oak && oak.density === 650 && oak.youngsModulus === '11 GPa' && oak.conductivity === 0.13, 'MATERIALS: a new card saved (' + JSON.stringify(oak) + ')');
ck((await snap(B.id)).materialName === 'Oak test', 'Assign gives the selected solid the card');
await press('[data-a3dmbact="export"]');
let got = await waitFor(async () => fs.readdirSync(DL).find((f) => /\.FCMat$/.test(f)), 10000);
const fc = got ? fs.readFileSync(path.join(DL, got), 'utf8') : '';
ck(/Name: "Oak test"/.test(fc) && /Density: "650 kg\/m\^3"/.test(fc) && /LinearElastic:/.test(fc), 'Export writes FreeCAD\'s .FCMat (' + got + ')');
await press('[data-a3dlg="cancel"]');

// ---- V269: a spreadsheet cell drives the pattern's elevation ----
await ev(`window.__a3dSelectFor([${JSON.stringify(D.id)}]);`); await run('spreadsheet');
await fill('data-a3dsc', { A1: '2' }); await sleep(150);
await fill('data-a3dsc', { B1: '=A1*3' }); await sleep(150);
await ev(`document.querySelector('.a3d-dlg [data-a3dsc="B1"]').focus();`);
await fill('data-a3dsf', { prop: 'y' }, '[data-a3dsb="bind"]'); await sleep(300);
let dpos = (await snap(D.id)).pos;
ck(dpos && near(dpos[1], 6, 1e-9), 'SPREADSHEET: B1 = A1 * 3 bound to the elevation sets it to 6 (' + JSON.stringify(dpos) + ')');
await fill('data-a3dsc', { A1: '1' }); await sleep(300);
dpos = (await snap(D.id)).pos;
ck(dpos && near(dpos[1], 3, 1e-9), 'changing A1 to 1 moves it to 3');
await shot('v269-spreadsheet');
await press('[data-a3dlg="cancel"]');

// ---- V190: a LAS cloud ----
function lasFile(file) {
  const pts = [];
  for (let i = 0; i < 20; i++) for (let j = 0; j < 20; j++) pts.push([500000 + i, 4400000 + j, 100 + i * 0.1, 2]);
  for (let i = 0; i < 6; i++) for (let j = 0; j < 6; j++) for (let h = 0; h < 5; h++) pts.push([500005 + i, 4400005 + j, 101 + h, 6]);
  const hs = 227, rl = 26, buf = Buffer.alloc(hs + rl * pts.length);
  buf.write('LASF', 0, 'latin1'); buf.writeUInt8(1, 24); buf.writeUInt8(2, 25); buf.writeUInt16LE(hs, 94); buf.writeUInt32LE(hs, 96);
  buf.writeUInt8(2, 104); buf.writeUInt16LE(rl, 105); buf.writeUInt32LE(pts.length, 107);
  const sc = 0.01, off = [500000, 4400000, 0];
  for (let k = 0; k < 3; k++) { buf.writeDoubleLE(sc, 131 + 8 * k); buf.writeDoubleLE(off[k], 155 + 8 * k);
    buf.writeDoubleLE(Math.max(...pts.map((p) => p[k])), 179 + 16 * k); buf.writeDoubleLE(Math.min(...pts.map((p) => p[k])), 187 + 16 * k); }
  pts.forEach((p, i) => { const at = hs + i * rl;
    for (let k = 0; k < 3; k++) buf.writeInt32LE(Math.round((p[k] - off[k]) / sc), at + 4 * k);
    buf.writeUInt8(p[3], at + 15); buf.writeUInt16LE(p[3] === 2 ? 30000 : 60000, at + 20); buf.writeUInt16LE(20000, at + 22); buf.writeUInt16LE(10000, at + 24); });
  fs.writeFileSync(file, buf);
  return pts.length;
}
const lasPath = path.join(DL, 'test-cloud.las'), nPts = lasFile(lasPath);
await ev(`window.__a3dSelectFor([]);`); await pickFile(lasPath);
let PC = await waitFor(async () => { const s = await ev('return window.__a3dPcState();'); return s.clouds.length ? s : null; }, 10000);
const cloud = PC && PC.clouds[0];
ck(cloud && cloud.n === nPts && cloud.loaded && JSON.stringify(cloud.classes) === '[2,6]', 'a LAS file imports as a cloud: ' + nPts + ' points, ground and building classes (' + JSON.stringify(cloud) + ')');
ck(cloud && JSON.stringify(cloud.origin) === '[500009,4400009,100]', 'its whole-metre origin kept (' + JSON.stringify(cloud && cloud.origin) + ')');
await ev(`window.__a3dRunAct('v:iso');`); await sleep(300); await ev(`window.__a3dSelectFor([${JSON.stringify(cloud.id)}]);window.__a3dRunCmd('zoomSel')||window.__a3dRunCmd('zoomFit');`); await sleep(800);
PC = await ev('return window.__a3dPcState();');
ck(PC.drewGl, 'drawn as points with WebGL');
await shot('v190-01-cloud');
// Properties: colour by class, then ground to surface
await ev(`window.__a3dSelectFor([${JSON.stringify(cloud.id)}]);`);
await waitFor(() => ev(`return !!document.querySelector('[data-propf="pcmode"]');`), 5000); await sleep(700);
const modeOk = await ev(`const s=document.querySelector('[data-propf="pcmode"]');if(!s)return false;s.value='class';s.dispatchEvent(new Event('change',{bubbles:true}));return true;`);
await sleep(300);
ck(modeOk && (await ev('return window.__a3dPcState();')).clouds[0].mode === 'class', 'Properties colours it by class');
await ev(`const b=document.querySelector('[data-propf="pcground"]');b&&b.click();`); await sleep(300);
await fill('data-a3dpg', { cell: '2' }, '[data-a3dpgact="preview"]'); await sleep(300);
PC = await ev('return window.__a3dPcState();');
ck(PC.preview === 121, 'Ground to surface previews the lowest ground point of each 2 m cell: 11 by 11 over the 20 m grid (' + PC.preview + ')');
await shot('v190-02-ground-preview');
await press('[data-a3dpgact="create"]'); await sleep(500);
const terr = (await ev('return window.__a3dObjects();')).filter((o) => o.t === 'terrain');
ck(terr.length === 1, 'Create makes a terrain surface from them');

// ---- V271: an STL soup repaired and made a solid ----
const stl = ['solid soup'];
const P8 = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]];
[[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [3, 0, 4, 7]].forEach((q, f) => {
  for (const t of [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]) { const tt = f === 2 ? t.slice().reverse() : t;
    stl.push(' facet normal 0 0 0', '  outer loop', ...tt.map((i) => '   vertex ' + P8[i].map((c) => c + 40).join(' ')), '  endloop', ' endfacet'); }
});
stl.push('endsolid soup');
const stlPath = path.join(DL, 'soup.stl'); fs.writeFileSync(stlPath, stl.join('\n') + '\n');
const before = (await ev('return window.__a3dObjects();')).map((o) => o.id);
await pickFile(stlPath);
const soup = await waitFor(async () => (await ev('return window.__a3dObjects();')).find((o) => before.indexOf(o.id) < 0), 10000);
await ev(`window.__a3dSelectFor([${JSON.stringify(soup.id)}]);`); await run('meshrepair'); await sleep(300);
const sm = await snap(soup.id);
ck(sm && sm.mesh.v.length === 8 && sm.mesh.f.length === 12, 'MESHREPAIR welds the soup into a closed cube (' + (sm && sm.mesh.v.length) + ' points, ' + (sm && sm.mesh.f.length) + ' faces)');
await ev(`window.__a3dSelectFor([${JSON.stringify(soup.id)}]);`); await run('meshtosolid'); await sleep(1200);
const ss = (await solids()).find((v) => v.id === soup.id);
ck(ss && near(ss.volume, 1, 1e-6), 'MESHTOSOLID makes it a true solid of 1 m3 (' + (ss && ss.volume) + ')');

// ---- V272: drawing views ----
const Eb = await boxAt(0, 12, 2, 13, 3);
await ev(`window.__a3dSelectFor([${JSON.stringify(Eb.id)}]);`); await run('viewbase');
await fill('data-a3dvb', { front: true, top: true, right: true, iso: true, hidden: true, gap: '1' }, '[data-a3dlg="ok"]'); await sleep(1500);
const objs = await ev('return window.__a3dObjects();');
const views = ['Front', 'Top', 'Right', 'Isometric'].map((n) => objs.filter((o) => o.t === 'sketch' && o.name.indexOf(n + ' view') === 0).length);
ck(views.every((n) => n > 0), 'VIEWBASE draws front, top, right and isometric views as lines (' + views.join(', ') + ')');
await ev(`window.__a3dSelectFor([]);window.__a3dRunCmd('2d');window.__a3dCamSet({tx:9,ty:0,tz:8,dist:11});`); await sleep(700); await shot('v272-views');

// ---- V273: a hinge, and the bill of materials ----
const F = await boxAt(30, 0, 31, 1, 1), G = await boxAt(31, 0, 33, 1, 2);
await ev(`window.__a3dRunCmd('2d');window.__a3dSelectFor([${JSON.stringify(F.id)},${JSON.stringify(G.id)}]);window.__a3dCamSet({tx:31.5,ty:0,tz:0.5,dist:14});`); await sleep(300); await run('joint');
await fill('data-a3djt', { type: 'revolute', rmin: '-90', rmax: '120' }, '[data-a3dlg="ok"]'); await sleep(200);
await click([31, 0]); await sleep(200);
ck(!!(await snap(G.id)).joint, 'JOINT: the hinge clicked, the door joined to its post');
await ev(`window.__a3dSelectFor([]);`); await click([32.5, 0.5]);   /* the door clicked, as a user selects it */
await waitFor(() => ev(`return !!document.querySelector('[data-propf="jointval"]');`), 5000); await sleep(300);
const jOk = await ev(`const i=document.querySelector('[data-propf="jointval"]');if(!i)return false;i.value='90';i.dispatchEvent(new Event('change',{bubbles:true}));return true;`);
await sleep(500);
const gb = bounds(await snap(G.id));
ck(jOk && near(gb[0], 31, 1e-6) && near(gb[3], 32, 1e-6) && near(gb[2], -2, 1e-6) && near(gb[5], 0, 1e-6), 'Properties turns the door 90 degrees about its hinge, to the north (' + gb.map((v) => +v.toFixed(3)) + ')');
const g2 = (await solids()).find((v) => v.id === G.id);
ck(g2 && near(g2.volume, 4, 1e-6), 'the turned door is still a solid');
await run('bom'); await sleep(300);
const rows = await ev(`return [...document.querySelectorAll('.a3d-dlg table tr')].slice(1).map((r)=>[...r.cells].map((c)=>c.textContent));`);
ck(rows.length === 1 && rows[0][2] === '2', 'BOM counts the assembly\'s two extrusions in one row (' + JSON.stringify(rows) + ')');
await press('[data-a3dlg="cancel"]');
await ev(`window.__a3dRunAct('v:iso');window.__a3dSelectFor([]);`); await sleep(300); await ev(`window.__a3dRunCmd('zoomFit');`); await sleep(800);
await shot('v273-assembly');

const real = errors.filter((e) => !/favicon\.ico/.test(e));
ck(real.length === 0, 'no console errors (' + real.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
