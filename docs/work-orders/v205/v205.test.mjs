/* V205's work-order tests (docs/work-orders/v205/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/render/splats.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v205/v205.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v205/v205.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimSplatParse", "bimSplatBounds", "bimSplatFit2", "bimSplatApply", "bimSplatOrder"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/render/splats.js'), 'utf8');
  if (process.env.V205_REF) src += fs.readFileSync(process.env.V205_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/render/splats.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// antimatter15's .splat: 32 bytes a splat: position 3 x float32, scale 3 x float32, colour 4 x uint8, rotation 4 x uint8
function splat(rows) {
  const b = new ArrayBuffer(32 * rows.length), dv = new DataView(b);
  rows.forEach((r, i) => { const o = i * 32; r.p.forEach((v, k) => dv.setFloat32(o + 4 * k, v, true)); r.s.forEach((v, k) => dv.setFloat32(o + 12 + 4 * k, v, true)); r.c.forEach((v, k) => dv.setUint8(o + 24 + k, v)); r.q.forEach((v, k) => dv.setUint8(o + 28 + k, v)); });
  return b;
}
const ROWS = [{ p: [1, 2, 3], s: [0.5, 0.5, 0.25], c: [255, 0, 0, 200], q: [255, 128, 128, 128] }, { p: [-1, 0, 5], s: [1, 1, 1], c: [0, 255, 0, 255], q: [128, 0, 128, 128] }];
test('WO-01 a .splat file read splat by splat; a bad length refused', () => {
  const s = fn('bimSplatParse')(splat(ROWS));
  assert.equal(s.n, 2);
  assert.deepEqual(Array.from(s.pos), [1, 2, 3, -1, 0, 5]);
  assert.deepEqual(Array.from(s.scale.slice(0, 3)), [0.5, 0.5, 0.25]);
  assert.deepEqual(Array.from(s.rgba.slice(0, 4)), [255, 0, 0, 200]);
  near(s.rot[0], 127 / 128, 1e-7); assert.equal(s.rot[1], 0); near(s.rot[5], -1, 1e-7);
  assert.deepEqual(fn('bimSplatParse')(new ArrayBuffer(33)), { error: 'not a .splat file (its length is not a multiple of 32)' });
});
test('WO-02 bounds and centre of the positions', () => {
  assert.deepEqual(fn('bimSplatBounds')(new Float32Array([1, 2, 3, -1, 0, 5])), { min: [-1, 0, 3], max: [1, 2, 5], centre: [0, 1, 4] });
  assert.equal(fn('bimSplatBounds')(new Float32Array(0)), null);
});
test('WO-03 placement from two point pairs: scale, a turn about the vertical, a move', () => {
  const T = fn('bimSplatFit2')([0, 0, 0], [1, 0, 0], [10, 2, 10], [10, 2, 12]);
  near(T.s, 2); near(T.rot, Math.PI / 2, 1e-12);
  assert.equal(fn('bimSplatFit2')([0, 0, 0], [0, 5, 0], [1, 1, 1], [2, 2, 2]), null, 'a vertical pair gives no heading');
});
test('WO-04 a point placed: both pairs land on their targets', () => {
  const T = X.bimSplatFit2([1, 0, 1], [3, 1, 1], [5, 10, 5], [5, 11, 9]);
  const p = fn('bimSplatApply')(T, [1, 0, 1]), q = fn('bimSplatApply')(T, [3, 0, 1]);
  near(p[0], 5, 1e-12); near(p[1], 10, 1e-12); near(p[2], 5, 1e-12);
  near(q[0], 5, 1e-12); near(q[2], 9, 1e-12);
});
test('WO-05 splats ordered back to front from the eye; ties by index', () => {
  assert.deepEqual(fn('bimSplatOrder')(new Float32Array([0, 0, 1, 0, 0, 5, 0, 0, 3, 0, 0, -5]), [0, 0, 0]), [1, 3, 2, 0]);
  assert.deepEqual(fn('bimSplatOrder')(null, [0, 0, 0]), []);
});
