/* V214's work-order tests (docs/work-orders/v214/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/bim/proforma.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v214/v214.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v214/v214.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimPfmLine", "bimPfmTotals", "bimPfmCost", "bimPfmMetrics"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/proforma.js'), 'utf8');
  if (process.env.V214_REF) src += fs.readFileSync(process.env.V214_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/proforma.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// the research's fixture (docs/research/experiments/notion-later-20261113): 100 flats at 1800 a month, 10,000 m2 retail at 30 a year
const LINES = [{ name: 'Residential', qty: 100, rate: 1800, periods: 12, vacancy: 0.05 }, { name: 'Retail', qty: 10000, rate: 30, vacancy: 0.10 }];
test('WO-01 one income line: gross and after vacancy', () => {
  assert.deepEqual(fn('bimPfmLine')(LINES[0]), { name: 'Residential', gross: 2160000, effective: 2052000 });
  assert.deepEqual(fn('bimPfmLine')({ qty: 2, rate: 5, vacancy: 3 }), { name: '', gross: 10, effective: 10 });
});
test('WO-02 totals and NOI (the fixture: 2,460,000 gross, 2,322,000 effective, 2,022,000 NOI)', () => {
  const t = fn('bimPfmTotals')(LINES, 300000);
  near(t.gross, 2460000, 1e-6); near(t.effective, 2322000, 1e-6); near(t.noi, 2022000, 1e-6); assert.equal(t.opex, 300000);
});
test('WO-03 the cost total, numbers only', () => {
  assert.equal(fn('bimPfmCost')([{ amount: 6e6 }, { amount: 14e6 }, { amount: 3e6 }, { amount: 1e6 }, { amount: 'x' }]), 24e6);
});
test('WO-04 yield on cost, value by capitalisation, profit and margin', () => {
  const m = fn('bimPfmMetrics')(2022000, 24e6, 0.06);
  near(m.yieldOnCost, 0.08425, 1e-12); near(m.value, 33700000, 1e-6); near(m.profit, 9700000, 1e-6); near(m.marginOnCost, 9.7 / 24, 1e-12);
  assert.deepEqual(fn('bimPfmMetrics')(100, 0, 0), { yieldOnCost: null, value: null, profit: null, marginOnCost: null });
});
