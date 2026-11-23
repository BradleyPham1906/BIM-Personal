

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
