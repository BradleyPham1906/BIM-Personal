/* V223's work-order tests (docs/work-orders/v223/SPEC.md, WO-01 to WO-03): the pure functions of src/js/engine/bim/procurement.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v223/v223.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v223/v223.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimCpIso", "bimCpDate", "bimCpWorkdayBefore", "bimCpScores"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/procurement.js'), 'utf8');
  if (process.env.V223_REF) src += fs.readFileSync(process.env.V223_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/procurement.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// the research's CP4 fixture (docs/research/fixtures/cp4-cp5-fixture.py)
test('WO-01 an ISO date to a UTC time and back', () => {
  assert.equal(fn('bimCpDate')('2026-01-16'), Date.UTC(2026, 0, 16));
  assert.equal(fn('bimCpDate')('16/01/2026'), null);
  assert.equal(fn('bimCpIso')(Date.UTC(2026, 0, 8)), '2026-01-08', 'bimCpIso, written with WO-01');
});
test('WO-02 the order deadline: n working days before the need date, weekends and holidays skipped', () => {
  assert.equal(fn('bimCpWorkdayBefore')('2026-01-16', 5, ['2026-01-12']), '2026-01-08');
  assert.equal(fn('bimCpWorkdayBefore')('2026-01-19', 1, []), '2026-01-16', 'Monday to Friday');
  assert.equal(fn('bimCpWorkdayBefore')('2026-01-16', 0, []), '2026-01-16');
  assert.equal(fn('bimCpWorkdayBefore')('soon', 2, []), null);
});
test('WO-03 a drawing-intake check\'s precision and recall (the toy 0.8 and 0.8)', () => {
  assert.deepEqual(fn('bimCpScores')(8, 2, 2), { precision: 0.8, recall: 0.8 });
  assert.deepEqual(fn('bimCpScores')(0, 0, 0), { precision: null, recall: null });
});
