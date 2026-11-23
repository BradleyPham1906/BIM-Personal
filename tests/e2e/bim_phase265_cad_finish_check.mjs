/* bim_phase265_cad_finish_check.mjs -- V265's browser check, the end of the CADCraft list: DONUT, WIPEOUT (read
   back from the canvas's pixels), a polyline's global width set in Properties, CIRCLE TTR on two picked lines,
   BEDIT and BCLOSE redefining two inserts, XATTACH through the page's own file chooser and XREF's Detach, and a
   hatch with a hole exported as a DXF HATCH and read back. Typed as a user types them, picked with the mouse.

   To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase265_cad_finish_check.mjs <a folder for the screenshots> */
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
const sks = () => ev('return window.__a3dSketchWorld();');
const hatches = () => ev('return window.__a3dHatches();');
const dlgSet = (sel, vals) => ev(`const f=[...document.querySelectorAll('.a3d-dlg [${sel}]')];if(!f.length)return false;const d=f[0].closest('.a3d-dlg');
  for(const e of f){const k=e.getAttribute('${sel}');if(${JSON.stringify(vals)}[k]!==undefined)e.value=${JSON.stringify(vals)}[k];}d.querySelector('[data-a3dlg="ok"]').click();return true;`);
const pixel = (p) => ev(`const s=window.__a3dToScreen(${JSON.stringify(p)},0);const c=document.getElementById('a3d-canvas');
  const k=c.width/c.getBoundingClientRect().width;const d=c.getContext('2d').getImageData(Math.round(s[0]*k),Math.round(s[1]*k),1,1).data;return [d[0],d[1],d[2]];`);
