/* V274's work-order tests (docs/work-orders/v274/SPEC.md, WO-01 to WO-09): the pure functions of src/js/engine/render/headset.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v274/v274.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v274/v274.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimHsUrlBytes', 'bimHsProfileDecode', 'bimHsDistort', 'bimHsLayout', 'bimHsEyeTan', 'bimHsHeadQuat',
  'bimHsYaw', 'bimHsRecentre', 'bimHsSupport'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/render/headset.js'), 'utf8');
  if (process.env.V274_REF) src += fs.readFileSync(process.env.V274_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/render/headset.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);
const nearArr = (a, b, e, m) => { assert.equal(a.length, b.length, m); a.forEach((v, i) => near(v, b[i], e, (m || '') + '[' + i + ']')); };

// Google Cardboard v1's profile, as the Cardboard SDK ships it (sdk/qrcode/cardboard_v1/cardboard_v1.cc, Apache-2.0)
const V1 = [0x0a, 0x0c, 0x47, 0x6f, 0x6f, 0x67, 0x6c, 0x65, 0x2c, 0x20, 0x49, 0x6e, 0x63, 0x2e, 0x12, 0x0c, 0x43, 0x61, 0x72,
  0x64, 0x62, 0x6f, 0x61, 0x72, 0x64, 0x20, 0x76, 0x31, 0x1d, 0x31, 0x08, 0x2c, 0x3d, 0x25, 0x8f, 0xc2, 0x75, 0x3d, 0x2a, 0x10,
  0x00, 0x00, 0x20, 0x42, 0x00, 0x00, 0x20, 0x42, 0x00, 0x00, 0x20, 0x42, 0x00, 0x00, 0x20, 0x42, 0x35, 0x29, 0x5c, 0x0f, 0x3d,
  0x3a, 0x08, 0xc1, 0xca, 0xe1, 0x3e, 0x77, 0xbe, 0x1f, 0x3e, 0x58, 0x00, 0x60, 0x01];
const V1_URL = 'https://google.com/cardboard/cfg?p=CgxHb29nbGUsIEluYy4SDENhcmRib2FyZCB2MR0xCCw9JY_CdT0qEAAAIEIAACBCAAAgQgAAIEI1KVwPPToIwcrhPne-Hz5YAGAB';
const V2 = { vendor: '', model: '', sl: 0.039, il: 0.064, fov: [60, 60, 60, 60], valign: 'bottom', tl: 0.035, k: [0.34, 0.55], button: 'magnet' };
const IPHONE13 = { w: 2532, h: 1170, ppi: 460 };
const f32 = (v) => { const b = new Uint8Array(4); new DataView(b.buffer).setFloat32(0, v, true); return Array.from(b); };

test('WO-01 the bytes of a viewer QR link: URL-safe base64, padding added; no p parameter gives null', () => {
  const b = fn('bimHsUrlBytes')(V1_URL);
  assert.ok(b instanceof Uint8Array, 'a Uint8Array');
  assert.deepEqual(Array.from(b), V1, 'the - and _ characters are read as + and /');
  assert.deepEqual(Array.from(fn('bimHsUrlBytes')('https://x.example/cfg?a=1&p=WAE&b=2')), [0x58, 0x01], 'p among other parameters, padding added');
  assert.equal(fn('bimHsUrlBytes')('https://google.com/cardboard/cfg?q=abc'), null);
  assert.equal(fn('bimHsUrlBytes')('https://google.com/cardboard/cfg?p='), null);
  assert.equal(fn('bimHsUrlBytes')(''), null);
});

test('WO-02 Cardboard v1 decoded field by field', () => {
  assert.deepEqual(fn('bimHsProfileDecode')(new Uint8Array(V1)), { vendor: 'Google, Inc.', model: 'Cardboard v1', sl: 0.042, il: 0.06,
    fov: [40, 40, 40, 40], valign: 'bottom', tl: 0.035, k: [0.441, 0.156], button: 'magnet' });
});
test('WO-02 fields left out keep Cardboard v2; enums, unpacked repeats and unknown fields', () => {
  const D = fn('bimHsProfileDecode');
  assert.deepEqual(D(new Uint8Array([0x58, 0x02])), Object.assign({}, V2, { valign: 'top' }), 'only the alignment given');
  assert.deepEqual(D(new Uint8Array([0x60, 0x00, 0x58, 0x01])), Object.assign({}, V2, { button: 'none', valign: 'center' }));
  // k as two unpacked float32 fields (wire type 5), and an unknown varint field 9 skipped
  const bytes = [0x3d].concat(f32(0.25), [0x3d], f32(0.5), [0x48, 0x96, 0x01]);
  assert.deepEqual(D(new Uint8Array(bytes)).k, [0.25, 0.5], 'unpacked repeated floats');
  // three fov values are not four: the default stays
  assert.deepEqual(D(new Uint8Array([0x2a, 0x0c].concat(f32(30), f32(30), f32(30)))).fov, [60, 60, 60, 60]);
  assert.equal(D(new Uint8Array([0x58, 0x07])).valign, 'bottom', 'an unknown enum value keeps the default');
});
test('WO-02 broken bytes refused with one message', () => {
  const D = fn('bimHsProfileDecode'), E = { error: 'the viewer settings could not be read' };
  assert.deepEqual(D(new Uint8Array(0)), E);
  assert.deepEqual(D(null), E);
  assert.deepEqual(D(new Uint8Array([0x0a, 0x10, 0x41])), E, 'a string running past the end');
  assert.deepEqual(D(new Uint8Array([0x1d, 0x00, 0x00])), E, 'a float cut short');
  assert.deepEqual(D(new Uint8Array([0x0b])), E, 'wire type 3');
});

test('WO-03 the lens polynomial', () => {
  near(fn('bimHsDistort')([0.34, 0.55], 0.5), 0.5596875, 1e-12);
  near(fn('bimHsDistort')([0.441, 0.156], -0.3), -0.3 * (1 + 0.441 * 0.09 + 0.156 * 0.0081), 1e-12, 'odd in t');
  near(fn('bimHsDistort')([0.1, 0.2, 0.3], 1), 1.6, 1e-12, 'a third coefficient used');
  near(fn('bimHsDistort')([], 0.7), 0.7, 1e-12);
});

test('WO-04 lenses placed on an iPhone 13 for each alignment', () => {
  const L = fn('bimHsLayout')(V2, IPHONE13), mpp = 0.0254 / 460;
  near(L.mpp, mpp, 1e-15);
  nearArr(L.lensL, [1266 - 0.032 / mpp, 0.031 / mpp], 1e-9);
  nearArr(L.lensR, [1266 + 0.032 / mpp, 0.031 / mpp], 1e-9);
  near(fn('bimHsLayout')(Object.assign({}, V2, { valign: 'center' }), IPHONE13).lensL[1], 585, 1e-9);
  near(fn('bimHsLayout')(Object.assign({}, V2, { valign: 'top' }), IPHONE13).lensR[1], 1170 - 0.031 / mpp, 1e-9);
  near(fn('bimHsLayout')(V2, Object.assign({ bezel: 0 }, IPHONE13)).lensL[1], 0.035 / mpp, 1e-9, 'a bezel of 0 is not the default');
});

test('WO-05 each eye limited by the lens and by its half of the screen', () => {
  const L = X.bimHsLayout ? X.bimHsLayout(V2, IPHONE13) : { mpp: 0.0254 / 460, lensL: [686.4724409448818, 561.4173228346458], lensR: [1845.5275590551182, 561.4173228346458] };
  const l = fn('bimHsEyeTan')(V2, IPHONE13, L, 'left'), r = fn('bimHsEyeTan')(V2, IPHONE13, L, 'right');
  near(l.left, Math.tan(Math.PI / 3), 1e-7, 'outer: the lens limits');
  near(l.right, 1.2128752, 1e-7, 'inner: the screen middle, through the lens polynomial');
  near(l.bottom, 1.1401467, 1e-7); near(l.top, 1.3403824, 1e-7);
  near(r.left, l.right, 1e-12, 'mirrored'); near(r.right, l.left, 1e-12); near(r.bottom, l.bottom, 1e-12);
  const P = Object.assign({}, V2, { fov: [50, 20, 45, 45] }), a = fn('bimHsEyeTan')(P, IPHONE13, L, 'left'), b = fn('bimHsEyeTan')(P, IPHONE13, L, 'right');
  near(a.left, Math.tan(50 * Math.PI / 180), 1e-9, 'fov[0] is the outer side'); near(a.right, Math.tan(20 * Math.PI / 180), 1e-9);
  near(b.right, Math.tan(50 * Math.PI / 180), 1e-9, 'the right eye\'s outer side is its right'); near(b.left, Math.tan(20 * Math.PI / 180), 1e-9);
});

test('WO-06 the head from the motion sensors', () => {
  const H = fn('bimHsHeadQuat'), h = Math.SQRT1_2;
  nearArr(H(0, 0, 0, 0), [-h, 0, 0, h], 1e-12, 'flat face up: looking down');
  nearArr(H(0, 90, 0, 0), [0, 0, 0, 1], 1e-12, 'upright in portrait: looking ahead');
  nearArr(H(0, 90, 0, 90), [0, 0, -h, h], 1e-12, 'landscape: the screen angle turns it about Z');
  const q = H(30, 90, 0, 0);
  nearArr(q, [0, Math.sin(Math.PI / 12), 0, Math.cos(Math.PI / 12)], 1e-12, 'alpha 30: a turn of 30 degrees about the vertical');
  const g = H(10, 80, 20, 0), n = Math.hypot(g[0], g[1], g[2], g[3]);
  near(n, 1, 1e-12, 'a unit quaternion');
  nearArr(H(10, 80, 20, undefined), g, 1e-12, 'a missing screen angle is 0');
  assert.equal(H(null, 90, 0, 0), null);
  assert.equal(H(0, undefined, 0, 0), null);
});

test('WO-07 the heading of the view', () => {
  const H = X.bimHsHeadQuat || ((a) => [0, Math.sin(a * Math.PI / 360), 0, Math.cos(a * Math.PI / 360)]);
  near(fn('bimHsYaw')(H(30, 90, 0, 0)), Math.PI / 6, 1e-12);
  near(fn('bimHsYaw')(H(-100, 90, 0, 0)), -100 * Math.PI / 180, 1e-12, 'negative headings keep their sign');
  near(fn('bimHsYaw')([0, 0, 0, 1]), 0, 1e-12);
  near(fn('bimHsYaw')([-Math.SQRT1_2, 0, 0, Math.SQRT1_2]), 0, 1e-12, 'looking straight down: 0');
});

test('WO-08 re-centring sets the heading to 0 and keeps the pitch', () => {
  const H = X.bimHsHeadQuat, Y = X.bimHsYaw;
  const q = H ? H(40, 70, 5, 90) : [0.1, 0.3, -0.2, 0.927];
  const yaw = Y ? Y(q) : 0.6, c = fn('bimHsRecentre')(q, yaw);
  near(Math.hypot(c[0], c[1], c[2], c[3]), Math.hypot(q[0], q[1], q[2], q[3]), 1e-12, 'still unit length');
  if (Y) near(Y(c), 0, 1e-12, 'the heading is 0');
  // the forward vector's height (the pitch) does not change: fy = 2 (w x - y z) is the same in both
  const fy = (r) => 2 * (r[3] * r[0] - r[1] * r[2]);
  near(fy(c), fy(q), 1e-12, 'the pitch is kept');
  nearArr(fn('bimHsRecentre')([0, Math.sin(0.25), 0, Math.cos(0.25)], 0.5), [0, 0, 0, 1], 1e-12, 'a pure turn of 0.5 rad undone');
});

test('WO-09 what the device supports, with the notes in order', () => {
  const S = fn('bimHsSupport');
  assert.deepEqual(S({ secure: true, webgl2: true, motion: true, standalone: true }), { ok: true, notes: [] });
  assert.deepEqual(S({ secure: true, webgl2: true, motion: false, standalone: false }), { ok: true, notes: [
    'This device has no motion sensors the page can read; drag to look around.',
    'Add the app to your Home Screen for a full-screen headset view.'] });
  assert.deepEqual(S({ secure: false, webgl2: false, motion: true, standalone: true }), { ok: false, notes: [
    'Open the app over https to use the headset.', 'This browser cannot draw the headset view (no WebGL 2).'] });
});
