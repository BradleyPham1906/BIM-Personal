// V248, the shape of the ground: curvature, ruggedness and what can be seen from a point
// (docs/work-orders/v248/SPEC.md). The pure functions of WO-01 to WO-03, in src/js/engine/terrain/terrain-shape.js.
//
//   node --test docs/work-orders/v248/v248.test.mjs
//
// V248_IMPL=<path to an .mjs exporting the functions> runs the same tests against another implementation
// (Claude checked these tests that way against a reference, 2026-11-21).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { loadEngine } from '../../../tests/unit/helpers/engine.mjs';

const F = process.env.V248_IMPL ? await import(pathToFileURL(path.resolve(process.env.V248_IMPL)).href) : loadEngine();
const near = (a, b, e, msg) => assert.ok(Math.abs(a - b) <= (e || 1e-9), (msg || '') + ' ' + a + ' vs ' + b);
// a grid as bimLandGround gives it: nx columns, nz rows, cell metres, H heights, ok flags
function grid(nx, nz, cell, f) {
  const H = new Float64Array(nx * nz), ok = new Array(nx * nz).fill(true);
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) H[j * nx + i] = f(i * cell, j * cell);
  return { nx, nz, cell, H, ok };
}

// ---- WO-01 bimCurvature ---- Zevenbergen and Thorne (1987)
test('WO-01 a valley across a slope: profile curvature -2a, plan curvature 0', () => {
  const G = grid(5, 5, 2, (x, z) => 0.05 * x * x + 0.3 * x);
  const c = F.bimCurvature(G), k = 2 * 5 + 2;
  near(c.profile[k], -0.1, 1e-9);
  near(c.plan[k], 0, 1e-9);
});
test('WO-01 a bowl seen from its side: both curvatures from D, E, F, G, H', () => {
  const G = grid(5, 5, 1, (x, z) => 0.1 * x * x + 0.05 * z * z + 0.02 * x * z + 0.4 * x - 0.2 * z);
  const c = F.bimCurvature(G), k = 2 * 5 + 2, x = 2, z = 2;
  // D = f_xx / 2, E = f_zz / 2, F = (-z1 + z3 + z7 - z9) / 4L^2 = -f_xz (rows run to +z), G = f_x, H = -f_z
  const D = 0.1, E = 0.05, Fv = -0.02, g = 0.2 * x + 0.02 * z + 0.4, h = -(0.1 * z + 0.02 * x - 0.2), q = g * g + h * h;
  near(c.profile[k], -2 * (D * g * g + E * h * h + Fv * g * h) / q, 1e-9);
  near(c.plan[k], 2 * (D * h * h + E * g * g - Fv * g * h) / q, 1e-9);
});
test('WO-01 a flat cell is 0; an edge cell or one beside missing ground is NaN', () => {
  const G = grid(4, 4, 1, () => 5);
  const c = F.bimCurvature(G);
  near(c.plan[5], 0); near(c.profile[5], 0);
  assert.ok(Number.isNaN(c.plan[0]) && Number.isNaN(c.profile[3]));
  G.ok[1] = false;
  const c2 = F.bimCurvature(G);
  assert.ok(Number.isNaN(c2.plan[5]));
  assert.ok(c2.plan instanceof Float64Array && c2.profile instanceof Float64Array);
});

// ---- WO-02 bimTri ---- Riley, DeGloria and Elliot (1999)
test('WO-02 the root of the summed squared differences to the eight neighbours', () => {
  const G = grid(3, 3, 1, () => 0); G.H[4] = 2; G.H[0] = 3;
  const t = F.bimTri(G);
  near(t[4], Math.sqrt(7 * 4 + 1), 1e-12);
  assert.ok(Number.isNaN(t[0]), 'an edge cell has no eight neighbours');
});
test('WO-02 a plane is as rugged everywhere; missing ground gives NaN', () => {
  const G = grid(5, 5, 1, (x) => 2 * x), t = F.bimTri(G);
  near(t[6], Math.sqrt(3 * 4 + 3 * 4), 1e-12); near(t[12], t[6]);
  G.ok[12] = false; const t2 = F.bimTri(G);
  assert.ok(Number.isNaN(t2[12]) && Number.isNaN(t2[6]));
  assert.ok(t2 instanceof Float64Array);
});

// ---- WO-03 bimViewshed ----
test('WO-03 flat ground: every cell within reach is seen; beyond it 255', () => {
  const G = grid(7, 7, 10, () => 0), v = F.bimViewshed(G, 3, 3, 1.6, 0, 25);
  assert.ok(v instanceof Uint8Array);
  assert.equal(v[3 * 7 + 3], 1);
  assert.equal(v[3 * 7 + 5], 1);
  assert.equal(v[3 * 7 + 6], 255, '30 m away, beyond 25 m');
  assert.equal(v[1 * 7 + 1], 255, '28.3 m away');
  assert.equal(v[2 * 7 + 2], 1);
});
test('WO-03 a wall hides what lies behind it, not what stands above its line', () => {
  const G = grid(9, 1, 1, () => 0); G.H[4] = 5;
  let v = F.bimViewshed(G, 0, 0, 1.6, 0, 100);
  assert.deepEqual(Array.from(v), [1, 1, 1, 1, 1, 0, 0, 0, 0]);
  G.H[8] = 20; v = F.bimViewshed(G, 0, 0, 1.6, 0, 100);
  assert.equal(v[8], 1, 'a tower behind the wall is seen');
  v = F.bimViewshed(G, 0, 0, 1.6, 10, 100);
  assert.deepEqual(Array.from(v).slice(5), [1, 1, 1, 1], 'targets 10 m tall are seen over it');
});
test('WO-03 missing ground: not seen there (255), and it hides nothing; no ground at the eye: all 255', () => {
  const G = grid(5, 1, 1, () => 0); G.H[2] = 50; G.ok[2] = false;
  const v = F.bimViewshed(G, 0, 0, 1.6, 0, 100);
  assert.deepEqual(Array.from(v), [1, 1, 255, 1, 1]);
  G.ok[0] = false;
  assert.deepEqual(Array.from(F.bimViewshed(G, 0, 0, 1.6, 0, 100)), [255, 255, 255, 255, 255]);
});
test('WO-03 a slope up from the eye is seen; a ridge hides the far side', () => {
  const G = grid(11, 1, 1, (x) => (x <= 5 ? x : 10 - x) * 2);
  const v = F.bimViewshed(G, 0, 0, 1.6, 0, 100);
  assert.deepEqual(Array.from(v).slice(0, 6), [1, 1, 1, 1, 1, 1]);
  assert.deepEqual(Array.from(v).slice(6), [0, 0, 0, 0, 0]);
});
