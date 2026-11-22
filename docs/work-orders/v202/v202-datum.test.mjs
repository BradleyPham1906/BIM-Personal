// V202 part C, heights on one datum (docs/work-orders/v202/SPEC.md, part C).
// The pure functions of WO-22 and WO-23, in src/js/engine/map/cog-datum.js.
//
//   node --test docs/work-orders/v202/v202-datum.test.mjs
//   node --test --test-name-pattern="WO-22" docs/work-orders/v202/v202-datum.test.mjs
//
// V202C_IMPL=<path to an .mjs exporting the functions> runs the same tests against another implementation
// (Claude checked these tests that way against a reference, 2026-11-21).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { loadEngine } from '../../../tests/unit/helpers/engine.mjs';

const F = process.env.V202C_IMPL ? await import(pathToFileURL(path.resolve(process.env.V202C_IMPL)).href) : loadEngine();
const near = (a, b, e, msg) => assert.ok(Math.abs(a - b) <= (e || 1e-9), (msg || '') + ' ' + a + ' vs ' + b);

// ---- WO-22 bimGeoidAt ----
// a 3 x 2 grid of nodes: x0 230, y0 58 (the first node, north-west), 1 degree apart, rows from the north
const GRID = { w: 3, h: 2, x0: 230, y0: 58, dx: 1, dy: -1, data: new Float32Array([0, 1, 2, 10, 11, 12]) };
test('WO-22 bilinear between nodes; longitudes taken round to the grid', () => {
  near(F.bimGeoidAt(GRID, 230, 58), 0);
  near(F.bimGeoidAt(GRID, -130, 58), 0, 1e-9, '-130 is 230');
  near(F.bimGeoidAt(GRID, 230.5, 58), 0.5);
  near(F.bimGeoidAt(GRID, -129.5, 57.5), 5.5);
  near(F.bimGeoidAt(GRID, 232, 57), 12, 1e-9, 'the last node');
  near(F.bimGeoidAt(GRID, 231.25, 57.75), 3.75);
});
test('WO-22 NaN off the grid, at a NaN node or for bad input', () => {
  assert.ok(Number.isNaN(F.bimGeoidAt(GRID, 233, 58)));
  assert.ok(Number.isNaN(F.bimGeoidAt(GRID, 231, 59)));
  assert.ok(Number.isNaN(F.bimGeoidAt(GRID, 231, 56.5)));
  const g2 = { ...GRID, data: new Float32Array([0, NaN, 2, 10, 11, 12]) };
  assert.ok(Number.isNaN(F.bimGeoidAt(g2, 230.5, 57.5)));
  near(F.bimGeoidAt(g2, 231.5, 57), 11.5, 1e-9, 'the NaN node is not one of the four');
  assert.ok(Number.isNaN(F.bimGeoidAt(GRID, NaN, 58)));
  assert.ok(Number.isNaN(F.bimGeoidAt(null, 230, 58)));
});

// ---- WO-23 bimDatumShift ----
// measured at 30th Street Station, 2026-11-21: N EGM96 -34.274, EGM2008 -33.843, GEOID18 (NAVD88) -32.979
const N = { egm96: -34.274, egm2008: -33.843, navd88: -32.979 };
test('WO-23 a height moved between datums at 30th Street Station', () => {
  near(F.bimDatumShift(10, 'egm96', 'navd88', N), 8.705, 1e-9, 'an EGM96 height reads 1.295 m high against NAVD88');
  near(F.bimDatumShift(10, 'navd88', 'egm96', N), 11.295, 1e-9);
  near(F.bimDatumShift(10, 'egm2008', 'navd88', N), 9.136, 1e-9);
  near(F.bimDatumShift(10, 'navd88', 'navd88', N), 10);
  near(F.bimDatumShift(10, 'ellipsoid', 'navd88', N), 42.979, 1e-9);
  near(F.bimDatumShift(10, 'egm96', 'ellipsoid', N), -24.274, 1e-9);
});
test('WO-23 NaN for an unknown datum, a missing N or a bad height', () => {
  assert.ok(Number.isNaN(F.bimDatumShift(10, 'navd29', 'navd88', N)));
  assert.ok(Number.isNaN(F.bimDatumShift(10, 'egm96', 'navd88', { egm96: -34 })));
  assert.ok(Number.isNaN(F.bimDatumShift(NaN, 'egm96', 'navd88', N)));
  assert.ok(Number.isNaN(F.bimDatumShift(10, 'egm96', 'navd88', null)));
});
