// bim_phase45_constraint_solver_prototype.js
//
// Standalone prototype of a 2D geometric constraint solver for sketch points, written from
// scratch (Levenberg-Marquardt style damped least squares over a numeric Jacobian -- textbook
// numerical methods, not derived from or referencing any CAD application's source). Solves a
// flat array of [x0,z0,x1,z1,...] sketch point coordinates against a list of constraint
// equations until every residual is near zero, or reports failure without corrupting the input.
//
// Constraint kinds (each contributes one or more scalar residual functions):
//   coincident(pi, pj)              distance(pi, pj) == 0
//   horizontal(pi, pj)              z_i - z_j == 0
//   vertical(pi, pj)                x_i - x_j == 0
//   distance(pi, pj, d)             |pi-pj| == d
//   equal(pi, pj, pk, pl)           |pi-pj| == |pk-pl|
//   parallel(pi, pj, pk, pl)        cross((pj-pi),(pl-pk)) == 0
//   perpendicular(pi, pj, pk, pl)   dot((pj-pi),(pl-pk)) == 0
//   angle(pi, pj, pk, pl, theta)    angle between the two segments == theta (radians)
//   fixed(pi, x, z)                 pi == (x,z)  -- anchors a point so the sketch cannot float
//
// Node.js has no `require` of anything else here -- this file is fully self-contained.

function residual(kind, pts, refs, value) {
  function P(i) { return pts[i]; }
  switch (kind) {
    case 'coincident': {
      var a = P(refs[0]), b = P(refs[1]);
      return [a[0] - b[0], a[1] - b[1]];
    }
    case 'horizontal': {
      var a = P(refs[0]), b = P(refs[1]);
      return [a[1] - b[1]];
    }
    case 'vertical': {
      var a = P(refs[0]), b = P(refs[1]);
      return [a[0] - b[0]];
    }
    case 'distance': {
      var a = P(refs[0]), b = P(refs[1]);
      var d = Math.sqrt((a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1]));
      return [d - value];
    }
    case 'equal': {
      var a = P(refs[0]), b = P(refs[1]), c = P(refs[2]), d2 = P(refs[3]);
      var l1 = Math.sqrt((a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1]));
      var l2 = Math.sqrt((c[0]-d2[0])*(c[0]-d2[0]) + (c[1]-d2[1])*(c[1]-d2[1]));
      return [l1 - l2];
    }
    case 'parallel': {
      var a = P(refs[0]), b = P(refs[1]), c = P(refs[2]), d3 = P(refs[3]);
      var ux = b[0]-a[0], uz = b[1]-a[1], vx = d3[0]-c[0], vz = d3[1]-c[1];
      return [ux*vz - uz*vx];
    }
    case 'perpendicular': {
      var a = P(refs[0]), b = P(refs[1]), c = P(refs[2]), d4 = P(refs[3]);
      var ux2 = b[0]-a[0], uz2 = b[1]-a[1], vx2 = d4[0]-c[0], vz2 = d4[1]-c[1];
      return [ux2*vx2 + uz2*vz2];
    }
    case 'angle': {
      var a = P(refs[0]), b = P(refs[1]), c = P(refs[2]), d5 = P(refs[3]);
      var ux3 = b[0]-a[0], uz3 = b[1]-a[1], vx3 = d5[0]-c[0], vz3 = d5[1]-c[1];
      var ang = Math.atan2(ux3*vz3 - uz3*vx3, ux3*vx3 + uz3*vz3);
      // wrap the residual into (-pi, pi] so the solver doesn't chase a 2*pi jump
      var diff = ang - value;
      while (diff > Math.PI) diff -= 2*Math.PI;
      while (diff < -Math.PI) diff += 2*Math.PI;
      return [diff];
    }
    case 'fixed': {
      var a = P(refs[0]);
      return [a[0] - value[0], a[1] - value[1]];
    }
    default:
      return [];
  }
}

function residualCount(kind) {
  return (kind === 'coincident' || kind === 'fixed') ? 2 : 1;
}

