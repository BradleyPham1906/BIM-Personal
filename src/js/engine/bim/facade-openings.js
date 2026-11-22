
/* ================= __acad3dV193: LOD-F, LOD3 openings on rectified facades, the pure part =================
     docs/research/research-notion-v191-openings.md and docs/work-orders/v193/SPEC.md. Openings on a rectified facade:
     one-dimensional clusters, snapping, regularised rows and columns, overlaps, the app's wall opening. Each function is a
     work order, added below as it is built; none uses another file's names.
*/

function bimOpnCluster(values, tol) {
  tol = tol === undefined || tol < 0 ? 0.05 : tol;
  var indexed = values.map(function(value, index) { return [value, index]; });
  indexed.sort(function(a, b) { return a[0] - b[0] || a[1] - b[1]; });
  var clusters = [];
  var members = [];
  var sum = 0;
  var previous = null;
  indexed.forEach(function(entry) {
    var value = entry[0];
    var index = entry[1];
    if (previous !== null && value - previous > tol) {
      clusters.push({ members: members, mean: sum / members.length });
      members = [];
      sum = 0;
    }
    members.push(index);
    sum += value;
    previous = value;
  });
  if (members.length) clusters.push({ members: members, mean: sum / members.length });
  clusters.forEach(function(cluster) { cluster.members.sort(function(a, b) { return a - b; }); });
  return clusters;
}
/* --- WO-02 --- */
function bimOpnSnap(values, tol) {
  var result = values.slice();
  bimOpnCluster(values, tol).forEach(function(cluster) {
    cluster.members.forEach(function(index) { result[index] = cluster.mean; });
  });
  return result;
}

/* --- WO-03 --- */
function bimOpnRegularise(rects, tol) {
  var sills = rects.map(function(rect) { return rect.y; });
  var heads = rects.map(function(rect) { return rect.y + rect.h; });
  var centres = rects.map(function(rect) { return rect.x + rect.w / 2; });
  var snappedSills = bimOpnSnap(sills, tol);
  var snappedHeads = bimOpnSnap(heads, tol);
  var snappedCentres = bimOpnSnap(centres, tol);
  return rects.map(function(rect, index) {
    var x = snappedCentres[index] - rect.w / 2;
    var y = snappedSills[index];
    var head = snappedHeads[index];
    return {
      x: x,
      y: y,
      w: rect.w,
      h: head - y,
      moved: Math.max(Math.abs(x - rect.x), Math.abs(y - rect.y), Math.abs(head - (rect.y + rect.h)))
    };
  });
}

/* --- WO-04 --- */
function bimOpnOverlap(rects) {
  var pairs = [];
  var i;
  var j;
  for (i = 0; i < rects.length; i++) {
    for (j = i + 1; j < rects.length; j++) {
      var a = rects[i];
      var b = rects[j];
      var overlapX = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
      var overlapY = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
      if (overlapX > 1e-9 && overlapY > 1e-9) pairs.push([i, j]);
    }
  }
  return pairs;
}

/* --- WO-05 --- */
function bimOpnToWall(rect, len, height) {
  if (rect.w <= 0 || rect.h <= 0 || rect.x < 0 || rect.x + rect.w > len || rect.y < 0) return null;
  if (height > 0 && rect.y + rect.h > height) return null;
  return {
    along: rect.x + rect.w / 2,
    sill: rect.y,
    width: rect.w,
    height: rect.h,
    kind: rect.y <= 0.05 ? 'door' : 'window'
  };
}
