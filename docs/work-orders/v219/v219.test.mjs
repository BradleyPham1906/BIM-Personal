/* V219's work-order tests (docs/work-orders/v219/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/analysis/gpu-compute-ref.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v219/v219.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v219/v219.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimGcDiffuse", "bimGcCompare", "bimGcSum", "bimGcWorkgroups"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/analysis/gpu-compute-ref.js'), 'utf8');
  if (process.env.V219_REF) src += fs.readFileSync(process.env.V219_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/analysis/gpu-compute-ref.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// the research's fixture (docs/research/experiments/webgpu-stencil-cpu.py): an 18 x 18 grid, a unit spike at (9, 9),
// 100 explicit diffusion steps with alpha 0.24 and a zero boundary; numpy float64 sum 0.30728186670470226
const spike = () => { const a = new Array(18 * 18).fill(0); a[9 * 18 + 9] = 1; return a; };
test('WO-01 the CPU reference: double precision matches the fixture', () => {
  const x = fn('bimGcDiffuse')(spike(), 18, 0.24, 100, false);
  near(X.bimGcSum ? X.bimGcSum(x) : x.reduce((p, q) => p + q, 0), 0.30728186670470226, 1e-15);
  assert.equal(x[0], 0, 'the boundary stays 0');
});
test('WO-01 single precision, rounded every operation, as a GPU would', () => {
  const y = fn('bimGcDiffuse')(spike(), 18, 0.24, 100, true);
  near(y.reduce((p, q) => p + q, 0), 0.30728190113586606, 1e-9);
});
test('WO-02 the largest and RMS difference between two results (the fixture: 6.1e-10 and 1.6e-10)', () => {
  const x = X.bimGcDiffuse(spike(), 18, 0.24, 100, false), y = X.bimGcDiffuse(spike(), 18, 0.24, 100, true);
  const c = fn('bimGcCompare')(x, y);
  assert.ok(c.max > 1e-11 && c.max < 2e-9, 'max ' + c.max);
  assert.ok(c.rms < c.max);
  assert.deepEqual(fn('bimGcCompare')([1, 2], [1, 2]), { max: 0, rms: 0 });
});
test('WO-03 a sum', () => { assert.equal(fn('bimGcSum')([1, 2, 3.5]), 6.5); });
test('WO-04 workgroups to cover n cells', () => {
  assert.equal(fn('bimGcWorkgroups')(18, 8), 3);
  assert.equal(fn('bimGcWorkgroups')(16), 2);
});
