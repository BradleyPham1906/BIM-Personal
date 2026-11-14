/* V180's work-order tests (docs/work-orders/v180/SPEC.md, WO-01 to WO-06): the pure functions of src/js/engine/bim/interiors-clearance.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v180/v180.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v180/v180.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimClrRect", "bimClrZone", "bimClrOverlap", "bimClrConflicts", "bimClrCircleFits", "bimClrRule"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/interiors-clearance.js'), 'utf8');
  if (process.env.V180_REF) src += fs.readFileSync(process.env.V180_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/interiors-clearance.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const SQ = (x, z, s) => [[x, z], [x + s, z], [x + s, z + s], [x, z + s]];
test('WO-01 a rectangle turned about its centre, counter-clockwise corners', () => {
  const r = fn('bimClrRect')([1, 2], 2, 1, 0);
  assert.deepEqual(r, [[0, 1.5], [2, 1.5], [2, 2.5], [0, 2.5]]);
  const q = fn('bimClrRect')([0, 0], 2, 1, Math.PI / 2);
  near(q[0][0], 0.5, 1e-12); near(q[0][1], -1, 1e-12); near(q[2][0], -0.5, 1e-12); near(q[2][1], 1, 1e-12);
});
test('WO-02 the clearance zone in front of an item (its local +z side), widened by side', () => {
  const z = fn('bimClrZone')({ center: [0, 0], w: 1, d: 0.6, rot: 0 }, 0.9, 0.1);
  assert.deepEqual(z.map((p) => p.map((v) => Math.round(v * 1e9) / 1e9)), [[-0.6, 0.3], [0.6, 0.3], [0.6, 1.2], [-0.6, 1.2]]);
  assert.equal(fn('bimClrZone')({ center: [0, 0], w: 1, d: 0.6 }, 0, 0), null);
});
test('WO-03 convex overlap by separating axes; touching is not overlapping', () => {
  const f = fn('bimClrOverlap');
  assert.equal(f(SQ(0, 0, 1), SQ(0.5, 0.5, 1)), true);
  assert.equal(f(SQ(0, 0, 1), SQ(1, 0, 1)), false);
  assert.equal(f(SQ(0, 0, 1), SQ(2, 2, 1)), false);
  assert.equal(f(SQ(0, 0, 1), [[1.2, 0.5], [2, -1], [2, 2]]), false);
  assert.equal(f(SQ(0, 0, 1), null), false);
});
test('WO-04 a zone blocked by another item\'s body or an obstacle; zones may overlap each other', () => {
  const items = [
    { id: 'bed', body: SQ(0, 0, 2), zone: SQ(0, 2, 1) },
    { id: 'desk', body: SQ(0.5, 2.5, 0.4), zone: SQ(0.4, 2.2, 0.3) },
    { id: 'chair', body: SQ(5, 5, 0.5), zone: null }
  ];
  assert.deepEqual(fn('bimClrConflicts')(items, [{ id: 'wall', poly: [[0.8, 2.8], [3, 2.8], [3, 3.5], [0.8, 3.5]] }]),
    [{ item: 'bed', with: 'desk' }, { item: 'bed', with: 'wall' }]);
  assert.deepEqual(fn('bimClrConflicts')(null, []), []);
});
test('WO-05 a turning circle fits a room only inside and clear of every edge', () => {
  const room = SQ(0, 0, 2);
  assert.equal(fn('bimClrCircleFits')(room, [1, 1], 0.762), true);
  assert.equal(fn('bimClrCircleFits')(room, [0.5, 1], 0.762), false);
  assert.equal(fn('bimClrCircleFits')(room, [1, 1], 1), true, 'exactly touching');
  assert.equal(fn('bimClrCircleFits')(room, [5, 1], 0.1), false);
  assert.equal(fn('bimClrCircleFits')([[0, 0], [4, 0], [4, 4], [2, 1], [0, 4]], [2, 2], 0.3), false, 'outside a concave notch');
});
test('WO-06 a measurement against a registry rule, with its clause and edition', () => {
  const rule = { minIn: 32, clause: '404.2.3', edition: '2010 ADA Standards' };
  assert.deepEqual(fn('bimClrRule')(rule, 0.8128), { clause: '404.2.3', edition: '2010 ADA Standards', status: 'meets', measuredIn: 32 });
  assert.equal(fn('bimClrRule')(rule, 31.9 * 0.0254).status, 'below');
  assert.deepEqual(fn('bimClrRule')(rule, null), { clause: '404.2.3', edition: '2010 ADA Standards', status: 'not evaluated' });
  assert.deepEqual(fn('bimClrRule')(null, 1), { clause: '', edition: '', status: 'not evaluated' });
});
