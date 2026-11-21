// V239, heights on one datum: a cloud-optimised GeoTIFF reader and the geoids (docs/work-orders/v239/SPEC.md).
// The pure functions of WO-01 to WO-05, in src/js/engine/map/cog-datum.js.
//
//   node --test docs/work-orders/v239/v239.test.mjs
//   node --test --test-name-pattern="WO-01" docs/work-orders/v239/v239.test.mjs
//
// V239_IMPL=<path to an .mjs exporting the functions> runs the same tests against another implementation
// (Claude checked these tests that way against a reference, 2026-11-21).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { loadEngine } from '../../../tests/unit/helpers/engine.mjs';

const F = process.env.V239_IMPL ? await import(pathToFileURL(path.resolve(process.env.V239_IMPL)).href) : loadEngine();
const near = (a, b, e, msg) => assert.ok(Math.abs(a - b) <= (e || 1e-9), (msg || '') + ' ' + a + ' vs ' + b);

// ---- a TIFF writer for the tests: one IFD, the tags given, classic or BigTIFF, either byte order ----
// tags: [[tag, type, values]] with type 2 (ASCII string), 3 (SHORT), 4 (LONG), 12 (DOUBLE), 16 (LONG8)
function tiff(tags, o = {}) {
  const le = o.le !== false, big = !!o.big, SZ = { 2: 1, 3: 2, 4: 4, 12: 8, 16: 8 };
  const esz = big ? 20 : 12, csz = big ? 8 : 2, vsz = big ? 8 : 4, hdr = big ? 16 : 8;
  tags = tags.slice().sort((a, b) => a[0] - b[0]);
  const ifdLen = csz + tags.length * esz + vsz;
  let extra = hdr + ifdLen;
  const ext = tags.map(([, type, v]) => { const n = type === 2 ? v.length + 1 : v.length, tot = SZ[type] * n; if (tot <= vsz) return null; const at = extra; extra += tot + (tot % 2); return at; });
  const pad = o.pad || 0, buf = new ArrayBuffer(extra + pad), dv = new DataView(buf), u8 = new Uint8Array(buf);
  const w64 = (at, v) => { dv.setUint32(at + (le ? 0 : 4), v % 4294967296, le); dv.setUint32(at + (le ? 4 : 0), Math.floor(v / 4294967296), le); };
  u8[0] = u8[1] = le ? 0x49 : 0x4d;
  dv.setUint16(2, big ? 43 : 42, le);
  if (big) { dv.setUint16(4, 8, le); dv.setUint16(6, 0, le); w64(8, hdr); } else dv.setUint32(4, hdr, le);
  if (big) w64(hdr, tags.length); else dv.setUint16(hdr, tags.length, le);
  tags.forEach(([tag, type, v], i) => {
    const e = hdr + csz + i * esz, n = type === 2 ? v.length + 1 : v.length;
    dv.setUint16(e, tag, le); dv.setUint16(e + 2, type, le);
    if (big) w64(e + 4, n); else dv.setUint32(e + 4, n, le);
    let at = e + (big ? 12 : 8);
    if (ext[i] !== null) { if (big) w64(at, ext[i]); else dv.setUint32(at, ext[i], le); at = ext[i]; }
    for (let k = 0; k < n; k++) {
      const p = at + k * SZ[type];
      if (type === 2) u8[p] = k < v.length ? v.charCodeAt(k) : 0;
      else if (type === 3) dv.setUint16(p, v[k], le);
      else if (type === 4) dv.setUint32(p, v[k], le);
      else if (type === 12) dv.setFloat64(p, v[k], le);
      else w64(p, v[k]);
    }
  });
  return u8;
}
// a 600 x 300 float32 raster in 256 x 256 tiles (3 across, 2 down), as GEM-15 and PROJ's grids are laid out
const BASE = (offT = 4, extraTags = []) => [
  [256, 3, [600]], [257, 3, [300]], [258, 3, [32]], [259, 3, [8]], [277, 3, [1]], [284, 3, [1]], [317, 3, [3]], [339, 3, [3]],
  [322, 3, [256]], [323, 3, [256]], [324, offT, [1000, 2000, 3000, 4000, 5000, 6000]], [325, offT, [10, 20, 30, 40, 50, 60]],
  ...extraTags,
];
const GEO = [[33550, 12, [15, 15, 0]], [33922, 12, [0, 0, 0, 481000, 4425000, 0]], [34735, 3, [1, 1, 0, 2, 1024, 0, 1, 1, 3072, 0, 1, 32618]], [42113, 2, 'nan']];

