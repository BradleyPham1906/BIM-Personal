/* V275's work-order tests (docs/work-orders/v275/SPEC.md, WO-01 to WO-06): the pure functions of src/js/engine/views/explode-view.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v275/v275.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v275/v275.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimXvRanks', 'bimXvLevelOf', 'bimXvGap', 'bimXvOffset', 'bimXvOffsets', 'bimXvNext'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/views/explode-view.js'), 'utf8');
  if (process.env.V275_REF) src += fs.readFileSync(process.env.V275_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/views/explode-view.js'); return X[n]; };

// two buildings; levels listed out of order; an IFC storey; a level without height
const LEVELS = [
  { id: 'a2', name: 'Level 2', elev: 6, height: 3, buildingId: 'A' },
  { id: 'a0', name: 'Level 0', elev: 0, height: 3.5, buildingId: 'A' },
  { id: 'a1', name: 'Level 1', elev: 3, height: 3, buildingId: 'A' },
  { id: 'b0', name: 'Ground (IFC)', elev: 0, height: 4, buildingId: 'B' },
  { id: 'b1', name: 'First (IFC)', elev: 4, buildingId: 'B' }
];

test('WO-01 storeys ranked by elevation within each building', () => {
  assert.deepEqual(fn('bimXvRanks')(LEVELS), { a0: 0, a1: 1, a2: 2, b0: 0, b1: 1 });
  assert.deepEqual(fn('bimXvRanks')([{ id: 'x', elev: 3 }, { id: 'y', elev: 3 }, { id: 'z', elev: -3 }]), { z: 0, x: 1, y: 2 },
    'no building is one group; equal elevations keep their order');
  assert.deepEqual(fn('bimXvRanks')([]), {});
  assert.deepEqual(fn('bimXvRanks')(null), {});
});

test('WO-02 an element\'s storey: its own level, then the IFC storey name, then its height', () => {
  const F = fn('bimXvLevelOf');
  assert.equal(F({ levelId: 'a1', storey: 'First', minY: 99 }, LEVELS), 'a1', 'its own level wins');
  assert.equal(F({ levelId: 'gone', storey: 'First', minY: 0 }, LEVELS), 'b1', 'a level that no longer exists falls to the storey name');
  assert.equal(F({ storey: 'Ground', minY: 50 }, LEVELS), 'b0', 'IFC storeys are named "<storey> (IFC)"');
  assert.equal(F({ storey: 'Roof', minY: 3.02 }, LEVELS), 'a1', 'no such storey: by height, a slab 2 cm above a level is on it');
  assert.equal(F({ minY: 2.96 }, LEVELS), 'a1', 'within 5 cm below a level counts as on it');
  assert.equal(F({ minY: 2.9 }, LEVELS), 'a0');
  assert.equal(F({ minY: -4 }, LEVELS), 'a0', 'below every level: the lowest (first of equal lowest)');
  assert.equal(F({}, LEVELS), null, 'nothing to go by');
  assert.equal(F({ minY: 1 }, []), null);
});

test('WO-03 the gap is the tallest storey', () => {
  assert.equal(fn('bimXvGap')(LEVELS), 4);
  assert.equal(fn('bimXvGap')([{ id: 'x', elev: 0 }]), 3, 'no heights: 3 m');
  assert.equal(fn('bimXvGap')([{ id: 'x', elev: 0, height: -2 }, { id: 'y', elev: 0, height: NaN }]), 3);
  assert.equal(fn('bimXvGap')(null), 3);
});

test('WO-04 the offset: rank times gap times the amount, upward', () => {
  const O = fn('bimXvOffset');
  assert.deepEqual(O(2, 0.5, 4), [0, 4, 0]);
  assert.deepEqual(O(2, 1.7, 4), [0, 8, 0], 'the amount is at most 1');
  assert.deepEqual(O(2, -1, 4), [0, 0, 0], 'and at least 0');
  assert.deepEqual(O(null, 1, 4), [0, 0, 0], 'no storey: stays');
  assert.deepEqual(O(undefined, 1, 4), [0, 0, 0]);
  assert.deepEqual(O(0, 1, 4), [0, 0, 0]);
});

test('WO-05 every element\'s offset; the ground storey and unplaced elements are left out', () => {
  const items = [
    { id: 'w0', levelId: 'a0' }, { id: 'w2', levelId: 'a2' }, { id: 'c1', storey: 'First' },
    { id: 's1', minY: 3 }, { id: 'loose' }
  ];
  assert.deepEqual(fn('bimXvOffsets')(items, LEVELS, 0.5), { w2: [0, 4, 0], c1: [0, 2, 0], s1: [0, 2, 0] });
  assert.deepEqual(fn('bimXvOffsets')(items, LEVELS, 0), {}, 'collapsed: nothing moves');
  assert.deepEqual(fn('bimXvOffsets')([], LEVELS, 1), {});
});

test('WO-06 the explode state: toggle, set, collapse; never changed in place', () => {
  const N = fn('bimXvNext');
  assert.deepEqual(N(null, { type: 'toggle' }), { on: true, amount: 0.5 }, 'turned on from nothing: half way');
  assert.deepEqual(N({ on: false, amount: 0.8 }, { type: 'toggle' }), { on: true, amount: 0.8 }, 'turned on: the last amount');
  const s = { on: true, amount: 0.8 }, t = N(s, { type: 'toggle' });
  assert.deepEqual(t, { on: false, amount: 0.8 }, 'turned off: the amount kept');
  assert.deepEqual(s, { on: true, amount: 0.8 }, 'the old state is not changed');
  assert.notEqual(t, s);
  assert.deepEqual(N(s, { type: 'set', amount: 0.25 }), { on: true, amount: 0.25 });
  assert.deepEqual(N(s, { type: 'set', amount: 3 }), { on: true, amount: 1 });
  assert.deepEqual(N(s, { type: 'set', amount: 0 }), { on: false, amount: 0 }, 'set to 0 is off');
  assert.deepEqual(N(s, { type: 'collapse' }), { on: false, amount: 0 });
  assert.deepEqual(N(s, { type: 'nonsense' }), { on: true, amount: 0.8 });
});
