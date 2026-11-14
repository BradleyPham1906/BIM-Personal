/* V187's work-order tests (docs/work-orders/v187/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/drawing/nurbs-edit.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v187/v187.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v187/v187.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimNeKnotInsert", "bimNeMovePoint", "bimNeBlend", "bimNeElevate", "bimNeReverse"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/drawing/nurbs-edit.js'), 'utf8');
  if (process.env.V187_REF) src += fs.readFileSync(process.env.V187_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/drawing/nurbs-edit.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// an independent evaluator (Cox-de Boor recursion), only for the tests
function N(i, p, u, k) {
  if (p === 0) return (u >= k[i] && u < k[i + 1]) || (u === 1 && k[i + 1] === 1 && k[i] < 1) ? 1 : 0;
  const a = k[i + p] - k[i] ? (u - k[i]) / (k[i + p] - k[i]) * N(i, p - 1, u, k) : 0;
  const b = k[i + p + 1] - k[i + 1] ? (k[i + p + 1] - u) / (k[i + p + 1] - k[i + 1]) * N(i + 1, p - 1, u, k) : 0;
  return a + b;
}
function P(c, u) {
  let x = 0, y = 0, z = 0, W = 0;
  c.pts.forEach((p, i) => { const b = N(i, c.deg, u, c.knots) * (c.w ? c.w[i] : 1); x += p[0] * b; y += p[1] * b; z += p[2] * b; W += b; });
  return [x / W, y / W, z / W];
}
const C = { deg: 3, pts: [[0, 0, 0], [1, 2, 0], [3, 2, 1], [4, 0, 0], [6, 1, 0]], w: [1, 2, 1, 0.5, 1], knots: [0, 0, 0, 0, 0.5, 1, 1, 1, 1] };
test('WO-01 Boehm knot insertion: one more point, the same curve', () => {
  const D = fn('bimNeKnotInsert')(C, 0.3);
  assert.equal(D.pts.length, 6);
  assert.deepEqual(D.knots, [0, 0, 0, 0, 0.3, 0.5, 1, 1, 1, 1]);
  for (const u of [0, 0.1, 0.3, 0.45, 0.6, 0.99]) { const a = P(C, u), b = P(D, u); for (let q = 0; q < 3; q++) near(a[q], b[q], 1e-12, 'u ' + u); }
  assert.equal(fn('bimNeKnotInsert')(C, 0), null);
  assert.equal(fn('bimNeKnotInsert')(C, 1), null);
  assert.equal(fn('bimNeKnotInsert')({ deg: 1, pts: [[0, 0, 0], [1, 0, 0]], knots: [0, 0, 1, 1] }, 0.5).w, undefined);
});
test('WO-02 moving one control point gives a new curve, the old one unchanged', () => {
  const D = fn('bimNeMovePoint')(C, 2, [0, 0, 1]);
  assert.deepEqual(D.pts[2], [3, 2, 2]); assert.deepEqual(C.pts[2], [3, 2, 1]);
  assert.deepEqual(D.w, C.w); assert.notEqual(D.w, C.w);
  assert.equal(fn('bimNeMovePoint')(C, 9, [0, 0, 0]), null);
});
test('WO-03 a G1 blend: a cubic from the end of one curve to the start of another, along their tangents', () => {
  const B = fn('bimNeBlend')([0, 0, 0], [2, 0, 0], [3, 3, 0], [0, 5, 0]);
  near(B.pts[1][0], Math.hypot(3, 3) / 3); assert.deepEqual(B.pts[1].slice(1), [0, 0]);
  near(B.pts[2][1], 3 - Math.hypot(3, 3) / 3);
  assert.deepEqual(B.knots, [0, 0, 0, 0, 1, 1, 1, 1]);
  assert.deepEqual(fn('bimNeBlend')([0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], 0.5).pts[1], [0.5, 0, 0]);
});
test('WO-04 a Bezier raised one degree keeps its shape', () => {
  const Q = fn('bimNeElevate')([[0, 0, 0], [1, 2, 0], [2, 0, 0]]);
  [[0, 0, 0], [2 / 3, 4 / 3, 0], [4 / 3, 4 / 3, 0], [2, 0, 0]].forEach((e, i) => e.forEach((x, q) => near(Q[i][q], x, 1e-12)));
  const a = P({ deg: 2, pts: [[0, 0, 0], [1, 2, 0], [2, 0, 0]], knots: [0, 0, 0, 1, 1, 1] }, 0.37);
  const b = P({ deg: 3, pts: Q, knots: [0, 0, 0, 0, 1, 1, 1, 1] }, 0.37);
  near(a[0], b[0], 1e-12); near(a[1], b[1], 1e-12);
});
test('WO-05 a reversed curve runs the other way through the same points', () => {
  const R = fn('bimNeReverse')(C);
  assert.deepEqual(R.knots, [0, 0, 0, 0, 0.5, 1, 1, 1, 1]);
  const a = P(C, 0.2), b = P(R, 0.8);
  for (let q = 0; q < 3; q++) near(a[q], b[q], 1e-12);
  assert.deepEqual(C.pts[0], [0, 0, 0], 'the input unchanged');
});
