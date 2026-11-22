/* V242's work-order tests (docs/work-orders/v242/SPEC.md): the pure functions of src/js/engine/structure/modal.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v242/v242.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v242/v242.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text.
   Expected numbers come from the research's worked examples (docs/research/research-physical-world/ and
   docs/research/experiments/physical-world/), not from the implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimEigJacobi', 'bimModalLumped', 'bimModalPart', 'bimCqcRho', 'bimModalCombine', 'bimShearK', 'bimRsaScale'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/structure/modal.js'), 'utf8');
  if (process.env.V242_REF) src += fs.readFileSync(process.env.V242_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/structure/modal.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const exactW1 = (n, k, m) => 2 * Math.sqrt(k / m) * Math.sin(Math.PI / (2 * (2 * n + 1)));
test('WO-01 Jacobi: eigenvalues ascending, unit eigenvectors, a check of A v = lambda v', () => {
  const e = fn('bimEigJacobi'), A = [[4, 1, 2], [1, 3, 0], [2, 0, 5]], r = e(A);
  for (let i = 1; i < 3; i++) assert.ok(r.values[i] >= r.values[i - 1]);
  near(r.values.reduce((a, b) => a + b, 0), 12, 1e-10, 'the trace');
  r.vectors.forEach((v, i) => {
    near(Math.hypot(...v), 1, 1e-10);
    for (let k = 0; k < 3; k++) near(A[k][0] * v[0] + A[k][1] * v[1] + A[k][2] * v[2], r.values[i] * v[k], 1e-9);
  });
  assert.deepEqual(A, [[4, 1, 2], [1, 3, 0], [2, 0, 5]], 'A is not changed');
  assert.deepEqual(e([[2, 0], [0, 1]]).values, [1, 2]);
  assert.ok(e([[1, 2], [3, 1]]).error); assert.ok(e([[1, 2]]).error);
});
test('WO-02 modes of a lumped-mass model: the research\'s 2-storey shear building', () => {
  const m = fn('bimModalLumped')([[80000, -40000], [-40000, 40000]], [100, 100]);
  near(m[0].w2, 152.7864045, 1e-6); near(m[1].w2, 1047.2135955, 1e-6);
  near(m[0].T, 0.50832, 5e-6); near(m[1].T, 0.19416, 5e-6);
  near(m[0].phi[1] / m[0].phi[0], 1.6180339887, 1e-9); near(m[1].phi[1] / m[1].phi[0], -0.6180339887, 1e-9);
  m.forEach((md) => near(100 * md.phi[0] ** 2 + 100 * md.phi[1] ** 2, 1, 1e-10, 'mass-normalised'));
  near(m[0].w, Math.sqrt(m[0].w2), 1e-12);
});
test('WO-02 a 10-storey uniform shear building against the closed form, and bad masses', () => {
  const K = [], n = 10;
  for (let i = 0; i < n; i++) { K.push(Array(n).fill(0)); }
  for (let i = 0; i < n; i++) { K[i][i] = (i < n - 1 ? 2 : 1) * 1000; if (i) { K[i][i - 1] = -1000; K[i - 1][i] = -1000; } }
  near(fn('bimModalLumped')(K, Array(n).fill(2))[0].w, exactW1(n, 1000, 2), 1e-9);
  assert.ok(fn('bimModalLumped')([[1]], [0]).error); assert.ok(fn('bimModalLumped')([[1, 0], [0, 1]], [1]).error);
});
test('WO-03 participation: gamma and effective mass, the research\'s 94.72% and 5.28%', () => {
  const m = X.bimModalLumped ? X.bimModalLumped([[80000, -40000], [-40000, 40000]], [100, 100]) : null;
  const modes = m || [{ phi: [0.0525731112, 0.0850650808] }, { phi: [0.0850650808, -0.0525731112] }];
  const p = fn('bimModalPart')(modes, [100, 100], [1, 1]);
  near(p[0].ratio, 0.5 + 1 / Math.sqrt(5), 1e-8); near(p[1].ratio, 0.5 - 1 / Math.sqrt(5), 1e-8);
  near(p[0].mEff, 189.4427191, 1e-5); near(Math.abs(p[0].gamma), 13.7638192, 1e-5);
  const q = fn('bimModalPart')([{ phi: [1, 1.6180339887] }], [100, 100], [1, 1]);
  near(q[0].gamma, 0.7236068, 1e-6, 'any scaling of phi: gamma for phi as given'); near(q[0].mEff, 189.4427191, 1e-5, 'effective mass does not depend on the scaling');
  near(fn('bimModalPart')(modes, [100, 100], [1, 0])[0].ratio + fn('bimModalPart')(modes, [100, 100], [1, 0])[1].ratio, 1, 1e-9, 'one dof in the direction');
});
test('WO-04 the CQC correlation (5%), symmetric, 1 on the diagonal', () => {
  const r = fn('bimCqcRho');
  near(r(10, 10, 0.05), 1, 1e-12); near(r(10, 9, 0.05), 0.4730, 5e-5); near(r(10, 5, 0.05), 0.01849, 5e-6); near(r(10, 3.82, 0.05), 0.00886, 5e-6);
  near(r(10, 20, 0.05), r(20, 10, 0.05), 1e-15); assert.equal(r(10, 5, 0), 0); assert.ok(Number.isNaN(r(0, 5, 0.05)));
});
test('WO-05 combining modal values: SRSS, and CQC, which reduces to SRSS for far-apart modes', () => {
  const c = fn('bimModalCombine');
  near(c([3, 4], [10, 30], 0.05, 'srss'), 5, 1e-12);
  near(c([3, 4], [10, 30], 0.05, 'cqc'), Math.sqrt(9 + 16 + 2 * X.bimCqcRho(10, 30, 0.05) * 12), 1e-12);
  near(c([3, 4], [10, 10.5], 0.05, 'cqc'), 6.6617, 5e-5, 'close modes add nearly directly');
  near(c([3, -4], [10, 10.5], 0.05, 'cqc'), Math.sqrt(25 - 24 * X.bimCqcRho(10, 10.5, 0.05)), 1e-12, 'signs count in CQC');
  near(c([7], [10], 0.05, 'cqc'), 7, 1e-12);
});
test('WO-06 a shear building\'s stiffness from storey stiffnesses, ground storey first', () => {
  assert.deepEqual(fn('bimShearK')([40000, 40000]), [[80000, -40000], [-40000, 40000]]);
  assert.deepEqual(fn('bimShearK')([3, 2, 1]), [[5, -2, 0], [-2, 3, -1], [0, -1, 1]]);
  assert.deepEqual(fn('bimShearK')([7]), [[7]]); assert.deepEqual(fn('bimShearK')([]), []);
});
test('WO-07 scaling the spectrum\'s base shear up to the ELF shear (100%), never down', () => {
  const s = fn('bimRsaScale');
  near(s(900, 1170.2), 1170.2 / 900, 1e-12); assert.equal(s(1300, 1170.2), 1); assert.equal(s(1170.2, 1170.2), 1); assert.ok(Number.isNaN(s(0, 1)));
});
