/* Interiors I1 (V179, docs/work-orders/v179/SPEC.md): the pure functions of src/js/engine/bim/interiors.js
   (WO-01 to WO-09, read as text), then the facts from the model and the bubble layout of
   src/js/engine/bim/interiors-model.js (WO-10, WO-11, through the engine). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
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

test('WO-01 a programme item: text trimmed, count at least 1, the area range in order, unknowns null; the brief fields (program-to-plan, 2026-11-16)', () => {
  const full = { id: 'p1', use: 'Bedroom', count: 2, areaMin: 10, areaMax: 14, rationale: 'brief',
    building: '', level: null, group: '', status: 'unknown', source: '', params: {}, open: 'auto' };
  assert.deepEqual(fn('bimIntProgramItem')({ id: 'p1', use: ' Bedroom ', count: 2.7, areaMin: 14, areaMax: 10, rationale: 'brief' }), full);
  assert.deepEqual(fn('bimIntProgramItem')({ count: 0, areaMin: -1 }), { id: '', use: '', count: 1, areaMin: null, areaMax: null, rationale: '',
    building: '', level: null, group: '', status: 'unknown', source: '', params: {}, open: 'auto' });
  assert.deepEqual(fn('bimIntProgramItem')(null).count, 1);
  const b = fn('bimIntProgramItem')({ use: 'Waiting', building: ' Clinic ', level: 1.6, group: 'Public', status: 'confirmed', source: 'brief rev B',
    params: { privacy: 2, daylight: '3', noise: Infinity, 'bad key': 1 }, open: 'open' });
  assert.equal(b.building, 'Clinic'); assert.equal(b.level, 1); assert.equal(b.group, 'Public');
  assert.equal(b.status, 'confirmed'); assert.equal(b.source, 'brief rev B'); assert.equal(b.open, 'open');
  assert.deepEqual(b.params, { privacy: 2, 'bad key': 1 }, 'finite numbers kept, anything else dropped');
  const c = fn('bimIntProgramItem')({ level: -1, status: 'maybe', open: 'yes', params: [1, 2] });
  assert.equal(c.level, -1, 'a basement is a level'); assert.equal(c.status, 'unknown'); assert.equal(c.open, 'auto'); assert.deepEqual(c.params, {});
  assert.equal(fn('bimIntProgramItem')({ level: 'two' }).level, null);
});

test('WO-02 a relation: two different rooms; kind, relation, strength, reason and status defaulted', () => {
  assert.deepEqual(fn('bimIntRelation')({ a: 'Kitchen', b: 'Dining', kind: 'required', rel: 'near', nearM: 6 }),
    { a: 'Kitchen', b: 'Dining', kind: 'required', rel: 'near', nearM: 6, strength: 2, reason: '', status: 'approved' });
  assert.deepEqual(fn('bimIntRelation')({ a: 'x', b: 'y', kind: 'must', rel: 'beside', nearM: -2 }),
    { a: 'x', b: 'y', kind: 'desired', rel: 'next', nearM: 15, strength: 2, reason: '', status: 'approved' });
  assert.equal(fn('bimIntRelation')({ a: 'x', b: 'x' }), null);
  assert.equal(fn('bimIntRelation')({ a: 'x' }), null);
  ['access', 'visual', 'acoustic', 'secure', 'sequence'].forEach((r) => assert.equal(fn('bimIntRelation')({ a: 'x', b: 'y', rel: r }).rel, r));
  const s1 = fn('bimIntRelation')({ a: 'x', b: 'y', strength: 1, reason: ' staff route ', status: 'suggested' });
  assert.equal(s1.strength, 1); assert.equal(s1.reason, 'staff route'); assert.equal(s1.status, 'suggested');
  assert.equal(fn('bimIntRelation')({ a: 'x', b: 'y', strength: 3.0 }).strength, 3);
  assert.equal(fn('bimIntRelation')({ a: 'x', b: 'y', strength: 4 }).strength, 2);
  assert.equal(fn('bimIntRelation')({ a: 'x', b: 'y', strength: 1.5 }).strength, 2);
  assert.equal(fn('bimIntRelation')({ a: 'x', b: 'y', status: 'rejected' }).status, 'rejected');
  assert.equal(fn('bimIntRelation')({ a: 'x', b: 'y', status: 'ok' }).status, 'approved');
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
test('WO-07 next and apart from shared walls and doors; near from the route; access from a door; missing facts not evaluated', () => {
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
  // the relation kinds added by program-to-plan (2026-11-16): direct access needs a door; the rest are not measured yet
  assert.deepEqual(c({ a: 'C', b: 'B', rel: 'access', nearM: 15 }, FACTS), { status: 'met', why: 'a door between them' });
  assert.deepEqual(c({ a: 'A', b: 'B', rel: 'access', nearM: 15 }, FACTS), { status: 'not met', why: 'no door between them' });
  ['visual', 'acoustic', 'secure', 'sequence'].forEach((r) =>
    assert.deepEqual(c({ a: 'A', b: 'B', rel: r, nearM: 15 }, FACTS), { status: 'not evaluated', why: 'not measured in this phase' }));
  assert.deepEqual(c({ a: 'A', b: 'B', rel: 'next', nearM: 15, status: 'rejected' }, FACTS), { status: 'not evaluated', why: 'the relation was rejected' });
  assert.deepEqual(c({ a: 'A', b: 'Z', rel: 'visual', nearM: 15 }, FACTS), { status: 'not evaluated', why: 'a room is not in the model' });
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

// ---- WO-10, WO-11: bim/interiors-model.js, through the engine ----
import { loadEngine } from './helpers/engine.mjs';
const E = loadEngine();

test('WO-10 facts by use: a shared wall, a door, a route; one level only; the outside of each level apart', () => {
  const rooms = [
    { id: 'A', use: 'Kitchen', pts: A.pts, levelId: 'L0' },
    { id: 'B', use: 'Dining', pts: B.pts, levelId: 'L0' },
    { id: 'C', use: 'Office', pts: C.pts, levelId: 'L0' },
    { id: 'D', use: 'Bedroom', pts: A.pts, levelId: 'L1' }
  ];
  // a door in the wall between A and B at x 4.1, its dir along the wall (+z): left is -x (A), right is +x (B)
  const doors = [{ id: 'd1', center: [4.1, 2], dir: [0, 1], width: 0.9, levelId: 'L0' }];
  const r = E.bimIntFactsFrom(rooms, doors, 0.5);
  assert.deepEqual(r.facts.rooms, { Kitchen: 1, Dining: 1, Office: 1, Bedroom: 1 });
  near(r.facts.shared['Dining|Kitchen'], 4);
  near(r.facts.shared['Dining|Office'], 2);
  assert.equal(r.facts.shared['Bedroom|Kitchen'], undefined, 'another level shares nothing');
  assert.deepEqual(r.facts.doors, { 'Dining|Kitchen': 1 });
  near(r.facts.dist.Kitchen.Dining, 2.1 + 1.6, 1e-9);
  assert.equal(r.facts.dist.Kitchen.Office, undefined, 'no door to the office: no route');
  assert.deepEqual(E.bimIntCheck(E.bimIntRelation({ a: 'Kitchen', b: 'Dining', rel: 'near', nearM: 3 }), r.facts),
    { status: 'not met', why: 'route 3.7 m, over 3 m' });
  assert.deepEqual(E.bimIntCheck(E.bimIntRelation({ a: 'Office', b: 'Dining', rel: 'next' }), r.facts),
    { status: 'met', why: 'a shared wall' });
  assert.deepEqual(E.bimIntCheck(E.bimIntRelation({ a: 'Office', b: 'Dining', rel: 'access' }), r.facts),
    { status: 'not met', why: 'no door between them' });
});

test('WO-10 a programme read from a building: bad items and relations dropped, nothing written', () => {
  const b = { programme: { items: [{ id: 'p1', use: 'Kitchen' }, { use: 'no id' }], relations: [{ a: 'Kitchen', b: 'Kitchen' }, { a: 'Kitchen', b: 'Dining' }] } };
  const before = JSON.stringify(b);
  const P = E.bimIntProgOf(b);
  assert.deepEqual(P.items.map((x) => x.id), ['p1']);
  assert.equal(P.relations.length, 1);
  assert.equal(JSON.stringify(b), before);
  assert.deepEqual(E.bimIntProgOf(null), { items: [], relations: [] });
});

test('WO-11 the bubble layout: the same programme draws the same, circles do not overlap, apart is farther than next', () => {
  const items = [{ use: 'K', r: 2 }, { use: 'D', r: 2 }, { use: 'G', r: 2 }, { use: 'B', r: 1.5 }];
  const rels = [{ a: 'K', b: 'D', rel: 'next' }, { a: 'B', b: 'G', rel: 'apart' }];
  const P = E.bimIntBubbleLayout(items, rels), Q = E.bimIntBubbleLayout(items, rels);
  assert.deepEqual(P, Q);
  const d = (i, j) => Math.hypot(P[i].x - P[j].x, P[i].y - P[j].y);
  for (let i = 0; i < 4; i++) for (let j = i + 1; j < 4; j++) assert.ok(d(i, j) >= P[i].r + P[j].r - 1e-3, i + ' overlaps ' + j);
  assert.ok(d(3, 2) - 3.5 > d(0, 1) - 4, 'apart is farther than next');
  assert.deepEqual(E.bimIntBubbleLayout([], []), []);
});
