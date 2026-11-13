// V201, site context C3: measured heights, ground and bridges (docs/work-orders/v201/SPEC.md).
// The pure functions of WO-01 to WO-05, in src/js/engine/map/measured-context.js. Outside `npm test`
// until WO-06 moves these into tests/unit/.
//
//   node --test docs/work-orders/v201/v201.test.mjs
//   node --test --test-name-pattern="WO-01" docs/work-orders/v201/v201.test.mjs
//
// V201_IMPL=<path to an .mjs exporting the five functions> runs the same tests against another
// implementation (Claude checked these tests that way against a reference, 2026-11-13).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { loadEngine } from '../../../tests/unit/helpers/engine.mjs';

const F = process.env.V201_IMPL ? await import(pathToFileURL(path.resolve(process.env.V201_IMPL)).href) : loadEngine();
const R = 6378137, D = Math.PI / 180;
const mx = (lon) => R * lon * D, my = (lat) => R * Math.log(Math.tan(Math.PI / 4 + lat * D / 2));
const lonOf = (x) => x / R / D, latOf = (y) => (2 * Math.atan(Math.exp(y / R)) - Math.PI / 2) / D;

// a TIFF, built here: float32 samples in strips or tiles, either byte order, tags as given
function tiff(o) {
  const le = o.le !== false, w = o.w, h = o.h, vals = o.vals, blocks = [];
  if (o.tile) {
    const [tw, th] = o.tile;
    for (let ty = 0; ty < Math.ceil(h / th); ty++) for (let tx = 0; tx < Math.ceil(w / tw); tx++) {
      const b = [];
      for (let y = 0; y < th; y++) for (let x = 0; x < tw; x++) { const X = tx * tw + x, Y = ty * th + y; b.push(X < w && Y < h ? vals[Y * w + X] : 777); }
      blocks.push(b);
    }
  } else { const r = o.rps || h; for (let y = 0; y < h; y += r) blocks.push(vals.slice(y * w, Math.min(h, y + r) * w)); }
  let off = 8; const offs = [], counts = [];
  for (const b of blocks) { offs.push(off); counts.push(b.length * 4); off += b.length * 4; }
  const E = [[256, 4, [w]], [257, 4, [h]], [258, 3, [o.bps || 32]], [259, 3, [o.comp || 1]], [262, 3, [1]], [277, 3, [o.spp || 1]]];
  if (o.tile) E.push([322, 3, [o.tile[0]]], [323, 3, [o.tile[1]]], [324, 4, offs], [325, 4, counts]);
  else E.push([273, 4, offs], [278, 4, [o.rps || h]], [279, 4, counts]);
  if (o.sf !== null) E.push([339, 3, [o.sf === undefined ? 3 : o.sf]]);
  E.sort((a, b) => a[0] - b[0]);
  let eo = off;
  for (const e of E) { const sz = e[1] === 3 ? 2 : 4; if (e[2].length * sz > 4) { e.ext = eo; eo += e[2].length * sz; } }
  const ifd = eo, buf = new ArrayBuffer(ifd + 2 + E.length * 12 + 4), dv = new DataView(buf);
  dv.setUint8(0, le ? 0x49 : 0x4d); dv.setUint8(1, le ? 0x49 : 0x4d); dv.setUint16(2, 42, le); dv.setUint32(4, ifd, le);
  blocks.forEach((b, i) => b.forEach((v, k) => dv.setFloat32(offs[i] + k * 4, v, le)));
  dv.setUint16(ifd, E.length, le);
  E.forEach((e, i) => {
    const p = ifd + 2 + i * 12, sz = e[1] === 3 ? 2 : 4, at = e.ext !== undefined ? e.ext : p + 8;
    dv.setUint16(p, e[0], le); dv.setUint16(p + 2, e[1], le); dv.setUint32(p + 4, e[2].length, le);
    if (e.ext !== undefined) dv.setUint32(p + 8, e.ext, le);
    e[2].forEach((v, k) => (sz === 2 ? dv.setUint16(at + k * 2, v, le) : dv.setUint32(at + k * 4, v, le)));
  });
  return new Uint8Array(buf);
}
const seq = (n) => Array.from({ length: n }, (_, i) => (i % 7) * 0.5 - 1.25 + Math.floor(i / 7));
const same = (r, w, h, vals) => { assert.ok(r, 'a result'); assert.equal(r.w, w); assert.equal(r.h, h); assert.ok(r.data instanceof Float32Array); assert.deepEqual(Array.from(r.data), vals.map(Math.fround)); };

