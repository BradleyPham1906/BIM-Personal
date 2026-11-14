/* V184's work-order tests (docs/work-orders/v184/SPEC.md, WO-01 to WO-06): the pure functions of src/js/engine/drawing/surfaces.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v184/v184.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v184/v184.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimSrfGrid", "bimSrfExtrude", "bimSrfRotate", "bimSrfRevolve", "bimSrfLoft", "bimSrfCoons"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/drawing/surfaces.js'), 'utf8');
  if (process.env.V184_REF) src += fs.readFileSync(process.env.V184_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/drawing/surfaces.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 quads over a grid of rows by cols, wrapped in u when closed', () => {
  assert.deepEqual(fn('bimSrfGrid')(2, 3, false), [[0, 1, 4, 3], [1, 2, 5, 4]]);
  assert.deepEqual(fn('bimSrfGrid')(2, 3, true), [[0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5]]);
  assert.deepEqual(fn('bimSrfGrid')(1, 3, false), []);
});
test('WO-02 a curve extruded along a vector', () => {
  const m = fn('bimSrfExtrude')([[0, 0, 0], [1, 0, 0], [2, 0, 1]], [0, 3, 0]);
  assert.deepEqual(m.v, [[0, 0, 0], [1, 0, 0], [2, 0, 1], [0, 3, 0], [1, 3, 0], [2, 3, 1]]);
  assert.deepEqual(m.f, [[0, 1, 4, 3], [1, 2, 5, 4]]);
  assert.equal(fn('bimSrfExtrude')([[0, 0, 0]], [0, 1, 0]), null);
});
test('WO-03 a point turned about an axis (Rodrigues), right-handed', () => {
  const r = fn('bimSrfRotate')([2, 0, 0], [1, 0, 0], [0, 0, 5], Math.PI / 2);
  near(r[0], 1, 1e-12); near(r[1], 1, 1e-12); near(r[2], 0, 1e-12);
  const q = fn('bimSrfRotate')([1, 0, 0], [0, 0, 0], [1, 1, 1], 2 * Math.PI / 3);
  near(q[0], 0, 1e-12); near(q[1], 1, 1e-12); near(q[2], 0, 1e-12);
});
test('WO-04 a revolve: rings of the profile; a full turn shares its first ring', () => {
  const prof = [[1, 0, 0], [1, 2, 0]];
  const full = fn('bimSrfRevolve')(prof, [0, 0, 0], [0, 1, 0], 2 * Math.PI, 4);
  assert.equal(full.v.length, 8); assert.equal(full.f.length, 4);
  assert.deepEqual(full.f[3], [6, 7, 1, 0]);
  for (const p of full.v) near(Math.hypot(p[0], p[2]), 1, 1e-12);
  const half = fn('bimSrfRevolve')(prof, [0, 0, 0], [0, 1, 0], Math.PI, 2);
  assert.equal(half.v.length, 6); assert.equal(half.f.length, 2);
  near(half.v[4][0], -1, 1e-12);
  assert.equal(fn('bimSrfRevolve')([[1, 0, 0]], [0, 0, 0], [0, 1, 0], 1, 2), null);
});
test('WO-05 a loft between two curves of the same count, in rows', () => {
  const m = fn('bimSrfLoft')([[0, 0, 0], [1, 0, 0]], [[0, 0, 2], [1, 1, 2]], 2);
  assert.deepEqual(m.v, [[0, 0, 0], [1, 0, 0], [0, 0, 1], [1, 0.5, 1], [0, 0, 2], [1, 1, 2]]);
  assert.equal(m.f.length, 2);
  assert.equal(fn('bimSrfLoft')([[0, 0, 0], [1, 0, 0]], [[0, 0, 1]], 1), null);
});
test('WO-06 a Coons patch from four edges: flat edges give the flat square', () => {
  const c0 = [[0, 0, 0], [1, 0, 0], [2, 0, 0]], c1 = [[0, 2, 0], [1, 2, 0], [2, 2, 0]];
  const d0 = [[0, 0, 0], [0, 1, 0], [0, 2, 0]], d1 = [[2, 0, 0], [2, 1, 0], [2, 2, 0]];
  const m = fn('bimSrfCoons')(c0, c1, d0, d1);
  assert.equal(m.v.length, 9); assert.equal(m.f.length, 4);
  assert.deepEqual(m.v[4], [1, 1, 0]);
  const bump = fn('bimSrfCoons')([[0, 0, 0], [1, 0, 1], [2, 0, 0]], c1, d0, d1);
  near(bump.v[4][2], 0.5, 1e-12, 'a raised edge raises the middle halfway');
  assert.equal(fn('bimSrfCoons')(c0, c1.slice(0, 2), d0, d1), null);
});
