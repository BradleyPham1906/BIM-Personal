   /* ================= __acad3dV191: LOD-D, LOD1.3 and LOD2.2 roofs from LiDAR, the pure part =================
     docs/research/research-notion-v189-roofs.md and docs/work-orders/v191/SPEC.md. Roof planes from LiDAR points: Jacobi
     eigenvectors, the least-squares plane and its RMS, points in a footprint, coverage, heights on a plane. Each function
     is a work order, added below as it is built; none uses another file's names. */

/* WO-01 bimRoofJacobi(A): eigen-decomposition of a symmetric 3x3 by cyclic Jacobi rotations */
function bimRoofJacobi(A) {
  var a = [[A[0][0],A[0][1],A[0][2]],[A[1][0],A[1][1],A[1][2]],[A[2][0],A[2][1],A[2][2]]];
  var v = [[1,0,0],[0,1,0],[0,0,1]];
  for (var iter = 0; iter < 50; iter++) {
    var maxOff = 0, p = -1, q = -1, i, k;
    for (i = 0; i < 3; i++) for (k = i + 1; k < 3; k++) if (Math.abs(a[i][k]) > maxOff) { maxOff = Math.abs(a[i][k]); p = i; q = k; }
    if (maxOff < 1e-15 || p < 0) break;
    var app = a[p][p], apq = a[p][q], aqq = a[q][q];
    var theta = Math.abs(app - aqq) < 1e-15 ? (apq > 0 ? Math.PI / 4 : -Math.PI / 4) : 0.5 * Math.atan2(2 * apq, app - aqq);
    var c = Math.cos(theta), s = Math.sin(theta);
    for (i = 0; i < 3; i++) if (i !== p && i !== q) { var akp = a[p][i], akq = a[q][i]; a[p][i] = c * akp + s * akq; a[q][i] = -s * akp + c * akq; a[i][p] = a[p][i]; a[i][q] = a[q][i]; }
    a[p][p] = c * c * app + 2 * c * s * apq + s * s * aqq;
    a[q][q] = s * s * app - 2 * c * s * apq + c * c * aqq;
    a[p][q] = 0; a[q][p] = 0;
    for (i = 0; i < 3; i++) { var vip = v[i][p], viq = v[i][q]; v[i][p] = c * vip + s * viq; v[i][q] = -s * vip + c * viq; }
  }
  return { values: [a[0][0], a[1][1], a[2][2]], vectors: [[v[0][0],v[1][0],v[2][0]],[v[0][1],v[1][1],v[2][1]],[v[0][2],v[1][2],v[2][2]]] };
}

/* WO-03 bimRoofInRing(pts, ring): points whose (x,y) is inside the ring (even-odd) */
function bimRoofInRing(pts, ring) {
  var result = [];
  for (var i = 0; i < pts.length; i++) {
    var x = pts[i][0], y = pts[i][1], inside = false, j = ring.length - 1, k;
    for (k = 0; k < ring.length; k++) { var xi = ring[k][0], yi = ring[k][1], xj = ring[j][0], yj = ring[j][1]; if ((yi > y) !== (yj > y)) { var xint = (xj - xi) * (y - yi) / (yj - yi) + xi; if (x < xint) inside = !inside; } j = k; }
    if (inside) result.push(pts[i]);
  }
  return result;
}

/* WO-04 bimRoofCoverage(pts, ring, cell): share of footprint cells holding at least one point */
function bimRoofCoverage(pts, ring, cell) {
  if (cell === undefined || cell <= 0) cell = 1;
  var minX = ring[0][0], minY = ring[0][1], maxX = ring[0][0], maxY = ring[0][1], i;
  for (i = 1; i < ring.length; i++) { if (ring[i][0] < minX) minX = ring[i][0]; if (ring[i][1] < minY) minY = ring[i][1]; if (ring[i][0] > maxX) maxX = ring[i][0]; if (ring[i][1] > maxY) maxY = ring[i][1]; }
  var cellMap = {};
  for (i = 0; i < pts.length; i++) cellMap[Math.floor((pts[i][0] - minX) / cell) + ',' + Math.floor((pts[i][1] - minY) / cell)] = true;
  var total = 0, covered = 0, gx = minX;
  while (gx < maxX) { var gy = minY; while (gy < maxY) { var cxCenter = gx + cell / 2, cyCenter = gy + cell / 2, inside = false, j = ring.length - 1, k; for (k = 0; k < ring.length; k++) { var xi = ring[k][0], yi = ring[k][1], xj = ring[j][0], yj = ring[j][1]; if ((yi > cyCenter) !== (yj > cyCenter)) { var xint = (xj - xi) * (cyCenter - yi) / (yj - yi) + xi; if (cxCenter < xint) inside = !inside; } j = k; } if (inside) { total++; if (cellMap[Math.floor((cxCenter - minX) / cell) + ',' + Math.floor((cyCenter - minY) / cell)]) covered++; } gy += cell; } gx += cell; }
  return total === 0 ? 0 : covered / total;
}

/* WO-05 bimRoofZ(pl, x, y): height on the plane at plan point (x, y) */
function bimRoofZ(pl, x, y) {
  if (Math.abs(pl.n[2]) < 1e-12) return null;
  return pl.c[2] - (pl.n[0] * (x - pl.c[0]) + pl.n[1] * (y - pl.c[1])) / pl.n[2];
}
