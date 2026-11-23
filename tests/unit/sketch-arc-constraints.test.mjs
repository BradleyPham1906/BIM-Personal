// V267: constraints on a sketch's arcs (engine/drawing/sketch-arc-constraints.js): radius and diameter drive the
// arc's bulge, a point on an arc, a line tangent to an arc.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-6) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);
const arcOf = (pts, B, a, b) => E.bimBulgeArc(pts[a], pts[b], B[a]);

test('an arc is named by its end points in either order, and must be a neighbouring pair', () => {
  assert.equal(E.bimConArcSeg(4, 1, 2, true), 1);
  assert.equal(E.bimConArcSeg(4, 2, 1, true), 1);
  assert.equal(E.bimConArcSeg(4, 0, 3, true), 3, 'the closing segment of a closed sketch');
  assert.equal(E.bimConArcSeg(4, 0, 3, false), -1, 'an open sketch has no closing segment');
  assert.equal(E.bimConArcSeg(4, 0, 2, true), -1);
  assert.deepEqual(E.bimConArcRefs('tangent', [0, 1, 3, 2], 4, true), [0, 1, 2, 3]);
});

test('a radius drives the arc: its bulge changes, its ends stay where pinned', () => {
  // a half circle of radius 1 from (0,0) to (2,0), then straight back along a line below
  const pts = [[0, 0], [2, 0], [2, 1], [0, 1]], B = [1, 0, 0, 0];
  near(arcOf(pts, B, 0, 1).radius, 1);
  const cons = [{ type: 'radius', refs: [0, 1], value: 1.25 },
    { type: 'fixed', refs: [0], value: [0, 0] }, { type: 'fixed', refs: [1], value: [2, 0] }];
  const res = E.bimSolveSketchConstraints(pts, cons, { bulges: B });
  assert.ok(res.residualNorm < 1e-4, 'solved');
  assert.ok(res.bulges[0] > 0, 'the arc stays on its side of the chord');
  near(arcOf(res.pts, res.bulges, 0, 1).radius, 1.25, 1e-4);
  near(res.pts[1][0], 2, 1e-6);
  assert.ok(Math.abs(res.bulges[0] - 1) > 0.1, 'the bulge moved, not the ends');
  const dia = E.bimSolveSketchConstraints(pts, [{ type: 'diameter', refs: [0, 1], value: 3 }].concat(cons.slice(1)), { bulges: B });
  near(arcOf(dia.pts, dia.bulges, 0, 1).radius, 1.5, 1e-4);
});

test('a point is pulled onto the arc\'s circle', () => {
  const pts = [[0, 0], [2, 0], [3, 3]], B = [1, 0, 0];
  const res = E.bimSolveSketchConstraints(pts, [{ type: 'pointonarc', refs: [2, 0, 1] },
    { type: 'fixed', refs: [0], value: [0, 0] }, { type: 'fixed', refs: [1], value: [2, 0] }], { bulges: B });
  assert.ok(res.residualNorm < 1e-4);
  const a = arcOf(res.pts, res.bulges, 0, 1), p = res.pts[2];
  near(Math.hypot(p[0] - a.center[0], p[1] - a.center[1]), a.radius, 1e-4);
});

test('a line is made tangent to an arc: its distance from the centre is the radius', () => {
  const pts = [[0, 0], [2, 0], [4, 2], [-1, 2]], B = [1, 0, 0, 0];   // the line 2-3 runs at z = 2
  const res = E.bimSolveSketchConstraints(pts, [{ type: 'tangent', refs: [2, 3, 0, 1] },
    { type: 'fixed', refs: [0], value: [0, 0] }, { type: 'fixed', refs: [1], value: [2, 0] },
    { type: 'horizontal', refs: [2, 3] }], { bulges: B });
  assert.ok(res.residualNorm < 1e-4);
  const a = arcOf(res.pts, res.bulges, 0, 1), A = res.pts[2], L = res.pts[3];
  const d = Math.abs((a.center[0] - A[0]) * (L[1] - A[1]) - (a.center[1] - A[1]) * (L[0] - A[0])) / Math.hypot(L[0] - A[0], L[1] - A[1]);
  near(d, a.radius, 1e-4);
});

test('constraints without arcs solve as before (no bulges passed)', () => {
  const res = E.bimSolveSketchConstraints([[0, 0], [1, 0.2]], [{ type: 'horizontal', refs: [0, 1] }]);
  assert.ok(res.residualNorm < 1e-4);
  near(res.pts[0][1], res.pts[1][1], 1e-6);
});
