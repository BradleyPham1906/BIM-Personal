/* V207's work-order tests (docs/work-orders/v207/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/assets/gltf-assets.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v207/v207.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v207/v207.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimAstGltfStats", "bimAstFitBox", "bimAstCheck", "bimAstCredit"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/assets/gltf-assets.js'), 'utf8');
  if (process.env.V207_REF) src += fs.readFileSync(process.env.V207_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/assets/gltf-assets.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const G = { extensionsUsed: ['KHR_materials_unlit', 'KHR_draco_mesh_compression'], accessors: [{ count: 300 }, { count: 36 }, { count: 9 }],
  meshes: [{ primitives: [{ attributes: { POSITION: 0 }, indices: 1 }, { attributes: { POSITION: 2 } }, { mode: 1, attributes: { POSITION: 0 } }] }], materials: [{}, {}], textures: [{}] };
test('WO-01 a glTF\'s counts from its JSON: triangles from indices, else positions; lines left out', () => {
  assert.deepEqual(fn('bimAstGltfStats')(G), { meshes: 1, primitives: 3, triangles: 15, materials: 2, textures: 1, extensions: ['KHR_draco_mesh_compression', 'KHR_materials_unlit'] });
  assert.equal(fn('bimAstGltfStats')(null), null);
  assert.deepEqual(fn('bimAstGltfStats')({}).triangles, 0);
});
test('WO-02 a model seated on the origin: centred in plan, its base at 0, scaled to a size', () => {
  assert.deepEqual(fn('bimAstFitBox')([-1, 2, 0], [3, 4, 2], 0), { scale: 1, move: [-1, -2, -1], size: [4, 2, 2] });
  assert.deepEqual(fn('bimAstFitBox')([0, 0, 0], [4, 2, 2], 2), { scale: 0.5, move: [-1, 0, -0.5], size: [2, 1, 1] });
});
test('WO-03 the limits that ask before a model is added', () => {
  assert.deepEqual(fn('bimAstCheck')({ triangles: 250000 }, 31457280), ['250000 triangles, over 200000', '30 MB, over 20 MB']);
  assert.deepEqual(fn('bimAstCheck')({ triangles: 10 }, 1000, { triangles: 5 }), ['10 triangles, over 5']);
  assert.deepEqual(fn('bimAstCheck')(null, 0), ['not a glTF file']);
});
test('WO-04 the credit line for THIRD_PARTY_NOTICES and the Assets card', () => {
  assert.equal(fn('bimAstCredit')({ title: 'Sedan', author: 'valdrada', license: 'CC BY 4.0', source: 'github.com/valdrada' }), '"Sedan" by valdrada, CC BY 4.0 (github.com/valdrada)');
  assert.equal(fn('bimAstCredit')({}), '"Untitled"');
});
