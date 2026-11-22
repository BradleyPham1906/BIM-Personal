// V265: the end of the CADCraft list: hatch holes, DONUT, WIPEOUT, polyline widths, CIRCLE TTR
// (engine/drawing/hatch-more.js, draw-extra.js; import-dxf.js for widths).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);

test('DONUT: a ring is a circle with a circular hole; a dot has none', () => {
  const r = E.bimDonutRings([2, 3], 1, 3);
  assert.equal(r.holes.length, 1);
  const o = { pts: r.pts, bulges: r.bulges, holes: r.holes };
  near(E.bimBulgedArea(r.pts, r.bulges, true), Math.PI * 1.5 * 1.5, 1e-9);
  near(E.bimHatchHoleArea(o), Math.PI * 0.25, 1e-9);
  near(E.bimHatchArea(Object.assign({ t: 'hatch' }, o)), Math.PI * (2.25 - 0.25), 1e-9);
  assert.equal(E.bimDonutRings([0, 0], 0, 2).holes.length, 0);
  assert.equal(E.bimDonutRings([0, 0], 0, 0), null);
});

test('an island is found inside its outer boundary', () => {
  const ring = [[0, 0], [10, 0], [10, 10], [0, 10]];
  assert.equal(E.bimPointInRing([5, 5], ring), true);
  assert.equal(E.bimPointInRing([15, 5], ring), false);
});

test('a DXF LWPOLYLINE keeps its constant width (43)', () => {
  const r = E.dxfParse('0\nSECTION\n2\nENTITIES\n0\nLWPOLYLINE\n8\n0\n90\n2\n70\n0\n43\n0.25\n10\n0\n20\n0\n10\n5\n20\n0\n0\nENDSEC\n0\nEOF\n');
  near(r.entities[0].width, 0.25);
});

test('CIRCLE TTR: tangent to two lines, in the corner the picks were made in', () => {
  // the x axis and the z axis; picks in the +x, +z corner
  const c = E.bimCircleTTR([[0, 0], [10, 0]], [[0, 0], [0, 10]], [5, 0], [0, 5], 1);
  near(c.center[0], 1); near(c.center[1], 1); near(c.radius, 1);
  // picks on the other side of the z axis: the -x, +z corner
  const d = E.bimCircleTTR([[-10, 0], [10, 0]], [[0, 0], [0, 10]], [-5, 0], [0, 5], 2);
  near(d.center[0], -2); near(d.center[1], 2);
  // two lines at 90 degrees not through the origin, the circle touches both
  const l1 = [[0, 2], [10, 2]], l2 = [[7, -5], [7, 10]];
  const e = E.bimCircleTTR(l1, l2, [3, 2], [7, 8], 1.5);
  near(Math.abs(e.center[1] - 2), 1.5); near(Math.abs(e.center[0] - 7), 1.5);
  assert.ok(e.center[1] > 2 && e.center[0] < 7, 'on the picks\' sides');
  assert.equal(E.bimCircleTTR([[0, 0], [1, 0]], [[0, 1], [1, 1]], [0.5, 0], [0.5, 1], 0.5), null, 'parallel lines');
});

test('BCLOSE finds each insert of the block once, with its point and its attribute values', () => {
  const objs = [
    { id: 'a', blockRef: { name: 'TAG', id: 'blk1', ins: 'i1', at: [5, 0], level: 'L0' } },
    { id: 'b', t: 'text', text: 'D7', attrib: { tag: 'MARK' }, blockRef: { name: 'TAG', id: 'blk1', ins: 'i1', at: [5, 0] } },
    { id: 'c', blockRef: { name: 'TAG', id: 'blk1', ins: 'i2', at: [10, 0] } },
    { id: 'd', blockRef: { name: 'OTHER', id: 'blk2', ins: 'i3', at: [0, 0] } },
    { id: 'e', blockRef: { name: 'TAG', ins: 'i4' } },   // an insert from before V265: no point, left alone
  ];
  const I = E.bimBlockInserts(objs, 'blk1', 'TAG');
  assert.equal(I.length, 2);
  assert.deepEqual(I[0].ids, ['a', 'b']); assert.deepEqual(I[0].at, [5, 0]); assert.deepEqual(I[0].values, { MARK: 'D7' });
  assert.deepEqual(I[1].ids, ['c']);
});

test('XREF lists each attached drawing once, with its object count', () => {
  const L = E.bimXrefList([{ xref: { id: 'x1', name: 'site.dxf' } }, { xref: { id: 'x1', name: 'site.dxf' } }, { t: 'sketch' }, { xref: { id: 'x2', name: 'base.dwg' } }]);
  assert.deepEqual(L, [{ id: 'x1', name: 'site.dxf', count: 2 }, { id: 'x2', name: 'base.dwg', count: 1 }]);
});

test('a DXF pattern family reaches every tile once: its period and offset are a basis of the tile lattice', () => {
  for (const name of ['diagonal', 'cross', 'brick', 'concrete', 'steel', 'dots', 'horizontal', 'vertical']) {
    const def = E.bimPatternDef(name), T = E.dxfPatternTile(def, 1), W = T[0], H = T[1];
    for (const f of E.dxfPatternLines(def, W, H, 0)) {
      const a = f.angle * Math.PI / 180, d = [Math.cos(a), Math.sin(a)];
      const per = f.dashes.length ? f.dashes.reduce((s, x) => s + Math.abs(x), 0) : null;
      // the parallelogram of the period (along d) and the offset has the tile's area
      if (per !== null) near(Math.abs(per * d[0] * f.offset[1] - per * d[1] * f.offset[0]), W * H, 1e-9);
      else assert.ok(Math.abs(d[0] * f.offset[1] - d[1] * f.offset[0]) > 0, name + ': a continuous line still steps to the next one');
    }
  }
  assert.equal(E.dxfHatchPattern('ANSI31R'), 'diagonal-reverse');
  assert.deepEqual(E.dxfPatternTile(E.bimPatternDef('diagonal'), 2), [0.5, 0.5]);
});
