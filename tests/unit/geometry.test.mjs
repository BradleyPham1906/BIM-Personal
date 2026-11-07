// Geometry: vectors and meshes (core/mesh-primitives.js), plan polygons (bim/rooms.js), and the
// plan helpers precision editing uses (editing/precision-editing.js).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);
const nearAll = (a, b, eps) => { assert.equal(a.length, b.length); a.forEach((x, i) => near(x, b[i], eps)); };

test('vector arithmetic', () => {
  assert.deepEqual(E.vsub([3, 2, 1], [1, 1, 1]), [2, 1, 0]);
  assert.equal(E.vdot([1, 2, 3], [4, 5, 6]), 32);
  assert.deepEqual(E.vcross([1, 0, 0], [0, 1, 0]), [0, 0, 1]);
  nearAll(E.vnorm([3, 0, 4]), [0.6, 0, 0.8]);
  assert.deepEqual(E.vnorm([0, 0, 0]), [0, 0, 0], 'a zero vector stays zero, not NaN');
});

test('a face normal follows the winding', () => {
  const ccw = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]];
  assert.deepEqual(E.faceNormal(ccw), [0, 0, 1]);
  assert.deepEqual(E.faceNormal(ccw.slice().reverse()), [0, 0, -1]);
});

test('a box has 8 corners and 6 faces, centred on the origin', () => {
  const b = E.mkBoxP(2, 4, 6);
  assert.equal(b.v.length, 8);
  assert.equal(b.f.length, 6);
  const xs = b.v.map((p) => p[0]), ys = b.v.map((p) => p[1]), zs = b.v.map((p) => p[2]);
  assert.deepEqual([Math.min(...xs), Math.max(...xs)], [-1, 1]);
  assert.deepEqual([Math.min(...ys), Math.max(...ys)], [-2, 2]);
  assert.deepEqual([Math.min(...zs), Math.max(...zs)], [-3, 3]);
});

test('polygon area, signed by winding', () => {
  const sq = [[0, 0], [4, 0], [4, 3], [0, 3]];
  assert.equal(E.bimPolyArea(sq), 12);
  assert.equal(E.bimPolySignedArea(sq), 12);
  assert.equal(E.bimPolySignedArea(sq.slice().reverse()), -12);
  assert.equal(E.bimPolyArea(sq.slice().reverse()), 12);
  assert.equal(E.bimPolyArea([[0, 0], [1, 1]]), 0, 'a degenerate polygon has no area');
});

test('point in polygon, an L-shaped room', () => {
  const L = [[0, 0], [6, 0], [6, 2], [2, 2], [2, 6], [0, 6]];
  assert.equal(E.bimPointInPoly([1, 1], L), true);
  assert.equal(E.bimPointInPoly([1, 5], L), true);
  assert.equal(E.bimPointInPoly([4, 4], L), false, 'the notch is outside');
  assert.equal(E.bimPointInPoly([7, 1], L), false);
});

test('rotating a point about a centre', () => {
  nearAll(E.bimRotatePoint([2, 1], [1, 1], Math.PI / 2), [1, 2]);
  nearAll(E.bimRotatePoint([2, 1], [1, 1], 2 * Math.PI), [2, 1]);
});

test('two lines meet; parallel lines do not', () => {
  nearAll(E.bimLineLineIntersect([0, 0], [2, 2], [0, 2], [2, 0]), [1, 1]);
  assert.equal(E.bimLineLineIntersect([0, 0], [1, 0], [0, 1], [1, 1]), null);
});
