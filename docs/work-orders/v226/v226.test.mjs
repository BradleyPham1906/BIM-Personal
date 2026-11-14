/* V226's work-order tests (docs/work-orders/v226/SPEC.md, WO-01 to WO-03): the pure functions of src/js/engine/structure/penndot-input.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v226/v226.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v226/v226.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimPdName", "bimPdShared", "bimPdStOrder"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/structure/penndot-input.js'), 'utf8');
  if (process.env.V226_REF) src += fs.readFileSync(process.env.V226_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/structure/penndot-input.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// docs/research/penndot/PENNDOT_INPUT_SPEC.md: PSLRFD 44 commands, STLRFD 57, 23 shared; DPL means different things
test('WO-01 a command\'s meaning depends on the program: the DPL trap', () => {
  assert.equal(fn('bimPdName')('PS', 'DPL'), 'Drape Point Location');
  assert.equal(fn('bimPdName')('ST', 'DPL'), 'Design Plate Location');
  assert.equal(fn('bimPdName')('PS', 'BDM'), 'Beam Dimensions');
  assert.equal(fn('bimPdName')('PS', 'DRB'), null, 'a steel command in the prestressed program');
  assert.equal(fn('bimPdName')('XX', 'CFG'), null);
});
test('WO-02 the shared core: 23 commands both programs have', () => {
  assert.deepEqual(fn('bimPdShared')(), ['CDF', 'CFG', 'CLD', 'CTL', 'DLD', 'DPL', 'GEO', 'LDF', 'OAN', 'OIN', 'ORF', 'OSC', 'PLD', 'SAL', 'SID', 'SKW', 'SLB', 'SLL', 'SPL', 'SST', 'TTL', 'UDF', 'URF']);
});
test('WO-03 STLRFD commands in the manual\'s section order', () => {
  assert.deepEqual(fn('bimPdStOrder')(['CFG', 'TTL', 'GEO', 'SPL', 'MAT', 'OIN']), { ok: true });
  assert.deepEqual(fn('bimPdStOrder')(['CFG', 'GEO', 'TTL']), { ok: false, why: 'out of the manual\'s order: TTL' });
  assert.deepEqual(fn('bimPdStOrder')(['CFG', 'BDM']), { ok: false, why: 'not an STLRFD command: BDM' });
});
