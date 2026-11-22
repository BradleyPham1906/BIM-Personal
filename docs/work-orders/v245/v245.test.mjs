/* V245's work-order tests (docs/work-orders/v245/SPEC.md): the pure functions of src/js/engine/structure/time-history.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v245/v245.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v245/v245.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text.
   Expected numbers come from the research's worked examples (docs/research/research-physical-world/ and
   docs/research/experiments/physical-world/), not from the implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimRayleigh', 'bimNewmarkSdof', 'bimThSolve', 'bimNewmarkMdof', 'bimGroundRead'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/structure/time-history.js'), 'utf8');
  if (process.env.V245_REF) src += fs.readFileSync(process.env.V245_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/structure/time-history.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 Rayleigh damping: a0 and a1 give the ratio at both chosen frequencies', () => {
  const r = fn('bimRayleigh')(12.3607, 32.3607, 0.05);
  near(r.a0, 0.894428, 1e-6); near(r.a1, 0.00223607, 1e-8);
  [12.3607, 32.3607].forEach((w) => near(r.a0 / (2 * w) + r.a1 * w / 2, 0.05, 1e-12));
  assert.ok(fn('bimRayleigh')(10, 10, 0.05).error); assert.ok(fn('bimRayleigh')(0, 10, 0.05).error);
});
test('WO-02 Newmark, average acceleration: the research\'s half-sine pulse (Chopra\'s example 5.3 data)', () => {
  const m = 0.2533, k = 10, c = 2 * 0.05 * m * Math.sqrt(k / m), p = [];
  for (let i = 0; i <= 10; i++) { const t = i * 0.1; p.push(t <= 0.6 + 1e-12 ? 10 * Math.sin(Math.PI * t / 0.6) : 0); }
  const r = fn('bimNewmarkSdof')({ m, c, k, p, dt: 0.1 });
  [0, 0.0437, 0.2326, 0.6121, 1.0825, 1.4310, 1.4231, 0.9622, 0.1908, -0.6044, -1.1442].forEach((v, i) => near(r.u[i], v, 6e-5, 't = ' + i / 10));
  assert.equal(r.u.length, 11); assert.equal(r.v.length, 11); assert.equal(r.a.length, 11);
});
test('WO-02 undamped free vibration: u_n = cos(n theta), theta = 2 atan(w dt / 2) (no decay, a longer period)', () => {
  const w = 5, dt = 0.1, th = 2 * Math.atan(w * dt / 2);
  const r = fn('bimNewmarkSdof')({ m: 2, c: 0, k: 50, p: Array(200).fill(0), dt, u0: 1, v0: 0 });
  r.u.forEach((u, i) => near(u, Math.cos(i * th), 1e-11));
  near(r.a[0], -25, 1e-12, 'a0 from equilibrium at t = 0');
  const g = fn('bimNewmarkSdof')({ m: 2, c: 0, k: 50, p: Array(10).fill(0), dt, u0: 0, v0: 0, gamma: 0.5, beta: 1 / 6 });
  assert.ok(g.u.every((u) => u === 0), 'gamma and beta may be given');
  assert.ok(fn('bimNewmarkSdof')({ m: 0, c: 0, k: 1, p: [0], dt: 0.1 }).error); assert.ok(fn('bimNewmarkSdof')({ m: 1, c: 0, k: 1, p: [], dt: 0.1 }).error);
});
test('WO-03 a dense solve with pivoting, and null when singular', () => {
  const s = fn('bimThSolve'), A = [[0, 2, 1], [1, 1, 0], [3, 0, 1]];
  const x = s(A, [5, 3, 4]); near(x[0], 1, 1e-12); near(x[1], 2, 1e-12); near(x[2], 1, 1e-12);
  assert.deepEqual(A, [[0, 2, 1], [1, 1, 0], [3, 0, 1]], 'A is not changed');
  assert.equal(s([[1, 2], [2, 4]], [1, 2]), null);
});
test('WO-04 Newmark for many degrees of freedom: one dof equals the single-dof result', () => {
  const ag = [0, 1, 2, 1, 0, 0, 0, 0, -1, 0];
  const r = fn('bimNewmarkMdof')({ M: [[2]], C: [[0.3]], K: [[50]], ag, dt: 0.02, iota: [1] });
  const s = X.bimNewmarkSdof ? X.bimNewmarkSdof({ m: 2, c: 0.3, k: 50, p: ag.map((a) => -2 * a), dt: 0.02 }) : null;
  assert.equal(r.u.length, ag.length);
  if (s) r.u.forEach((u, i) => near(u[0], s.u[i], 1e-14));
  near(r.u[1][0], -0.00009960159362549801, 1e-15);
});
test('WO-04 two storeys under a ground pulse: modal superposition gives the same answer', () => {
  const m = 100, kk = 40000, M = [[m, 0], [0, m]], K = [[2 * kk, -kk], [-kk, kk]], dt = 0.005, N = 400, ag = [];
  for (let i = 0; i < N; i++) { const t = i * dt; ag.push(t <= 0.5 ? 0.3 * 9.80665 * Math.sin(Math.PI * t / 0.5) : 0); }
  const C = [[0, 0], [0, 0]];
  const r = fn('bimNewmarkMdof')({ M, C, K, ag, dt, iota: [1, 1] });
  const w2 = [(3 - Math.sqrt(5)) / 2 * kk / m, (3 + Math.sqrt(5)) / 2 * kk / m], phi = [[1, (1 + Math.sqrt(5)) / 2], [1, (1 - Math.sqrt(5)) / 2]];
  const roof = Array(N).fill(0);
  for (let n = 0; n < 2; n++) {
    const Mn = m * (phi[n][0] ** 2 + phi[n][1] ** 2), Ln = m * (phi[n][0] + phi[n][1]);
    const q = X.bimNewmarkSdof ? X.bimNewmarkSdof({ m: Mn, c: 0, k: w2[n] * Mn, p: ag.map((a) => -Ln * a), dt }).u : null;
    if (!q) return assert.fail('WO-02 is needed for this check');
    q.forEach((v, i) => { roof[i] += phi[n][1] * v; });
  }
  r.u.forEach((u, i) => near(u[1], roof[i], 1e-12));
  assert.ok(Math.max(...r.u.map((u) => Math.abs(u[1]))) > 0.01);
  assert.ok(fn('bimNewmarkMdof')({ M, C, K, ag, dt, iota: [1] }).error); assert.ok(fn('bimNewmarkMdof')({ M: [[0]], C: [[0]], K: [[1]], ag: [0, 1], dt, iota: [1] }).error);
});
test('WO-05 reading a ground-motion record: two columns, time and acceleration (g)', () => {
  const g = fn('bimGroundRead');
  assert.deepEqual(g('# El Centro, a test\n0 0\n0.01, 0.1\n0.02\t-0.2\n\n0.03;0.05  # end\n'), { dt: 0.01, a: [0, 0.1, -0.2, 0.05], n: 4 });
  assert.deepEqual(g('0 0\r\n0.5 1e-2\r\n'), { dt: 0.5, a: [0, 0.01], n: 2 });
  assert.ok(g('0 0\n0.01 1\n0.03 2').error.indexOf('line 3') === 0);
  assert.ok(g('0 0\n0.01 x').error.indexOf('line 2') === 0); assert.ok(g('0 0\n0.01').error.indexOf('line 2') === 0);
  assert.ok(g('0 0').error); assert.ok(g('').error); assert.ok(g('0 0\n0 1').error); assert.ok(g(null).error);
});
