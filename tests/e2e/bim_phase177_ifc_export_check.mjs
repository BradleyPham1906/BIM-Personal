/* bim_phase177_ifc_export_check.mjs -- V177's browser check: File, Export, IFC, through IfcOpenShell in its worker
   (docs/research/research-ifcopenshell-app.md, docs/work-orders/v177/SPEC.md).

   It drives Edge (or any Chromium) through the DevTools protocol with Node's own WebSocket, no dependencies, as
   bim_phase198_rendered_map_check.mjs does. To run it:
     python -m http.server 8765 --bind 127.0.0.1                        (from the repository's root)
     msedge --headless=new --remote-debugging-port=9337 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase177_ifc_export_check.mjs
   A small house is drawn with the app's own tools (two levels, straight walls, a wall with an arc, a floor, a door,
   a window, a column, a box), saved as IFC, and the file's text is read: its storeys, its classes, the cut
   openings, the kept names. Then the file is opened again by the app's IFC import and the elements counted. */
const PORT = +(process.env.CDP_PORT || 9337), APP = (process.env.APP_BASE || 'http://127.0.0.1:8765') + '/canvas_v10.html';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function target() {
  for (let i = 0; i < 40; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' }); return await r.json(); } catch (e) { await sleep(250); }
  }
  throw new Error('no browser on port ' + PORT);
}
async function connect(t) {
  const ws = new WebSocket(t.webSocketDebuggerUrl); let id = 0; const wait = {}, logs = [];
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  ws.onmessage = (m) => {
    const d = JSON.parse(m.data);
    if (d.id && wait[d.id]) { wait[d.id](d); delete wait[d.id]; }
    else if (d.method === 'Runtime.consoleAPICalled') logs.push(d.params.type + ': ' + d.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
    else if (d.method === 'Runtime.exceptionThrown') logs.push('exception: ' + (d.params.exceptionDetails.exception && d.params.exceptionDetails.exception.description || d.params.exceptionDetails.text).slice(0, 300));
  };
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; wait[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
  return { send, logs };
}
const C = await connect(await target());
await C.send('Runtime.enable'); await C.send('Page.enable');
await C.send('Emulation.setDeviceMetricsOverride', { width: 1500, height: 950, deviceScaleFactor: 1, mobile: false });
async function ev(expr) {
  const r = await C.send('Runtime.evaluate', { expression: `(async()=>{${expr}})()`, awaitPromise: true, returnByValue: true });
  if (r.result.exceptionDetails) return { __err: (r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description || r.result.exceptionDetails.text).slice(0, 400) };
  return r.result.result.value;
}
let pass = 0, fail = 0;
function ck(ok, msg) { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + msg); }
const count = (text, cls) => (text.match(new RegExp('=\\s*' + cls + '\\(', 'g')) || []).length;

await C.send('Page.navigate', { url: APP });
await sleep(5000);
let r = await ev('return window.__acad3dV177||null;');
ck(r && /ifcout/.test(r), 'the V177 marker (' + r + ')');

// the model, with the app's own tools
r = await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('3d');
  var w1=window.__a3dCurvedWall([[0,0],[6,0],[6,4]],null,0.2,3,'center',false);
  var w2=window.__a3dCurvedWall([[0,4],[0,0]],null,0.3,3,'left',false);
  var arc=window.__a3dCurvedWall([[0,4],[6,4]],[0.3],0.2,3,'center',false);
  var d=window.__a3dDoorAt(w1,[2,0],0.9,2.1);
  var n=window.__a3dWindowAt(w1,[6,2],1.2,1.2,0.9);
  var f=window.__a3dFloorAt([[0,0],[6,0],[6,4],[0,4]],0,0.2);
  var c=window.__a3dColumnAt([3,2],0,0.4,0.4,3);
  return {w1:w1,w2:w2,arc:arc,d:d,n:n,f:f,c:c,objs:window.__a3dIfcSave&&typeof window.__a3dIfcSave.model};`);
ck(r && r.w1 && r.w2 && r.arc && r.d && r.n && r.f && r.c, 'the house is drawn: two straight walls, an arc wall, a door, a window, a floor, a column (' + JSON.stringify(r) + ')');
ck(r && r.objs === 'function', 'the model-as-data functions are in this build');

// the button, in the Export group
r = await ev(`var q=function(){return document.querySelector('[data-a3dr="m:exportifc"],[data-rkact="m:exportifc"]');},b=q(),all=document.getElementById('a3d-dall');
  if(!b&&all){all.click();await new Promise(function(r){setTimeout(r,500);});b=q();}
  var out=b?{label:b.getAttribute('aria-label')||'',text:(b.textContent||'').trim()}:null;
  if(all&&b)all.click();
  return out;`);
ck(!!r && /IFC/.test(r.text + r.label), 'All tools, Export has an IFC button (' + JSON.stringify(r) + ')');

// Save as IFC: the first time loads IfcOpenShell
const t0 = Date.now();
r = await ev(`try{var R=await window.__a3dIfcExport();return {text:R.text,written:R.written,left:R.left,summary:R.summary,ms:R.ms,os:window.__a3dIfcos()};}catch(e){return {err:String(e&&e.message||e),os:window.__a3dIfcos()};}`);
const first = Date.now() - t0;
ck(r && !r.err && !r.__err, 'the model is written as IFC' + (r && (r.err || r.__err) ? ': ' + (r.err || r.__err) : ' in ' + first + ' ms the first time (IfcOpenShell ' + (r.os && r.os.version) + ' started in ' + (r.os && r.os.ms) + ' ms)'));
const text = (r && r.text) || '';
ck(text.startsWith('ISO-10303-21;') && /FILE_SCHEMA\(\('IFC4'\)\)/.test(text), 'an IFC4 file (' + text.length + ' characters)');
ck(r && r.os && r.os.version === '0.8.5', 'IfcOpenShell 0.8.5 wrote it');
ck(first < 60000, 'the first save, with IfcOpenShell\'s start, took under a minute (' + first + ' ms)');
ck(count(text, 'IFCWALL') === 4, 'four walls: three straight segments and the arc wall as its shape (' + count(text, 'IFCWALL') + ')');
ck(count(text, 'IFCDOOR') === 1 && count(text, 'IFCWINDOW') === 1, 'a door and a window (' + count(text, 'IFCDOOR') + ', ' + count(text, 'IFCWINDOW') + ')');
ck(count(text, 'IFCOPENINGELEMENT') === 2 && count(text, 'IFCRELVOIDSELEMENT') === 2 && count(text, 'IFCRELFILLSELEMENT') === 2, 'each cuts its wall and fills its opening');
ck(count(text, 'IFCSLAB') === 1 && count(text, 'IFCCOLUMN') === 1, 'a slab and a column');
ck(count(text, 'IFCBUILDINGSTOREY') >= 1, 'the levels as storeys (' + count(text, 'IFCBUILDINGSTOREY') + ')');
ck(count(text, 'IFCEXTRUDEDAREASOLID') >= 5, 'the straight walls, the slab and the column are extrusions, not triangles (' + count(text, 'IFCEXTRUDEDAREASOLID') + ')');
ck(/BIM_Personal/.test(text), 'each element carries the BIM_Personal property set');
ck(r && r.written === 8 && r.left && r.left.length === 0, 'eight elements written (four walls, a door, a window, a floor, a column), none left out (' + (r && r.written) + ', ' + JSON.stringify(r && r.left) + ')');

// a second save does not start it again
const t1 = Date.now();
let r2 = await ev(`var R=await window.__a3dIfcExport();return {n:R.text.length,ms:R.ms};`);
ck(r2 && r2.n > 1000 && Date.now() - t1 < 10000, 'a second save is quick (' + (Date.now() - t1) + ' ms)');

// the file opened again by the app's own IFC import
r = await ev(`window.__a3dTestSetObjs([]);var text=${JSON.stringify(text)};
  var R=await window.__a3dIfc.importBuffer(new TextEncoder().encode(text),'house.ifc');
  return {n:R.ids.length,by:R.text};`);
ck(r && !r.__err && r.n === 8, 'the app opens its own file again: ' + (r && r.n) + ' elements (' + JSON.stringify(r && (r.by || r.__err)) + ')');

// Make editable (WO-16): an imported wall without an opening, and the floor, rebuilt as the app's own under their GlobalIds
r = await ev(`return window.__a3dIfcEdit.list();`);
const L = r || [], freeWall = L.find((x) => x.type === 'wall' && !x.why), cutWall = L.find((x) => x.type === 'wall' && /opening/.test(x.why)),
  slab = L.find((x) => x.type === 'floor');
ck(L.length === 5 && freeWall && cutWall && slab, 'the imported walls and floor are offered or refused with a reason (' + JSON.stringify(L.map((x) => x.type + ':' + (x.why || 'ok'))) + ')');
r = await ev(`const n0=window.__a3dIfcEdit.count(),b0=window.__a3dIfcEdit.info('${freeWall && freeWall.id}').box;
  window.__a3dSelectFor(['${freeWall && freeWall.id}']);window.__a3dRefreshProps();await new Promise(r=>setTimeout(r,300));
  const btn=document.querySelector('#a3d-propsbody [data-ifcedit]');if(!btn)return {nobtn:true};
  btn.click();await new Promise(r=>setTimeout(r,300));
  const id=window.__a3dIfcEdit.byGuid('${freeWall && freeWall.guid}');
  return {id,n0,n1:window.__a3dIfcEdit.count(),b0,info:id?window.__a3dIfcEdit.info(id):null};`);
const same = (a, b) => a && b && a.every((v, i) => Math.abs(v - b[i]) < 0.03);
ck(r && r.id && r.n1 === r.n0 && r.info && !r.info.imported && r.info.centerline && r.info.guid === freeWall.guid,
  'Properties\' Make editable: the wall is now the app\'s own wall, in its place, under its GlobalId (' + JSON.stringify(r && (r.nobtn ? 'no button' : r.info && { guid: r.info.guid, cl: r.info.centerline, t: r.info.thickness })) + ')');
ck(r && r.info && same(r.b0, r.info.box), 'it stands exactly where the imported wall stood (' + JSON.stringify([r && r.b0, r && r.info && r.info.box]) + ')');
r = await ev(`const id=window.__a3dIfcEdit.make('${slab && slab.id}');return id?window.__a3dIfcEdit.info(id):null;`);
ck(r && r.type === 'floor' && r.profile && r.guid === slab.guid, 'the floor too (' + JSON.stringify(r && { guid: r.guid, n: r.profile && r.profile.length }) + ')');
r = await ev(`return window.__a3dIfcEdit.make('${cutWall && cutWall.id}');`);
ck(r === null, 'a wall an opening cuts is refused, not rebuilt without its cut');
r = await ev(`window.__a3dRunCmd('undo');await new Promise(r=>setTimeout(r,300));const id=window.__a3dIfcEdit.byGuid('${slab && slab.guid}');return id?window.__a3dIfcEdit.info(id):null;`);
ck(r && r.imported === true && r.type === 'floor', 'one undo puts the imported floor back (' + JSON.stringify(r && { imported: r.imported, guid: r.guid }) + ')');
r = await ev(`var R=await window.__a3dIfcExport();return R.text;`);
ck(typeof r === 'string' && r.indexOf("'" + freeWall.guid + "'") >= 0 && r.indexOf("'" + slab.guid + "'") >= 0,
  'saved again, the editable wall and floor keep their GlobalIds');

const bad = C.logs.filter((l) => /^(error|exception)/.test(l));
ck(bad.length === 0, 'no console errors' + (bad.length ? ': ' + bad.slice(0, 3).join(' | ') : ''));
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
