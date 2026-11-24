/* e05 (H5): symmetric 3x3 eigenproblems, Jacobi against the trigonometric closed form, on random, near-degenerate
   and wide-magnitude matrices (a thin rod's inertia, a stress state with one tiny component) */
import { eigJacobi, eigTrig, qToMat, randUnitQ, matMul3, matT3, rng } from './ref.mjs';
var R = rng(5);
function build(l, Q) { var D = [l[0], 0, 0, 0, l[1], 0, 0, 0, l[2]]; return matMul3(matMul3(Q, D), matT3(Q)); }
function resid(A, lam, v) {
  var Av = [A[0]*v[0] + A[1]*v[1] + A[2]*v[2], A[3]*v[0] + A[4]*v[1] + A[5]*v[2], A[6]*v[0] + A[7]*v[1] + A[8]*v[2]];
  return Math.hypot(Av[0] - lam*v[0], Av[1] - lam*v[1], Av[2] - lam*v[2]);
}
function relValErr(got, exact) {
  var g = got.slice().sort(function (a, b) { return a - b; }), e = exact.slice().sort(function (a, b) { return a - b; }), m = 0, i;
  for (i = 0; i < 3; i++) m = Math.max(m, Math.abs(g[i] - e[i])/Math.abs(e[i]));
  return m;
}
var cases = {
  random: function () { return [R()*10 + .1, R()*10 + .1, R()*10 + .1]; },
  near_degenerate_1e_10: function () { var a = R() + 1; return [a, a*(1 + 1e-10), R() + 3]; },
  wide_1e_8: function () { return [1, 1, 1e-8]; },
  wide_1e_12: function () { return [1e-12, 1, 1]; },
  exactly_double: function () { return [2, 2, 5]; }
};
var out = {}, k;
for (k in cases) {
  var vJ = 0, vT = 0, rJ = 0, rT = 0, n;
  for (n = 0; n < 5000; n++) {
    var l = cases[k](), Q = qToMat(randUnitQ(R)), A = build(l, Q), J = eigJacobi(A), T = eigTrig(A), i, nrm = Math.max(Math.abs(l[0]), Math.abs(l[1]), Math.abs(l[2]));
    vJ = Math.max(vJ, relValErr(J.val, l)); vT = Math.max(vT, relValErr(T.val, l));
    for (i = 0; i < 3; i++) {
      rJ = Math.max(rJ, resid(A, J.val[i], [J.vec[i], J.vec[3 + i], J.vec[6 + i]])/nrm);
      rT = Math.max(rT, resid(A, T.val[i], T.vecs[i])/nrm);
    }
  }
  out[k] = { jacobi_rel_value_err: vJ, trig_rel_value_err: vT, jacobi_resid: rJ, trig_resid: rT };
}
var t0 = Date.now(), A0 = build([3, 2, 1], qToMat(randUnitQ(R))), z = 0, m;
for (m = 0; m < 1e6; m++) z += eigJacobi(A0).val[0];
var tJ = (Date.now() - t0)*1e6/1e6; t0 = Date.now();   /* ms for 1e6 calls = ns per call */
for (m = 0; m < 1e6; m++) z += eigTrig(A0).val[0];
var tT = (Date.now() - t0)*1e6/1e6;
console.log(JSON.stringify({ experiment: 'e05', samples: 5000, cases: out, ns_per_call: { jacobi: tJ, trig: tT }, sink: z > 0 }));
