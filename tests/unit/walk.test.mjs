// V203 Walkthrough W1: the walk's arithmetic (walk/walk-math.js, WO-01 to WO-08, moved here from the work order at C-08)
// and Walk's own pure parts (walk/walk-mode.js): the walker's body and rules from the registry, the model's triangles.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const fn = (n) => { assert.equal(typeof E[n], 'function', n + ' is not in the engine'); return E[n]; };
const near = (a, b, e = 1e-4) => assert.ok(Math.abs(a - b) <= e, a + ' is not ' + b);
const nearAll = (a, b, e = 1e-4) => { assert.equal(a.length, b.length); a.forEach((x, i) => near(x, b[i], e)); };

/* ---------------- WO-01 bimWalkStepUp(riserMm, varMm) ---------------- */
test('WO-01 bimWalkStepUp: the IRC riser (196 mm) and its variation (9.5 mm), in metres to the millimetre', () => {
  near(fn('bimWalkStepUp')(196, 9.5), 0.206, 1e-9);
});
test('WO-01 bimWalkStepUp: the IBC riser (178 mm), and a riser of 210 mm', () => {
  near(fn('bimWalkStepUp')(178, 9.5), 0.188, 1e-9);
  near(fn('bimWalkStepUp')(210, 9.5), 0.22, 1e-9);
});
test('WO-01 bimWalkStepUp: a missing or negative variation counts as 0', () => {
  near(fn('bimWalkStepUp')(178, undefined), 0.178, 1e-9);
  near(fn('bimWalkStepUp')(178, -1), 0.178, 1e-9);
});
test('WO-01 bimWalkStepUp: no riser, or not a number, is 0', () => {
  assert.equal(fn('bimWalkStepUp')(0, 9.5), 0);
  assert.equal(fn('bimWalkStepUp')(-2, 9.5), 0);
  assert.equal(fn('bimWalkStepUp')('196', 9.5), 0);
  assert.equal(fn('bimWalkStepUp')(NaN, 9.5), 0);
});

/* ---------------- WO-02 bimWalkCapsule(B, R) ---------------- */
const RULES = { stepUp: 0.206, slopeDeg: 35, chairSlope: 1 / 12 };
test('WO-02 bimWalkCapsule: a standing person', () => {
  const c = fn('bimWalkCapsule')({ top: 1.75, eye: 1.63, sh: 0.46 }, RULES);
  near(c.h, 1.75); near(c.r, 0.23); near(c.half, 0.645); near(c.eye, 1.63); near(c.step, 0.206); near(c.slope, 0.610865);
});
test('WO-02 bimWalkCapsule: a wheelchair user steps nothing and climbs 1:12', () => {
  const c = fn('bimWalkCapsule')({ top: 1.3, eye: 1.152, sh: 0.5, chair: true }, RULES);
  near(c.r, 0.25); near(c.half, 0.4); near(c.eye, 1.152); assert.equal(c.step, 0); near(c.slope, 0.083141);
});
test('WO-02 bimWalkCapsule: the radius kept between 0.2 and 0.35 m', () => {
  near(fn('bimWalkCapsule')({ top: 1.75, eye: 1.63, sh: 0.2 }, RULES).r, 0.2);
  near(fn('bimWalkCapsule')({ top: 1.75, eye: 1.63, sh: 0.9 }, RULES).r, 0.35);
});
test('WO-02 bimWalkCapsule: no height is 1.75 m, no eye is 0.12 m below the top, half at least 0.05 m', () => {
  const c = fn('bimWalkCapsule')({ sh: 0.46 }, RULES);
  near(c.h, 1.75); near(c.eye, 1.63);
  near(fn('bimWalkCapsule')({ top: 0.4, eye: 0.3, sh: 0.46 }, RULES).half, 0.05);
});

