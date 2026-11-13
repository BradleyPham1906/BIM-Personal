/* bim_phase198_rendered_map_check.mjs -- V198's browser check: the map in the rendered view, on the ground and
   draped on a terrain (docs/research/research-rendered-map.md).

   It drives Edge (or any Chromium) through the DevTools protocol with Node's own WebSocket, no dependencies, as
   bim_phase174_boards_edge_check.mjs does. To run it:
     python -m http.server 8765 --bind 127.0.0.1                        (from the repository's root)
     msedge --headless=new --remote-debugging-port=9335 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase198_rendered_map_check.mjs <a folder for the screenshots>
   The tiles are served by this script (the DevTools protocol's Fetch domain), with CORS: every tile red with a blue
   square in its north-west corner and a green bar along its east side, so a map turned, mirrored or misplaced shows.
   Each case is drawn twice from the same camera, by the shaded view (WebGL) and by the rendered view, and the two
   pictures are compared pixel by pixel by colour class (red, blue, green): the light differs, the classes must not. */
import fs from 'node:fs';
import zlib from 'node:zlib';
const PORT = +(process.env.CDP_PORT || 9335), APP = (process.env.APP_BASE || 'http://127.0.0.1:8765') + '/canvas_v10.html', OUT = process.argv[2] || '.';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ---- a tile, as a PNG written here
function crc32(b) { let c, t = crc32.t; if (!t) { t = crc32.t = []; for (let n = 0; n < 256; n++) { c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } } c = 0xffffffff; for (const x of b) c = t[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; }
function chunk(type, data) { const l = Buffer.alloc(4); l.writeUInt32BE(data.length); const td = Buffer.concat([Buffer.from(type), data]); const c = Buffer.alloc(4); c.writeUInt32BE(crc32(td)); return Buffer.concat([l, td, c]); }
function tilePng() {
  const W = 256, raw = Buffer.alloc((W * 3 + 1) * W);
  for (let y = 0; y < W; y++) {
    raw[y * (W * 3 + 1)] = 0;
    for (let x = 0; x < W; x++) {
      let c = [208, 32, 32];
      if (x < 96 && y < 96) c = [32, 64, 208];
      else if (x >= 216) c = [32, 176, 48];
      const o = y * (W * 3 + 1) + 1 + x * 3; raw[o] = c[0]; raw[o + 1] = c[1]; raw[o + 2] = c[2];
    }
  }
  const ih = Buffer.alloc(13); ih.writeUInt32BE(W, 0); ih.writeUInt32BE(W, 4); ih[8] = 8; ih[9] = 2;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ih), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
}
const TILE = tilePng().toString('base64');

