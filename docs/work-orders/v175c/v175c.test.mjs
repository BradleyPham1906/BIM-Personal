/* V175c's work-order tests: the pure functions of src/js/engine/sheets/layouts.js (WO-01 to WO-05).

   Outside tests/unit/ while the work orders are open, so `npm test` and CI stay green on main. Run them with:
     node --test docs/work-orders/v175c/v175c.test.mjs
   One work order's cases only (WO-02, say):
     node --test --test-name-pattern="WO-02" docs/work-orders/v175c/v175c.test.mjs
   A function not built yet fails its own cases and no others. When all five pass, Claude moves this file to
   tests/unit/layouts.test.mjs (WO-06). The functions are pure and use no engine name: the file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimLyNextNumber', 'bimLyNumberValid', 'bimLyLabel', 'bimLyTabs', 'bimLyDupNumbers'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/sheets/layouts.js'), 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const L = load();
const fn = (n) => { assert.equal(typeof L[n], 'function', n + ' is not built yet in src/js/engine/sheets/layouts.js'); return L[n]; };

/* ---------------- WO-01 bimLyNextNumber ---------------- */
test('WO-01 the next number after the highest of that prefix', () => {
  assert.equal(fn('bimLyNextNumber')(['A101', 'A103', 'A102'], 'A'), 'A104');
});
test('WO-01 none yet starts at 101', () => {
  assert.equal(fn('bimLyNextNumber')([], 'A'), 'A101');
  assert.equal(fn('bimLyNextNumber')(['P7', 'x', ''], 'A'), 'A101');
});
test('WO-01 a number below 100 does not lower the start', () => {
  assert.equal(fn('bimLyNextNumber')(['A5', 'A99'], 'A'), 'A101');
});
test('WO-01 the prefix is matched without case and spaces are trimmed', () => {
  assert.equal(fn('bimLyNextNumber')([' a110 ', 'A109'], 'A'), 'A111');
});
test('WO-01 another prefix keeps its own series', () => {
  assert.equal(fn('bimLyNextNumber')(['A101', 'P101', 'P102'], 'P'), 'P103');
});
test('WO-01 a number with more after its digits is not counted', () => {
  assert.equal(fn('bimLyNextNumber')(['A101', 'A150b', 'A1.5'], 'A'), 'A102');
});
test('WO-01 not a list, or null entries, are left out', () => {
  assert.equal(fn('bimLyNextNumber')(null, 'A'), 'A101');
  assert.equal(fn('bimLyNextNumber')(['A101', null, 7], 'A'), 'A102');
});

/* ---------------- WO-02 bimLyNumberValid ---------------- */
test('WO-02 a good number is kept, trimmed, its inner spaces made one', () => {
  assert.equal(fn('bimLyNumberValid')('  A-101  '), 'A-101');
  assert.equal(fn('bimLyNumberValid')('S  2.1'), 'S 2.1');
});
test('WO-02 at most 12 characters', () => {
  assert.equal(fn('bimLyNumberValid')('ABCDEFGHIJKLMNOP'), 'ABCDEFGHIJKL');
});
test('WO-02 only letters, digits, space, dot, dash and underscore', () => {
  assert.equal(fn('bimLyNumberValid')('A<101>'), '');
  assert.equal(fn('bimLyNumberValid')('A_1.2-3'), 'A_1.2-3');
});
test('WO-02 empty or not a string gives an empty string', () => {
  assert.equal(fn('bimLyNumberValid')('   '), '');
  assert.equal(fn('bimLyNumberValid')(101), '');
  assert.equal(fn('bimLyNumberValid')(null), '');
});

/* ---------------- WO-03 bimLyLabel ---------------- */
test('WO-03 number and name', () => {
  assert.equal(fn('bimLyLabel')('A101', 'Site plan'), 'A101 - Site plan');
});
test('WO-03 one of the two alone', () => {
  assert.equal(fn('bimLyLabel')('A101', ''), 'A101');
  assert.equal(fn('bimLyLabel')('', 'Site plan'), 'Site plan');
  assert.equal(fn('bimLyLabel')(null, '  Site plan '), 'Site plan');
});
test('WO-03 neither gives Layout', () => {
  assert.equal(fn('bimLyLabel')('', ''), 'Layout');
  assert.equal(fn('bimLyLabel')(undefined, null), 'Layout');
});

/* ---------------- WO-04 bimLyTabs ---------------- */
const SEQ = [{ t: 'sheet', id: 's1', num: 'A101', name: 'Plan' }, { t: 'board', id: 'b1', num: 'A102', name: 'Climate and risk' },
  { t: 'board', id: 'b2', num: '', name: 'Moodboard' }];
test('WO-04 a tab a layout, in order, with its label and kind', () => {
  assert.deepEqual(fn('bimLyTabs')(SEQ, 'b1'), [
    { id: 's1', t: 'sheet', label: 'A101 - Plan', on: false },
    { id: 'b1', t: 'board', label: 'A102 - Climate and risk', on: true },
    { id: 'b2', t: 'board', label: 'Moodboard', on: false }]);
});
test('WO-04 no layout on screen: none is on; not a list gives none', () => {
  assert.equal(fn('bimLyTabs')(SEQ, null).filter((x) => x.on).length, 0);
  assert.deepEqual(fn('bimLyTabs')(null, 's1'), []);
});
test('WO-04 the list given is not changed', () => {
  const C = JSON.parse(JSON.stringify(SEQ));
  fn('bimLyTabs')(C, 's1');
  assert.deepEqual(C, SEQ);
});

/* ---------------- WO-05 bimLyDupNumbers ---------------- */
test('WO-05 the numbers used more than once, each once, in the order first seen', () => {
  assert.deepEqual(fn('bimLyDupNumbers')([{ num: 'A102' }, { num: 'A101' }, { num: 'a102 ' }, { num: 'A101' }, { num: 'A103' }]), ['A102', 'A101']);
});
test('WO-05 empty numbers are not duplicates; none gives none', () => {
  assert.deepEqual(fn('bimLyDupNumbers')([{ num: '' }, { num: '' }, { num: null }, {}]), []);
  assert.deepEqual(fn('bimLyDupNumbers')([]), []);
  assert.deepEqual(fn('bimLyDupNumbers')(null), []);
});
