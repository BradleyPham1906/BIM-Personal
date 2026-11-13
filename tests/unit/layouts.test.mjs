/* V175c step 1: the pure functions of src/js/engine/sheets/layouts.js (WO-01 to WO-05, built by Cline), then
   Claude's part on them (WO-06): a board's number kept and given, one series, the layouts' list. Moved here from
   docs/work-orders/v175c/v175c.test.mjs when the work orders were done. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadEngine } from './helpers/engine.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
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

/* ================= WO-06, Claude's part ================= */
const E = loadEngine();
const A3D = E.A3D;

test('a board keeps a good number and drops a bad one', () => {
  const P = E.bimPresValid({ boards: [{ kind: 'custom', id: 'board-c1', name: 'Mood', num: '  P 12 ' }, { kind: 'custom', id: 'board-c2', name: 'X', num: '<b>' }], order: [] });
  assert.equal(P.boards[0].num, 'P 12');
  assert.equal('num' in P.boards[1], false);
});

test('boards without a number get the next ones, after the sheets, in the set\'s order; sheets follow the same series', () => {
  A3D.sheets.length = 0;
  A3D.sheets.push({ id: 'sheet-1', number: 'A101', name: 'Plan', w: 420, h: 297, viewports: [] }, { id: 'sheet-2', number: 'A104', name: 'Sections', w: 420, h: 297, viewports: [] });
  A3D.pres = { boards: [{ id: 'board-c1', kind: 'custom', name: 'Second', figs: [] }, { id: 'board-c2', kind: 'custom', name: 'First', figs: [] }, { id: 'board-c3', kind: 'custom', name: 'Kept', figs: [], num: 'A110' }], order: ['board-c2', 'board-c1'] };
  const P = E.bimPresData();
  const num = (id) => P.boards.filter((b) => b.id === id)[0].num;
  assert.equal(num('board-c2'), 'A111', 'first in the set\'s order');
  assert.equal(num('board-c1'), 'A112');
  assert.equal(num('board-c3'), 'A110', 'a number already given is kept');
  assert.equal(E.bimNextSheetNumber(), 'A113', 'a new sheet follows the boards');
  const L = E.bimLyEntries();
  assert.deepEqual(L.map((e) => e.num), L.map((e) => e.t === 'sheet' ? A3D.sheets.filter((s) => s.id === e.id)[0].number : P.boards.filter((b) => b.id === e.id)[0].num));
  assert.deepEqual(E.bimLyDupNumbers(L), []);
  A3D.sheets.length = 0;
  A3D.pres = null;
});
