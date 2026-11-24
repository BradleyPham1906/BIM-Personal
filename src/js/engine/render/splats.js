

/* ================= __acad3dV205: LOD-G, Gaussian splats as a backdrop, the pure part =================
     docs/research/research-notion-v192-splats.md and docs/work-orders/v205/SPEC.md. A .splat file read, its bounds,
     placement from two point pairs (a similarity about the vertical, Y up), placed points, back-to-front order. Each
     function is a work order, added below as it is built; none uses another file's names.
*/

function bimSplatParse(buf) {
  if (buf.byteLength % 32 !== 0) {
    return { error: 'not a .splat file (its length is not a multiple of 32)' };
  }
  var n = buf.byteLength / 32;
  var dv = new DataView(buf);
  var pos = new Float32Array(n * 3);
  var scale = new Float32Array(n * 3);
  var rgba = new Uint8Array(n * 4);
  var rot = new Float32Array(n * 4);
  for (var i = 0; i < n; i++) {
    var o = i * 32;
    for (var k = 0; k < 3; k++) {
      pos[i * 3 + k] = dv.getFloat32(o + 4 * k, true);
    }
    for (var k = 0; k < 3; k++) {
      scale[i * 3 + k] = dv.getFloat32(o + 12 + 4 * k, true);
    }
    for (var k = 0; k < 4; k++) {
      rgba[i * 4 + k] = dv.getUint8(o + 24 + k);
    }
    for (var k = 0; k < 4; k++) {
      rot[i * 4 + k] = (dv.getUint8(o + 28 + k) - 128) / 128;
    }
  }
  return { n: n, pos: pos, scale: scale, rgba: rgba, rot: rot };
}

function bimSplatBounds(pos) {
  if (pos === null || pos === undefined || pos.length === 0) {
    return null;
  }
  var n = pos.length / 3;
  var min = new Float32Array(3);
  var max = new Float32Array(3);
  min[0] = pos[0];
  min[1] = pos[1];
  min[2] = pos[2];
  max[0] = pos[0];
  max[1] = pos[1];
  max[2] = pos[2];
  for (var i = 1; i < n; i++) {
    var p = i * 3;
    if (pos[p] < min[0]) min[0] = pos[p];
    if (pos[p + 1] < min[1]) min[1] = pos[p + 1];
    if (pos[p + 2] < min[2]) min[2] = pos[p + 2];
    if (pos[p] > max[0]) max[0] = pos[p];
    if (pos[p + 1] > max[1]) max[1] = pos[p + 1];
    if (pos[p + 2] > max[2]) max[2] = pos[p + 2];
  }
  var centre = new Float32Array(3);
  centre[0] = (min[0] + max[0]) / 2;
  centre[1] = (min[1] + max[1]) / 2;
  centre[2] = (min[2] + max[2]) / 2;
  return { min: [min[0], min[1], min[2]], max: [max[0], max[1], max[2]], centre: [centre[0], centre[1], centre[2]] };
}

function bimSplatFit2(a0, a1, b0, b1) {
  var adx = a1[0] - a0[0];
  var adz = a1[2] - a0[2];
  var bdx = b1[0] - b0[0];
  var bdz = b1[2] - b0[2];
  var alen = Math.sqrt(adx * adx + adz * adz);
  var blen = Math.sqrt(bdx * bdx + bdz * bdz);
  if (alen < 1e-9 || blen < 1e-9) {
    return null;
  }
  var s = blen / alen;
  var rot = Math.atan2(bdz, bdx) - Math.atan2(adz, adx);
  var tx = b0[0] - s * (adx * Math.cos(rot) - adz * Math.sin(rot));
  var ty = b0[1] - s * a0[1];
  var tz = b0[2] - s * (adx * Math.sin(rot) + adz * Math.cos(rot));
  return { s: s, rot: rot, t: [tx, ty, tz] };
}

function bimSplatApply(T, p) {
  var s = T.s;
  var cx = Math.cos(T.rot);
  var sz = Math.sin(T.rot);
  var x = T.t[0];
  var y = s * p[1] + T.t[1];
  var z = s * p[0] + s + T.t[2];
  return [x, y, z];
}

function bimSplatOrder(pos, eye) {
  if (pos === null || pos === undefined || pos.length === 0) {
    return [];
  }
  var n = pos.length / 3;
  var d = [];
  for (var i = 0; i < n; i++) {
    var p = i * 3;
    var ex = eye ? eye[0] - pos[p] : 0;
    var ey = eye ? eye[1] - pos[p + 1] : 0;
    var ez = eye ? eye[2] - pos[p + 2] : 0;
    d[i] = ex * ex + ey * ey + ez * ez;
  }
  var order = [];
  for (var i = 0; i < n; i++) {
    order[i] = i;
  }
  order.sort(function (i, j) {
    return d[j] - d[i];
  });
  return order;
}
  /* ================= __acad3dV205: LOD-G, Gaussian splats as a backdrop, the pure part =================
     docs/research/research-notion-v192-splats.md and docs/work-orders/v205/SPEC.md. A .splat file read, its bounds,
     placement from two point pairs (a similarity about the vertical, Y up), placed points, back-to-front order. Each
     function is a work order, added below as it is built; none uses another file's names. */
