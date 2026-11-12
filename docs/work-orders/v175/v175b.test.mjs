/* V175b's work-order tests: the pure functions of src/js/engine/sheets/live-board.js (WO-01 to WO-10).

   Not under tests/unit/ while the work orders are open, so `npm test` and CI stay green on main. Run them with:
     node --test docs/work-orders/v175/v175b.test.mjs
   One work order's cases only (WO-03, say):
     node --test --test-name-pattern="WO-03" docs/work-orders/v175/v175b.test.mjs
   A function not built yet fails its own cases and no others. When all ten pass, Claude moves this file to
   tests/unit/live-board.test.mjs (WO-11).

   The file is read as text and its functions run on their own: they are pure, and bimLvFormat is the only
   engine name they may use (passed in from the engine). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadEngine } from '../../../tests/unit/helpers/engine.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimLbHist', 'bimLbPct', 'bimLbBars', 'bimLbSort', 'bimLbTotals', 'bimLbUnesc', 'bimLbKpiLabels',
  'bimLbKpiFind', 'bimLbTableHtml', 'bimLbHistSvg'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/sheets/live-board.js'), 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  const ret = 'return {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};';
  const E = loadEngine();
  return new Function('bimLvFormat', src + '\n' + ret)(E.bimLvFormat);
}
const B = load();
const fn = (n) => { assert.equal(typeof B[n], 'function', n + ' is not built yet in src/js/engine/sheets/live-board.js'); return B[n]; };

/* ---------------- WO-01 bimLbHist ---------------- */
test('WO-01 counts each digit into its bin', () => {
  assert.deepEqual(fn('bimLbHist')('0012', 4), [2, 1, 1, 0]);
});
test('WO-01 a dot (a roof cell) and digits past the last bin are left out', () => {
  assert.deepEqual(fn('bimLbHist')('0.1..9', 4), [1, 1, 0, 0]);
});
test('WO-01 an empty or missing string gives zeros', () => {
  assert.deepEqual(fn('bimLbHist')('', 3), [0, 0, 0]);
  assert.deepEqual(fn('bimLbHist')(null, 2), [0, 0]);
});
test('WO-01 other characters are left out', () => {
  assert.deepEqual(fn('bimLbHist')('0a1-1', 2), [1, 2]);
});

/* ---------------- WO-02 bimLbPct ---------------- */
test('WO-02 a share as a percentage to one decimal', () => {
  assert.equal(fn('bimLbPct')(1, 3), 33.3);
  assert.equal(fn('bimLbPct')(3, 3), 100);
  assert.equal(fn('bimLbPct')(0, 5), 0);
});
test('WO-02 no total, or not numbers, gives null', () => {
  assert.equal(fn('bimLbPct')(0, 0), null);
  assert.equal(fn('bimLbPct')(1, -2), null);
  assert.equal(fn('bimLbPct')('1', 2), null);
  assert.equal(fn('bimLbPct')(NaN, 2), null);
});

/* ---------------- WO-03 bimLbBars ---------------- */
test('WO-03 bars share the width, the tallest fills the height', () => {
  assert.deepEqual(fn('bimLbBars')([1, 2], 10, 4, 2), [{ x: 0, y: 2, w: 4, h: 2 }, { x: 6, y: 0, w: 4, h: 4 }]);
});
test('WO-03 values are rounded to two decimals', () => {
  const R = fn('bimLbBars')([1, 3, 2], 10, 9, 1);
  assert.deepEqual(R.map((r) => r.w), [2.67, 2.67, 2.67]);
  assert.deepEqual(R.map((r) => r.x), [0, 3.67, 7.33]);
  assert.deepEqual(R.map((r) => r.h), [3, 9, 6]);
  assert.deepEqual(R.map((r) => r.y), [6, 0, 3]);
});
test('WO-03 all zero gives flat bars; no counts gives none', () => {
  assert.deepEqual(fn('bimLbBars')([0, 0], 10, 4, 0), [{ x: 0, y: 4, w: 5, h: 0 }, { x: 5, y: 4, w: 5, h: 0 }]);
  assert.deepEqual(fn('bimLbBars')([], 10, 4, 2), []);
});

/* ---------------- WO-04 bimLbSort ---------------- */
const ROWS = [{ n: 'b', a: 20 }, { n: 'A', a: 5 }, { n: '', a: 12 }, { n: 'c', a: '' }, { n: 'a', a: 5 }];
test('WO-04 numbers sort as numbers, empty last', () => {
  assert.deepEqual(fn('bimLbSort')(ROWS, 'a', false).map((r) => r.n), ['A', 'a', '', 'b', 'c']);
});
test('WO-04 descending reverses the values, ties keep their order, empty still last', () => {
  assert.deepEqual(fn('bimLbSort')(ROWS, 'a', true).map((r) => r.n), ['b', '', 'A', 'a', 'c']);
});
test('WO-04 text sorts without case, empty last', () => {
  assert.deepEqual(fn('bimLbSort')(ROWS, 'n', false).map((r) => r.a), [5, 5, 20, '', 12]);
});
test('WO-04 the list given is not changed', () => {
  const L = ROWS.slice();
  fn('bimLbSort')(L, 'a', true);
  assert.deepEqual(L, ROWS);
});

