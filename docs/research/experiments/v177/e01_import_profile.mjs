// V177 e01: where the 25 s of `import ifcopenshell` (0.8.5, Pyodide 0.29.5) go, in Node. The wheels are V176's
// pinned ones in .cache/ifcos/ (run docs/work-orders/v176/v176.test.mjs once to fetch them).
//   node docs/research/experiments/v177/e01_import_profile.mjs
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
// time every WebAssembly compile and instantiate over 1 MB
const T = { compile: 0, inst: 0, n: 0 };
const M0 = WebAssembly.Module, I0 = WebAssembly.Instance;
WebAssembly.Module = function (b) { const t = Date.now(); const m = new M0(b); if (b.byteLength > 1e6) { T.compile += Date.now() - t; T.n++; console.log('sync compile', b.byteLength, Date.now() - t, 'ms'); } return m; };
WebAssembly.Module.prototype = M0.prototype; Object.setPrototypeOf(WebAssembly.Module, M0);
WebAssembly.Instance = function (m, i) { const t = Date.now(); const r = new I0(m, i); const d = Date.now() - t; if (d > 50) { T.inst += d; console.log('sync instantiate', d, 'ms'); } return r; };
WebAssembly.Instance.prototype = I0.prototype;
const c0 = WebAssembly.compile; WebAssembly.compile = async function (b) { const t = Date.now(); const m = await c0.call(WebAssembly, b); if (b.byteLength > 1e6) console.log('async compile', b.byteLength, Date.now() - t, 'ms'); return m; };
const { loadPyodide } = createRequire(import.meta.url)(path.join(RT, 'pyodide.js'));
const py = await loadPyodide({ indexURL: RT + path.sep });
await py.loadPackage('numpy');
for (const f of WHEELS) { const b = fs.readFileSync(path.join(CACHE, f)); py.unpackArchive(new Uint8Array(b.buffer, b.byteOffset, b.byteLength), 'wheel'); }
const step = (label, code) => { const t = Date.now(); py.runPython(code); console.log(label, Date.now() - t, 'ms'); };
step('import shapely', 'import shapely');
step('import the wrapper (.so)', 'import ifcopenshell.ifcopenshell_wrapper');
step('import ifcopenshell', 'import ifcopenshell');
step('import api + util', 'import ifcopenshell.api, ifcopenshell.api.project, ifcopenshell.api.root, ifcopenshell.api.unit, ifcopenshell.api.context, ifcopenshell.api.aggregate, ifcopenshell.api.geometry, ifcopenshell.api.spatial, ifcopenshell.util.element, ifcopenshell.util.placement, ifcopenshell.util.unit');
step('create_file IFC4', 'f = ifcopenshell.api.project.create_file(version="IFC4")');
console.log(JSON.stringify(T));
