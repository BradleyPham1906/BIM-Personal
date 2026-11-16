/* V235's work-order tests (docs/work-orders/v235/SPEC.md, WO-01 to WO-09): the pure functions of
   src/js/engine/bim/program-graph-lab.js. Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v235/v235.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v235/v235.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimGlEdges', 'bimGlBlocks', 'bimGlHubs', 'bimGlDepth', 'bimGlLouvain', 'bimGlCoverage', 'bimGlOpenGuess', 'bimGlAxes', 'bimGlSuggestPath'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/program-graph-lab.js'), 'utf8');
  if (process.env.V235_REF) src += fs.readFileSync(process.env.V235_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/program-graph-lab.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// two triangles (a b c) and (d e f) joined by one link c-d, all primary
const IDS = ['a', 'b', 'c', 'd', 'e', 'f'];
const TRI = () => [['a', 'b'], ['b', 'c'], ['a', 'c'], ['d', 'e'], ['e', 'f'], ['d', 'f'], ['c', 'd']].map((p) => ({ a: p[0], b: p[1], strength: 1 }));

test('WO-01 the edges: known rooms, one per pair in order, weight 3, 2, 1 by strength, rejected and self links left out', () => {
  assert.deepEqual(fn('bimGlEdges')(['x', 'y', 'z'], [{ a: 'y', b: 'x', strength: 1 }, { a: 'x', b: 'y', strength: 3 }, { a: 'x', b: 'z' },
    { a: 'z', b: 'z', strength: 1 }, { a: 'x', b: 'q', strength: 1 }, { a: 'y', b: 'z', strength: 3, status: 'rejected' }, { a: 'y', b: 'z', strength: 3 }, null]),
    [{ a: 'x', b: 'y', w: 3 }, { a: 'x', b: 'z', w: 2 }, { a: 'y', b: 'z', w: 1 }]);
});

test('WO-02 articulation points and bridges with the rooms on each side; small bridges filtered', () => {
  assert.deepEqual(fn('bimGlBlocks')(IDS, TRI()), { articulation: ['c', 'd'], bridges: [{ a: 'c', b: 'd', sides: [3, 3] }] });
  const tail = TRI().concat([{ a: 'f', b: 'g', strength: 1 }]);
  const r = fn('bimGlBlocks')(IDS.concat(['g']), tail);
  assert.deepEqual(r.articulation, ['c', 'd', 'f']);
  assert.deepEqual(r.bridges, [{ a: 'c', b: 'd', sides: [3, 4] }, { a: 'f', b: 'g', sides: [6, 1] }]);
  assert.deepEqual(fn('bimGlBlocks')(IDS.concat(['g']), tail, 2).bridges, [{ a: 'c', b: 'd', sides: [3, 4] }]);
  assert.deepEqual(fn('bimGlBlocks')(['p', 'q'], []), { articulation: [], bridges: [] });
});

test('WO-03 hub scores: the sum of link weights, the top room (ties to the first id), the mean', () => {
  const h = fn('bimGlHubs')(IDS, TRI());
  assert.deepEqual(h.hub, { a: 6, b: 6, c: 9, d: 9, e: 6, f: 6 });
  assert.equal(h.top, 'c'); assert.equal(h.max, 9); near(h.avg, 42 / 6);
  assert.deepEqual(fn('bimGlHubs')([], []), { hub: {}, top: null, max: 0, avg: 0 });
});

test('WO-04 depth from the centre of the largest connected part', () => {
  const d = fn('bimGlDepth')(IDS.concat(['z']), TRI());
  assert.equal(d.centre, 'c');
  assert.deepEqual(d.depth, { c: 0, a: 1, b: 1, d: 1, e: 2, f: 2 });
  near(d.avg, 7 / 5); assert.equal(d.max, 2);
  assert.deepEqual(fn('bimGlDepth')([], []), { centre: null, depth: {}, avg: 0, max: 0 });
});

test('WO-05 clusters by Louvain with a resolution; repeatable; never in two pieces', () => {
  const L = fn('bimGlLouvain');
  const r = L(IDS, TRI(), 1);
  assert.deepEqual(r.community, { a: 0, b: 0, c: 0, d: 1, e: 1, f: 1 }); assert.equal(r.count, 2); near(r.modularity, 2 * (9 / 21 - 0.25));
  assert.deepEqual(L(IDS, TRI()), r, 'resolution 1 by default, and the same answer twice');
  const one = L(IDS, TRI(), 0.05); assert.equal(one.count, 1); near(one.modularity, 0.95);
  const six = L(IDS, TRI(), 5); assert.equal(six.count, 6); near(six.modularity, -5 * (4 * 36 + 2 * 81) / 1764);
  const iso = L(['p', 'q', 'r'], [{ a: 'p', b: 'q', strength: 1 }]);
  assert.deepEqual(iso.community, { p: 0, q: 0, r: 1 });
  assert.deepEqual(L(['p', 'q'], []), { community: { p: 0, q: 1 }, count: 2, modularity: 0 });
});

test('WO-06 path coverage: rooms on at least one path, and those left out in order', () => {
  assert.deepEqual(fn('bimGlCoverage')([{ rooms: ['a', 'c'] }, { rooms: ['c', 'e', 'zz'] }, null], IDS),
    { covered: 3, total: 6, missing: ['b', 'd', 'f'] });
  assert.deepEqual(fn('bimGlCoverage')([], ['a']), { covered: 0, total: 1, missing: ['a'] });
});

test('WO-07 a walk-through room guessed from its name', () => {
  const o = fn('bimGlOpenGuess');
  ['Main Lobby', 'waiting area', 'Reception', 'ENTRANCE HALL', 'Staff lounge', 'Vestibule 2'].forEach((n) => assert.equal(o(n), 'open', n));
  ['Office', 'Consult 1', 'Sports hall', 'Receptionist office desk'.replace('Reception', 'Desk'), '', null].forEach((n) => assert.equal(o(n), 'closed', String(n)));
});

test('WO-08 principal axes of a building\'s rooms: the long and short extents and their ratio', () => {
  const a = fn('bimGlAxes')([[0, 0], [10, 0], [10, 2], [0, 2]]);
  near(a.major, 10); near(a.minor, 2); near(a.aspect, 5); near(a.angle, 0);
  const b = fn('bimGlAxes')([[0, 0], [0, 10], [2, 10], [2, 0]]);
  near(b.major, 10, 1e-9); near(b.minor, 2, 1e-9); near(b.aspect, 5, 1e-9); near(Math.abs(b.angle), Math.PI / 2, 1e-9);
  assert.deepEqual(fn('bimGlAxes')([[1, 1]]), { major: 0, minor: 0, aspect: null, angle: 0 });
  assert.equal(fn('bimGlAxes')([[0, 0], [5, 0]]).aspect, null, 'a line has no width');
});

test('WO-09 a suggested path: breadth first from the entrance, the strongest links first', () => {
  const L = [{ a: 'lobby', b: 'wc', strength: 3 }, { a: 'lobby', b: 'wait', strength: 1 }, { a: 'wait', b: 'consult', strength: 1 },
    { a: 'lobby', b: 'office', strength: 2 }, { a: 'office', b: 'store', strength: 2, status: 'rejected' }];
  assert.deepEqual(fn('bimGlSuggestPath')(['lobby', 'wait', 'consult', 'office', 'wc', 'store'], L, 'lobby'),
    { name: 'Suggested from lobby', rooms: ['lobby', 'wait', 'office', 'wc', 'consult'], freq: 'primary', status: 'suggested' });
  assert.equal(fn('bimGlSuggestPath')(['a'], [], 'z'), null);
});
