  /* ================= __acad3dV183: Freeform F1, NURBS curves, the pure part =================
     docs/research/research-freeform-f1-f7.md (F1) and docs/work-orders/v183/SPEC.md. NURBS curves: clamped knots, the
     knot span, the basis functions (The NURBS Book A2.1, A2.2), rational points, tangents, adaptive samples. Each function
     is a work order, added below as it is built; none uses another file's names. */
function bimNurbsKnots(n, p) {
  if (!(n > p && p >= 1)) return [];
  var kv = [];
  for (var i = 0; i <= p; i++) kv.push(0);
  for (var i = 1; i <= n - p - 1; i++) kv.push(i / (n - p));
  for (var i = 0; i <= p; i++) kv.push(1);
  return kv;
}

function bimNurbsSpan(n, p, u, k) {
  if (u >= k[n]) return n - 1;
  if (u <= k[p]) return p;
  var low = p;
  var high = n - 1;
  while (high > low) {
    var mid = Math.floor((low + high + 1) / 2);
    if (u >= k[mid]) low = mid;
    else high = mid - 1;
  }
  return low;
}

function bimNurbsBasis(span, u, p, k) {
  var N = [];
  for (var i = 0; i <= p; i++) N[i] = 0;
  N[0] = 1;
  var left = [];
  var right = [];
  for (var j = 1; j <= p; j++) {
    left[j] = u - k[span + 1 - j];
    right[j] = k[span + j] - u;
    var saved = 0;
    for (var r = 0; r < j; r++) {
      var denom = right[r + 1] + left[j - r];
      var temp = denom !== 0 ? N[r] / denom : 0;
      N[r] = saved + right[r + 1] * temp;
      saved = left[j - r] * temp;
    }
    N[j] = saved;
  }
  return N;
}

function bimNurbsPoint(c, u) {
  var p = c.deg, k = c.knots, n = c.pts.length;
  var span = bimNurbsSpan(n, p, u, k), N = bimNurbsBasis(span, u, p, k);
  var x = 0, y = 0, z = 0, sw = 0, i, q, w, b;
  for (i = 0; i <= p; i++) {
    q = c.pts[span - p + i];
    w = (c.w && typeof c.w[span - p + i] === 'number') ? c.w[span - p + i] : 1;
    b = w * N[i];
    x += q[0] * b; y += q[1] * b; z += (q[2] || 0) * b; sw += b;
  }
  return [x / sw, y / sw, z / sw];
}

function bimNurbsTangent(c, u, h) {
  if (!(typeof h === 'number' && h > 0)) h = 1e-6;
  var a = Math.max(0, u - h), b = Math.min(1, u + h);
  if (b <= a) return [0, 0, 0];
  var Pa = bimNurbsPoint(c, a), Pb = bimNurbsPoint(c, b), d = b - a;
  return [(Pb[0] - Pa[0]) / d, (Pb[1] - Pa[1]) / d, (Pb[2] - Pa[2]) / d];
}

function bimNurbsSample(c, tol) {
  if (!(typeof tol === 'number' && tol > 0)) tol = 0.001;
  var out = [bimNurbsPoint(c, 0)];
  // the distance of M from the chord A B (from A when the chord has no length)
  function off(A, B, M) {
    var dx = B[0] - A[0], dy = B[1] - A[1], dz = B[2] - A[2];
    var mx = M[0] - A[0], my = M[1] - A[1], mz = M[2] - A[2];
    var L2 = dx * dx + dy * dy + dz * dz, t = L2 > 0 ? (mx * dx + my * dy + mz * dz) / L2 : 0;
    var ex = mx - t * dx, ey = my - t * dy, ez = mz - t * dz;
    return Math.sqrt(ex * ex + ey * ey + ez * ez);
  }
  function split(a, b, Pa, Pb) {
    var m = (a + b) / 2, Pm = bimNurbsPoint(c, m);
    if ((off(Pa, Pb, Pm) > tol || b - a > 0.25) && b - a > 1e-6) {
      split(a, m, Pa, Pm);
      split(m, b, Pm, Pb);
      return;
    }
    out.push(Pb);
  }
  split(0, 1, out[0], bimNurbsPoint(c, 1));
  return out;
}
