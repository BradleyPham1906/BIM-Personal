/* V277a research: reference implementations used by the experiments e01 to e08 (data scripts, not a suite).
   ES5 style on purpose, so the timings reflect code the engine could ship. Conventions under test:
   quaternion [x, y, z, w], Hamilton algebra (ij = k), active rotation v' = q v q*; 3x3 matrices row-major;
   symmetric rank 2 in Voigt order [11, 22, 33, 23, 13, 12]. */

export function qmul(a, b) {
  return [a[3]*b[0] + a[0]*b[3] + a[1]*b[2] - a[2]*b[1],
          a[3]*b[1] - a[0]*b[2] + a[1]*b[3] + a[2]*b[0],
          a[3]*b[2] + a[0]*b[1] - a[1]*b[0] + a[2]*b[3],
          a[3]*b[3] - a[0]*b[0] - a[1]*b[1] - a[2]*b[2]];
}
export function qnorm(q) { return Math.sqrt(q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3]); }
export function qnormalize(q) { var n = qnorm(q); return [q[0]/n, q[1]/n, q[2]/n, q[3]/n]; }
export function qrot(q, v) {
  var x = q[0], y = q[1], z = q[2], w = q[3];
  var tx = 2*(y*v[2] - z*v[1]), ty = 2*(z*v[0] - x*v[2]), tz = 2*(x*v[1] - y*v[0]);
  return [v[0] + w*tx + (y*tz - z*ty), v[1] + w*ty + (z*tx - x*tz), v[2] + w*tz + (x*ty - y*tx)];
}
export function qFromAxisAngle(a, t) {
  var s = Math.sin(t/2); return [a[0]*s, a[1]*s, a[2]*s, Math.cos(t/2)];
}
/* exp map of a rotation vector phi (radians), Taylor near zero (Sola 2017, eq. 101 and its small-angle form) */
export function qExp(p) {
  var t = Math.sqrt(p[0]*p[0] + p[1]*p[1] + p[2]*p[2]), s, c;
  if (t < 1e-8) { s = 0.5 - t*t/48; c = 1 - t*t/8; }
  else { s = Math.sin(t/2)/t; c = Math.cos(t/2); }
  return [p[0]*s, p[1]*s, p[2]*s, c];
}
export function qToMat(q) {
  var x = q[0], y = q[1], z = q[2], w = q[3];
  return [1 - 2*(y*y + z*z), 2*(x*y - z*w), 2*(x*z + y*w),
          2*(x*y + z*w), 1 - 2*(x*x + z*z), 2*(y*z - x*w),
          2*(x*z - y*w), 2*(y*z + x*w), 1 - 2*(x*x + y*y)];
}
/* trace-only conversion: correct only while w is not small */
export function matToQTrace(m) {
  var w = 0.5*Math.sqrt(Math.max(0, 1 + m[0] + m[4] + m[8])), f = 1/(4*w);
  return [(m[7] - m[5])*f, (m[2] - m[6])*f, (m[3] - m[1])*f, w];
}
/* Shepperd 1978: take the largest of w^2, x^2, y^2, z^2 (from the trace and the diagonal) as the pivot */
export function matToQShepperd(m) {
  var t = m[0] + m[4] + m[8], r, s;
  if (t >= m[0] && t >= m[4] && t >= m[8]) {
    r = Math.sqrt(1 + t); s = 0.5/r;
    return [(m[7] - m[5])*s, (m[2] - m[6])*s, (m[3] - m[1])*s, 0.5*r];
  }
  if (m[0] >= m[4] && m[0] >= m[8]) {
    r = Math.sqrt(1 + m[0] - m[4] - m[8]); s = 0.5/r;
    return [0.5*r, (m[1] + m[3])*s, (m[2] + m[6])*s, (m[7] - m[5])*s];
  }
  if (m[4] >= m[8]) {
    r = Math.sqrt(1 - m[0] + m[4] - m[8]); s = 0.5/r;
    return [(m[1] + m[3])*s, 0.5*r, (m[5] + m[7])*s, (m[2] - m[6])*s];
  }
  r = Math.sqrt(1 - m[0] - m[4] + m[8]); s = 0.5/r;
  return [(m[2] + m[6])*s, (m[5] + m[7])*s, 0.5*r, (m[3] - m[1])*s];
}
/* slerp (Shoemake 1985) with the shorter arc; below the threshold, lerp and optionally renormalise */
export function qslerp(a, b, t, thresh, renorm) {
  var d = a[0]*b[0] + a[1]*b[1] + a[2]*b[2] + a[3]*b[3], bb = b, s0, s1, o, so, r;
  if (d < 0) { d = -d; bb = [-b[0], -b[1], -b[2], -b[3]]; }
  if (d < thresh) { o = Math.acos(d); so = Math.sin(o); s0 = Math.sin((1 - t)*o)/so; s1 = Math.sin(t*o)/so; }
  else { s0 = 1 - t; s1 = t; }
  r = [s0*a[0] + s1*bb[0], s0*a[1] + s1*bb[1], s0*a[2] + s1*bb[2], s0*a[3] + s1*bb[3]];
  return (renorm && d >= thresh) ? qnormalize(r) : r;
}
/* Euler, R = Rz(psi) Ry(theta) Rx(phi) */
export function eulerZYXToMat(phi, theta, psi) {
  var cx = Math.cos(phi), sx = Math.sin(phi), cy = Math.cos(theta), sy = Math.sin(theta), cz = Math.cos(psi), sz = Math.sin(psi);
  return [cz*cy, cz*sy*sx - sz*cx, cz*sy*cx + sz*sx,
          sz*cy, sz*sy*sx + cz*cx, sz*sy*cx - cz*sx,
          -sy, cy*sx, cy*cx];
}
export function matToEulerZYX(m, eps) {
  var s = -m[6];
  if (s > 1) s = 1; if (s < -1) s = -1;
  var th = Math.asin(s);
  if (Math.abs(m[6]) > 1 - (eps || 1e-12)) return [0, th, Math.atan2(-m[1], m[4])];   /* gimbal lock: phi set to 0 */
  return [Math.atan2(m[7], m[8]), th, Math.atan2(m[3], m[0])];
}
export function matMul3(a, b) {
  var r = new Array(9), i, j;
  for (i = 0; i < 3; i++) for (j = 0; j < 3; j++) r[3*i + j] = a[3*i]*b[j] + a[3*i + 1]*b[3 + j] + a[3*i + 2]*b[6 + j];
  return r;
}
export function matT3(a) { return [a[0], a[3], a[6], a[1], a[4], a[7], a[2], a[5], a[8]]; }
export function matDiff3(a, b) { var e = 0, i; for (i = 0; i < 9; i++) e = Math.max(e, Math.abs(a[i] - b[i])); return e; }
export function orthoErr(m) { return matDiff3(matMul3(m, matT3(m)), [1, 0, 0, 0, 1, 0, 0, 0, 1]); }

