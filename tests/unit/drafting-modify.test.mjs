// V250 (D2): AutoCAD's modify commands (engine/editing/drafting-modify.js), their geometry.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();

test('STRETCH moves only the points inside the crossing window', () => {
  const r = E.bimStretchPts([[0, 0], [10, 0], [10, 5], [0, 5]], [8, -1, 12, 6], [2, 0]);
  assert.deepEqual(r.pts, [[0, 0], [12, 0], [12, 5], [0, 5]]);
  assert.equal(r.moved, 2);
  assert.equal(r.all, false);
  // the window's corners may be given either way round
  assert.equal(E.bimStretchPts([[1, 1]], [2, 2, 0, 0], [1, 1]).all, true);
  assert.equal(E.bimStretchPts([[5, 5]], [0, 0, 2, 2], [1, 1]).moved, 0);
});

test('EXPLODE splits a polyline into its segments, arcs keeping their bulge', () => {
  const parts = E.bimExplodePoly([[0, 0], [4, 0], [4, 3]], [0, 0.5], false);
  assert.equal(parts.length, 2);
  assert.deepEqual(parts[0].pts, [[0, 0], [4, 0]]);
  assert.equal(parts[0].bulges, null);
  assert.deepEqual(parts[1].bulges, [0.5]);
  const closed = E.bimExplodePoly([[0, 0], [4, 0], [4, 3], [0, 3]], null, true);
  assert.equal(closed.length, 4, 'a closed rectangle gives four lines');
  assert.deepEqual(closed[3].pts, [[0, 3], [0, 0]]);
});

test('JOIN chains lines that meet end to end, reversing where needed', () => {
  const runs = E.bimJoinPolys([
    { pts: [[0, 0], [5, 0]] },
    { pts: [[5, 5], [5, 0]] },          // drawn the other way
    { pts: [[20, 20], [30, 20]] },     // apart from the rest
  ], 1e-6);
  assert.equal(runs.length, 2);
  assert.deepEqual(runs[0].pts, [[0, 0], [5, 0], [5, 5]]);
  assert.equal(runs[0].closed, false);
});

test('JOIN closes a run that comes back to its start', () => {
  const runs = E.bimJoinPolys([
    { pts: [[0, 0], [4, 0]] }, { pts: [[4, 0], [4, 3]] }, { pts: [[0, 3], [4, 3]] }, { pts: [[0, 3], [0, 0]] },
  ], 1e-6);
  assert.equal(runs.length, 1);
  assert.equal(runs[0].closed, true);
  assert.equal(runs[0].pts.length, 4);
});

test('JOIN reverses an arc by reversing and negating its bulge', () => {
  const runs = E.bimJoinPolys([{ pts: [[0, 0], [2, 0]] }, { pts: [[4, 0], [2, 0]], bulges: [0.4] }], 1e-6);
  assert.deepEqual(runs[0].pts, [[0, 0], [2, 0], [4, 0]]);
  assert.deepEqual(runs[0].bulges, [0, -0.4]);
  const r = E.bimReversePoly({ pts: [[0, 0], [1, 0], [2, 1]], bulges: [0.1, 0.3] });
  assert.deepEqual(r.pts, [[2, 1], [1, 0], [0, 0]]);
  assert.deepEqual(r.bulges, [-0.3, -0.1]);
});

test('OVERKILL drops repeated vertices and a closing vertex that repeats the first', () => {
  const r = E.bimOverkillPts([[0, 0], [0, 0], [4, 0], [4, 3], [0, 0]], null, true, 1e-6);
  assert.deepEqual(r.pts, [[0, 0], [4, 0], [4, 3]]);
  assert.equal(r.removed, 2);
  assert.equal(E.bimOverkillPts([[0, 0], [1, 0]], null, false).removed, 0);
});

test('OVERKILL sees the same line drawn either way as a duplicate', () => {
  const a = { t: 'sketch', pts: [[0, 0], [5, 0]], closed: false, y: 0 };
  const b = { t: 'sketch', pts: [[5, 0], [0, 0]], closed: false, y: 0 };
  const c = { t: 'sketch', pts: [[0, 0], [6, 0]], closed: false, y: 0 };
  assert.equal(E.bimOverkillKey(a, 1e-4), E.bimOverkillKey(b, 1e-4));
  assert.notEqual(E.bimOverkillKey(a, 1e-4), E.bimOverkillKey(c, 1e-4));
});

test('DRAWORDER moves the chosen objects to the front or the back, in their own order', () => {
  const L = ['a', 'b', 'c', 'd'].map((id) => ({ id }));
  assert.deepEqual(E.bimDrawOrder(L, ['b', 'a'], 'front').map((o) => o.id), ['c', 'd', 'a', 'b']);
  assert.deepEqual(E.bimDrawOrder(L, ['d'], 'back').map((o) => o.id), ['d', 'a', 'b', 'c']);
});

test('MATCHPROP copies only the properties the source has', () => {
  const src = { layer: 'L2', col: '#ff0000', hatch: { pat: 'ANSI31' } };
  const dst = { layer: 'L1', col: '#00ff00', lineweight: 0.5 };
  assert.equal(E.bimMatchProps(src, dst), 3);
  assert.equal(dst.layer, 'L2');
  assert.equal(dst.col, '#ff0000');
  assert.equal(dst.lineweight, 0.5, 'a property the source lacks is left alone');
  src.hatch.pat = 'X';
  assert.equal(dst.hatch.pat, 'ANSI31', 'the copy does not share the source object');
});