async function target() {
  for (let i = 0; i < 40; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' }); return await r.json(); } catch (e) { await sleep(250); }
  }
  throw new Error('no browser on port ' + PORT);
}
async function connect(t) {
  const ws = new WebSocket(t.webSocketDebuggerUrl); let id = 0; const wait = {}, ev = [], on = {};
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && wait[d.id]) { wait[d.id](d); delete wait[d.id]; } else { ev.push(d); if (on[d.method]) on[d.method](d.params); } };
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; wait[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
  return { send, ev, on, ws };
}
const C = await connect(await target());
await C.send('Runtime.enable'); await C.send('Log.enable'); await C.send('Page.enable');
await C.send('Emulation.setDeviceMetricsOverride', { width: 1500, height: 950, deviceScaleFactor: 1, mobile: false });
let tiles = 0;
C.on['Fetch.requestPaused'] = (p) => {
  tiles++;
  C.send('Fetch.fulfillRequest', { requestId: p.requestId, responseCode: 200, body: TILE,
    responseHeaders: [{ name: 'Content-Type', value: 'image/png' }, { name: 'Access-Control-Allow-Origin', value: '*' }] });
};
await C.send('Fetch.enable', { patterns: [{ urlPattern: 'https://tiles.example.org/*' }] });
async function ev(expr) {
  const r = await C.send('Runtime.evaluate', { expression: `(async()=>{${expr}})()`, awaitPromise: true, returnByValue: true });
  if (r.result.exceptionDetails) return { __err: (r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description || r.result.exceptionDetails.text).slice(0, 400) };
  return r.result.result.value;
}
let pass = 0, fail = 0;
function ck(ok, msg) { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + msg); }
async function shot() { const r = await C.send('Page.captureScreenshot', { format: 'png' }); return r.result.data; }
// a screenshot's pixels in the 3D view by colour class (r, b, g, or . for none), every 4th pixel each way
async function classes(b64, name) {
  fs.writeFileSync(`${OUT}/${name}.png`, Buffer.from(b64, 'base64'));
  return ev(`const im=new Image();im.src='data:image/png;base64,${b64}';await im.decode();
    const q=document.getElementById('a3d-canvas').getBoundingClientRect(),c=document.createElement('canvas');c.width=im.width;c.height=im.height;
    const x=c.getContext('2d');x.drawImage(im,0,0);const d=x.getImageData(0,0,c.width,c.height).data;let s='';
    for(let y=Math.ceil(q.top)+40;y<q.bottom-40;y+=4)for(let X=Math.ceil(q.left)+40;X<q.right-40;X+=4){const o=(y*c.width+X)*4,r=d[o],g=d[o+1],b=d[o+2];
      s+=(r>g+50&&r>b+50)?'r':(b>r+50&&b>g+20)?'b':(g>r+40&&g>b+30)?'g':'.';}
    return s;`);
}
function compare(a, b) {
  let both = 0, agree = 0, mapA = 0, mapB = 0, blueA = 0;
  for (let i = 0; i < Math.min(a.length, b.length); i++) {
    if (a[i] !== '.') mapA++; if (b[i] !== '.') mapB++; if (a[i] === 'b') blueA++;
    if (a[i] !== '.' && b[i] !== '.') { both++; if (a[i] === b[i]) agree++; }
  }
  return { n: a.length, mapA, mapB, blueA, both, agree: both ? agree / both : 0 };
}
const W8 = (ms) => `await new Promise(r=>setTimeout(r,${ms || 250}));`;
async function settle() { for (let i = 0; i < 12; i++) { await ev('window.__a3dRunCmd&&0;' + W8(250)); } }
// the same camera drawn by the shaded view and by the rendered view
async function both(name) {
  await ev(`await window.__a3dRendered(false);window.__a3dGraphics('webgl');` + W8(600));
  await settle();
  const a = await classes(await shot(), name + '-shaded');
  const r = await ev(`const s=await window.__a3dRendered(true);` + W8(2500) + `return {s:s,drawn:window.__a3dMapDrawn&&window.__a3dMapDrawn()};`);
  await settle();
  const b = await classes(await shot(), name + '-rendered');
  return { cmp: compare(a, b), r };
}

