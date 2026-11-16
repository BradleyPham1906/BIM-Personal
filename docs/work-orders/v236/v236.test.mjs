/* V236's work-order tests (docs/work-orders/v236/SPEC.md, WO-01 to WO-08): the pure functions of
   src/js/engine/bim/program-layout.js. Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v236/v236.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v236/v236.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimPlBayWidth', 'bimPlSmall', 'bimPlBands', 'bimPlWallGraph', 'bimPlRoute', 'bimPlCorridors', 'bimPlStair', 'bimPlScore'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/program-layout.js'), 'utf8');
  if (process.env.V236_REF) src += fs.readFileSync(process.env.V236_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/program-layout.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const unit = (id) => ({ ids: [id], k: 1 });
// four rooms of one bay each, packed two by two with no corridor: A B / D C (bay 4 m, depth 5 m)
const FOUR = () => fn('bimPlBands')(['A', 'B', 'C', 'D'].map(unit), 4, 5, 0);
// six rooms, three a side: A B C / F E D
const SIX = () => fn('bimPlBands')(['A', 'B', 'C', 'D', 'E', 'F'].map(unit), 4, 5, 0);

test('WO-01 the bay width: whole bays per room, the least area error over the range, ties to the narrower', () => {
  const b = fn('bimPlBayWidth')([20, 30, 12], 5, 3, 4.5, 0.3);
  assert.equal(b.bay, 3); assert.deepEqual(b.bays, [1, 2, 1]); near(b.error, 8 / 62);
  const c = fn('bimPlBayWidth')([20, 40], 5, 4, 4, 0.3); assert.deepEqual([c.bay, c.bays, c.error], [4, [1, 2], 0]);
  assert.equal(fn('bimPlBayWidth')([], 5, 3, 4, 0.3), null); assert.equal(fn('bimPlBayWidth')([10], 0, 3, 4, 0.3), null);
});

test('WO-02 small rooms clustered with their most strongly linked small neighbour, up to the maximum', () => {
  const C = fn('bimPlSmall')([{ id: 'off', area: 20 }, { id: 'wc1', area: 4 }, { id: 'wc2', area: 4 }, { id: 'st', area: 6 }, { id: 'cl', area: 5 }, { id: 'wc3', area: 3 }],
    [{ a: 'wc1', b: 'wc2', strength: 1 }, { a: 'st', b: 'wc1', strength: 2 }, { a: 'cl', b: 'wc2', strength: 3 }, { a: 'wc3', b: 'wc1', strength: 1 }, { a: 'off', b: 'cl', strength: 1 }], 4, 5, 0.6, 3);
  assert.deepEqual(C, [{ ids: ['off'], area: 20, small: false }, { ids: ['wc1', 'wc2', 'st'], area: 14, small: true },
    { ids: ['cl'], area: 5, small: true }, { ids: ['wc3'], area: 3, small: true }]);
  assert.deepEqual(fn('bimPlSmall')([{ id: 'a', area: 3 }, { id: 'b', area: 3 }], [{ a: 'a', b: 'b', strength: 2, status: 'rejected' }], 4, 5).length, 2, 'a rejected link does not join');
});

test('WO-03 two bands either side of a corridor: the first half left to right, the rest right to left; a cluster stacked, its first room by the corridor', () => {
  const B = fn('bimPlBands')([{ ids: ['A'], k: 1 }, { ids: ['B'], k: 2 }, { ids: ['C', 'D'], areas: [6, 2], k: 1 }], 4, 5, 1.8);
  assert.deepEqual(B, { rooms: [{ id: 'A', x: 0, y: 0, w: 4, h: 5 }, { id: 'B', x: 4, y: 0, w: 8, h: 5 },
    { id: 'C', x: 8, y: 6.8, w: 4, h: 3.75 }, { id: 'D', x: 8, y: 10.55, w: 4, h: 1.25 }], length: 12, spare: [0, 2], corridor: { x: 0, y: 5, w: 12, h: 1.8 } });
  assert.deepEqual(FOUR().rooms.map((r) => [r.id, r.x, r.y]), [['A', 0, 0], ['B', 4, 0], ['C', 4, 5], ['D', 0, 5]]);
});

test('WO-04 the wall graph: corners and T-junctions, one edge per wall piece, exterior walls dearer, each room\'s vertices and edges', () => {
  const g = fn('bimPlWallGraph')(FOUR().rooms);
  assert.deepEqual(g.v, [[0, 0], [4, 0], [4, 5], [0, 5], [8, 0], [8, 5], [8, 10], [4, 10], [0, 10]]);
  assert.deepEqual(g.e.map((e) => [e.a, e.b, e.len, e.ext, e.cost]), [[0, 1, 4, true, 12], [1, 2, 5, false, 5], [2, 3, 4, false, 4], [0, 3, 5, true, 15],
    [1, 4, 4, true, 12], [4, 5, 5, true, 15], [2, 5, 4, false, 4], [5, 6, 5, true, 15], [6, 7, 4, true, 12], [2, 7, 5, false, 5], [7, 8, 4, true, 12], [3, 8, 5, true, 15]]);
  assert.deepEqual(g.roomV, { A: [0, 1, 2, 3], B: [1, 2, 4, 5], C: [2, 5, 6, 7], D: [2, 3, 7, 8] });
  assert.deepEqual(g.roomE, { A: [0, 1, 2, 3], B: [1, 4, 5, 6], C: [6, 7, 8, 9], D: [2, 9, 10, 11] });
  const t = fn('bimPlWallGraph')([{ id: 'big', x: 0, y: 0, w: 8, h: 4 }, { id: 'p', x: 0, y: 4, w: 4, h: 4 }, { id: 'q', x: 4, y: 4, w: 4, h: 4 }], 2);
  assert.ok(t.v.some((v) => v[0] === 4 && v[1] === 4), 'a T-junction splits the long wall');
  assert.equal(t.e.filter((e) => e.ext).every((e) => e.cost === 2 * e.len), true);
});

test('WO-05 a route between two rooms along the walls, from any vertex of one to any of the other', () => {
  const g = fn('bimPlWallGraph')(SIX().rooms);
  const r = fn('bimPlRoute')(g, 'A', 'C');
  assert.equal(r.cost, 4); assert.equal(r.edges.length, 1); assert.deepEqual([g.v[g.e[r.edges[0]].a], g.v[g.e[r.edges[0]].b]], [[4, 5], [8, 5]]);
  assert.deepEqual(fn('bimPlRoute')(g, 'A', 'B').edges, [], 'rooms that meet need no wall');
  assert.equal(fn('bimPlRoute')(g, 'A', 'Z'), null);
  const only = {}; only[0] = 1; assert.equal(fn('bimPlRoute')(g, 'A', 'D', only), null, 'with only one edge allowed there is no way');
});

test('WO-06 corridors from user paths: direct legs, ends attached, use counts, the spine, spurs nearest first, failures', () => {
  const g4 = fn('bimPlWallGraph')(FOUR().rooms);
  assert.deepEqual(fn('bimPlCorridors')(g4, [{ rooms: ['A', 'C'], freq: 'primary' }, { rooms: ['B', 'D'], freq: 'secondary' }, { rooms: ['A', 'B', 'Z'] }]),
    { edges: { 1: { count: 2, weight: 5, spine: true }, 9: { count: 2, weight: 5, spine: true } }, direct: [['A', 'B']], spurs: [], noAccess: [], failed: [['B', 'Z']] });
  const g6 = fn('bimPlWallGraph')(SIX().rooms);
  assert.deepEqual(fn('bimPlCorridors')(g6, [{ rooms: ['A', 'C'], freq: 'primary' }]),
    { edges: { 1: { count: 1, weight: 3, spine: false }, 5: { count: 1, weight: 3, spine: false }, 6: { count: 1, weight: 3, spine: false } },
      direct: [], spurs: [{ room: 'D', edges: [12], length: 5 }, { room: 'F', edges: [14], length: 5 }], noAccess: [], failed: [] });
  const two = fn('bimPlCorridors')(g6, [{ rooms: ['A', 'C'], freq: 'primary' }, { rooms: ['F', 'C'], freq: 'occasional' }], { spine: 2 });
  assert.deepEqual(two.edges, { 1: { count: 1, weight: 3, spine: false }, 5: { count: 2, weight: 4, spine: true }, 6: { count: 2, weight: 4, spine: true }, 14: { count: 1, weight: 1, spine: false } });
  assert.deepEqual(two.spurs, [{ room: 'D', edges: [12], length: 5 }]);
  assert.deepEqual(fn('bimPlCorridors')(g6, []).noAccess, ['A', 'B', 'C', 'D', 'E', 'F'], 'no paths, no corridor: every room reported');
});

test('WO-07 the stair: the corridor corner least far from the rooms by weight, or with the shortest worst leg', () => {
  const g = fn('bimPlWallGraph')(FOUR().rooms), C = fn('bimPlCorridors')(g, [{ rooms: ['A', 'C'] }, { rooms: ['B', 'D'] }]), net = Object.keys(C.edges).map(Number);
  assert.deepEqual(fn('bimPlStair')(g, net, [1, 7], { A: 1, B: 1, C: 1, D: 1 }, 'median'), { vertex: 1, sum: 10, worst: 5 });
  assert.deepEqual(fn('bimPlStair')(g, net, [7, 1], { A: 1, B: 1, C: 1, D: 1 }, 'median'), { vertex: 1, sum: 10, worst: 5 }, 'ties to the lower vertex');
  assert.deepEqual(fn('bimPlStair')(g, net, [1, 2, 7], { A: 1, B: 1, C: 1, D: 1 }, 'centre'), { vertex: 2, sum: 0, worst: 0 });
  assert.deepEqual(fn('bimPlStair')(g, net, [1, 7], { A: 3, B: 1, C: 1, D: 1 }, 'median'), { vertex: 1, sum: 10, worst: 5 });
  assert.deepEqual(fn('bimPlStair')(g, net, [1, 7], { A: 1, B: 1, C: 3, D: 3 }, 'median'), { vertex: 7, sum: 10, worst: 5 });
  assert.equal(fn('bimPlStair')(g, [], [1], { C: 1 }, 'median'), null, 'no corridor reaches the room');
});

test('WO-08 the scorecard: fill, corridor share, area deviation, required adjacency met, forbidden broken', () => {
  const s = fn('bimPlScore')(FOUR().rooms, [{ id: 'A', areaMin: 16, areaMax: 24 }, { id: 'B', areaMax: 25 }, { id: 'C' }, { id: 'D', areaMin: 20 }],
    [{ a: 'A', b: 'B', kind: 'required' }, { a: 'A', b: 'C', kind: 'required' }, { a: 'B', b: 'D', kind: 'forbidden' }, { a: 'A', b: 'D', kind: 'forbidden' },
      { a: 'A', b: 'C', kind: 'required', status: 'rejected' }, { a: 'A', b: 'C', kind: 'required', rel: 'near' }], 0, 80);
  assert.equal(s.fill, 1); assert.equal(s.corridorShare, 0);
  assert.deepEqual(Object.keys(s.deviation).sort(), ['A', 'B', 'D']); near(s.deviation.B, -0.2); near(s.worst, -0.2);
  assert.deepEqual([s.required, s.met, s.adjacency, s.forbidden], [2, 1, 0.5, 1]);
  const z = fn('bimPlScore')([], [], [], 0, 0); assert.deepEqual([z.fill, z.corridorShare, z.adjacency, z.worst], [null, null, null, 0]);
});
