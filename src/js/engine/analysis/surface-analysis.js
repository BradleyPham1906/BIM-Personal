

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


function bimAnVertexNormals(m) {
  var v = m.v, f = m.f, n = [], i, j, k, r, len, out = [];
  for (i = 0; i < v.length; i++) {
    n.push([0, 0, 0]);
  }
  for (i = 0; i < f.length; i++) {
    r = bimAnFaceNormal(v, f[i]);
    for (j = 0; j < f[i].length; j++) {
      k = f[i][j];
      n[k][0] += r.n[0] * r.area;
      n[k][1] += r.n[1] * r.area;
      n[k][2] += r.n[2] * r.area;
    }
  }
  for (i = 0; i < v.length; i++) {
    len = Math.sqrt(n[i][0] * n[i][0] + n[i][1] * n[i][1] + n[i][2] * n[i][2]);
    if (len < 1e-15) {
      out.push(n[i]);
    } else {
      out.push([n[i][0] / len, n[i][1] / len, n[i][2] / len]);
    }
  }
  return out;
}

function bimAnDraft(n, pull) {
  var pl = Math.sqrt(pull[0] * pull[0] + pull[1] * pull[1] + pull[2] * pull[2]), c;
  c = (n[0] * pull[0] + n[1] * pull[1] + n[2] * pull[2]) / pl;
  if (c < -1) {
    c = -1;
  }
  if (c > 1) {
    c = 1;
  }
  return 90 - Math.acos(c) * 180 / Math.PI;
}

function bimAnZebra(n, view, stripes) {
  var s = Math.floor(stripes), d, r, k;
  if (!(s >= 1)) {
    s = 10;
  }
  d = n[0] * view[0] + n[1] * view[1] + n[2] * view[2];
  r = [2 * d * n[0] - view[0], 2 * d * n[1] - view[1], 2 * d * n[2] - view[2]];
  k = (r[1] + 1) / 2 * s;
  k = Math.floor(k);
  if (k < 0) {
    k = 0;
  }
  if (k > s - 1) {
    k = s - 1;
  }
  return k % 2;
}


function bimAnGauss(m) {
  var v = m.v, f = m.f, deficit = [], area = [], i, j, fi, share, prev, cur, nxt, e1, e2, len1, len2, c, ang;
  for (i = 0; i < v.length; i++) {
    deficit.push(2 * Math.PI);
    area.push(0);
  }
  for (i = 0; i < f.length; i++) {
    fi = f[i];
    share = bimAnFaceNormal(v, fi).area / fi.length;
    for (j = 0; j < fi.length; j++) {
      cur = fi[j];
      prev = fi[(j - 1 + fi.length) % fi.length];
      nxt = fi[(j + 1) % fi.length];
      e1 = [v[prev][0] - v[cur][0], v[prev][1] - v[cur][1], v[prev][2] - v[cur][2]];
      e2 = [v[nxt][0] - v[cur][0], v[nxt][1] - v[cur][1], v[nxt][2] - v[cur][2]];
      len1 = Math.sqrt(e1[0] * e1[0] + e1[1] * e1[1] + e1[2] * e1[2]);
      len2 = Math.sqrt(e2[0] * e2[0] + e2[1] * e2[1] + e2[2] * e2[2]);
      c = (e1[0] * e2[0] + e1[1] * e2[1] + e1[2] * e2[2]) / (len1 * len2);
      if (c < -1) {
        c = -1;
      }
      if (c > 1) {
        c = 1;
      }
      ang = Math.acos(c);
      deficit[cur] -= ang;
      area[cur] += share;
    }
  }
  return { deficit: deficit, area: area };
}

