// V255 (D8): ID, DIST, AREA and LIST (engine/annotation/inquiry.js), their arithmetic.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);

test('DIST: distance, plan angle and deltas', () => {
  const d = E.bimInquiryDist([1, 1], [4, 5]);
  near(d.d, 5); near(d.dx, 3); near(d.dy, 4); near(d.angle, Math.atan2(4, 3) * 180 / Math.PI);
  near(E.bimInquiryDist([0, 0], [0, -2]).angle, 270, 1e-9);
});

test('AREA: points as a closed outline; a circle by its arcs', () => {
  const r = E.bimInquiryArea([[0, 0], [4, 0], [4, 3], [0, 3]]);
  near(r.area, 12); near(r.perimeter, 14);
  assert.equal(E.bimInquiryArea([[0, 0], [1, 1]]), null, 'two points have no area');
  // a unit circle as two bulge-1 arcs: pi, 2 pi (through bimBulgedArea directly, as AREA of a selected circle uses it)
  near(E.bimBulgedArea([[1, 0], [-1, 0]], [1, 1], true), Math.PI, 1e-9);
  near(E.bimBulgedLength([[1, 0], [-1, 0]], [1, 1], true), 2 * Math.PI, 1e-9);
});

test('LIST: what it says of a line, a closed polyline and a text', () => {
  const line = { id: 'a', name: 'Sketch 1', t: 'sketch', pts: [[0, 0], [3, 4]], closed: false, y: 0 };
  const rows = Object.fromEntries(E.bimListRows(line).filter((r) => Array.isArray(r)));
  assert.equal(rows.Type, 'Line');
  assert.match(rows.Length, /^5/);
  assert.match(rows['Angle in plan'], /^53\.13/);
  const rect = { id: 'b', t: 'sketch', pts: [[0, 0], [4, 0], [4, 3], [0, 3]], y: 0 };
  const rr = Object.fromEntries(E.bimListRows(rect));
  assert.equal(rr.Type, 'Polyline');
  assert.match(rr.Area, /^12/);
  assert.match(rr.Perimeter, /^14/);
  const tx = { id: 'c', t: 'text', text: 'Hall', pt: [1, 2], y: 0, height: 0.3, rot: 90 };
  const tr = Object.fromEntries(E.bimListRows(tx));
  assert.equal(tr.Text, 'Hall');
  assert.match(tr.Rotation, /^90/);
});
