

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
  const x = c[0];
  const z = c[1];
  const cosRot = Math.cos(rot);
  const sinRot = Math.sin(rot);
  const corners = [
    [-w / 2, -d / 2],
    [w / 2, -d / 2],
    [w / 2, d / 2],
    [-w / 2, d / 2],
  ];
  return corners.map(([cx, cz]) => [
    cx * cosRot - cz * sinRot + x,
    cx * sinRot + cz * cosRot + z,
  ]);
}

function bimClrZone(it, front, side) {
  if (front <= 0) return null;
  const { center, w, d, rot } = it;
  const x = center[0];
  const z = center[1];
  // Zone centre: offset from item center in the direction (-sin rot, cos rot)
  // by distance (d/2 + front/2)
  const cx = x - Math.sin(rot) * (d / 2 + front / 2);
  const cz = z + Math.cos(rot) * (d / 2 + front / 2);
  // Zone dimensions
  const zoneW = w / 2 + side;
  const zoneD = front / 2;
  // Local corners relative to zone centre (before rotation)
  const localCorners = [
    [-zoneW, -zoneD],
    [zoneW, -zoneD],
    [zoneW, zoneD],
    [-zoneW, zoneD],
  ];
  // Rotate and translate
  const cosRot = Math.cos(rot);
  const sinRot = Math.sin(rot);
  return localCorners.map(([lcx, lcz]) => [
    lcx * cosRot - lcz * sinRot + cx,
    lcx * sinRot + lcz * cosRot + cz,
  ]);
}

function bimClrOverlap(a, b) {
  if (a === null || b === null) return false;
  if (a.length < 3 || b.length < 3) return false;
  function getAxes(poly) {
    const axes = [];
    for (let i = 0; i < poly.length; i++) {
      const p1 = poly[i];
      const p2 = poly[(i + 1) % poly.length];
      const ex = p2[0] - p1[0];
      const ez = p2[1] - p1[1];
      // Normal perpendicular to edge
      axes.push([ez, -ex]);
    }
    return axes;
  }
  function project(poly, axis) {
    const [ax, az] = axis;
    let min = ax * poly[0][0] + az * poly[0][1];
    let max = min;
    for (let i = 1; i < poly.length; i++) {
      const proj = ax * poly[i][0] + az * poly[i][1];
      if (proj < min) min = proj;
      if (proj > max) max = proj;
    }
    return [min, max];
  }
  function overlapIntervals(i1, i2) {
    return Math.max(i1[0], i2[0]) < Math.min(i1[1], i2[1]);
  }
  const allAxes = [...getAxes(a), ...getAxes(b)];
  for (const axis of allAxes) {
    const projA = project(a, axis);
    const projB = project(b, axis);
    if (!overlapIntervals(projA, projB)) return false;
  }
  return true;
}

function bimClrConflicts(items, obstacles) {
  if (!items) return [];
  const conflicts = [];
  for (const item of items) {
    if (!item || !item.zone) continue;
    // Check against other items' bodies
    for (const other of items) {
      if (!other || other.id === item.id || !other.body) continue;
      if (bimClrOverlap(item.zone, other.body)) {
        conflicts.push({ item: item.id, with: other.id });
      }
    }
    // Check against obstacles
    for (const obstacle of obstacles) {
      if (!obstacle || !obstacle.poly) continue;
      if (bimClrOverlap(item.zone, obstacle.poly)) {
        conflicts.push({ item: item.id, with: obstacle.id });
      }
    }
  }
  return conflicts;
}

function bimClrCircleFits(poly, c, r) {
  if (r <= 0 || poly.length < 3) return false;
  // Point-in-polygon using even-odd rule
  function pointInPolygon(poly, px, pz) {
    let inside = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      const xi = poly[i][0], zi = poly[i][1];
      const xj = poly[j][0], zj = poly[j][1];
      const intersect = ((zi > pz) !== (zj > pz)) &&
        (px < (xj - xi) * (pz - zi) / (zj - zi) + xi);
      if (intersect) inside = !inside;
    }
    return inside;
  }
  // Distance from point to line segment
  function pointToSegmentDist(px, pz, x1, z1, x2, z2) {
    const dx = x2 - x1;
    const dz = z2 - z1;
    const lengthSq = dx * dx + dz * dz;
    let t;
    if (lengthSq === 0) {
      const dx2 = px - x1;
      const dz2 = pz - z1;
      return Math.sqrt(dx2 * dx2 + dz2 * dz2);
    }
    t = ((px - x1) * dx + (pz - z1) * dz) / lengthSq;
    if (t < 0) {
      const dx2 = px - x1;
      const dz2 = pz - z1;
      return Math.sqrt(dx2 * dx2 + dz2 * dz2);
    } else if (t > 1) {
      const dx2 = px - x2;
      const dz2 = pz - z2;
      return Math.sqrt(dx2 * dx2 + dz2 * dz2);
    } else {
      const projX = x1 + t * dx;
      const projZ = z1 + t * dz;
      const dx2 = px - projX;
      const dz2 = pz - projZ;
      return Math.sqrt(dx2 * dx2 + dz2 * dz2);
    }
  }
  // Check centre is inside polygon
  if (!pointInPolygon(poly, c[0], c[1])) return false;
  // Check distance to every edge segment
  for (let i = 0; i < poly.length; i++) {
    const j = (i + 1) % poly.length;
    const dist = pointToSegmentDist(c[0], c[1], poly[i][0], poly[i][1], poly[j][0], poly[j][1]);
    if (dist < r - 1e-9) return false;
  }
  return true;
}

function bimClrRule(rule, m) {
  if (!rule) {
    return { clause: '', edition: '', status: 'not evaluated' };
  }
  if (typeof m !== 'number') {
    return { clause: rule.clause || '', edition: rule.edition || '', status: 'not evaluated' };
  }
  const measuredIn = Math.round(m / 0.0254 * 100) / 100;
  const status = m / 0.0254 >= rule.minIn - 1e-9 ? 'meets' : 'below';
  return { clause: rule.clause || '', edition: rule.edition || '', status, measuredIn };
}
