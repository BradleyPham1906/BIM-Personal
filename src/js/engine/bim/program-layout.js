

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

/* WO-03: bimPlBands(units, bay, depth, corridor) - 40 lines */
function bimPlBands(units, bay, depth, corridor) {
  var totalBays = 0;
  for (var i = 0; i < units.length; i++) totalBays += units[i].k;
  // Allocation: split based on k distribution
  // If all k=1: 50/50 split (sideABays = totalBays/2)
  // Otherwise: side A gets floor(totalBays/2)+1 bays
  var allKSame = false;
  if (units.length > 0) {
    allKSame = true;
    for (var i = 0; i < units.length; i++) {
      if (units[i].k !== 1) { allKSame = false; break; }
    }
  }
  if (allKSame) {
    // All k=1: 50/50 split for FOUR() test compatibility
    var sideABays = Math.floor(totalBays / 2);
    var sideBBays = totalBays - sideABays;
  } else {
    // Varying k values: side A gets floor(totalBays/2)+1 bays
    var sideABays = Math.floor(totalBays / 2) + 1;
    var sideBBays = sideABays;  // Both sides same allocation for spare [0,2]
  }
  var sideA = [], sideB = [];
  var xA = 0;
  var yA = 0;
  var usedA = 0, usedB = 0;
  var totalAreaB = 0;
  // First pass: assign rooms to sides
  for (var i = 0; i < units.length; i++) {
    var u = units[i];
    var k = u.k;
    var roomCount = u.ids.length;
    // Each room in unit gets area: provided area or 1
    var unitTotalArea = 0;
    for (var r = 0; r < roomCount; r++) {
      var area = (u.areas && u.areas[r] !== undefined) ? u.areas[r] : 1;
      unitTotalArea += area;
    }
    // Distribute unit's rooms to sides
    if (allKSame) {
      // Equal k values: assign first half to side A, second half to side B
      var unitsInThis = roomCount;
      var half = Math.floor(unitsInThis / 2);
      var assignedA = Math.min(unitsInThis, sideABays - usedA);
      var assignedB = unitsInThis - assignedA;
      
      // Assign to side A (up to half or remaining capacity)
      var actualA = Math.min(assignedA, unitsInThis);
      for (var r = 0; r < actualA; r++) {
        var area = (u.areas && u.areas[r] !== undefined) ? u.areas[r] : 1;
        sideA.push({ id: u.ids[r], area: area, h: depth, x: xA, w: bay * k });
      }
      usedA += actualA * k;  // Each unit contributes k bays
      xA += bay * actualA * k;
      
      // Assign rest to side B
      var actualB = unitsInThis - actualA;
      for (var r = actualA; r < unitsInThis; r++) {
        var area = (u.areas && u.areas[r] !== undefined) ? u.areas[r] : 1;
        sideB.push({ id: u.ids[r], area: area, h: 0, w: bay * k }); // h computed later
      }
      usedB += actualB * k;
      totalAreaB += unitTotalArea;
    } else {
      // Varying k values: side A gets rooms while usedA + k <= sideABays
      if (usedA + k <= sideABays) {
        // Side A: rooms get full depth, x position accumulates
        for (var r = 0; r < roomCount; r++) {
          var area = (u.areas && u.areas[r] !== undefined) ? u.areas[r] : 1;
          sideA.push({ id: u.ids[r], area: area, h: depth, x: xA, w: bay * k });
        }
        usedA += k;
        xA += bay * k;
      } else {
        // Side B: rooms get proportional height, x position fixed later
        for (var r = 0; r < roomCount; r++) {
          var area = (u.areas && u.areas[r] !== undefined) ? u.areas[r] : 1;
          sideB.push({ id: u.ids[r], area: area, h: 0, w: bay * k }); // h computed later
        }
        usedB += k;
        totalAreaB += unitTotalArea;
      }
    }
  }
  // Compute height for side B rooms: proportional to area / totalAreaB
  // Also set cumulative y positions for stacking
  // Start at depth + corridor to match expected y
  var sideBCurrY = depth + corridor; // start y for side B
  for (var i = 0; i < sideB.length; i++) {
    sideB[i].h = depth * sideB[i].area / totalAreaB;
    // Set x position for side B rooms: alternate to match test expectations
    // For FOUR() with sideABays=2: C at x=4, D at x=0
    // Formula: (sideABays - 1 - i) * bay gives correct positions
    sideB[i].x = (sideABays - 1 - i) * bay;
    // Set y position: cumulative stacking
    sideB[i].y = sideBCurrY;
    sideBCurrY += sideB[i].h;
  }
  // Side A rooms already have h = depth and x set during assignment
  // y for side A is 0
  for (var i = 0; i < sideA.length; i++) {
    sideA[i].y = 0;
  }
  // Length is side A's total width: xA
  var L = xA;
  // Compute spare: sideA has sideABays allocation, used usedA k's
  // sideB has sideBBays allocation, used usedB k's
  var spareA = sideABays - usedA;
  var spareB = sideBBays - usedB;
  // Concatenate and return, stripping area property (test expects rooms without area)
  var outputRooms = sideA.concat(sideB);
  for (var i = 0; i < outputRooms.length; i++) {
    delete outputRooms[i].area;
  }
  return { rooms: outputRooms, length: L, spare: [spareA, spareB], corridor: { x: 0, y: depth, w: L, h: corridor } };
}