// ---- WO-01 bimTiffF32
test('WO-01 reads a little-endian TIFF in one-row strips', () => {
  const v = seq(6); same(F.bimTiffF32(tiff({ w: 3, h: 2, vals: v, rps: 1 })), 3, 2, v);
});
test('WO-01 reads a big-endian TIFF in one strip', () => {
  const v = [1.5, -2]; same(F.bimTiffF32(tiff({ le: false, w: 2, h: 1, vals: v })), 2, 1, v);
});
test('WO-01 reads tiles and skips the padding of edge tiles', () => {
  const v = seq(20 * 18); same(F.bimTiffF32(tiff({ w: 20, h: 18, vals: v, tile: [16, 16] })), 20, 18, v);
  const vb = seq(5 * 3); same(F.bimTiffF32(tiff({ le: false, w: 5, h: 3, vals: vb, tile: [16, 16] })), 5, 3, vb);
});
test('WO-01 reads strips of several rows, the last one short', () => {
  const v = seq(4 * 5); same(F.bimTiffF32(tiff({ w: 4, h: 5, vals: v, rps: 2 })), 4, 5, v);
});
test('WO-01 honours the byte offset of a Uint8Array view', () => {
  const t = tiff({ w: 2, h: 2, vals: [1, 2, 3, 4] }), big = new Uint8Array(t.length + 3); big.set(t, 3);
  same(F.bimTiffF32(big.subarray(3)), 2, 2, [1, 2, 3, 4]);
});
test('WO-01 returns null for what it cannot read exactly', () => {
  const ok = { w: 2, h: 2, vals: [1, 2, 3, 4] };
  assert.equal(F.bimTiffF32(tiff({ ...ok, comp: 5 })), null, 'compressed');
  assert.equal(F.bimTiffF32(tiff({ ...ok, sf: 1 })), null, 'unsigned integers');
  assert.equal(F.bimTiffF32(tiff({ ...ok, sf: null })), null, 'no SampleFormat');
  assert.equal(F.bimTiffF32(tiff({ ...ok, bps: 16 })), null, '16 bits');
  assert.equal(F.bimTiffF32(tiff({ ...ok, spp: 2 })), null, 'two samples');
  assert.equal(F.bimTiffF32(new Uint8Array([0x50, 0x4b, 3, 4, 0, 0, 0, 0])), null, 'not a TIFF');
  assert.equal(F.bimTiffF32(new Uint8Array([0x49, 0x49, 43, 0, 8, 0, 0, 0])), null, 'wrong magic number');
  const t = tiff({ w: 2, h: 2, vals: [1, 2, 3, 4], rps: 1 }), dv = new DataView(t.buffer);
  // the strip offsets live outside the IFD entry; point the last one past the end
  const ifd = dv.getUint32(4, true), n = dv.getUint16(ifd, true);
  for (let i = 0; i < n; i++) if (dv.getUint16(ifd + 2 + i * 12, true) === 273) { const at = dv.getUint32(ifd + 2 + i * 12 + 8, true); dv.setUint32(at + 4, t.length - 4, true); }
  assert.equal(F.bimTiffF32(t), null, 'a strip past the end');
  const big = tiff({ w: 1, h: 1, vals: [1] }), bv = new DataView(big.buffer), bi = bv.getUint32(4, true), bn = bv.getUint16(bi, true);
  for (let i = 0; i < bn; i++) { const p = bi + 2 + i * 12, tg = bv.getUint16(p, true); if (tg === 256 || tg === 257) bv.setUint32(p + 8, 5000, true); }
  assert.equal(F.bimTiffF32(big), null, '5000 x 5000 is above the limit');
});

