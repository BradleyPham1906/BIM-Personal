/* V213's work-order tests (docs/work-orders/v213/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/site-tools/generators.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v213/v213.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v213/v213.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimGenAchievable", "bimGenStoreys", "bimGenStalls", "bimGenParking", "bimGenLots"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/site-tools/generators.js'), 'utf8');
  if (process.env.V213_REF) src += fs.readFileSync(process.env.V213_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/site-tools/generators.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 the achievable area under FAR and coverage, plate by plate (the research\'s fixture)', () => {
  assert.deepEqual(fn('bimGenAchievable')(2000, 1.2, 0.5, 4), { plateCap: 1000, capacity: 4000, farLimit: 2400, achievable: 2400, plates: [1000, 1000, 400, 0] });
  assert.deepEqual(fn('bimGenAchievable')(1000, 3, 0.6, 2).plates, [600, 600]);
});
test('WO-02 storeys that fit an envelope height at a floor-to-floor', () => {
  assert.deepEqual(fn('bimGenStoreys')(14, 3.5), { storeys: 4, top: 14 });
  assert.deepEqual(fn('bimGenStoreys')(13.9, 3.5), { storeys: 3, top: 10.5 });
  assert.deepEqual(fn('bimGenStoreys')(10), { storeys: 2, top: 7 });
  assert.deepEqual(fn('bimGenStoreys')(0, 3), { storeys: 0, top: 0 });
});
test('WO-03 stalls a set of ratios asks for, rounded up', () => {
  assert.equal(fn('bimGenStalls')([{ qty: 100, per: 1, ratio: 1 }, { qty: 1000, per: 100, ratio: 2.5 }]), 125);
  assert.equal(fn('bimGenStalls')([{ qty: 30, per: 1, ratio: 0.5 }, { qty: 1, per: 0, ratio: 9 }]), 15);
  assert.equal(fn('bimGenStalls')([]), 0);
});
test('WO-04 90-degree stalls on double-loaded aisles in a rectangle, a single row in what is left', () => {
  assert.deepEqual(fn('bimGenParking')(52, 40), { perRow: 20, doubleModules: 2, singleRows: 0, stalls: 80 });
  assert.deepEqual(fn('bimGenParking')(52, 49.2), { perRow: 20, doubleModules: 2, singleRows: 1, stalls: 100 });
  assert.deepEqual(fn('bimGenParking')(10, 10, { w: 2.5, d: 5 }, 6), { perRow: 4, doubleModules: 0, singleRows: 0, stalls: 0 });
});
test('WO-05 lots along a frontage: as many as the target allows, equal widths', () => {
  assert.deepEqual(fn('bimGenLots')(100, 15), Array(6).fill(100 / 6));
  assert.deepEqual(fn('bimGenLots')(10, 15), [10]);
  assert.deepEqual(fn('bimGenLots')(0, 15), []);
});
