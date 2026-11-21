// V240, the surface model: GEM-15's DSM and DTM, levelled to the local ground, and heights from them
// (docs/work-orders/v240/SPEC.md). The pure functions of WO-01 to WO-03, in src/js/engine/map/surface-model.js.
//
//   node --test docs/work-orders/v240/v240.test.mjs
//
// V240_IMPL=<path to an .mjs exporting the functions> runs the same tests against another implementation
// (Claude checked these tests that way against a reference, 2026-11-21).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { loadEngine } from '../../../tests/unit/helpers/engine.mjs';

const F = process.env.V240_IMPL ? await import(pathToFileURL(path.resolve(process.env.V240_IMPL)).href) : loadEngine();
const B = 'https://storage.googleapis.com/climate-and-sustainability/gem-15/';

// ---- WO-01 bimGemCell ---- (names read from GEM-15's STAC catalog, 2026-11-21)
test('WO-01 the cell and its two files at 30th Street Station', () => {
  assert.deepEqual(F.bimGemCell(-75.1822, 39.9557), {
    group: 'p30_m80', cell: 'wm76s39', dsm: B + 'p30_m80/wm76s39/dsm/zall/mosaic.tif', dtm: B + 'p30_m80/wm76s39/dtm/zall/mosaic.tif' });
});
test('WO-01 the names in every quarter of the globe', () => {
  const c = (lon, lat) => { const r = F.bimGemCell(lon, lat); return r && r.group + '/' + r.cell; };
  assert.equal(c(-9.5, 51.2), 'p50_m10/wm10s51');
  assert.equal(c(0.3, 50.5), 'p50_p0/w0s50');
  assert.equal(c(172.4, -34.2), 'm40_p170/w172sm35');
  assert.equal(c(-70.5, -0.5), 'm10_m80/wm71sm1');
  assert.equal(c(-70, 10), 'p10_m70/wm70s10', 'a whole degree starts its own cell');
});
test('WO-01 null outside 61 S to 84 N, off the globe or for bad input', () => {
  assert.equal(F.bimGemCell(0, 84), null);
  assert.equal(F.bimGemCell(0, -61.5), null);
  assert.notEqual(F.bimGemCell(0, -61), null);
  assert.equal(F.bimGemCell(180, 10), null);
  assert.equal(F.bimGemCell(NaN, 10), null);
});

// ---- WO-02 bimSurfaceOffset ----
const open = (ref, dtm) => ({ ref, dtm, dsm: dtm + 0.2, std: 0.3 });
test('WO-02 the median offset over open ground, and its spread', () => {
  const r = F.bimSurfaceOffset([open(10, 12), open(11, 13.5), open(12, 13.6), open(9, 11), open(10, 12.4)]);
  assert.deepEqual(r, { offset: -2, n: 5, mad: 0.4 });
});
test('WO-02 cells under buildings or trees, or with missing values, are left out', () => {
  const p = [open(10, 12), open(10, 12), open(10, 12), open(10, 12), open(10, 13),
    { ref: 10, dtm: 30, dsm: 46, std: 0.5 }, { ref: 10, dtm: 30, dsm: 30.5, std: 3.2 }, { ref: null, dtm: 1, dsm: 1, std: 0 }, { ref: 5, dtm: NaN, dsm: 1, std: 0 }, null];
  assert.deepEqual(F.bimSurfaceOffset(p), { offset: -2, n: 5, mad: 0 });
});
test('WO-02 null with fewer than five open cells', () => {
  assert.equal(F.bimSurfaceOffset([open(1, 2), open(1, 2), open(1, 2), open(1, 2)]), null);
  assert.equal(F.bimSurfaceOffset(null), null);
});
test('WO-02 an even count takes the mean of the middle two', () => {
  assert.equal(F.bimSurfaceOffset([open(0, 1), open(0, 2), open(0, 3), open(0, 4), open(0, 5), open(0, 6)]).offset, -3.5);
});

// ---- WO-03 bimFootprintHeight ----
test('WO-03 the median of the 95th percentiles over the footprint, above the ground', () => {
  const cells = [{ p95: 47.2 }, { p95: 46.8 }, { p95: 47.6 }, { p95: 45.1 }, { p95: 47.0 }];
  assert.deepEqual(F.bimFootprintHeight(cells, 13.2), { h: 33.8, n: 5, spread: 0.2, from: 'gem15' });
});
test('WO-03 null with under three cells, nothing standing (under 2 m), or no ground', () => {
  assert.equal(F.bimFootprintHeight([{ p95: 20 }, { p95: 20 }], 5), null);
  assert.equal(F.bimFootprintHeight([{ p95: 6 }, { p95: 6.5 }, { p95: 6.9 }], 5), null);
  assert.equal(F.bimFootprintHeight([{ p95: 20 }, { p95: 20 }, { p95: 20 }], NaN), null);
  assert.equal(F.bimFootprintHeight(null, 5), null);
});
test('WO-03 missing values are skipped; an even count takes the mean of the middle two', () => {
  const r = F.bimFootprintHeight([{ p95: 10 }, { p95: NaN }, { p95: 12 }, {}, { p95: 14 }, { p95: 16 }], 2);
  assert.deepEqual(r, { h: 11, n: 4, spread: 2, from: 'gem15' });
});
