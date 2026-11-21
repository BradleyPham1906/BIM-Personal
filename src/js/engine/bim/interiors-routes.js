  /* ================= __acad3dV181: Interiors I3, circulation and escape routes, the pure part =================
     docs/research/research-notion-v177-v180-interiors.md (I3) and docs/work-orders/v181/SPEC.md. A walkable grid in plan
     [x, z]; the shortest 8-way route on it (Dijkstra, no corner cutting); the nearest exit; a route against a travel limit.
     Each function is a work order, added below as it is built; none uses another file's names. */


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
  if (!room || room.length < 3 || !(cell > 0)) return null;
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
  var i = Math.floor((p[0] - g.x0) / g.cell);
  var j = Math.floor((p[1] - g.z0) / g.cell);
  if (i < 0 || i >= g.nx || j < 0 || j >= g.nz) return -1;
  var idx = j * g.nx + i;
  return g.free[idx] === 1 ? idx : -1;
}
function bimEgPath(g, a, b) {
  if (!g || !a || !b) return null;
  var startCell = bimEgCell(g, a);
  var endCell = bimEgCell(g, b);
  if (startCell === -1 || endCell === -1) return null;
  if (startCell === endCell) return { len: 0, cells: [startCell] };
  var nx = g.nx, nz = g.nz;
  var free = g.free;
  var cellSize = g.cell;
  var gScore = {};
  var cameFrom = {};
  for (var i = 0; i < nx * nz; i++) {
    gScore[i] = Infinity;
  }
  gScore[startCell] = 0;
  var openSet = [startCell];
  var openSetHash = {};
  openSetHash[startCell] = true;
  while (openSet.length > 0) {
    var minIdx = 0;
    for (var i = 1; i < openSet.length; i++) {
      if (gScore[openSet[i]] < gScore[openSet[minIdx]] || (gScore[openSet[i]] === gScore[openSet[minIdx]] && openSet[i] < openSet[minIdx])) {
        minIdx = i;
      }
    }
    var current = openSet[minIdx];
    if (current === endCell) break;
    openSet.splice(minIdx, 1);
    openSetHash[current] = false;
    var ci = current % nx;
    var cj = Math.floor(current / nx);
    var neighbors = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]];
    for (var n = 0; n < 8; n++) {
      var dx = neighbors[n][0];
      var dz = neighbors[n][1];
      var nxIdx = ci + dx;
      var nzIdx = cj + dz;
      if (nxIdx < 0 || nxIdx >= nx || nzIdx < 0 || nzIdx >= nz) continue;
      var neighborCell = nzIdx * nx + nxIdx;
      if (!free[neighborCell]) continue;
      if (dx !== 0 && dz !== 0) {
        var adj1 = cj * nx + nxIdx;
        var adj2 = nzIdx * nx + ci;
        if (!free[adj1] || !free[adj2]) continue;
      }
      var moveCost = (dx !== 0 && dz !== 0) ? cellSize * Math.sqrt(2) : cellSize;
      var tentativeG = gScore[current] + moveCost;
      if (tentativeG < gScore[neighborCell]) {
        cameFrom[neighborCell] = current;
        gScore[neighborCell] = tentativeG;
        if (!openSetHash[neighborCell]) {
          openSetHash[neighborCell] = true;
          openSet.push(neighborCell);
        }
      }
    }
  }
  if (gScore[endCell] === Infinity) return null;
  var path = [];
  var cell = endCell;
  while (cell !== startCell) {
    path.unshift(cell);
    cell = cameFrom[cell];
    if (cell === undefined) return null;
  }
  path.unshift(startCell);
  return { len: gScore[endCell], cells: path };
}
function bimEgNearest(routes) {
  if (!routes) return null;
  var keys = Object.keys(routes).sort();
  var best = null;
  for (var i = 0; i < keys.length; i++) {
    var name = keys[i];
    var route = routes[name];
    if (!route) continue;
    if (best === null || route.len < best.len) {
      best = { exit: name, len: route.len };
    }
  }
  return best;
}
function bimEgStatus(route, limit) {
  if (!route) return { status: 'blocked', why: 'no route to an exit' };
  if (!(limit > 0)) return { status: 'not evaluated', why: 'no travel limit chosen' };
  var lenStr = route.len.toFixed(1);
  var limitStr = String(limit);
  if (route.len <= limit) {
    return { status: 'within', why: lenStr + ' m of ' + limitStr + ' m' };
  }
  return { status: 'over', why: lenStr + ' m, over ' + limitStr + ' m' };
}
export { bimEgGrid, bimEgNearest, bimEgPath, bimEgStatus };
