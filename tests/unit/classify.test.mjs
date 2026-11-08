// V173: the classification methods and stretches (map/classify.js), against mapclassify's worked
// examples on its calemp data (58 values; PySAL mapclassify, BSD-3-Clause, tests/test_mapclassify.py)
// and simple-statistics' Jenks cases, as docs/research/research-contents-pane/classification.md records.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const cal = JSON.parse(fs.readFileSync(new URL('../fixtures/data/calemp.json', import.meta.url), 'utf8'));
const near = (a, b, eps) => { assert.equal(a.length, b.length, `${a} vs ${b}`); a.forEach((x, i) => assert.ok(Math.abs(x - b[i]) <= eps, `${a} is not ${b}`)); };

test('natural breaks are Fisher-Jenks exact: calemp k=5 and k=9', () => {
  const r = E.bimClsBreaks(cal, 'natural', { k: 5 });
  assert.deepEqual(r.breaks, [75.29, 192.05, 370.5, 722.85, 4111.45]);
  assert.deepEqual(r.counts, [49, 3, 4, 1, 1]);
  assert.ok(Math.abs(r.gvf - 0.998435) < 1e-5, `gvf ${r.gvf}`);
  assert.deepEqual(E.bimClsBreaks(cal, 'natural', { k: 9 }).breaks, [16.7, 40.48, 75.29, 110.74, 192.05, 264.93, 370.5, 722.85, 4111.45]);
});

test('natural breaks on simple-statistics cases', () => {
  assert.deepEqual(E.bimClsBreaks([1, 2, 4, 5, 7, 9, 10, 20], 'natural', { k: 3 }).breaks, [5, 10, 20]);
  assert.deepEqual(E.bimClsBreaks([2, 32, 33, 34, 100], 'natural', { k: 3 }).breaks, [2, 34, 100]);
  assert.deepEqual(E.bimClsBreaks([9, 10, 11, 12, 13], 'natural', { k: 5 }).breaks, [9, 10, 11, 12, 13]);
});

test('natural breaks agree with a brute-force optimum on small random data', () => {
  let seed = 7; const rnd = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
  for (let t = 0; t < 30; t++) {
    const x = Array.from({ length: 9 + (t % 5) }, () => Math.round(rnd() * 1000) / 10).sort((a, b) => a - b);
    const u = [...new Set(x)];
    const k = 3;
    if (u.length < k) continue;
    const sse = (a) => { const m = a.reduce((s, v) => s + v, 0) / a.length; return a.reduce((s, v) => s + (v - m) ** 2, 0); };
    let best = Infinity;
    for (let i = 1; i < x.length; i++) for (let j = i + 1; j < x.length; j++) {
      if (x[i] === x[i - 1] || x[j] === x[j - 1]) continue;
      best = Math.min(best, sse(x.slice(0, i)) + sse(x.slice(i, j)) + sse(x.slice(j)));
    }
    const b = E.bimClsBreaks(x, 'natural', { k }).breaks;
    const cls = b.map((hi, c) => x.filter((v) => v <= hi && (c === 0 || v > b[c - 1])));
    assert.ok(Math.abs(cls.reduce((s, a) => s + sse(a), 0) - best) < 1e-6, `case ${t}`);
  }
});

test('quantile is type 7 and equal interval spans the range', () => {
  const q = E.bimClsBreaks(cal, 'quantile', { k: 5 });
  near(q.breaks, [1.464, 5.798, 13.278, 54.616, 4111.45], 1e-9);
  assert.deepEqual(q.counts, [12, 11, 12, 11, 12]);
  const e = E.bimClsBreaks(cal, 'equal', { k: 5 });
  near(e.breaks, [822.394, 1644.658, 2466.922, 3289.186, 4111.45], 1e-9);
  assert.deepEqual(e.counts, [57, 0, 0, 0, 1]);
});

test('standard deviation steps from the mean, the sample sd', () => {
  const r = E.bimClsBreaks([1, 2, 3, 4, 5, 6, 7, 8, 9], 'stddev', { step: 1, centre: 'break' });
  // mean 5, s = sqrt(7.5) = 2.7386: breaks on the lattice 5 + j s inside (1, 9), then the highest
  near(r.breaks, [5 - 2.7386127875258306, 5, 5 + 2.7386127875258306, 9], 1e-9);
  const c = E.bimClsBreaks([1, 2, 3, 4, 5, 6, 7, 8, 9], 'stddev', { step: 1, centre: 'class' });
  // the class of width s centred on 5; 5 - 1.5 s = 0.89 and 5 + 1.5 s = 9.11 fall outside (1, 9)
  near(c.breaks, [5 - 0.5 * 2.7386127875258306, 5 + 0.5 * 2.7386127875258306, 9], 1e-9);
});

