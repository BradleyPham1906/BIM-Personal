/* V239's work-order tests (docs/work-orders/v239/SPEC.md): the pure functions of src/js/engine/structure/floor-loads.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v239/v239.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v239/v239.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text.
   Expected numbers come from the research's worked examples (docs/research/research-physical-world/ and
   docs/research/experiments/physical-world/), not from the implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimLiveKll', 'bimLiveReduce', 'bimRoofLive'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/structure/floor-loads.js'), 'utf8');
  if (process.env.V239_REF) src += fs.readFileSync(process.env.V239_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/structure/floor-loads.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 KLL by the member\'s kind (Table 4.7-1), 1 for anything else', () => {
  const k = fn('bimLiveKll');
  assert.equal(k('interior column'), 4); assert.equal(k('exterior column'), 4);
  assert.equal(k('edge column cantilever'), 3); assert.equal(k('corner column cantilever'), 2);
  assert.equal(k('edge beam'), 2); assert.equal(k('interior beam'), 2);
  assert.equal(k('one-way slab'), 1); assert.equal(k(''), 1); assert.equal(k('toString'), 1); assert.equal(k(undefined), 1);
});
test('WO-02 live load reduction: the research\'s office cases (Lo 2.40 kPa)', () => {
  const r = fn('bimLiveReduce');
  near(r(2.40, 4, 128, 2).L, 1.08473, 5e-5); assert.equal(r(2.40, 4, 128, 2).rule, 'reduced');
  near(r(2.40, 4, 64, 1).L, 1.28551, 5e-5);
  near(r(2.40, 2, 32, 1).L, 1.97100, 5e-5);
  near(r(2.40, 4, 320, 5).L, 0.96, 1e-12, 'the 0.4 floor for two or more floors');
  near(r(2.40, 4, 1000, 1).L, 1.20, 1e-12, 'the 0.5 floor for one floor');
});
test('WO-02 the exceptions: small areas, heavy loads, garages, not reducible', () => {
  const r = fn('bimLiveReduce');
  assert.deepEqual(r(2.40, 2, 16, 1), { L: 2.40, rule: 'small' });
  assert.equal(r(2.40, 2, 18.58, 1).rule, 'reduced', 'KLL AT = 37.16 exactly is reduced');
  assert.deepEqual(r(2.40, 2, 18.57, 1), { L: 2.40, rule: 'small' });
  near(r(7.18, 4, 128, 2).L, 5.744, 1e-12); assert.equal(r(7.18, 4, 128, 2).rule, 'heavy');
  assert.deepEqual(r(7.18, 4, 128, 1), { L: 7.18, rule: 'heavy' });
  assert.deepEqual(r(4.79, 4, 128, 1).rule, 'reduced', '4.79 kPa is not above the limit');
  near(r(1.92, 4, 500, 3, 'garage').L, 1.536, 1e-12); assert.equal(r(1.92, 4, 500, 3, 'garage').rule, 'garage');
  assert.deepEqual(r(1.92, 4, 500, 1, 'garage'), { L: 1.92, rule: 'garage' });
  assert.deepEqual(r(4.79, 4, 500, 3, 'none'), { L: 4.79, rule: 'none' });
  assert.ok(r(-1, 4, 10, 1).error); assert.ok(r(2.4, 0, 10, 1).error); assert.ok(r(2.4, 4, NaN, 1).error);
});
test('WO-03 roof live load: R1 by area, R2 by slope, kept between 0.58 and 0.96 kPa', () => {
  const r = fn('bimRoofLive');
  near(r(0.96, 10, 0), 0.96, 1e-12);
  near(r(0.96, 30, 0), 0.96 * (1.2 - 0.33), 1e-12);
  near(r(0.96, 30, 0.5), 0.96 * 0.87 * 0.9, 1e-12, 'F = 6 in/ft gives R2 0.9');
  near(r(0.96, 570 * 0.09290304, 5 / 12), 0.58, 1e-12, 'ENERCALC\'s case, held at the 12 psf minimum');
  near(r(0.96, 60, 1), 0.58, 1e-12);
  near(r(0.96, 18.58, 0), 0.96, 1e-12); near(r(0.96, 55.74, 0), 0.58, 1e-12, '0.6 x 0.96 = 0.576 is held at 0.58'); near(r(1.2, 55.74, 0), 0.72, 1e-12, 'R1 = 0.6 at 55.74 m2');
  near(r(0.96, 10, 4 / 12), 0.96, 1e-12, 'F = 4 exactly keeps R2 = 1');
  assert.ok(Number.isNaN(r(0.96, -1, 0))); assert.ok(Number.isNaN(r(0.96, 10, -0.1)));
});