/* ---------------- WO-03 bimWalkLook(v, dx, dy, k) ---------------- */
test('WO-03 bimWalkLook: the mouse to the right turns right (yaw falls), down looks down (pitch rises)', () => {
  const v = fn('bimWalkLook')({ yaw: 0, pitch: 0 }, 100, 50, 0.002);
  near(v.yaw, -0.2); near(v.pitch, 0.1);
});
test('WO-03 bimWalkLook: yaw wraps into (-pi, pi]', () => {
  near(fn('bimWalkLook')({ yaw: 3.1, pitch: 0 }, -100, 0, 0.002).yaw, 3.3 - 2 * Math.PI);
  near(fn('bimWalkLook')({ yaw: -3.1, pitch: 0 }, 100, 0, 0.002).yaw, -3.3 + 2 * Math.PI);
});
test('WO-03 bimWalkLook: pitch kept within 1.5 rad either way', () => {
  near(fn('bimWalkLook')({ yaw: 0, pitch: 1.4 }, 0, 100, 0.002).pitch, 1.5);
  near(fn('bimWalkLook')({ yaw: 0, pitch: -1.4 }, 0, -100, 0.002).pitch, -1.5);
});
test('WO-03 bimWalkLook: does not change the object it is given', () => {
  const v = { yaw: 0, pitch: 0 }; fn('bimWalkLook')(v, 10, 10, 0.01);
  assert.deepEqual(v, { yaw: 0, pitch: 0 });
});

/* ---------------- WO-04 bimWalkMove(inp, yaw, speed, fly) ---------------- */
test('WO-04 bimWalkMove: forward at yaw 0 is -z', () => {
  nearAll(fn('bimWalkMove')({ f: 1, s: 0, run: false, up: 0 }, 0, 1.34, false), [0, 0, -1.34]);
});
test('WO-04 bimWalkMove: forward and right together are no faster than one, and running doubles', () => {
  const h = Math.SQRT1_2;
  nearAll(fn('bimWalkMove')({ f: 1, s: 1, run: false, up: 0 }, Math.PI / 2, 1, false), [-h, 0, -h]);
  nearAll(fn('bimWalkMove')({ f: 1, s: 1, run: true, up: 0 }, Math.PI / 2, 1, false), [-2 * h, 0, -2 * h]);
});
test('WO-04 bimWalkMove: a half push on the joystick walks at half speed', () => {
  nearAll(fn('bimWalkMove')({ f: 0.5, s: 0, run: false, up: 0 }, 0, 2, false), [0, 0, -1]);
});
test('WO-04 bimWalkMove: up only when flying', () => {
  nearAll(fn('bimWalkMove')({ f: 0, s: 0, run: false, up: 1 }, 0, 1.34, true), [0, 1.34, 0]);
  nearAll(fn('bimWalkMove')({ f: 0, s: 0, run: false, up: 1 }, 0, 1.34, false), [0, 0, 0]);
});

/* ---------------- WO-05 bimWalkCamFirst(p, eye, yaw, pitch) ---------------- */
const eyeOf = (c) => { const cp = Math.cos(c.pitch); const d = [cp * Math.sin(c.yaw), Math.sin(c.pitch), cp * Math.cos(c.yaw)];
  return [c.tx + d[0] * c.dist, c.ty + d[1] * c.dist, c.tz + d[2] * c.dist]; };   // camVecs's eye
test('WO-05 bimWalkCamFirst: the camera\'s eye is the walker\'s eyes', () => {
  const c = fn('bimWalkCamFirst')([2, 0, 3], 1.6, 0, 0);
  near(c.tx, 2); near(c.ty, 1.6); near(c.tz, 2); assert.equal(c.dist, 1); assert.equal(c.yaw, 0); assert.equal(c.pitch, 0);
  nearAll(eyeOf(c), [2, 1.6, 3]);
});
test('WO-05 bimWalkCamFirst: any yaw and pitch keep the eye at the eyes', () => {
  const c = fn('bimWalkCamFirst')([-5, 1.2, 7], 1.5, 0.9, -0.4);
  nearAll(eyeOf(c), [-5, 2.7, 7]); near(c.yaw, 0.9); near(c.pitch, -0.4);
});

