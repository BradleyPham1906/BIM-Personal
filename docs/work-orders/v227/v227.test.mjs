/* V227's work-order tests (docs/work-orders/v227/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/site/drone-plan.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v227/v227.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v227/v227.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimDpGsd", "bimDpHeight", "bimDpFootprint", "bimDpSpacing", "bimDpLines"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/site/drone-plan.js'), 'utf8');
  if (process.env.V227_REF) src += fs.readFileSync(process.env.V227_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/site/drone-plan.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// photogrammetry flight planning (GSD = sensor width x height / (focal length x image width))
test('WO-01 ground sample distance in cm a pixel', () => {
  near(fn('bimDpGsd')(13.2, 8.8, 5472, 30), 13.2 * 30 * 100 / (8.8 * 5472), 1e-12);
  near(fn('bimDpGsd')(13.2, 8.8, 5472, 30), 0.8224, 1e-4);
  assert.equal(fn('bimDpGsd')(13.2, 0, 5472, 30), null);
});
test('WO-02 the height for a target GSD (the inverse)', () => {
  near(fn('bimDpHeight')(0.5, 13.2, 8.8, 5472), 0.5 * 8.8 * 5472 / 1320, 1e-12);
  near(X.bimDpGsd(13.2, 8.8, 5472, fn('bimDpHeight')(0.5, 13.2, 8.8, 5472)), 0.5, 1e-12);
});
test('WO-03 a photo\'s footprint on the ground', () => {
  const f = fn('bimDpFootprint')(13.2, 8.8, 8.8, 20);
  near(f.w, 30, 1e-12); near(f.h, 20, 1e-12);
});
test('WO-04 the spacing between photos for an overlap', () => {
  near(fn('bimDpSpacing')(30, 0.8), 6, 1e-12);
  assert.equal(fn('bimDpSpacing')(30, 1), null);
});
test('WO-05 flight lines to cover a width', () => {
  assert.equal(fn('bimDpLines')(60, 6), 11);
  assert.equal(fn('bimDpLines')(61, 6), 12);
  assert.equal(fn('bimDpLines')(60, 0), null);
});
