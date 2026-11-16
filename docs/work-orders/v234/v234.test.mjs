/* V234's work-order tests (docs/work-orders/v234/SPEC.md, WO-01 to WO-07): the pure functions of
   src/js/engine/bim/program-graph.js. Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v234/v234.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v234/v234.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimPgNodes', 'bimPgGower', 'bimPgParamLinks', 'bimPgCollapse', 'bimPgContain', 'bimPgTick', 'bimPgSettle'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/program-graph.js'), 'utf8');
  if (process.env.V234_REF) src += fs.readFileSync(process.env.V234_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/program-graph.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);
const dist = (p, q) => Math.hypot(p.x - q.x, p.y - q.y);

test('WO-01 nodes from programme items: one per copy, sorted by id, radius from area, the spiral, saved and pinned positions', () => {
  const items = [{ id: 'b', areaMin: 12, areaMax: 12, count: 2.6, building: 'X' }, { id: 'a', areaMax: 20, building: 'X' }, { id: '' }, null, { id: 'c' }];
  const n = fn('bimPgNodes')(items, { centers: { X: [100, 50] } });
  assert.deepEqual(n.map((x) => x.id), ['a', 'b#1', 'b#2', 'c']);
  assert.deepEqual(n.map((x) => x.item), ['a', 'b', 'b', 'c']);
  near(n[0].r, Math.sqrt(20 / Math.PI)); near(n[1].r, Math.sqrt(12 / Math.PI)); near(n[3].area, 10, 0, 'no area: 10 m2');
  const mean = (Math.sqrt(20 / Math.PI) + 2 * Math.sqrt(12 / Math.PI) + Math.sqrt(10 / Math.PI)) / 4;
  near(n[0].x, 100 + mean * Math.sqrt(0.5), 1e-6); near(n[0].y, 50, 1e-6);
  const ang = Math.PI * (3 - Math.sqrt(5));
  near(n[1].x, 100 + mean * Math.sqrt(1.5) * Math.cos(ang), 1e-6); near(n[1].y, 50 + mean * Math.sqrt(1.5) * Math.sin(ang), 1e-6);
  near(n[3].x, mean * Math.sqrt(0.5), 1e-6, 'a building without a centre spirals round the origin');
  assert.deepEqual([n[0].vx, n[0].vy, n[0].fx, n[0].fy], [0, 0, null, null]);
  const m = fn('bimPgNodes')(items, { centers: { X: [100, 50] }, saved: { a: [1, 2] }, pins: { 'b#2': [7, 8] }, scale: 2 });
  assert.deepEqual([m[0].x, m[0].y], [1, 2]); assert.deepEqual([m[2].x, m[2].y, m[2].fx, m[2].fy], [7, 8, 7, 8]);
  near(m[0].r, 2 * Math.sqrt(20 / Math.PI));
  assert.deepEqual(fn('bimPgNodes')([], {}), []);
});

test('WO-02 Gower similarity: weighted, range-normalised, blanks skipped, null with nothing shared', () => {
  const g = fn('bimPgGower');
  near(g({ p: 1, q: 5 }, { p: 3, q: 5 }, { p: 1, q: 1 }, { p: 4, q: 4 }), 0.75);
  near(g({ p: 1, q: 5 }, { p: 3, q: 5 }, { p: 3, q: 1 }, { p: 4, q: 4 }), 0.625);
  near(g({ p: 1 }, { p: 3, q: 5 }, { p: 1, q: 1 }, { p: 4, q: 4 }), 0.5, 1e-9, 'q blank in one: skipped');
  near(g({ p: 2 }, { p: 2 }, { p: 1 }, { p: 0 }), 1, 1e-9, 'a range of 0: alike');
  near(g({ p: 1, q: 1 }, { p: 5, q: 1 }, { p: 0, q: 1 }, { p: 4, q: 4 }), 1, 1e-9, 'a weight of 0 does not count');
  assert.equal(g({ p: 1 }, { q: 1 }, { p: 1, q: 1 }, { p: 4, q: 4 }), null);
  assert.equal(g(null, { p: 1 }, { p: 1 }, { p: 1 }), null);
});

test('WO-03 links from parameters: each room\'s top k above the floor, a maximum spanning tree, strengths by band, all suggested', () => {
  const items = [{ id: 'c', params: { privacy: 5 } }, { id: 'a', params: { privacy: 1 } }, { id: 'b', params: { privacy: 1 } },
    { id: 'd', params: { privacy: 5 } }, { id: 'e', params: {} }];
  const L = fn('bimPgParamLinks')(items, { privacy: 1 });
  assert.deepEqual(L, [
    { a: 'a', b: 'b', kind: 'desired', rel: 'next', nearM: 15, strength: 1, reason: 'similar parameters 1.00', status: 'suggested' },
    { a: 'a', b: 'c', kind: 'desired', rel: 'next', nearM: 15, strength: 3, reason: 'similar parameters 0.00', status: 'suggested' },
    { a: 'c', b: 'd', kind: 'desired', rel: 'next', nearM: 15, strength: 1, reason: 'similar parameters 1.00', status: 'suggested' }]);
  const M = fn('bimPgParamLinks')([{ id: 'a', params: { p: 0 } }, { id: 'b', params: { p: 1.5 } }, { id: 'c', params: { p: 10 } }], { p: 1 }, { k: 1, floor: 0.5, bands: [0.95, 0.8] });
  assert.deepEqual(M.map((x) => [x.a, x.b, x.strength, x.reason]), [['a', 'b', 2, 'similar parameters 0.85'], ['b', 'c', 3, 'similar parameters 0.15']]);
  assert.deepEqual(fn('bimPgParamLinks')([], { p: 1 }), []);
});

test('WO-04 building-level links: the strongest strength and the count, same building and rejected left out', () => {
  const R = [{ a: 'a', b: 'c', strength: 2 }, { a: 'c', b: 'b', strength: 1 }, { a: 'a', b: 'b', strength: 1 },
    { a: 'a', b: 'c', strength: 1, status: 'rejected' }, { a: 'a', b: 'z', strength: 1 }, { a: 'd', b: 'a', strength: 3 }];
  assert.deepEqual(fn('bimPgCollapse')(R, { a: 'X', b: 'X', c: 'Y', d: 'W' }),
    [{ a: 'W', b: 'X', strength: 3, count: 1 }, { a: 'X', b: 'Y', strength: 1, count: 2 }]);
  assert.deepEqual(fn('bimPgCollapse')([], {}), []);
});

test('WO-05 a point kept inside a polygon, a radius in from its edge, either winding', () => {
  const ct = fn('bimPgContain'), sq = [[0, 0], [10, 0], [10, 10], [0, 10]], cw = sq.slice().reverse();
  assert.deepEqual(ct([5, 5], 1, sq), [5, 5]);
  [sq, cw].forEach((P) => {
    const a = ct([12, 5], 1, P); near(a[0], 9); near(a[1], 5);
    const b = ct([0.5, 5], 1, P); near(b[0], 1); near(b[1], 5);
    const c = ct([5, -3], 2, P); near(c[0], 5); near(c[1], 2);
  });
  assert.deepEqual(ct([3, 4], 1, [[0, 0], [1, 1]]), [3, 4]);
});

const twoLinked = (x2) => ({ nodes: [{ id: 'a', building: '', r: 1, x: 0, y: 0, vx: 0, vy: 0, fx: null, fy: null },
  { id: 'b', building: '', r: 1, x: x2, y: 0, vx: 0, vy: 0, fx: null, fy: null }], links: [{ a: 'a', b: 'b', strength: 1 }], parents: {}, opts: { charge: 0 }, alpha: 1 });
test('WO-06 one tick: alpha cools, a link pulls, collision pushes, pins hold, a parent contains, the input untouched', () => {
  const tk = fn('bimPgTick'), s = twoLinked(20), before = JSON.stringify(s), t = tk(s);
  assert.equal(JSON.stringify(s), before, 'the input is not changed');
  near(t.alpha, 1 - 0.0228);
  assert.ok(dist(t.nodes[0], t.nodes[1]) < 20, 'the link pulls them together');
  const p = twoLinked(20); p.nodes[0].fx = 0; p.nodes[0].fy = 0; const tp = tk(p);
  assert.deepEqual([tp.nodes[0].x, tp.nodes[0].y, tp.nodes[0].vx], [0, 0, 0]); assert.ok(tp.nodes[1].x < 20);
  const c = twoLinked(0.5); c.links = []; const tc = tk(c);
  assert.ok(dist(tc.nodes[0], tc.nodes[1]) > 0.5, 'overlapping bubbles are pushed apart');
  const q = twoLinked(0.5); q.links = []; q.opts = { charge: -5 }; q.nodes = [Object.assign({}, q.nodes[0], { building: 'B', x: 10, y: 0 })];
  q.parents = { B: { cx: 0, cy: 0, R: 5 } }; const tq = tk(q);
  near(Math.hypot(tq.nodes[0].x, tq.nodes[0].y), 4, 1e-9, 'held a radius inside the circle');
  const g = twoLinked(0.5); g.links = []; g.nodes = [Object.assign({}, g.nodes[0], { building: 'B', x: 30, y: 5 })];
  g.parents = { B: { poly: [[0, 0], [10, 0], [10, 10], [0, 10]] } }; const tg = tk(g);
  near(tg.nodes[0].x, 9, 1e-9); assert.ok(tg.nodes[0].y >= 1 - 1e-9 && tg.nodes[0].y <= 9 + 1e-9);
});

test('WO-07 settle: ticks until alpha is under its minimum or the limit; repeatable; linked rooms end closer', () => {
  const st = fn('bimPgSettle');
  const mk = () => ({ nodes: ['a', 'b', 'c', 'd', 'e'].map((id, i) => ({ id, building: 'B', r: 1.5, x: i * 3 - 6, y: (i % 2) * 2, vx: 0, vy: 0, fx: null, fy: null })),
    links: [{ a: 'a', b: 'b', strength: 1 }, { a: 'b', b: 'c', strength: 1 }, { a: 'c', b: 'd', strength: 2 }, { a: 'd', b: 'e', strength: 3 }],
    parents: { B: { cx: 0, cy: 0, R: 12 } }, opts: {}, alpha: 1 });
  const r = st(mk());
  assert.equal(r.ticks, 300); assert.equal(r.settled, true); assert.ok(r.sim.alpha < 0.001);
  assert.deepEqual(st(mk()), r, 'the same input gives the same result');
  const N = {}; r.sim.nodes.forEach((n) => { N[n.id] = n; });
  assert.ok(dist(N.a, N.b) < dist(N.a, N.e), 'linked rooms end closer than the ends of the chain');
  r.sim.nodes.forEach((n) => assert.ok(Math.hypot(n.x, n.y) <= 12 - 1.5 + 1e-9, n.id + ' inside its building'));
  for (let i = 0; i < 5; i++) for (let j = i + 1; j < 5; j++) assert.ok(dist(r.sim.nodes[i], r.sim.nodes[j]) > 3 * 0.9, 'no bubble mostly over another');
  const s10 = st(mk(), 10); assert.equal(s10.ticks, 10); assert.equal(s10.settled, false);
});
