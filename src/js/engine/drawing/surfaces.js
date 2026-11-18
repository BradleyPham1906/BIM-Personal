

  /* ================= __acad3dV184: Freeform F2, surfaces from curves, the pure part =================
     docs/research/research-freeform-f1-f7.md (F2) and docs/work-orders/v184/SPEC.md. Surfaces from sampled curves as quad
     meshes: a grid's faces, extrude, a turn about an axis, revolve, loft, Coons patch. Each function is a work order,
     added below as it is built; none uses another file's names. */


function bimSrfGrid(rows, cols, closeU) {
  var result = [];
  for (var j = 0; j < rows - 1; j++) {
    for (var i = 0; i < (closeU ? cols : cols - 1); i++) {
      var a = j * cols + i;
      var b = j * cols + (i + 1) % cols;
      result.push([a, b, b + cols, a + cols]);
    }
  }
  return result;
}


function bimSrfExtrude(pts, vec) {
  if (!pts || pts.length < 2) return null;
  var n = pts.length;
  var v = [];
  var i;
  for (i = 0; i < n; i++) {
    v.push([pts[i][0], pts[i][1], pts[i][2]]);
  }
  for (i = 0; i < n; i++) {
    v.push([pts[i][0] + vec[0], pts[i][1] + vec[1], pts[i][2] + vec[2]]);
  }
  return { v: v, f: bimSrfGrid(2, n, false) };
}
