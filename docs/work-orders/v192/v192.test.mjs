/* V192's work-order tests (docs/work-orders/v192/SPEC.md, WO-01 to WO-06): the pure functions of src/js/engine/map/facade-rectify.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v192/v192.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v192/v192.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimFacSolve", "bimFacNorm", "bimFacMul", "bimFacApply", "bimFacHomography", "bimFacError"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/map/facade-rectify.js'), 'utf8');
  if (process.env.V192_REF) src += fs.readFileSync(process.env.V192_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/map/facade-rectify.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const HT = [[1.2, 0.1, 30], [-0.05, 0.9, 10], [0.0004, 0.0002, 1]];
const ap = (H, p) => { const w = H[2][0] * p[0] + H[2][1] * p[1] + H[2][2]; return [(H[0][0] * p[0] + H[0][1] * p[1] + H[0][2]) / w, (H[1][0] * p[0] + H[1][1] * p[1] + H[1][2]) / w]; };
const SRC = [[0, 0], [400, 20], [380, 300], [10, 280], [200, 150], [100, 60]];
test('WO-01 a linear system by Gaussian elimination with partial pivoting', () => {
  const x = fn('bimFacSolve')([[0, 2, 1], [1, 1, 1], [2, 1, 3]], [5, 5, 12]);
  near(x[0], 1, 1e-12); near(x[1], 1, 1e-12); near(x[2], 3, 1e-12);
  assert.equal(fn('bimFacSolve')([[1, 2], [2, 4]], [1, 2]), null);
});
test('WO-02 Hartley normalisation: centroid to the origin, mean distance sqrt 2', () => {
  const T = fn('bimFacNorm')([[0, 0], [2, 0], [2, 2], [0, 2]]);
  near(T[0][0], 1, 1e-12); near(T[0][2], -1, 1e-12); near(T[1][2], -1, 1e-12); assert.deepEqual(T[2], [0, 0, 1]);
});
test('WO-03 3x3 matrix product', () => {
  assert.deepEqual(fn('bimFacMul')([[1, 2, 0], [0, 1, 0], [0, 0, 1]], [[1, 0, 3], [0, 1, 4], [0, 0, 1]]), [[1, 2, 11], [0, 1, 4], [0, 0, 1]]);
});
test('WO-04 a point through a homography, divided by w', () => {
  assert.deepEqual(fn('bimFacApply')([[2, 0, 1], [0, 2, 1], [0, 0, 2]], [3, 4]), [3.5, 4.5]);
});
test('WO-05 the homography from point pairs recovers a known one; too few pairs give null', () => {
  const H = fn('bimFacHomography')(SRC, SRC.map((p) => ap(HT, p)));
  for (const p of [[50, 50], [350, 250]]) { const a = ap(HT, p), b = ap(H, p); near(a[0], b[0], 1e-6); near(a[1], b[1], 1e-6); }
  near(H[2][2], 1, 1e-12);
  assert.equal(fn('bimFacHomography')(SRC.slice(0, 3), SRC.slice(0, 3)), null);
});
test('WO-06 check-point error: RMS and the largest distance', () => {
  const I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  assert.deepEqual(fn('bimFacError')(I, [[0, 0], [1, 1]], [[3, 4], [1, 1]]), { rms: Math.sqrt(12.5), max: 5 });
  assert.deepEqual(fn('bimFacError')(I, [], []), { rms: 0, max: 0 });
});
