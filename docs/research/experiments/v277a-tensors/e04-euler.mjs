/* e04 (H4): Euler ZYX round trip, and how close to +-90 degrees of pitch it breaks */
import { eulerZYXToMat, matToEulerZYX, matDiff3, rng } from './ref.mjs';
var R = rng(4), rows = [];
[0.5, 1.0, 1.5, Math.PI/2 - 1e-3, Math.PI/2 - 1e-5, Math.PI/2 - 1e-7, Math.PI/2 - 1e-9, Math.PI/2].forEach(function (th) {
  var eAng = 0, eMat = 0, k;
  for (k = 0; k < 2000; k++) {
    var phi = (R() - .5)*2*Math.PI*0.99, psi = (R() - .5)*2*Math.PI*0.99, M = eulerZYXToMat(phi, th, psi), e = matToEulerZYX(M);
    eMat = Math.max(eMat, matDiff3(eulerZYXToMat(e[0], e[1], e[2]), M));
    eAng = Math.max(eAng, Math.abs(e[0] - phi), Math.abs(e[1] - th), Math.abs(e[2] - psi));
  }
  rows.push({ pitch_rad: th, max_angle_err_rad: eAng, max_matrix_err: eMat });
});
console.log(JSON.stringify({ experiment: 'e04', rows: rows }));
