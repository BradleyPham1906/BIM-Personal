/* V228's work-order tests (docs/work-orders/v228/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/bim/generated-elements.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v228/v228.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v228/v228.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimGelKey", "bimGelShape", "bimGelReconcile", "bimGelOverrides", "bimGelApply"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/generated-elements.js'), 'utf8');
  if (process.env.V228_REF) src += fs.readFileSync(process.env.V228_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/generated-elements.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// a facade's windows are keyed by storey and bay, as the research's e03 names them
const K = (s, b) => 'g1|Facade:front/Floor:' + s + '/Bay:' + b + '/Window:0';
test('WO-01 a key from the generator and the path of rules and indexes; bad parts refused', () => {
  const key = fn('bimGelKey');
  assert.deepEqual(key('g1', [['Facade', 'front'], ['Floor', 3], ['Bay', 2], ['Window', 0]]), { key: K(3, 2) });
  assert.deepEqual(key('g1', [['Mass', 0]]), { key: 'g1|Mass:0' });
  assert.deepEqual(key('', [['Mass', 0]]), { error: 'bad generator id' });
  assert.deepEqual(key('g|1', [['Mass', 0]]), { error: 'bad generator id' });
  assert.deepEqual(key('g1', []), { error: 'empty path' });
  assert.deepEqual(key('g1', [['Mass', 0], ['Fa/cade', 1]]), { error: 'bad rule name at 1' });
  assert.deepEqual(key('g1', [['Mass', -1]]), { error: 'bad index at 0' });
  assert.deepEqual(key('g1', [['Mass', 1.5]]), { error: 'bad index at 0' });
  assert.deepEqual(key('g1', [['Mass', 'a:b']]), { error: 'bad index at 0' });
  assert.deepEqual(key('g1', [['Mass', '']]), { error: 'bad index at 0' });
});
test('WO-02 the shape of a key: number indexes become *, names stay', () => {
  const shape = fn('bimGelShape');
  assert.equal(shape(K(3, 2)), 'g1|Facade:front/Floor:*/Bay:*/Window:*');
  assert.equal(shape('g1|Mass:0'), 'g1|Mass:*');
  assert.equal(shape('g1|Side:north2/Bay:12'), 'g1|Side:north2/Bay:*');
  assert.equal(shape('nokey'), 'nokey');
});
test('WO-03 a new run against the elements already there: update, create, remove; duplicates', () => {
  const rec = fn('bimGelReconcile');
  const ex = [{ id: 'a', key: K(0, 0) }, { id: 'b', key: K(0, 1) }, { id: 'c', key: K(0, 2) }];
  const d0 = { key: K(0, 1), w: 1 }, d1 = { key: K(0, 0), w: 2 }, d2 = { key: K(0, 3), w: 3 };
  assert.deepEqual(rec(ex, [d0, d1, d2]), { update: [{ id: 'b', item: d0 }, { id: 'a', item: d1 }], create: [d2], remove: ['c'] });
  assert.deepEqual(rec([], [d0]), { update: [], create: [d0], remove: [] });
  assert.deepEqual(rec(ex, []), { update: [], create: [], remove: ['a', 'b', 'c'] });
  assert.deepEqual(rec(ex, [d0, { key: K(0, 1) }]), { error: 'duplicate key ' + K(0, 1) });
  // two elements already carrying one key: the first is kept, the second removed, before the unmatched ones
  assert.deepEqual(rec([{ id: 'a', key: K(0, 0) }, { id: 'z', key: K(0, 0) }, { id: 'c', key: K(0, 2) }], [d1]),
    { update: [{ id: 'a', item: d1 }], create: [], remove: ['z', 'c'] });
  assert.deepEqual(ex.map((e) => e.id), ['a', 'b', 'c']);
});
test('WO-04 overrides sorted: apply, dormant (the place is gone for now), listed (the rule is gone)', () => {
  const ov = fn('bimGelOverrides');
  const keys = [K(0, 0), K(0, 1), K(1, 0), K(1, 1)];
  const o1 = { key: K(1, 1), prop: 'w', value: 1.2 }, o2 = { key: K(1, 7), prop: 'w', value: 1.0 };
  const o3 = { key: 'g1|Facade:front/Floor:1/Balcony:0', prop: 'd', value: 1.5 }, o4 = { key: 'g2|Mass:0', prop: 'h', value: 3 };
  assert.deepEqual(ov([o1, o2, o3, o4], keys), { apply: [o1], dormant: [o2], listed: [o3, o4] });
  assert.deepEqual(ov([], keys), { apply: [], dormant: [], listed: [] });
  assert.deepEqual(ov([o1], []), { apply: [], dormant: [], listed: [o1] });
});
test('WO-05 an item with its overrides applied: a copy, the changed properties named', () => {
  const ap = fn('bimGelApply');
  const item = { key: K(1, 1), kind: 'window', props: { w: 0.8, h: 1.6 } };
  const r = ap(item, [{ key: K(1, 1), prop: 'w', value: 1.2 }, { key: K(0, 0), prop: 'h', value: 9 }, { key: K(1, 1), prop: 'sill', value: 1.0 }, { key: K(1, 1), prop: 'w', value: 1.4 }]);
  assert.deepEqual(r, { key: K(1, 1), kind: 'window', props: { w: 1.4, h: 1.6, sill: 1.0 }, ov: ['w', 'sill'] });
  assert.deepEqual(item.props, { w: 0.8, h: 1.6 });
  assert.deepEqual(ap({ key: 'g1|Mass:0' }, []), { key: 'g1|Mass:0', props: {}, ov: [] });
});
