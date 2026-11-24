/* V277a's work-order tests (docs/work-orders/v277a/SPEC.md): the pure functions of src/js/engine/math/math.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v277a/v277a.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v277a/v277a.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text.
   Expected numbers come from closed forms and from the research (docs/research/research-tensors-rotations.md,
   docs/research/experiments/v277a-tensors/), not from the implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimV3Add', 'bimV3Sub', 'bimV3Scale', 'bimV3Dot', 'bimV3Cross', 'bimV3Len', 'bimV3Norm',
  'bimM3Ident', 'bimM3Mul', 'bimM3T', 'bimM3MulV', 'bimM3Det',
  'bimQMul', 'bimQConj', 'bimQNormalize', 'bimQCanon', 'bimQRotate', 'bimQFromAxisAngle',
  'bimQToM3', 'bimM3ToQ', 'bimQExp', 'bimQLog', 'bimQSlerp', 'bimQIntegrate', 'bimEulerToQ', 'bimQToEuler',
  'bimTrsToM4', 'bimM4MulPoint', 'bimSymToMandel', 'bimMandelToSym', 'bimMandelFromVoigt', 'bimMandelToVoigt',
  'bimSymRotate', 'bimMandelRotM', 'bimMandelRotate4', 'bimSymInvariants', 'bimSymEig3', 'bimIsoStiffness',
  'bimOrthoCompliance', 'bimWoodOrtho', 'bimInv6'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/math/math.js'), 'utf8');
  if (process.env.V277A_REF) src += fs.readFileSync(process.env.V277A_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/math/math.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-12 : e), (m || '') + ' ' + a + ' is not ' + b);
const nearV = (a, b, e, m) => { assert.equal(a.length, b.length, (m || '') + ' length'); a.forEach((x, i) => near(x, b[i], e, (m || '') + ' [' + i + ']')); };
const sameRot = (a, b, e, m) => near(Math.abs(a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]), 1, e === undefined ? 1e-12 : e, (m || '') + ' same rotation');
const H = Math.PI / 2;

test('WO-01 vec3: add, sub, scale, dot, cross (right-handed), length, unit; inputs unchanged', () => {
  const a = [1, 2, 3], b = [-4, 0.5, 2];
  assert.deepEqual(fn('bimV3Add')(a, b), [-3, 2.5, 5]);
  assert.deepEqual(fn('bimV3Sub')(a, b), [5, 1.5, 1]);
  assert.deepEqual(fn('bimV3Scale')(a, -2), [-2, -4, -6]);
  assert.equal(fn('bimV3Dot')(a, b), 3);
  assert.deepEqual(fn('bimV3Cross')([1, 0, 0], [0, 1, 0]), [0, 0, 1], 'x cross y is z');
  assert.deepEqual(fn('bimV3Cross')(a, b), [2.5, -14, 8.5]);
  near(fn('bimV3Len')([3, 4, 12]), 13);
  nearV(fn('bimV3Norm')([0, -5, 0]), [0, -1, 0]);
  assert.deepEqual(fn('bimV3Norm')([0, 0, 0]), [0, 0, 0], 'the zero vector stays zero, never NaN');
  assert.deepEqual(a, [1, 2, 3]); assert.deepEqual(b, [-4, 0.5, 2]);
});

test('WO-02 mat3 (row-major): identity, product order, transpose, matrix times vector, determinant', () => {
  const A = [1, 2, 3, 4, 5, 6, 7, 8, 10], B = [0, 1, 0, -1, 0, 0, 0, 0, 1];
  assert.deepEqual(fn('bimM3Ident')(), [1, 0, 0, 0, 1, 0, 0, 0, 1]);
  assert.deepEqual(fn('bimM3Mul')(A, B), [-2, 1, 3, -5, 4, 6, -8, 7, 10], 'A times B, rows of A by columns of B');
  assert.deepEqual(fn('bimM3Mul')(B, A), [4, 5, 6, -1, -2, -3, 7, 8, 10], 'not commutative');
  assert.deepEqual(fn('bimM3T')(A), [1, 4, 7, 2, 5, 8, 3, 6, 10]);
  assert.deepEqual(fn('bimM3MulV')(A, [1, 0, -1]), [-2, -2, -3]);
  near(fn('bimM3Det')(A), -3); near(fn('bimM3Det')(B), 1);
});

test('WO-03 quaternion [x, y, z, w], Hamilton: i j = k, conjugate, normalise, canonical w >= 0', () => {
  const m = fn('bimQMul');
  assert.deepEqual(m([1, 0, 0, 0], [0, 1, 0, 0]), [0, 0, 1, 0], 'i j = k (Hamilton, not JPL)');
  assert.deepEqual(m([0, 1, 0, 0], [1, 0, 0, 0]), [0, 0, -1, 0], 'j i = -k');
  assert.deepEqual(m([0, 0, 0, 1], [0.1, 0.2, 0.3, 0.9]), [0.1, 0.2, 0.3, 0.9], 'identity');
  assert.deepEqual(fn('bimQConj')([1, 2, 3, 4]), [-1, -2, -3, 4]);
  nearV(fn('bimQNormalize')([0, 0, 3, 4]), [0, 0, 0.6, 0.8]);
  assert.deepEqual(fn('bimQNormalize')([0, 0, 0, 0]), [0, 0, 0, 1], 'zero becomes the identity');
  assert.deepEqual(fn('bimQCanon')([0.5, -0.5, 0.5, -0.5]), [-0.5, 0.5, -0.5, 0.5]);
  assert.deepEqual(fn('bimQCanon')([0.6, 0, 0, 0.8]), [0.6, 0, 0, 0.8]);
});

test('WO-04 rotate a vector; from axis and angle (any axis length, a zero axis is the identity)', () => {
  const q = fn('bimQFromAxisAngle')([0, 0, 5], H);
  nearV(q, [0, 0, Math.SQRT1_2, Math.SQRT1_2], 1e-15, 'the axis is normalised');
  nearV(fn('bimQRotate')(q, [1, 0, 0]), [0, 1, 0], 1e-15, 'a right-handed quarter turn about z takes x to y');
  const q2 = fn('bimQFromAxisAngle')([1, 1, 1], 2 * Math.PI / 3);
  nearV(fn('bimQRotate')(q2, [1, 0, 0]), [0, 1, 0], 1e-15, 'a third of a turn about (1,1,1) cycles the axes');
  nearV(fn('bimQRotate')(q2, [0, 0, 2]), [2, 0, 0], 1e-15);
  assert.deepEqual(fn('bimQFromAxisAngle')([0, 0, 0], 1), [0, 0, 0, 1]);
});

test('WO-05 quaternion to matrix and back by Shepperd\'s pivot: exact near and at a half turn (e02)', () => {
  const toM = fn('bimQToM3'), toQ = fn('bimM3ToQ');
  nearV(toM([0, Math.SQRT1_2, 0, Math.SQRT1_2]), [0, 0, 1, 0, 1, 0, -1, 0, 0], 1e-15, 'a quarter turn about y');
  const half = toM([0, 0, 1, 0]);
  nearV(half, [-1, 0, 0, 0, -1, 0, 0, 0, 1], 1e-15, 'a half turn about z');
  const back = toQ(half); assert.ok(back.every(Number.isFinite), 'no NaN at a half turn'); sameRot(back, [0, 0, 1, 0]);
  const ax = [0.36, -0.48, 0.8];
  [0.3, 2.5, Math.PI - 1e-6, Math.PI].forEach((t) => {
    const q = [ax[0] * Math.sin(t / 2), ax[1] * Math.sin(t / 2), ax[2] * Math.sin(t / 2), Math.cos(t / 2)], r = toQ(toM(q));
    sameRot(r, q, 1e-12, 'angle ' + t); assert.ok(r[3] >= 0, 'canonical w >= 0'); near(Math.hypot(...r), 1, 1e-14);
  });
});

test('WO-06 exponential and logarithm maps: a rotation vector to a quaternion and back, small angles too', () => {
  const ex = fn('bimQExp'), lg = fn('bimQLog');
  nearV(ex([0, 0, Math.PI]), [0, 0, 1, Math.cos(Math.PI / 2)], 1e-15, 'pi about z');
  nearV(ex([1e-10, 0, 0]), [5e-11, 0, 0, 1], 1e-20, 'below 1e-8 rad: the Taylor series, no 0/0');
  assert.deepEqual(ex([0, 0, 0]), [0, 0, 0, 1]);
  nearV(lg(ex([0.3, -1.2, 0.4])), [0.3, -1.2, 0.4], 1e-14);
  nearV(lg([0, 0, 0, -1]), [0, 0, 0], 1e-15, '-1 is the identity');
  nearV(lg([-0.6, 0, 0, -0.8]), [2 * Math.atan2(0.6, 0.8), 0, 0], 1e-14, 'canonical first: the shorter angle');
});

test('WO-07 slerp: halfway, shorter arc for a negated end, renormalised fallback for near-equal ends (e03)', () => {
  const s = fn('bimQSlerp'), a = [0, 0, 0, 1], b = [0, 0, 1, 0];
  nearV(s(a, b, 0.5), [0, 0, Math.SQRT1_2, Math.SQRT1_2], 1e-15, 'halfway to a half turn is a quarter turn');
  nearV(s(a, b, 0), a, 1e-15); nearV(s(a, b, 1), b, 1e-15);
  sameRot(s(a, [0, 0, -Math.SQRT1_2, -Math.SQRT1_2], 0.5), [0, 0, Math.sin(Math.PI / 8), Math.cos(Math.PI / 8)], 1e-14, '-q2 is taken the short way');
  const c = [0, 0, Math.sin(5e-4), Math.cos(5e-4)], r = s(a, c, 0.5);
  near(Math.hypot(...r), 1, 1e-15, 'unit even in the linear fallback');
  sameRot(r, [0, 0, Math.sin(2.5e-4), Math.cos(2.5e-4)], 1e-12);
});

test('WO-08 integrate orientation with the exponential map: an hour at 60 Hz stays exact (e01b)', () => {
  const step = fn('bimQIntegrate'), w = [0.3, 1.2, -0.7], dt = 1 / 60;
  let q = [0, 0, 0, 1];
  for (let i = 0; i < 216000; i++) q = step(q, w, dt);
  const n = Math.hypot(...w), th = n * 3600, ex = [w[0] / n * Math.sin(th / 2), w[1] / n * Math.sin(th / 2), w[2] / n * Math.sin(th / 2), Math.cos(th / 2)];
  sameRot(q, ex, 1e-9, 'after 216,000 steps');
  near(Math.hypot(...q), 1, 1e-14);
  const q1 = step([0, 0, 0, 1], [0, 0, H], 1);
  nearV(fn('bimQRotate')(q1, [1, 0, 0]), [0, 1, 0], 1e-15, 'w in the world frame: a quarter turn about z in one second');
  const q2 = step(fn('bimQFromAxisAngle')([1, 0, 0], H), [0, 0, H], 1);
  nearV(fn('bimQRotate')(q2, [0, 1, 0]), [0, 0, 1], 1e-15, 'the world-frame turn is applied after the body\'s own (q2 = dq q); q dq would give [-1, 0, 0]');
});

test('WO-09 angles people type: yaw, pitch, roll about the displayed axes (X east, Y north, Z up), and back', () => {
  const eq = fn('bimEulerToQ'), qe = fn('bimQToEuler'), rot = fn('bimQRotate');
  nearV(rot(eq(H, 0, 0), [1, 0, 0]), [0, 0, -1], 1e-15, 'yaw 90 degrees turns east (+x) to north (-z), counterclockwise from above');
  nearV(rot(eq(0, H, 0), [0, 1, 0]), [1, 0, 0], 1e-15, 'pitch tips up (+y) toward east about the north axis');
  nearV(rot(eq(0, 0, H), [0, 0, -1]), [0, 1, 0], 1e-15, 'roll tips north (-z) up about the east axis');
  const r = qe(eq(0.4, -0.7, 1.1)); near(r.yaw, 0.4, 1e-13); near(r.pitch, -0.7, 1e-13); near(r.roll, 1.1, 1e-13);
  const g = qe(eq(0.5, H, 0.2));
  near(g.pitch, H, 1e-7, 'gimbal lock: pitch kept'); near(g.roll, 0, 0, 'roll set to 0');
  sameRot(eq(g.yaw, g.pitch, g.roll), eq(0.5, H, 0.2), 1e-12, 'the rotation is kept at gimbal lock');
});

test('WO-10 a placement (translation, rotation, scale) as a column-major 4x4, and a point through it', () => {
  const M = fn('bimTrsToM4')([10, 20, 30], [0, 0, Math.SQRT1_2, Math.SQRT1_2], [2, 3, 4]);
  nearV(M, [0, 2, 0, 0, -3, 0, 0, 0, 0, 0, 4, 0, 10, 20, 30, 1], 1e-15, 'columns are the scaled axes, then the translation');
  nearV(fn('bimM4MulPoint')(M, [1, 1, 1]), [7, 22, 34], 1e-14, 'scale, then rotate, then translate (glTF TRS)');
  nearV(fn('bimM4MulPoint')([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1], [2, 4, 6]), [2 / 7, 4 / 7, 6 / 7], 1e-15, 'w = z + 1 = 7 divides');
});

test('WO-11 Mandel and Voigt forms of a symmetric tensor; the shear factors differ for stress and strain', () => {
  const s = [10, 4, 5, 4, 20, 6, 5, 6, 30], m = fn('bimSymToMandel')(s), r2 = Math.SQRT2;
  nearV(m, [10, 20, 30, 6 * r2, 5 * r2, 4 * r2], 1e-14, 'order 11, 22, 33, 23, 13, 12; shears times sqrt 2');
  nearV(fn('bimMandelToSym')(m), s, 1e-14);
  nearV(fn('bimMandelToVoigt')(m, 'stress'), [10, 20, 30, 6, 5, 4], 1e-14, 'Voigt stress keeps the shear');
  nearV(fn('bimMandelToVoigt')(m, 'strain'), [10, 20, 30, 12, 10, 8], 1e-14, 'Voigt strain doubles it (engineering shear)');
  nearV(fn('bimMandelFromVoigt')([10, 20, 30, 12, 10, 8], 'strain'), m, 1e-14);
  nearV(fn('bimMandelFromVoigt')([10, 20, 30, 6, 5, 4], 'stress'), m, 1e-14);
});

test('WO-12 rotating a symmetric tensor: R s R^T, and the 6x6 Mandel rotation is orthogonal (e06)', () => {
  const R = fn('bimQToM3')(fn('bimQFromAxisAngle')([0, 0, 1], H)), s = [10, 0, 0, 0, 2, 0, 0, 0, 3];
  nearV(fn('bimSymRotate')(R, s), [2, 0, 0, 0, 10, 0, 0, 0, 3], 1e-14, 'a quarter turn swaps the x and y stresses');
  const R2 = fn('bimQToM3')(fn('bimQFromAxisAngle')([0.2, -0.5, 0.8], 1.3)), t = [3, -1, 2, -1, 5, 0.5, 2, 0.5, -4];
  const Q = fn('bimMandelRotM')(R2);
  for (let i = 0; i < 6; i++) for (let j = 0; j < 6; j++) {
    let d = 0; for (let k = 0; k < 6; k++) d += Q[k][i] * Q[k][j];
    near(d, i === j ? 1 : 0, 1e-14, 'Q^T Q at ' + i + ',' + j);
  }
  const via = fn('bimSymToMandel')(t).map((_, i) => Q[i].reduce((a, q, k) => a + q * fn('bimSymToMandel')(t)[k], 0));
  nearV(fn('bimMandelToSym')(via), fn('bimSymRotate')(R2, t), 1e-13, 'Q m equals R s R^T');
});

test('WO-13 rotating a 6x6 stiffness: Q C Q^T; an isotropic one does not change', () => {
  const Q = fn('bimMandelRotM')(fn('bimQToM3')(fn('bimQFromAxisAngle')([1, 2, 3], 0.9)));
  const C = fn('bimIsoStiffness')(210e9, 0.3), Cr = fn('bimMandelRotate4')(Q, C);
  for (let i = 0; i < 6; i++) for (let j = 0; j < 6; j++) near(Cr[i][j], C[i][j], 1e-3, 'isotropic at ' + i + ',' + j);
  const D = [[1, 0, 0, 0, 0, 0], [0, 2, 0, 0, 0, 0], [0, 0, 3, 0, 0, 0], [0, 0, 0, 4, 0, 0], [0, 0, 0, 0, 5, 0], [0, 0, 0, 0, 0, 6]];
  const Qz = fn('bimMandelRotM')(fn('bimQToM3')([0, 0, Math.SQRT1_2, Math.SQRT1_2])), Dr = fn('bimMandelRotate4')(Qz, D);
  near(Dr[0][0], 2, 1e-14, 'a quarter turn about z swaps 11 and 22'); near(Dr[1][1], 1, 1e-14);
  near(Dr[3][3], 5, 1e-14, 'and swaps the 23 and 13 shears'); near(Dr[4][4], 4, 1e-14); near(Dr[5][5], 6, 1e-14);
});

test('WO-14 invariants: I1, I2, I3, J2 and the von Mises stress', () => {
  const inv = fn('bimSymInvariants');
  const u = inv([100, 0, 0, 0, 0, 0, 0, 0, 0]);
  near(u.I1, 100); near(u.I2, 0); near(u.I3, 0); near(u.vonMises, 100, 1e-12, 'uniaxial: von Mises equals the stress');
  const sh = inv([0, 50, 0, 50, 0, 0, 0, 0, 0]);
  near(sh.vonMises, 50 * Math.sqrt(3), 1e-12, 'pure shear tau: sqrt(3) tau'); near(sh.I2, -2500);
  const h = inv([-7, 0, 0, 0, -7, 0, 0, 0, -7]);
  near(h.vonMises, 0, 1e-12, 'hydrostatic: no deviatoric part'); near(h.I3, -343); near(h.I2, 147);
  const g = inv([3, 1, 2, 1, 5, 0, 2, 0, 4]); near(g.I1, 12); near(g.I2, 42); near(g.I3, 36);
});

test('WO-15 principal values by cyclic Jacobi: exact on equal and wide-ranging eigenvalues (e05)', () => {
  const e = fn('bimSymEig3'), A = [4, 1, 2, 1, 3, 0, 2, 0, 5], r = e(A);
  assert.deepEqual(A, [4, 1, 2, 1, 3, 0, 2, 0, 5], 'A is not changed');
  for (let i = 1; i < 3; i++) assert.ok(r.values[i] >= r.values[i - 1], 'ascending');
  const check = (M, res) => res.vectors.forEach((v, i) => { near(Math.hypot(...v), 1, 1e-13);
    for (let k = 0; k < 3; k++) near(M[3 * k] * v[0] + M[3 * k + 1] * v[1] + M[3 * k + 2] * v[2], res.values[i] * v[k], 1e-12 * Math.max(1, Math.abs(res.values[2]))); });
  check(A, r);
  const R = fn('bimQToM3')(fn('bimQFromAxisAngle')([0.3, 0.9, -0.2], 0.77)), D = [2, 0, 0, 0, 2, 0, 0, 0, 5];
  const S = fn('bimM3Mul')(fn('bimM3Mul')(R, D), fn('bimM3T')(R)), rs = e(S);
  nearV(rs.values, [2, 2, 5], 1e-13, 'two equal eigenvalues (a cylinder)'); check(S, rs);
  near(Math.abs(fn('bimV3Dot')(rs.vectors[0], rs.vectors[1])), 0, 1e-13, 'an orthonormal pair in the repeated plane');
  const W = fn('bimM3Mul')(fn('bimM3Mul')(R, [1, 0, 0, 0, 1, 0, 0, 0, 1e-8]), fn('bimM3T')(R)), rw = e(W);
  check(W, rw); near(rw.values[0], 1e-8, 1e-15, 'a thin rod\'s tiny inertia');
  assert.ok(e([1, 2, 0, 3, 1, 0, 0, 0, 1]).error, 'not symmetric'); assert.ok(e([1, 0, 0]).error);
});

test('WO-16 isotropic stiffness in Mandel form: steel, and a uniaxial strain\'s stresses', () => {
  const C = fn('bimIsoStiffness')(200e9, 0.25), lam = 200e9 * 0.25 / (1.25 * 0.5), mu = 200e9 / 2.5;
  near(C[0][0], lam + 2 * mu, 1); near(C[0][1], lam, 1); near(C[3][3], 2 * mu, 1, 'Mandel shear diagonal is 2 mu, not mu');
  near(C[0][3], 0, 0); near(C[3][4], 0, 0);
  const sig = C.map((row) => row[0] * 1e-3);
  near(sig[0], (lam + 2 * mu) * 1e-3, 1e-3); near(sig[1], lam * 1e-3, 1e-3);
  assert.ok(fn('bimIsoStiffness')(-1, 0.3).error); assert.ok(fn('bimIsoStiffness')(1, 0.5).error); assert.ok(fn('bimIsoStiffness')(1, -1).error);
});

test('WO-17 orthotropic compliance from nine constants, minor ratios by reciprocity, refused when not positive definite', () => {
  const c = { E1: 12, E2: 0.8, E3: 0.5, G23: 0.06, G13: 0.7, G12: 0.75, nu12: 0.4, nu13: 0.45, nu23: 0.6 };
  const S = fn('bimOrthoCompliance')(c);
  near(S[0][0], 1 / 12); near(S[1][1], 1 / 0.8); near(S[2][2], 2);
  near(S[0][1], -0.4 / 12); near(S[1][0], -0.4 / 12, 1e-15, 'symmetric: S21 = -nu21/E2 = -nu12/E1');
  near(S[0][2], -0.45 / 12); near(S[1][2], -0.6 / 0.8); near(S[2][1], -0.6 / 0.8);
  near(S[3][3], 1 / (2 * 0.06), 1e-12, 'Mandel shear: 1/(2 G23)'); near(S[4][4], 1 / 1.4); near(S[5][5], 1 / 1.5);
  near(S[0][3], 0, 0);
  assert.ok(fn('bimOrthoCompliance')(Object.assign({}, c, { G12: 0 })).error, 'a zero modulus');
  assert.ok(fn('bimOrthoCompliance')(Object.assign({}, c, { nu23: 2 })).error, 'not positive definite');
});

test('WO-18 timber from the Wood Handbook (FPL-GTR-282, 2021, Tables 5-1 and 5-2): Douglas-fir', () => {
  const df = { ET_EL: 0.050, ER_EL: 0.068, GLR_EL: 0.064, GLT_EL: 0.078, GRT_EL: 0.007, muLR: 0.292, muLT: 0.449, muRT: 0.390 };
  const S = fn('bimWoodOrtho')(13.4e9, df), EL = 13.4e9;
  near(S[0][0] * EL, 1, 1e-12, 'axis 1 is longitudinal'); near(S[1][1] * EL, 1 / 0.068, 1e-9, 'axis 2 radial'); near(S[2][2] * EL, 20, 1e-9, 'axis 3 tangential');
  near(S[0][1] * EL, -0.292, 1e-12); near(S[0][2] * EL, -0.449, 1e-12); near(S[1][2] * EL, -0.390 / 0.068, 1e-9);
  near(S[3][3] * EL, 1 / 0.014, 1e-9, 'G_RT on the 23 shear'); near(S[4][4] * EL, 1 / 0.156, 1e-9, 'G_LT on 13'); near(S[5][5] * EL, 1 / 0.128, 1e-9, 'G_LR on 12');
  assert.ok(fn('bimWoodOrtho')(13.4e9, Object.assign({}, df, { GRT_EL: null })).error, 'a dash in Table 5-1');
  assert.ok(fn('bimWoodOrtho')(0, df).error);
});

test('WO-19 the inverse of a 6x6 (stiffness from compliance), with pivoting; singular refused', () => {
  const inv = fn('bimInv6'), C = fn('bimIsoStiffness')(30e9, 0.2), S = inv(C);
  for (let i = 0; i < 6; i++) for (let j = 0; j < 6; j++) { let s = 0; for (let k = 0; k < 6; k++) s += C[i][k] * S[k][j]; near(s, i === j ? 1 : 0, 1e-12); }
  near(S[0][0], 1 / 30e9, 1e-24, 'isotropic compliance 1/E'); near(S[0][1], -0.2 / 30e9, 1e-24, '-nu/E');
  const P = [[0, 1, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0], [0, 0, 2, 0, 0, 0], [0, 0, 0, 4, 0, 0], [0, 0, 0, 0, 5, 0], [0, 0, 0, 0, 0, 8]];
  const Pi = inv(P); near(Pi[0][1], 1, 1e-15, 'a zero first pivot needs a row swap'); near(Pi[5][5], 0.125, 1e-15);
  assert.ok(inv([[1, 2, 0, 0, 0, 0], [2, 4, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]]).error, 'singular');
  assert.ok(inv([[1]]).error, 'not 6x6');
});