/* ---------------- WO-06 bimWalkCamThird(p, eye, yaw, pitch, boom, hit) ---------------- */
test('WO-06 bimWalkCamThird: the focus at the eyes, the camera the boom behind', () => {
  const c = fn('bimWalkCamThird')([2, 0, 3], 1.6, 0, 0.3, 3, null);
  near(c.tx, 2); near(c.ty, 1.6); near(c.tz, 3); near(c.dist, 3); near(c.pitch, 0.3);
});
test('WO-06 bimWalkCamThird: a wall behind pulls the camera in, 0.2 m short of it, never under 0.3 m', () => {
  near(fn('bimWalkCamThird')([0, 0, 0], 1.6, 0, 0, 3, 1.5).dist, 1.3);
  near(fn('bimWalkCamThird')([0, 0, 0], 1.6, 0, 0, 3, 0.2).dist, 0.3);
  near(fn('bimWalkCamThird')([0, 0, 0], 1.6, 0, 0, 3, 10).dist, 3);
  near(fn('bimWalkCamThird')([0, 0, 0], 1.6, 0, 0, 3, Infinity).dist, 3);
});

/* ---------------- WO-07 bimWalkJoy(cx, cy, x, y, R, dead) ---------------- */
test('WO-07 bimWalkJoy: right is s, up the screen is forward', () => {
  assert.deepEqual(fn('bimWalkJoy')(100, 100, 150, 100, 50, 0.12), { s: 1, f: 0 });
  assert.deepEqual(fn('bimWalkJoy')(100, 100, 100, 75, 50, 0.12), { s: 0, f: 0.5 });
});
test('WO-07 bimWalkJoy: beyond the ring counts as the ring', () => {
  const j = fn('bimWalkJoy')(100, 100, 100, 25, 50, 0.12);
  near(j.s, 0); near(j.f, 1);
  const k = fn('bimWalkJoy')(0, 0, 100, -100, 50, 0.12);
  near(k.s, Math.SQRT1_2); near(k.f, Math.SQRT1_2);
});
test('WO-07 bimWalkJoy: inside the dead zone, or no ring, is still', () => {
  assert.deepEqual(fn('bimWalkJoy')(100, 100, 103, 100, 50, 0.12), { s: 0, f: 0 });
  assert.deepEqual(fn('bimWalkJoy')(100, 100, 150, 100, 0, 0.12), { s: 0, f: 0 });
});

/* ---------------- WO-08 bimWalkKeys(held, joy) ---------------- */
test('WO-08 bimWalkKeys: W and D, or the arrows', () => {
  assert.deepEqual(fn('bimWalkKeys')({ KeyW: true, KeyD: true }, null), { f: 1, s: 1, run: false, up: 0, ghost: false });
  assert.deepEqual(fn('bimWalkKeys')({ ArrowDown: true, ArrowLeft: true }, null), { f: -1, s: -1, run: false, up: 0, ghost: false });
});
test('WO-08 bimWalkKeys: opposite keys cancel; Shift runs, Space rises, C sinks, Alt passes through', () => {
  assert.deepEqual(fn('bimWalkKeys')({ KeyW: true, KeyS: true, ShiftRight: true, Space: true, AltLeft: true }, null),
    { f: 0, s: 0, run: true, up: 1, ghost: true });
  assert.deepEqual(fn('bimWalkKeys')({ KeyC: true }, null), { f: 0, s: 0, run: false, up: -1, ghost: false });
});
test('WO-08 bimWalkKeys: the joystick adds, kept within -1 and 1; false keys are not held', () => {
  assert.deepEqual(fn('bimWalkKeys')({ KeyW: true, KeyA: false }, { s: 0.5, f: 0.75 }), { f: 1, s: 0.5, run: false, up: 0, ghost: false });
  assert.deepEqual(fn('bimWalkKeys')({}, { s: -0.25, f: 0.5 }), { f: 0.5, s: -0.25, run: false, up: 0, ghost: false });
});
test('WO-08 bimWalkKeys: nothing held is still', () => {
  assert.deepEqual(fn('bimWalkKeys')(null, null), { f: 0, s: 0, run: false, up: 0, ghost: false });
});
test('WO-08 bimWalkKeys: running does not change the direction; the joystick still adds (audit, 2026-11-14)', () => {
  assert.deepEqual(fn('bimWalkKeys')({ KeyW: true, ShiftLeft: true }, { s: 0, f: -0.5 }), { f: 0.5, s: 0, run: true, up: 0, ghost: false });
  assert.deepEqual(fn('bimWalkKeys')({ KeyD: true, ShiftRight: true }, null), { f: 0, s: 1, run: true, up: 0, ghost: false });
});
test('WO-08 bimWalkKeys: Space and C together cancel (audit, 2026-11-14)', () => {
  assert.deepEqual(fn('bimWalkKeys')({ Space: true, KeyC: true }, null), { f: 0, s: 0, run: false, up: 0, ghost: false });
});

