/* e01 (H2): does a quaternion or a matrix stay a rotation under a million compositions? Renormalised or not. */
import { qmul, qnorm, qnormalize, qToMat, matMul3, orthoErr, randUnitQ, rng, qExp } from './ref.mjs';
var R = rng(277), N = 1000000, small = [], i;
for (i = 0; i < 1000; i++) { var q = randUnitQ(R), s = 1e-2; small.push(qExp([(R() - .5)*s, (R() - .5)*s, (R() - .5)*s])); }
var qa = [0, 0, 0, 1], qb = [0, 0, 0, 1], M = [1, 0, 0, 0, 1, 0, 0, 0, 1], worstA = 0, worstB = 0;
for (i = 0; i < N; i++) {
  var d = small[i % 1000];
  qa = qmul(d, qa);
  qb = qnormalize(qmul(d, qb));
  if (i % 1000 === 999) { worstA = Math.max(worstA, Math.abs(qnorm(qa) - 1)); worstB = Math.max(worstB, Math.abs(qnorm(qb) - 1)); }
  if (i < 100000) M = matMul3(qToMat(d), M);
}
console.log(JSON.stringify({ experiment: 'e01', compositions: N,
  quat_no_renorm_max_norm_err: worstA, quat_renorm_max_norm_err: worstB,
  matrix_1e5_products_orthogonality_err: orthoErr(M), node: process.version }));
