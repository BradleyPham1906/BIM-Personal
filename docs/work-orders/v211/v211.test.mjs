/* V211's work-order tests (docs/work-orders/v211/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/walk/walk-record.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v211/v211.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v211/v211.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimRecAngle", "bimRecAdd", "bimRecAt", "bimRecInfo"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/walk/walk-record.js'), 'utf8');
  if (process.env.V211_REF) src += fs.readFileSync(process.env.V211_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/walk/walk-record.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 the signed shortest turn between two headings', () => {
  near(fn('bimRecAngle')(0.1, 2 * Math.PI - 0.1), -0.2, 1e-12);
  near(fn('bimRecAngle')(3, -3), 2 * Math.PI - 6, 1e-12);
  near(fn('bimRecAngle')(0, 1), 1, 1e-12);
});
test('WO-02 a pose recorded only when it moved or turned enough; the path copied', () => {
  let p = [];
  p = fn('bimRecAdd')(p, { p: [0, 1.6, 0], yaw: 0 }, 0);
  const q = fn('bimRecAdd')(p, { p: [0.01, 1.6, 0], yaw: 0.001 }, 0.1);
  assert.equal(q.length, 1);
  const r = fn('bimRecAdd')(q, { p: [1, 1.6, 0], yaw: 0 }, 1);
  assert.equal(r.length, 2); assert.equal(q.length, 1, 'not changed in place');
  assert.deepEqual(r[1], { t: 1, p: [1, 1.6, 0], yaw: 0, pitch: 0 });
  assert.equal(fn('bimRecAdd')(q, { p: [0, 1.6, 0], yaw: 0.5 }, 1).length, 2, 'a turn alone is recorded');
});
const PATH = [{ t: 0, p: [0, 1.6, 0], yaw: 2 * Math.PI - 0.2, pitch: 0 }, { t: 2, p: [4, 1.6, 0], yaw: 0.2, pitch: 0.1 }];
test('WO-03 the pose at a time: positions linear, heading the short way round', () => {
  const m = fn('bimRecAt')(PATH, 1);
  assert.deepEqual(m.p, [2, 1.6, 0]);
  near(Math.cos(m.yaw), 1, 1e-12, 'through 0, not through pi');
  near(m.pitch, 0.05, 1e-12);
  assert.deepEqual(fn('bimRecAt')(PATH, 9).p, [4, 1.6, 0]);
  assert.deepEqual(fn('bimRecAt')(PATH, -1).p, [0, 1.6, 0]);
  assert.equal(fn('bimRecAt')([], 1), null);
});
test('WO-04 a path\'s length, duration and poses', () => {
  assert.deepEqual(fn('bimRecInfo')(PATH), { length: 4, duration: 2, poses: 2 });
  assert.deepEqual(fn('bimRecInfo')([]), { length: 0, duration: 0, poses: 0 });
});
