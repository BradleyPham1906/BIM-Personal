

  /* ================= __acad3dV236: The layout view, the pure part =================
     docs/research/research-program-to-plan.md, its layout-methods.md, anthropocity-features.md and algorithms.md, and
     docs/work-orders/v236/SPEC.md. Rooms on a bay grid in two bands, small rooms clustered, the wall graph, corridors
     routed from user paths (direct legs, a spine, spurs), the stair, and the scorecard every study carries. Each
     function is a work order, added below as it is built; none uses another file's names. */
/* WO-01: bimPlBayWidth(areas, depth, bmin, bmax, step) - 24 lines */
function bimPlBayWidth(areas, depth, bmin, bmax, step) {
  if (depth <= 0 || areas.reduce(function (s, a) { return s + a; }, 0) <= 0) return null;
  var best = null, b = bmin, k, total, err;
  while (b <= bmax) {
    k = [];
    for (var i = 0; i < areas.length; i++) k[i] = Math.max(1, Math.round(areas[i] / (b * depth)));
    total = areas.reduce(function (s, a) { return s + a; }, 0);
    err = 0;
    for (var i = 0; i < k.length; i++) err += Math.abs(k[i] * b * depth - areas[i]);
    err = err / total;
    if (best === null || err < best.error - 1e-12) best = { bay: b, bays: k, error: err };
    b = Number((b + step).toFixed(6));
  }
  return best;
}

/* WO-02: bimPlSmall(rooms, links, bay, depth, t, maxPer) - 36 lines */
function bimPlSmall(rooms, links, bay, depth, t, maxPer) {
  t = t || 0.6; maxPer = maxPer || 3;
  var isSmall = function (a) { return a.area < t * bay * depth; };
  var clusters = []; var ids, area, small;
  for (var r = 0; r < rooms.length; r++) {
    var room = rooms[r];
    if (!isSmall(room)) clusters.push([[room.id], room.area, false]);
    else {
      var bestIdx = -1, bestStr = -1;
      for (var l = 0; l < links.length; l++) {
        var link = links[l];
        if ((link.a === room.id || link.b === room.id) && link.status !== 'rejected') {
          var otherId = (link.a === room.id) ? link.b : link.a;
          if (isSmall(rooms.find(function (ri) { return ri.id === otherId; }))) {
            var cid = -1;
            for (var i = 0; i < clusters.length; i++)
              if (clusters[i][0].indexOf(otherId) >= 0) { cid = i; break; }
            if (cid >= 0 && clusters[i][0].length < maxPer) {
              var str = link.strength !== undefined ? link.strength : 2;
              if (str > bestStr || (str === bestStr && bestIdx >= 0 && clusters[bestIdx][0][0] > clusters[cid][0][0])) bestStr = str, bestIdx = cid;
            }
          }
        }
      }
      if (bestIdx >= 0) { clusters[bestIdx][0].push(room.id); clusters[bestIdx][1] += room.area; }
      else clusters.push([[room.id], room.area, true]);
    }
  }
  var r = []; var c;
  for (var i = 0; i < clusters.length; i++) { c = clusters[i]; r.push({ ids: c[0], area: c[1], small: c[2] }); }
  return r;
}
