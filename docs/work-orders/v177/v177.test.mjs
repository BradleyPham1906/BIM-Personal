// V177, Save as IFC (docs/work-orders/v177/SPEC.md): the adapter src/py/bim_ifcos.py's new functions (WO-01 to WO-08),
// run in the app's own Pyodide with the pinned IfcOpenShell 0.8.5 wheels, as V176's tests run them (the same setup,
// the same cache .cache/ifcos/; the first run needs the network). Outside `npm test`.
//
//   node --test docs/work-orders/v177/v177.test.mjs
//   node --test --test-name-pattern="WO-03" docs/work-orders/v177/v177.test.mjs
//
// A function not built yet fails its own cases and no others.
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
  py.runPython('import ifcopenshell, ifcopenshell.api.project, ifcopenshell.api.root, ifcopenshell.util.element, ifcopenshell.util.placement, ifcopenshell.util.unit');
  T.import = Date.now() - t; t = Date.now();
  py.runPython(fs.readFileSync(path.join(ROOT, 'src', 'py', 'bim_ifcos.py'), 'utf8') +
    (process.env.V177_REF ? fs.readFileSync(process.env.V177_REF, 'utf8') : ''));
  T.adapter = Date.now() - t;
  console.log('# times (ms): boot ' + T.boot + ', install ' + T.install + ', import ifcopenshell ' + T.import + ', the adapter ' + T.adapter);
});


// a Python expression about the project, answered as JSON
const q = (expr) => JSON.parse(py.runPython(`import json\njson.dumps(${expr})`));
const built = (fn) => assert.ok(q(`'${fn}' in globals()`), fn + ' is not built yet in src/py/bim_ifcos.py');
const near = (a, b, msg) => assert.ok(Math.abs(a - b) < 1e-6, (msg || '') + ' ' + a + ' is not ' + b);
// a fresh project with one storey at 0, its guid
const fresh = () => { call('bim_ifcos_new_project', 'V177', 0); return q('_bim_ifcos_file.by_type("IfcBuildingStorey")[0].GlobalId'); };
// the placement matrix of an element, rows, rounded
const place = (guid) => q(`[[round(float(c), 6) for c in row] for row in ifcopenshell.util.placement.get_local_placement(_bim_ifcos_file.by_guid("${guid}").ObjectPlacement)]`);

/* ---------------- WO-01 bim_ifcos_add_storey ---------------- */
test('WO-01 a storey is added under the building, with its elevation', () => {
  built('bim_ifcos_add_storey');
  fresh();
  const r = call('bim_ifcos_add_storey', 'Level 1', 3.5);
  assert.equal(typeof r.guid, 'string');
  assert.deepEqual(call('bim_ifcos_summary', '').storeys, [{ name: 'Level 0', elevation: 0 }, { name: 'Level 1', elevation: 3.5 }]);
  assert.equal(q(`ifcopenshell.util.element.get_aggregate(_bim_ifcos_file.by_guid("${r.guid}")).is_a()`), 'IfcBuilding');
});
test('WO-01 no project', () => {
  built('bim_ifcos_add_storey');
  py.runPython('_bim_ifcos_file = None');
  assert.deepEqual(call('bim_ifcos_add_storey', 'Level 1', 3), { error: 'no project' });
});

/* ---------------- WO-02 bim_ifcos_add_wall_on ---------------- */
test('WO-02 a wall on the named storey, at its own height z, turned to its line', () => {
  built('bim_ifcos_add_wall_on');
  fresh();
  const s1 = call('bim_ifcos_add_storey', 'Level 1', 3).guid;
  const r = call('bim_ifcos_add_wall_on', s1, 'Wall B', 1, 1, 1, 5, 3.2, 2.8, 0.3, -0.15);
  const M = place(r.guid);
  near(M[0][3], 1); near(M[1][3], 1); near(M[2][3], 3.2);
  near(M[0][0], 0, 'cos'); near(M[1][0], 1, 'sin');
  assert.equal(q(`ifcopenshell.util.element.get_container(_bim_ifcos_file.by_guid("${r.guid}")).GlobalId`), s1);
  // the body: 4 m long, 0.3 m thick from -0.15 to 0.15 across the line, 2.8 m high
  const box = q(`(lambda it: [it.Depth, it.Position.Location.Coordinates[1]])(_bim_ifcos_file.by_guid("${r.guid}").Representation.Representations[0].Items[0])`);
  near(box[0], 2.8); near(box[1], -0.15);
});
test('WO-02 the errors: no storey, zero length, a bad size', () => {
  built('bim_ifcos_add_wall_on');
  const s0 = fresh();
  assert.deepEqual(call('bim_ifcos_add_wall_on', 'nope', 'W', 0, 0, 4, 0, 0, 3, 0.2, 0), { error: 'no storey' });
  assert.deepEqual(call('bim_ifcos_add_wall_on', s0, 'W', 2, 2, 2, 2, 0, 3, 0.2, 0), { error: 'zero length' });
  assert.deepEqual(call('bim_ifcos_add_wall_on', s0, 'W', 0, 0, 4, 0, 0, 0, 0.2, 0), { error: 'bad size' });
  assert.deepEqual(call('bim_ifcos_add_wall_on', s0, 'W', 0, 0, 4, 0, 0, 3, -1, 0), { error: 'bad size' });
  assert.equal(q('len(_bim_ifcos_file.by_type("IfcWall"))'), 0);
});

