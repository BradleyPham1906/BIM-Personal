/* V305's work-order tests (docs/work-orders/v305/SPEC.md): the pure functions of src/js/engine/bim/ifc-identity.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v305/v305.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v305/v305.test.mjs
   A function not built yet fails its own cases and no others. The files are read as text: ifc-identity.js, with the
   GlobalId codec it may use from io/ifc-review.js (bimTorGuidFromHex, bimTorGuidToHex, bimTorGuidValid, tested in
   tests/unit/thatopen.test.mjs against IfcOpenShell's guid.py). Expected values come from RFC 4122 (version 4) and the
   rules in the SPEC, not from an implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimIfcGuidNew', 'bimIfcEnsureIdentity', 'bimIfcSegmentGuids', 'bimIfcForgetIdentity', 'bimIfcSpatialIds',
  'bimIfcDedupe', 'bimTorGuidFromHex', 'bimTorGuidToHex', 'bimTorGuidValid'];
function strip(t) { return t.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n'); }
function load() {
  let src = strip(fs.readFileSync(path.join(ROOT, 'src/js/engine/io/ifc-review.js'), 'utf8')) +
    strip(fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/ifc-identity.js'), 'utf8'));
  if (process.env.V305_REF) src += fs.readFileSync(process.env.V305_REF, 'utf8');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/ifc-identity.js'); return X[n]; };
/* a seeded rand: 0, 1/256, 2/256, ... so byte i is i (mod 256) before the version and variant bits */
const seq = (start) => { let i = start || 0; return () => ((i++) % 256) / 256; };
const VALID = (g) => X.bimTorGuidValid(g);

test('WO-01 a new GlobalId: 16 bytes from rand, RFC 4122 version 4 and variant bits, compressed to 22 characters', () => {
  const f = fn('bimIfcGuidNew');
  // bytes 0..15; byte 6 = (6 & 0x0f) | 0x40 = 0x46; byte 8 = (8 & 0x3f) | 0x80 = 0x88
  const g = f(seq(0));
  assert.equal(X.bimTorGuidToHex(g), '00010203040546078809' + '0a0b0c0d0e0f');
  assert.ok(VALID(g));
  // the version nibble and variant bits hold for any bytes: 0xff everywhere gives 4f and bf
  const h = X.bimTorGuidToHex(f(() => 0.999999));
  assert.equal(h, 'ffffffffffff4fffbfffffffffffffff');
  // rand outside [0, 1) and not a number is clamped: 1 or more is the top byte, below 0 or NaN is 0
  assert.equal(X.bimTorGuidToHex(f(() => 7)), h);
  assert.equal(X.bimTorGuidToHex(f(() => -3)), '000000000000400080' + '00000000000000');
  assert.equal(X.bimTorGuidToHex(f(() => NaN)), '000000000000400080' + '00000000000000');
  // no rand given: Math.random, still a valid version 4 GlobalId, and two in a row differ
  const a = f(), b = f();
  assert.ok(VALID(a) && VALID(b) && a !== b);
  assert.match(X.bimTorGuidToHex(a), /^[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}$/);
});

test('WO-02 an element\'s identity: kept once made, an imported GlobalId adopted, never replaced', () => {
  const f = fn('bimIfcEnsureIdentity');
  const b = { type: 'wall' }, r = f(b, seq(0));
  assert.equal(r, b, 'the same record, stamped');
  assert.ok(VALID(b.ifc.guid));
  assert.equal(X.bimTorGuidToHex(b.ifc.guid), '00010203040546078809' + '0a0b0c0d0e0f');
  const first = b.ifc.guid;
  f(b, seq(100));
  assert.equal(b.ifc.guid, first, 'a valid GlobalId is never replaced');
  // an imported element: its IFC GlobalId (bim.guid) becomes its identity
  const imp = { type: 'ifc', guid: '3ZYW59sxj8lei475l7EhLU' };
  f(imp, seq(0));
  assert.equal(imp.ifc.guid, '3ZYW59sxj8lei475l7EhLU');
  // what else bim.ifc holds is kept; an invalid GlobalId there is replaced
  const c = { type: 'column', ifc: { guid: 'not-a-guid', cls: 'IfcColumn', predefined: 'PILASTER' } };
  f(c, seq(0));
  assert.ok(VALID(c.ifc.guid));
  assert.equal(c.ifc.cls, 'IfcColumn');
  assert.equal(c.ifc.predefined, 'PILASTER');
  // an imported GlobalId that is not valid is not adopted
  const d = { guid: 'xyz' };
  f(d, seq(0));
  assert.ok(VALID(d.ifc.guid) && d.ifc.guid !== 'xyz');
  assert.equal(f(null, seq(0)), null);
  assert.equal(f(undefined, seq(0)), null);
});