/* symmetric 3x3 eigen, cyclic Jacobi: returns {val:[3], vec: row-major columns are eigenvectors} */
export function eigJacobi(A) {
  var a = A.slice(), v = [1, 0, 0, 0, 1, 0, 0, 0, 1], sweep, p, q, k, off, apq, th, t, c, s, tau, akp, akq, vkp, vkq, app, aqq;
  var pairs = [[0, 1], [0, 2], [1, 2]];
  for (sweep = 0; sweep < 50; sweep++) {
    off = a[1]*a[1] + a[2]*a[2] + a[5]*a[5];
    if (off === 0) break;
    for (k = 0; k < 3; k++) {
      p = pairs[k][0]; q = pairs[k][1]; apq = a[3*p + q];
      if (apq === 0) continue;
      app = a[4*p]; aqq = a[4*q];
      th = (aqq - app)/(2*apq);
      t = (th >= 0 ? 1 : -1)/(Math.abs(th) + Math.sqrt(th*th + 1));
      c = 1/Math.sqrt(t*t + 1); s = t*c; tau = s/(1 + c);
      for (var r = 0; r < 3; r++) {
        if (r === p || r === q) continue;
        akp = a[3*r + p]; akq = a[3*r + q];
        a[3*r + p] = a[3*p + r] = akp - s*(akq + tau*akp);
        a[3*r + q] = a[3*q + r] = akq + s*(akp - tau*akq);
      }
      a[4*p] = app - t*apq; a[4*q] = aqq + t*apq; a[3*p + q] = a[3*q + p] = 0;
      for (r = 0; r < 3; r++) {
        vkp = v[3*r + p]; vkq = v[3*r + q];
        v[3*r + p] = vkp - s*(vkq + tau*vkp); v[3*r + q] = vkq + s*(vkp - tau*vkq);
      }
    }
  }
  return {val: [a[0], a[4], a[8]], vec: v};
}
/* symmetric 3x3 eigenvalues, the trigonometric closed form (Smith 1961), vectors from cross products of rows of A - lI */
export function eigTrig(A) {
  var a00 = A[0], a11 = A[4], a22 = A[8], a01 = A[1], a02 = A[2], a12 = A[5];
  var p1 = a01*a01 + a02*a02 + a12*a12, l = [a00, a11, a22];
  if (p1 !== 0) {
    var q = (a00 + a11 + a22)/3, b00 = a00 - q, b11 = a11 - q, b22 = a22 - q;
    var p2 = b00*b00 + b11*b11 + b22*b22 + 2*p1, p = Math.sqrt(p2/6);
    var det = b00*(b11*b22 - a12*a12) - a01*(a01*b22 - a12*a02) + a02*(a01*a12 - b11*a02);
    var r = det/(2*p*p*p); if (r < -1) r = -1; if (r > 1) r = 1;
    var ph = Math.acos(r)/3;
    l = [q + 2*p*Math.cos(ph), 0, q + 2*p*Math.cos(ph + 2*Math.PI/3)]; l[1] = 3*q - l[0] - l[2];
  }
  var vec = [], i;
  for (i = 0; i < 3; i++) {
    var r0 = [a00 - l[i], a01, a02], r1 = [a01, a11 - l[i], a12], r2 = [a02, a12, a22 - l[i]];
    var c = [cross(r0, r1), cross(r0, r2), cross(r1, r2)], best = c[0], bn = dot(c[0], c[0]), j;
    for (j = 1; j < 3; j++) { var n = dot(c[j], c[j]); if (n > bn) { bn = n; best = c[j]; } }
    bn = Math.sqrt(bn) || 1; vec.push([best[0]/bn, best[1]/bn, best[2]/bn]);
  }
  return {val: l, vecs: vec};
}
export function cross(a, b) { return [a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0]]; }
export function dot(a, b) { return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]; }

