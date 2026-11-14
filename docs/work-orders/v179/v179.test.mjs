/* V179's work-order tests (docs/work-orders/v179/SPEC.md, WO-01 to WO-09): the pure functions of
   src/js/engine/bim/interiors.js, Interiors I1 (programme and adjacency) and the first measurement of I2.

   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v179/v179.test.mjs
     node --test --test-name-pattern="WO-04" docs/work-orders/v179/v179.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimIntProgramItem', 'bimIntRelation', 'bimIntInside', 'bimIntSharedLength', 'bimIntDoorLinks', 'bimIntDistances',
  'bimIntCheck', 'bimIntMatch', 'bimIntMinWidth'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/interiors.js'), 'utf8');
  if (process.env.V179_REF) src += fs.readFileSync(process.env.V179_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const I = load();
const fn = (n) => { assert.equal(typeof I[n], 'function', n + ' is not built yet in src/js/engine/bim/interiors.js'); return I[n]; };
const near = (a, b) => assert.ok(Math.abs(a - b) < 1e-9, a + ' is not ' + b);

// three rooms in a row along x, 4 m deep, with 0.2 m walls between: A [0,4], B [4.2,7.2], C [7.4,10]
const A = { id: 'A', pts: [[0, 0], [4, 0], [4, 4], [0, 4]] };
const B = { id: 'B', pts: [[4.2, 0], [7.2, 0], [7.2, 4], [4.2, 4]] };
const C = { id: 'C', pts: [[7.4, 0], [10, 0], [10, 2], [7.4, 2]] };

test('WO-01 a programme item: text trimmed, count at least 1, the area range in order, unknowns null', () => {
  assert.deepEqual(fn('bimIntProgramItem')({ id: 'p1', use: ' Bedroom ', count: 2.7, areaMin: 14, areaMax: 10, rationale: 'brief' }),
    { id: 'p1', use: 'Bedroom', count: 2, areaMin: 10, areaMax: 14, rationale: 'brief' });
  assert.deepEqual(fn('bimIntProgramItem')({ count: 0, areaMin: -1 }), { id: '', use: '', count: 1, areaMin: null, areaMax: null, rationale: '' });
  assert.deepEqual(fn('bimIntProgramItem')(null).count, 1);
});

test('WO-02 a relation: two different rooms; kind, relation and the near distance defaulted', () => {
  assert.deepEqual(fn('bimIntRelation')({ a: 'Kitchen', b: 'Dining', kind: 'required', rel: 'near', nearM: 6 }),
    { a: 'Kitchen', b: 'Dining', kind: 'required', rel: 'near', nearM: 6 });
  assert.deepEqual(fn('bimIntRelation')({ a: 'x', b: 'y', kind: 'must', rel: 'beside', nearM: -2 }),
    { a: 'x', b: 'y', kind: 'desired', rel: 'next', nearM: 15 });
  assert.equal(fn('bimIntRelation')({ a: 'x', b: 'x' }), null);
  assert.equal(fn('bimIntRelation')({ a: 'x' }), null);
});

test('WO-03 a point inside a polygon (even-odd), plan [x, z]', () => {
  const f = fn('bimIntInside');
  assert.equal(f([1, 1], A.pts), true);
  assert.equal(f([5, 1], A.pts), false);
  assert.equal(f([2, 2], [[0, 0], [4, 0], [4, 4], [2, 1], [0, 4]]), false, 'in the notch of a concave room');
  assert.equal(f([1, 1], null), false);
});

test('WO-04 the length two rooms share across a wall up to the tolerance', () => {
  near(fn('bimIntSharedLength')(A.pts, B.pts, 0.3), 4);
  near(fn('bimIntSharedLength')(B.pts, C.pts, 0.3), 2, 'C is only 2 m deep');
  near(fn('bimIntSharedLength')(A.pts, C.pts, 0.3), 0);
  near(fn('bimIntSharedLength')(A.pts, B.pts, 0.1), 0, 'the wall is thicker than the tolerance');
  near(fn('bimIntSharedLength')(A.pts, B.pts), 4, 'the default tolerance is 0.5 m');
  near(fn('bimIntSharedLength')(A.pts, [[0, 0], [1, 0]]), 0);
});

test('WO-05 a door links the rooms on its two sides; outside is a room called outside', () => {
  const doors = [
    { id: 'd1', center: [4.1, 2], dir: [0, 1], width: 0.9 },
    { id: 'd2', center: [2, 0], dir: [1, 0], width: 1 },
    { id: 'd3', center: [2, 2], dir: [1, 0], width: 0.8 },
    { id: 'd4', center: [8, 1], dir: [0, 0] }
  ];
  assert.deepEqual(fn('bimIntDoorLinks')([A, B, C], doors), [
    { a: 'A', b: 'B', door: 'd1', width: 0.9 },
    { a: 'A', b: 'outside', door: 'd2', width: 1 }
  ]);
  assert.deepEqual(fn('bimIntDoorLinks')(null, doors), []);
});

test('WO-06 route costs from one room by the doors; unreachable rooms are absent, not zero', () => {
  const links = [{ a: 'A', b: 'corr', door: 'dA' }, { a: 'B', b: 'corr', door: 'dB' }, { a: 'corr', b: 'exit', door: 'dX' }, { a: 'D', b: 'E', door: 'dD' }];
  const d = fn('bimIntDistances')(links, 'A', { dA: 4, dB: 3, dX: 6 });
  assert.deepEqual(d, { A: 0, corr: 4, B: 7, exit: 10 });
  assert.equal('D' in d, false);
  assert.deepEqual(fn('bimIntDistances')(links, 'B', null), { B: 0, corr: 1, A: 2, exit: 2 });
  assert.deepEqual(fn('bimIntDistances')(null, 'A'), {});
});

const FACTS = { rooms: { A: 1, B: 1, C: 1 }, shared: { 'A|B': 4 }, doors: { 'B|C': 1 }, dist: { A: { C: 9 } } };
test('WO-07 next and apart from shared walls and doors; near from the route; missing facts not evaluated', () => {
  const c = fn('bimIntCheck');
  assert.deepEqual(c({ a: 'B', b: 'A', rel: 'next', nearM: 15 }, FACTS), { status: 'met', why: 'a shared wall' });
  assert.deepEqual(c({ a: 'C', b: 'B', rel: 'next', nearM: 15 }, FACTS), { status: 'met', why: 'a door between them' });
  assert.deepEqual(c({ a: 'A', b: 'C', rel: 'next', nearM: 15 }, FACTS), { status: 'not met', why: 'no shared wall or door' });
  assert.deepEqual(c({ a: 'A', b: 'B', rel: 'apart', nearM: 15 }, FACTS), { status: 'not met', why: 'a shared wall' });
  assert.deepEqual(c({ a: 'A', b: 'C', rel: 'apart', nearM: 15 }, FACTS), { status: 'met', why: 'no shared wall or door' });
  assert.deepEqual(c({ a: 'A', b: 'C', rel: 'near', nearM: 10 }, FACTS), { status: 'met', why: 'route 9.0 m' });
  assert.deepEqual(c({ a: 'A', b: 'C', rel: 'near', nearM: 5 }, FACTS), { status: 'not met', why: 'route 9.0 m, over 5 m' });
  assert.deepEqual(c({ a: 'B', b: 'C', rel: 'near', nearM: 5 }, FACTS), { status: 'not evaluated', why: 'no route between them' });
  assert.deepEqual(c({ a: 'A', b: 'Z', rel: 'next', nearM: 15 }, FACTS), { status: 'not evaluated', why: 'a room is not in the model' });
  assert.deepEqual(c(null, FACTS), { status: 'not evaluated', why: 'not a relation' });
});

test('WO-08 the programme against the rooms: short, over, an area out of range, ok', () => {
  const items = [
    { id: 'p1', use: 'Bedroom', count: 2, areaMin: 10, areaMax: 16 },
    { id: 'p2', use: 'Bath', count: 1, areaMin: null, areaMax: null },
    { id: 'p3', use: 'Study', count: 1, areaMin: 8, areaMax: null },
    { id: 'p4', use: 'Kitchen', count: 1, areaMin: 6, areaMax: 20 }
  ];
  const rooms = [{ id: 'r1', use: 'Bedroom', area: 12 }, { id: 'r2', use: 'Bath', area: 5 }, { id: 'r3', use: 'Bath', area: 4 },
    { id: 'r4', use: 'Study', area: 7 }, { id: 'r5', use: 'Kitchen', area: 15 }, null];
  assert.deepEqual(fn('bimIntMatch')(items, rooms), [
    { id: 'p1', use: 'Bedroom', need: 2, have: 1, rooms: ['r1'], offArea: [], status: 'short' },
    { id: 'p2', use: 'Bath', need: 1, have: 2, rooms: ['r2', 'r3'], offArea: [], status: 'over' },
    { id: 'p3', use: 'Study', need: 1, have: 1, rooms: ['r4'], offArea: ['r4'], status: 'area' },
    { id: 'p4', use: 'Kitchen', need: 1, have: 1, rooms: ['r5'], offArea: [], status: 'ok' }
  ]);
  assert.deepEqual(fn('bimIntMatch')(null, rooms), []);
});

test('WO-09 a width in metres against a minimum in inches: a measurement, not a finding', () => {
  const m = fn('bimIntMinWidth');
  assert.deepEqual([31.9, 32, 32.1].map((i) => m(i * 0.0254, 32)), ['below', 'meets', 'meets']);
  assert.equal(m(null, 32), 'not evaluated');
  assert.equal(m(0.9, undefined), 'not evaluated');
});
