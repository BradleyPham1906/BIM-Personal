/* V222's work-order tests (docs/work-orders/v222/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/bim/cost-plan.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v222/v222.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v222/v222.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimCpSlabNet", "bimCpLine", "bimCpAllocate", "bimCpBuckets"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/cost-plan.js'), 'utf8');
  if (process.env.V222_REF) src += fs.readFileSync(process.env.V222_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/cost-plan.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// the research's fixture (docs/research/experiments/cp0-cp3-fixture.py): a 6 x 4 m slab, 0.2 m, with a 1 x 1 m opening
const P = { waste: 0.05, matRate: 120, hoursPer: 0.5, labRate: 50 };
test('WO-01 a slab\'s net volume less its openings', () => {
  near(fn('bimCpSlabNet')(6, 4, 0.2, [{ w: 1, l: 1 }]), 4.6, 1e-12);
  near(fn('bimCpSlabNet')(6, 4, 0.2, []), 4.8, 1e-12);
  assert.equal(fn('bimCpSlabNet')(1, 1, 0.2, [{ w: 2, l: 2 }]), 0);
});
test('WO-02 a cost line: order quantity with waste, material, labour hours and cost', () => {
  const r = fn('bimCpLine')(4.6, P);
  near(r.order, 4.83, 1e-12); near(r.material, 579.6, 1e-9); near(r.hours, 2.3, 1e-12); near(r.labour, 115, 1e-9);
  near(r.total + 100, 794.6, 1e-9, 'with the fixture\'s 100 not from the model');
});
test('WO-03 an allocation: shares within 100%, the rest unallocated; over 100% refused (the CP4 fixture)', () => {
  const a = fn('bimCpAllocate')(1000, [0.6, 0.4]); near(a.assigned[0], 600, 1e-9); near(a.unallocated, 0, 1e-9);
  near(fn('bimCpAllocate')(1000, [0.6]).unallocated, 400, 1e-9);
  assert.deepEqual(fn('bimCpAllocate')(1000, [0.6, 0.6]), { error: 'invalid allocation' });
  assert.deepEqual(fn('bimCpAllocate')(1000, [-0.1]), { error: 'invalid allocation' });
});
test('WO-04 planned cost by working day: the fixture\'s two buckets add up to 794.6', () => {
  const b = fn('bimCpBuckets')([{ amount: 579.6, split: { day1: 0.5, day2: 0.5 } }, { amount: 115, split: { day1: 0.5, day2: 0.5 } }, { amount: 100, split: { day1: 1 } }]);
  near(b.day1 + b.day2, 794.6, 1e-9); near(b.day2, 347.3, 1e-9);
});
