/* V183's work-order tests (docs/work-orders/v183/SPEC.md, WO-01 to WO-06): the pure functions of src/js/engine/drawing/nurbs.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v183/v183.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v183/v183.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimNurbsKnots", "bimNurbsSpan", "bimNurbsBasis", "bimNurbsPoint", "bimNurbsTangent", "bimNurbsSample"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/drawing/nurbs.js'), 'utf8');
  if (process.env.V183_REF) src += fs.readFileSync(process.env.V183_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/drawing/nurbs.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// a quarter circle of radius 1 as a rational quadratic (The NURBS Book, example 7.1): weights 1, sqrt(2)/2, 1
const ARC = { deg: 2, pts: [[1, 0, 0], [1, 1, 0], [0, 1, 0]], w: [1, Math.SQRT1_2, 1], knots: [0, 0, 0, 1, 1, 1] };
test('WO-01 a clamped uniform knot vector', () => {
  assert.deepEqual(fn('bimNurbsKnots')(4, 2), [0, 0, 0, 0.5, 1, 1, 1]);
  assert.deepEqual(fn('bimNurbsKnots')(3, 2), [0, 0, 0, 1, 1, 1]);
  assert.deepEqual(fn('bimNurbsKnots')(6, 3), [0, 0, 0, 0, 1 / 3, 2 / 3, 1, 1, 1, 1]);
  assert.deepEqual(fn('bimNurbsKnots')(2, 2), []);
});
test('WO-02 the knot span holding u (The NURBS Book A2.1), the last span at u = 1', () => {
  const k = [0, 0, 0, 0.5, 1, 1, 1];
  assert.deepEqual([0, 0.25, 0.5, 0.75, 1].map((u) => fn('bimNurbsSpan')(4, 2, u, k)), [2, 2, 3, 3, 3]);
});
test('WO-03 the non-zero basis functions (A2.2): they sum to one', () => {
  const k = [0, 0, 0, 0.5, 1, 1, 1], N = fn('bimNurbsBasis')(2, 0.25, 2, k);
  near(N[0], 0.25); near(N[1], 0.625); near(N[2], 0.125);
  const M = fn('bimNurbsBasis')(3, 0.75, 2, k);
  near(M[0] + M[1] + M[2], 1, 1e-15);
});
test('WO-04 a rational point: every point of the quarter circle at radius 1', () => {
  for (const u of [0, 0.1, 0.3, 0.5, 0.77, 1]) { const P = fn('bimNurbsPoint')(ARC, u); near(Math.hypot(P[0], P[1]), 1, 1e-12, 'u ' + u); }
  assert.deepEqual(fn('bimNurbsPoint')(ARC, 0), [1, 0, 0]);
  const L = { deg: 1, pts: [[0, 0, 0], [2, 0, 0], [2, 2, 0]], knots: [0, 0, 0.5, 1, 1] };
  assert.deepEqual(fn('bimNurbsPoint')(L, 0.75), [2, 1, 0], 'no weights means all 1');
});
test('WO-05 a tangent by central difference, clamped at the ends', () => {
  const T = fn('bimNurbsTangent')(ARC, 0.5);
  near(T[0] / Math.hypot(T[0], T[1]), -Math.SQRT1_2, 1e-6); near(T[1] / Math.hypot(T[0], T[1]), Math.SQRT1_2, 1e-6);
  const S = fn('bimNurbsTangent')(ARC, 0);
  near(S[0] / Math.hypot(S[0], S[1]), 0, 1e-5);
});
test('WO-06 samples within the chord tolerance, ends exact, at least 5 points', () => {
  const pts = fn('bimNurbsSample')(ARC, 1e-3);
  assert.deepEqual(pts[0], [1, 0, 0]); near(pts[pts.length - 1][0], 0, 1e-12); near(pts[pts.length - 1][1], 1);
  assert.ok(pts.length >= 5);
  for (let i = 1; i < pts.length; i++) { const m = [(pts[i][0] + pts[i - 1][0]) / 2, (pts[i][1] + pts[i - 1][1]) / 2]; assert.ok(1 - Math.hypot(m[0], m[1]) <= 1e-3 + 1e-9, 'chord error'); }
  assert.ok(fn('bimNurbsSample')(ARC, 1e-5).length > pts.length);
});
