/* V307's work-order tests (docs/work-orders/v307/SPEC.md): the pure functions of src/js/engine/io/ifc-save-types.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v307/v307.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v307/v307.test.mjs
   A function not built yet fails its own cases and no others. The files are read as text: ifc-save-types.js, with
   what it may use from io/ifc-review.js (the GlobalId codec) and bim/ifc-identity.js (V305's bimIfcGuidNew: V305 WO-01
   comes first). The type classes are IFC4's (IfcWallType ... IfcFootingType); the predefined type rule is SPEC 4. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimIfcTypeClassOf', 'bimIfcTypePredefinedDefault', 'bimIfcEnsureTypeIdentity', 'bimIfcPredefinedPair',
  'bimIfcSaveTypes', 'bimTorGuidValid', 'bimTorGuidToHex', 'bimIfcGuidNew'];
function strip(t) { return t.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n'); }
function load() {
  let src = ['src/js/engine/io/ifc-review.js', 'src/js/engine/bim/ifc-identity.js', 'src/js/engine/io/ifc-save-types.js']
    .map((f) => strip(fs.readFileSync(path.join(ROOT, f), 'utf8'))).join('\n');
  if (process.env.V307_REF) src += fs.readFileSync(process.env.V307_REF, 'utf8');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet (V307, or V305 WO-01 for bimIfcGuidNew)'); return X[n]; };
const seq = (start) => { let i = start || 0; return () => ((i++) % 256) / 256; };

test('WO-01 the IFC4 type class of each of the app\'s type categories', () => {
  const f = fn('bimIfcTypeClassOf');
  assert.equal(f('wall'), 'IfcWallType');
  assert.equal(f('floor'), 'IfcSlabType');
  assert.equal(f('ceiling'), 'IfcCoveringType');
  assert.equal(f('column'), 'IfcColumnType');
  assert.equal(f('beam'), 'IfcBeamType');
  assert.equal(f('footing'), 'IfcFootingType');
  assert.equal(f('stripfooting'), 'IfcFootingType');
  assert.equal(f('roof'), '', 'no type category for roofs in TYPE_CATS');
  assert.equal(f(''), '');
  assert.equal(f(undefined), '');
  assert.equal(f('hasOwnProperty'), '', 'only the categories, not what every object has');
});

test('WO-02 each category\'s default predefined type, as its instances\' (V306)', () => {
  const f = fn('bimIfcTypePredefinedDefault');
  assert.equal(f('wall'), 'STANDARD');
  assert.equal(f('floor'), 'FLOOR');
  assert.equal(f('ceiling'), 'CEILING');
  assert.equal(f('column'), 'COLUMN');
  assert.equal(f('beam'), 'BEAM');
  assert.equal(f('footing'), 'PAD_FOOTING');
  assert.equal(f('stripfooting'), 'STRIP_FOOTING');
  assert.equal(f('roof'), 'NOTDEFINED');
  assert.equal(f(null), 'NOTDEFINED');
});

test('WO-03 a type\'s identity: a lasting GlobalId and its predefined type, stamped once', () => {
  const f = fn('bimIfcEnsureTypeIdentity');
  const t = { id: 'wt-200', name: 'Generic 200mm', params: { thickness: 0.2 } };
  assert.equal(f(t, 'wall', seq(0)), t);
  assert.equal(X.bimTorGuidToHex(t.ifc.guid), '000102030405460788090a0b0c0d0e0f', 'made by bimIfcGuidNew');
  assert.equal(t.ifc.predefined, 'STANDARD');
  const g = t.ifc.guid;
  f(t, 'wall', seq(99));
  assert.equal(t.ifc.guid, g, 'kept');
  // the type's own predefined type is kept when it is a non-empty string
  const s = { id: 'x', ifc: { predefined: 'SHEAR', note: 'kept' } };
  f(s, 'wall', seq(0));
  assert.equal(s.ifc.predefined, 'SHEAR');
  assert.equal(s.ifc.note, 'kept');
  assert.ok(X.bimTorGuidValid(s.ifc.guid));
  const u = { id: 'y', ifc: { guid: 'bad', predefined: '' } };
  f(u, 'floor', seq(0));
  assert.ok(X.bimTorGuidValid(u.ifc.guid));
  assert.equal(u.ifc.predefined, 'FLOOR');
  assert.equal(f(null, 'wall', seq(0)), null);
});

test('WO-04 where the predefined type is written: on the type, and on the element only where it differs', () => {
  const f = fn('bimIfcPredefinedPair');
  assert.deepEqual(f('STANDARD', 'STANDARD'), { type: 'STANDARD', instance: null }, 'the same: the element inherits');
  assert.deepEqual(f('STANDARD', null), { type: 'STANDARD', instance: null });
  assert.deepEqual(f('STANDARD', ''), { type: 'STANDARD', instance: null });
  assert.deepEqual(f('STANDARD', 'SHEAR'), { type: 'STANDARD', instance: 'SHEAR' }, 'the element overrides its type');
  assert.deepEqual(f(null, 'SHEAR'), { type: null, instance: 'SHEAR' }, 'no type: the element\'s own');
  assert.deepEqual(f(null, null), { type: null, instance: 'NOTDEFINED' });
  assert.deepEqual(f('', 'COLUMN'), { type: null, instance: 'COLUMN' }, 'an empty type predefined is none');
});

test('WO-05 the types to write: only those used, with a class and a valid GlobalId, in their order', () => {
  const f = fn('bimIfcSaveTypes');
  const g1 = '3ZYW59sxj8lei475l7EhLU', g2 = '0DWNLFS3f90xUoIMNC0Sga', g3 = '2GNgSHJ5j9BRUjqT$7tE8w';
  const types = [
    { id: 'a', cat: 'wall', name: 'Wall 200', ifc: { guid: g1, predefined: 'STANDARD' } },
    { id: 'b', cat: 'floor', name: 'Slab 250', ifc: { guid: g2, predefined: 'FLOOR' } },
    { id: 'c', cat: 'wall', name: 'Unused', ifc: { guid: g3, predefined: 'STANDARD' } },
    { id: 'd', cat: 'roof', name: 'No class', ifc: { guid: g3 } },
    { id: 'e', cat: 'column', name: 'No identity' }];
  const used = { a: true, b: true, d: true, e: true };
  assert.deepEqual(f(types, used), [
    { id: 'a', guid: g1, cls: 'IfcWallType', name: 'Wall 200', predefined: 'STANDARD' },
    { id: 'b', guid: g2, cls: 'IfcSlabType', name: 'Slab 250', predefined: 'FLOOR' }]);
  // a missing predefined type is the category's default; a missing name is the id
  assert.deepEqual(f([{ id: 'z', cat: 'beam', ifc: { guid: g1 } }], { z: true }),
    [{ id: 'z', guid: g1, cls: 'IfcBeamType', name: 'z', predefined: 'BEAM' }]);
  assert.deepEqual(f(types, {}), []);
  assert.deepEqual(f(null, used), []);
});