await C.send('Page.navigate', { url: APP });
await sleep(5000);
let r = await ev('return window.__acad3dV198||null;');
ck(r && /rvmap/.test(r), 'the V198 marker (' + r + ')');
await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('3d');window.__a3dSelectFor([]);
  window.__a3dSetPropTab('project');window.__a3dRefreshProps();
  var a=document.querySelector('#a3d-propsbody [data-propmodel="sunlat"]');a.value='39.95';a.dispatchEvent(new Event('change',{bubbles:true}));
  var b=document.querySelector('#a3d-propsbody [data-propmodel="sunlon"]');b.value='-75.16';b.dispatchEvent(new Event('change',{bubbles:true}));
  window.__a3dMapSet('url','https://tiles.example.org/{z}/{x}/{y}.png');window.__a3dMapSet('style','custom');` + W8(500));

// 1. on the ground, in plan and in 3D
await ev(`window.__a3dColumnAt([0,0],0,2,2,8);window.__a3dFlat(true);window.__a3dCamSet({dist:200});` + W8(500));
let B = await both('plan');
ck(B.r && B.r.s && B.r.s.on !== false, 'the rendered view is on (' + JSON.stringify(B.r && B.r.s).slice(0, 160) + ')');
ck(B.r && B.r.drawn && B.r.drawn.path === 'rendered' && B.r.drawn.drawn > 0, 'the rendered view asked for the tiles and drew them (' + JSON.stringify(B.r && B.r.drawn && { path: B.r.drawn.path, drawn: B.r.drawn.drawn, tiles: B.r.drawn.tiles && B.r.drawn.tiles.length }) + ')');
ck(B.cmp.mapB > B.cmp.n * 0.5, 'in plan, the map fills the rendered view (' + B.cmp.mapB + ' of ' + B.cmp.n + ' samples)');
ck(B.cmp.blueA > 0 && B.cmp.agree > 0.9, 'in plan, the tiles lie where the shaded view puts them, the same way round (' + (B.cmp.agree * 100).toFixed(1) + '% of ' + B.cmp.both + ' agree)');
await ev(`window.__a3dFlat(false);window.__a3dCamSet({pitch:0.6,yaw:0.7,dist:120});` + W8(500));
B = await both('3d-ground');
ck(B.cmp.mapB > B.cmp.n * 0.3, 'in 3D, the map on the ground (' + B.cmp.mapB + ' of ' + B.cmp.n + ')');
ck(B.cmp.agree > 0.85, 'in 3D, the tiles where the shaded view puts them (' + (B.cmp.agree * 100).toFixed(1) + '% of ' + B.cmp.both + ' agree)');

// 2. turned by true north
await ev(`window.__a3dSetPropTab('project');window.__a3dRefreshProps();var t=document.querySelector('#a3d-propsbody [data-propmodel="truenorth"]');if(t){t.value='30';t.dispatchEvent(new Event('change',{bubbles:true}));}` + W8(500));
B = await both('3d-north30');
ck(B.cmp.agree > 0.85, 'turned 30 degrees by true north, the same (' + (B.cmp.agree * 100).toFixed(1) + '%)');

// 3. draped on a terrain
await ev(`window.__a3dTestSetObjs([]);var tid=window.__a3dMakeTerrain([[-60,-60,0,'',''],[60,-60,4,'',''],[60,60,12,'',''],[-60,60,2,'',''],[0,0,18,'',''],[20,-30,6,'','']]);
  window.__a3dSelectFor([]);window.__a3dFlat(false);window.__a3dCamSet({pitch:0.5,yaw:0.7,dist:160});` + W8(600));
B = await both('3d-terrain');
ck(B.cmp.mapB > B.cmp.n * 0.2, 'the map draped on the terrain in the rendered view (' + B.cmp.mapB + ' of ' + B.cmp.n + ')');
ck(B.cmp.agree > 0.85, 'draped where the shaded view drapes it (' + (B.cmp.agree * 100).toFixed(1) + '% of ' + B.cmp.both + ' agree)');

// 4. off
await ev(`window.__a3dSelectFor([]);window.__a3dMapSet('style','off');` + W8(800));   // unselected: the selection's blue is not the map's
await settle();
const off = await classes(await shot(), 'off');
ck([...off].filter((c) => c !== '.').length < off.length * 0.02, 'the map off: none in the rendered view');
await ev('await window.__a3dRendered(false);');

const errs = C.ev.filter((e) => (e.method === 'Runtime.exceptionThrown') || (e.method === 'Runtime.consoleAPICalled' && e.params.type === 'error') ||
  (e.method === 'Runtime.consoleAPICalled' && e.params.type === 'warning' && /\[BIM\] Rendered/.test(JSON.stringify(e.params.args))));
ck(errs.length === 0, 'no console errors, no rendered-view warnings (' + errs.length + ')' + (errs.length ? ': ' + JSON.stringify(errs[0]).slice(0, 300) : ''));
console.log(`\n${pass} passed, ${fail} failed; ${tiles} tiles served`);
C.ws.close();
process.exit(fail ? 1 : 0);