/* ---------------- WO-03 bim_ifcos_add_slab ---------------- */
test('WO-03 a slab from an outline, its depth, at z', () => {
  built('bim_ifcos_add_slab');
  const s0 = fresh();
  const r = call('bim_ifcos_add_slab', s0, 'Floor 1', [[0, 0], [6, 0], [6, 4], [0, 4]], -0.25, 0.25);
  assert.equal(typeof r.guid, 'string');
  near(place(r.guid)[2][3], -0.25);
  assert.equal(q(`_bim_ifcos_file.by_guid("${r.guid}").is_a()`), 'IfcSlab');
  near(q(`_bim_ifcos_file.by_guid("${r.guid}").Representation.Representations[0].Items[0].Depth`), 0.25);
  assert.equal(q(`ifcopenshell.util.element.get_container(_bim_ifcos_file.by_guid("${r.guid}")).GlobalId`), s0);
});
test('WO-03 a closed outline is accepted; the errors', () => {
  built('bim_ifcos_add_slab');
  const s0 = fresh();
  assert.equal(typeof call('bim_ifcos_add_slab', s0, 'F', [[0, 0], [3, 0], [3, 3], [0, 0]], 0, 0.2).guid, 'string');
  assert.deepEqual(call('bim_ifcos_add_slab', s0, 'F', [[0, 0], [3, 0]], 0, 0.2), { error: 'too few points' });
  assert.deepEqual(call('bim_ifcos_add_slab', s0, 'F', [[0, 0], [3, 0], [3, 3]], 0, 0), { error: 'bad size' });
  assert.deepEqual(call('bim_ifcos_add_slab', 'x', 'F', [[0, 0], [3, 0], [3, 3]], 0, 0.2), { error: 'no storey' });
});

/* ---------------- WO-04 bim_ifcos_add_column ---------------- */
test('WO-04 a rectangular column at its point, turned, its height', () => {
  built('bim_ifcos_add_column');
  const s0 = fresh();
  const r = call('bim_ifcos_add_column', s0, 'C1', 2, -3, 0, 0.4, 0.3, 3, Math.PI / 2);
  const M = place(r.guid);
  near(M[0][3], 2); near(M[1][3], -3); near(M[1][0], 1, 'sin');
  const p = q(`(lambda it: [it.SweptArea.XDim, it.SweptArea.YDim, it.Depth])(_bim_ifcos_file.by_guid("${r.guid}").Representation.Representations[0].Items[0])`);
  near(p[0], 0.4); near(p[1], 0.3); near(p[2], 3);
  assert.deepEqual(call('bim_ifcos_add_column', s0, 'C', 0, 0, 0, 0, 0.3, 3, 0), { error: 'bad size' });
});

