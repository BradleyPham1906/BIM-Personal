

function bimEgInside(p, poly) {
  if (!poly || poly.length < 3) return false;
  var inside = false;
  for (var i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    var xi = poly[i][0], zi = poly[i][1];
    var xj = poly[j][0], zj = poly[j][1];
    var intersect = ((zi > p[1]) !== (zj > p[1])) && (p[0] < (xj - xi) * (p[1] - zi) / (zj - zi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

function bimEgGrid(room, obstacles, cell) {
  if (!room || room.length < 3 || cell <= 0) return null;
  var x0 = room[0][0], z0 = room[0][1];
  for (var i = 1; i < room.length; i++) {
    if (room[i][0] < x0) x0 = room[i][0];
    if (room[i][1] < z0) z0 = room[i][1];
  }
  var maxX = room[0][0], maxZ = room[0][1];
  for (var i = 1; i < room.length; i++) {
    if (room[i][0] > maxX) maxX = room[i][0];
    if (room[i][1] > maxZ) maxZ = room[i][1];
  }
  var nx = Math.ceil((maxX - x0) / cell - 1e-9);
  var nz = Math.ceil((maxZ - z0) / cell - 1e-9);
  var free = new Uint8Array(nx * nz);
  for (var j = 0; j < nz; j++) {
    for (var i = 0; i < nx; i++) {
      var cx = x0 + (i + 0.5) * cell;
      var cz = z0 + (j + 0.5) * cell;
      var inRoom = bimEgInside([cx, cz], room);
      if (!inRoom) {
        free[j * nx + i] = 0;
        continue;
      }
      var blocked = false;
      if (obstacles && obstacles.length > 0) {
        for (var k = 0; k < obstacles.length; k++) {
          if (bimEgInside([cx, cz], obstacles[k])) {
            blocked = true;
            break;
          }
        }
      }
      free[j * nx + i] = blocked ? 0 : 1;
    }
  }
  return { x0: x0, z0: z0, cell: cell, nx: nx, nz: nz, free: free };
}
function bimEgCell(g, p) {
  if (!g || !p) return -1;
  var i = (p[0] - g.x0) / g.cell | 0;
  var j = (p[1] - g.z0) / g.cell | 0;
  if (i < 0 || i >= g.nx || j < 0 || j >= g.nz) return -1;
  var idx = j * g.nx + i;
  return g.free[idx] === 1 ? idx : -1;
}
  /* ================= __acad3dV181: Interiors I3, circulation and escape routes, the pure part =================
     docs/research/research-notion-v177-v180-interiors.md (I3) and docs/work-orders/v181/SPEC.md. A walkable grid in plan
     [x, z]; the shortest 8-way route on it (Dijkstra, no corner cutting); the nearest exit; a route against a travel limit.
     Each function is a work order, added below as it is built; none uses another file's names. */
