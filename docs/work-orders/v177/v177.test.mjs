// V177 step 1, Save as IFC's adapter (docs/work-orders/v177/SPEC.md): the app's own Pyodide (runtime/pyodide/
// 0.29.5) with IfcOpenShell's WebAssembly wheel (LGPL-3.0, unchanged) and its dependencies, each pinned by SHA-256 and
// kept in .cache/ifcos/ (not committed; fetched once), running the app's adapter src/py/bim_ifcos.py. Outside `npm test`
// until V177 pins the wheels in runtime/: the first run needs the network.
//
//   node --test docs/work-orders/v177/v177.test.mjs
//   node --test --test-name-pattern="WO-01" docs/work-orders/v177/v177.test.mjs
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const RT = path.join(ROOT, 'runtime', 'pyodide', '0.29.5');
const CACHE = path.join(ROOT, '.cache', 'ifcos');
const PYCDN = 'https://cdn.jsdelivr.net/pyodide/v0.29.5/full/';
// every wheel, pinned: IfcOpenShell's own (github.com/IfcOpenShell/wasm-wheels), Pyodide 0.29.5's builds of its
// dependencies (its pyodide-lock.json), and the two pure-Python ones Pyodide does not carry (PyPI). numpy is the
// app's own, in runtime/.
const WHEELS = [
  { f: 'six-1.17.0-py2.py3-none-any.whl', sha: 'bc830cfdc71a224b6d0e4337183a87ea53f21b6623deca5771ee3bc866fd8da2', u: PYCDN },
  { f: 'python_dateutil-2.9.0.post0-py2.py3-none-any.whl', sha: '1fe3a0346ef21bc85b295227256d6aed72aa8116178b019fc5ae5d57fbd213cf', u: PYCDN },
  { f: 'typing_extensions-4.15.0-py3-none-any.whl', sha: '42190f892f6219350c50e107954f57cb6196acac818fece4a7d21689c94f71de', u: PYCDN },
  { f: 'shapely-2.0.7-cp313-cp313-pyemscripten_2025_0_wasm32.whl', sha: '586daa7290c2d309f9e8d14589d4aa940b1d84502defb3adecc23e17897e476d', u: PYCDN },
  { f: 'isodate-0.7.2-py3-none-any.whl', sha: '28009937d8031054830160fce6d409ed342816b543597cece116d966c6d99e15',
    u: 'https://files.pythonhosted.org/packages/15/aa/0aca39a37d3c7eb941ba736ede56d689e7be91cab5d9ca846bde3999eba6/' },
  { f: 'lark-1.3.1-py3-none-any.whl', sha: 'c629b661023a014c37da873b4ff58a817398d12635d3bbb2c5a03be7fe5d1e12',
    u: 'https://files.pythonhosted.org/packages/82/3d/14ce75ef66813643812f3093ab17e46d3a206942ce7376d31ec2d36229e7/' },
  // 0.8.5, not 0.9.0.post1: 0.9's wheel keeps its schemas in separate modules and crashes opening a file when
  // unpacked alone (Claude, 2026-11-13; SPEC part 0)
  { f: 'ifcopenshell-0.8.5-cp313-cp313-pyodide_2025_0_wasm32.whl', sha: 'fbebb7a7144277be213d156ed9b77de30de1d92b0b2b0c815e4a07555bfb929c',
    u: 'https://raw.githubusercontent.com/IfcOpenShell/wasm-wheels/v0.8.5/' }
];
const sha256 = (b) => crypto.createHash('sha256').update(b).digest('hex');
async function pinned(w) {
  const p = path.join(CACHE, w.f);
  let b = fs.existsSync(p) ? fs.readFileSync(p) : null;
  if (!b || sha256(b) !== w.sha) {
    const r = await fetch(w.u + w.f);
    if (!r.ok) throw new Error(w.f + ': HTTP ' + r.status);
    b = Buffer.from(await r.arrayBuffer());
    if (sha256(b) !== w.sha) throw new Error(w.f + ': not the pinned file (SHA-256 differs)');
    fs.mkdirSync(CACHE, { recursive: true });
    fs.writeFileSync(p, b);
  }
  return b;
}

let py = null;
const T = {};
// the adapter's functions, called from JavaScript as the app will call them: arguments as JSON, the answer as JSON
const call = (fn, ...args) => JSON.parse(py.runPython(`import json\njson.dumps(${fn}(*json.loads(${JSON.stringify(JSON.stringify(args))})))`));