/* ---------------- WO-05 bim_ifcos_add_opening ---------------- */
test('WO-05 a door: an opening voids the wall and the door fills it', () => {
  built('bim_ifcos_add_opening');
  const s0 = fresh();
  const w = call('bim_ifcos_add_wall_on', s0, 'W', 0, 0, 5, 0, 0, 3, 0.2, -0.1).guid;
  const r = call('bim_ifcos_add_opening', w, 'door', 'Door 1', 2, 0, 0.9, 2.1, 0.2, -0.1);
  assert.equal(q(`_bim_ifcos_file.by_guid("${r.guid}").is_a()`), 'IfcDoor');
  assert.equal(q(`_bim_ifcos_file.by_guid("${r.opening}").VoidsElements[0].RelatingBuildingElement.GlobalId`), w);
  assert.equal(q(`_bim_ifcos_file.by_guid("${r.guid}").FillsVoids[0].RelatingOpeningElement.GlobalId`), r.opening);
  near(q(`_bim_ifcos_file.by_guid("${r.guid}").OverallWidth`), 0.9);
  // the opening starts half its width before 'along', and passes through the wall (0.05 m each side)
  const M = place(r.opening);
  near(M[0][3], 1.55); near(M[1][3], -0.15); near(M[2][3], 0);
  near(q(`_bim_ifcos_file.by_guid("${r.opening}").Representation.Representations[0].Items[0].Depth`), 2.1);
  assert.equal(q(`ifcopenshell.util.element.get_container(_bim_ifcos_file.by_guid("${r.guid}")).GlobalId`), s0);
});
test('WO-05 a window in a turned wall, at its sill', () => {
  built('bim_ifcos_add_opening');
  const s0 = fresh();
  const w = call('bim_ifcos_add_wall_on', s0, 'W', 10, 0, 10, 6, 0, 3, 0.2, -0.1).guid;
  const r = call('bim_ifcos_add_opening', w, 'window', 'Window 1', 3, 0.9, 1.2, 1.0, 0.2, -0.1);
  assert.equal(q(`_bim_ifcos_file.by_guid("${r.guid}").is_a()`), 'IfcWindow');
  const M = place(r.opening);
  // the wall runs along +Y from (10, 0): along 3 - 0.6 = 2.4 up the line; -0.15 across it is +0.15 in X
  near(M[0][3], 10.15); near(M[1][3], 2.4); near(M[2][3], 0.9);
});
test('WO-05 the errors', () => {
  built('bim_ifcos_add_opening');
  const s0 = fresh();
  const w = call('bim_ifcos_add_wall_on', s0, 'W', 0, 0, 5, 0, 0, 3, 0.2, -0.1).guid;
  assert.deepEqual(call('bim_ifcos_add_opening', 'x', 'door', 'D', 2, 0, 0.9, 2.1, 0.2, -0.1), { error: 'no wall' });
  assert.deepEqual(call('bim_ifcos_add_opening', s0, 'door', 'D', 2, 0, 0.9, 2.1, 0.2, -0.1), { error: 'no wall' });
  assert.deepEqual(call('bim_ifcos_add_opening', w, 'hatch', 'D', 2, 0, 0.9, 2.1, 0.2, -0.1), { error: 'bad kind' });
  assert.deepEqual(call('bim_ifcos_add_opening', w, 'door', 'D', 2, 0, 0, 2.1, 0.2, -0.1), { error: 'bad size' });
  assert.equal(q('len(_bim_ifcos_file.by_type("IfcOpeningElement"))'), 0);
});

/* ---------------- WO-06 bim_ifcos_add_mesh ---------------- */
const TET = { v: [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], f: [[0, 2, 1], [0, 1, 3], [1, 2, 3], [0, 3, 2]] };
test('WO-06 a mesh as its class, or as a proxy when the class is not on the list', () => {
  built('bim_ifcos_add_mesh');
  const s0 = fresh();
  const a = call('bim_ifcos_add_mesh', s0, 'Roof 1', 'IfcRoof', TET.v, TET.f);
  const b = call('bim_ifcos_add_mesh', s0, 'Thing', 'IfcFlowTerminal', TET.v, TET.f);
  const c = call('bim_ifcos_add_mesh', s0, 'Thing 2', '', TET.v, TET.f);
  assert.equal(q(`_bim_ifcos_file.by_guid("${a.guid}").is_a()`), 'IfcRoof');
  assert.equal(q(`_bim_ifcos_file.by_guid("${b.guid}").is_a()`), 'IfcBuildingElementProxy');
  assert.equal(q(`_bim_ifcos_file.by_guid("${c.guid}").is_a()`), 'IfcBuildingElementProxy');
  assert.equal(q(`len(_bim_ifcos_file.by_guid("${a.guid}").Representation.Representations[0].Items)`), 1);
});
test('WO-06 the errors: empty, a face too short, an index out of range', () => {
  built('bim_ifcos_add_mesh');
  const s0 = fresh();
  assert.deepEqual(call('bim_ifcos_add_mesh', s0, 'M', '', [], []), { error: 'empty mesh' });
  assert.deepEqual(call('bim_ifcos_add_mesh', s0, 'M', '', TET.v, [[0, 1]]), { error: 'bad face' });
  assert.deepEqual(call('bim_ifcos_add_mesh', s0, 'M', '', TET.v, [[0, 1, 4]]), { error: 'bad face' });
  assert.deepEqual(call('bim_ifcos_add_mesh', 'x', 'M', '', TET.v, TET.f), { error: 'no storey' });
});

