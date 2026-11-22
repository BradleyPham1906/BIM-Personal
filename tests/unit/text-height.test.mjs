// V254: text with a height is drawn at that height on the plan, turned by its rotation (annotation/dimensions.js).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);

test('the screen frame of a text: its height in pixels and its angle', () => {
  // a top view camera: the frame's size follows the zoom, its angle the rotation (north up, so +30 degrees turns up)
  const V = E.camVecs({ tx: 0, ty: 0, tz: 0, yaw: 0, pitch: Math.PI / 2 - 1e-6, dist: 20, fov: 0.8, ortho: true });
  const f0 = E.bimTextScreenFrame([0, 0, 0], 1, 0, V, 800, 600);
  const f1 = E.bimTextScreenFrame([0, 0, 0], 2, 0, V, 800, 600);
  assert.ok(f0.px > 1, 'a metre is some pixels');
  near(f1.px / f0.px, 2, 1e-6);
  const f30 = E.bimTextScreenFrame([0, 0, 0], 1, 30, V, 800, 600);
  near(Math.abs(f30.ang - f0.ang), Math.PI / 6, 1e-3);
});
