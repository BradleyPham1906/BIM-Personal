/* V193's work-order tests (docs/work-orders/v193/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/bim/facade-openings.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v193/v193.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v193/v193.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimOpnCluster", "bimOpnSnap", "bimOpnRegularise", "bimOpnOverlap", "bimOpnToWall"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/facade-openings.js'), 'utf8');
  if (process.env.V193_REF) src += fs.readFileSync(process.env.V193_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/facade-openings.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 one-dimensional clusters within a gap tolerance, their means', () => {
  const c = fn('bimOpnCluster')([0.92, 3.9, 0.88, 0.9, 4.0], 0.05);
  assert.deepEqual(c.map((x) => x.members), [[0, 2, 3], [1], [4]]);
  near(c[0].mean, 0.9, 1e-12);
  assert.deepEqual(fn('bimOpnCluster')([1, 1.04, 1.08], 0.05).map((x) => x.members), [[0, 1, 2]], 'chained within the gap');
  assert.deepEqual(fn('bimOpnCluster')([], 0.05), []);
});
test('WO-02 each value moved to its cluster\'s mean', () => {
  const s = fn('bimOpnSnap')([0.92, 3.9, 0.88], 0.05);
  near(s[0], 0.9, 1e-12); near(s[2], 0.9, 1e-12); assert.equal(s[1], 3.9);
});
test('WO-03 sills, heads and centres lined up; how far each moved', () => {
  const r = fn('bimOpnRegularise')([{ x: 1, y: 0.92, w: 1.2, h: 1.48 }, { x: 4.02, y: 0.88, w: 1.2, h: 1.5 }, { x: 1.03, y: 3.9, w: 1.2, h: 1.5 }], 0.05);
  near(r[0].y, 0.9, 1e-12); near(r[1].y, 0.9, 1e-12); near(r[0].y + r[0].h, 2.39, 1e-12); near(r[1].y + r[1].h, 2.39, 1e-12);
  near(r[0].x, 1.015, 1e-12); near(r[2].x, 1.015, 1e-12);
  near(r[0].moved, 0.02, 1e-12);
  assert.equal(r[2].y, 3.9);
});
test('WO-04 overlapping openings are found; touching ones are not', () => {
  assert.deepEqual(fn('bimOpnOverlap')([{ x: 0, y: 0, w: 1, h: 1 }, { x: 0.5, y: 0.5, w: 1, h: 1 }, { x: 1.5, y: 0, w: 1, h: 1 }]), [[0, 1]]);
  assert.deepEqual(fn('bimOpnOverlap')([{ x: 0, y: 0, w: 1, h: 1 }, { x: 1, y: 0, w: 1, h: 1 }]), []);
});
test('WO-05 an opening as the app\'s wall opening; outside the wall it is refused', () => {
  assert.deepEqual(fn('bimOpnToWall')({ x: 2, y: 0.9, w: 1.2, h: 1.5 }, 6, 3), { along: 2.6, sill: 0.9, width: 1.2, height: 1.5, kind: 'window' });
  assert.equal(fn('bimOpnToWall')({ x: 3, y: 0, w: 1, h: 2.1 }, 6, 3).kind, 'door');
  assert.equal(fn('bimOpnToWall')({ x: 5.5, y: 1, w: 1, h: 1 }, 6, 3), null);
  assert.equal(fn('bimOpnToWall')({ x: 1, y: 2.5, w: 1, h: 1 }, 6, 3), null);
  assert.equal(fn('bimOpnToWall')({ x: 1, y: 1, w: 0, h: 1 }, 6, 3), null);
});
