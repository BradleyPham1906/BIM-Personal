

  /* ================= __acad3dV179: Interiors I1, the pure part =================
     docs/research/research-notion-v177-v180-interiors.md (the owner's decisions as recommended, 2026-11-14) and
     docs/work-orders/v179/SPEC.md. The programme (uses, counts, area ranges) and its relations (next to, near,
     apart) kept apart from the measured rooms; the facts measured from the rooms: a point inside, the length two
     rooms share across a wall, the doors linking them, route costs by the doors; each relation met, not met or not
     evaluated, never guessed. Plan points are [x, z]. Each function is a work order in docs/work-orders/v179/TASKS.md,
     added below as it is built; none uses another file's names. */
function bimIntProgramItem(raw) {
  var r = raw || {};
  function str(v) { return typeof v === 'string' ? v : ''; }
  function trim(v) { return typeof v === 'string' ? v.replace(/^\s+|\s+$/g, '') : ''; }
  function area(v) { return (typeof v === 'number' && isFinite(v) && v >= 0) ? v : null; }
  var count = (typeof r.count === 'number' && isFinite(r.count) && r.count >= 1) ? Math.floor(r.count) : 1;
  var areaMin = area(r.areaMin), areaMax = area(r.areaMax), tmp;
  if (areaMin !== null && areaMax !== null && areaMin > areaMax) { tmp = areaMin; areaMin = areaMax; areaMax = tmp; }
  var level = (typeof r.level === 'number' && isFinite(r.level)) ? Math.floor(r.level) : null;
  var status = (r.status === 'unknown' || r.status === 'assumed' || r.status === 'confirmed') ? r.status : 'unknown';
  var params = {}, k;
  if (r.params && typeof r.params === 'object' && Object.prototype.toString.call(r.params) === '[object Object]') {
    for (k in r.params) {
      if (Object.prototype.hasOwnProperty.call(r.params, k) && typeof r.params[k] === 'number' && isFinite(r.params[k])) params[k] = r.params[k];
    }
  }
  var open = (r.open === 'open' || r.open === 'closed' || r.open === 'auto') ? r.open : 'auto';
  return { id: str(r.id), use: trim(r.use), count: count, areaMin: areaMin, areaMax: areaMax, rationale: str(r.rationale),
    building: trim(r.building), level: level, group: trim(r.group), status: status, source: str(r.source), params: params, open: open };
}
function bimIntRelation(raw) {
  if (!raw || typeof raw.a !== 'string' || typeof raw.b !== 'string' || raw.a === '' || raw.b === '' || raw.a === raw.b) return null;
  var kinds = { required: 1, desired: 1, forbidden: 1 };
  var rels = { next: 1, near: 1, apart: 1, access: 1, visual: 1, acoustic: 1, secure: 1, sequence: 1 };
  var stats = { suggested: 1, approved: 1, rejected: 1 };
  var kind = kinds.hasOwnProperty(raw.kind) ? raw.kind : 'desired';
  var rel = rels.hasOwnProperty(raw.rel) ? raw.rel : 'next';
  var nearM = (typeof raw.nearM === 'number' && isFinite(raw.nearM) && raw.nearM > 0) ? raw.nearM : 15;
  var strength = (raw.strength === 1 || raw.strength === 2 || raw.strength === 3) ? raw.strength : 2;
  var reason = typeof raw.reason === 'string' ? raw.reason.replace(/^\s+|\s+$/g, '') : '';
  var status = stats.hasOwnProperty(raw.status) ? raw.status : 'approved';
  return { a: raw.a, b: raw.b, kind: kind, rel: rel, nearM: nearM, strength: strength, reason: reason, status: status };
}
function bimIntInside(p, poly) {
  if (!poly || poly.length === 0) {
    return false;
  }
  // even-odd crossing test
  var x = p[0];
  var z = p[1];
  var inside = false;
  for (var i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    var xi = poly[i][0];
    var zi = poly[i][1];
    var xj = poly[j][0];
    var zj = poly[j][1];
    var intersect = ((zi > z) !== (zj > z)) &&
      (x < (xj - xi) * (z - zi) / (zj - zi) + xi);
    if (intersect) {
      inside = !inside;
    }
  }
  return inside;
}
function bimIntSharedLength(pa, pb, tol) {
  if (!pa || pa.length < 3 || !pb || pb.length < 3) {
    return 0;
  }
  // default tol is 0.5 when not a number 0 or more
  if (tol === undefined || tol === null || !isFinite(tol) || tol < 0) {
    tol = 0.5;
  }
  
  // helper: project point q onto line from p1 to p2, return parameter t
  function projectOnEdge(p1, p2, q) {
    var dx = p2[0] - p1[0];
    var dz = p2[1] - p1[1];
    var lenSq = dx * dx + dz * dz;
    if (lenSq === 0) {
      return 0;
    }
    var t = ((q[0] - p1[0]) * dx + (q[1] - p1[1]) * dz) / lenSq;
    return t;
  }
  
  // helper: clip a parameter t to [0, 1] range
  function clipT(t) {
    if (t < 0) return 0;
    if (t > 1) return 1;
    return t;
  }
  
  var total = 0;
  
  // for each edge of pa
  for (var i = 0; i < pa.length; i++) {
    var j = (i + 1) % pa.length;
    var edgeLen = Math.sqrt((pa[j][0] - pa[i][0]) * (pa[j][0] - pa[i][0]) +
      (pa[j][1] - pa[i][1]) * (pa[j][1] - pa[i][1]));
    // skip edge shorter than 1e-9
    if (edgeLen < 1e-9) continue;
    
    var pi = pa[i];
    var pj = pa[j];
    
    // for each edge of pb
    for (var k = 0; k < pb.length; k++) {
      var l = (k + 1) % pb.length;
      // check if both ends of pb edge lie within tol of the line of pa edge
      var k1 = projectOnEdge(pi, pj, pb[k]);
      var k2 = projectOnEdge(pi, pj, pb[l]);
      
      // both ends must lie within tol of the edge's line
      // distance from point to line
      function pointLineDist(p, p1, p2) {
        var dx = p2[0] - p1[0];
        var dz = p2[1] - p1[1];
        var lenSq = dx * dx + dz * dz;
        if (lenSq === 0) {
          return Math.sqrt((p[0] - p1[0]) * (p[0] - p1[0]) + (p[1] - p1[1]) * (p[1] - p1[1]));
        }
        var t = ((p[0] - p1[0]) * dx + (p[1] - p1[1]) * dz) / lenSq;
        var closest = { x: p1[0] + t * dx, z: p1[1] + t * dz };
        return Math.sqrt((p[0] - closest.x) * (p[0] - closest.x) + (p[1] - closest.z) * (p[1] - closest.z));
      }
      
      if (pointLineDist(pb[k], pi, pj) <= tol && pointLineDist(pb[l], pi, pj) <= tol) {
        // project both onto edge and compute overlap
        var t_k = clipT(k1);
        var t_l = clipT(k2);
        var tMin = Math.min(t_k, t_l);
        var tMax = Math.max(t_k, t_l);
        var overlapT1 = Math.max(tMin, 0);
        var overlapT2 = Math.min(tMax, 1);
        
        if (overlapT1 < overlapT2) {
          var segLen = (overlapT2 - overlapT1) * edgeLen;
          total += segLen;
        }
      }
    }
  }
  return total;
}
function bimIntDoorLinks(rooms, doors, reach) {
  if (!rooms || rooms.length === 0 || !doors || doors.length === 0) {
    return [];
  }
  // reach 0.4 m unless a positive number
  if (reach === undefined || reach === null || !isFinite(reach) || reach <= 0) {
    reach = 0.4;
  }
  
  var dirNorm = function(dx, dz) {
    var len = Math.sqrt(dx * dx + dz * dz);
    if (len === 0) return { dx: 0, dz: 0, len: 0 };
    return { dx: dx / len, dz: dz / len, len: len };
  };
  
  var links = [];
  
  for (var d = 0; d < doors.length; d++) {
    var door = doors[d];
    if (!door.center || door.dir === undefined || door.dir === null) continue;
    var dx = door.dir[0];
    var dz = door.dir[1];
    var norm = dirNorm(dx, dz);
    var len = norm.len;
    
    if (len === 0) continue;
    
    // the points center ± (-dz, dx) / |dir| * reach
    var leftPoint = [door.center[0] + (-norm.dz) * reach, door.center[1] + norm.dx * reach];
    var rightPoint = [door.center[0] - (-norm.dz) * reach, door.center[1] - norm.dx * reach];
    
    var leftRoom = 'outside';
    var rightRoom = 'outside';
    
    if (rooms) {
      for (var r = 0; r < rooms.length; r++) {
        var rm = rooms[r];
        if (bimIntInside(leftPoint, rm.pts)) {
          leftRoom = rm.id;
        }
        if (bimIntInside(rightPoint, rm.pts)) {
          rightRoom = rm.id;
        }
      }
    }
    
    var width = door.width !== undefined && door.width !== null ? door.width : null;
    
    // a link {a: <left>, b: <right>, door: id, width: width or null} unless both sides are the same
    if (leftRoom !== rightRoom) {
      links.push({ a: leftRoom, b: rightRoom, door: door.id, width: width });
    }
  }
  return links;
}
function bimIntDistances(links, from, cost) {
  if (!links || links.length === 0 || !from) {
    return {};
  }
  
  // cost: cost[door] when that is a number 0 or more, else 1
  function getCost(doorId) {
    if (cost && cost[doorId] !== undefined && isFinite(cost[doorId]) && cost[doorId] >= 0) {
      return cost[doorId];
    }
    return 1;
  }
  
  // Build adjacency list: room -> [{room, cost}]
  var adj = {};
  for (var i = 0; i < links.length; i++) {
    var link = links[i];
    var a = link.a;
    var b = link.b;
    var door = link.door;
    var c = getCost(door);
    
    if (!adj[a]) adj[a] = [];
    if (!adj[b]) adj[b] = [];
    
    adj[a].push({ room: b, cost: c });
    adj[b].push({ room: a, cost: c });
  }
  
  // Dijkstra
  var dist = {};
  var visited = {};
  var pq = [];
  
  dist[from] = 0;
  // simple priority queue using array
  pq.push(from);
  
  while (pq.length > 0) {
    // find unvisited with minimum distance
    var minDist = Infinity;
    var minIdx = -1;
    for (var n = 0; n < pq.length; n++) {
      var room = pq[n];
      if (!visited[room] && dist[room] < minDist) {
        minDist = dist[room];
        minIdx = n;
      }
    }
    
    if (minIdx === -1) break;
    
    var u = pq[minIdx];
    // remove from pq
    pq.splice(minIdx, 1);
    visited[u] = true;
    
    if (adj[u]) {
      for (var n = 0; n < adj[u].length; n++) {
        var v = adj[u][n].room;
        var w = adj[u][n].cost;
        if (!visited[v]) {
          var newDist = dist[u] + w;
          if (typeof dist[v] === 'undefined' || newDist < dist[v]) {
            dist[v] = newDist;
          }
          pq.push(v);
        }
      }
    }
  }
  
  dist[from] = 0;
  return dist;
}
function bimIntCheck(rel, facts) {
  if (!rel) {
    return { status: 'not evaluated', why: 'not a relation' };
  }
  
  if (rel.status === 'rejected') {
    return { status: 'not evaluated', why: 'the relation was rejected' };
  }

  // either room missing from facts.rooms: not evaluated, 'a room is not in the model'
  if (!facts || !facts.rooms || facts.rooms[rel.a] === undefined || facts.rooms[rel.b] === undefined) {
    return { status: 'not evaluated', why: 'a room is not in the model' };
  }
  
  // Shared length and door count read under 'a|b' or 'b|a'
  var sharedKey = rel.a + '|' + rel.b;
  var sharedLen = facts.shared && facts.shared[sharedKey] !== undefined ? facts.shared[sharedKey] : null;
  if (sharedLen === null) {
    sharedKey = rel.b + '|' + rel.a;
    sharedLen = facts.shared && facts.shared[sharedKey] !== undefined ? facts.shared[sharedKey] : null;
  }
  
  var doorKey = rel.a + '|' + rel.b;
  var doorCount = facts.doors && facts.doors[doorKey] !== undefined ? facts.doors[doorKey] : null;
  if (doorCount === null) {
    doorKey = rel.b + '|' + rel.a;
    doorCount = facts.doors && facts.doors[doorKey] !== undefined ? facts.doors[doorKey] : null;
  }
  
  // next: met when either is above 0 ('a door between them' when a door, else 'a shared wall'), else not met 'no shared wall or door'
  if (rel.rel === 'next') {
    if ( (sharedLen !== null && sharedLen > 0) || (doorCount !== null && doorCount > 0) ) {
      if (doorCount !== null && doorCount > 0) {
        return { status: 'met', why: 'a door between them' };
      } else {
        return { status: 'met', why: 'a shared wall' };
      }
    } else {
      return { status: 'not met', why: 'no shared wall or door' };
    }
  }
  
  // apart: the reverse with the same reasons
  if (rel.rel === 'apart') {
    if (doorCount !== null && doorCount > 0) {
      return { status: 'not met', why: 'a door between them' };
    }
    if (sharedLen !== null && sharedLen > 0) {
      return { status: 'not met', why: 'a shared wall' };
    }
    return { status: 'met', why: 'no shared wall or door' };
  }
  
  // near: facts.dist[a][b]; absent: not evaluated, 'no route between them'; else met 'route 9.0 m' when within nearM, else not met 'route 9.0 m, over 5 m' (one decimal, nearM as it is)
  if (rel.rel === 'near') {
    var distAB = facts.dist && facts.dist[rel.a] && facts.dist[rel.a][rel.b] !== undefined ? facts.dist[rel.a][rel.b] : null;
    if (distAB === null) {
      return { status: 'not evaluated', why: 'no route between them' };
    }
    var nearM = (rel.nearM !== undefined && rel.nearM !== null && isFinite(rel.nearM) && rel.nearM > 0) ? rel.nearM : 15;
    if (distAB <= nearM) {
      // one decimal, always show one decimal place
      var formattedDist = Math.round(distAB * 10) / 10;
      var formatted = formattedDist.toFixed(1);
      return { status: 'met', why: 'route ' + formatted + ' m' };
    } else {
      // distance exceeds nearM, show the actual route distance
      var formattedDist = Math.round(distAB * 10) / 10;
      var formatted = formattedDist.toFixed(1);
      return { status: 'not met', why: 'route ' + formatted + ' m, over ' + nearM + ' m' };
    }
  }
  
  if (rel.rel === 'access') {
    if (doorCount !== null && doorCount > 0) return { status: 'met', why: 'a door between them' };
    return { status: 'not met', why: 'no door between them' };
  }
  if (rel.rel === 'visual' || rel.rel === 'acoustic' || rel.rel === 'secure' || rel.rel === 'sequence') {
    return { status: 'not evaluated', why: 'not measured in this phase' };
  }
  return { status: 'not evaluated', why: 'not a relation' };
}
function bimIntMatch(items, rooms) {
  if (!items || items.length === 0 || !rooms) {
    return [];
  }
  
  var result = [];
  
  for (var i = 0; i < items.length; i++) {
    var item = items[i];
    var use = item.use;
    var count = item.count;
    var areaMin = item.areaMin;
    var areaMax = item.areaMax;
    
    // the rooms of the same use in order (rooms)
    var sameUseRooms = [];
    var have = 0;
    var offArea = [];
    
    if (rooms) {
      for (var r = 0; r < rooms.length; r++) {
        var rm = rooms[r];
        if (rm === null || rm === undefined) continue;
        if (rm.use === use) {
          sameUseRooms.push(rm.id);
          // check area
          if (typeof rm.area !== 'number' || !isFinite(rm.area) ||
              (areaMin !== null && rm.area < areaMin) || (areaMax !== null && rm.area > areaMax)) {
            offArea.push(rm.id);
          }
          have++;
        }
      }
    }
    
    // status: 'short' when fewer than count, 'over' when more, else 'area' when any is out of range, else 'ok'
    var status;
    if (have < count) {
      status = 'short';
    } else if (have > count) {
      status = 'over';
    } else if (offArea.length > 0) {
      status = 'area';
    } else {
      status = 'ok';
    }
    
    result.push({
      id: item.id,
      use: use,
      need: count,
      have: have,
      rooms: sameUseRooms,
      offArea: offArea,
      status: status
    });
  }
  return result;
}
function bimIntMinWidth(widthM, minIn) {
  if (widthM === undefined || widthM === null || minIn === undefined || minIn === null ||
      !isFinite(widthM) || !isFinite(minIn)) {
    return 'not evaluated';
  }
  // meets when widthM / 0.0254 >= minIn - 1e-9, else 'below'
  var widthIn = widthM / 0.0254;
  if (widthIn >= minIn - 1e-9) {
    return 'meets';
  } else {
    return 'below';
  }
}
export {
  bimIntCheck, bimIntDistances, bimIntDoorLinks, bimIntMatch, bimIntProgramItem, bimIntRelation,
  bimIntSharedLength
};
