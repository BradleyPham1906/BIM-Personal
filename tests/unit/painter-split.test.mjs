// V200: the 2D view's faces cut small before they are sorted (render/painter-split.js), so a big floor no
// longer paints over what stands on it when the model is drawn without WebGL or WebGPU.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const len = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const area = (t) => { const [a, b, c] = t; const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
  return Math.hypot(u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]) / 2; };
const square = (s) => [[0, 0, 0], [s, 0, 0], [s, 0, s], [0, 0, s]];

test('a small triangle stays one piece with its whole outline', () => {
  const p = E.bimPaintPieces([[0, 0, 0], [0.05, 0, 0], [0, 0, 0.05]], { left: 100 });
  assert.equal(p.length, 1);
  assert.deepEqual(p[0].e, [true, true, true]);
});

test('a big face is cut into pieces no longer than the step, covering it exactly', () => {
  const p = E.bimPaintPieces(square(4), { left: 1e6 }, 0.5);
  assert.ok(p.length > 32, `only ${p.length} pieces`);
  let a = 0, outline = 0;
  for (const t of p) {
    for (let j = 0; j < 3; j++) {
      assert.ok(len(t.w[j], t.w[(j + 1) % 3]) <= 0.5 + 1e-9);
      if (t.e[j]) outline += len(t.w[j], t.w[(j + 1) % 3]);
    }
    a += area(t.w);
  }
  assert.ok(Math.abs(a - 16) < 1e-9, `area ${a}`);
  assert.ok(Math.abs(outline - 16) < 1e-9, `the outline stroked is ${outline} long, not the square's 16 (no cut is stroked)`);
});

test('a concave face is cut by its ears, covering only itself, its outline kept', () => {
  const L = [[0, 0, 0], [4, 0, 0], [4, 0, 1], [1, 0, 1], [1, 0, 4], [0, 0, 4]];   // an L, 7 square metres
  const p = E.bimPaintPieces(L, { left: 1e6 }, 100);
  assert.equal(p.length, 4);
  let a = 0, outline = 0;
  for (const t of p) { a += area(t.w); for (let j = 0; j < 3; j++) if (t.e[j]) outline += len(t.w[j], t.w[(j + 1) % 3]); }
  assert.ok(Math.abs(a - 7) < 1e-9, `the pieces cover ${a}, not the L's 7: a fan would spill outside it`);
  assert.ok(Math.abs(outline - 16) < 1e-9, `the outline stroked is ${outline} long, not the L's 16`);
});

test('past the frame budget a face is only fanned', () => {
  const b = { left: 0 };
  assert.equal(E.bimPaintPieces(square(40), b).length, 2);
  assert.equal(E.bimPaintPieces([[0, 0, 0], [40, 0, 0], [0, 0, 40]], b).length, 1);
});

test('with the screen given, a side is cut only while it is long on the screen', () => {
  // a 30 m floor seen from far (half a px a metre): too small on screen to cut; seen close (100 px a metre): cut
  const far = (p) => [p[0] / 2, p[2] / 2, 100], near = (p) => [p[0] * 100, p[2] * 100, 10];
  const pf = E.bimPaintPieces(square(30), { left: 1e6 }, 0, far), pn = E.bimPaintPieces(square(30), { left: 1e6 }, 0, near);
  assert.equal(pf.length, 2);
  assert.ok(pn.length > 500, `only ${pn.length} pieces close up`);
  for (const t of pn) assert.equal(t.s.length, 3, 'each piece carries its screen points');
});

test('the floor where a sofa stands sorts behind the sofa, though the whole floor sorted in front of it', () => {
  // the eye high over the near edge of a 30 m floor, looking at a sofa near the far side
  const eye = [15, 12, -6], d = [0, -0.45, 0.89];   // the view direction (toward the scene)
  const depth = (p) => (p[0] - eye[0]) * d[0] + (p[1] - eye[1]) * d[1] + (p[2] - eye[2]) * d[2];
  const floor = square(30);
  const sofaFront = [[14, 0, 25], [16, 0, 25], [16, 0.85, 25], [14, 0.85, 25]];
  const avg = (w) => w.reduce((s, p) => s + depth(p), 0) / w.length;
  assert.ok(avg(floor) < avg(sofaFront), 'the old sort: the whole floor nearer than the sofa, so painted over it');
  const under = E.bimPaintPieces(floor, { left: 1e6 }, 0.5).find((t) => {
    const c = [(t.w[0][0] + t.w[1][0] + t.w[2][0]) / 3, 0, (t.w[0][2] + t.w[1][2] + t.w[2][2]) / 3];
    return Math.abs(c[0] - 15) < 0.4 && Math.abs(c[2] - 25.3) < 0.4;
  });
  assert.ok(under, 'a piece of floor under the sofa');
  assert.ok(avg(under.w) > avg(sofaFront), 'the new sort: the floor under the sofa is farther, so painted first');
});
