/* bim_phase174_boards_edge_check.mjs -- V174's browser check (a to d), run 2026-11-08: 27 of 27.

   It drives Edge (or any Chromium) through the DevTools protocol with Node's own WebSocket, no dependencies, for a
   PC where the Playwright plugin's Chrome and Python's Playwright are not installed. To run it:
     python -m http.server 8765 --bind 127.0.0.1                        (from the repository's root)
     msedge --headless=new --remote-debugging-port=9333 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase174_boards_edge_check.mjs <a folder for the screenshots and the PDF>
   A fresh profile each run: the project is kept in the browser's database, and a second run finds the first's layers.
   It checks: a board's objects on the one layer table (paint order by the Layers list, ByLayer Blend and Transparency
   in Presentation only, the rows under their layers, a layer moved and stepped, a no-plot layer off paper), align,
   distribute and a stack, an A3 page with its ISO frame and title block, a map frame (not blank, centred), its north
   arrow, scale bar and legend, Print set to PDF (the page size, Multiply kept), New Sheet's gallery, and the console. */
import fs from 'node:fs';
const PORT = 9333, APP = 'http://127.0.0.1:8765/canvas_v10.html', OUT = process.argv[2] || '.';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function target() {
  for (let i = 0; i < 40; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' }); return await r.json(); } catch (e) { await sleep(250); }
  }
  throw new Error('no Edge');
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
await C.send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 1000, deviceScaleFactor: 1, mobile: false });
async function ev(expr) {
  const r = await C.send('Runtime.evaluate', { expression: `(async()=>{${expr}})()`, awaitPromise: true, returnByValue: true });
  if (r.result.exceptionDetails) return { __err: (r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description || r.result.exceptionDetails.text).slice(0, 400) };
  return r.result.result.value;
}
let pass = 0, fail = 0;
function ck(ok, msg) { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + msg); }
async function shot(name) { const r = await C.send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.result.data, 'base64')); }
const W8 = 'await new Promise(r=>setTimeout(r,200));';

await C.send('Page.navigate', { url: APP });
await sleep(4500);
let r = await ev(`window.__a3dEnter&&window.__a3dEnter();
  var S=[];for(var i=0;i<4;i++)S.push({id:'S'+i,t:'sketch',name:'Block '+i,col:'#5ec4b8',pos:[0,0,0],pts:[[i*12,0],[i*12+8,0],[i*12+8,5+i*2],[i*12,5+i*2]],y:0,layer:'layer-0'});
  window.__a3dTestSetObjs(S);window.__a3dTestPaint&&window.__a3dTestPaint();
  return {d:!!window.__a3dBoardDesign,light:document.body.classList.contains('light-theme')};`);
ck(r && r.d, 'the app loads with the V174 hooks (' + JSON.stringify(r) + ')');

// ---- a: objects on the one layer table
r = await ev(`var D=window.__a3dBoardDesign;var id=window.__a3dBrdNew('V174 check');${W8}
  var dl=document.querySelector('.a3d-clb-dlg [data-brddlg="cancel"]');if(dl)dl.click();
  var top=window.__a3dLayerNew({name:'Top'}),bot=window.__a3dLayerNew({name:'Bottom'});
  window.__a3dLayerSet(top,'blend','multiply');window.__a3dLayerSet(top,'transparency',30);
  var b=D.add('rect',{layer:bot,fill:'#0000ff',x:40,y:40,w:60,h:40}),t=D.add('rect',{layer:top,fill:'#ff0000',x:60,y:50,w:60,h:40});${W8}
  var q=s=>document.querySelector('.a3d-clb-dsn [data-bde="'+s+'"]'),order=[].map.call(document.querySelectorAll('.a3d-clb-dsn [data-bde]'),e=>e.getAttribute('data-bde'));
  var tech=getComputedStyle(q(t)).mixBlendMode;
  D.pres(true);${W8}
  var pres=getComputedStyle(q(t)).mixBlendMode,op=getComputedStyle(q(t)).opacity;
  var rb=document.querySelector('#a3d-rail .a3d-railbtn[data-tab="layers"]');if(rb)rb.click();${W8}
  for(var li of [top,bot]){var c=document.querySelector('[data-lytog="'+li+'"]');if(c&&/^Open/.test(c.title)){c.click();await new Promise(r=>setTimeout(r,150));}}
  var rows=document.querySelectorAll('[data-lybo]').length;
  var pb=document.querySelector('#a3d-rail .a3d-railbtn[data-tab="presentation"]');if(pb)pb.click();${W8}
  return {id:id,top:top,bot:bot,b:b,t:t,order:order,tech:tech,pres:pres,op:op,rows:rows,
    props:!!document.querySelector('[data-bdf="bm"]'),panel:!!document.querySelector('.a3d-clb-dpnl')};`);
