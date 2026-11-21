// V242, water on the ground: hollows filled, the way water runs, how much gathers, where it comes from
// (docs/work-orders/v242/SPEC.md). The pure functions of WO-01 to WO-04, in src/js/engine/terrain/ground-water.js.
//
//   node --test docs/work-orders/v242/v242.test.mjs
//
// V242_IMPL=<path to an .mjs exporting the functions> runs the same tests against another implementation
// (Claude checked these tests that way against a reference, 2026-11-21).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { loadEngine } from '../../../tests/unit/helpers/engine.mjs';

const F = process.env.V242_IMPL ? await import(pathToFileURL(path.resolve(process.env.V242_IMPL)).href) : loadEngine();
const near = (a, b, e, msg) => assert.ok(Math.abs(a - b) <= (e || 1e-9), (msg || '') + ' ' + a + ' vs ' + b);
const G = (nx, nz, cell, rows) => ({ nx, nz, cell, H: Float64Array.from(rows.flat()), ok: new Array(nx * nz).fill(true) });
const DI = [1, 1, 0, -1, -1, -1, 0, 1], DJ = [0, 1, 1, 1, 0, -1, -1, -1];

// ---- WO-01 bimFill ---- Barnes, Lehman and Mulla (2014), priority-flood with epsilon
const PIT = () => G(5, 5, 1, [[9, 9, 9, 9, 9], [9, 5, 5, 5, 9], [9, 5, 1, 5, 9], [9, 5, 5, 5, 4], [9, 9, 9, 9, 9]]);
test('WO-01 a hollow fills to its spill height; nothing is lowered', () => {
  const g = PIT(), f = F.bimFill(g, 0);
  assert.ok(f instanceof Float64Array);
  for (let k = 0; k < 25; k++) assert.ok(f[k] >= g.H[k], 'never lower at ' + k);
  near(f[12], 5); near(f[6], 5); near(f[19], 4, 1e-12, 'the outlet keeps its height');
  near(f[0], 9);
});
test('WO-01 with epsilon every inner cell has a lower neighbour, so water can leave', () => {
  const g = PIT(), f = F.bimFill(g, 0.01);
  for (let j = 1; j < 4; j++) for (let i = 1; i < 4; i++) {
    let lower = false;
    for (let d = 0; d < 8; d++) if (f[(j + DJ[d]) * 5 + i + DI[d]] < f[j * 5 + i]) lower = true;
    assert.ok(lower, 'cell ' + i + ',' + j);
  }
  assert.ok(f[12] > 5 && f[12] < 5.1);
});
test('WO-01 missing ground is NaN and its neighbours are outlets', () => {
  const g = PIT(); g.ok[13] = false;
  const f = F.bimFill(g, 0);
  assert.ok(Number.isNaN(f[13]));
  near(f[12], 1, 1e-12, 'the pit drains into the missing cell beside it');
});

// ---- WO-02 bimD8 ---- O'Callaghan and Mark (1984)
test('WO-02 the steepest drop, diagonals over cell x sqrt 2', () => {
  const g = G(3, 3, 1, [[5, 5, 5], [5, 5, 3], [5, 5, 2.4]]);
  const d = F.bimD8(g);
  assert.ok(d instanceof Int8Array);
  assert.equal(d[4], 0, 'east: 2 / 1 beats south-east: 2.6 / 1.414');
  g.H[8] = 2; assert.equal(F.bimD8(g)[4], 1, 'south-east: 3 / 1.414 = 2.12 beats 2');
  g.H[8] = 2.2; assert.equal(F.bimD8(g)[4], 0, '2.8 / 1.414 = 1.98 loses to 2');
});
test('WO-02 -1 at a pit, a flat, missing ground; ties go to the lowest direction', () => {
  const g = G(3, 3, 1, [[5, 5, 5], [5, 1, 5], [5, 5, 5]]);
  const d = F.bimD8(g);
  assert.equal(d[4], -1);
  assert.equal(d[0], 1, 'the corner falls south-east into the pit');
  assert.equal(d[1], 2);
  assert.equal(F.bimD8(G(2, 1, 1, [[3, 3]]))[0], -1);
  const t = G(3, 1, 1, [[2, 5, 2]]); assert.equal(F.bimD8(t)[1], 0, 'east and west tie: east (0)');
  t.ok[2] = false; assert.equal(F.bimD8(t)[1], 4); assert.equal(F.bimD8(t)[2], -1);
});

// ---- WO-03 bimFlowAcc ----
test('WO-03 each cell counts itself and every cell that drains through it', () => {
  const g = G(4, 1, 1, [[4, 3, 2, 1]]), d = F.bimD8(g), a = F.bimFlowAcc(g, d);
  assert.ok(a instanceof Float64Array);
  assert.deepEqual(Array.from(a), [1, 2, 3, 4]);
});
test('WO-03 a V-shaped valley gathers its sides; missing ground is NaN', () => {
  const g = G(3, 3, 1, [[3, 2, 3], [2.5, 1.5, 2.5], [2, 1, 2]]), d = F.bimD8(g), a = F.bimFlowAcc(g, d);
  near(a[7], 9 - 0, 1e-12, 'everything reaches the outlet at the bottom middle');
  g.ok[0] = false; const a2 = F.bimFlowAcc(g, F.bimD8(g));
  assert.ok(Number.isNaN(a2[0])); near(a2[7], 8);
});

// ---- WO-04 bimCatchment ----
test('WO-04 the cells whose water reaches a cell, the cell included', () => {
  const g = G(3, 3, 1, [[3, 2, 3], [2.5, 1.5, 2.5], [2, 1, 2]]), d = F.bimD8(g);
  const c = F.bimCatchment(g, d, 7);
  assert.ok(c instanceof Uint8Array);
  assert.deepEqual(Array.from(c), [1, 1, 1, 1, 1, 1, 1, 1, 1]);
  const c4 = F.bimCatchment(g, d, 4);
  assert.equal(c4[4], 1); assert.equal(c4[7], 0); assert.equal(c4[6], 0);
  assert.equal(c4.reduce((s, v) => s + v, 0), F.bimFlowAcc(g, d)[4], 'a catchment is as big as the flow it gathers');
});
test('WO-04 a missing or out-of-range cell gives no catchment', () => {
  const g = G(2, 1, 1, [[2, 1]]), d = F.bimD8(g);
  assert.deepEqual(Array.from(F.bimCatchment(g, d, 5)), [0, 0]);
  g.ok[1] = false; assert.deepEqual(Array.from(F.bimCatchment(g, F.bimD8(g), 1)), [0, 0]);
});