before(async () => {
  let t = Date.now();
  const { loadPyodide } = createRequire(import.meta.url)(path.join(RT, 'pyodide.js'));
  py = await loadPyodide({ indexURL: RT + path.sep });
  T.boot = Date.now() - t; t = Date.now();
  await py.loadPackage('numpy');
  for (const w of WHEELS) { const b = await pinned(w); py.unpackArchive(new Uint8Array(b.buffer, b.byteOffset, b.byteLength), 'wheel'); }
  T.install = Date.now() - t; t = Date.now();
  py.runPython('import ifcopenshell, ifcopenshell.api.project, ifcopenshell.api.root, ifcopenshell.util.element, ifcopenshell.util.placement, ifcopenshell.util.unit, ifcopenshell.geom');
  T.import = Date.now() - t; t = Date.now();
  py.runPython(fs.readFileSync(path.join(ROOT, 'src', 'py', 'bim_ifcos.py'), 'utf8'));
  T.adapter = Date.now() - t;
  console.log('# times (ms): boot ' + T.boot + ', install ' + T.install + ', import ifcopenshell ' + T.import + ', the adapter ' + T.adapter);
});

// an element's box in the world, in metres, from IfcOpenShell's own geometry kernel: [x0, y0, z0, x1, y1, z1]
const box = (guid) => JSON.parse(py.runPython(`import json
_s = ifcopenshell.geom.settings()
_s.set("use-world-coords", True)
_sh = ifcopenshell.geom.create_shape(_s, _bim_ifcos_file.by_guid(${JSON.stringify(guid)}))
_v = _sh.geometry.verts
json.dumps([round(min(_v[0::3]), 4), round(min(_v[1::3]), 4), round(min(_v[2::3]), 4), round(max(_v[0::3]), 4), round(max(_v[1::3]), 4), round(max(_v[2::3]), 4)])`));
const ev = (code) => JSON.parse(py.runPython('import json\njson.dumps(' + code + ')'));
const near = (a, b, msg) => { assert.equal(a.length, b.length, msg); a.forEach((v, i) => assert.ok(Math.abs(v - b[i]) < 1e-3, (msg || 'box') + ': ' + JSON.stringify(a) + ' is not ' + JSON.stringify(b))); };
const LEVELS = [{ name: 'Ground', elev: 0 }, { name: 'First', elev: 3.2 }];

