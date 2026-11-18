

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


function bimSrfRotate(p, o, ax, a) {
  var x = [p[0] - o[0], p[1] - o[1], p[2] - o[2]];
  var len = Math.sqrt(ax[0] * ax[0] + ax[1] * ax[1] + ax[2] * ax[2]);
  var k = [ax[0] / len, ax[1] / len, ax[2] / len];
  var c = Math.cos(a);
  var s = Math.sin(a);
  var kx = k[1] * x[2] - k[2] * x[1];
  var ky = k[2] * x[0] - k[0] * x[2];
  var kz = k[0] * x[1] - k[1] * x[0];
  var kdotx = k[0] * x[0] + k[1] * x[1] + k[2] * x[2];
  var r = [];
  r[0] = x[0] * c + kx * s + k[0] * kdotx * (1 - c) + o[0];
  r[1] = x[1] * c + ky * s + k[1] * kdotx * (1 - c) + o[1];
  r[2] = x[2] * c + kz * s + k[2] * kdotx * (1 - c) + o[2];
  return r;
}


function bimSrfRevolve(pts, o, ax, angle, segs) {
  if (!pts || pts.length < 2) return null;
  var n = pts.length;
  if (!segs || segs < 1) segs = 24;
  var full = Math.abs(angle - 2 * Math.PI) < 1e-9;
  var rings = full ? segs : segs + 1;
  var v = [];
  var j, i, r, ang;
  for (j = 0; j < rings; j++) {
    ang = angle * j / segs;
    for (i = 0; i < n; i++) {
      r = bimSrfRotate(pts[i], o, ax, ang);
      v.push([r[0], r[1], r[2]]);
    }
  }
  var f = [];
  for (j = 0; j < segs; j++) {
    for (i = 0; i < n - 1; i++) {
      var a = j * n + i;
      var b = ((j + 1) % rings) * n + i;
      f.push([a, a + 1, b + 1, b]);
    }
  }
  return { v: v, f: f };
}
