// V253 (D3): CIRCLE 2P and 3P, ELLIPSE and REVCLOUD (engine/drawing/draw-extra.js), their geometry.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);

test('CIRCLE 2P: the two points are the ends of a diameter', () => {
  const c = E.bimCircle2P([0, 0], [4, 0]);
  assert.deepEqual(c.center, [2, 0]); near(c.radius, 2);
  assert.equal(E.bimCircle2P([1, 1], [1, 1]), null);
});

test('ELLIPSE: the axis endpoints and the other half-axis', () => {
  const e = E.bimEllipseFromAxis([0, 0], [6, 0], 1, 4);
  assert.deepEqual(e.center, [3, 0]); near(e.a, 3); near(e.b, 1);
  near(e.pts[0][0], 6); near(e.pts[1][1], 1); near(e.pts[2][0], 0);
  // the third click's distance from the axis line is the other half-axis
  near(E.bimDistToLine([10, 2], [0, 0], [6, 0]), 2);
  assert.equal(E.bimEllipseFromAxis([0, 0], [0, 0], 1), null);
});

test('REVCLOUD: arcs along the rectangle, all bulging outward', () => {
  const r = E.bimRevcloudRect([0, 0], [2, 1], 0.5);
  assert.equal(r.pts.length, 12);   // 4 + 2 + 4 + 2 arcs
  assert.equal(new Set(r.bulges).size, 1, 'every arc bulges the same way');
  // an arc bulging outward from the bottom edge passes below it: its apex has z < 0
  const arc = E.bimBulgeArc(r.pts[0], r.pts[1], r.bulges[0]);
  assert.ok(arc.apex[1] < 0, 'the bottom edge\'s arcs bulge out of the rectangle (' + arc.apex + ')');
  assert.equal(E.bimRevcloudRect([0, 0], [0, 3]), null);
});
