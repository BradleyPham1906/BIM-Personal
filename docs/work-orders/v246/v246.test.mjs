/* V246's work-order tests (docs/work-orders/v246/SPEC.md): the pure functions of src/js/engine/analysis/form-finding.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v246/v246.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v246/v246.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text.
   Expected numbers come from the research's worked examples (docs/research/research-physical-world/ and
   docs/research/experiments/physical-world/), not from the implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimFfSolve', 'bimFdm', 'bimDr'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/analysis/form-finding.js'), 'utf8');
  if (process.env.V246_REF) src += fs.readFileSync(process.env.V246_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/analysis/form-finding.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

function grid(n) {
  const xyz = [], edges = [], fixed = [];
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { xyz.push([i, j, 0]); if (i === 0 || j === 0 || i === n - 1 || j === n - 1) fixed.push(j * n + i); }
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { if (i + 1 < n) edges.push([j * n + i, j * n + i + 1]); if (j + 1 < n) edges.push([j * n + i, (j + 1) * n + i]); }
  return { xyz, edges, fixed };
}
const STAR = { xyz: [[0, 0, 0], [2, 0, 0], [2, 2, 0], [0, 2, 0], [0.7, 1.6, 3]], edges: [[4, 0], [4, 1], [4, 2], [4, 3]], fixed: [0, 1, 2, 3], loads: [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, -1]] };
test('WO-01 a dense solve for several right-hand sides, with pivoting', () => {
  const s = fn('bimFfSolve'), X1 = s([[0, 2], [1, 1]], [[2, 4], [3, 3]]);
  near(X1[0][0], 2, 1e-12); near(X1[1][0], 1, 1e-12); near(X1[0][1], 1, 1e-12); near(X1[1][1], 2, 1e-12);
  assert.equal(s([[1, 1], [1, 1]], [[1], [2]]), null);
});
test('WO-02 the force density method: one node on four corners settles at the mean plus p / sum q', () => {
  const r = fn('bimFdm')({ ...STAR, q: [1, 1, 1, 1] });
  near(r.xyz[4][0], 1, 1e-12); near(r.xyz[4][1], 1, 1e-12); near(r.xyz[4][2], -0.25, 1e-12);
  assert.deepEqual(r.xyz[0], [0, 0, 0]); r.forces.forEach((f, e) => near(f, r.lengths[e], 1e-12, 'q = 1: force = length'));
  near(r.lengths[0], Math.sqrt(2 + 0.0625), 1e-12);
  near(fn('bimFdm')({ ...STAR, q: [-1, -1, -1, -1] }).xyz[4][2], 0.25, 1e-12, 'negative q: a vault in compression');
  near(fn('bimFdm')({ ...STAR, q: [2, 2, 2, 2] }).xyz[4][2], -0.125, 1e-12, 'doubling q halves the sag');
  assert.deepEqual(STAR.xyz[4], [0.7, 1.6, 3], 'the input is not changed');
});
test('WO-02 a 5 x 5 net, fixed edges, unit loads: the research\'s exact sags', () => {
  const g = grid(5), r = fn('bimFdm')({ ...g, q: g.edges.map(() => 1), loads: g.xyz.map(() => [0, 0, -1]) });
  near(r.xyz[6][2], -11 / 16, 1e-12); near(r.xyz[7][2], -7 / 8, 1e-12); near(r.xyz[12][2], -9 / 8, 1e-12);
  near(r.xyz[12][0], 2, 1e-12); near(r.xyz[6][1], 1, 1e-12, 'the plan stays on the grid');
  assert.ok(r.forces.every((f) => f > 0));
});
test('WO-02 a free node with no path to a support is refused', () => {
  const r = fn('bimFdm')({ xyz: [[0, 0, 0], [1, 0, 0], [5, 5, 5]], edges: [[0, 1]], q: [1], fixed: [0, 1], loads: [[0, 0, 0], [0, 0, 0], [0, 0, -1]] });
  assert.ok(r.error); assert.ok(fn('bimFdm')({ ...STAR, q: [1] }).error);
});
test('WO-03 dynamic relaxation with kinetic damping reaches the FDM shape (rest length 0, k = q)', () => {
  const g = grid(5), loads = g.xyz.map(() => [0, 0, -1]);
  const r = fn('bimDr')({ ...g, k: g.edges.map(() => 1), loads });
  assert.equal(r.converged, true); assert.ok(r.residual < 1e-9);
  near(r.xyz[12][2], -1.125, 1e-8); near(r.xyz[6][2], -0.6875, 1e-8);
  assert.ok(r.iterations < 200, 'kinetic damping converges in about 81 steps, not hundreds: ' + r.iterations);
  assert.deepEqual(r.xyz[0], [0, 0, 0]);
});
test('WO-03 rest lengths change the shape, and a step limit is kept', () => {
  const g = grid(5), loads = g.xyz.map(() => [0, 0, -1]);
  const r = fn('bimDr')({ ...g, k: g.edges.map(() => 1), rest: g.edges.map(() => 0.5), loads, kmax: 20000 });
  assert.equal(r.converged, true); assert.ok(r.xyz[12][2] < -1.2, 'rest length 0.5 sags more than -1.125');
  const s = fn('bimDr')({ ...g, k: g.edges.map(() => 1), loads, kmax: 3 });
  assert.equal(s.converged, false); assert.equal(s.iterations, 3);
});
