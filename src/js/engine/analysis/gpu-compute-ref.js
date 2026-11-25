

  /* ================= __acad3dV219: WebGPU compute: the CPU reference first, the pure part =================
     docs/research/research-notion-later-webgpu-compute.md and docs/work-orders/v219/SPEC.md. The CPU reference a GPU kernel
     must match: explicit diffusion in double or single precision, the comparison, a sum, workgroups. Each function is a
     work order, added below as it is built; none uses another file's names. */

/* WO-01 bimGcDiffuse(a, n, alpha, steps, f32): explicit diffusion on an n x n grid */
function bimGcDiffuse(a, n, alpha, steps, f32) {
  var grid = [];
  for (var i = 0; i < a.length; i++) {
    grid[i] = a[i];
  }
  for (var step = 0; step < steps; step++) {
    var next = [];
    for (var i = 0; i < grid.length; i++) {
      next[i] = grid[i];
    }
    for (var row = 1; row < n - 1; row++) {
      for (var col = 1; col < n - 1; col++) {
        var idx = row * n + col;
        var c = grid[idx];
        var up = grid[(row - 1) * n + col];
        var down = grid[(row + 1) * n + col];
        var left = grid[row * n + col - 1];
        var right = grid[row * n + col + 1];
        var val;
        if (f32) {
          var fa = Math.fround(alpha);
          var t1 = Math.fround(up + down);
          var t2 = Math.fround(t1 + left);
          var t3 = Math.fround(t2 + right);
          var t4 = Math.fround(t3 - 4 * c);
          var t5 = Math.fround(t4 * fa);
          val = Math.fround(c + t5);
        } else {
          val = c + alpha * (up + down + left + right - 4 * c);
        }
        next[idx] = val;
      }
    }
    grid = next;
  }
  return grid;
}

/* WO-02 bimGcCompare(a, b): max absolute difference and RMS */
function bimGcCompare(a, b) {
  var max = 0;
  var sumSq = 0;
  var len = a.length;
  for (var i = 0; i < len; i++) {
    var d = Math.abs(a[i] - b[i]);
    if (d > max) {
      max = d;
    }
    sumSq += d * d;
  }
  var rms = len > 0 ? Math.sqrt(sumSq / len) : 0;
  return { max: max, rms: rms };
}

/* WO-03 bimGcSum(a): the sum of all cells */
function bimGcSum(a) {
  var s = 0;
  for (var i = 0; i < a.length; i++) {
    s += a[i];
  }
  return s;
}

/* WO-04 bimGcWorkgroups(n, size): ceil(n / size), size defaults to 8 */
function bimGcWorkgroups(n, size) {
  if (size === undefined || size <= 0) {
    size = 8;
  }
  return Math.ceil(n / size);
}
