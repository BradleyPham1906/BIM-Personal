// bim_phase45_constraint_solver_prototype_tests.js
//
// Node-only correctness tests for bim_phase45_constraint_solver_prototype.js, run before any of
// that solver's logic is ported into canvas_v10_work.html. These are not the browser regression
// suite (that comes later, against the embedded copy) -- this is the "does the algorithm itself
// actually converge to the right answer" gate.

var solver = require('./bim_phase45_constraint_solver_prototype.js');
var solveSketch = solver.solveSketch;
var estimateDOF = solver.estimateDOF;
var residual = solver.residual;

var pass = 0, fail = 0;

function approx(a, b, eps) {
  eps = eps === undefined ? 1e-4 : eps;
  return Math.abs(a - b) < eps;
}

function check(name, cond) {
  if (cond) { pass++; }
  else { fail++; console.log('FAIL: ' + name); }
}

// ---------------------------------------------------------------------------
// Test 1: fixed + horizontal + vertical + distance solves a known 3-4-5 right triangle.
// A is pinned at the origin. B is forced horizontal from A at distance 3. C is forced vertical
// from B at distance 4. The hypotenuse A-C must come out to exactly 5 by Pythagoras -- nothing in
// the constraint list states that fact directly, so this genuinely exercises the solver rather
// than checking a value that was fed in.
(function test1_rightTriangle() {
  var pts = [[0.3, 0.2], [2.5, 0.6], [2.9, 3.4]]; // perturbed initial guess
  var cons = [
    { type: 'fixed', refs: [0], value: [0, 0] },
    { type: 'horizontal', refs: [0, 1] },
    { type: 'distance', refs: [0, 1], value: 3 },
    { type: 'vertical', refs: [1, 2] },
    { type: 'distance', refs: [1, 2], value: 4 }
  ];
  var res = solveSketch(pts, cons);
  check('test1: solver did not error', !res.error);
  check('test1: residual converged near zero', res.residualNorm < 1e-6);
  check('test1: A pinned at origin', approx(res.pts[0][0], 0) && approx(res.pts[0][1], 0));
  check('test1: B is horizontal from A at distance 3', approx(res.pts[1][0], 3) && approx(res.pts[1][1], 0));
  check('test1: C is vertical from B at distance 4', approx(res.pts[2][0], 3) && approx(res.pts[2][1], 4));
  var ac = Math.sqrt(res.pts[2][0]*res.pts[2][0] + res.pts[2][1]*res.pts[2][1]);
  check('test1: hypotenuse A-C computes to 5 (3-4-5 triangle, not asserted directly by any constraint)', approx(ac, 5, 1e-3));
})();

// ---------------------------------------------------------------------------
// Test 2: coincident constraint merges two separate points onto each other.
(function test2_coincident() {
  var pts = [[0, 0], [4, 4]];
  var cons = [{ type: 'coincident', refs: [0, 1] }];
  var res = solveSketch(pts, cons);
  check('test2: solver did not error', !res.error);
  check('test2: points merged (coincident residual ~0)', res.residualNorm < 1e-6);
  check('test2: x coordinates equal', approx(res.pts[0][0], res.pts[1][0]));
  check('test2: z coordinates equal', approx(res.pts[0][1], res.pts[1][1]));
})();

// ---------------------------------------------------------------------------
// Test 3: an over-constrained / contradictory system must NOT be reported as solved. Two
// conflicting distance constraints on the same pinned pair of points (3 vs 5) cannot both be
// satisfied -- the solver must report a nonzero residual rather than silently claiming success,
// per the "fail gracefully, never a silently-wrong result" requirement.
(function test3_conflicting() {
  var pts = [[0, 0], [4, 0]];
  var cons = [
    { type: 'fixed', refs: [0], value: [0, 0] },
    { type: 'horizontal', refs: [0, 1] },
    { type: 'distance', refs: [0, 1], value: 3 },
    { type: 'distance', refs: [0, 1], value: 5 }
  ];
  var res = solveSketch(pts, cons);
  check('test3: solver did not error (reports via residual, not exception)', !res.error);
  check('test3: contradictory constraints leave a nonzero residual (not falsely marked solved)', res.residualNorm > 0.5);
})();

// ---------------------------------------------------------------------------
// Test 4: equal-length constraint drives two independent segments to the same length.
(function test4_equal() {
  var pts = [[0, 0], [3, 0], [10, 10], [10, 10.2]];
  var cons = [
    { type: 'fixed', refs: [0], value: [0, 0] },
    { type: 'horizontal', refs: [0, 1] },
    { type: 'distance', refs: [0, 1], value: 3 },
    { type: 'equal', refs: [2, 3, 0, 1] }
  ];
  var res = solveSketch(pts, cons);
  var l1 = Math.sqrt(Math.pow(res.pts[2][0]-res.pts[3][0], 2) + Math.pow(res.pts[2][1]-res.pts[3][1], 2));
  check('test4: solver did not error', !res.error);
  check('test4: residual converged', res.residualNorm < 1e-5);
  check('test4: second segment length equals first (3)', approx(l1, 3, 1e-3));
})();