test('WO-01 bim_ifcos_matrix, bim_ifcos_storey, bim_ifcos_body, bim_ifcos_keep_guid: the small parts every element uses', () => {
  assert.deepEqual(ev('[[round(float(v), 6) + 0 for v in r] for r in bim_ifcos_matrix(1, 2, 3, 0)]'), [[1, 0, 0, 1], [0, 1, 0, 2], [0, 0, 1, 3], [0, 0, 0, 1]]);
  assert.deepEqual(ev('[[round(float(v), 6) + 0 for v in r] for r in bim_ifcos_matrix(0, 0, 0, math.pi / 2)]'), [[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]);
  call('bim_ifcos_new_project', 'Parts', 0);
  assert.equal(ev('bim_ifcos_storey(0).Name'), 'Level 0');
  assert.equal(ev('bim_ifcos_storey(7).Name'), 'Level 0', 'a level that is not there: the first storey');
  assert.equal(ev('bim_ifcos_storey(None).Name'), 'Level 0');
  assert.equal(ev('bim_ifcos_body().ContextIdentifier'), 'Body');
  py.runPython('_p = ifcopenshell.api.root.create_entity(_bim_ifcos_file, ifc_class="IfcBuildingElementProxy", name="P")');
  assert.equal(ev('bim_ifcos_keep_guid(_p, "2O2Fr$t4X7Zf8NOew3FLOH")'), '2O2Fr$t4X7Zf8NOew3FLOH');
  assert.equal(ev('_p.GlobalId'), '2O2Fr$t4X7Zf8NOew3FLOH');
  py.runPython('_q = ifcopenshell.api.root.create_entity(_bim_ifcos_file, ifc_class="IfcBuildingElementProxy", name="Q")\n_g1 = _q.GlobalId');
  assert.equal(ev('bim_ifcos_keep_guid(_q, "2O2Fr$t4X7Zf8NOew3FLOH") == _g1'), true, 'a GlobalId already in the file is not given twice');
  assert.equal(ev('bim_ifcos_keep_guid(_q, "short") == _g1'), true, 'not 22 characters: left as it is');
  assert.equal(ev('bim_ifcos_keep_guid(_q, "") == _g1'), true);
  assert.equal(ev('bim_ifcos_keep_guid(_q, None) == _g1'), true);
  assert.equal(ev('bim_ifcos_keep_guid(_q, "2O2Fr$t4X7Zf8NOew3FL!!") == _g1'), true, 'a character outside IFC\'s 64: left as it is');
});

test('WO-02 bim_ifcos_begin: a project with one storey for each level, named and placed at its elevation', () => {
  const s = call('bim_ifcos_begin', 'House', LEVELS);
  assert.deepEqual(s.storeys, [{ name: 'Ground', elevation: 0 }, { name: 'First', elevation: 3.2 }]);
  assert.deepEqual(s.products, { IfcBuilding: 1, IfcBuildingStorey: 2, IfcSite: 1 });
  assert.equal(ev('_bim_ifcos_file.by_type("IfcProject")[0].Name'), 'House');
  assert.deepEqual(ev('[round(float(ifcopenshell.util.placement.get_local_placement(s.ObjectPlacement)[2][3]), 6) for s in _bim_ifcos_file.by_type("IfcBuildingStorey")]'), [0, 3.2]);
  assert.equal(ev('len(_bim_ifcos_file.by_type("IfcBuilding")[0].IsDecomposedBy[0].RelatedObjects)'), 2, 'both storeys are parts of the building');
  assert.deepEqual(call('bim_ifcos_begin', 'Empty', []).storeys, [{ name: 'Level 0', elevation: 0 }], 'no levels: one, Level 0');
  assert.deepEqual(call('bim_ifcos_begin', 'Broken', [{ name: 'No elevation' }]), { error: 'failed' }, 'audit: a level without its elevation is an error, not an exception');
});

test('WO-03 bim_ifcos_put_wall: a straight wall on its level, from its base, with its offset from the line', () => {
  call('bim_ifcos_begin', 'Walls', LEVELS);
  const w = call('bim_ifcos_put_wall', { guid: '1kTvXnbbzCWw8lcMd1dR4o', name: 'Wall A', level: 1, x0: 1, y0: 2, x1: 5, y1: 2, base: 3.2, height: 2.7, thickness: 0.2, offset: -0.1 });
  assert.deepEqual(w, { guid: '1kTvXnbbzCWw8lcMd1dR4o' }, 'the GlobalId it was given');
  near(box(w.guid), [1, 1.9, 3.2, 5, 2.1, 5.9], 'centred on its line (offset -thickness/2), from 3.2 to 5.9');
  assert.equal(ev('ifcopenshell.util.element.get_container(_bim_ifcos_file.by_guid("1kTvXnbbzCWw8lcMd1dR4o")).Name'), 'First');
  assert.equal(ev('_bim_ifcos_file.by_guid("1kTvXnbbzCWw8lcMd1dR4o").is_a()'), 'IfcWall');
  assert.equal(ev('_bim_ifcos_file.by_guid("1kTvXnbbzCWw8lcMd1dR4o").Name'), 'Wall A');
  const v = call('bim_ifcos_put_wall', { name: 'Wall B', level: 0, x0: 0, y0: 0, x1: 0, y1: 4, base: 0, height: 3, thickness: 0.3, offset: 0 });
  assert.match(v.guid, /^[0-9A-Za-z_$]{22}$/, 'no GlobalId given: a new one');
  near(box(v.guid), [-0.3, 0, 0, 0, 4, 3], 'offset 0: the wall lies to the left of its line');
  assert.deepEqual(call('bim_ifcos_put_wall', { name: 'Zero', level: 0, x0: 1, y0: 1, x1: 1, y1: 1, base: 0, height: 3, thickness: 0.2, offset: 0 }), { error: 'zero length' });
  assert.equal(ev('len(_bim_ifcos_file.by_type("IfcWall"))'), 2);
  assert.match(call('bim_ifcos_put_wall', { level: 0, x0: 0, y0: 5, x1: 3, y1: 5, base: 0, height: 3, thickness: 0.2 }).guid, /^[0-9A-Za-z_$]{22}$/, 'audit: a wall with no name and no offset is still written');
  assert.match(call('bim_ifcos_put_prism', { level: 0, pts: [[0, 0], [1, 0], [1, 1]], base: 0, depth: 0.2 }).guid, /^[0-9A-Za-z_$]{22}$/, 'audit: a prism with no name or class is a slab');
});

test('WO-04 bim_ifcos_put_prism: an outline raised by a depth (a floor slab, a column), as the class asked for', () => {
  call('bim_ifcos_begin', 'Prisms', LEVELS);
  const s = call('bim_ifcos_put_prism', { name: 'Floor', cls: 'IfcSlab', level: 1, pts: [[0, 0], [6, 0], [6, 4], [0, 4]], base: 3.0, depth: 0.2 });
  near(box(s.guid), [0, 0, 3, 6, 4, 3.2], 'the slab');
  assert.equal(ev(`_bim_ifcos_file.by_guid(${JSON.stringify(s.guid)}).is_a()`), 'IfcSlab');
  assert.equal(ev(`ifcopenshell.util.element.get_container(_bim_ifcos_file.by_guid(${JSON.stringify(s.guid)})).Name`), 'First');
  const c = call('bim_ifcos_put_prism', { guid: '3cUkl32yn9qRSPvBJVyWYp', name: 'Column', cls: 'IfcColumn', level: 0, pts: [[1.8, 1.8], [2.2, 1.8], [2.2, 2.2], [1.8, 2.2]], base: 0, depth: 3 });
  assert.deepEqual(c, { guid: '3cUkl32yn9qRSPvBJVyWYp' });
  near(box(c.guid), [1.8, 1.8, 0, 2.2, 2.2, 3], 'the column');
  assert.equal(ev('_bim_ifcos_file.by_guid("3cUkl32yn9qRSPvBJVyWYp").is_a()'), 'IfcColumn');
  assert.deepEqual(call('bim_ifcos_put_prism', { name: 'Two', cls: 'IfcSlab', level: 0, pts: [[0, 0], [1, 0]], base: 0, depth: 0.2 }), { error: 'bad outline' });
  assert.deepEqual(call('bim_ifcos_put_prism', { name: 'Flat', cls: 'IfcSlab', level: 0, pts: [[0, 0], [1, 0], [1, 1]], base: 0, depth: 0 }), { error: 'bad outline' });
  assert.equal(ev('len(_bim_ifcos_file.by_type("IfcSlab"))'), 1, 'nothing added by a refused one');
});

test('WO-05 bim_ifcos_put_opening: a door or a window, and the opening it fills, cut through its wall', () => {
  call('bim_ifcos_begin', 'Openings', LEVELS);
  const w = call('bim_ifcos_put_wall', { name: 'Host', level: 0, x0: 0, y0: 0, x1: 6, y1: 0, base: 0, height: 3, thickness: 0.2, offset: -0.1 });
  const d = call('bim_ifcos_put_opening', { guid: '0pJ7fGQDj3leJjVNZI5NAY', name: 'Door 1', cls: 'IfcDoor', host: w.guid, x: 2, y: 0, a: 0, base: 0, width: 0.9, height: 2.1, depth: 0.4 });
  assert.equal(d.guid, '0pJ7fGQDj3leJjVNZI5NAY');
  assert.match(d.opening, /^[0-9A-Za-z_$]{22}$/);
  assert.equal(ev('_bim_ifcos_file.by_guid("0pJ7fGQDj3leJjVNZI5NAY").is_a()'), 'IfcDoor');
  assert.equal(ev(`_bim_ifcos_file.by_guid(${JSON.stringify(d.opening)}).is_a()`), 'IfcOpeningElement');
  assert.equal(ev(`_bim_ifcos_file.by_guid(${JSON.stringify(d.opening)}).VoidsElements[0].RelatingBuildingElement.GlobalId`), w.guid, 'the opening voids its wall');
  assert.equal(ev(`_bim_ifcos_file.by_guid(${JSON.stringify(d.opening)}).HasFillings[0].RelatedBuildingElement.GlobalId`), d.guid, 'the door fills the opening');
  assert.equal(ev('ifcopenshell.util.element.get_container(_bim_ifcos_file.by_guid("0pJ7fGQDj3leJjVNZI5NAY")).Name'), 'Ground', 'in its wall\'s storey');
  near(box(d.opening), [1.55, -0.2, 0, 2.45, 0.2, 2.1], 'centred on (2, 0), 0.9 wide, 0.4 through the wall, 2.1 high');
  const db = box(d.guid);
  assert.ok(Math.abs(db[0] - 1.55) < 0.05 && Math.abs(db[3] - 2.45) < 0.05 && Math.abs(db[5] - 2.1) < 0.05, 'the door stands in its opening, its frame a little over it (' + db + ')');
  const n = call('bim_ifcos_put_opening', { name: 'Window 1', cls: 'IfcWindow', host: w.guid, x: 4.5, y: 0, a: 0, base: 0.9, width: 1.2, height: 1.2, depth: 0.4 });
  assert.equal(ev(`_bim_ifcos_file.by_guid(${JSON.stringify(n.guid)}).is_a()`), 'IfcWindow');
  near(box(n.opening), [3.9, -0.2, 0.9, 5.1, 0.2, 2.1], 'the window\'s opening');
  // a wall along +Y: the opening turns with it
  const u = call('bim_ifcos_put_wall', { name: 'Side', level: 0, x0: 6, y0: 0, x1: 6, y1: 5, base: 0, height: 3, thickness: 0.2, offset: -0.1 });
  const t = call('bim_ifcos_put_opening', { name: 'Door 2', cls: 'IfcDoor', host: u.guid, x: 6, y: 2.5, a: Math.PI / 2, base: 0, width: 1, height: 2, depth: 0.4 });
  near(box(t.opening), [5.8, 2, 0, 6.2, 3, 2], 'the opening in the wall along +Y');
  assert.deepEqual(call('bim_ifcos_put_opening', { name: 'Lost', cls: 'IfcDoor', host: '3cUkl32yn9qRSPvBJVyWYp', x: 0, y: 0, a: 0, base: 0, width: 1, height: 2, depth: 0.4 }), { error: 'no host' });
  assert.deepEqual(call('bim_ifcos_put_opening', { name: 'Thin', cls: 'IfcDoor', host: w.guid, x: 1, y: 0, a: 0, base: 0, width: 0, height: 2, depth: 0.4 }), { error: 'bad size' });
  assert.equal(ev('len(_bim_ifcos_file.by_type("IfcOpeningElement"))'), 3);
});

test('WO-06 bim_ifcos_put_mesh and bim_ifcos_put_psets: any other element as its triangles, and property sets on an element', () => {
  call('bim_ifcos_begin', 'Meshes', LEVELS);
  const V = [[0, 0, 0], [2, 0, 0], [0, 2, 0], [0, 0, 2]], F = [[0, 2, 1], [0, 1, 3], [1, 2, 3], [0, 3, 2]];
  const m = call('bim_ifcos_put_mesh', { guid: '2XQ$n5SLP5MBLyL442paFx', name: 'Roof', cls: 'IfcRoof', level: 1, verts: V, faces: F });
  assert.deepEqual(m, { guid: '2XQ$n5SLP5MBLyL442paFx' });
  assert.equal(ev('_bim_ifcos_file.by_guid("2XQ$n5SLP5MBLyL442paFx").is_a()'), 'IfcRoof');
  near(box(m.guid), [0, 0, 0, 2, 2, 2], 'the mesh');
  assert.equal(ev('ifcopenshell.util.element.get_container(_bim_ifcos_file.by_guid("2XQ$n5SLP5MBLyL442paFx")).Name'), 'First');
  assert.deepEqual(call('bim_ifcos_put_mesh', { name: 'None', cls: 'IfcBuildingElementProxy', level: 0, verts: V, faces: [] }), { error: 'empty mesh' });
  assert.deepEqual(call('bim_ifcos_put_mesh', { name: 'Odd', cls: 'IfcNoSuchThing', level: 0, verts: V, faces: F }), { error: 'failed' }, 'a class IFC4 does not have');
  assert.deepEqual(call('bim_ifcos_put_psets', m.guid, [{ name: 'BIM_Personal', props: { Layer: 'Roofs', Pitch: 30, Kept: true } }, { name: 'Pset_Other', props: { Note: 'from the app' } }]), { psets: 2 });
  assert.deepEqual(ev('{k: v for k, v in ifcopenshell.util.element.get_psets(_bim_ifcos_file.by_guid("2XQ$n5SLP5MBLyL442paFx"))["BIM_Personal"].items() if k != "id"}'), { Layer: 'Roofs', Pitch: 30, Kept: true });
  assert.deepEqual(call('bim_ifcos_put_psets', m.guid, [{ name: 'Empty', props: {} }]), { psets: 0 }, 'a set with no properties is not written');
  assert.deepEqual(call('bim_ifcos_put_psets', '0pJ7fGQDj3leJjVNZI5NAY', [{ name: 'X', props: { a: 1 } }]), { error: 'not found' });
});

test('WO-07 bim_ifcos_export: a whole model written as one IFC file, with what could not be written told', () => {
  const model = {
    name: 'Export', levels: LEVELS,
    walls: [
      { id: 'w1', guid: '1kTvXnbbzCWw8lcMd1dR4o', name: 'Wall 1', level: 0, x0: 0, y0: 0, x1: 6, y1: 0, base: 0, height: 3, thickness: 0.2, offset: -0.1, psets: [{ name: 'BIM_Personal', props: { Layer: 'Walls' } }] },
      { id: 'w2', name: 'Wall 2', level: 0, x0: 6, y0: 0, x1: 6, y1: 4, base: 0, height: 3, thickness: 0.2, offset: -0.1 },
      { id: 'w3', name: 'No length', level: 0, x0: 2, y0: 2, x1: 2, y1: 2, base: 0, height: 3, thickness: 0.2, offset: 0 }],
    prisms: [{ id: 'f1', name: 'Floor', cls: 'IfcSlab', level: 0, pts: [[0, 0], [6, 0], [6, 4], [0, 4]], base: -0.2, depth: 0.2 }],
    openings: [
      { id: 'd1', name: 'Door', cls: 'IfcDoor', host: 'w1', x: 2, y: 0, a: 0, base: 0, width: 0.9, height: 2.1, depth: 0.4 },
      { id: 'd2', name: 'Orphan', cls: 'IfcWindow', host: 'w3', x: 2, y: 2, a: 0, base: 1, width: 1, height: 1, depth: 0.4 },
      { id: 'd3', name: 'Nowhere', cls: 'IfcWindow', host: 'w9', x: 2, y: 2, a: 0, base: 1, width: 1, height: 1, depth: 0.4 }],
    meshes: [{ id: 'm1', name: 'Roof', cls: 'IfcRoof', level: 1, verts: [[0, 0, 3], [6, 0, 3], [3, 2, 5], [6, 4, 3], [0, 4, 3]], faces: [[0, 1, 2], [1, 3, 2], [3, 4, 2], [4, 0, 2], [0, 4, 3], [0, 3, 1]] }]
  };
  const r = call('bim_ifcos_export', model, '/tmp/export.ifc');
  assert.ok(r.bytes > 2000, 'a file was written (' + r.bytes + ' bytes)');
  assert.deepEqual(r.summary.products, { IfcBuilding: 1, IfcBuildingStorey: 2, IfcDoor: 1, IfcRoof: 1, IfcSite: 1, IfcSlab: 1, IfcWall: 2 });
  assert.deepEqual(r.summary.storeys, [{ name: 'Ground', elevation: 0 }, { name: 'First', elevation: 3.2 }]);
  assert.deepEqual(r.skipped, [{ id: 'w3', why: 'zero length' }, { id: 'd2', why: 'no host' }, { id: 'd3', why: 'no host' }]);
  assert.equal(r.written, 5, 'two walls, a floor, a door, a roof');
  const text = py.FS.readFile('/tmp/export.ifc', { encoding: 'utf8' });
  assert.ok(text.startsWith('ISO-10303-21;'));
  assert.ok(text.includes('1kTvXnbbzCWw8lcMd1dR4o'), 'the wall kept its GlobalId in the file');
  py.runPython('_g = ifcopenshell.open("/tmp/export.ifc")');
  assert.deepEqual(ev('{k: v for k, v in ifcopenshell.util.element.get_psets(_g.by_guid("1kTvXnbbzCWw8lcMd1dR4o"))["BIM_Personal"].items() if k != "id"}'), { Layer: 'Walls' });
  assert.equal(ev('len(_g.by_type("IfcRelVoidsElement"))'), 1);
  // the wall read back from the file, with its door cut: the hole is there (more corners than a box's eight)
  py.runPython('_cut = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), _g.by_guid("1kTvXnbbzCWw8lcMd1dR4o"))');
  assert.ok(ev('len(_cut.geometry.verts) // 3') > 8, 'the door is cut out of the wall');
  // an empty model is still a valid file
  const e = call('bim_ifcos_export', { name: 'Nothing', levels: [] }, '/tmp/empty.ifc');
  assert.deepEqual(e.summary.products, { IfcBuilding: 1, IfcBuildingStorey: 1, IfcSite: 1 });
  assert.deepEqual(e.skipped, []);
  assert.equal(e.written, 0);
});

