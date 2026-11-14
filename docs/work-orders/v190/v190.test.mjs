/* V190's work-order tests (docs/work-orders/v190/SPEC.md, WO-01 to WO-11): the pure functions of
   src/js/engine/map/pointcloud.js, LOD-C's first slice: local LAS and PLY files read, sampled to a point budget and
   rebased in double precision; class names, height colours and ground points by cell.

   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v190/v190.test.mjs
     node --test --test-name-pattern="WO-02" docs/work-orders/v190/v190.test.mjs
   The LAS and PLY files are built here byte by byte from the specifications (ASPRS LAS 1.2 and 1.4, PLY), so the
   expected values do not come from the code under test. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimPcSniff', 'bimPcLasHeader', 'bimPcStep', 'bimPcLasPoints', 'bimPcOrigin', 'bimPcPlyHeader', 'bimPcPlyRead',
  'bimPcPlyPoints', 'bimPcClassName', 'bimPcHeightColour', 'bimPcGround'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/map/pointcloud.js'), 'utf8');
  if (process.env.V190_REF) src += fs.readFileSync(process.env.V190_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const P = load();
const fn = (n) => { assert.equal(typeof P[n], 'function', n + ' is not built yet in src/js/engine/map/pointcloud.js'); return P[n]; };
const near = (a, b, e) => assert.ok(Math.abs(a - b) < (e || 1e-9), a + ' is not ' + b);

// a LAS file: header (227 bytes for 1.2, 375 for 1.4), no VLRs, then the points
// pts: [{x, y, z (metres), cls, rgb: [r, g, b] 16-bit}]
function las({ minor = 2, format = 2, pts, scale = [0.01, 0.01, 0.01], offset = [500000, 4400000, 0], legacyCount = true, cut = 0 }) {
  const hs = minor >= 4 ? 375 : 227, rl = { 0: 20, 2: 26, 3: 34, 6: 30, 7: 36 }[format];
  const buf = new ArrayBuffer(hs + rl * pts.length), dv = new DataView(buf);
  'LASF'.split('').forEach((c, i) => dv.setUint8(i, c.charCodeAt(0)));
  dv.setUint8(24, 1); dv.setUint8(25, minor); dv.setUint16(94, hs, true); dv.setUint32(96, hs, true);
  dv.setUint8(104, format); dv.setUint16(105, rl, true); dv.setUint32(107, legacyCount ? pts.length : 0, true);
  for (let j = 0; j < 3; j++) { dv.setFloat64(131 + 8 * j, scale[j], true); dv.setFloat64(155 + 8 * j, offset[j], true); }
  const ax = ['x', 'y', 'z'];
  for (let j = 0; j < 3; j++) {
    dv.setFloat64(179 + 16 * j, Math.max(...pts.map((p) => p[ax[j]])), true);
    dv.setFloat64(187 + 16 * j, Math.min(...pts.map((p) => p[ax[j]])), true);
  }
  if (minor >= 4) { dv.setUint32(247, pts.length, true); dv.setUint32(251, 0, true); }
  pts.forEach((p, i) => {
    const at = hs + i * rl;
    for (let j = 0; j < 3; j++) dv.setInt32(at + 4 * j, Math.round((p[ax[j]] - offset[j]) / scale[j]), true);
    if (format >= 6) dv.setUint8(at + 16, p.cls); else dv.setUint8(at + 15, p.cls | 0x20); // 0x20: a synthetic flag above the 5 class bits
    const rgbAt = { 2: 20, 3: 28, 7: 30 }[format];
    if (rgbAt) p.rgb.forEach((v, j) => dv.setUint16(at + rgbAt + 2 * j, v, true));
  });
  return new DataView(cut ? buf.slice(0, buf.byteLength - cut) : buf);
}
const PTS = [
  { x: 500010.25, y: 4400020.5, z: 12.34, cls: 2, rgb: [65535, 0, 256] },
  { x: 500010.26, y: 4400020.51, z: 12.35, cls: 2, rgb: [0, 32768, 512] },
  { x: 500012.0, y: 4400021.0, z: 20.0, cls: 6, rgb: [1024, 1024, 1024] },
  { x: 500013.5, y: 4400022.25, z: 15.5, cls: 5, rgb: [0, 0, 0] }
];
const bytesOf = (dv) => new Uint8Array(dv.buffer, dv.byteOffset, dv.byteLength);

test('WO-01 the format from the first bytes, not the name', () => {
  const f = fn('bimPcSniff');
  assert.equal(f(bytesOf(las({ pts: PTS }))), 'las');
  const z = bytesOf(las({ pts: PTS })).slice(); z[104] |= 0x80;
  assert.equal(f(z), 'laz');
  assert.equal(f(new TextEncoder().encode('ply\nformat ascii 1.0\n')), 'ply');
  assert.equal(f(new TextEncoder().encode('plyx')), '');
  assert.equal(f(new Uint8Array([1, 2])), '');
  assert.equal(f(null), '');
});

test('WO-02 a LAS 1.2 header: version, format, count, scale, offset, bounds', () => {
  const h = fn('bimPcLasHeader')(las({ pts: PTS }));
  assert.deepEqual([h.versionMajor, h.versionMinor, h.headerSize, h.offsetToPoints, h.pointFormat, h.recordLength, h.count], [1, 2, 227, 227, 2, 26, 4]);
  assert.deepEqual(h.scale, [0.01, 0.01, 0.01]);
  assert.deepEqual(h.offset, [500000, 4400000, 0]);
  assert.deepEqual(h.min, [500010.25, 4400020.5, 12.34]);
  assert.deepEqual(h.max, [500013.5, 4400022.25, 20]);
});
test('WO-02 LAS 1.4: the 64-bit count when the legacy count is 0', () => {
  const h = fn('bimPcLasHeader')(las({ minor: 4, format: 6, pts: PTS, legacyCount: false }));
  assert.equal(h.count, 4);
  assert.equal(h.pointFormat, 6);
});
test('WO-02 the errors: short, unsupported format, short record, truncated', () => {
  const f = fn('bimPcLasHeader');
  assert.deepEqual(f(new DataView(new ArrayBuffer(100))), { error: 'too short' });
  const d4 = las({ pts: PTS }); d4.setUint8(104, 4);
  assert.deepEqual(f(d4), { error: 'point format 4 not supported' });
  const dr = las({ pts: PTS }); dr.setUint16(105, 19, true);
  assert.deepEqual(f(dr), { error: 'record too short' });
  assert.deepEqual(f(las({ pts: PTS, cut: 1 })), { error: 'truncated' });
});

test('WO-03 the step that keeps a count within a budget', () => {
  const f = fn('bimPcStep');
  assert.deepEqual([f(10, 100), f(10, 10), f(11, 10), f(1000000, 250000), f(10, 0), f(10, null)], [1, 1, 2, 4, 1, 1]);
});

test('WO-04 the points: rebased before float32, classes masked to 5 bits, colours to 8 bits', () => {
  const dv = las({ pts: PTS }), h = P.bimPcLasHeader ? P.bimPcLasHeader(dv) : null;
  const c = fn('bimPcLasPoints')(dv, h, 1000, [500010, 4400020, 12]);
  assert.equal(c.n, 4);
  assert.ok(c.xyz instanceof Float32Array);
  near(c.xyz[0], 0.25, 1e-6); near(c.xyz[1], 0.5, 1e-6); near(c.xyz[2], 0.34, 1e-6);
  near(c.xyz[3] - c.xyz[0], 0.01, 1e-6, 'a centimetre survives');
  assert.deepEqual(Array.from(c.cls), [2, 2, 6, 5]);
  assert.deepEqual(Array.from(c.rgb.slice(0, 6)), [255, 0, 1, 0, 128, 2]);
});
test('WO-04 a budget samples every k-th point; format 0 has no colour; format 6 reads its class byte', () => {
  const h0 = P.bimPcLasHeader(las({ format: 0, pts: PTS }));
  const c0 = fn('bimPcLasPoints')(las({ format: 0, pts: PTS }), h0, 2, [0, 0, 0]);
  assert.equal(c0.n, 2);
  assert.equal(c0.rgb, null);
  assert.deepEqual(Array.from(c0.cls), [2, 6]);
  const d6 = las({ minor: 4, format: 6, pts: PTS });
  assert.deepEqual(Array.from(fn('bimPcLasPoints')(d6, P.bimPcLasHeader(d6), 10, null).cls), [2, 2, 6, 5]);
});

test('WO-05 the origin: the centre of x and y and the bottom z, floored to whole metres', () => {
  assert.deepEqual(fn('bimPcOrigin')({ min: [500010.25, 4400020.5, 12.34], max: [500013.5, 4400022.25, 20] }), [500011, 4400021, 12]);
  assert.deepEqual(fn('bimPcOrigin')({ min: [-10.5, -3, -2.5], max: [-1, 3, 0] }), [-6, 0, -3]);
});

const PLY_A = 'ply\nformat ascii 1.0\ncomment made by hand\nelement vertex 3\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nelement face 0\nproperty list uchar int vertex_indices\nend_header\n1 2 3 255 0 0\n4 5 6 0 255 0\n7 8 9 0 0 255\n';
test('WO-06 a PLY header: the format, the vertex count and properties, where the data starts', () => {
  const h = fn('bimPcPlyHeader')(PLY_A);
  assert.equal(h.format, 'ascii');
  assert.equal(h.count, 3);
  assert.deepEqual(h.props.map((p) => p.name + ':' + p.type), ['x:float', 'y:float', 'z:float', 'red:uchar', 'green:uchar', 'blue:uchar']);
  assert.equal(PLY_A.slice(h.headerBytes, h.headerBytes + 5), '1 2 3');
  assert.equal(fn('bimPcPlyHeader')(PLY_A.replace(/\n/g, '\r\n')).headerBytes, PLY_A.replace(/\n/g, '\r\n').indexOf('1 2 3'));
});
test('WO-06 the errors', () => {
  const f = fn('bimPcPlyHeader');
  assert.deepEqual(f('obj'), { error: 'not a PLY header' });
  assert.deepEqual(f('ply\nformat binary_big_endian 1.0\nelement vertex 1\nproperty float x\nend_header\n'), { error: 'format binary_big_endian not supported' });
  assert.deepEqual(f('ply\nformat ascii 1.0\nend_header\n'), { error: 'no vertex element' });
  assert.deepEqual(f('ply\nformat ascii 1.0\nelement vertex 1\nproperty list uchar int x\nend_header\n'), { error: 'a list property on vertices' });
  assert.deepEqual(f(5), { error: 'not text' });
});

test('WO-07 a binary PLY value of each type, little-endian', () => {
  const dv = new DataView(new ArrayBuffer(16)), f = fn('bimPcPlyRead');
  dv.setInt8(0, -5); assert.equal(f(dv, 0, 'char'), -5);
  dv.setUint8(0, 250); assert.equal(f(dv, 0, 'uint8'), 250);
  dv.setInt16(0, -300, true); assert.equal(f(dv, 0, 'short'), -300);
  dv.setUint16(0, 60000, true); assert.equal(f(dv, 0, 'ushort'), 60000);
  dv.setInt32(0, -70000, true); assert.equal(f(dv, 0, 'int32'), -70000);
  dv.setUint32(0, 4000000000, true); assert.equal(f(dv, 0, 'uint'), 4000000000);
  dv.setFloat32(0, 1.5, true); assert.equal(f(dv, 0, 'float'), 1.5);
  dv.setFloat64(0, 500000.125, true); assert.equal(f(dv, 0, 'double'), 500000.125);
});

test('WO-08 ASCII PLY points with colour, rebased', () => {
  const b = new TextEncoder().encode(PLY_A), h = P.bimPcPlyHeader(PLY_A);
  const c = fn('bimPcPlyPoints')(b, h, 10, [1, 1, 1]);
  assert.equal(c.n, 3);
  assert.deepEqual(Array.from(c.xyz), [0, 1, 2, 3, 4, 5, 6, 7, 8]);
  assert.deepEqual(Array.from(c.rgb), [255, 0, 0, 0, 255, 0, 0, 0, 255]);
  assert.equal(c.cls, null);
});
test('WO-08 binary PLY with doubles and no colour, sampled; missing x, y, z; truncated', () => {
  const head = 'ply\nformat binary_little_endian 1.0\nelement vertex 4\nproperty double x\nproperty double y\nproperty double z\nproperty float intensity\nend_header\n';
  const hb = new TextEncoder().encode(head), buf = new Uint8Array(hb.length + 4 * 28), dv = new DataView(buf.buffer);
  buf.set(hb);
  for (let i = 0; i < 4; i++) { dv.setFloat64(hb.length + i * 28, 500000 + i, true); dv.setFloat64(hb.length + i * 28 + 8, 10 * i, true); dv.setFloat64(hb.length + i * 28 + 16, 0.001 * i, true); dv.setFloat32(hb.length + i * 28 + 24, 1, true); }
  const h = P.bimPcPlyHeader(head);
  const c = fn('bimPcPlyPoints')(buf, h, 2, [500000, 0, 0]);
  assert.equal(c.n, 2);
  assert.equal(c.rgb, null);
  near(c.xyz[3], 2, 1e-6); near(c.xyz[4], 20, 1e-6); near(c.xyz[5], 0.002, 1e-6);
  assert.deepEqual(fn('bimPcPlyPoints')(buf.slice(0, buf.length - 1), h, 10, null), { error: 'truncated' });
  const noz = P.bimPcPlyHeader('ply\nformat ascii 1.0\nelement vertex 1\nproperty float x\nproperty float y\nend_header\n');
  assert.deepEqual(fn('bimPcPlyPoints')(new Uint8Array(0), noz, 10, null), { error: 'no x, y, z' });
});

test('WO-09 ASPRS class names, and a number for the rest', () => {
  const f = fn('bimPcClassName');
  assert.deepEqual([2, 6, 9, 17, 18, 8, 64].map(f), ['Ground', 'Building', 'Water', 'Bridge deck', 'High noise', 'Class 8', 'Class 64']);
});

test('WO-10 the height ramp: blue-green low, red high, clamped; a flat cloud mid', () => {
  const f = fn('bimPcHeightColour');
  assert.deepEqual(f(0, 0, 10), [0, 255, 128]);
  assert.deepEqual(f(10, 0, 10), [255, 0, 0]);
  assert.deepEqual(f(5, 0, 10), [255, 255, 64]);
  assert.deepEqual(f(-3, 0, 10), [0, 255, 128]);
  assert.deepEqual(f(4, 4, 4), [255, 255, 64]);
});

test('WO-11 ground points thinned to the lowest in each cell; other classes left out', () => {
  const cloud = { n: 5, xyz: new Float32Array([0.2, 0.2, 5, 0.8, 0.9, 4, 1.5, 0.5, 6, 0.5, 0.5, 1, 3, 3, 9]), cls: new Uint8Array([2, 2, 2, 6, 1]) };
  assert.deepEqual(fn('bimPcGround')(cloud, 1).map((p) => p.map((v) => Math.round(v * 10) / 10)), [[0.8, 0.9, 4], [1.5, 0.5, 6]]);
  assert.equal(fn('bimPcGround')(cloud, 5).length, 1);
  assert.deepEqual(fn('bimPcGround')({ n: 1, xyz: new Float32Array(3), cls: null }, 1), []);
});
