// V202b, site context geometry (map/surroundings-3d.js): roads and railways follow the ground between
// OpenStreetMap's points, and a bridge deck meets the ground at its abutments and stays level over a valley.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();

test('bimCtxDense puts a point at least every step metres and keeps the ends', () => {
  const d = E.bimCtxDense([[0, 0], [20, 0], [20, 3]], 5);
  assert.deepEqual(d[0], [0, 0]);
  assert.deepEqual(d[d.length - 1], [20, 3]);
  for (let i = 1; i < d.length; i++) {
    const l = Math.hypot(d[i][0] - d[i - 1][0], d[i][1] - d[i - 1][1]);
    assert.ok(l <= 5 + 1e-9 && l > 0, 'segment ' + i + ' is ' + l);
  }
  assert.equal(d.length, 6);
});

const line = (n, step) => Array.from({ length: n }, (_, i) => [i * step, 0]);

test('a bridge over flat ground meets the ground at both abutments and rises clear in the middle', () => {
  const p = line(41, 5), g = p.map(() => 10);
  const d = E.bimCtxDeckProfile(p, g, 6, true, true, 40);
  assert.ok(Math.abs(d[0] - 10.05) < 1e-9 && Math.abs(d[40] - 10.05) < 1e-9, 'ends at the ground');
  assert.ok(Math.abs(d[20] - 16) < 1e-9, 'middle 6 m clear');
  for (let i = 1; i < 21; i++) assert.ok(d[i] >= d[i - 1] - 1e-9, 'no dip on the way up');
});

test('a bridge over a river valley stays level from bank to bank, not 6 m over the water', () => {
  const p = line(21, 10), g = p.map((_, i) => (i === 0 || i === 20 ? 12 : 2));
  const d = E.bimCtxDeckProfile(p, g, 6, true, true, 40);
  for (let i = 0; i < 21; i++) assert.ok(Math.abs(d[i] - 12) < 1e-6 || i === 0 || i === 20, 'level at ' + i + ': ' + d[i]);
  assert.ok(d[10] >= g[10] + 6 - 1e-9);
});

test('an end shared with another bridge way does not come down to the ground', () => {
  const p = line(21, 5), g = p.map(() => 0);
  const d = E.bimCtxDeckProfile(p, g, 6, true, false, 40);
  assert.ok(Math.abs(d[20] - 6) < 1e-9, 'the shared end stays at deck height');
  assert.ok(d[0] < 0.1, 'the abutment comes down');
});

test('bimCtxBridgeEnds counts shared ends by layer only for bridges', () => {
  const m = E.bimCtxBridgeEnds([
    { tags: { bridge: 'yes', layer: '1' }, line: { pts: [[0, 0], [10, 0]] } },
    { tags: { bridge: 'yes', layer: '1' }, line: { pts: [[10, 0], [20, 0]] } },
    { tags: { highway: 'primary' }, line: { pts: [[20, 0], [30, 0]] } },
  ]);
  assert.equal(m['100,0@1'], 2);
  assert.equal(m['0,0@1'], 1);
  assert.equal(m['300,0@1'], undefined);
});
