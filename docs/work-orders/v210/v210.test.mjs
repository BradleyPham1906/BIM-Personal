/* V210's work-order tests (docs/work-orders/v210/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/walk/walk-swim.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v210/v210.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v210/v210.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimSwmUnder", "bimSwmStep", "bimSwmFog", "bimSwmSurface"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/walk/walk-swim.js'), 'utf8');
  if (process.env.V210_REF) src += fs.readFileSync(process.env.V210_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/walk/walk-swim.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 under water when the eye is below the surface', () => {
  assert.equal(fn('bimSwmUnder')(1, 2), true);
  assert.equal(fn('bimSwmUnder')(2, 2), false);
  assert.equal(fn('bimSwmUnder')(1, null), false, 'no water');
});
test('WO-02 a swimming step: thrust, drag against the velocity, buoyancy up', () => {
  const v = fn('bimSwmStep')([1, 0, 0], [0, 0, 1], 0.5, { drag: 2, buoy: 0.3, thrust: 1.5 });
  near(v[0], 0, 1e-12); near(v[1], 0.15, 1e-12); near(v[2], 0.75, 1e-12);
  const d = fn('bimSwmStep')([0, 0, 0], [], 1, {});
  near(d[1], 0.3, 1e-12, 'defaults: drag 2, buoyancy 0.3, thrust 1.5');
});
test('WO-03 the water\'s haze from depth: clear at the surface, full at the clear depth', () => {
  assert.equal(fn('bimSwmFog')(0, 8), 0);
  assert.equal(fn('bimSwmFog')(4, 8), 0.5);
  assert.equal(fn('bimSwmFog')(20), 1);
});
test('WO-04 a swimmer kept just under the surface', () => {
  assert.deepEqual(fn('bimSwmSurface')([1, 5, 1], 3, 0.2), [1, 2.8, 1]);
  assert.deepEqual(fn('bimSwmSurface')([1, 1, 1], 3), [1, 1, 1]);
});