// ---------------------------------------------------------------------------
// Test 5: parallel constraint drives two segments to a zero cross product (same direction).
// The second segment is fully pinned down (fixed start point + explicit length) alongside the
// parallel constraint so the system is well-determined -- leaving its length and start point
// free as well would create a flat valley (any length/position satisfies "parallel") that a
// numeric-Jacobian Gauss-Newton crawls across very slowly, which is a property of that degenerate
// setup, not a defect in the parallel residual itself.
(function test5_parallel() {
  var pts = [[0, 0], [4, 0], [1, 1], [5, 1.8]];
  var cons = [
    { type: 'fixed', refs: [0], value: [0, 0] },
    { type: 'horizontal', refs: [0, 1] },
    { type: 'distance', refs: [0, 1], value: 4 },
    { type: 'fixed', refs: [2], value: [1, 1] },
    { type: 'distance', refs: [2, 3], value: 4 },
    { type: 'parallel', refs: [0, 1, 2, 3] }
  ];
  var res = solveSketch(pts, cons);
  var ux = res.pts[1][0]-res.pts[0][0], uz = res.pts[1][1]-res.pts[0][1];
  var vx = res.pts[3][0]-res.pts[2][0], vz = res.pts[3][1]-res.pts[2][1];
  check('test5: solver did not error', !res.error);
  check('test5: residual converged', res.residualNorm < 1e-5);
  check('test5: cross product of the two segment directions is ~0 (parallel)', approx(ux*vz - uz*vx, 0, 1e-3));
})();

// ---------------------------------------------------------------------------
// Test 6: perpendicular constraint drives two segments to a zero dot product. Same
// well-determined shape as test 5, for the same reason (avoid the flat-valley degeneracy).
(function test6_perpendicular() {
  var pts = [[0, 0], [4, 0], [1, 1], [1.6, 5]];
  var cons = [
    { type: 'fixed', refs: [0], value: [0, 0] },
    { type: 'horizontal', refs: [0, 1] },
    { type: 'distance', refs: [0, 1], value: 4 },
    { type: 'fixed', refs: [2], value: [1, 1] },
    { type: 'distance', refs: [2, 3], value: 4 },
    { type: 'perpendicular', refs: [0, 1, 2, 3] }
  ];
  var res = solveSketch(pts, cons);
  var ux = res.pts[1][0]-res.pts[0][0], uz = res.pts[1][1]-res.pts[0][1];
  var vx = res.pts[3][0]-res.pts[2][0], vz = res.pts[3][1]-res.pts[2][1];
  check('test6: solver did not error', !res.error);
  check('test6: residual converged', res.residualNorm < 1e-5);
  check('test6: dot product of the two segment directions is ~0 (perpendicular)', approx(ux*vx + uz*vz, 0, 1e-3));
})();

// ---------------------------------------------------------------------------
// Test 7: angle constraint drives the angle between two segments to a specific value (60 degrees).
(function test7_angle() {
  var pts = [[0, 0], [4, 0], [0, 0], [3, 1]];
  var cons = [
    { type: 'fixed', refs: [0], value: [0, 0] },
    { type: 'fixed', refs: [2], value: [0, 0] },
    { type: 'horizontal', refs: [0, 1] },
    { type: 'distance', refs: [0, 1], value: 4 },
    { type: 'distance', refs: [2, 3], value: 4 },
    { type: 'angle', refs: [0, 1, 2, 3], value: Math.PI / 3 }
  ];
  var res = solveSketch(pts, cons);
  var ux = res.pts[1][0]-res.pts[0][0], uz = res.pts[1][1]-res.pts[0][1];
  var vx = res.pts[3][0]-res.pts[2][0], vz = res.pts[3][1]-res.pts[2][1];
  var ang = Math.atan2(ux*vz - uz*vx, ux*vx + uz*vz);
  check('test7: solver did not error', !res.error);
  check('test7: residual converged', res.residualNorm < 1e-4);
  check('test7: angle between segments is 60 degrees (pi/3)', approx(Math.abs(ang), Math.PI/3, 1e-3));
})();

// ---------------------------------------------------------------------------
// Test 8: estimateDOF returns a sane, monotonically-decreasing count as constraints are added,
// and zero constraints leaves full 2*N freedom.
(function test8_dof() {
  check('test8: 3 unconstrained points have 6 DOF', estimateDOF(3, []) === 6);
  var consA = [{ type: 'fixed', refs: [0], value: [0,0] }];
  check('test8: pinning one point removes exactly 2 DOF', estimateDOF(3, consA) === 4);
  var consB = consA.concat([{ type: 'horizontal', refs: [0,1] }, { type: 'distance', refs: [0,1], value: 3 }]);
  check('test8: adding horizontal+distance removes 2 more DOF', estimateDOF(3, consB) === 2);
  check('test8: DOF never reported negative even when over-constrained', estimateDOF(1, [
    { type: 'fixed', refs: [0], value: [0,0] },
    { type: 'horizontal', refs: [0,0] },
    { type: 'vertical', refs: [0,0] }
  ]) === 0);
})();

// ---------------------------------------------------------------------------
console.log('\n' + pass + ' passed, ' + fail + ' failed');
if (fail > 0) process.exit(1);
