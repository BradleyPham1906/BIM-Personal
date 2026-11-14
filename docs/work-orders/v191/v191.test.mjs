/* V191's work-order tests (docs/work-orders/v191/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/map/roofs-lidar.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v191/v191.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v191/v191.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimRoofJacobi", "bimRoofPlane", "bimRoofInRing", "bimRoofCoverage", "bimRoofZ"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/map/roofs-lidar.js'), 'utf8');
  if (process.env.V191_REF) src += fs.readFileSync(process.env.V191_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/map/roofs-lidar.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// a roof plane z = 10 + 0.5 x - 0.25 y sampled on a grid, with and without known noise
const grid = (noise) => { const p = []; let s = 1; for (let i = 0; i < 10; i++) for (let j = 0; j < 10; j++) { s = (s * 16807) % 2147483647; const e = noise ? (s / 2147483647 < 0.5 ? -noise : noise) : 0; p.push([i, j, 10 + 0.5 * i - 0.25 * j + e]); } return p; };
test('WO-01 Jacobi eigenvalues and vectors of a symmetric 3x3', () => {
  const e = fn('bimRoofJacobi')([[2, 1, 0], [1, 2, 0], [0, 0, 5]]);
  const v = e.values.slice().sort((a, b) => a - b);
  near(v[0], 1, 1e-12); near(v[1], 3, 1e-12); near(v[2], 5, 1e-12);
  const i = e.values.findIndex((x) => Math.abs(x - 1) < 1e-9), u = e.vectors[i];
  near(Math.abs(u[0]), Math.SQRT1_2, 1e-9); near(Math.abs(u[1]), Math.SQRT1_2, 1e-9); near(u[0] * u[1], -0.5, 1e-9);
});
test('WO-02 a least-squares plane: exact without noise, RMS equal to the noise with it', () => {
  const p = fn('bimRoofPlane')(grid(0)), want = [-0.5, 0.25, 1].map((x) => x / Math.sqrt(1.3125));
  for (let k = 0; k < 3; k++) near(p.n[k], want[k], 1e-9);
  near(p.rms, 0, 1e-9);
  near(fn('bimRoofPlane')(grid(0.05)).rms, 0.05 / Math.sqrt(1.3125), 0.001, 'vertical noise 0.05 measured square to the plane, within 2%');
  assert.equal(fn('bimRoofPlane')([[0, 0, 0], [1, 0, 0]]), null);
});
const RING = [[0, 0], [9, 0], [9, 9], [0, 9]];
test('WO-03 points inside a footprint (plan x, y)', () => {
  assert.deepEqual(fn('bimRoofInRing')([[1, 1, 5], [10, 1, 5], [8.9, 8.9, 1]], RING), [[1, 1, 5], [8.9, 8.9, 1]]);
});
test('WO-04 coverage: the share of footprint cells with a point', () => {
  near(fn('bimRoofCoverage')(grid(0), RING, 1), 81 / 81);
  const half = grid(0).filter((q) => q[0] < 4.5);
  near(fn('bimRoofCoverage')(half, RING, 1), 45 / 81, 1e-12);
  assert.equal(fn('bimRoofCoverage')([], RING, 1), 0);
});
test('WO-05 the plane\'s height at a plan point; a vertical plane has none', () => {
  const p = X.bimRoofPlane(grid(0));
  near(fn('bimRoofZ')(p, 4, 2), 11.5, 1e-9);
  assert.equal(fn('bimRoofZ')({ c: [0, 0, 0], n: [1, 0, 0] }, 1, 1), null);
});
