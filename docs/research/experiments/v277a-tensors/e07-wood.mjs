/* e07 (H7): the Wood Handbook's orthotropic constants (FPL-GTR-282, 2021, Tables 5-1 and 5-2, ~12% MC):
   reciprocity nu_ij/E_i = nu_ji/E_j, and whether the compliance is positive definite. Axes 1 L, 2 R, 3 T.
   Values transcribed for every species with all six Poisson's ratios and all five elastic ratios. */
import { eigJacobi } from './ref.mjs';
var T = {   /* ET/EL, ER/EL, GLR/EL, GLT/EL, GRT/EL ; muLR, muLT, muRT, muTR, muRL, muTL */
  'Balsa': [0.015, 0.046, 0.054, 0.037, 0.005, 0.229, 0.488, 0.665, 0.231, 0.018, 0.009],
  'Birch, yellow': [0.050, 0.078, 0.074, 0.068, 0.017, 0.426, 0.451, 0.697, 0.426, 0.043, 0.024],
  'Mahogany, African': [0.050, 0.111, 0.088, 0.059, 0.021, 0.297, 0.641, 0.604, 0.264, 0.033, 0.032],
  'Mahogany, Honduras': [0.064, 0.107, 0.066, 0.086, 0.028, 0.314, 0.533, 0.600, 0.326, 0.033, 0.034],
  'Sweetgum': [0.050, 0.115, 0.089, 0.061, 0.021, 0.325, 0.403, 0.682, 0.309, 0.044, 0.023],
  'Walnut, black': [0.056, 0.106, 0.085, 0.062, 0.021, 0.495, 0.632, 0.718, 0.367, 0.052, 0.036],
  'Yellow-poplar': [0.043, 0.092, 0.075, 0.069, 0.011, 0.318, 0.392, 0.703, 0.329, 0.030, 0.019],
  'Douglas-fir': [0.050, 0.068, 0.064, 0.078, 0.007, 0.292, 0.449, 0.390, 0.374, 0.036, 0.029],
  'Spruce, Sitka': [0.043, 0.078, 0.064, 0.061, 0.003, 0.372, 0.467, 0.435, 0.245, 0.040, 0.025],
  'Spruce, Engelmann': [0.059, 0.128, 0.124, 0.120, 0.010, 0.422, 0.462, 0.530, 0.255, 0.083, 0.058]
};
function compliance(E1, E2, E3, n12, n13, n21, n23, n31, n32) {   /* the normal 3x3 block, symmetrised; and its asymmetry */
  var S = [1/E1, -n21/E2, -n31/E3, -n12/E1, 1/E2, -n32/E3, -n13/E1, -n23/E2, 1/E3];
  var asym = { S12_vs_S21: Math.abs(S[1] - S[3])/Math.abs(S[1]), S13_vs_S31: Math.abs(S[2] - S[6])/Math.abs(S[2]), S23_vs_S32: Math.abs(S[5] - S[7])/Math.abs(S[5]) };
  var Ss = [S[0], (S[1] + S[3])/2, (S[2] + S[6])/2, (S[1] + S[3])/2, S[4], (S[5] + S[7])/2, (S[2] + S[6])/2, (S[5] + S[7])/2, S[8]];
  return { asym: asym, minEig: Math.min.apply(null, eigJacobi(Ss).val) };
}
var rows = [], k;
for (k in T) {
  var r = T[k], E1 = 1, E3 = r[0], E2 = r[1];
  /* muLR = nu_12, muLT = nu_13, muRT = nu_23, muTR = nu_32, muRL = nu_21, muTL = nu_31 */
  var c = compliance(E1, E2, E3, r[5], r[6], r[9], r[7], r[10], r[8]);
  /* the alternative the Handbook's note points to: keep the well measured major ratios, derive the minor ones */
  var d = compliance(E1, E2, E3, r[5], r[6], r[5]*E2/E1, r[7], r[6]*E3/E1, r[7]*E3/E2);
  rows.push({ species: k, asym_as_tabulated: c.asym, minEig_symmetrised: c.minEig, minEig_minor_from_reciprocity: d.minEig,
    derived_muRL: +(r[5]*E2/E1).toFixed(4), tabulated_muRL: r[9], derived_muTL: +(r[6]*E3/E1).toFixed(4), tabulated_muTL: r[10] });
}
console.log(JSON.stringify({ experiment: 'e07', source: 'FPL-GTR-282 (2021) Tables 5-1, 5-2', rows: rows }, null, 1));
