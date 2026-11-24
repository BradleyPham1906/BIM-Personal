/* e06 (H6): rotating a symmetric rank 2 tensor in Mandel form is an orthogonal 6x6 map; Voigt is not, and its
   inner product needs the factor 2 on the shear strains */
import { rotSym, mandelRot, symToMandel, mandelToSym, matMulN, matTN, matVecN, qToMat, randUnitQ, rng } from './ref.mjs';
var R = rng(6), eOrth = 0, eRot = 0, eEnergyV = 0, eEnergyM = 0, eVoigtOrth = 0, k, i;
function rsym() { var a = [R() - .5, R() - .5, R() - .5, R() - .5, R() - .5, R() - .5]; return [a[0], a[5], a[4], a[5], a[1], a[3], a[4], a[3], a[2]]; }
function dd(a, b) { var s = 0, i; for (i = 0; i < 9; i++) s += a[i]*b[i]; return s; }
function voigtRotStress(Rm) { /* Voigt stress rotation built the same way as Mandel's, from basis tensors */
  var T = [], e, c, i, k; for (i = 0; i < 36; i++) T.push(0);
  for (k = 0; k < 6; k++) { e = [0, 0, 0, 0, 0, 0]; e[k] = 1;
    var m = [e[0], e[5], e[4], e[5], e[1], e[3], e[4], e[3], e[2]], r = rotSym(Rm, m);
    c = [r[0], r[4], r[8], r[5], r[2], r[1]]; for (i = 0; i < 6; i++) T[6*i + k] = c[i]; }
  return T;
}
for (k = 0; k < 20000; k++) {
  var Rm = qToMat(randUnitQ(R)), Q = mandelRot(Rm), QtQ = matMulN(matTN(Q, 6), Q, 6);
  for (i = 0; i < 36; i++) eOrth = Math.max(eOrth, Math.abs(QtQ[i] - (i % 7 === 0 ? 1 : 0)));
  var T = voigtRotStress(Rm), TtT = matMulN(matTN(T, 6), T, 6);
  for (i = 0; i < 36; i++) eVoigtOrth = Math.max(eVoigtOrth, Math.abs(TtT[i] - (i % 7 === 0 ? 1 : 0)));
  var s = rsym(), e = rsym(), direct = rotSym(Rm, s), viaQ = mandelToSym(matVecN(Q, symToMandel(s), 6));
  for (i = 0; i < 9; i++) eRot = Math.max(eRot, Math.abs(direct[i] - viaQ[i]));
  var full = dd(s, e), sm = symToMandel(s), em = symToMandel(e), m = 0, v = 0;
  for (i = 0; i < 6; i++) m += sm[i]*em[i];
  var sv = [s[0], s[4], s[8], s[5], s[2], s[1]], ev = [e[0], e[4], e[8], 2*e[5], 2*e[2], 2*e[1]];
  for (i = 0; i < 6; i++) v += sv[i]*ev[i];
  eEnergyM = Math.max(eEnergyM, Math.abs(m - full)); eEnergyV = Math.max(eEnergyV, Math.abs(v - full));
}
console.log(JSON.stringify({ experiment: 'e06', samples: 20000, mandel_QtQ_minus_I: eOrth, voigt_stress_TtT_minus_I: eVoigtOrth,
  mandel_rotation_vs_direct: eRot, energy_mandel_err: eEnergyM, energy_voigt_engineering_shear_err: eEnergyV }));