/* ---------------- WO-05 bimLbTotals ---------------- */
test('WO-05 areas and counts are summed, other columns are empty', () => {
  const cols = [{ k: 'n', kind: 'text' }, { k: 'a', kind: 'area' }, { k: 'c', kind: 'count' }];
  const rows = [{ n: 'x', a: 10.5, c: 2 }, { n: 'y', a: 4, c: '' }, { n: 'z', a: '3', c: 1 }];
  assert.deepEqual(fn('bimLbTotals')(rows, cols), ['', 14.5, 3]);
});
test('WO-05 a column with no numbers is empty; no rows gives empties', () => {
  const cols = [{ k: 'a', kind: 'area' }];
  assert.deepEqual(fn('bimLbTotals')([{ a: '' }, { a: null }], cols), ['']);
  assert.deepEqual(fn('bimLbTotals')([], cols), ['']);
});

/* ---------------- WO-06 bimLbUnesc ---------------- */
test('WO-06 the five entities are read back', () => {
  assert.equal(fn('bimLbUnesc')('a &amp; b &lt;c&gt; &quot;d&quot; &#39;e&#39;'), 'a & b <c> "d" \'e\'');
});
test('WO-06 an escaped entity stays one level escaped', () => {
  assert.equal(fn('bimLbUnesc')('&amp;lt;'), '&lt;');
});
test('WO-06 not a string gives an empty string', () => {
  assert.equal(fn('bimLbUnesc')(null), '');
});

/* ---------------- WO-07 bimLbKpiLabels ---------------- */
const KP = ['<div class="a3d-clb-kpi" data-kpi="Lot area"><b>1</b></div>', '<div class="x">no label</div>',
  '<div class="a3d-clb-kpi" data-kpi="Heat &amp; cold">2</div>'];
test('WO-07 the labels, read back, skipping a card without one', () => {
  assert.deepEqual(fn('bimLbKpiLabels')(KP), ['Lot area', 'Heat & cold']);
});
test('WO-07 not a list gives an empty list', () => {
  assert.deepEqual(fn('bimLbKpiLabels')(null), []);
});

/* ---------------- WO-08 bimLbKpiFind ---------------- */
test('WO-08 the index in the list of the card with that label', () => {
  assert.equal(fn('bimLbKpiFind')(KP, 'Heat & cold'), 2);
  assert.equal(fn('bimLbKpiFind')(KP, 'Lot area'), 0);
});
test('WO-08 a label that is not there, or no list, gives -1', () => {
  assert.equal(fn('bimLbKpiFind')(KP, 'Heat &amp; cold'), -1);
  assert.equal(fn('bimLbKpiFind')(KP, 'Nope'), -1);
  assert.equal(fn('bimLbKpiFind')(null, 'Lot area'), -1);
});

/* ---------------- WO-09 bimLbTableHtml ---------------- */
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
test('WO-09 a head, rows and a foot', () => {
  assert.equal(fn('bimLbTableHtml')(['Name', 'Area'], [['A<1', '5 m2'], ['B', '7 m2']], ['Total', '12 m2'], esc),
    '<table class="a3d-clb-dtab"><thead><tr><th>Name</th><th>Area</th></tr></thead><tbody><tr><td>A&lt;1</td><td>5 m2</td></tr>' +
    '<tr><td>B</td><td>7 m2</td></tr></tbody><tfoot><tr><td>Total</td><td>12 m2</td></tr></tfoot></table>');
});
test('WO-09 a short row is filled, a long one cut; no foot when it is null', () => {
  assert.equal(fn('bimLbTableHtml')(['a', 'b'], [['1'], ['1', '2', '3']], null, esc),
    '<table class="a3d-clb-dtab"><thead><tr><th>a</th><th>b</th></tr></thead><tbody><tr><td>1</td><td></td></tr>' +
    '<tr><td>1</td><td>2</td></tr></tbody></table>');
});
test('WO-09 no rows says so across the table', () => {
  assert.equal(fn('bimLbTableHtml')(['a', 'b', 'c'], [], null, esc),
    '<table class="a3d-clb-dtab"><thead><tr><th>a</th><th>b</th><th>c</th></tr></thead><tbody><tr><td colspan="3" class="none">No rows</td></tr></tbody></table>');
});

/* ---------------- WO-10 bimLbHistSvg ---------------- */
test('WO-10 one rect a bar, coloured in turn, a flat bar left out', () => {
  assert.equal(fn('bimLbHistSvg')([{ x: 0, y: 2, w: 4, h: 2 }, { x: 5, y: 4, w: 4, h: 0 }, { x: 10, y: 0, w: 4, h: 4 }], ['#111111', '#222222'], 14, 4),
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 4" width="14" height="4" preserveAspectRatio="none">' +
    '<rect x="0" y="2" width="4" height="2" fill="#111111"/><rect x="10" y="0" width="4" height="4" fill="#111111"/></svg>');
});
test('WO-10 no colours gives grey', () => {
  assert.equal(fn('bimLbHistSvg')([{ x: 0, y: 0, w: 1, h: 1 }], [], 1, 1),
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1" width="1" height="1" preserveAspectRatio="none"><rect x="0" y="0" width="1" height="1" fill="#888888"/></svg>');
});
