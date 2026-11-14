/* V209's work-order tests (docs/work-orders/v209/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/walk/walk-drone.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v209/v209.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v209/v209.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimDrnClamp", "bimDrnOrbit", "bimDrnRoute", "bimDrnAt"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/walk/walk-drone.js'), 'utf8');
  if (process.env.V209_REF) src += fs.readFileSync(process.env.V209_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/walk/walk-drone.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 the drone kept between its lowest and highest flight above the ground', () => {
  assert.deepEqual(fn('bimDrnClamp')([1, 0.5, 2], 2, 120, 0), [1, 2, 2]);
  assert.deepEqual(fn('bimDrnClamp')([1, 500, 2], 2, 120, 10), [1, 130, 2]);
  assert.deepEqual(fn('bimDrnClamp')([1, 50, 2]), [1, 50, 2], 'defaults 2 and 120 above 0');
});
test('WO-02 an orbit about a target: radius, height, one turn a period', () => {
  const o = fn('bimDrnOrbit')([10, 0, 5], 20, 30, 7.5, 30);
  near(o.eye[0], 10, 1e-12); near(o.eye[2], 25, 1e-12); assert.equal(o.eye[1], 30);
  assert.deepEqual(o.target, [10, 0, 5]);
});
const WP = [[0, 10, 0], [30, 10, 0], [30, 10, 40]];
test('WO-03 a waypoint route: its legs and length', () => {
  assert.deepEqual(fn('bimDrnRoute')(WP), { segs: [30, 40], length: 70 });
  assert.deepEqual(fn('bimDrnRoute')([[0, 0, 0]]), { segs: [], length: 0 });
});
test('WO-04 the point a distance along the route, clamped to its ends', () => {
  const r = X.bimDrnRoute(WP);
  assert.deepEqual(fn('bimDrnAt')(WP, r, 15), [15, 10, 0]);
  assert.deepEqual(fn('bimDrnAt')(WP, r, 50), [30, 10, 20]);
  assert.deepEqual(fn('bimDrnAt')(WP, r, 999), [30, 10, 40]);
  assert.deepEqual(fn('bimDrnAt')(WP, r, -5), [0, 10, 0]);
  assert.equal(fn('bimDrnAt')([], r, 1), null);
});
