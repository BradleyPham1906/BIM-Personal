

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