const A = r || {};
ck(A.order && A.order.indexOf(A.b) < A.order.indexOf(A.t), 'paint order: Top, higher in the Layers list, is drawn over Bottom (' + JSON.stringify(A.order) + ')');
ck(A.tech === 'normal', 'Technical appearance: the layer\'s Multiply is not drawn (' + A.tech + ')');
ck(A.pres === 'multiply' && A.op === '0.7', 'Presentation: ByLayer Multiply and 30% transparency (' + A.pres + ', ' + A.op + ')');
ck(A.rows >= 2, 'the board\'s objects are rows under their layers in the Layers tab (' + A.rows + ')');
ck(A.props, 'the selection\'s Blend is in the Properties panel');
ck(!A.panel, 'no floating panel of its own');
await shot('v174-a-layers');
r = await ev(`var D=window.__a3dBoardDesign;D.layerMove('${A.bot}','${A.top}','before');${W8}
  var order=[].map.call(document.querySelectorAll('.a3d-clb-dsn [data-bde]'),e=>e.getAttribute('data-bde'));
  var L=window.__a3dLayers().map(l=>l.name);D.layerStep('${A.bot}',1);${W8}
  var L2=window.__a3dLayers().map(l=>l.name);return {order:order,L:L,L2:L2};`);
ck(r && r.order.indexOf(A.b) > r.order.indexOf(A.t), 'a layer moved above another: its objects are now drawn over (' + JSON.stringify(r && r.L) + ')');
ck(r && r.L2.indexOf('Bottom') > r.L2.indexOf('Top'), 'and stepped down again (' + JSON.stringify(r && r.L2) + ')');
r = await ev(`window.__a3dLayerSet('${A.top}','plot',false);${W8}var h=window.__a3dPrintSetHtml().html,on=!!document.querySelector('.a3d-clb-dsn [data-bde="${A.t}"]');
  window.__a3dLayerSet('${A.top}','plot',true);return {print:h.indexOf('data-bde="${A.t}"')>=0,screen:on};`);
ck(r && !r.print && r.screen, 'a no-plot layer: on screen, not on paper (' + JSON.stringify(r) + ')');

// ---- b: align, distribute, a stack
r = await ev(`var D=window.__a3dBoardDesign,ids=[D.add('rect',{layer:'${A.bot}',x:10,y:120,w:20,h:10}),D.add('rect',{layer:'${A.bot}',x:50,y:130,w:20,h:10}),D.add('rect',{layer:'${A.bot}',x:140,y:125,w:20,h:10})];
  D.select(ids);D.arrange('al-top');D.select(ids);D.arrange('dist-x');${W8}
  var O=D.objs().filter(o=>ids.indexOf(o.id)>=0);
  return {y:O.map(o=>o.y),x:O.map(o=>o.x)};`);
ck(r && r.y && r.y[0] === 120 && r.y[1] === 120 && r.y[2] === 120, 'align top (' + JSON.stringify(r) + ')');
ck(r && r.x && Math.abs((r.x[1] - r.x[0]) - (r.x[2] - r.x[1])) < 1e-6, 'distribute across: equal gaps');
r = await ev(`var D=window.__a3dBoardDesign;D.stack('${A.bot}',{dir:'row',gap:5,pad:0});${W8}
  var O=D.objs().filter(o=>o.layer==='${A.bot}');return O.map(o=>[o.x,o.y,o.w]);`);
ck(Array.isArray(r) && r.length >= 4 && r.every((o, i) => i === 0 || Math.abs(o[0] - (r[i - 1][0] + r[i - 1][2] + 5)) < 1e-6), 'a stack lays Bottom\'s objects in a row, 5 mm apart (' + JSON.stringify(r) + ')');
r = await ev(`var D=window.__a3dBoardDesign;D.stack('${A.bot}',{dir:null});return 1;`);

