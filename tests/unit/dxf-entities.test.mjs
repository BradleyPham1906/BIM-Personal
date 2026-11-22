// V251 (D7): DXF fidelity on import (engine/io/dxf-entities.js and import-dxf.js's parser).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);
const nearPt = (p, q, eps = 1e-9) => { near(p[0], q[0], eps); near(p[1], q[1], eps); };
// a DXF file from [code, value] pairs
const dxf = (pairs) => pairs.map(([c, v]) => `${c}\n${v}`).join('\n') + '\n0\nEOF\n';

test('MTEXT formatting codes are stripped, paragraphs kept', () => {
  assert.equal(E.dxfTextPlain('{\\fArial|b1;Room}\\PArea 12 m\\S2^;'), 'Room\nArea 12 m2/');
  assert.equal(E.dxfTextPlain('\\H2.5;\\C1;Note\\~one'), 'Note one');
  assert.equal(E.dxfTextPlain('%%c100 %%d45 %%p5'), 'Ø100 °45 ±5');
});

test('an ELLIPSE is sampled on its own axes', () => {
  const e = E.dxfEllipsePts([1, 1], [2, 0], 0.5, 0, Math.PI * 2, 4);
  assert.equal(e.closed, true);
  assert.equal(e.pts.length, 4);
  nearPt(e.pts[0], [3, 1]); nearPt(e.pts[1], [1, 2]); nearPt(e.pts[2], [-1, 1]);
  // turned 90 degrees: the major axis points north
  const r = E.dxfEllipsePts([0, 0], [0, 2], 0.5, 0, Math.PI / 2, 2);
  assert.equal(r.closed, false);
  nearPt(r.pts[0], [0, 2]); nearPt(r.pts[2], [-1, 0]);
});

test('a SPLINE: a clamped quadratic passes through its ends and its known midpoint', () => {
  const pts = E.dxfSplinePts(2, [[0, 0], [1, 2], [2, 0]], [0, 0, 0, 1, 1, 1], null, null, 4);
  nearPt(pts[0], [0, 0]); nearPt(pts[4], [2, 0]);
  nearPt(pts[2], [1, 1], 1e-12);   // Bezier at t = 1/2: (0 + 2*1 + 0)/4 * 2 = 1
  // no usable knots: the fit points
  assert.deepEqual(E.dxfSplinePts(3, [[0, 0]], [], null, [[0, 0], [5, 5]]), [[0, 0], [5, 5]]);
});

test('an INSERT moves, scales and turns its block about the base point', () => {
  const line = { type: 'LINE', layer: '0', color: null, p1: [1, 1, 0], p2: [2, 1, 0] };
  const o = E.dxfXform(line, { at: [10, 0], sx: 2, sy: 2, rot: 90, layer: 'WALLS' }, [1, 1]);
  nearPt(o.p1, [10, 0]); nearPt(o.p2, [10, 2]);
  assert.equal(o.layer, 'WALLS', 'layer 0 in a block takes the insert\'s layer');
  const arc = { type: 'ARC', c: [0, 0], r: 1, a1: 0, a2: 90 };
  const m = E.dxfXform(arc, { at: [0, 0], sx: -1, sy: 1, rot: 0 }, [0, 0]);
  near(m.a1, 90); near(m.a2, 180);   // mirrored in x: the quarter moves to the second quadrant
  near(E.dxfXform(arc, { at: [0, 0], sx: 3, sy: 3, rot: 30 }, [0, 0]).r, 3);
});

test('nested blocks expand, and a block that inserts itself stops', () => {
  const blocks = {
    A: { base: [0, 0], ents: [{ type: 'LINE', p1: [0, 0, 0], p2: [1, 0, 0] }] },
    B: { base: [0, 0], ents: [{ type: 'INSERT', name: 'A', at: [5, 0], sx: 1, sy: 1, rot: 0 }] },
    LOOP: { base: [0, 0], ents: [{ type: 'INSERT', name: 'LOOP', at: [1, 0], sx: 1, sy: 1, rot: 0 }] },
  };
  const out = E.dxfExpandInserts([{ type: 'INSERT', name: 'B', at: [0, 10], sx: 1, sy: 1, rot: 0 }], blocks, 0);
  assert.equal(out.length, 1);
  nearPt(out[0].p1, [5, 10]); nearPt(out[0].p2, [6, 10]);
  assert.equal(E.dxfExpandInserts([{ type: 'INSERT', name: 'LOOP', at: [0, 0] }], blocks, 0).length, 0);
  const arr = E.dxfExpandInserts([{ type: 'INSERT', name: 'A', at: [0, 0], sx: 1, sy: 1, rot: 0, cols: 3, colSp: 2 }], blocks, 0);
  assert.deepEqual(arr.map((e) => e.p1[0]), [0, 2, 4], 'a column array repeats the block');
});

