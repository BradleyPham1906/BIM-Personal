

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
