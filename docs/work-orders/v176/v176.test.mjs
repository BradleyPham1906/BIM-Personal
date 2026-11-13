// V176, IfcOpenShell in the browser's Python (docs/work-orders/v176/SPEC.md): the app's own Pyodide (runtime/pyodide/
// 0.29.5) with IfcOpenShell's WebAssembly wheel (LGPL-3.0, unchanged) and its dependencies, each pinned by SHA-256 and
// kept in .cache/ifcos/ (not committed; fetched once), running the app's adapter src/py/bim_ifcos.py. Outside `npm test`
// until V177 pins the wheels in runtime/: the first run needs the network.
//
//   node --test docs/work-orders/v176/v176.test.mjs
//   node --test --test-name-pattern="WO-01" docs/work-orders/v176/v176.test.mjs
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
  py.runPython(fs.readFileSync(path.join(ROOT, 'src', 'py', 'bim_ifcos.py'), 'utf8'));
  T.adapter = Date.now() - t;
  console.log('# times (ms): boot ' + T.boot + ', install ' + T.install + ', import ifcopenshell ' + T.import + ', the adapter ' + T.adapter);
});

// millimetres; a wall 4 m long, 200 mm thick, 3 m high on a storey at 3.5 m, with a 1 m by 1.2 m opening
// (the same file as tests/unit/ifc-full.test.mjs)
const IFC = fs.readFileSync(path.join(ROOT, 'tests', 'unit', 'ifc-full.test.mjs'), 'utf8').match(/const IFC = `([\s\S]*?)`;/)[1];

test('setup: the pinned IfcOpenShell imports in the app\'s own Pyodide', () => {
  // the wheel's own metadata carries its version (0.9's wasm build said ifcopenshell.version == '0.0.0')
  assert.equal(py.runPython('import importlib.metadata\nimportlib.metadata.version("ifcopenshell")'), '0.8.5');
  assert.ok(T.import < 60000, 'imported in under a minute (' + T.import + ' ms)');
});

test('WO-01 bim_ifcos_summary: an IFC file\'s schema, its elements by class and its storeys in metres', () => {
  py.FS.writeFile('/tmp/t.ifc', IFC);
  const s = call('bim_ifcos_summary', '/tmp/t.ifc');
  assert.equal(s.schema, 'IFC4');
  assert.deepEqual(s.products, { IfcBuilding: 1, IfcBuildingStorey: 1, IfcSite: 1, IfcWall: 1 }, 'openings are not counted');
  assert.deepEqual(s.storeys, [{ name: 'Level 1', elevation: 3.5 }]);
  assert.deepEqual(call('bim_ifcos_summary', '/tmp/none.ifc'), { error: 'not found' });
});

test('WO-02 bim_ifcos_new_project: a new IFC4 project with a site, a building, a storey and a body context', () => {
  const s = call('bim_ifcos_new_project', 'Test project', 0);
  assert.equal(s.schema, 'IFC4');
  assert.deepEqual(s.products, { IfcBuilding: 1, IfcBuildingStorey: 1, IfcSite: 1 });
  assert.deepEqual(s.storeys, [{ name: 'Level 0', elevation: 0 }]);
  assert.equal(py.runPython('_bim_ifcos_file.by_type("IfcProject")[0].Name'), 'Test project');
  assert.equal(py.runPython('len([c for c in _bim_ifcos_file.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier == "Body"])'), 1);
  assert.equal(py.runPython('round(ifcopenshell.util.unit.calculate_unit_scale(_bim_ifcos_file), 6)'), 1, 'lengths in metres');
});

test('WO-03 bim_ifcos_add_wall: a wall from one point to another, on the storey, its length, height and thickness', () => {
  call('bim_ifcos_new_project', 'Walls', 0);
  const w = call('bim_ifcos_add_wall', 'Wall A', 1, 2, 5, 2, 3, 0.2);
  assert.match(w.guid, /^[0-9A-Za-z_$]{22}$/);
  const s = call('bim_ifcos_summary', '');
  assert.equal(s.products.IfcWall, 1);
  const pl = JSON.parse(py.runPython(`import json\nw = _bim_ifcos_file.by_guid(${JSON.stringify(w.guid)})\nm = ifcopenshell.util.placement.get_local_placement(w.ObjectPlacement)\njson.dumps([round(float(m[0][3]), 6), round(float(m[1][3]), 6), round(float(m[0][0]), 6), round(float(m[1][0]), 6), ifcopenshell.util.element.get_container(w).Name])`));
  assert.deepEqual(pl, [1, 2, 1, 0, 'Level 0'], 'starts at (1, 2), runs along +X, on Level 0');
  const w2 = call('bim_ifcos_add_wall', 'Wall B', 0, 0, 0, 4, 3, 0.2);
  const d = JSON.parse(py.runPython(`import json\nm = ifcopenshell.util.placement.get_local_placement(_bim_ifcos_file.by_guid(${JSON.stringify(w2.guid)}).ObjectPlacement)\njson.dumps([round(float(m[0][0]), 6), round(float(m[1][0]), 6)])`));
  assert.deepEqual(d, [0, 1], 'a wall along +Y is turned a quarter turn');
  assert.deepEqual(call('bim_ifcos_add_wall', 'Zero', 1, 1, 1, 1, 3, 0.2), { error: 'zero length' });
});

test('WO-04 bim_ifcos_write_read: the project written as IFC text and read back the same', () => {
  call('bim_ifcos_new_project', 'Round trip', 0);
  call('bim_ifcos_add_wall', 'Wall A', 0, 0, 6, 0, 3, 0.25);
  const r = call('bim_ifcos_write_read', '/tmp/out.ifc');
  assert.ok(r.bytes > 500, 'a file was written (' + r.bytes + ' bytes)');
  assert.ok(py.FS.readFile('/tmp/out.ifc', { encoding: 'utf8' }).startsWith('ISO-10303-21;'));
  assert.deepEqual(r.summary.products, { IfcBuilding: 1, IfcBuildingStorey: 1, IfcSite: 1, IfcWall: 1 });
  assert.deepEqual(r.summary.storeys, [{ name: 'Level 0', elevation: 0 }]);
});
