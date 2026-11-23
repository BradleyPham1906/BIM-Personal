

  /* ================= __acad3dV189: Freeform F7, Make2D (hidden-line drawings), the pure part =================
     docs/research/research-freeform-f1-f7.md (F7) and docs/work-orders/v189/SPEC.md. Make2D on meshes: projection to a
     view, the edges a drawing keeps, a depth test against triangles, an edge cut to its visible runs. Each function is a
     work order, added below as it is built; none uses another file's names. */
function bimM2Project(p, view) {
  return [
    p[0] * view.right[0] + p[1] * view.right[1] + p[2] * view.right[2],
    p[0] * view.up[0] + p[1] * view.up[1] + p[2] * view.up[2],
    p[0] * view.dir[0] + p[1] * view.dir[1] + p[2] * view.dir[2]
  ];
}
function bimM2Edges(m, dir, creaseDeg) {
  var v = m.v, f = m.f, nf = f.length;
  var norms = [], i, j, face, x, y, z, c, s, len;
  for (i = 0; i < nf; i++) {
    face = f[i];
    x = 0; y = 0; z = 0;
    for (j = 0; j < face.length; j++) {
      c = v[face[j]];
      s = v[face[(j + 1) % face.length]];
      x += (c[1] - s[1]) * (c[2] + s[2]);
      y += (c[2] - s[2]) * (c[0] + s[0]);
      z += (c[0] - s[0]) * (c[1] + s[1]);
    }
    len = Math.sqrt(x * x + y * y + z * z);
    norms.push([x / len, y / len, z / len]);
  }
  var edgeMap = {}, order = [], a, b, key, ei, ej;
  for (i = 0; i < nf; i++) {
    face = f[i];
    for (j = 0; j < face.length; j++) {
      ei = face[j];
      ej = face[(j + 1) % face.length];
      a = ei < ej ? ei : ej;
      b = ei < ej ? ej : ei;
      key = a + ',' + b;
      if (!edgeMap[key]) {
        edgeMap[key] = [i];
        order.push(key);
      } else if (edgeMap[key].length < 2 && edgeMap[key][0] !== i) {
        edgeMap[key].push(i);
      }
    }
  }
  var result = [], k, parts, faces, dd0, dd1, dot, cosC;
  if (!(creaseDeg > 0)) {
    creaseDeg = 30;
  }
  cosC = Math.cos(creaseDeg * Math.PI / 180);
  for (k = 0; k < order.length; k++) {
    key = order[k];
    parts = key.split(',');
    a = +parts[0];
    b = +parts[1];
    faces = edgeMap[key];
    if (faces.length !== 2) {
      result.push([a, b, 'boundary']);
    } else {
      dd0 = norms[faces[0]][0] * dir[0] + norms[faces[0]][1] * dir[1] + norms[faces[0]][2] * dir[2];
      dd1 = norms[faces[1]][0] * dir[0] + norms[faces[1]][1] * dir[1] + norms[faces[1]][2] * dir[2];
      if ((dd0 < 0) !== (dd1 < 0)) {
        result.push([a, b, 'silhouette']);
      } else {
        dot = norms[faces[0]][0] * norms[faces[1]][0] + norms[faces[0]][1] * norms[faces[1]][1] + norms[faces[0]][2] * norms[faces[1]][2];
        if (dot < cosC) {
          result.push([a, b, 'crease']);
        }
      }
    }
  }
  return result;
}
function bimM2Hidden(p, tris, view, eps) {
  if (!(eps > 0)) {
    eps = 1e-6;
  }
  var pp = bimM2Project(p, view);
  var px = pp[0], py = pp[1], pd = pp[2];
  var nt = tris.length, i, tri, q0, q1, q2;
  var ax, ay, bx, by, cx, cy, denom, wa, wb, wc, id;
  for (i = 0; i < nt; i++) {
    tri = tris[i];
    q0 = bimM2Project(tri[0], view);
    q1 = bimM2Project(tri[1], view);
    q2 = bimM2Project(tri[2], view);
    ax = q0[0]; ay = q0[1];
    bx = q1[0]; by = q1[1];
    cx = q2[0]; cy = q2[1];
    denom = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy);
    if (!(denom > 0) && !(denom < 0)) {
      continue;
    }
    wa = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / denom;
    wb = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / denom;
    wc = 1 - wa - wb;
    if (wa >= eps && wb >= eps && wc >= eps) {
      id = wa * q0[2] + wb * q1[2] + wc * q2[2];
      if (id < pd - eps) {
        return true;
      }
    }
  }
  return false;
}
function bimM2Visible(a, b, tris, view, samples) {
  if (!(samples > 0)) {
    samples = 16;
  }
  var dx = b[0] - a[0], dy = b[1] - a[1], dz = b[2] - a[2];
  var kept = [], i, t, mx, my, mz;
  for (i = 0; i < samples; i++) {
    t = (i + 0.5) / samples;
    mx = a[0] + dx * t;
    my = a[1] + dy * t;
    mz = a[2] + dz * t;
    kept.push(!bimM2Hidden([mx, my, mz], tris, view));
  }
  var result = [], runStart = -1, t0, t1, x0, y0, z0, x1, y1, z1, p0, p1;
  for (i = 0; i <= samples; i++) {
    if (i < samples && kept[i]) {
      if (runStart < 0) {
        runStart = i;
      }
    } else if (runStart >= 0) {
      t0 = runStart / samples;
      t1 = i / samples;
      x0 = a[0] + dx * t0;
      y0 = a[1] + dy * t0;
      z0 = a[2] + dz * t0;
      x1 = a[0] + dx * t1;
      y1 = a[1] + dy * t1;
      z1 = a[2] + dz * t1;
      p0 = bimM2Project([x0, y0, z0], view);
      p1 = bimM2Project([x1, y1, z1], view);
      result.push([[p0[0], p0[1]], [p1[0], p1[1]]]);
      runStart = -1;
    }
  }
  return result;
}