await C.send('Page.navigate', { url: APP });
await sleep(5000);
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('2d');window.__a3dCamSet&&window.__a3dCamSet({tx:8,ty:0,tz:-3,dist:30});
  window.__a3dSnapSet({point:false,grid:true,ortho:false});`);
await sleep(600);
// DONUT
await run('donut');
ck(true === await dlgSet('data-a3ddn', { i: '1', o: '2' }), 'DONUT asks for the inside and outside diameters');
await click([2, 0]); await tap('Escape');
let Hs = await hatches();
ck(Hs.length === 1 && Hs[0].holes && Hs[0].holes.length === 1, 'DONUT: a solid hatch with one hole');
// WIPEOUT over a line
await ev(`window.__a3dSelectFor([]);`);
await run('poly'); await click([0, -3]); await click([8, -3]); await tap('Enter'); await tap('Escape');
const lineId = (await sks()).slice(-1)[0].id;
const before = await pixel([3, -3]);
await ev(`window.__a3dSelectFor([]);`);
await run('wipeout'); await click([2, -2]); await click([4, -2]); await click([4, -4]); await click([2, -4]); await tap('Enter');
Hs = await hatches();
ck(Hs.some((h) => h.wipeout), 'WIPEOUT: a wipeout made from four corners');
await ev(`window.__a3dSelectFor([]);window.__a3dTestPaint();`); await sleep(200);
const under = await pixel([3, -3]), outside = await pixel([6, -3]), bg = await pixel([3, -3.6]);
ck(JSON.stringify(under) === JSON.stringify(bg) && JSON.stringify(outside) !== JSON.stringify(bg), 'the line is hidden under the wipeout and shows beside it (' + JSON.stringify({ before, under, outside, bg }) + ')');
await shot('v265-01-donut-wipeout');
// polyline width in Properties
await ev(`window.__a3dSelectFor([]);`); await click([6.5, -3]); await sleep(300);
ck(true === await ev(`const s=document.querySelector('#a3d-propsbody [data-propf="plwidth"]');if(!s)return false;s.value='0.4';s.dispatchEvent(new Event('change',{bubbles:true}));return true;`), 'Properties offers Global width');
const lw = await ev(`window.__a3dTestPaint();return window.__a3dLastLook(${JSON.stringify(lineId)});`);
ck(lw && lw.plWidth === 0.4 && lw.width > 8, 'the polyline is drawn 0.4 m wide (' + (lw && lw.width) + ' px)');
// CIRCLE TTR between two lines meeting at (10, 0)
await ev(`window.__a3dSelectFor([]);`);
await run('poly'); await click([10, 0]); await click([18, 0]); await tap('Enter'); await tap('Escape');
await ev(`window.__a3dSelectFor([]);`);
await run('poly'); await click([10, 0]); await click([10, -6]); await tap('Enter'); await tap('Escape');
await ev(`window.__a3dSelectFor([]);`);
await run('circlettr'); await click([14, 0]); await click([10, -3]);
ck(true === await dlgSet('data-a3dttr', { r: '1' }), 'CIRCLE TTR asks for the radius after two lines');
const circ = (await sks()).slice(-1)[0];
const cx = (circ.pts[0][0] + circ.pts[1][0]) / 2, cz = (circ.pts[0][1] + circ.pts[1][1]) / 2;
ck(Math.abs(cx - 11) < 1e-6 && Math.abs(cz + 1) < 1e-6, 'CIRCLE TTR: centre (11, -1), tangent to both (' + cx + ', ' + cz + ')');
await shot('v265-02-width-ttr');
// BEDIT and BCLOSE: a block inserted twice, redefined (the view moved over them: x 22 to 31 is under the right panel otherwise)
await ev(`window.__a3dSelectFor([]);window.__a3dCamSet({tx:26,ty:0,tz:-1,dist:20});`); await sleep(300);
await run('rect'); await click([22, 0]); await click([23, -1]);
const rid = (await sks()).slice(-1)[0].id;
const blk = await ev(`return window.__a3dBlockSave('PANEL',[${JSON.stringify(rid)}]);`);
await ev(`window.__a3dBlockInsert(${JSON.stringify(blk)},26,0);window.__a3dBlockInsert(${JSON.stringify(blk)},30,0);`);
let B = await ev('return window.__a3dBlockRefs();');
ck(B.length === 2, 'two inserts of PANEL');
await run('bedit');
ck(true === await ev(`const s=document.querySelector('.a3d-dlg [data-a3dbe="id"]');if(!s)return false;s.value=${JSON.stringify(blk)};s.closest('.a3d-dlg').querySelector('[data-a3dlg="ok"]').click();return true;`), 'BEDIT asks which block');
await ev(`window.__a3dSelectFor([]);`);
await run('poly'); await click([22, 0]); await click([23, -1]); await tap('Enter'); await tap('Escape');
await run('bclose');
ck(true === await ev(`const x=document.querySelector('.a3d-dlg [data-a3dlg="discard"]');if(!x)return false;x.closest('.a3d-dlg').querySelector('[data-a3dlg="ok"]').click();return true;`), 'BCLOSE offers Save and Discard');
B = await ev('return window.__a3dBlockRefs();');
const ins = new Set(B.map((b) => b.blockRef.ins));
ck(B.length === 4 && ins.size === 2, 'BCLOSE redefined both inserts: each now has the rectangle and the new line (' + B.length + ' objects, ' + ins.size + ' inserts)');
await shot('v265-03-bedit');
// XATTACH through the page's own file chooser
const DIR = path.resolve(OUT, 'xref'); fs.mkdirSync(DIR, { recursive: true });
const XF = path.join(DIR, 'site.dxf');
fs.writeFileSync(XF, '0\nSECTION\n2\nENTITIES\n0\nLINE\n8\nSITE\n10\n0\n20\n10\n11\n20\n21\n10\n0\nLINE\n8\nSITE\n10\n20\n20\n10\n11\n20\n21\n20\n0\nENDSEC\n0\nEOF\n');
await C.send('Page.setInterceptFileChooserDialog', { enabled: true });
const chooser = new Promise((res) => C.ws.addEventListener('message', function h(m) { const d = JSON.parse(m.data); if (d.method === 'Page.fileChooserOpened') { C.ws.removeEventListener('message', h); res(d.params); } }));
await run('xattach');
const fc = await Promise.race([chooser, sleep(5000).then(() => null)]);
ck(!!fc, 'XATTACH opens a file chooser');
if (fc) await C.send('DOM.setFileInputFiles', { backendNodeId: fc.backendNodeId, files: [XF] });
await sleep(1500);
let X = await ev('return window.__a3dXrefs();');
ck(X.length === 1 && X[0].name === 'site.dxf' && X[0].count === 2, 'the drawing is attached as a reference: 2 objects (' + JSON.stringify(X) + ')');
await run('xref');
ck(true === await ev(`const b=document.querySelector('.a3d-dlg [data-a3dxr="detach"]');if(!b)return false;b.click();return true;`), 'XREF lists it with Detach');
X = await ev('return window.__a3dXrefs();');
ck(X.length === 0, 'Detach takes it out');
// the donut exported as a DXF HATCH with its hole, and read back
const dxf = await ev('return window.__a3dBuildDXF().text;');
ck(/\nHATCH\r?\n/.test(dxf) && /\n91\r?\n2\r?\n/.test(dxf), 'the DXF export writes a HATCH with two boundary paths');
await ev(`window.__a3dTestSetObjs([]);window.__a3dImportDXF(${JSON.stringify(dxf)},'roundtrip.dxf');`);
Hs = await hatches();
ck(Hs.length === 1 && Hs[0].holes && Hs[0].holes.length === 1 && Hs[0].pattern === 'solid', 'read back: the donut, its hole kept (' + Hs.length + ' hatch)');
const real = errors.filter((e) => !/favicon\.ico/.test(e));
ck(real.length === 0, 'no console errors (' + real.slice(0, 3).join(' | ') + ')');
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
