/* ================= __acad3dV182: Interiors I4, sightlines and views, the pure part =================
     docs/research/research-notion-v177-v180-interiors.md (I4) and docs/work-orders/v182/SPEC.md. Rays against wall segments
     in plan [x, z]: the nearest hit, the isovist polygon, its area, a sightline, the share of a window seen. Geometry, not
     daylight. Each function is a work order, added below as it is built; none uses another file's names.
*/

function bimIsoHit(p, dx, dz, segs) {
  var bestT = Infinity;
  for (var i = 0; i < segs.length; i++) {
    var s = segs[i];
    var x1 = s[0][0], z1 = s[0][1];
    var x2 = s[1][0], z2 = s[1][1];
    var den = dx * (z2 - z1) - dz * (x2 - x1);
    if (Math.abs(den) < 1e-12) continue; // parallel
    var t = ((x1 - p[0]) * (z2 - z1) - (z1 - p[1]) * (x2 - x1)) / den;
    var u = ((x1 - p[0]) * dz - (z1 - p[1]) * dx) / den;
    if (t > 1e-9 && u >= -1e-9 && u <= 1 + 1e-9) {
      if (t < bestT) bestT = t;
    }
  }
  return bestT;
}


function bimIsovist(p, segs, n, maxR) {
  var count = n !== undefined ? Math.max(n, 3) : 360;
  var angleStep = 2 * Math.PI / count;
  var result = [];
  for (var i = 0; i < count; i++) {
    var angle = angleStep * i;
    var dx = Math.cos(angle);
    var dz = Math.sin(angle);
    var hitT = bimIsoHit(p, dx, dz, segs);
    var dist = hitT !== Infinity ? Math.min(hitT, maxR <= 0 ? 50 : maxR) : maxR <= 0 ? 50 : maxR;
    result.push([p[0] + dx * dist, p[1] + dz * dist]);
  }
  return result;
}

function bimIsoArea(poly) {
  if (poly === null || poly.length < 3) return 0;
  var area = 0;
  for (var i = 0; i < poly.length; i++) {
    var j = (i + 1) % poly.length;
    area += (poly[j][0] - poly[i][0]) * (poly[j][1] + poly[i][1]);
  }
  return Math.abs(area) / 2;
}function bimIsoSees(p, q, segs) {
  if (p[0] === q[0] && p[1] === q[1]) return true; // coincident
  var dist = Math.hypot(q[0] - p[0], q[1] - p[1]);
  var hitT = bimIsoHit(p, q[0] - p[0], q[1] - p[1], segs);
  if (hitT === Infinity) return true; // nothing blocking
  var hitDist = Math.hypot(hitT * (q[0] - p[0]), hitT * (q[1] - p[1]));
  return hitDist >= dist - 1e-9;
}

function bimIsoWindows(p, windows, segs, samples) {
  var result = [];
  var sampleCount = samples === undefined || samples < 1 ? 5 : Math.floor(samples);
  for (var w = 0; w < windows.length; w++) {
    var win = windows[w];
    var winResult = [];
    for (var s = 0; s < sampleCount; s++) {
      var t = (s + 0.5) / sampleCount;
      var x = win.a[0] + (win.b[0] - win.a[0]) * t;
      var z = win.a[1] + (win.b[1] - win.a[1]) * t;
      var sees = bimIsoSees(p, [x, z], segs);
      winResult.push(sees);
    }
    var trueCount = 0;
    for (var i = 0; i < winResult.length; i++) {
      if (winResult[i]) trueCount++;
    }
    result.push({
      id: win.id,
      fraction: sampleCount > 0 ? trueCount / sampleCount : 0
    });
  }
  return result;
}

/* __acad3dV182 */