/* ---------------- WO-07 bim_ifcos_add_pset ---------------- */
test('WO-07 a property set with its plain values; others left out', () => {
  built('bim_ifcos_add_pset');
  const s0 = fresh();
  const w = call('bim_ifcos_add_wall_on', s0, 'W', 0, 0, 5, 0, 0, 3, 0.2, -0.1).guid;
  const r = call('bim_ifcos_add_pset', w, 'BIM_Personal', { Material: 'Concrete', FireRating: 2, LoadBearing: true, Skip: null, List: [1] });
  assert.deepEqual(r, { count: 3 });
  assert.deepEqual(q(`ifcopenshell.util.element.get_psets(_bim_ifcos_file.by_guid("${w}"))["BIM_Personal"]["Material"]`), 'Concrete');
  assert.deepEqual(call('bim_ifcos_add_pset', 'x', 'P', { a: 1 }), { error: 'no element' });
  assert.deepEqual(call('bim_ifcos_add_pset', w, '', { a: 1 }), { error: 'bad pset' });
});

/* ---------------- WO-08 bim_ifcos_save_model ---------------- */
const MODEL = {
  name: 'House',
  levels: [{ id: 'L0', name: 'Ground', elevation: 0 }, { id: 'L1', name: 'First', elevation: 3 }],
  walls: [
    { id: 'w1', name: 'Wall 1', level: 'L0', x0: 0, y0: 0, x1: 6, y1: 0, z: 0, height: 3, thickness: 0.2, offset: -0.1 },
    { id: 'w2', name: 'Wall 2', level: 'L1', x0: 0, y0: 0, x1: 0, y1: 4, z: 3, height: 3, thickness: 0.2, offset: -0.1 },
    { id: 'w3', name: 'Bad', level: 'L0', x0: 1, y0: 1, x1: 1, y1: 1, z: 0, height: 3, thickness: 0.2, offset: -0.1 }
  ],
  slabs: [{ id: 's1', name: 'Floor 1', level: 'L1', points: [[0, 0], [6, 0], [6, 4], [0, 4]], z: 2.8, depth: 0.2 }],
  columns: [{ id: 'c1', name: 'Column 1', level: 'L0', x: 3, y: 2, z: 0, width: 0.3, depth: 0.3, height: 3, rotation: 0 }],
  openings: [
    { id: 'd1', name: 'Door 1', kind: 'door', wall: 'w1', along: 2, sill: 0, width: 0.9, height: 2.1 },
    { id: 'd2', name: 'Lost', kind: 'door', wall: 'w3', along: 0, sill: 0, width: 0.9, height: 2.1 }
  ],
  meshes: [{ id: 'm1', name: 'Roof 1', level: 'L1', ifcClass: 'IfcRoof', vertices: TET.v, faces: TET.f }],
  psets: [{ id: 'w1', name: 'BIM_Personal', props: { AppId: 'w1' } }]
};
test('WO-08 a whole model saved, read back, every element counted', () => {
  built('bim_ifcos_save_model');
  const r = call('bim_ifcos_save_model', MODEL, '/tmp/v177-house.ifc');
  assert.ok(r.bytes > 1000);
  assert.deepEqual(r.summary.storeys, [{ name: 'Ground', elevation: 0 }, { name: 'First', elevation: 3 }]);
  assert.deepEqual(r.summary.products, { IfcBuilding: 1, IfcBuildingStorey: 2, IfcColumn: 1, IfcDoor: 1, IfcRoof: 1, IfcSite: 1, IfcSlab: 1, IfcWall: 2 });
  assert.deepEqual(Object.keys(r.guids).sort(), ['c1', 'd1', 'm1', 's1', 'w1', 'w2']);
  assert.deepEqual(r.skipped.sort(), ['d2', 'w3']);
  assert.equal(q(`ifcopenshell.util.element.get_container(_bim_ifcos_file.by_guid("${r.guids.w2}")).Name`), 'First');
  assert.equal(q(`ifcopenshell.util.element.get_psets(_bim_ifcos_file.by_guid("${r.guids.w1}"))["BIM_Personal"]["AppId"]`), 'w1');
});
test('WO-08 no levels: one storey, Level 0; an unknown level goes to the first; not a model', () => {
  built('bim_ifcos_save_model');
  const r = call('bim_ifcos_save_model', { name: 'Bare', walls: [{ id: 'w', name: 'W', level: 'nowhere', x0: 0, y0: 0, x1: 2, y1: 0, z: 0, height: 3, thickness: 0.2, offset: -0.1 }] }, '/tmp/v177-bare.ifc');
  assert.deepEqual(r.summary.storeys, [{ name: 'Level 0', elevation: 0 }]);
  assert.equal(r.summary.products.IfcWall, 1);
  assert.deepEqual(call('bim_ifcos_save_model', 'nope', '/tmp/x.ifc'), { error: 'bad model' });
});
