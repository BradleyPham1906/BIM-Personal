

  /* ================= __acad3dV185: Freeform F3, sweeps, pipes and caps, the pure part =================
     docs/research/research-freeform-f1-f7.md (F3) and docs/work-orders/v185/SPEC.md. Rotation-minimising frames by
     double reflection; a profile swept along a rail; a circle profile; caps. Each function is a work order, added below
     as it is built; none uses another file's names. */


function bimSwpNorm(a) {
  var len = Math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]);
  if (len < 1e-15) return [0, 0, 0];
  return [a[0] / len, a[1] / len, a[2] / len];
}


function bimSwpCross(a, b) {
  return [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0]
  ];
}


function bimSwpPerp(t) {
  var e;
  if (Math.abs(t[0]) <= Math.abs(t[1]) && Math.abs(t[0]) <= Math.abs(t[2])) e = [1, 0, 0];
  else if (Math.abs(t[1]) <= Math.abs(t[2])) e = [0, 1, 0];
  else e = [0, 0, 1];
  return bimSwpNorm(bimSwpCross(t, e));
}


function bimSwpFrames(rail) {
  var npts = rail.length;
  var frames = [];
  var i, t, n, b;
  var v1, v2, len, d1, d2, dot;
  var pi, pim1, pip1;
  var prevT, prevN;
  var rn, rt;
  if (npts < 2) return [];
  for (i = 0; i < npts; i++) {
    pi = rail[i];
    if (i === 0) {
      pip1 = rail[1];
      t = [pip1[0] - pi[0], pip1[1] - pi[1], pip1[2] - pi[2]];
    } else if (i === npts - 1) {
      pim1 = rail[i - 1];
      t = [pi[0] - pim1[0], pi[1] - pim1[1], pi[2] - pim1[2]];
    } else {
      pim1 = rail[i - 1];
      pip1 = rail[i + 1];
      t = [pip1[0] - pim1[0], pip1[1] - pim1[1], pip1[2] - pim1[2]];
    }
    len = Math.sqrt(t[0] * t[0] + t[1] * t[1] + t[2] * t[2]);
    t = [t[0] / len, t[1] / len, t[2] / len];
    if (i === 0) {
      n = bimSwpPerp(t);
    } else {
      pim1 = rail[i - 1];
      v1 = [pi[0] - pim1[0], pi[1] - pim1[1], pi[2] - pim1[2]];
      d1 = v1[0] * v1[0] + v1[1] * v1[1] + v1[2] * v1[2];
      dot = v1[0] * prevN[0] + v1[1] * prevN[1] + v1[2] * prevN[2];
      rn = [prevN[0] - 2 * dot / d1 * v1[0], prevN[1] - 2 * dot / d1 * v1[1], prevN[2] - 2 * dot / d1 * v1[2]];
      dot = v1[0] * prevT[0] + v1[1] * prevT[1] + v1[2] * prevT[2];
      rt = [prevT[0] - 2 * dot / d1 * v1[0], prevT[1] - 2 * dot / d1 * v1[1], prevT[2] - 2 * dot / d1 * v1[2]];
      v2 = [t[0] - rt[0], t[1] - rt[1], t[2] - rt[2]];
      d2 = v2[0] * v2[0] + v2[1] * v2[1] + v2[2] * v2[2];
      if (d1 < 1e-30) {
        n = prevN;
      } else if (d2 < 1e-30) {
        n = rn;
      } else {
        dot = v2[0] * rn[0] + v2[1] * rn[1] + v2[2] * rn[2];
        n = [rn[0] - 2 * dot / d2 * v2[0], rn[1] - 2 * dot / d2 * v2[1], rn[2] - 2 * dot / d2 * v2[2]];
      }
      len = Math.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
      n = [n[0] / len, n[1] / len, n[2] / len];
    }
    b = bimSwpCross(t, n);
    frames.push({p: pi, t: t, n: n, b: b});
    prevT = t;
    prevN = n;
  }
  return frames;
}


function bimSwpSweep(profile, rail, closed) {
  var frames = bimSwpFrames(rail);
  var m = profile ? profile.length : 0;
  if (frames.length < 2 || m < 2) return null;
  var nframes = frames.length;
  var v = [];
  var f = [];
  var i, j, a, next;
  var p, nrm, bin, pt;
  for (i = 0; i < nframes; i++) {
    p = frames[i].p;
    nrm = frames[i].n;
    bin = frames[i].b;
    for (j = 0; j < m; j++) {
      pt = profile[j];
      v.push([p[0] + pt[0] * nrm[0] + pt[1] * bin[0], p[1] + pt[0] * nrm[1] + pt[1] * bin[1], p[2] + pt[0] * nrm[2] + pt[1] * bin[2]]);
    }
  }
  var lastJ = closed ? m : m - 1;
  for (i = 0; i < nframes - 1; i++) {
    for (j = 0; j < lastJ; j++) {
      a = i * m + j;
      next = i * m + (j + 1) % m;
      f.push([a, next, next + m, a + m]);
    }
  }
  return {v: v, f: f};
}


function bimSwpCircle(r, n) {
  var count = n === undefined || n < 3 ? 16 : Math.floor(n);
  var pts = [];
  var i, a;
  for (i = 0; i < count; i++) {
    a = 2 * Math.PI * i / count;
    pts.push([r * Math.cos(a), r * Math.sin(a)]);
  }
  return pts;
}


function bimSwpCap(mesh, start, count, flip) {
  var newMesh = {v: [], f: []};
  var i, j, k, cx, cy, cz;
  var centerIndex;
  for (i = 0; i < mesh.v.length; i++) {
    newMesh.v.push([mesh.v[i][0], mesh.v[i][1], mesh.v[i][2]]);
  }
  cx = 0;
  cy = 0;
  cz = 0;
  for (i = 0; i < count; i++) {
    j = start + i;
    cx += mesh.v[j][0];
    cy += mesh.v[j][1];
    cz += mesh.v[j][2];
  }
  cx /= count;
  cy /= count;
  cz /= count;
  centerIndex = newMesh.v.length;
  newMesh.v.push([cx, cy, cz]);
  for (i = 0; i < mesh.f.length; i++) {
    newMesh.f.push([mesh.f[i][0], mesh.f[i][1], mesh.f[i][2], mesh.f[i][3]]);
  }
  for (i = 0; i < count; i++) {
    j = start + i;
    k = start + (i + 1) % count;
    if (flip) {
      newMesh.f.push([centerIndex, k, j]);
    } else {
      newMesh.f.push([centerIndex, j, k]);
    }
  }
  return newMesh;
}