test('WO-03 a wall\'s segments: the first is the wall\'s own GlobalId, the rest kept in order, made as needed', () => {
  const f = fn('bimIfcSegmentGuids');
  const b = { type: 'wall' };
  const s3 = f(b, 3, seq(0));
  assert.equal(s3.length, 3);
  assert.equal(s3[0], b.ifc.guid, 'segment 0 is the wall itself');
  assert.deepEqual(b.ifc.segGuids, s3, 'kept on the record');
  assert.ok(s3.every(VALID));
  assert.equal(new Set(s3).size, 3, 'all different');
  // more segments: the first three are kept, the fourth and fifth made
  const s5 = f(b, 5, seq(50));
  assert.deepEqual(s5.slice(0, 3), s3);
  assert.equal(new Set(s5).size, 5);
  // fewer: cut to length, the kept ones unchanged
  assert.deepEqual(f(b, 2, seq(0)), s3.slice(0, 2));
  assert.deepEqual(b.ifc.segGuids, s3.slice(0, 2));
  // an invalid or repeated entry is replaced, in its place
  b.ifc.segGuids = [b.ifc.guid, 'bad', s3[1], s3[1]];
  const s4 = f(b, 4, seq(200));
  assert.equal(s4[0], b.ifc.guid);
  assert.ok(VALID(s4[1]) && s4[1] !== 'bad');
  assert.equal(s4[2], s3[1]);
  assert.notEqual(s4[3], s3[1], 'a repeat is not kept');
  assert.equal(new Set(s4).size, 4);
  // no segments: an empty list; a record without identity gets one first
  const e = {};
  assert.deepEqual(f(e, 0, seq(0)), []);
  assert.ok(VALID(e.ifc.guid));
  assert.deepEqual(e.ifc.segGuids, []);
  assert.deepEqual(f(null, 3, seq(0)), []);
});

test('WO-04 a copy forgets its identity, and keeps everything else', () => {
  const f = fn('bimIfcForgetIdentity');
  const b = { type: 'wall', guid: '3ZYW59sxj8lei475l7EhLU', thickness: 0.2,
    ifc: { guid: '0000000000000000000000', segGuids: ['0000000000000000000000'], openingGuid: '1111111111111111111111', cls: 'IfcWall', predefined: 'SHEAR' } };
  const r = f(b);
  assert.equal(r, b);
  assert.deepEqual(b, { type: 'wall', thickness: 0.2, ifc: { cls: 'IfcWall', predefined: 'SHEAR' } });
  // nothing left in ifc: ifc goes
  const c = { type: 'door', ifc: { guid: '0000000000000000000000', openingGuid: '1111111111111111111111' } };
  f(c);
  assert.deepEqual(c, { type: 'door' });
  const d = { type: 'slab' };
  assert.deepEqual(f(d), { type: 'slab' });
  assert.equal(f(null), null);
});

test('WO-05 the project, site, buildings and storeys: one GlobalId each, kept while they exist', () => {
  const f = fn('bimIfcSpatialIds');
  const a = f(null, ['lvl-0', 'lvl-1'], ['bldg-0'], seq(0));
  assert.deepEqual(Object.keys(a).sort(), ['buildings', 'levels', 'project', 'site']);
  assert.deepEqual(Object.keys(a.levels).sort(), ['lvl-0', 'lvl-1']);
  assert.deepEqual(Object.keys(a.buildings), ['bldg-0']);
  const all = [a.project, a.site, a.buildings['bldg-0'], a.levels['lvl-0'], a.levels['lvl-1']];
  assert.ok(all.every(VALID));
  assert.equal(new Set(all).size, 5);
  // made in this order: project, site, buildings in their order, levels in their order
  assert.equal(X.bimTorGuidToHex(a.project), '00010203040546078809' + '0a0b0c0d0e0f');
  // the next call keeps what is still there, drops what is gone, makes what is new; the input is not changed
  const before = JSON.stringify(a);
  const b = f(a, ['lvl-1', 'lvl-2'], ['bldg-0', 'bldg-1'], seq(7));
  assert.equal(JSON.stringify(a), before, 'the previous record is not changed');
  assert.equal(b.project, a.project);
  assert.equal(b.site, a.site);
  assert.equal(b.levels['lvl-1'], a.levels['lvl-1']);
  assert.equal(b.levels['lvl-0'], undefined);
  assert.ok(VALID(b.levels['lvl-2']) && VALID(b.buildings['bldg-1']));
  assert.equal(new Set([b.project, b.site, b.buildings['bldg-0'], b.buildings['bldg-1'], b.levels['lvl-1'], b.levels['lvl-2']]).size, 6);
  // an invalid one in the previous record is made again; no levels or buildings: empty maps
  const c = f({ project: 'bad', site: a.site, buildings: {}, levels: {} }, [], [], seq(0));
  assert.ok(VALID(c.project) && c.project !== 'bad');
  assert.equal(c.site, a.site);
  assert.deepEqual(c.levels, {});
  assert.deepEqual(c.buildings, {});
});

test('WO-06 GlobalIds made unique before a save: first one kept, repeats and missing ones made', () => {
  const f = fn('bimIfcDedupe');
  const g1 = '3ZYW59sxj8lei475l7EhLU', g2 = '0DWNLFS3f90xUoIMNC0Sga';
  const items = [{ id: 'a', guid: g1 }, { id: 'b', guid: g2 }, { id: 'c', guid: g1 }, { id: 'd' }, { id: 'e', guid: 'bad' }];
  const copy = JSON.stringify(items);
  const r = f(items, seq(0));
  assert.equal(JSON.stringify(items), copy, 'the items are not changed');
  assert.equal(r.guids.a, g1, 'the first keeps it');
  assert.equal(r.guids.b, g2);
  assert.ok(VALID(r.guids.c) && r.guids.c !== g1, 'the copy gets a new one');
  assert.ok(VALID(r.guids.d) && VALID(r.guids.e));
  assert.equal(r.repeated, 1);
  assert.equal(r.made, 3, 'c (repeated), d (missing), e (invalid)');
  assert.equal(new Set(Object.values(r.guids)).size, 5);
  assert.deepEqual(f([], seq(0)), { guids: {}, made: 0, repeated: 0 });
  // an item without an id is left out
  const s = f([{ guid: g1 }, { id: 'x', guid: g1 }], seq(0));
  assert.deepEqual(Object.keys(s.guids), ['x']);
  assert.equal(s.guids.x, g1);
});