// ---- WO-02 bimDep3Url
const BASE = 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer';
test('WO-02 writes the exportImage address in Web Mercator', () => {
  const a = { w: -75.1665, s: 39.9505, e: -75.161, n: 39.9545 };
  const want = BASE + '/exportImage?bbox=' + mx(a.w).toFixed(2) + ',' + my(a.s).toFixed(2) + ',' + mx(a.e).toFixed(2) + ',' + my(a.n).toFixed(2) +
    '&bboxSR=3857&imageSR=3857&size=94,89&format=tiff&pixelType=F32&compression=None&interpolation=RSP_BilinearInterpolation&f=image';
  assert.equal(F.bimDep3Url(a, 94, 89), want);
  assert.ok(F.bimDep3Url({ w: 1, s: 1, e: 2, n: 2 }, 2, 2).indexOf('bbox=111319.49,111325.14,222638.98,222684.21&') > 0);
});
test('WO-02 returns null for a missing area or a bad size', () => {
  const a = { w: 0, s: 0, e: 1, n: 1 };
  assert.equal(F.bimDep3Url(null, 10, 10), null);
  assert.equal(F.bimDep3Url(a, 1, 10), null);
  assert.equal(F.bimDep3Url(a, 10, 2001), null);
  assert.equal(F.bimDep3Url(a, 2.5, 10), null);
});

// ---- WO-03 bimDep3ElevAt
const A = { w: -0.001, e: 0.001, s: -0.001, n: 0.001 };
const at = (fx, fy) => [lonOf(mx(A.w) + fx * (mx(A.e) - mx(A.w))), latOf(my(A.n) - fy * (my(A.n) - my(A.s)))];
test('WO-03 returns a pixel centre exactly, and the mean at the middle', () => {
  const g = { w: 2, h: 2, data: new Float32Array([1, 2, 3, 4]), a: A };
  let p = at(0.25, 0.25); assert.ok(Math.abs(F.bimDep3ElevAt(g, p[0], p[1]) - 1) < 1e-6, 'north-west centre');
  p = at(0.75, 0.75); assert.ok(Math.abs(F.bimDep3ElevAt(g, p[0], p[1]) - 4) < 1e-6, 'south-east centre');
  p = at(0.5, 0.5); assert.ok(Math.abs(F.bimDep3ElevAt(g, p[0], p[1]) - 2.5) < 1e-6, 'the middle');
  p = at(0.5, 0.25); assert.ok(Math.abs(F.bimDep3ElevAt(g, p[0], p[1]) - 1.5) < 1e-6, 'between the two north centres');
});
test('WO-03 clamps at the edges and is NaN outside', () => {
  const g = { w: 2, h: 2, data: new Float32Array([1, 2, 3, 4]), a: A };
  let p = at(0.01, 0.01); assert.ok(Math.abs(F.bimDep3ElevAt(g, p[0], p[1]) - 1) < 1e-6, 'the outer half pixel');
  assert.ok(Number.isNaN(F.bimDep3ElevAt(g, 0.002, 0)), 'east of the grid');
  assert.ok(Number.isNaN(F.bimDep3ElevAt(g, 0, -0.002)), 'south of the grid');
});
test('WO-03 is NaN on nodata', () => {
  const g = { w: 2, h: 2, data: new Float32Array([1, 2, 3, -3.4e38]), a: A };
  let p = at(0.5, 0.5); assert.ok(Number.isNaN(F.bimDep3ElevAt(g, p[0], p[1])));
  p = at(0.25, 0.25); assert.ok(Math.abs(F.bimDep3ElevAt(g, p[0], p[1]) - 1) < 1e-6, 'a pixel centre does not use the nodata cell');
});