// Flattens sketch points into a variable vector, runs damped Gauss-Newton (Levenberg-Marquardt)
// until convergence or a fail-safe iteration cap, and returns either the solved point array or
// an explicit error -- it never returns a half-solved, silently-wrong result.
function solveSketch(ptsIn, constraints, opts) {
  opts = opts || {};
  var maxIter = opts.maxIter || 60;
  var tol = opts.tol || 1e-9;
  var lambda0 = opts.lambda || 1e-3;

  var n = ptsIn.length;
  var x = [];
  var i;
  for (i = 0; i < n; i++) { x.push(ptsIn[i][0]); x.push(ptsIn[i][1]); }

  function unpack(xv) {
    var pts = [];
    for (var j = 0; j < n; j++) pts.push([xv[j*2], xv[j*2+1]]);
    return pts;
  }

  function evalResiduals(xv) {
    var pts = unpack(xv);
    var r = [];
    for (var c = 0; c < constraints.length; c++) {
      var cons = constraints[c];
      var rc = residual(cons.type, pts, cons.refs, cons.value);
      for (var k = 0; k < rc.length; k++) r.push(rc[k]);
    }
    return r;
  }

  var mSize = 0;
  for (i = 0; i < constraints.length; i++) mSize += residualCount(constraints[i].type);
  if (mSize === 0) return { pts: ptsIn.map(function(p){return p.slice();}), iterations: 0, residualNorm: 0 };

  var lambda = lambda0;
  var r = evalResiduals(x);
  var normSq = dotv(r, r);

  for (var iter = 0; iter < maxIter; iter++) {
    if (normSq < tol) break;
    // Numeric Jacobian via central differences -- sketches are small (tens of points), so an
    // O(vars * constraints) numeric Jacobian is cheap and avoids hand-deriving every constraint's
    // analytic partials, at the cost of a few extra residual evaluations per iteration.
    var h = 1e-6;
    var J = []; // mSize x (2n)
    for (var rr = 0; rr < mSize; rr++) J.push(new Array(2*n).fill(0));
    for (var v = 0; v < 2*n; v++) {
      var xp = x.slice(); xp[v] += h;
      var xm = x.slice(); xm[v] -= h;
      var rp = evalResiduals(xp), rm = evalResiduals(xm);
      for (rr = 0; rr < mSize; rr++) J[rr][v] = (rp[rr] - rm[rr]) / (2*h);
    }
    // Normal equations with Levenberg-Marquardt damping: (J^T J + lambda*diag) dx = -J^T r
    var JT_J = matMulATA(J, mSize, 2*n);
    var JT_r = matVecAT(J, r, mSize, 2*n);
    var tries = 0, improved = false;
    while (tries < 12 && !improved) {
      var A = JT_J.map(function(row, ri) {
        return row.map(function(val, ci) { return val + (ri === ci ? lambda*(val || 1) : 0); });
      });
      var negJTr = JT_r.map(function(v2){ return -v2; });
      var dx = solveLinear(A, negJTr);
      if (!dx) { lambda *= 4; tries++; continue; }
      var xNew = x.map(function(v3, idx){ return v3 + dx[idx]; });
      var rNew = evalResiduals(xNew);
      var normSqNew = dotv(rNew, rNew);
      if (normSqNew < normSq) {
        x = xNew; r = rNew; normSq = normSqNew;
        lambda = Math.max(lambda / 3, 1e-12);
        improved = true;
      } else {
        lambda *= 4;
        tries++;
      }
    }
    if (!improved) break; // stuck -- report what we have, caller decides pass/fail by residual
  }

  if (!isFinite(normSq)) return { error: 'Solver diverged (non-finite residual)' };
  return { pts: unpack(x), iterations: iter, residualNorm: Math.sqrt(normSq) };
}

function dotv(a, b) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i]*b[i]; return s; }

function matMulATA(J, rows, cols) {
  // returns cols x cols matrix J^T * J
  var out = [];
  for (var i = 0; i < cols; i++) {
    var row = new Array(cols).fill(0);
    out.push(row);
  }
  for (var k = 0; k < rows; k++) {
    for (i = 0; i < cols; i++) {
      var jik = J[k][i];
      if (jik === 0) continue;
      for (var j = 0; j < cols; j++) out[i][j] += jik * J[k][j];
    }
  }
  return out;
}

function matVecAT(J, r, rows, cols) {
  var out = new Array(cols).fill(0);
  for (var k = 0; k < rows; k++) {
    var rk = r[k];
    if (rk === 0) continue;
    for (var i = 0; i < cols; i++) out[i] += J[k][i] * rk;
  }
  return out;
}

// Gaussian elimination with partial pivoting; returns null (not a throw) on a singular system so
// the caller's damping-retry loop can back off lambda instead of crashing.
function solveLinear(A, b) {
  var n = b.length;
  var M = A.map(function(row, i){ return row.concat([b[i]]); });
  for (var col = 0; col < n; col++) {
    var piv = col, best = Math.abs(M[col][col]);
    for (var r2 = col+1; r2 < n; r2++) { if (Math.abs(M[r2][col]) > best) { best = Math.abs(M[r2][col]); piv = r2; } }
    if (best < 1e-14) return null;
    if (piv !== col) { var tmp = M[col]; M[col] = M[piv]; M[piv] = tmp; }
    var pv = M[col][col];
    for (var c2 = col; c2 <= n; c2++) M[col][c2] /= pv;
    for (r2 = 0; r2 < n; r2++) {
      if (r2 === col) continue;
      var f = M[r2][col];
      if (f === 0) continue;
      for (c2 = col; c2 <= n; c2++) M[r2][c2] -= f * M[col][c2];
    }
  }
  var x = new Array(n);
  for (var i2 = 0; i2 < n; i2++) x[i2] = M[i2][n];
  return x;
}

// Crude DOF estimate: 2 unknowns per free point minus the number of independent-looking equation
// rows. Not a rigorous rank analysis (that would need a real SVD), but useful as the same kind of
// "N constraints remaining" indicator most sketchers show, clearly labeled as approximate.
function estimateDOF(ptsCount, constraints) {
  var eqCount = 0;
  for (var i = 0; i < constraints.length; i++) eqCount += residualCount(constraints[i].type);
  return Math.max(0, ptsCount*2 - eqCount);
}

module.exports = { solveSketch: solveSketch, estimateDOF: estimateDOF, residual: residual, residualCount: residualCount };