/* symmetric rank 2 <-> full 3x3; Mandel and Voigt vectors */
var S2 = Math.SQRT2;
export function symToMandel(m) { return [m[0], m[4], m[8], S2*m[5], S2*m[2], S2*m[1]]; }
export function mandelToSym(v) {
  var a = v[3]/S2, b = v[4]/S2, c = v[5]/S2;
  return [v[0], c, b, c, v[1], a, b, a, v[2]];
}
export function rotSym(R, m) { return matMul3(matMul3(R, m), matT3(R)); }
/* the 6x6 Mandel rotation, column k = mandel(R E_k R^T) for the orthonormal Mandel basis E_k */
export function mandelRot(R) {
  var Q = [], k, e, col, i;
  for (i = 0; i < 36; i++) Q.push(0);
  for (k = 0; k < 6; k++) {
    e = [0, 0, 0, 0, 0, 0]; e[k] = 1;
    col = symToMandel(rotSym(R, mandelToSym(e)));
    for (i = 0; i < 6; i++) Q[6*i + k] = col[i];
  }
  return Q;
}
export function matMulN(a, b, n) {
  var r = [], i, j, k, s;
  for (i = 0; i < n; i++) for (j = 0; j < n; j++) { s = 0; for (k = 0; k < n; k++) s += a[n*i + k]*b[n*k + j]; r.push(s); }
  return r;
}
export function matTN(a, n) { var r = [], i, j; for (i = 0; i < n; i++) for (j = 0; j < n; j++) r.push(a[n*j + i]); return r; }
export function matVecN(a, v, n) { var r = [], i, k, s; for (i = 0; i < n; i++) { s = 0; for (k = 0; k < n; k++) s += a[n*i + k]*v[k]; r.push(s); } return r; }

/* a deterministic random source (mulberry32), so every run of an experiment is the same */
export function rng(seed) {
  var s = seed >>> 0;
  return function () {
    s = (s + 0x6D2B79F5) >>> 0; var t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0)/4294967296;
  };
}
export function randUnitQ(R) {
  var u1 = R(), u2 = R()*2*Math.PI, u3 = R()*2*Math.PI, a = Math.sqrt(1 - u1), b = Math.sqrt(u1);
  return [a*Math.sin(u2), a*Math.cos(u2), b*Math.sin(u3), b*Math.cos(u3)];   /* Shoemake's uniform random rotation */
}
