// V177 e05: the ifcopenshell.api calls Save as IFC will name, run once each in the app's Pyodide (0.8.5).
//   node --liftoff-only docs/research/experiments/v177/e05_api_calls.mjs
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..');
const RT = path.join(ROOT, 'runtime', 'pyodide', '0.29.5');
const CACHE = process.env.IFCOS_CACHE || path.join(ROOT, '.cache', 'ifcos');
const WHEELS = ['six-1.17.0-py2.py3-none-any.whl', 'python_dateutil-2.9.0.post0-py2.py3-none-any.whl', 'typing_extensions-4.15.0-py3-none-any.whl',
  'shapely-2.0.7-cp313-cp313-pyemscripten_2025_0_wasm32.whl', 'isodate-0.7.2-py3-none-any.whl', 'lark-1.3.1-py3-none-any.whl',
  'ifcopenshell-0.8.5-cp313-cp313-pyodide_2025_0_wasm32.whl'];
const { loadPyodide } = createRequire(import.meta.url)(path.join(RT, 'pyodide.js'));
const py = await loadPyodide({ indexURL: RT + path.sep });
await py.loadPackage('numpy');
for (const f of WHEELS) { const b = fs.readFileSync(path.join(CACHE, f)); py.unpackArchive(new Uint8Array(b.buffer, b.byteOffset, b.byteLength), 'wheel'); }
py.runPython(fs.readFileSync(path.join(ROOT, 'src', 'py', 'bim_ifcos.py'), 'utf8'));
const steps = [
  ['more imports', 'import ifcopenshell.api.feature, ifcopenshell.api.pset, ifcopenshell.api.attribute, ifcopenshell.guid, ifcopenshell.util.shape_builder'],
  ['project + wall', 'bim_ifcos_new_project("E05", 0)\nw = bim_ifcos_add_wall("W", 0, 0, 5, 0, 3, 0.2)\nf = _bim_ifcos_file\nwall = f.by_guid(w["guid"])\nstorey = f.by_type("IfcBuildingStorey")[0]\nbody = [c for c in f.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier == "Body"][0]'],
  ['second storey', 's2 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Level 1")\ns2.Elevation = 3.0\nifcopenshell.api.aggregate.assign_object(f, products=[s2], relating_object=f.by_type("IfcBuilding")[0])\nifcopenshell.api.geometry.edit_object_placement(f, product=s2, matrix=numpy.array([[1,0,0,0],[0,1,0,0],[0,0,1,3.0],[0,0,0,1]], dtype=float))'],
  ['slab polyline', 'slab = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSlab", name="S")\nr = ifcopenshell.api.geometry.add_slab_representation(f, context=body, depth=0.2, polyline=[(0.0,0.0),(5.0,0.0),(5.0,4.0),(0.0,4.0)])\nifcopenshell.api.geometry.assign_representation(f, product=slab, representation=r)\nifcopenshell.api.geometry.edit_object_placement(f, product=slab, matrix=numpy.eye(4))\nifcopenshell.api.spatial.assign_container(f, products=[slab], relating_structure=storey)'],
  ['opening', 'op = ifcopenshell.api.root.create_entity(f, ifc_class="IfcOpeningElement", name="O")\nr = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=0.9, height=2.1, thickness=0.4)\nifcopenshell.api.geometry.assign_representation(f, product=op, representation=r)\nifcopenshell.api.geometry.edit_object_placement(f, product=op, matrix=numpy.array([[1,0,0,2.0],[0,1,0,-0.1],[0,0,1,0],[0,0,0,1]], dtype=float))\nifcopenshell.api.feature.add_feature(f, feature=op, element=wall)'],
  ['door', 'door = ifcopenshell.api.root.create_entity(f, ifc_class="IfcDoor", name="D")\nr = ifcopenshell.api.geometry.add_door_representation(f, context=body, overall_height=2.1, overall_width=0.9)\nifcopenshell.api.geometry.assign_representation(f, product=door, representation=r)\nifcopenshell.api.geometry.edit_object_placement(f, product=door, matrix=numpy.array([[1,0,0,2.0],[0,1,0,0],[0,0,1,0],[0,0,0,1]], dtype=float))\nifcopenshell.api.feature.add_filling(f, opening=op, element=door)\nifcopenshell.api.spatial.assign_container(f, products=[door], relating_structure=storey)'],
  ['window', 'win = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWindow", name="Wi")\nr = ifcopenshell.api.geometry.add_window_representation(f, context=body, overall_height=1.2, overall_width=1.0)\nifcopenshell.api.geometry.assign_representation(f, product=win, representation=r)'],
  ['mesh', 'px = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingElementProxy", name="M")\nr = ifcopenshell.api.geometry.add_mesh_representation(f, context=body, vertices=[[(0.0,0.0,0.0),(1.0,0.0,0.0),(0.0,1.0,0.0),(0.0,0.0,1.0)]], faces=[[(0,2,1),(0,1,3),(1,2,3),(0,3,2)]])\nifcopenshell.api.geometry.assign_representation(f, product=px, representation=r)\nifcopenshell.api.spatial.assign_container(f, products=[px], relating_structure=storey)'],
  ['column (slab call as a box)', 'col = ifcopenshell.api.root.create_entity(f, ifc_class="IfcColumn", name="C")\nr = ifcopenshell.api.geometry.add_slab_representation(f, context=body, depth=3.0, polyline=[(-0.2,-0.2),(0.2,-0.2),(0.2,0.2),(-0.2,0.2)])\nifcopenshell.api.geometry.assign_representation(f, product=col, representation=r)'],
  ['pset', 'ps = ifcopenshell.api.pset.add_pset(f, product=wall, name="BIMPersonal")\nifcopenshell.api.pset.edit_pset(f, pset=ps, properties={"Layer": "Walls", "Thickness": 0.2})'],
  ['guid kept', 'wall.GlobalId = "2O2Fr$t4X7Zf8NOew3FLOH"\nassert f.by_guid("2O2Fr$t4X7Zf8NOew3FLOH") == wall'],
  ['new guid', 'g = ifcopenshell.guid.new(); assert len(g) == 22'],
  ['write + read', 'f.write("/tmp/e05.ifc")\ng = ifcopenshell.open("/tmp/e05.ifc")\nimport json\nout = json.dumps([sorted(set(e.is_a() for e in g.by_type("IfcProduct"))), len(g.by_type("IfcRelVoidsElement")), len(g.by_type("IfcRelFillsElement")), [s.Name for s in g.by_type("IfcBuildingStorey")], ifcopenshell.util.element.get_psets(g.by_guid("2O2Fr$t4X7Zf8NOew3FLOH")).get("BIMPersonal")])'],
  ['geom of the slab (kernel)', 'import ifcopenshell.geom\nst = ifcopenshell.geom.settings()\nsh = ifcopenshell.geom.create_shape(st, g.by_type("IfcSlab")[0])\nnv = len(sh.geometry.verts) // 3'],
  ['geom of the wall with its opening', 'sh = ifcopenshell.geom.create_shape(st, g.by_type("IfcWall")[0])\nnw = len(sh.geometry.verts) // 3'],
];
for (const [label, code] of steps) {
  const t = Date.now();
  try { py.runPython(code); console.log('ok  ', label, Date.now() - t, 'ms'); }
  catch (x) { console.log('FAIL', label, String(x.message).trim().split('\n').slice(-2).join(' | ')); }
}
try { console.log(py.runPython('out'), 'slab verts', py.runPython('nv'), 'wall verts', py.runPython('nw'), 'bytes', py.runPython('import os\nos.path.getsize("/tmp/e05.ifc")')); } catch (x) { console.log(String(x.message).split('\n').slice(-2)[0]); }