// ---- WO-04 bimCityHeightPick
const sq = (x0, z0, x1, z1) => [[x0, z0], [x1, z0], [x1, z1], [x0, z1]];
const REC = { id: 'phl-li-footprints', roof: 'approx_hgt', top: 'max_hgt', base: 'base_elevation', unit: 0.3048 };
const CITY = [
  { ring: sq(-50, -50, 50, 50), a: { approx_hgt: 170, max_hgt: 558.2, base_elevation: 34.5 } },
  { ring: sq(-10, -10, 10, 10), a: { approx_hgt: 100, max_hgt: null, base_elevation: null } }
];
test('WO-04 takes the city ring holding the footprint, in metres', () => {
  assert.deepEqual(F.bimCityHeightPick(sq(30, 30, 40, 40), CITY, REC), { h: 51.82, top: 170.14, base: 10.52, from: 'city', id: 'phl-li-footprints' });
});
test('WO-04 prefers the smallest ring when several hold the centre', () => {
  assert.deepEqual(F.bimCityHeightPick(sq(-5, -5, 5, 5), CITY, REC), { h: 30.48, top: null, base: null, from: 'city', id: 'phl-li-footprints' });
});
test('WO-04 returns null outside, or with no roof height', () => {
  assert.equal(F.bimCityHeightPick(sq(60, 60, 70, 70), CITY, REC), null);
  assert.equal(F.bimCityHeightPick(sq(30, 30, 40, 40), [{ ring: sq(-50, -50, 50, 50), a: { approx_hgt: 0 } }], REC), null);
  assert.equal(F.bimCityHeightPick(sq(30, 30, 40, 40), [{ ring: sq(-50, -50, 50, 50), a: {} }], REC), null);
  assert.equal(F.bimCityHeightPick(sq(30, 30, 40, 40), [], REC), null);
});
test('WO-04 drops a top that is not above the roof', () => {
  const r = F.bimCityHeightPick(sq(30, 30, 40, 40), [{ ring: sq(-50, -50, 50, 50), a: { approx_hgt: 100, max_hgt: 90, base_elevation: 0 } }], REC);
  assert.deepEqual(r, { h: 30.48, top: null, base: 0, from: 'city', id: 'phl-li-footprints' });
});

// ---- WO-05 bimNbiPick
const NB = (p, o) => ({ p, a: Object.assign({ STRUCTURE_NUMBER_008: '000000000039109 ', FACILITY_CARRIED_007: '17th Street', YEAR_BUILT_027: 1898,
  DECK_WIDTH_MT_052: 15.1, STRUCTURE_LEN_MT_049: 25, MAIN_UNIT_SPANS_045: 1, VERT_CLR_UND_054B: 6.43, VERT_CLR_UND_REF_054A: 'R' }, o || {}) });
const LINE = [[0, 0], [100, 0]];
test('WO-05 picks the structure within reach of the line, as its NBI record', () => {
  assert.deepEqual(F.bimNbiPick(LINE, [NB([150, 0]), NB([40, 12])], 0),
    { id: '000000000039109', carried: '17th Street', year: 1898, width: 15.1, length: 25, spans: 1, clear: 6.43, clearRef: 'R', dist: 12 });
});
test('WO-05 measures to the segments, beyond their ends too', () => {
  assert.equal(F.bimNbiPick(LINE, [NB([-10, 0])], 30).dist, 10);
  assert.equal(F.bimNbiPick([[0, 0], [50, 0], [50, 50]], [NB([60, 25])], 30).dist, 10);
});
test('WO-05 keeps only measured numbers', () => {
  const r = F.bimNbiPick(LINE, [NB([40, 1], { VERT_CLR_UND_054B: 99.99, DECK_WIDTH_MT_052: 0, MAIN_UNIT_SPANS_045: null, FACILITY_CARRIED_007: undefined })], 30);
  assert.equal(r.clear, null); assert.equal(r.width, null); assert.equal(r.spans, null); assert.equal(r.carried, null); assert.equal(r.length, 25);
});
test('WO-05 honours maxD, keeps the first on a tie, and is null when nothing is near', () => {
  assert.equal(F.bimNbiPick(LINE, [NB([40, 12])], 5), null);
  assert.equal(F.bimNbiPick(LINE, [NB([40, 31])], 0), null, 'the default reach is 30 m');
  assert.equal(F.bimNbiPick(LINE, [NB([20, 3], { YEAR_BUILT_027: 1900 }), NB([80, -3], { YEAR_BUILT_027: 2000 })], 30).year, 1900);
  assert.equal(F.bimNbiPick(LINE, [], 30), null);
});
