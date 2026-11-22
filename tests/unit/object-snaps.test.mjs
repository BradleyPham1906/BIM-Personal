// V249 (D1): running object snaps and polar tracking (engine/drawing/object-snaps.js).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);
const nearPt = (p, q, eps = 1e-9) => { near(p[0], q[0], eps); near(p[1], q[1], eps); };
const ALL = { end: true, mid: true, cen: true, qua: true, int: true, per: true, tan: true, nea: true, node: true };
const pick = (prims, c, tol, last, modes, nodes) =>
  E.bimOsnapPick(E.bimOsnapCandidates(prims, c, tol, last || null, modes || ALL, nodes || null));

test('a polyline becomes lines, and a bulge becomes an arc', () => {
  const sq = E.bimOsnapPolyPrims([[0, 0], [4, 0], [4, 3]], null, true, [1, 2]);
  assert.equal(sq.length, 3);
  assert.equal(sq[0].k, 'L');
  nearPt(sq[0].a, [1, 2]);
  const circ = E.bimOsnapPolyPrims([[1, 0], [-1, 0]], [1, 1], true, [0, 0]);
  assert.equal(circ.length, 2);
  assert.ok(circ.every((p) => p.k === 'A'));
  circ.forEach((p) => { nearPt(p.c, [0, 0], 1e-9); near(p.r, 1, 1e-9); });
});

test('endpoint and midpoint of a line', () => {
  const L = E.bimOsnapPolyPrims([[0, 0], [10, 0]], null, false);
  let w = pick(L, [0.1, 0.1], 0.5);
  assert.equal(w.kind, 'end'); nearPt(w.p, [0, 0]);
  w = pick(L, [5.1, 0.2], 0.5);
  assert.equal(w.kind, 'mid'); nearPt(w.p, [5, 0]);
});

test('nearest only wins when nothing else is in range', () => {
  const L = E.bimOsnapPolyPrims([[0, 0], [10, 0]], null, false);
  const w = pick(L, [3, 0.2], 0.5);
  assert.equal(w.kind, 'nea'); nearPt(w.p, [3, 0]);
  assert.equal(pick(L, [3, 0.2], 0.5, null, { nea: false, end: true }), null);
});

test('center and quadrant of a circle', () => {
  // started at 30 degrees, so no arc's own midpoint or end sits on a quadrant
  const s = [2 * Math.cos(Math.PI / 6), 2 * Math.sin(Math.PI / 6)];
  const C = E.bimOsnapPolyPrims([s, [-s[0], -s[1]]], [1, 1], true);
  let w = pick(C, [0.1, -0.1], 0.5);
  assert.equal(w.kind, 'cen'); nearPt(w.p, [0, 0], 1e-9);
  w = pick(C, [0.1, 2.05], 0.5);
  assert.equal(w.kind, 'qua'); nearPt(w.p, [0, 2], 1e-9);
});

test('intersection of two crossing lines, and an endpoint wins a tie at a corner', () => {
  const X = E.bimOsnapPolyPrims([[0, 0], [10, 10]], null, false)
    .concat(E.bimOsnapPolyPrims([[0, 6], [12, 0]], null, false));
  const w = pick(X, [4.1, 3.9], 0.5);
  assert.equal(w.kind, 'int'); nearPt(w.p, [4, 4], 1e-9);
  const corner = E.bimOsnapPolyPrims([[0, 0], [4, 0], [4, 4]], null, false);
  assert.equal(pick(corner, [4.05, 0.05], 0.5).kind, 'end');
});

test('line against circle, and circle against circle', () => {
  const ln = { k: 'L', a: [-5, 0], b: [5, 0] };
  const ci = { k: 'A', c: [0, 0], r: 2, a1: 0, sw: Math.PI * 2 - 1e-12 };
  const xs = E.bimOsnapIntersect(ln, ci).sort((a, b) => a[0] - b[0]);
  assert.equal(xs.length, 2); nearPt(xs[0], [-2, 0], 1e-9); nearPt(xs[1], [2, 0], 1e-9);
  const c2 = { k: 'A', c: [2, 0], r: 2, a1: 0, sw: Math.PI * 2 - 1e-12 };
  const ys = E.bimOsnapIntersect(ci, c2).sort((a, b) => a[1] - b[1]);
  assert.equal(ys.length, 2); nearPt(ys[0], [1, -Math.sqrt(3)], 1e-9); nearPt(ys[1], [1, Math.sqrt(3)], 1e-9);
  // an arc that only covers the upper half keeps only the upper crossing
  const half = { k: 'A', c: [0, 0], r: 2, a1: 0, sw: Math.PI };
  const zs = E.bimOsnapIntersect(half, c2);
  assert.equal(zs.length, 1); nearPt(zs[0], [1, Math.sqrt(3)], 1e-9);
});

test('perpendicular from the last point to a line', () => {
  const L = E.bimOsnapPolyPrims([[0, 0], [10, 0]], null, false);
  const w = pick(L, [3.2, 0.1], 0.5, [3, 5], { per: true });
  assert.equal(w.kind, 'per'); nearPt(w.p, [3, 0]);
});

test('tangent from the last point to a circle', () => {
  const C = [{ k: 'A', c: [0, 0], r: 1, a1: 0, sw: Math.PI * 2 - 1e-12 }];
  // from (2,0) the tangent points are at 60 degrees either side of the x axis
  const w = pick(C, [0.55, 0.8], 0.3, [2, 0], { tan: true });
  assert.equal(w.kind, 'tan'); nearPt(w.p, [0.5, Math.sqrt(3) / 2], 1e-9);
});

test('node: a point object', () => {
  const w = pick([], [1.05, 1], 0.2, null, { node: true }, [[1, 1]]);
  assert.equal(w.kind, 'node'); nearPt(w.p, [1, 1]);
});

test('polar tracking moves the point onto the nearest increment', () => {
  const t = E.bimPolarTrack([0, 0], [10, 0.3], 45, 3);
  near(t.angle, 0); nearPt(t.p, [10, 0], 1e-9);
  const d = E.bimPolarTrack([1, 1], [1 + 5, 1 + 5.2], 45, 3);
  near(d.angle, 45); near(d.p[0] - 1, d.p[1] - 1, 1e-9);
  assert.equal(E.bimPolarTrack([0, 0], [10, 3], 45, 3), null, '17 degrees is not near 0 or 45');
  near(E.bimPolarTrack([0, 0], [0, -4], 90, 3).angle, 270);
});

test('a circle offers its quadrants, not the ends and middles of its two halves', () => {
  const C = E.bimOsnapPolyPrims([[2, 0], [-2, 0]], [1, 1], true);
  assert.ok(C.every((P) => P.circle));
  const w = pick(C, [0.05, 2.02], 0.3);
  assert.equal(w.kind, 'qua'); nearPt(w.p, [0, 2], 1e-9);
  assert.equal(pick(C, [2.02, 0.02], 0.3).kind, 'qua');
  const open = E.bimOsnapPolyPrims([[2, 0], [-2, 0]], [1], false);
  assert.ok(!open[0].circle, 'an open arc is not a circle');
});
