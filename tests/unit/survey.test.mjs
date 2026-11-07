// Survey arithmetic (survey/survey-arithmetic.js): bearings, legs, and a traverse.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();

test('bearings are read in the ways surveyors write them', () => {
  for (const s of ['N 45 30 00 E', 'N45-30-00E', 'N 45.5 E', 'N 45°30\'00" E']) {
    assert.deepEqual(E.bimParseBearing(s), { az: 45.5 }, s);
  }
  assert.equal(E.bimParseBearing('S 45 W').az, 225);
  assert.ok(E.bimParseBearing('hello').error, 'text that is not a bearing is an error, not a number');
});

test('a bearing written out reads back as the same azimuth', () => {
  for (const az of [0, 12.25, 90, 135.5, 200, 271, 359.5]) {
    const back = E.bimParseBearing(E.bimFormatBearing(az));
    assert.ok(Math.abs(back.az - az) < 1e-6, `${az} -> ${E.bimFormatBearing(az)} -> ${back.az}`);
  }
});

test('legs: one bearing and distance per line; a bad line is reported by its number', () => {
  const r = E.bimParseLegs('N 0 E 10\nnot a leg\n\nS 90 W 5');
  assert.equal(r.legs.length, 2);
  assert.equal(r.legs[1].d, 5);
  assert.equal(r.errors.length, 1);
  assert.match(r.errors[0], /^line 2:/);
});

test('a closed square traverse: no misclosure, its perimeter and area', () => {
  const legs = [0, 90, 180, 270].map((az) => ({ az, d: 10 }));
  const t = E.bimTraverse([0, 0], legs, 0);
  assert.ok(t.misclosure < 1e-9);
  assert.equal(t.perimeter, 40);
  assert.ok(Math.abs(t.area - 100) < 1e-9);
  assert.equal(t.ring.length, 4);
});
