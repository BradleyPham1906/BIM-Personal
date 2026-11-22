/* V247's work-order tests (docs/work-orders/v247/SPEC.md): the pure functions of src/js/engine/terrain/runoff.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v247/v247.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v247/v247.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text.
   Expected numbers come from the research's worked examples (docs/research/research-physical-world/ and
   docs/research/experiments/physical-world/), not from the implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimRunFill', 'bimRunD8', 'bimRunAccum', 'bimRunC', 'bimRunRational', 'bimRunCatchment'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/terrain/runoff.js'), 'utf8');
  if (process.env.V247_REF) src += fs.readFileSync(process.env.V247_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/terrain/runoff.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

/* the research's 4 x 4 plane (10 - row - 0.5 col, row 0 north) with a pit of 6.0 at row 1, col 1 */
const Z = []; for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) Z.push(10 - r - 0.5 * c); Z[5] = 6;
test('WO-01 Priority-Flood with epsilon: the pit is raised just above its lowest way out, nothing else moves', () => {
  const w = fn('bimRunFill')(Z, 4, 4, 1e-3);
  near(w[5], 7.001, 1e-9); Z.forEach((z, i) => { if (i !== 5) assert.equal(w[i], z); });
  assert.equal(Z[5], 6, 'the input is not changed');
  const flat = fn('bimRunFill')(Z, 4, 4, 0); assert.equal(flat[5], 7, 'epsilon 0 leaves a flat');
  const nd = Z.slice(); nd[15] = null; nd[10] = 1;
  const v = fn('bimRunFill')(nd, 4, 4, 1e-3); assert.equal(v[15], null); assert.equal(v[10], 1, 'next to NoData is an outlet');
  assert.equal(fn('bimRunFill')([1, 2], 4, 4, 0), null);
});
test('WO-02 D8: the steepest drop per distance (diagonals at sqrt 2), -1 with no lower neighbour', () => {
  const d = fn('bimRunD8');
  assert.deepEqual(d(Z, 4, 4, 1), [3, 4, 5, 4, 2, -1, 6, 4, 1, 0, 3, 4, 2, 2, 2, -1]);
  assert.deepEqual(d([1, 1, 1, 1], 2, 2, 1), [-1, -1, -1, -1]);
  assert.deepEqual(d([5, 4, 4, 0], 2, 2, 1), [3, 4, 2, -1], 'a diagonal drop of 5 beats a straight drop of 1');
  assert.deepEqual(d([2, 1, 1, 0], 2, 2, 10), [3, 4, 2, -1]);
  assert.deepEqual(d([5, null, 4, 0], 2, 2, 1), [3, -1, 2, -1], 'NoData cells are skipped');
  assert.equal(d([1], 2, 2, 1), null);
});
test('WO-03 accumulation: each cell counts itself and every cell upstream', () => {
  const a = fn('bimRunAccum');
  assert.deepEqual(a([3, 4, 5, 4, 2, -1, 6, 4, 1, 0, 3, 4, 2, 2, 2, -1], 4, 4), [1, 1, 1, 1, 1, 8, 1, 2, 1, 1, 1, 3, 1, 2, 3, 8]);
  assert.deepEqual(a([3, 4, 5, 4, 2, 3, 3, 4, 3, 3, 3, 4, 2, 2, 2, -1], 4, 4), [1, 1, 1, 1, 1, 5, 1, 2, 1, 1, 6, 4, 1, 3, 5, 16]);
  assert.equal(a([2, 6], 2, 1), null, 'a cycle is refused'); assert.deepEqual(a([0], 1, 1), [1], 'a direction off the grid is an outlet');
});
test('WO-03 with WO-01 and WO-02: after the fill, all 16 cells reach the outlet', () => {
  if (!X.bimRunFill || !X.bimRunD8) return assert.fail('needs WO-01 and WO-02');
  const acc = fn('bimRunAccum')(X.bimRunD8(X.bimRunFill(Z, 4, 4, 1e-3), 4, 4, 1), 4, 4);
  assert.equal(acc[15], 16);
});
test('WO-04 the composite runoff coefficient, weighted by area (HEC-22 eq. 4.2)', () => {
  const c = fn('bimRunC');
  near(c([{ C: 0.9, area: 1 }, { C: 0.3, area: 1 }]), 0.6, 1e-12); near(c([{ C: 0.9, area: 3 }, { C: 0.1, area: 1 }]), 0.7, 1e-12);
  assert.ok(Number.isNaN(c([]))); assert.ok(Number.isNaN(c([{ C: 1.2, area: 1 }]))); assert.ok(Number.isNaN(c([{ C: 0.5, area: -1 }])));
});
test('WO-05 the rational method, SI: Q = C i A / 360 (m3/s, mm/h, ha), warned above 80 ha', () => {
  const r = fn('bimRunRational');
  near(r(0.6, 100, 2).Q, 0.333333, 1e-6); assert.equal(r(0.6, 100, 2).warn, '');
  near(r(0.9, 131.3, 0.5).Q, 0.9 * 131.3 * 0.5 / 360, 1e-12);
  assert.ok(r(0.5, 50, 81).warn.length > 0); assert.equal(r(0.5, 50, 80).warn, '');
  assert.ok(r(1.1, 50, 1).error); assert.ok(r(0.5, -1, 1).error);
});
/* WO-06, added 2026-11-21 (docs/research/research-terrain-surface.md: a point's catchment, offered to V247 by the owner's choice).
   The directions are WO-02's for the research's 4 x 4 plane with its pit; WO-03's counts give each catchment's size. */
const D = [3, 4, 5, 4, 2, -1, 6, 4, 1, 0, 3, 4, 2, 2, 2, -1];
test('WO-06 the catchment of a cell: the cell and every cell whose water reaches it', () => {
  const k = fn('bimRunCatchment');
  assert.deepEqual(k(D, 4, 4, 5), [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0], 'the pit gathers 8 cells');
  assert.deepEqual(k(D, 4, 4, 15), [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1], 'the outlet gathers the other 8');
  assert.deepEqual(k(D, 4, 4, 0), [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'a ridge cell gathers only itself');
  assert.deepEqual(k([3, 4, 5, 4, 2, 3, 3, 4, 3, 3, 3, 4, 2, 2, 2, -1], 4, 4, 15), new Array(16).fill(1), 'after the fill, everything reaches the outlet');
});
test('WO-06 the same size as the accumulation; a cell off the grid gathers nothing; a bad grid is null', () => {
  const k = fn('bimRunCatchment');
  const acc = [1, 1, 1, 1, 1, 8, 1, 2, 1, 1, 1, 3, 1, 2, 3, 8];
  for (let i = 0; i < 16; i++) assert.equal(k(D, 4, 4, i).reduce((s, v) => s + v, 0), acc[i], 'cell ' + i);
  assert.deepEqual(k([0, 4], 2, 1, 2), [0, 0]); assert.deepEqual(k([0, 4], 2, 1, -1), [0, 0]); assert.deepEqual(k([0, 4], 2, 1, 0.5), [0, 0]);
  assert.deepEqual(k([2, 6], 2, 1, 0), [1, 1], 'a cycle is walked once');
  assert.equal(k([1], 2, 2, 0), null);
  const d2 = D.slice(); assert.deepEqual(k(d2, 4, 4, 5), k(D, 4, 4, 5)); assert.deepEqual(d2, D, 'the input is not changed');
});
