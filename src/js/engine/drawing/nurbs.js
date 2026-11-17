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

