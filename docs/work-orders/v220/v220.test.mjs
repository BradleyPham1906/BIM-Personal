/* V220's work-order tests (docs/work-orders/v220/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/render/water-sim.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v220/v220.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v220/v220.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimWtrStep", "bimWtrDrop", "bimWtrSchlick", "bimWtrCaustic"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/render/water-sim.js'), 'utf8');
  if (process.env.V220_REF) src += fs.readFileSync(process.env.V220_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/render/water-sim.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 a heightfield step: a flat pond stays flat; a bump spreads and the total is kept', () => {
  const n = 7, flat = new Array(n * n).fill(0);
  const s = fn('bimWtrStep')(flat, flat, n, 1);
  assert.ok(s.h.every((x) => x === 0));
  const h = flat.slice(); h[3 * n + 3] = 1;
  const t = fn('bimWtrStep')(h, flat, n, 1);
  near(t.h[3 * n + 3], -1, 1e-12); near(t.h[3 * n + 2], 0.5, 1e-12);
  near(t.h.reduce((a, b) => a + b, 0), 1, 1e-12, 'no velocity change in total when the boundary is untouched');
});
test('WO-02 a drop: a smooth dip of strength s within radius r, nothing outside', () => {
  const d = fn('bimWtrDrop')(new Array(25).fill(0), 5, 2, 2, 2, 1);
  near(d[2 * 5 + 2], 1, 1e-12);
  assert.equal(d[0], 0);
});
test('WO-03 Schlick\'s Fresnel: the research\'s air-to-water f0, and grazing 1', () => {
  near(fn('bimWtrSchlick')(1, 1.333, 1), Math.pow(0.333 / 2.333, 2), 1e-15);
  near(fn('bimWtrSchlick')(1, 1.333, 0), 1, 1e-15);
});
test('WO-04 a caustic\'s brightness: old area over new (the fixture: 1, 4, 100, 1e6)', () => {
  assert.deepEqual([1, 0.25, 0.01, 0.000001].map((a) => fn('bimWtrCaustic')(1, a)).map((x) => Math.round(x)), [1, 4, 100, 1000000]);
  assert.equal(fn('bimWtrCaustic')(1, 0), Infinity);
});