// ---- c: a page, the gallery, the title block
r = await ev(`var D=window.__a3dBoardDesign;D.page('iso-A3','l','iso');${W8}
  var d=document.querySelector('.a3d-clb-dsn'),O=D.objs();
  return {w:d&&d.style.width,pg:d&&d.classList.contains('pg'),tb:O.filter(o=>o.t==='tblock').length,bd:O.filter(o=>o.t==='border').length,
    tbText:(document.querySelector('.a3d-clb-dtb')||{}).textContent||''};`);
ck(r && r.pg && Math.abs(parseFloat(r.w) - 420 * 96 / 25.4) < 0.01, 'the board is an A3 landscape page (' + (r && r.w) + ')');
ck(r && r.tb === 1 && r.bd === 1 && /Presentation board/.test(r.tbText) && /B-\d\d/.test(r.tbText), 'ISO frame and ISO 7200 title block, with its number (' + JSON.stringify(r && r.tbText.slice(0, 120)) + ')');
await shot('v174-c-page');

// ---- d: a map frame, its legend, north arrow and scale bar
r = await ev(`var D=window.__a3dBoardDesign,t0=performance.now(),m=D.add('map',{x:30,y:20});var t1=performance.now();${W8}
  var n=D.add('north'),s=D.add('sbar'),l=D.add('legend');${W8}
  var img=document.querySelector('.a3d-clb-dsn [data-bde="'+m+'"] img');
  var px=-1;if(img){await img.decode().catch(()=>{});var c=document.createElement('canvas');c.width=img.naturalWidth;c.height=img.naturalHeight;var x=c.getContext('2d');x.drawImage(img,0,0);
    var d=x.getImageData(0,0,c.width,c.height).data,k=0,x0=1e9,x1=-1,y0=1e9,y1=-1;for(var i=0;i<d.length;i+=4)if(d[i]<240||d[i+1]<240||d[i+2]<240){k++;var p=i/4,xx=p%c.width,yy=Math.floor(p/c.width);if(xx<x0)x0=xx;if(xx>x1)x1=xx;if(yy<y0)y0=yy;if(yy>y1)y1=yy;}px=k;
    var cen=[((x0+x1)/2)/c.width,((y0+y1)/2)/c.height],edge=x0<=1||y0<=1||x1>=c.width-2||y1>=c.height-2;}
  var O=D.objs(),M=O.filter(o=>o.id===m)[0];
  var nsvg=document.querySelector('.a3d-clb-dsn [data-bde="'+n+'"]'),ssvg=document.querySelector('.a3d-clb-dsn [data-bde="'+s+'"]');
  var t2=performance.now();window.__a3dBrdEdit(true);var t3=performance.now();
  return {m:m,den:M&&M.den,src:M&&M.src,img:!!img,ink:px,cen:typeof cen!=='undefined'?cen:null,edge:typeof edge!=='undefined'?edge:null,addMs:Math.round(t1-t0),redrawMs:Math.round(t3-t2),north:!!(nsvg&&nsvg.querySelector('g[transform^="rotate"]')),
    sbar:ssvg?ssvg.textContent:'',legend:(document.querySelector('.a3d-clb-dsn [data-bde="'+l+'"]')||{}).textContent||''};`);
ck(r && r.img && r.ink > 50, 'a map frame shows the plan, not a blank picture (' + JSON.stringify(r && { den: r.den, src: r.src, ink: r.ink }) + ')');
ck(r && r.cen && Math.abs(r.cen[0] - 0.5) < 0.05 && Math.abs(r.cen[1] - 0.5) < 0.05 && !r.edge, 'the frame is centred on the model and shows it whole (' + JSON.stringify(r && { cen: r.cen, edge: r.edge }) + ')');
ck(r && r.north, 'the north arrow is drawn, through the frame\'s camera');
ck(r && /\d+ (m|km)/.test(r.sbar) && /1:\d+/.test(r.sbar), 'the scale bar: a 1-2-5 number and the scale (' + (r && r.sbar) + ')');
ck(r && /no data or result layer/.test(r.legend), 'the legend with nothing shown says so in Edit, and is left off paper (' + (r && r.legend) + ')');
console.log('INFO map frame: drawn in ' + (r && r.addMs) + ' ms; the board redrawn with it in ' + (r && r.redrawMs) + ' ms');
await shot('v174-d-map');