// ---- WO-01 bimTiffIfd ----
test('WO-01 a classic little-endian tiled TIFF: sizes, tiles, compression, predictor', () => {
  const r = F.bimTiffIfd(tiff(BASE()));
  assert.equal(r.big, false); assert.equal(r.le, true);
  assert.deepEqual([r.w, r.h, r.tw, r.th, r.spp, r.bps, r.fmt, r.comp, r.pred, r.planar], [600, 300, 256, 256, 1, 32, 3, 8, 3, 1]);
  assert.deepEqual(r.offsets, [1000, 2000, 3000, 4000, 5000, 6000]);
  assert.deepEqual(r.counts, [10, 20, 30, 40, 50, 60]);
  assert.equal(r.nodata, null); assert.equal(r.scale, null); assert.equal(r.tie, null); assert.equal(r.epsg, null);
});
test('WO-01 a BigTIFF with LONG8 offsets, the geo tags and GDAL nodata', () => {
  const r = F.bimTiffIfd(tiff(BASE(16, GEO), { big: true }));
  assert.equal(r.big, true);
  assert.deepEqual(r.offsets, [1000, 2000, 3000, 4000, 5000, 6000]);
  assert.deepEqual(r.scale, [15, 15]);
  assert.deepEqual(r.tie, [0, 0, 481000, 4425000]);
  assert.equal(r.epsg, 32618);
  assert.ok(Number.isNaN(r.nodata));
});
test('WO-01 big-endian, defaults for missing tags, a number nodata, a geographic EPSG', () => {
  const tags = BASE().filter((t) => ![277, 284, 317].includes(t[0])).concat([[42113, 2, '-9999'], [34735, 3, [1, 1, 0, 1, 2048, 0, 1, 6318]]]);
  const r = F.bimTiffIfd(tiff(tags, { le: false }));
  assert.equal(r.le, false);
  assert.deepEqual([r.spp, r.pred, r.planar], [1, 1, 1]);
  assert.equal(r.nodata, -9999);
  assert.equal(r.epsg, 6318);
  assert.deepEqual(r.offsets, [1000, 2000, 3000, 4000, 5000, 6000]);
});
test('WO-01 a value above 2^32 in a BigTIFF LONG8 is read whole', () => {
  const tags = BASE(16).map((t) => (t[0] === 324 ? [324, 16, [5e9, 2000, 3000, 4000, 5000, 6000]] : t));
  assert.equal(F.bimTiffIfd(tiff(tags, { big: true })).offsets[0], 5e9);
});
test('WO-01 null for: not a TIFF, no tiles, a cut-off IFD, an array past the end', () => {
  assert.equal(F.bimTiffIfd(new Uint8Array([1, 2, 3, 4, 5, 6, 7, 8])), null);
  assert.equal(F.bimTiffIfd(null), null);
  assert.equal(F.bimTiffIfd(tiff(BASE().filter((t) => t[0] !== 322 && t[0] !== 324))), null);
  const whole = tiff(BASE(16, GEO), { big: true });
  assert.equal(F.bimTiffIfd(whole.slice(0, 40)), null);
  assert.equal(F.bimTiffIfd(whole.slice(0, whole.length - 8)), null, 'the last array runs past the bytes');
});

// ---- WO-02 bimCogTiles ----
const IFD = { w: 600, h: 300, tw: 256, th: 256, offsets: [1000, 2000, 3000, 4000, 5000, 6000], counts: [10, 20, 30, 40, 50, 60] };
test('WO-02 the tiles a window touches, row by row', () => {
  assert.deepEqual(F.bimCogTiles(IFD, 0, 0, 1, 1), [{ t: 0, col: 0, row: 0, off: 1000, len: 10 }]);
  assert.deepEqual(F.bimCogTiles(IFD, 250, 250, 260, 260).map((x) => x.t), [0, 1, 3, 4]);
  assert.deepEqual(F.bimCogTiles(IFD, 0, 0, 600, 300).map((x) => [x.col, x.row]), [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1]]);
  assert.deepEqual(F.bimCogTiles(IFD, 512, 256, 513, 257)[0], { t: 5, col: 2, row: 1, off: 6000, len: 60 });
});
test('WO-02 a window is clipped to the image; an empty one gives []', () => {
  assert.deepEqual(F.bimCogTiles(IFD, -50, -50, 10, 10).map((x) => x.t), [0]);
  assert.deepEqual(F.bimCogTiles(IFD, 590, 290, 900, 900).map((x) => x.t), [5]);
  assert.deepEqual(F.bimCogTiles(IFD, 10, 10, 10, 20), []);
  assert.deepEqual(F.bimCogTiles(IFD, 700, 0, 800, 10), []);
  assert.deepEqual(F.bimCogTiles(null, 0, 0, 1, 1), []);
});

