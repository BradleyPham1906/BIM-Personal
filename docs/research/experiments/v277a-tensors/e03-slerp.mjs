/* e03: slerp's switch to lerp for near-equal quaternions: three.js (0.9995, renormalised) against gl-matrix (1-1e-6, not) */
import { qslerp, qnorm, qmul, qExp, qFromAxisAngle, randUnitQ, rng } from './ref.mjs';
var R = rng(3), rows = [];
[1e-1, 3.2e-2, 1e-2, 1e-3, 1e-5].forEach(function (ang) {
  var eA = 0, nA = 0, eB = 0, nB = 0, k, t;
  for (k = 0; k < 2000; k++) {
    var a = randUnitQ(R), ax = [R() - .5, R() - .5, R() - .5], n = Math.hypot(ax[0], ax[1], ax[2]); ax = [ax[0]/n, ax[1]/n, ax[2]/n];
    var b = qmul(qFromAxisAngle(ax, ang), a);
    for (t = 0.1; t < 1; t += 0.2) {
      var exact = qmul(qFromAxisAngle(ax, ang*t), a);
      var A = qslerp(a, b, t, 0.9995, true), B = qslerp(a, b, t, 1 - 1e-6, false);
      var dA = Math.abs(A[0]*exact[0] + A[1]*exact[1] + A[2]*exact[2] + A[3]*exact[3])/qnorm(A), dB = Math.abs(B[0]*exact[0] + B[1]*exact[1] + B[2]*exact[2] + B[3]*exact[3])/qnorm(B);
      eA = Math.max(eA, 2*Math.acos(Math.min(1, dA))); eB = Math.max(eB, 2*Math.acos(Math.min(1, dB)));
      nA = Math.max(nA, Math.abs(qnorm(A) - 1)); nB = Math.max(nB, Math.abs(qnorm(B) - 1));
    }
  }
  rows.push({ separation_rad: ang, three_angle_err_rad: eA, three_norm_err: nA, glmatrix_angle_err_rad: eB, glmatrix_norm_err: nB });
});
console.log(JSON.stringify({ experiment: 'e03', rows: rows }));
