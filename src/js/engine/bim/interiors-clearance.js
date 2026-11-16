

  /* ================= __acad3dV180: Interiors I2, clearance and ergonomics, the pure part ================
     docs/research/research-notion-v177-v180-interiors.md (I2) and docs/work-orders/v180/SPEC.md. Footprints and clearance
     zones as convex polygons in plan [x, z]; overlap by separating axes; a turning circle inside a room; a measurement
     against a registry rule. Each function is a work order, added below as it is built; none uses another file's names.

     WO-01: bimClrRect
     WO-02: bimClrZone
     WO-03: bimClrOverlap
     WO-04: bimClrConflicts
     WO-05: bimClrCircleFits
     WO-06: bimClrRule
*/

function bimClrRect(c, w, d, rot) {
  var cs = Math.cos(rot), sn = Math.sin(rot), L = [[-w / 2, -d / 2], [w / 2, -d / 2], [w / 2, d / 2], [-w / 2, d / 2]], out = [], i;
  for (i = 0; i < 4; i++) out.push([L[i][0] * cs - L[i][1] * sn + c[0], L[i][0] * sn + L[i][1] * cs + c[1]]);
  return out;
}
function bimClrZone(it, front, side) {
  if (!(front > 0) || !it || !it.center) return null;
  var rot = it.rot || 0, k = it.d / 2 + front / 2;
  side = typeof side === 'number' && isFinite(side) ? side : 0;
  return bimClrRect([it.center[0] - Math.sin(rot) * k, it.center[1] + Math.cos(rot) * k], it.w + 2 * side, front, rot);
}
function bimClrOverlap(a, b) {
  if (!a || !b || a.length < 3 || b.length < 3) return false;
  var P = [a, b], q, i, ax, az, A, B;
  function proj(poly, ax, az) {
    var lo = Infinity, hi = -Infinity, j, v;
    for (j = 0; j < poly.length; j++) { v = ax * poly[j][0] + az * poly[j][1]; if (v < lo) lo = v; if (v > hi) hi = v; }
    return [lo, hi];
  }
  for (q = 0; q < 2; q++) {
    for (i = 0; i < P[q].length; i++) {
      var p1 = P[q][i], p2 = P[q][(i + 1) % P[q].length], len;
      ax = p2[1] - p1[1]; az = -(p2[0] - p1[0]); len = Math.sqrt(ax * ax + az * az);
      if (len < 1e-12) continue;
      ax /= len; az /= len;
      A = proj(a, ax, az); B = proj(b, ax, az);
      if (Math.min(A[1], B[1]) - Math.max(A[0], B[0]) <= 1e-9) return false;
    }
  }
  return true;
}
function bimClrConflicts(items, obstacles) {
  var out = [], i, j, it, o;
  items = items || []; obstacles = obstacles || [];
  for (i = 0; i < items.length; i++) {
    it = items[i];
    if (!it || !it.zone) continue;
    for (j = 0; j < items.length; j++) {
      o = items[j];
      if (!o || j === i || o.id === it.id || !o.body) continue;
      if (bimClrOverlap(it.zone, o.body)) out.push({ item: it.id, with: o.id });
    }
    for (j = 0; j < obstacles.length; j++) {
      o = obstacles[j];
      if (!o || !o.poly) continue;
      if (bimClrOverlap(it.zone, o.poly)) out.push({ item: it.id, with: o.id });
    }
  }
  return out;
}
function bimClrCircleFits(poly, c, r) {
  if (!(r > 0) || !poly || poly.length < 3 || !c) return false;
  var inside = false, i, j, n = poly.length, xi, zi, xj, zj, dx, dz, t, L2, px, pz;
  for (i = 0, j = n - 1; i < n; j = i++) {
    xi = poly[i][0]; zi = poly[i][1]; xj = poly[j][0]; zj = poly[j][1];
    if (((zi > c[1]) !== (zj > c[1])) && (c[0] < (xj - xi) * (c[1] - zi) / (zj - zi) + xi)) inside = !inside;
  }
  if (!inside) return false;
  for (i = 0; i < n; i++) {
    j = (i + 1) % n;
    dx = poly[j][0] - poly[i][0]; dz = poly[j][1] - poly[i][1]; L2 = dx * dx + dz * dz;
    t = L2 > 0 ? ((c[0] - poly[i][0]) * dx + (c[1] - poly[i][1]) * dz) / L2 : 0;
    t = Math.max(0, Math.min(1, t));
    px = poly[i][0] + t * dx - c[0]; pz = poly[i][1] + t * dz - c[1];
    if (Math.sqrt(px * px + pz * pz) < r - 1e-9) return false;
  }
  return true;
}
function bimClrRule(rule, m) {
  var out = { clause: rule && typeof rule.clause === 'string' ? rule.clause : '', edition: rule && typeof rule.edition === 'string' ? rule.edition : '', status: 'not evaluated' };
  if (!rule || typeof rule.minIn !== 'number' || !isFinite(rule.minIn) || typeof m !== 'number' || !isFinite(m)) return out;
  out.status = m / 0.0254 >= rule.minIn - 1e-9 ? 'meets' : 'below';
  out.measuredIn = Math.round(m / 0.0254 * 100) / 100;
  return out;
}

export { bimClrCircleFits, bimClrConflicts, bimClrRect, bimClrRule, bimClrZone };
