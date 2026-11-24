

  /* ================= __acad3dV209: Walkthrough W3, fly and drone, the pure part =================
     docs/research/research-walkthrough.md (W3) and docs/work-orders/v209/SPEC.md. The drone: the altitude band, an orbit,
     a waypoint route and the point along it. Each function is a work order, added below as it is built; none uses another
     file's names. */

/* WO-01 bimDrnClamp(p, minAlt, maxAlt, ground): p with its height clamped to ground + minAlt .. ground + maxAlt; minAlt defaults to 2, maxAlt to 120, ground to 0; SPEC 5 WO-01 */
function bimDrnClamp(p, minAlt, maxAlt, ground) {
  var m = minAlt >= 0 ? minAlt : 2;
  var a = maxAlt > 0 ? maxAlt : 120;
  var g = typeof ground === 'number' ? ground : 0;
  var lo = g + m;
  var hi = g + a;
  var y = p[1];
  if (y < lo) {
    y = lo;
  }
  if (y > hi) {
    y = hi;
  }
  return [p[0], y, p[2]];
}

/* WO-02 bimDrnOrbit(c, r, h, t, period): the eye on an orbit of radius r at height h about c, one turn per period (30 s default), and the target c; SPEC 5 WO-02 */
function bimDrnOrbit(c, r, h, t, period) {
  var per = period > 0 ? period : 30;
  var angle = 2 * Math.PI * t / per;
  return {
    eye: [c[0] + r * Math.cos(angle), c[1] + h, c[2] + r * Math.sin(angle)],
    target: [c[0], c[1], c[2]]
  };
}

/* WO-03 bimDrnRoute(pts): the 3D length of each leg and their sum; SPEC 5 WO-03 */
function bimDrnRoute(pts) {
  var segs = [];
  var total = 0;
  var i;
  for (i = 0; i + 1 < pts.length; i++) {
    var dx = pts[i + 1][0] - pts[i][0];
    var dy = pts[i + 1][1] - pts[i][1];
    var dz = pts[i + 1][2] - pts[i][2];
    var d = Math.sqrt(dx * dx + dy * dy + dz * dz);
    segs.push(d);
    total = total + d;
  }
  return { segs: segs, length: total };
}

/* WO-04 bimDrnAt(pts, route, dist): the point dist along the route, clamped to 0..length and interpolated on its leg; null for no points; SPEC 5 WO-04 */
function bimDrnAt(pts, route, dist) {
  if (!pts || pts.length === 0) {
    return null;
  }
  var d = dist < 0 ? 0 : dist;
  if (d > route.length) {
    d = route.length;
  }
  var i;
  var acc = 0;
  for (i = 0; i + 1 < pts.length; i++) {
    var seg = route.segs[i];
    if (d <= acc + seg) {
      var k = seg > 0 ? (d - acc) / seg : 0;
      return [
        pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k,
        pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k,
        pts[i][2] + (pts[i + 1][2] - pts[i][2]) * k
      ];
    }
    acc = acc + seg;
  }
  return [pts[pts.length - 1][0], pts[pts.length - 1][1], pts[pts.length - 1][2]];
}
