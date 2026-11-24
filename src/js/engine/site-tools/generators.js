

  /* ================= __acad3dV213: Generators: massing, parking, lots, the pure part =================
     docs/research/research-later-generators.md and docs/work-orders/v213/SPEC.md. The achievable area and its plates,
     storeys in a height, stalls from ratios, stalls in a rectangle, lots along a frontage. Each function is a work order,
     added below as it is built; none uses another file's names. */

function bimGenAchievable(lot, far, cov, levels) {
  var plateCap = lot * cov;
  var capacity = plateCap * levels;
  var farLimit = lot * far;
  var achievable = capacity < farLimit ? capacity : farLimit;
  var plates = [];
  var left = achievable;
  var i;
  for (i = 0; i < levels; i += 1) {
    plates.push(left < plateCap ? left : plateCap);
    left -= plates[i];
  }
  return { plateCap: plateCap, capacity: capacity, farLimit: farLimit, achievable: achievable, plates: plates };
}

function bimGenStoreys(h, ftf) {
  if (!(ftf > 0)) {
    ftf = 3.5;
  }
  if (!(h > 0)) {
    return { storeys: 0, top: 0 };
  }
  var storeys = Math.floor(h / ftf + 1e-9);
  return { storeys: storeys, top: storeys * ftf };
}

function bimGenStalls(needs) {
  var total = 0;
  var i;
  for (i = 0; i < needs.length; i += 1) {
    var n = needs[i];
    if (!(n.qty > 0) || !(n.per > 0)) {
      continue;
    }
    total += n.qty / n.per * n.ratio;
  }
  var result = Math.ceil(total - 1e-9);
  return result === 0 ? 0 : result;
}

function bimGenParking(w, d, stall, aisle) {
  var sw = 2.6;
  var sd = 5.5;
  if (stall && stall.w > 0) {
    sw = stall.w;
  }
  if (stall && stall.d > 0) {
    sd = stall.d;
  }
  var al = 7.2;
  if (aisle > 0) {
    al = aisle;
  }
  var perRow = Math.floor(w / sw + 1e-9);
  var module = 2 * sd + al;
  var doubleModules = Math.floor(d / module + 1e-9);
  var rest = d - doubleModules * module;
  var singleRows = rest >= sd + al ? 1 : 0;
  var stalls = perRow * (2 * doubleModules + singleRows);
  return { perRow: perRow, doubleModules: doubleModules, singleRows: singleRows, stalls: stalls };
}

function bimGenLots(frontage, target) {
  if (!(frontage > 0) || !(target > 0)) {
    return [];
  }
  var n = Math.floor(frontage / target + 1e-9);
  if (n < 1) {
    n = 1;
  }
  var size = frontage / n;
  var lots = [];
  var i;
  for (i = 0; i < n; i += 1) {
    lots.push(size);
  }
  return lots;
}
