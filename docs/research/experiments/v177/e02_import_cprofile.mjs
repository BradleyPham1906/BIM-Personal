// V177 e02: Python's own profile of the import (cProfile, by cumulative time), and of the api and util imports.
//   node docs/research/experiments/v177/e02_import_cprofile.mjs
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
const prof = (code) => py.runPython(`
import cProfile, pstats, io
pr = cProfile.Profile(); pr.enable()
${code}
pr.disable()
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats('cumulative').print_stats(${process.env.N || 28})
s.getvalue()`);
console.log(prof('import ifcopenshell'));
console.log(prof('import ifcopenshell.api, ifcopenshell.api.project, ifcopenshell.api.root, ifcopenshell.api.unit, ifcopenshell.api.context, ifcopenshell.api.aggregate, ifcopenshell.api.geometry, ifcopenshell.api.spatial, ifcopenshell.util.element, ifcopenshell.util.placement, ifcopenshell.util.unit'));