test('pretty follows R, log interval needs positive values, manual keeps what is inside', () => {
  assert.deepEqual(E.bimClsBreaks(cal, 'pretty', { k: 5 }).breaks, [1000, 2000, 3000, 4000, 4111.45]);
  assert.deepEqual(E.bimClsBreaks([-3.2, 7.9], 'pretty', { k: 5 }).breaks, [-2, 0, 2, 4, 6, 7.9]);
  assert.ok(E.bimClsBreaks([0, 1, 10], 'log', { k: 3 }).error);
  near(E.bimClsBreaks([1, 10, 100, 1000], 'log', { k: 3 }).breaks, [10, 100, 1000], 1e-9);
  assert.deepEqual(E.bimClsBreaks([0, 5, 10], 'manual', { breaks: [3, '7', 99, -1, 'x'] }).breaks, [3, 7, 10]);
});

test('edges: text and blanks dropped, one class for one value, fewer classes than asked are said', () => {
  const r = E.bimClsBreaks([NaN, null, undefined, '', 3, '4', Infinity, true, 'x', 1], 'equal', { k: 2 });
  assert.equal(r.n, 3);
  assert.deepEqual(r.breaks, [2.5, 4]);
  for (const m of ['natural', 'quantile', 'equal', 'stddev', 'pretty', 'log']) {
    const s = E.bimClsBreaks([7, 7, 7, 7], m, { k: 4 });
    assert.deepEqual(s.breaks, [7], m);
    assert.deepEqual(s.counts, [4], m);
  }
  const d = E.bimClsBreaks([0, 0, 0, 5, 5], 'natural', { k: 5 });
  assert.deepEqual(d.breaks, [0, 5]);
  assert.match(d.note, /2 classes of the 5 asked/);
  assert.ok(E.bimClsBreaks([], 'equal', {}).error);
  assert.ok(E.bimClsBreaks([1, 2], 'nonsense', {}).error);
});

test('a large list is sampled evenly for natural breaks, and the same every time', () => {
  const x = Array.from({ length: 150000 }, (_, i) => (i * 7919) % 150000);
  const a = E.bimClsBreaks(x, 'natural', { k: 5 }), b = E.bimClsBreaks(x, 'natural', { k: 5 });
  assert.equal(a.sampled, 100000);
  assert.deepEqual(a.breaks, b.breaks);
  assert.equal(a.breaks[a.breaks.length - 1], 149999);
  assert.equal(a.counts.reduce((s, c) => s + c, 0), 150000);
  assert.match(a.note, /even sample of 100000 of the 150000/);
});

test('stretches: min-max, standard deviation, percent clip, histogram equalised', () => {
  const x = Array.from({ length: 101 }, (_, i) => i);
  assert.deepEqual(E.bimClsStretch(x, 'minmax'), { type: 'minmax', lo: 0, hi: 100 });
  const c = E.bimClsStretch(x, 'clip');
  assert.equal(c.lo, 2); assert.equal(c.hi, 98);
  const s = E.bimClsStretch(x, 'stddev', { n: 1 });
  near([s.lo, s.hi], [50 - 29.300170647967224, 50 + 29.300170647967224], 1e-9);
  assert.equal(E.bimClsStretchAt(c, 50), 0.5);
  assert.equal(E.bimClsStretchAt(c, -10), 0);
  assert.equal(E.bimClsStretchAt(c, 500), 1);
  const skew = [1, 1, 1, 1, 1, 1, 1, 1, 2, 1000];
  const h = E.bimClsStretch(skew, 'histeq');
  assert.ok(E.bimClsStretchAt(h, 2) > 0.85, 'equalised: 2 sits high, since 9 of 10 values are at or below it');
  assert.ok(E.bimClsStretchAt(E.bimClsStretch(skew, 'minmax'), 2) < 0.01, 'linear: 2 sits at the bottom');
  assert.equal(E.bimClsStretchAt(c, 'x'), null);
  assert.ok(E.bimClsStretch(x, 'nonsense').error);
});
