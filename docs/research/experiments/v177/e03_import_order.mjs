// V177 e03: the same import with numpy, datetime and shapely imported first, step by step; run it under V8 flags
// to see what the time depends on.
//   node [--no-wasm-lazy-compilation | --liftoff-only | --no-liftoff] docs/research/experiments/v177/e03_import_order.mjs
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
let t = Date.now();
const py = await loadPyodide({ indexURL: RT + path.sep });
await py.loadPackage('numpy');
for (const f of WHEELS) { const b = fs.readFileSync(path.join(CACHE, f)); py.unpackArchive(new Uint8Array(b.buffer, b.byteOffset, b.byteLength), 'wheel'); }
console.log('boot + unpack', Date.now() - t, 'ms');
const out = [];
const step = (label, code) => { const t = Date.now(); py.runPython(code); out.push(label + ' ' + (Date.now() - t)); };
step('datetime', 'import datetime');
step('numpy', 'import numpy');
step('shapely', 'import shapely');
step('wrapper.so', 'import ifcopenshell._ifcopenshell_wrapper as W');
step('schema_names', 'W.schema_names()');
step('schema_names again', 'W.schema_names()');
step('ifcopenshell', 'import ifcopenshell');
step('api+util', 'import ifcopenshell.api, ifcopenshell.api.project, ifcopenshell.api.root, ifcopenshell.api.unit, ifcopenshell.api.context, ifcopenshell.api.aggregate, ifcopenshell.api.geometry, ifcopenshell.api.spatial, ifcopenshell.util.element, ifcopenshell.util.placement, ifcopenshell.util.unit');
step('create_file', 'f = ifcopenshell.api.project.create_file(version="IFC4")');
step('create_file again', 'f = ifcopenshell.api.project.create_file(version="IFC4")');
console.log(process.execArgv.join(' ') || '(no flags)', '|', out.join(', '), 'ms');