/* ---------------- C-05 walk-mode.js: the walker and the model ---------------- */
test('C-05 the rules: the IRC step and its variation, the walker\'s slope, running at twice the speed', () => {
  const R = E.bimWalkRules();
  near(R.stepUp, 0.206, 1e-9); assert.equal(R.slopeDeg, 35); assert.equal(R.run, 2);
  assert.ok(R.chairSlope > 0.08 && R.chairSlope < 0.084, 'a 1:12 ramp');
});
test('C-05 the walker: the mean adult between the registry\'s man and woman; the wheelchair user climbs no step', () => {
  const man = E.bimWalkBody({ who: 'man' }), wo = E.bimWalkBody({ who: 'woman' }), ad = E.bimWalkBody({ who: 'adult' });
  assert.ok(ad.top > wo.top && ad.top < man.top, 'between: ' + [wo.top, ad.top, man.top]);
  assert.ok(ad.eye < ad.top && ad.speed > 1 && ad.speed < 1.6);
  const own = E.bimWalkBody({ who: 'own', h: 1.9 });
  near(own.top, 1.9, 0.02);
  const ch = E.bimWalkBody({ who: 'chair' }), cap = E.bimWalkCapsule(ch, E.bimWalkRules());
  assert.equal(ch.chair, true); assert.equal(cap.step, 0); near(cap.slope, Math.atan(E.bimWalkRules().chairSlope), 1e-9);
  assert.ok(ch.eye < 1.3, 'seated eyes');
});
test('C-05 an element\'s triangles: each face fanned, at its place', () => {
  const o = { id: 'x', t: 'solid', pos: [10, 0, 5], mesh: { v: [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]], f: [[0, 1, 2, 3], [0, 1]] } };
  const T = E.bimWalkTris(o);
  assert.equal(T.length, 18, 'a quad is two triangles; a two-point face none');
  assert.deepEqual(Array.from(T.slice(0, 9)), [10, 0, 5, 11, 0, 5, 11, 0, 6]);
  assert.equal(E.bimWalkTris({ id: 'y', t: 'solid', pos: [0, 0, 0], mesh: { v: [], f: [] } }), null);
});
test('C-05 Jolt is asked for beside a copy on a disk first, then from the site with its SRI', () => {
  const S = E.bimWalkSources('file:', 'https://example.org/app/');
  assert.deepEqual(S.map((s) => s.u), ['runtime/jolt/1.1.1/bim-jolt.min.js', 'https://example.org/app/jolt/1.1.1/bim-jolt.min.js']);
  assert.deepEqual(S.map((s) => s.sri), [false, true]);
  assert.equal(E.bimWalkSources('https:', 'https://example.org/app/').length, 1);
});
