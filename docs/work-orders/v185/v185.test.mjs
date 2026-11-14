/* V185's work-order tests (docs/work-orders/v185/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/drawing/sweeps.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v185/v185.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v185/v185.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimSwpPerp", "bimSwpFrames", "bimSwpSweep", "bimSwpCircle", "bimSwpCap"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/drawing/sweeps.js'), 'utf8');
  if (process.env.V185_REF) src += fs.readFileSync(process.env.V185_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/drawing/sweeps.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
test('WO-01 helpers: a unit perpendicular from the least aligned world axis', () => {
  const p = fn('bimSwpPerp')([0, 0, 1]);
  near(dot(p, [0, 0, 1]), 0, 1e-15); near(Math.hypot(...p), 1, 1e-15);

  near(dot(fn('bimSwpPerp')([0.6, 0.8, 0]), [0.6, 0.8, 0]), 0, 1e-15);
});
test('WO-02 rotation-minimising frames (double reflection): orthonormal, no twist on a planar bend', () => {
  const rail = [[0, 0, 0], [1, 0, 0], [2, 0, 0], [2.7, 0.7, 0], [3, 1.7, 0], [3, 3, 0]];
  const F = fn('bimSwpFrames')(rail);
  assert.equal(F.length, 6);
  for (const q of F) { near(dot(q.t, q.n), 0, 1e-12); near(dot(q.n, q.n), 1, 1e-12); near(dot(q.b, q.t), 0, 1e-12); }
  for (const q of F) near(Math.abs(q.n[2]), 1, 1e-9, 'the normal stays out of the plane: no twist');
  assert.deepEqual(F[2].p, [2, 0, 0]);
  assert.deepEqual(fn('bimSwpFrames')([[0, 0, 0]]), []);
});
test('WO-03 a profile swept along the rail; closed profiles wrap', () => {
  const sq = [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]];
  const m = fn('bimSwpSweep')(sq, [[0, 0, 0], [0, 0, 4]], true);
  assert.equal(m.v.length, 8); assert.equal(m.f.length, 4);
  for (const p of m.v.slice(0, 4)) near(p[2], 0, 1e-12);
  for (const p of m.v) near(Math.hypot(p[0], p[1]), Math.SQRT1_2, 1e-12);
  assert.equal(fn('bimSwpSweep')(sq, [[0, 0, 0], [0, 0, 4]], false).f.length, 3);
  assert.equal(fn('bimSwpSweep')(sq, [[0, 0, 0]], true), null);
});
test('WO-04 a circle profile of n points', () => {
  const c = fn('bimSwpCircle')(2, 4);
  assert.equal(c.length, 4); near(c[1][0], 0, 1e-12); near(c[1][1], 2);
  assert.equal(fn('bimSwpCircle')(1).length, 16);
});
test('WO-05 a cap: a centre vertex and a fan over a ring, either way round', () => {
  const pipe = X.bimSwpSweep(X.bimSwpCircle(1, 4), [[0, 0, 0], [0, 0, 2]], true);
  const c = fn('bimSwpCap')(pipe, 0, 4, true);
  assert.equal(c.v.length, 9); assert.equal(c.f.length, 8);
  for (const x of c.v[8]) near(x, 0, 1e-12);
  assert.deepEqual(c.f[4], [8, 1, 0]);
  assert.deepEqual(fn('bimSwpCap')(pipe, 4, 4, false).f[4], [8, 4, 5]);
  assert.equal(pipe.v.length, 8, 'the input is not changed');
});
