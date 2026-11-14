/* V221's work-order tests (docs/work-orders/v221/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/analysis/lbm-ref.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v221/v221.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v221/v221.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimLbmEq", "bimLbmMoments", "bimLbmStep", "bimLbmBytes"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/analysis/lbm-ref.js'), 'utf8');
  if (process.env.V221_REF) src += fs.readFileSync(process.env.V221_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/analysis/lbm-ref.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 the D2Q9 equilibrium: at rest it is the weights times the density, and it carries the velocity', () => {
  const e = fn('bimLbmEq')(2, 0, 0);
  near(e[0], 8 / 9, 1e-15); near(e[5], 2 / 36, 1e-15);
  const f = fn('bimLbmEq')(1.2, 0.05, -0.02), E = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]];
  const rho = f.reduce((a, b) => a + b, 0), ux = f.reduce((a, b, i) => a + b * E[i][0], 0) / rho, uy = f.reduce((a, b, i) => a + b * E[i][1], 0) / rho;
  near(rho, 1.2, 1e-12); near(ux, 0.05, 1e-12); near(uy, -0.02, 1e-12);
});
test('WO-02 density and velocity from the populations', () => {
  assert.deepEqual(fn('bimLbmMoments')([0, 0, 0, 0, 0, 0, 0, 0, 0]), { rho: 0, ux: 0, uy: 0 });
  const m = fn('bimLbmMoments')([1, 1, 0, 0, 0, 0, 0, 0, 0]); near(m.rho, 2); near(m.ux, 0.5);
});
test('WO-03 a collide-and-stream step on a periodic box keeps the mass and the momentum', () => {
  const nx = 6, ny = 5, F = [];
  for (let k = 0; k < nx * ny; k++) F.push(X.bimLbmEq(1 + 0.01 * (k % 7), 0.02 * Math.sin(k), 0.01));
  const tot = (G) => { let r = 0, px = 0; for (const f of G) { const m = X.bimLbmMoments(f); r += m.rho; px += m.rho * m.ux; } return [r, px]; };
  const a = tot(F), b = tot(fn('bimLbmStep')(F, nx, ny, 0.8));
  near(b[0], a[0], 1e-12, 'mass'); near(b[1], a[1], 1e-12, 'momentum');
});
test('WO-04 memory for a D3Q19 box (the research\'s figures)', () => {
  assert.equal(fn('bimLbmBytes')(128, 19, 4), 159383552);
  assert.equal(fn('bimLbmBytes')(128, 19, 4, 2), 318767104);
  assert.equal(fn('bimLbmBytes')(256, 19, 4, 2), 2550136832);
});