// ---- WO-03 bimTiffUnpredict ----
const le32 = (vals) => { const b = new Uint8Array(vals.length * 4), d = new DataView(b.buffer); vals.forEach((v, k) => d.setFloat32(k * 4, v, true)); return b; };
// TIFF's floating-point predictor (Technote 3): each row's samples as big-endian byte planes, then byte differences with a stride of spp
function pred3(vals, tw, th, spp) {
  const m = tw * spp, out = new Uint8Array(vals.length * 4), d = new DataView(new ArrayBuffer(4));
  for (let j = 0; j < th; j++) {
    const row = new Uint8Array(m * 4);
    for (let k = 0; k < m; k++) { d.setFloat32(0, vals[j * m + k], false); for (let b = 0; b < 4; b++) row[b * m + k] = d.getUint8(b); }
    for (let b = row.length - 1; b >= spp; b--) row[b] = (row[b] - row[b - spp]) & 255;
    out.set(row, j * m * 4);
  }
  return out;
}
test('WO-03 no predictor: little-endian float32 as it is', () => {
  const f = F.bimTiffUnpredict(le32([1.5, -2, 3.25, 1e6]), 2, 2, 1, 1);
  assert.ok(f instanceof Float32Array);
  assert.deepEqual(Array.from(f), [1.5, -2, 3.25, 1e6]);
});
test('WO-03 the floating-point predictor, one sample and five samples a pixel', () => {
  const a = [-32.979, -32.97, -33.1, -32.5, 0, 1e-3, 12.75, -0.5, 8848.86];
  assert.deepEqual(Array.from(F.bimTiffUnpredict(pred3(a, 3, 3, 1), 3, 3, 1, 3)), Array.from(new Float32Array(a)));
  const b = Array.from({ length: 2 * 2 * 5 }, (_, k) => 40 + k * 0.37 - (k % 5) * 3.1);
  assert.deepEqual(Array.from(F.bimTiffUnpredict(pred3(b, 2, 2, 5), 2, 2, 5, 3)), Array.from(new Float32Array(b)));
});
test('WO-03 null for a short buffer or another predictor', () => {
  assert.equal(F.bimTiffUnpredict(le32([1, 2, 3]), 2, 2, 1, 1), null);
  assert.equal(F.bimTiffUnpredict(le32([1, 2, 3, 4]), 2, 2, 1, 2), null);
  assert.equal(F.bimTiffUnpredict(null, 1, 1, 1, 1), null);
});

// ---- WO-04 bimGeoidAt ----
// a 3 x 2 grid of nodes: x0 230, y0 58 (the first node, north-west), 1 degree apart, rows from the north
const GRID = { w: 3, h: 2, x0: 230, y0: 58, dx: 1, dy: -1, data: new Float32Array([0, 1, 2, 10, 11, 12]) };
test('WO-04 bilinear between nodes; longitudes taken round to the grid', () => {
  near(F.bimGeoidAt(GRID, 230, 58), 0);
  near(F.bimGeoidAt(GRID, -130, 58), 0, 1e-9, '-130 is 230');
  near(F.bimGeoidAt(GRID, 230.5, 58), 0.5);
  near(F.bimGeoidAt(GRID, -129.5, 57.5), 5.5);
  near(F.bimGeoidAt(GRID, 232, 57), 12, 1e-9, 'the last node');
  near(F.bimGeoidAt(GRID, 231.25, 57.75), 3.75);
});
test('WO-04 NaN off the grid, at a NaN node or for bad input', () => {
  assert.ok(Number.isNaN(F.bimGeoidAt(GRID, 233, 58)));
  assert.ok(Number.isNaN(F.bimGeoidAt(GRID, 231, 59)));
  assert.ok(Number.isNaN(F.bimGeoidAt(GRID, 231, 56.5)));
  const g2 = { ...GRID, data: new Float32Array([0, NaN, 2, 10, 11, 12]) };
  assert.ok(Number.isNaN(F.bimGeoidAt(g2, 230.5, 57.5)));
  near(F.bimGeoidAt(g2, 231.5, 57), 11.5, 1e-9, 'the NaN node is not one of the four');
  assert.ok(Number.isNaN(F.bimGeoidAt(GRID, NaN, 58)));
  assert.ok(Number.isNaN(F.bimGeoidAt(null, 230, 58)));
});

// ---- WO-05 bimDatumShift ----
// measured at 30th Street Station, 2026-11-21: N EGM96 -34.274, EGM2008 -33.843, GEOID18 (NAVD88) -32.979
const N = { egm96: -34.274, egm2008: -33.843, navd88: -32.979 };
test('WO-05 a height moved between datums at 30th Street Station', () => {
  near(F.bimDatumShift(10, 'egm96', 'navd88', N), 8.705, 1e-9, 'an EGM96 height reads 1.295 m high against NAVD88');
  near(F.bimDatumShift(10, 'navd88', 'egm96', N), 11.295, 1e-9);
  near(F.bimDatumShift(10, 'egm2008', 'navd88', N), 9.136, 1e-9);
  near(F.bimDatumShift(10, 'navd88', 'navd88', N), 10);
  near(F.bimDatumShift(10, 'ellipsoid', 'navd88', N), 42.979, 1e-9);
  near(F.bimDatumShift(10, 'egm96', 'ellipsoid', N), -24.274, 1e-9);
});
test('WO-05 NaN for an unknown datum, a missing N or a bad height', () => {
  assert.ok(Number.isNaN(F.bimDatumShift(10, 'navd29', 'navd88', N)));
  assert.ok(Number.isNaN(F.bimDatumShift(10, 'egm96', 'navd88', { egm96: -34 })));
  assert.ok(Number.isNaN(F.bimDatumShift(NaN, 'egm96', 'navd88', N)));
  assert.ok(Number.isNaN(F.bimDatumShift(10, 'egm96', 'navd88', null)));
});
