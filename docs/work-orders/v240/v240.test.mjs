/* V240's work-order tests (docs/work-orders/v240/SPEC.md): the pure functions of src/js/engine/structure/wind-loads.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v240/v240.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v240/v240.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text.
   Expected numbers come from the research's worked examples (docs/research/research-physical-world/ and
   docs/research/experiments/physical-world/), not from the implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimWindKz', 'bimWindQz', 'bimWindCpLee', 'bimWindStoreys', 'bimWindCases', 'bimWindNa'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/structure/wind-loads.js'), 'utf8');
  if (process.env.V240_REF) src += fs.readFileSync(process.env.V240_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/structure/wind-loads.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 Kz by the 7-22 terrain constants, held at 4.572 m and capped at zg', () => {
  const k = fn('bimWindKz');
  near(k(3.5, 'C'), 2.41 * Math.pow(15 / 2460, 2 / 9.8), 1e-12, 'below 15 ft uses 15 ft');
  near(k(3.5, 'C'), 0.8512, 5e-5); near(k(7, 'C'), 0.9285, 5e-5); near(k(10.5, 'C'), 1.0086, 5e-5);
  near(k(30, 'B'), 2.41 * Math.pow(30 / (3280 * 0.3048), 2 / 7.5), 1e-12, 'B uses 7.5 and 3280 ft (7-16 used 7.0 and 1200 ft)');
  near(k(30, 'D'), 2.41 * Math.pow(30 / (1935 * 0.3048), 2 / 11.5), 1e-12);
  near(k(800, 'C'), 2.41, 1e-12, 'above zg'); near(k(749.808, 'C'), 2.41, 1e-12);
  assert.ok(Number.isNaN(k(10, 'E'))); assert.ok(Number.isNaN(k(NaN, 'C')));
});
test('WO-02 velocity pressure q = 0.613 Kz Kzt Ke V^2 (Pa), Kd not in it', () => {
  const q = fn('bimWindQz');
  near(q(7, 'C', 50), 1422.9, 0.05); near(q(10.5, 'C', 50), 1545.6, 0.05);
  near(q(7, 'C', 50, 1.2, 0.9), 1422.9 * 1.08, 0.06, 'Kzt and Ke multiply');
  near(q(7, 'C', 50, undefined, undefined), q(7, 'C', 50, 1, 1), 1e-12, 'missing Kzt, Ke are 1');
});
test('WO-03 leeward wall Cp by L/B, linear between 1, 2 and 4', () => {
  const c = fn('bimWindCpLee');
  assert.equal(c(0.667), -0.5); assert.equal(c(1), -0.5); near(c(1.5), -0.4, 1e-12); near(c(2), -0.3, 1e-12);
  near(c(3), -0.25, 1e-12); near(c(4), -0.2, 1e-12); assert.equal(c(9), -0.2); assert.ok(Number.isNaN(c(-1)));
});
test('WO-04 storey forces, case 1: the research\'s 3-storey building (30 x 20 m, V 50 m/s, C)', () => {
  const r = fn('bimWindStoreys')({ levels: [3.5, 7, 10.5], B: 30, L: 20, V: 50, exp: 'C' });
  near(r.qh, 1545.6, 0.05);
  near(r.levels[0].F, 137.79, 0.01); near(r.levels[1].F, 144.98, 0.01); near(r.levels[2].F, 76.21, 0.01);
  near(r.total, 358.99, 0.02);
  near(r.levels[0].pl, -558.4, 0.05, 'leeward uses q at the roof for every level');
  near(r.levels[1].pw, 822.4, 0.05);
  assert.deepEqual([r.levels[0].lo, r.levels[0].hi, r.levels[1].lo, r.levels[1].hi, r.levels[2].lo, r.levels[2].hi], [1.75, 5.25, 5.25, 8.75, 8.75, 10.5]);
});
test('WO-04 the other face, Kd and G given, and bad input', () => {
  const s = fn('bimWindStoreys');
  const r = s({ levels: [3.5, 7, 10.5], B: 20, L: 30, V: 50, exp: 'C' });
  near(r.levels[0].pl, 1545.6 * 0.85 * 0.85 * -0.4, 0.05, 'L/B = 1.5 gives -0.4');
  const t = s({ levels: [4], B: 10, L: 10, V: 40, exp: 'B', Kd: 1, G: 1 });
  const q = 0.613 * 2.41 * Math.pow(4.572 / 999.744, 2 / 7.5) * 1600;
  near(t.levels[0].F, (0.8 * q + 0.5 * q) * 10 * 2 / 1000, 1e-9, 'one level: the band is z/2 to z');
  assert.ok(s({ levels: [3, 3], B: 1, L: 1, V: 1, exp: 'C' }).error); assert.ok(s({ levels: [], B: 1, L: 1, V: 1, exp: 'C' }).error);
  assert.ok(s({ levels: [3], B: 1, L: 1, V: 1, exp: 'X' }).error); assert.ok(s({ levels: [3], B: 0, L: 1, V: 1, exp: 'C' }).error);
});
test('WO-05 the four load cases of Figure 27.3-8 from the case 1 forces', () => {
  const c = fn('bimWindCases')([137.79, 100], [50], 30, 20);
  assert.equal(c.length, 2);
  near(c[0].c2x, 103.3425, 1e-9); near(c[0].mt2x, 465.04125, 1e-9); near(c[0].mt2z, 0.75 * 50 * 0.15 * 20, 1e-9);
  near(c[0].c3x, 103.3425, 1e-9); near(c[0].c3z, 37.5, 1e-9);
  near(c[0].c4x, 0.563 * 137.79, 1e-9); near(c[0].mt4, 0.563 * (137.79 * 4.5 + 50 * 3), 1e-9);
  assert.equal(c[1].c1z, 0); near(c[1].c4x, 56.3, 1e-9);
});
test('WO-06 approximate natural frequency (Hz) from the height in m', () => {
  const n = fn('bimWindNa');
  near(n('steel-mrf', 10.5), 22.2 / Math.pow(10.5 / 0.3048, 0.8), 1e-12); near(n('steel-mrf', 10.5), 1.308, 5e-4);
  near(n('concrete-mrf', 30), 43.5 / Math.pow(30 / 0.3048, 0.9), 1e-12);
  near(n('other', 30), 75 * 0.3048 / 30, 1e-12);
  assert.ok(Number.isNaN(n('shear-wall', 30))); assert.ok(Number.isNaN(n('steel-mrf', 0)));
});
