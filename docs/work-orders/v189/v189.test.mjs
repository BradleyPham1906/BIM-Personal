/* V189's work-order tests (docs/work-orders/v189/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/drawing/make2d.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v189/v189.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v189/v189.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimM2Project", "bimM2Edges", "bimM2Hidden", "bimM2Visible"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/drawing/make2d.js'), 'utf8');
  if (process.env.V189_REF) src += fs.readFileSync(process.env.V189_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/drawing/make2d.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const TOP = { right: [1, 0, 0], up: [0, 1, 0], dir: [0, 0, -1] };
const CUBE = { v: [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]],
  f: [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]] };
test('WO-01 a point in the view: right, up and depth along the view direction', () => {
  assert.deepEqual(fn('bimM2Project')([2, 3, 4], TOP), [2, 3, -4]);
  assert.deepEqual(fn('bimM2Project')([2, 3, 4], { right: [0, 1, 0], up: [0, 0, 1], dir: [1, 0, 0] }), [3, 4, 2]);
});
test('WO-02 the edges a drawing keeps: boundaries, silhouettes and creases', () => {
  const e = fn('bimM2Edges')(CUBE, [0, 0, -1], 30);
  assert.equal(e.length, 12, 'every cube edge is a 90 degree crease or a silhouette');
  assert.equal(e.filter((x) => x[2] === 'silhouette').length, 4, 'the top face faces the eye, the sides are edge-on: its 4 edges');
  const sheet = fn('bimM2Edges')({ v: [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], f: [[0, 1, 2], [0, 2, 3]] }, [0, 0, -1]);
  assert.deepEqual(sheet.map((x) => x[2]).sort(), ['boundary', 'boundary', 'boundary', 'boundary']);
});
const SLAB = [[[0, 0, 2], [4, 0, 2], [4, 4, 2]], [[0, 0, 2], [4, 4, 2], [0, 4, 2]]];
test('WO-03 a point is hidden when a triangle covers it nearer the eye', () => {
  assert.equal(fn('bimM2Hidden')([1, 2, 0], SLAB, TOP), true, 'under the slab, seen from above');
  assert.equal(fn('bimM2Hidden')([1, 2, 3], SLAB, TOP), false, 'above it');
  assert.equal(fn('bimM2Hidden')([6, 2, 0], SLAB, TOP), false, 'beside it');
  assert.equal(fn('bimM2Hidden')([4, 4, 2], SLAB, TOP), false, 'on its own corner');
});
test('WO-04 an edge cut to its visible runs, in view coordinates', () => {
  const v = fn('bimM2Visible')([-2, 2, 0], [6, 2, 0], SLAB, TOP, 8);
  assert.deepEqual(v, [[[-2, 2], [0, 2]], [[4, 2], [6, 2]]]);
  assert.deepEqual(fn('bimM2Visible')([-2, 2, 3], [6, 2, 3], SLAB, TOP, 4), [[[-2, 2], [6, 2]]]);
  assert.deepEqual(fn('bimM2Visible')([1, 1, 0], [3, 1, 0], SLAB, TOP), []);
});
