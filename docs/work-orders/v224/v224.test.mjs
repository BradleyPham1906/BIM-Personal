/* V224's work-order tests (docs/work-orders/v224/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/site/field-guide.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v224/v224.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v224/v224.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimFeBearing", "bimFeIntersect", "bimFeResect", "bimFeNext"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/site/field-guide.js'), 'utf8');
  if (process.env.V224_REF) src += fs.readFileSync(process.env.V224_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/site/field-guide.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 the bearing from one plan point to another, clockwise from north', () => {
  near(fn('bimFeBearing')([0, 0], [0, 10]), 0); near(fn('bimFeBearing')([0, 0], [10, 0]), 90);
  near(fn('bimFeBearing')([0, 0], [-10, -10]), 225); near(fn('bimFeBearing')([5, 5], [0, 5]), 270);
});
test('WO-02 where two bearings meet; parallel or behind gives none', () => {
  const p = fn('bimFeIntersect')([0, 0], 45, [10, 0], 315);
  near(p[0], 5, 1e-9); near(p[1], 5, 1e-9);
  assert.equal(fn('bimFeIntersect')([0, 0], 0, [10, 0], 0), null);
  assert.equal(fn('bimFeIntersect')([0, 0], 225, [10, 0], 135), null);
});
test('WO-03 a position from three or more sightings: the mean of each pair\'s meeting, with its spread', () => {
  const T = [20, 30], obs = [[0, 0], [40, 0], [0, 50]].map((f) => ({ from: f, az: X.bimFeBearing(f, T) }));
  const r = fn('bimFeResect')(T, obs);
  near(r.p[0], 20, 1e-9); near(r.p[1], 30, 1e-9); near(r.spread, 0, 1e-9); assert.equal(r.pairs, 3);
  assert.equal(fn('bimFeResect')(T, [obs[0]]), null);
});
test('WO-04 the next field step whose prerequisites are done; those waiting are listed', () => {
  const S = [{ id: 'mark', after: [] }, { id: 'drill', after: ['mark'] }, { id: 'anchor', after: ['drill'] }, { id: 'photo', after: [] }];
  assert.deepEqual(fn('bimFeNext')(S, []), { next: 'mark', blocked: [] });
  assert.deepEqual(fn('bimFeNext')(S, ['mark', 'photo']), { next: 'drill', blocked: [] });
  assert.deepEqual(fn('bimFeNext')([S[2], S[3]], []), { next: 'photo', blocked: ['anchor'] });
  assert.deepEqual(fn('bimFeNext')(S, ['mark', 'drill', 'anchor', 'photo']), { next: null, blocked: [] });
});