test('the parser reads blocks, inserts, text, ellipses, splines, solids and dimensions', () => {
  const text = dxf([
    [0, 'SECTION'], [2, 'HEADER'], [9, '$INSUNITS'], [70, 6], [0, 'ENDSEC'],
    [0, 'SECTION'], [2, 'BLOCKS'],
    [0, 'BLOCK'], [8, '0'], [2, 'DOOR'], [10, 0], [20, 0],
    [0, 'LINE'], [8, '0'], [10, 0], [20, 0], [11, 0.9], [21, 0],
    [0, 'ARC'], [8, '0'], [10, 0], [20, 0], [40, 0.9], [50, 0], [51, 90],
    [0, 'ENDBLK'],
    [0, 'BLOCK'], [8, '0'], [2, '*D1'], [10, 0], [20, 0],
    [0, 'LINE'], [8, '0'], [10, 0], [20, -1], [11, 5], [21, -1],
    [0, 'MTEXT'], [8, '0'], [10, 2.5], [20, -0.8], [40, 0.25], [1, '5000'],
    [0, 'ENDBLK'],
    [0, 'ENDSEC'],
    [0, 'SECTION'], [2, 'ENTITIES'],
    [0, 'INSERT'], [8, 'DOORS'], [2, 'DOOR'], [10, 10], [20, 0], [50, 90],
    [0, 'TEXT'], [8, 'NOTES'], [10, 1], [20, 2], [40, 0.3], [1, 'Kitchen'],
    [0, 'ELLIPSE'], [8, '0'], [10, 0], [20, 0], [11, 2], [21, 0], [40, 0.5], [41, 0], [42, 6.283185307179586],
    [0, 'SPLINE'], [8, '0'], [70, 8], [71, 2], [40, 0], [40, 0], [40, 0], [40, 1], [40, 1], [40, 1],
    [10, 0], [20, 0], [10, 1], [20, 2], [10, 2], [20, 0],
    [0, 'SOLID'], [8, '0'], [10, 0], [20, 0], [11, 1], [21, 0], [12, 0], [22, 1], [13, 1], [23, 1],
    [0, 'DIMENSION'], [8, 'DIMS'], [2, '*D1'], [70, 32],
    [0, 'ENDSEC'],
  ]);
  const r = E.dxfParse(text);
  assert.equal(r.blocks, 2);
  assert.equal(r.inserts, 2, 'the INSERT and the DIMENSION');
  const types = r.entities.map((e) => e.type).sort();
  assert.deepEqual(types, ['ARC', 'LINE', 'LINE', 'POLYPTS', 'POLYPTS', 'POLYPTS', 'TEXT', 'TEXT'].sort());
  const door = r.entities.find((e) => e.type === 'LINE' && e.layer === 'DOORS');
  nearPt(door.p1, [10, 0]); nearPt(door.p2, [10, 0.9]);   // turned 90 degrees at (10, 0)
  const arc = r.entities.find((e) => e.type === 'ARC');
  near(arc.a1, 90); near(arc.a2, 180);
  const t = r.entities.filter((e) => e.type === 'TEXT').map((e) => e.text).sort();
  assert.deepEqual(t, ['5000', 'Kitchen']);
  const solid = r.entities.find((e) => e.type === 'POLYPTS' && e.pts.length === 4 && e.closed && e.pts[2][0] === 1);
  assert.deepEqual(solid.pts, [[0, 0], [1, 0], [1, 1], [0, 1]], 'SOLID corners 3 and 4 are uncrossed');
  assert.equal(r.skipped.DIMENSION, undefined);
});
