/* V218's work-order tests (docs/work-orders/v218/SPEC.md, WO-01 to WO-03): the pure functions of src/js/engine/map/tiles3d.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v218/v218.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v218/v218.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimTilesSse", "bimTilesDist", "bimTilesSelect"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/map/tiles3d.js'), 'utf8');
  if (process.env.V218_REF) src += fs.readFileSync(process.env.V218_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/map/tiles3d.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 screen-space error in pixels (3D Tiles: geometric error over distance, by the view)', () => {
  near(fn('bimTilesSse')(10, 100, 1000, Math.PI / 2), 50, 1e-9);
  assert.equal(fn('bimTilesSse')(10, 0, 1000, 1), Infinity);
});
test('WO-02 distance from the eye to a bounding sphere, 0 inside', () => {
  assert.equal(fn('bimTilesDist')([0, 0, 0, 10], [30, 40, 0]), 40);
  assert.equal(fn('bimTilesDist')([0, 0, 0, 10], [1, 1, 1]), 0);
});
const TS = { geometricError: 100, refine: 'REPLACE', boundingVolume: { sphere: [0, 0, 0, 100] }, content: { uri: 'root.glb' },
  children: [{ geometricError: 10, boundingVolume: { sphere: [0, 0, 0, 50] }, content: { uri: 'a.glb' } },
             { geometricError: 10, refine: 'ADD', boundingVolume: { sphere: [1000, 0, 0, 50] }, content: { uri: 'b.glb' }, children: [{ geometricError: 0, boundingVolume: { sphere: [1000, 0, 0, 10] }, content: { uri: 'b1.glb' } }] }] };
test('WO-03 tiles to draw: refined until the error is small enough; REPLACE drops the parent, ADD keeps it', () => {
  assert.deepEqual(fn('bimTilesSelect')(TS, [0, 0, 5000], 1000, Math.PI / 2, 16), ['root.glb']);
  assert.deepEqual(fn('bimTilesSelect')(TS, [0, 0, 200], 1000, Math.PI / 2, 16), ['a.glb', 'b.glb']);
  assert.deepEqual(fn('bimTilesSelect')(TS, [1000, 0, 80], 1000, Math.PI / 2, 16), ['a.glb', 'b.glb', 'b1.glb']);
});
