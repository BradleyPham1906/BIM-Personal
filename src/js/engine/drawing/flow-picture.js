

  /* ================= __acad3dV188: Freeform F6, picture planes, text objects, flow along a surface, the pure part =================
     docs/research/research-freeform-f1-f7.md (F6) and docs/work-orders/v188/SPEC.md. Picture planes at the image's
     aspect, text boxes, and flow along a bilinear patch (points, height along its normal). Each function is a work order,
     added below as it is built; none uses another file's names. */
function bimPicPlane(wPx, hPx, widthM) {
  if (wPx <= 0 || hPx <= 0 || widthM <= 0) {
    return null;
  }
  var h = widthM * hPx / wPx;
  return { w: widthM, h: h, corners: [[0, 0], [widthM, 0], [widthM, h], [0, h]], uv: [[0, 1], [1, 1], [1, 0], [0, 0]] };
}
function bimTextBox(lines, h, ratio, gap) {
  if (!lines || lines.length === 0 || !(h > 0)) {
    return { w: 0, h: 0 };
  }
  if (!(ratio > 0)) {
    ratio = 0.6;
  }
  if (!(gap > 0)) {
    gap = 1.2;
  }
  var longest = 0, i;
  for (i = 0; i < lines.length; i++) {
    if (lines[i].length > longest) {
      longest = lines[i].length;
    }
  }
  return { w: longest * h * ratio, h: h + (lines.length - 1) * h * gap };
}
function bimFlowBox(pts) {
  if (!pts || pts.length === 0) {
    return null;
  }
  var minX = pts[0][0], minY = pts[0][1], maxX = pts[0][0], maxY = pts[0][1];
  var i, p;
  for (i = 1; i < pts.length; i++) {
    p = pts[i];
    minX = Math.min(minX, p[0]);
    minY = Math.min(minY, p[1]);
    maxX = Math.max(maxX, p[0]);
    maxY = Math.max(maxY, p[1]);
  }
  return [minX, minY, maxX, maxY];
}
function bimFlowBilinear(q, u, v) {
  var a = (1 - u) * (1 - v);
  var b = u * (1 - v);
  var c = u * v;
  var d = (1 - u) * v;
  return [
    a * q[0][0] + b * q[1][0] + c * q[2][0] + d * q[3][0],
    a * q[0][1] + b * q[1][1] + c * q[2][1] + d * q[3][1],
    a * q[0][2] + b * q[1][2] + c * q[2][2] + d * q[3][2]
  ];
}
