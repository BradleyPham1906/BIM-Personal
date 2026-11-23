/* V276's work-order tests (docs/work-orders/v276/SPEC.md, WO-01 to WO-08): the pure functions of src/js/engine/xr/hand-model.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v276/v276.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v276/v276.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimHdFrom21', 'bimHdEuro', 'bimHdPinch', 'bimHdDepth', 'bimHdPalmFacing', 'bimHdCapsules', 'bimInTwoHand', 'bimInPointerNext'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/xr/hand-model.js'), 'utf8');
  if (process.env.V276_REF) src += fs.readFileSync(process.env.V276_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/xr/hand-model.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);
const nearArr = (a, b, e, m) => { assert.equal(a.length, b.length, m); a.forEach((v, i) => near(v, b[i], e, (m || '') + '[' + i + ']')); };

// a right hand, palm down, fingers pointing forward (-Z), thumb to the left (-X): MediaPipe's 21 points in metres
const MP = [
  [0, 0, 0],
  [-0.03, 0, -0.02], [-0.045, 0, -0.04], [-0.055, 0, -0.06], [-0.06, 0, -0.08],          // thumb CMC, MCP, IP, tip
  [-0.025, 0, -0.09], [-0.026, 0, -0.13], [-0.027, 0, -0.155], [-0.028, 0, -0.175],      // index MCP, PIP, DIP, tip
  [0, 0, -0.092], [0, 0, -0.135], [0, 0, -0.162], [0, 0, -0.184],                        // middle
  [0.02, 0, -0.088], [0.021, 0, -0.128], [0.022, 0, -0.153], [0.023, 0, -0.173],         // ring
  [0.038, 0, -0.08], [0.04, 0, -0.11], [0.041, 0, -0.128], [0.042, 0, -0.145]            // pinky
];

test('WO-01 MediaPipe\'s 21 points rebuilt as WebXR\'s 25 joints, metacarpals placed from the generic hand', () => {
  const J = fn('bimHdFrom21')(MP);
  assert.equal(J.length, 25);
  nearArr(J[0], [0, 0, 0], 1e-12, 'wrist');
  nearArr(J[1], MP[1], 1e-12, 'thumb metacarpal is MediaPipe\'s CMC');
  nearArr(J[4], MP[4], 1e-12, 'thumb tip');
  nearArr(J[5], [-0.025 * 0.37, 0, -0.09 * 0.37], 1e-12, 'index metacarpal 37 % of the way to the knuckle');
  nearArr(J[6], MP[5], 1e-12, 'index proximal is the knuckle');
  nearArr(J[9], MP[8], 1e-12, 'index tip');
  nearArr(J[10], [0, 0, -0.092 * 0.32], 1e-12, 'middle metacarpal 32 %');
  nearArr(J[15], [0.02 * 0.33, 0, -0.088 * 0.33], 1e-12, 'ring metacarpal 33 %');
  nearArr(J[20], [0.038 * 0.5, 0, -0.08 * 0.5], 1e-12, 'pinky metacarpal 50 %');
  nearArr(J[24], MP[20], 1e-12, 'pinky tip');
  J[6][0] = 99; assert.equal(MP[5][0], -0.025, 'the joints are copies');
  assert.equal(fn('bimHdFrom21')(MP.slice(0, 20)), null);
  assert.equal(fn('bimHdFrom21')(null), null);
});

test('WO-02 the One Euro filter (Casiez et al. 2012)', () => {
  const E = fn('bimHdEuro');
  let r = E(null, 1, 0, {});
  assert.equal(r.value, 1, 'the first sample passes');
  // second sample after 0.1 s, cut-off 1 Hz, beta 0: alpha = 1 / (1 + (1 / 2 pi) / 0.1)
  const a = 1 / (1 + (1 / (2 * Math.PI)) / 0.1);
  r = E(r.state, 2, 0.1, { minCutoff: 1, beta: 0, dCutoff: 1 });
  near(r.value, 1 + a, 1e-12);
  // beta raises the cut-off with speed: a fast move is followed more closely
  const slow = E(E(null, 0, 0, {}).state, 1, 0.1, { minCutoff: 1, beta: 0 }).value;
  const fast = E(E(null, 0, 0, {}).state, 1, 0.1, { minCutoff: 1, beta: 1 }).value;
  assert.ok(fast > slow, 'beta follows speed');
  const s = { x: 5, dx: 0, t: 1 }, same = E(s, 9, 1, {});
  assert.equal(same.value, 5, 'no time passed: the last value');
  assert.deepEqual(s, { x: 5, dx: 0, t: 1 }, 'the state is not changed');
});

test('WO-03 pinch with two thresholds', () => {
  const P = fn('bimHdPinch');
  assert.equal(P(false, 0.014), true, 'in below 1.5 cm');
  assert.equal(P(false, 0.02), false, 'not yet');
  assert.equal(P(true, 0.02), true, 'held until 2.5 cm');
  assert.equal(P(true, 0.026), false);
  assert.equal(P(false, 0.02, 0.03, 0.05), true, 'thresholds given');
  assert.equal(P(true, NaN), false, 'lost tracking lets go');
});

test('WO-04 depth from the hand\'s span in the image', () => {
  const D = fn('bimHdDepth');
  near(D(0.085, 100, 1000), 0.85, 1e-12);
  assert.equal(D(0.085, 0, 1000), null);
  assert.equal(D(0.085, 100, -1), null);
  assert.equal(D(0, 100, 1000), null);
});

test('WO-05 the palm facing the eye, for either hand', () => {
  const J = X.bimHdFrom21 ? X.bimHdFrom21(MP) : null;
  if (!J) assert.fail('needs WO-01');
  const F = fn('bimHdPalmFacing');
  assert.equal(F(J, 'right', [0, -0.5, -0.1]), true, 'right palm down, the eye below');
  assert.equal(F(J, 'right', [0, 0.5, -0.1]), false, 'the eye above sees the back');
  const L = J.map((p) => [-p[0], p[1], p[2]]);   // the mirror image is a left hand, still palm down
  assert.equal(F(L, 'left', [0, -0.5, -0.1]), true);
  assert.equal(F(L, 'left', [0, 0.5, -0.1]), false);
  assert.equal(F(J, 'right', [0.5, -0.2, -0.1]), false, 'at a slant beyond 60 degrees');
  assert.equal(F(J, 'right', [0.5, -0.2, -0.1], 0.3), true, 'a looser test');
});

test('WO-06 a capsule on every bone', () => {
  const J = X.bimHdFrom21 ? X.bimHdFrom21(MP) : null;
  if (!J) assert.fail('needs WO-01');
  const C = fn('bimHdCapsules')(J, null);
  assert.equal(C.length, 24);
  assert.deepEqual([C[0].from, C[0].to], [0, 1], 'wrist to thumb metacarpal first');
  assert.deepEqual([C[4].from, C[4].to], [0, 5], 'wrist to index metacarpal');
  assert.deepEqual([C[23].from, C[23].to], [23, 24], 'pinky distal to tip last');
  nearArr(C[5].a, J[5], 1e-12); nearArr(C[5].b, J[6], 1e-12);
  assert.equal(C[5].r, 0.008, 'no radii: 8 mm');
  const radii = new Array(25).fill(0.01); radii[9] = 0.006;
  assert.equal(fn('bimHdCapsules')(J, radii)[8].r, 0.006, 'a bone takes its child joint\'s radius');
  assert.deepEqual(fn('bimHdCapsules')(J.slice(0, 21), null), []);
});

test('WO-07 two hands: scale, a turn about the vertical, a move (the handle bar)', () => {
  const T = fn('bimInTwoHand');
  const r = T([-0.1, 1, -0.4], [0.1, 1, -0.4], [-0.2, 1, -0.4], [0.2, 1, -0.4]);
  near(r.s, 2); near(r.rot, 0); nearArr(r.t, [0, 0, 0], 1e-12);
  const q = T([0, 1, 0], [0.2, 1, 0], [0, 1.1, 0], [0, 1.1, 0.2]);
  near(q.s, 1, 1e-12); near(q.rot, Math.PI / 2, 1e-12); nearArr(q.t, [-0.1, 0.1, 0.1], 1e-12);
  const w = T([0, 0, 0], [-0.2, 0, 0.001], [0, 0, 0], [-0.2, 0, -0.001]);
  assert.ok(Math.abs(w.rot) < 0.02, 'across the back of the circle: the short way, not almost 2 pi');
  assert.equal(T([0, 0, 0], [0.01, 0, 0], [0, 0, 0], [0.2, 0, 0]), null, 'hands starting together give nothing');
});

test('WO-08 a pointer: press, drag past a threshold, release, click, cancel', () => {
  const N = fn('bimInPointerNext');
  let r = N(null, { type: 'down', p: [0, 0, 0] });
  assert.deepEqual(r.emit, ['press']);
  r = N(r.state, { type: 'move', p: [0.005, 0, 0] });
  assert.deepEqual(r.emit, [], 'under 1 cm: still a press');
  const t = N(r.state, { type: 'up', p: [0.005, 0, 0] });
  assert.deepEqual(t.emit, ['release', 'click']);
  r = N(r.state, { type: 'move', p: [0.02, 0, 0] });
  assert.deepEqual(r.emit, ['dragstart', 'drag']);
  r = N(r.state, { type: 'move', p: [0.03, 0, 0] });
  assert.deepEqual(r.emit, ['drag']);
  assert.deepEqual(N(r.state, { type: 'up', p: [0.03, 0, 0] }).emit, ['release', 'dragend']);
  assert.deepEqual(N(r.state, { type: 'cancel' }).emit, ['cancel']);
  assert.deepEqual(N(null, { type: 'up', p: [0, 0] }).emit, [], 'up without down');
  assert.deepEqual(N(N(null, { type: 'down', p: [0, 0] }).state, { type: 'move', p: [5, 0] }, 4).emit, ['dragstart', 'drag'], 'a threshold in pixels, 2D');
  const st = { phase: 'down', start: [0, 0, 0] }; N(st, { type: 'move', p: [1, 0, 0] });
  assert.deepEqual(st, { phase: 'down', start: [0, 0, 0] }, 'the state is not changed');
});
