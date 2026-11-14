/* V208's work-order tests (docs/work-orders/v208/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/walk/walk-drive.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v208/v208.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v208/v208.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimDrvStep", "bimDrvTurnRadius", "bimDrvChase", "bimDrvKmh"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/walk/walk-drive.js'), 'utf8');
  if (process.env.V208_REF) src += fs.readFileSync(process.env.V208_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/walk/walk-drive.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const P = { wheelbase: 2.5, maxSteer: 0.5, accel: 3, decel: 7, drag: 0, vmax: 10 };
test('WO-01 a bicycle-model step: speed up, cap, brake to rest, turn by the steering', () => {
  const f = fn('bimDrvStep');
  let s = { x: 0, z: 0, heading: 0, speed: 0 };
  s = f(s, { throttle: 1 }, 1, P);
  assert.deepEqual(s, { x: 3, z: 0, heading: 0, speed: 3 });
  s = f({ x: 0, z: 0, heading: 0, speed: 9 }, { throttle: 1 }, 1, P);
  assert.equal(s.speed, 10, 'capped at vmax');
  assert.equal(f({ x: 0, z: 0, heading: 0, speed: 5 }, { brake: 1 }, 1, P).speed, 0, 'never backwards');
  const t = f({ x: 0, z: 0, heading: 0, speed: 5 }, { steer: 1 }, 0.1, P);
  near(t.heading, 5 / 2.5 * Math.tan(0.5) * 0.1, 1e-12);
  near(f({ x: 0, z: 0, heading: 0, speed: 5 }, { steer: 9 }, 0.1, P).heading, t.heading, 1e-12, 'steering clamped');
});
test('WO-02 the turning radius of the wheelbase at a steering angle', () => {
  near(fn('bimDrvTurnRadius')(2.5, 0.5), 2.5 / Math.tan(0.5), 1e-12);
  assert.equal(fn('bimDrvTurnRadius')(2.5, 0), Infinity);
});
test('WO-03 the chase camera behind the car at a height', () => {
  const c = fn('bimDrvChase')({ x: 10, z: 0, heading: Math.PI / 2 }, 6, 2.5);
  near(c.eye[0], 10, 1e-12); near(c.eye[2], -6, 1e-12); assert.equal(c.eye[1], 2.5);
  assert.deepEqual(c.target, [10, 1, 0]);
});
test('WO-04 speed in km/h for the dashboard', () => {
  assert.equal(fn('bimDrvKmh')(13.9), 50);
  assert.equal(fn('bimDrvKmh')(0), 0);
});
