// V258 (D4): DIMBASELINE, DIMCONTINUE, DIMORDINATE and the dimension style (engine/annotation/dim-tools.js).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);
const nearPt = (p, q) => { near(p[0], q[0]); near(p[1], q[1]); };
// a horizontal dimension from (0,0) to (2,0), its line 1 m to the -z side
const ref = { p1: [0, 0], p2: [2, 0], d1: [0, -1], d2: [2, -1], length: 2 };

test('DIMBASELINE: from the first point, one spacing further out each time', () => {
  const g1 = E.bimDimBaselineGeom(ref, [5, 0.3], 1, 0.6);
  nearPt(g1.p1, [0, 0]); nearPt(g1.d1, [0, -1.6]); nearPt(g1.d2, [5, -1.6]); near(g1.length, 5);
  const g2 = E.bimDimBaselineGeom(ref, [7, 0], 2, 0.6);
  nearPt(g2.d1, [0, -2.2]); near(g2.length, 7);
});

test('DIMCONTINUE: from the last second point, on the same line', () => {
  const g = E.bimDimContinueGeom(ref, [5, 0.4]);
  nearPt(g.p1, [2, 0]); nearPt(g.d1, [2, -1]); nearPt(g.d2, [5, -1]); near(g.length, 3, 1e-12);
  const g2 = E.bimDimContinueGeom(g, [9, 0]);
  nearPt(g2.d1, [5, -1]); near(g2.length, 4);
});

test('DIMORDINATE: a leader across the plan reads Y, one up the plan reads X', () => {
  const y = E.bimDimOrdinateGeom([3, 4], [6, 4.2]);
  assert.equal(y.axis, 'y'); near(y.value, 4);
  const x = E.bimDimOrdinateGeom([3, 4], [3.1, 1]);
  assert.equal(x.axis, 'x'); near(x.value, 3);
});

test('the style is checked, and the label follows its precision and the unit', () => {
  const s = E.bimDimStyleValid({ precision: '3', arrow: 'arrow', textHeight: -1, suffix: false, bogus: 1 });
  assert.equal(s.precision, 3); assert.equal(s.arrow, 'arrow'); assert.equal(s.textHeight, 0, 'a negative height is refused');
  assert.equal(s.bogus, undefined);
  assert.equal(E.bimDimStyleValid({ arrow: 'star' }).arrow, 'tick');
  assert.equal(E.bimDimLabelText(2.5, s), '2.500');
  assert.equal(E.bimDimLabelText(2.5, E.bimDimStyleValid(null)), '2.50 m');
});
