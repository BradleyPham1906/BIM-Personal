

  /* ================= __acad3dV186: Freeform F4, surface analysis, the pure part =================
     docs/research/research-freeform-f1-f7.md (F4) and docs/work-orders/v186/SPEC.md. Face normals and areas (Newell),
     vertex normals, draft angles, zebra stripes, Gaussian curvature by angle deficit. Each function is a work order, added
     below as it is built; none uses another file's names. */

function bimAnFaceNormal(v, face) {
  var n = [0, 0, 0], i, a, b, len;
  for (i = 0; i < face.length; i++) {
    a = v[face[i]];
    b = v[face[(i + 1) % face.length]];
    n[0] += (a[1] - b[1]) * (a[2] + b[2]);
    n[1] += (a[2] - b[2]) * (a[0] + b[0]);
    n[2] += (a[0] - b[0]) * (a[1] + b[1]);
  }
  len = Math.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
  if (len < 1e-15) {
    return { n: [0, 0, 0], area: 0 };
  }
  return { n: [n[0] / len, n[1] / len, n[2] / len], area: len / 2 };
}
