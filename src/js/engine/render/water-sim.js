

  /* ================= __acad3dV220: Water and presentation rendering, the pure part =================
     docs/research/research-notion-later-water-presentation.md and docs/work-orders/v220/SPEC.md. A heightfield wave step,
     a drop, Schlick's Fresnel, a caustic's brightness by area ratio. Each function is a work order, added below as it is
     built; none uses another file's names. */
function bimWtrStep(h, v, n, damp) {
  var i, j, newV, mean, newH;
  var newHArr = new Array(n * n).fill(0);
  var newVArr = new Array(n * n).fill(0);
  damp = damp <= 0 ? 0.995 : (damp > 1 ? 1 : damp);
  for (i = 1; i < n - 1; i += 1) {
    for (j = 1; j < n - 1; j += 1) {
      mean = (h[(i - 1) * n + j] + h[(i + 1) * n + j] + h[i * n + (j - 1)] + h[i * n + (j + 1)]) / 4;
      newV = v[i * n + j] + ((mean - h[i * n + j]) * 2) * damp;
      newH = h[i * n + j] + newV;
      newHArr[i * n + j] = newH;
      newVArr[i * n + j] = newV;
    }
  }
  // boundary unchanged
  return { h: newHArr, v: newVArr };
}

function bimWtrDrop(h, n, x, y, r, s) {
  var i, j, d, w, copyH, newH;
  copyH = h && h.slice ? h.slice() : Array.from(h || []);
  newH = new Array(n * n);
  for (var k = 0; k < n * n; k += 1) newH[k] = 0;
  for (i = 1; i < n - 1; i += 1) {
    for (j = 1; j < n - 1; j += 1) {
      d = Math.sqrt((i - x) * (i - x) + (j - y) * (j - y));
      if (d / r < 1) {
        w = 0.5 + Math.cos(Math.PI * (d / r)) / 2;
        newH[i * n + j] = copyH[i * n + j] + s * w;
      } else {
        newH[i * n + j] = copyH[i * n + j];
      }
    }
  }
  // boundary unchanged
  return newH;
}

function bimWtrSchlick(n1, n2, cosT) {
  var f0 = ((n1 - n2) * (n1 - n2)) / ((n1 + n2) * (n1 + n2));
  return f0 + (1 - f0) * Math.pow(1 - cosT, 5);
}

function bimWtrCaustic(oldA, newA) {
  if (newA <= 0) return Infinity;
  return oldA / newA;
}
