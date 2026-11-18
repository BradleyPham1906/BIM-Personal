

  /* ================= __acad3dV187: Freeform F5, point editing and blends, the pure part =================
     docs/research/research-freeform-f1-f7.md (F5) and docs/work-orders/v187/SPEC.md. Editing NURBS curves by their data:
     knot insertion (The NURBS Book A5.1), moving a control point, G1 blends, Bezier degree elevation, reversal. Each
     function is a work order, added below as it is built; none uses another file's names. */

/* __acad3dV187 WO-01: bimNeKnotInsert, Boehm knot insertion (The NURBS Book A5.1), pure. */
function bimNeKnotInsert(c, u) {
  var p = c.deg, pts = c.pts, knots = c.knots, w = c.w, n = pts.length - 1;
  var i, s, j, a, wi, wj, x, y, z, weight;
  if (!(knots[p] < u && u < knots[pts.length])) {
    return null;
  }
  s = p;
  while (s < knots.length - 1 && !(knots[s] <= u && u < knots[s + 1])) {
    s++;
  }
  var newKnots = knots.slice(0);
  newKnots.splice(s + 1, 0, u);
  var newPts = [], newW = [];
  for (i = 0; i <= n + 1; i++) {
    x = 0; y = 0; z = 0; weight = 0;
    if (i <= s - p) {
      j = i;
      wi = w ? w[j] : 1;
      x = pts[j][0] * wi; y = pts[j][1] * wi; z = pts[j][2] * wi; weight = wi;
    } else if (i > s) {
      j = i - 1;
      wi = w ? w[j] : 1;
      x = pts[j][0] * wi; y = pts[j][1] * wi; z = pts[j][2] * wi; weight = wi;
    } else {
      a = (u - knots[i]) / (knots[i + p] - knots[i]);
      wi = w ? w[i] : 1; wj = w ? w[i - 1] : 1;
      x = a * pts[i][0] * wi + (1 - a) * pts[i - 1][0] * wj;
      y = a * pts[i][1] * wi + (1 - a) * pts[i - 1][1] * wj;
      z = a * pts[i][2] * wi + (1 - a) * pts[i - 1][2] * wj;
      weight = a * wi + (1 - a) * wj;
    }
    newPts.push([x / weight, y / weight, z / weight]);
    if (w) {
      newW.push(weight);
    }
  }
  var out = { deg: p, pts: newPts, knots: newKnots };
  if (w) {
    out.w = newW;
  }
  return out;
}
/* __acad3dV187 WO-02: bimNeMovePoint, move control point i by d, pure. */
function bimNeMovePoint(c, i, d) {
  var pts = c.pts, n = pts.length, j, p, w, out;
  if (!(i >= 0 && i < n)) return null;
  var newPts = [];
  for (j = 0; j < n; j++) {
    p = pts[j];
    if (j === i) newPts.push([p[0] + d[0], p[1] + d[1], p[2] + d[2]]);
    else newPts.push([p[0], p[1], p[2]]);
  }
  w = [];
  for (j = 0; j < (c.w ? c.w.length : 0); j++) w.push(c.w[j]);
  out = { deg: c.deg, pts: newPts, knots: c.knots.slice(0) };
  if (c.w) out.w = w;
  return out;
}


/* __acad3dV187 WO-03: bimNeBlend, G1 cubic blend between two curve ends, pure. */
function bimNeBlend(p0, t0, p1, t1, k) {
  var s, l0, l1, h0, h1, pts;
  l0 = Math.hypot(t0[0], t0[1], t0[2]);
  l1 = Math.hypot(t1[0], t1[1], t1[2]);
  s = k > 0 ? k : Math.hypot(p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]) / 3;
  if (l0 === 0) l0 = 1;
  if (l1 === 0) l1 = 1;
  h0 = [t0[0] / l0 * s, t0[1] / l0 * s, t0[2] / l0 * s];
  h1 = [t1[0] / l1 * s, t1[1] / l1 * s, t1[2] / l1 * s];
  pts = [p0.slice(0), [p0[0] + h0[0], p0[1] + h0[1], p0[2] + h0[2]], [p1[0] - h1[0], p1[1] - h1[1], p1[2] - h1[2]], p1.slice(0)];
  return { deg: 3, pts: pts, knots: [0, 0, 0, 0, 1, 1, 1, 1] };
}
/* __acad3dV187 WO-04: bimNeElevate, raise Bezier points one degree, pure. */
function bimNeElevate(P) {
  var n = P.length - 1, i, Q = [];
  Q.push([P[0][0], P[0][1], P[0][2]]);
  for (i = 1; i <= n; i++) {
    Q.push([(i / (n + 1)) * P[i - 1][0] + (1 - i / (n + 1)) * P[i][0],
            (i / (n + 1)) * P[i - 1][1] + (1 - i / (n + 1)) * P[i][1],
            (i / (n + 1)) * P[i - 1][2] + (1 - i / (n + 1)) * P[i][2]]);
  }
  Q.push([P[n][0], P[n][1], P[n][2]]);
  return Q;
}

