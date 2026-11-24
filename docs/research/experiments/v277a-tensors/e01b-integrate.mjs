/* e01b: drift from integrating orientation at 60 Hz for an hour of spin (216,000 steps): the first-order update
   q += dt/2 (w x q) against the exact exp-map update q = Exp(w dt) x q (Sola 2017 eq. 201 and 101), each with and
   without renormalisation, and the orientation error against the closed form for a constant world angular velocity */
import { qmul, qnorm, qnormalize, qExp, qToMat, matDiff3 } from './ref.mjs';
var w = [0.3, 1.2, -0.7], dt = 1/60, N = 216000, i;
var qa = [0, 0, 0, 1], qb = [0, 0, 0, 1], qc = [0, 0, 0, 1], step = qExp([w[0]*dt, w[1]*dt, w[2]*dt]);
for (i = 0; i < N; i++) {
  var d = qmul([w[0], w[1], w[2], 0], qa);
  qa = [qa[0] + dt/2*d[0], qa[1] + dt/2*d[1], qa[2] + dt/2*d[2], qa[3] + dt/2*d[3]];
  var e = qmul([w[0], w[1], w[2], 0], qb);
  qb = qnormalize([qb[0] + dt/2*e[0], qb[1] + dt/2*e[1], qb[2] + dt/2*e[2], qb[3] + dt/2*e[3]]);
  qc = qmul(step, qc);
}
var exact = qExp([w[0]*dt*N, w[1]*dt*N, w[2]*dt*N]);
console.log(JSON.stringify({ experiment: 'e01b', steps: N, dt: dt,
  first_order_norm_after: qnorm(qa), first_order_matrix_err: matDiff3(qToMat(qa), qToMat(exact)),
  first_order_renorm_matrix_err: matDiff3(qToMat(qb), qToMat(exact)),
  expmap_norm_err: Math.abs(qnorm(qc) - 1), expmap_matrix_err: matDiff3(qToMat(qc), qToMat(exact)) }));
