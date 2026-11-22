/* V243's work-order tests (docs/work-orders/v243/SPEC.md): the pure functions of src/js/engine/structure/rc-checks.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v243/v243.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v243/v243.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text.
   Expected numbers come from the research's worked examples (docs/research/research-physical-world/ and
   docs/research/experiments/physical-world/), not from the implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimRcMat', 'bimRcSection', 'bimRcIe', 'bimRcState', 'bimRcFlexure', 'bimCheckBand'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/structure/rc-checks.js'), 'utf8');
  if (process.env.V243_REF) src += fs.readFileSync(process.env.V243_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/structure/rc-checks.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 concrete values from f\'c (MPa): Ec, fr and beta1 (ACI 318-19)', () => {
  const m = fn('bimRcMat');
  const a = m(30); near(a.Ec, 25742.96, 0.01); near(a.fr, 3.39588, 1e-5); near(a.beta1, 0.835714, 1e-6);
  near(m(30, 0.75).fr, 0.75 * 3.39588, 1e-5, 'lambda for lightweight'); near(m(30, 0.75).Ec, 25742.96, 0.01);
  assert.equal(m(25).beta1, 0.85); assert.equal(m(28).beta1, 0.85); near(m(35).beta1, 0.80, 1e-12); assert.equal(m(55).beta1, 0.65); assert.equal(m(80).beta1, 0.65);
  assert.ok(m(0).error); assert.ok(m(30, 1.2).error); assert.ok(m(30, 0).error);
});
test('WO-02 the section: Ig, yt, Mcr (kN m), n, kd and Icr, the research\'s 300 x 500 beam', () => {
  const s = fn('bimRcSection')(300, 500, 450, 942, 200000, 25742.960202742808, 3.39587985653203);
  near(s.Ig, 3.125e9, 1); assert.equal(s.yt, 250); near(s.Mcr, 42.448, 5e-4); near(s.n, 7.7691, 5e-5);
  near(s.kd, 125.774, 5e-3); near(s.Icr, 9.68303e8, 1e3);
  near(300 * s.kd * s.kd / 2, s.n * 942 * (450 - s.kd), 1e-3, 'kd balances the transformed section');
  assert.ok(fn('bimRcSection')(300, 500, 500, 942, 200000, 25000, 3).error, 'd must be inside h');
  assert.ok(fn('bimRcSection')(300, 500, 450, 0, 200000, 25000, 3).error);
});
test('WO-03 Ie, Table 24.2.3.5 (Bischoff, not Branson)', () => {
  const ie = fn('bimRcIe'), Mcr = 42.448498, Ig = 3.125e9, Icr = 9.683027e8;
  near(ie(Mcr, 60, Ig, Icr), 1.14392e9, 2e4); near(ie(Mcr, 120, Ig, Icr), 1.00695e9, 2e4);
  near(ie(Mcr, -120, Ig, Icr), ie(Mcr, 120, Ig, Icr), 1e-6, 'the sign of the moment does not matter');
  assert.equal(ie(Mcr, 20, Ig, Icr), Ig); assert.equal(ie(Mcr, 0, Ig, Icr), Ig); assert.equal(ie(Mcr, 2 / 3 * Mcr, Ig, Icr), Ig);
  const branson = Icr + (Ig - Icr) * Math.pow(Mcr / 60, 3);
  assert.ok(Math.abs(ie(Mcr, 60, Ig, Icr) - branson) > 5e8, 'Branson\'s equation would give 1.73e9');
  assert.ok(Number.isNaN(ie(0, 60, Ig, Icr))); assert.ok(Number.isNaN(ie(Mcr, 60, Ig, 2 * Ig)));
});
test('WO-04 the cracking state: uncracked up to 2/3 Mcr, reduced up to Mcr, cracked above', () => {
  const s = fn('bimRcState');
  assert.equal(s(20, 42.45), 'uncracked'); assert.equal(s(28.3, 42.45), 'uncracked'); assert.equal(s(30, 42.45), 'reduced');
  assert.equal(s(42.45, 42.45), 'reduced'); assert.equal(s(42.46, 42.45), 'cracked'); assert.equal(s(-60, 42.45), 'cracked');
  assert.equal(s(10, 0), 'none'); assert.equal(s(NaN, 42), 'none');
});
test('WO-05 flexural strength of a singly reinforced rectangle, with phi from the steel strain', () => {
  const f = fn('bimRcFlexure'), r = f(300, 450, 942, 420, 30, 200000);
  near(r.a, 51.718, 1e-3); near(r.c, 61.884, 1e-3); near(r.epst, 0.018815, 1e-6); assert.equal(r.phi, 0.9);
  near(r.Mn, 167.807, 1e-3); near(r.phiMn, 151.026, 1e-3);
  const t = f(300, 450, 4000, 420, 30, 200000);
  const a = 4000 * 420 / (0.85 * 30 * 300), c = a / (0.85 - 0.05 * 2 / 7), et = 0.003 * (450 - c) / c;
  near(t.phi, et >= 0.0051 ? 0.9 : (et <= 0.0021 ? 0.65 : 0.65 + 0.25 * (et - 0.0021) / 0.003), 1e-12, 'the transition zone');
  assert.ok(t.phi > 0.65 && t.phi < 0.9);
  assert.ok(f(300, 450, 20000, 420, 30, 200000).error, 'the neutral axis below the steel');
  assert.ok(f(300, 450, 942, 0, 30, 200000).error);
});
test('WO-06 ratio bands: none, low, mid, high, over', () => {
  const b = fn('bimCheckBand');
  assert.deepEqual([b(0), b(0.49), b(0.5), b(0.89), b(0.9), b(1), b(1.0001), b(null), b(undefined), b(NaN), b(-0.1), b(Infinity)],
    ['low', 'low', 'mid', 'mid', 'high', 'high', 'over', 'none', 'none', 'none', 'none', 'none']);
});