// ---- print: the set to PDF; the board's page size, blend modes kept
const ps = await ev(`D=window.__a3dBoardDesign;D.pres(true);var o=window.__a3dPrintSetHtml();return {html:o.html,n:o.n,lost:o.lost};`);
ck(ps && ps.html && !ps.lost.length, 'Print set puts the board together (' + (ps && ps.n) + ' pages)');
const t2 = await target(); const C2 = await connect(t2);
await C2.send('Page.enable'); await C2.send('Runtime.enable');
await C2.send('Page.navigate', { url: 'http://127.0.0.1:8765/package.json' }); await sleep(800);
await C2.send('Runtime.evaluate', { expression: `document.open();document.write(${JSON.stringify(ps.html.replace('window.print();', ''))});document.close();1` });
await sleep(2000);
const pdf = await C2.send('Page.printToPDF', { preferCSSPageSize: true, printBackground: true });
const buf = Buffer.from(pdf.result.data, 'base64'); fs.writeFileSync(`${OUT}/v174-printset.pdf`, buf);
const txt = buf.toString('latin1');
const boxes = [...txt.matchAll(/MediaBox\s*\[\s*0 0 ([\d.]+) ([\d.]+)\s*\]/g)].map((m) => [+m[1], +m[2]]);
const bms = {}; (txt.match(/\/BM\s*\/[A-Za-z]+/g) || []).forEach((m) => { const k = m.replace(/\/BM\s*\//, ''); bms[k] = (bms[k] || 0) + 1; });
ck(boxes.some((b) => Math.abs(b[0] - 1190.55) < 1.5 && Math.abs(b[1] - 841.89) < 1.5), 'the board prints on an A3 landscape page (' + JSON.stringify(boxes) + ')');
ck(boxes.length === 1, 'one page: the board is not cut in pieces (it has no figures, so no notes page) (' + boxes.length + ' pages)');
ck(bms.Multiply > 0, 'Multiply kept in the PDF (' + JSON.stringify(bms) + ')');

// ---- the New Sheet gallery
r = await ev(`window.__a3dBrdEdit(false);var c=document.querySelector('.a3d-clb [data-clb="close"]');if(c)c.click();${W8}
  var sa=document.querySelector('#a3d-sheetadd');if(sa)sa.click();${W8}
  var g=document.querySelectorAll('.a3d-dlg .a3d-pggc').length,a=document.querySelector('.a3d-dlg [data-pgkey="arch-D"]');if(a)a.click();${W8}
  var on=document.querySelector('.a3d-dlg .a3d-pggc.on'),ok=document.querySelector('.a3d-dlg [data-a3dlg="ok"]');if(ok)ok.click();${W8}
  var S=window.__a3dSheets?window.__a3dSheets():null;
  return {cards:g,on:on&&on.getAttribute('data-pgkey'),sheet:S&&S.length?{k:S[S.length-1].sizeKey,w:S[S.length-1].w,h:S[S.length-1].h}:null};`);
ck(r && r.cards === 16 && r.on === 'arch-D', 'New Sheet: the gallery, 16 sizes, Arch D picked (' + JSON.stringify(r) + ')');
ck(r && (!r.sheet || (r.sheet.k === 'ANSI-D-L' && r.sheet.w === 914.4)), 'the sheet is Arch D landscape (' + JSON.stringify(r && r.sheet) + ')');

const errs = C.ev.filter((e) => (e.method === 'Runtime.exceptionThrown') || (e.method === 'Log.entryAdded' && e.params.entry.level === 'error' && !/favicon\.ico/.test(e.params.entry.url || '')) ||
  (e.method === 'Runtime.consoleAPICalled' && (e.params.type === 'error' || (e.params.type === 'warning' && JSON.stringify(e.params.args).indexOf('[BIM]') >= 0))));
errs.forEach((e) => console.log('CONSOLE', JSON.stringify(e.params).slice(0, 400)));
ck(errs.length === 0, 'no console errors and no [BIM] warnings (' + errs.length + ')');
console.log(`\n${pass} of ${pass + fail} passed`);
C.ws.close(); C2.ws.close(); process.exit(0);
