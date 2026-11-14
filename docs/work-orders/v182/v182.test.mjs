/* V182's work-order tests (docs/work-orders/v182/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/bim/interiors-views.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v182/v182.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v182/v182.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimIsoHit", "bimIsovist", "bimIsoArea", "bimIsoSees", "bimIsoWindows"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/interiors-views.js'), 'utf8');
  if (process.env.V182_REF) src += fs.readFileSync(process.env.V182_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/interiors-views.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const BOX = [[[0, 0], [10, 0]], [[10, 0], [10, 6]], [[10, 6], [0, 6]], [[0, 6], [0, 0]]];
test('WO-01 the distance along a ray to the nearest wall segment, or Infinity', () => {
  near(fn('bimIsoHit')([2, 3], 1, 0, BOX), 8);
  near(fn('bimIsoHit')([2, 3], 0, -1, BOX), 3);
  assert.equal(fn('bimIsoHit')([2, 3], 1, 0, []), Infinity);
  near(fn('bimIsoHit')([2, 3], Math.SQRT1_2, Math.SQRT1_2, BOX), 3 * Math.SQRT2, 1e-12);
});
test('WO-02 an isovist: n rays from the eye, each to its hit or maxR', () => {
  const v = fn('bimIsovist')([5, 3], BOX, 4, 50);
  assert.equal(v.length, 4);
  near(v[0][0], 10); near(v[0][1], 3); near(v[1][0], 5, 1e-12); near(v[1][1], 6);
  const open = fn('bimIsovist')([0, 0], [], 4, 2);
  near(open[2][0], -2, 1e-12);
  assert.equal(fn('bimIsovist')([5, 3], BOX).length, 360);
});
test('WO-03 a polygon area by the shoelace formula, either winding', () => {
  near(fn('bimIsoArea')([[0, 0], [10, 0], [10, 6], [0, 6]]), 60);
  near(fn('bimIsoArea')([[0, 0], [0, 6], [10, 6], [10, 0]]), 60);
  assert.equal(fn('bimIsoArea')(null), 0);
  const v = X.bimIsovist([5, 3], BOX, 3600, 50);
  near(fn('bimIsoArea')(v), 60, 0.05, 'a fine isovist of a box is the box');
});
test('WO-04 a sightline is clear unless a wall crosses before the target', () => {
  const segs = BOX.concat([[[5, 0], [5, 4]]]);
  assert.equal(fn('bimIsoSees')([2, 2], [8, 2], segs), false);
  assert.equal(fn('bimIsoSees')([2, 5], [8, 5], segs), true);
  assert.equal(fn('bimIsoSees')([2, 2], [10, 2], BOX), true, 'a point on a wall is seen');
  assert.equal(fn('bimIsoSees')([2, 2], [2, 2], segs), true);
});
test('WO-05 the share of each window seen from the eye, by evenly spaced samples', () => {
  const segs = BOX.concat([[[5, 0], [5, 4]]]);
  const r = fn('bimIsoWindows')([2, 5], [{ id: 'east', a: [10, 0], b: [10, 6] }, { id: 'west', a: [0, 1], b: [0, 5] }], segs, 6);
  assert.deepEqual(r.map((x) => x.id), ['east', 'west']);
  assert.equal(r[1].fraction, 1);
  near(r[0].fraction, 4 / 6, 1e-12, 'the two lowest samples hidden by the half wall');
  assert.equal(fn('bimIsoWindows')([2, 2], [{ id: 'w', a: [10, 0], b: [10, 6] }], BOX)[0].fraction, 1);
});
