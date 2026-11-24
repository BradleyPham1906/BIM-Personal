/* e02 (H3): matrix to quaternion near 180 degrees: the trace-only formula against Shepperd's pivot */
import { qFromAxisAngle, qToMat, matToQTrace, matToQShepperd, matDiff3, rng } from './ref.mjs';
var R = rng(2), rows = [], angles = [0, 1, 2, 3, Math.PI - 1e-2, Math.PI - 1e-4, Math.PI - 1e-6, Math.PI - 1e-8, Math.PI];
angles.forEach(function (t) {
  var eT = 0, eS = 0, k;
  for (k = 0; k < 2000; k++) {
    var a = [R() - .5, R() - .5, R() - .5], n = Math.hypot(a[0], a[1], a[2]); a = [a[0]/n, a[1]/n, a[2]/n];
    var M = qToMat(qFromAxisAngle(a, t));
    eT = Math.max(eT, matDiff3(qToMat(matToQTrace(M)), M) || (isNaN(matDiff3(qToMat(matToQTrace(M)), M)) ? Infinity : 0));
    eS = Math.max(eS, matDiff3(qToMat(matToQShepperd(M)), M));
  }
  rows.push({ angle_rad: t, trace_only_max_err: eT, shepperd_max_err: eS });
});
console.log(JSON.stringify({ experiment: 'e02', samples_per_angle: 2000, rows: rows }));
