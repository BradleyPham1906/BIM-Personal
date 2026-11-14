/* V188's work-order tests (docs/work-orders/v188/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/drawing/flow-picture.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v188/v188.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v188/v188.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimPicPlane", "bimTextBox", "bimFlowBox", "bimFlowBilinear", "bimFlowMap"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/drawing/flow-picture.js'), 'utf8');
  if (process.env.V188_REF) src += fs.readFileSync(process.env.V188_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/drawing/flow-picture.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 a picture plane keeps the image\'s aspect at the width given', () => {
  assert.deepEqual(fn('bimPicPlane')(1600, 900, 8), { w: 8, h: 4.5, corners: [[0, 0], [8, 0], [8, 4.5], [0, 4.5]], uv: [[0, 1], [1, 1], [1, 0], [0, 0]] });
  assert.equal(fn('bimPicPlane')(0, 900, 8), null);
  assert.equal(fn('bimPicPlane')(10, 10, -1), null);
});
test('WO-02 a text box: the longest line by character width, lines by spacing', () => {
  assert.deepEqual(fn('bimTextBox')(['Level 1', 'Plan'], 0.5), { w: 2.1, h: 1.1 });
  assert.deepEqual(fn('bimTextBox')(['abc'], 1, 0.5, 2), { w: 1.5, h: 1 });
  assert.deepEqual(fn('bimTextBox')([], 1), { w: 0, h: 0 });
});
test('WO-03 the base box of points in plan', () => {
  assert.deepEqual(fn('bimFlowBox')([[1, 2, 0], [4, -1, 3], [2, 5, 0]]), [1, -1, 4, 5]);
  assert.equal(fn('bimFlowBox')([]), null);
});
const PATCH = [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]];
test('WO-04 a bilinear patch point from its four corners', () => {
  assert.deepEqual(fn('bimFlowBilinear')(PATCH, 0.5, 0.5), [5, 0, 5]);
  assert.deepEqual(fn('bimFlowBilinear')(PATCH, 1, 0), [10, 0, 0]);
  const twist = [[0, 0, 0], [1, 0, 0], [1, 1, 1], [0, 1, 0]];
  near(fn('bimFlowBilinear')(twist, 0.5, 0.5)[2], 0.25);
});
test('WO-05 flow along a surface: base box to the patch, height along its normal', () => {
  const out = fn('bimFlowMap')([[0, 0, 0], [2, 1, 0], [1, 0.5, 2]], [0, 0, 2, 1], PATCH);
  assert.deepEqual(out[0], [0, 0, 0]);
  assert.deepEqual(out[1], [10, 0, 10]);
  near(out[2][0], 5); near(out[2][1], -2, 1e-12, 'up the patch normal du x dv = -y'); near(out[2][2], 5);
  assert.equal(fn('bimFlowMap')([[0, 0, 0]], [0, 0, 0, 1], PATCH), null);
});
