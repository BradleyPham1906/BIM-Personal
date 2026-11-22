// V262 (D8): MASSPROP, COUNT and CAL (engine/annotation/inquiry-more.js).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);

test('MASSPROP of a 4 by 2 rectangle: bh^3/12 about its centroid, either winding', () => {
  for (const pts of [[[0, 0], [4, 0], [4, 2], [0, 2]], [[0, 2], [4, 2], [4, 0], [0, 0]]]) {
    const P = E.bimRegionProps(pts);
    near(P.area, 8); near(P.perimeter, 12); near(P.cx, 2); near(P.cy, 1);
    near(P.Ixx, 4 * 8 / 12); near(P.Iyy, 2 * 64 / 12); near(P.Ixy, 0);
    near(P.I1, 2 * 64 / 12); near(P.I2, 4 * 8 / 12);
    near(P.rx, Math.sqrt((32 / 12) / 8));
  }
});

test('MASSPROP of a right triangle: its centroid and Ixy', () => {
  const P = E.bimRegionProps([[0, 0], [3, 0], [0, 3]]);
  near(P.area, 4.5); near(P.cx, 1); near(P.cy, 1);
  near(P.Ixx, 3 * 27 / 36); near(P.Ixy, -(9 * 9) / 72);   // b^2 h^2 / 72, negative for this orientation
});

test('COUNT counts each insert once', () => {
  const objs = [{ blockRef: { name: 'CHAIR', ins: 'a' } }, { blockRef: { name: 'CHAIR', ins: 'a' } }, { blockRef: { name: 'CHAIR', ins: 'b' } },
    { blockRef: { name: 'DESK', ins: 'c' } }, { t: 'sketch' }];
  assert.deepEqual(E.bimCountBlocks(objs), { CHAIR: 2, DESK: 1 });
});

test('CAL reads expressions itself', () => {
  near(E.bimCalEval('(3.2+4.8)*2^2/sqrt(16)').value, 8);
  near(E.bimCalEval('2^3^2').value, 512, 1e-9);   // right-associative, as in mathematics
  near(E.bimCalEval('-2^2').value, -4);           // as in mathematics
  near(E.bimCalEval('2^-1').value, 0.5);
  near(E.bimCalEval('sin(30)+cos(60)').value, 1, 1e-12);
  near(E.bimCalEval('atan(1)').value, 45, 1e-12);
  near(E.bimCalEval('pi*2').value, 2 * Math.PI);
  near(E.bimCalEval('1.5e3/3').value, 500);
  assert.match(E.bimCalEval('1/0').error, /zero/);
  assert.match(E.bimCalEval('(1+2').error, /bracket/);
  assert.match(E.bimCalEval('alert(1)').error, /Unknown/);
  assert.match(E.bimCalEval('2+').error, /ends/);
});
