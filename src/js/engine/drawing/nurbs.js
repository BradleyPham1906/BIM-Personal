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
  var n = c.deg;
  var p = n;
  var k = c.knots;
  var m = c.pts.length - 1;
  
  // Handle boundary cases: u at or beyond the first/last knot
  // For a clamped curve with m+1 control points and degree p:
  // - u <= k[p] means u is at/before the first control point
  // - u >= k[m+1] means u is at/after the last control point
  if (u <= k[p]) {
    // Return first control point
    return [c.pts[0][0], c.pts[0][1], 0];
  }
  if (u >= k[m + 1]) {
    // Return last control point
    return [c.pts[m][0], c.pts[m][1], 0];
  }
  
  // Interior case: compute rational point using direct basis function calculation
  // Find span: the largest i such that k[i] <= u
  var span = p;
  while (span < m && u >= k[span + 1]) {
    span++;
  }
  
  // Compute basis functions N[i](u) for i = span-p, ..., span
  // Using the standard de Boor recurrence
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
  
  // Compute weighted sum for rational point
  var weightedSumX = 0;
  var weightedSumY = 0;
  var weightedSumW = 0;
  var iMin = span - p;
  if (iMin < 0) iMin = 0;
  var iMax = span;
  if (iMax > m) iMax = m;
  for (var i = iMin; i <= iMax; i++) {
    var w = (c.w && c.w[i] !== undefined) ? c.w[i] : 1;
    var px = c.pts[i][0];
    var py = c.pts[i][1];
    var basisIdx = i - iMin;
    if (basisIdx >= 0 && basisIdx <= p) {
      weightedSumX += px * w * N[basisIdx];
      weightedSumY += py * w * N[basisIdx];
      weightedSumW += w * N[basisIdx];
    }
  }
  var x = weightedSumX / weightedSumW;
  var y = weightedSumY / weightedSumW;
  return [x, y, 0];
}

function bimNurbsTangent(c, u) {
  var h = 1e-6, a = u - h, b = u + h;
  if (a < 0) a = 0;
  if (b > 1) b = 1;
  if (b <= a) return [0, 0, 0];
  
  // Compute points at a and b using bimNurbsPoint
  var Pa = bimNurbsPoint(c, a);
  var Pb = bimNurbsPoint(c, b);
  
  // Central difference: (Pb - Pa) / (b - a)
  var dx = Pb[0] - Pa[0];
  var dy = Pb[1] - Pa[1];
  var dt = b - a;
  
  if (dt === 0) return [0, 0, 0];
  
  return [dx / dt, dy / dt, 0];
}

function bimNurbsSample(c, tol) {
  if (tol <= 0) tol = 0.001;
  var samples = [];
  var t = 0;
  var P0 = bimNurbsPoint(c, t);
  samples.push(P0);
  function subdivide(a, b) {
    var Pa = bimNurbsPoint(c, a);
    var Pb = bimNurbsPoint(c, b);
    var M = [(Pa[0] + Pb[0]) / 2, (Pa[1] + Pb[1]) / 2];
    var chordError = 1 - Math.hypot(M[0], M[1]);
    var intervalSize = b - a;
    if (chordError > tol || intervalSize > 0.25) {
      if (intervalSize > 1e-6) {
        var mid = (a + b) / 2;
        subdivide(a, mid);
        subdivide(mid, b);
        return;
      }
    }
    var last = samples[samples.length - 1];
    if (Math.hypot(Pb[0] - last[0], Pb[1] - last[1]) > 1e-9) samples.push(Pb);
  }
  subdivide(0, 1);
  return samples;
}

