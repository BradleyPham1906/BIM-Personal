/* V241's work-order tests (docs/work-orders/v241/SPEC.md): the pure functions of src/js/engine/structure/seismic-elf.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v241/v241.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v241/v241.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text.
   Expected numbers come from the research's worked examples (docs/research/research-physical-world/ and
   docs/research/experiments/physical-world/), not from the implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimSeisSa', 'bimSeisSaMulti', 'bimSeisTa', 'bimSeisCu', 'bimSeisCs', 'bimSeisFx', 'bimSeisUsgsUrl', 'bimSeisUsgsRead', 'bimSeisDrift'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/structure/seismic-elf.js'), 'utf8');
  if (process.env.V241_REF) src += fs.readFileSync(process.env.V241_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/structure/seismic-elf.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const EXP = path.join(ROOT, 'docs/research/experiments/physical-world');
const LA = JSON.parse(fs.readFileSync(path.join(EXP, 'usgs-asce7-22-la-siteC-rcII.json'), 'utf8'));
const OCEAN = JSON.parse(fs.readFileSync(path.join(EXP, 'usgs-asce7-22-ocean-error.json'), 'utf8'));
const P = { sds: 1.46, sd1: 0.70, tl: 8 };
test('WO-01 the two-period design spectrum, its four branches', () => {
  const s = fn('bimSeisSa'), T0 = 0.2 * 0.7 / 1.46, Ts = 0.7 / 1.46;
  near(s(0, P), 0.4 * 1.46, 1e-12); near(s(T0 / 2, P), 1.46 * 0.7, 1e-12); near(s(T0, P), 1.46, 1e-12);
  near(s(Ts, P), 1.46, 1e-12); near(s(1, P), 0.7, 1e-12); near(s(8, P), 0.7 / 8, 1e-12); near(s(10, P), 0.7 * 8 / 100, 1e-12);
  assert.ok(Number.isNaN(s(-1, P))); assert.ok(Number.isNaN(s(1, { sds: 1, sd1: 0, tl: 8 })));
});
test('WO-02 the multi-period spectrum: linear between the USGS periods, then 1/T and TL/T^2', () => {
  const s = fn('bimSeisSaMulti'), p = LA.response.data.multiPeriodDesignSpectrum;
  near(s(0.598202866, p.periods, p.ordinates, 8), 1.0439, 5e-5, 'the research\'s method 1 value');
  near(s(0.2, p.periods, p.ordinates, 8), 1.62, 1e-12); near(s(0, p.periods, p.ordinates, 8), 0.65, 1e-12);
  near(s(0.125, p.periods, p.ordinates, 8), 1.43, 1e-12); near(s(0.0875, p.periods, p.ordinates, 8), 1.235, 1e-12);
  near(s(12, [0, 10], [1, 0.042], 16), 0.042 * 10 / 12, 1e-12); near(s(20, [0, 10], [1, 0.042], 16), 0.042 * 10 * 16 / 400, 1e-12);
  near(s(12, [0, 10], [1, 0.042], 8), 0.042 * 10 * 8 / 144, 1e-12, 'TL below 10 s');
  assert.ok(Number.isNaN(s(1, [0], [1], 8))); assert.ok(Number.isNaN(s(1, [0, 1], [1], 8))); assert.ok(Number.isNaN(s(-1, [0, 1], [1, 1], 8)));
});
test('WO-03 approximate period Ta = Ct hn^x (Table 12.8-2, hn in m)', () => {
  const t = fn('bimSeisTa');
  near(t('steel-mrf', 14), 0.5982, 5e-5); near(t('steel-mrf', 14), 0.0724 * Math.pow(14, 0.8), 5e-4, 'the SI Ct, rounded');
  near(t('concrete-mrf', 20), 0.016 * Math.pow(20 / 0.3048, 0.9), 1e-12); near(t('steel-ebf', 20), 0.03 * Math.pow(20 / 0.3048, 0.75), 1e-12);
  near(t('steel-brbf', 20), t('steel-ebf', 20), 1e-12); near(t('shear-wall', 20), 0.02 * Math.pow(20 / 0.3048, 0.75), 1e-12);
  assert.ok(Number.isNaN(t('steel-mrf', 0)));
});
test('WO-04 Cu by SD1 (Table 12.8-1), the lower value between rows', () => {
  const c = fn('bimSeisCu');
  assert.equal(c(0.7), 1.4); assert.equal(c(0.4), 1.4); assert.equal(c(0.3), 1.4); assert.equal(c(0.25), 1.5);
  assert.equal(c(0.2), 1.5); assert.equal(c(0.15), 1.6); assert.equal(c(0.12), 1.7); assert.equal(c(0.05), 1.7); assert.ok(Number.isNaN(c(-1)));
});
test('WO-05 Cs, method 2: the research\'s 4-storey steel SMF (V 1170.2 kN)', () => {
  const c = fn('bimSeisCs'), o = { sds: 1.46, sd1: 0.7, s1: 0.75, tl: 8, R: 8, Ie: 1, T: 0.5982028664659826 };
  const r = c(o); near(r.cs * 8000, 1170.17, 0.01); assert.equal(r.governs, 'sd1');
  assert.deepEqual(c({ ...o, T: 0.3 }), { cs: 1.46 / 8, governs: 'sds' });
  near(c({ ...o, T: 10 }).cs, 0.044 * 1.46, 1e-12); assert.equal(c({ ...o, T: 10 }).governs, 'min');
  near(c({ ...o, sds: 0.9, T: 10 }).cs, 0.5 * 0.75 / 8, 1e-12, 'S1 >= 0.6 bound above 0.044 SDS'); assert.equal(c({ ...o, sds: 0.9, T: 10 }).governs, 's1');
  assert.equal(c({ ...o, sds: 0.9, s1: 0.59, T: 10 }).governs, 'min', 'S1 below 0.6: no S1 bound');
  const lowS1 = { ...o, s1: 0.4, T: 9 }; near(c(lowS1).cs, Math.max(0.7 * 8 / (81 * 8), 0.044 * 1.46), 1e-12); assert.equal(c(lowS1).governs, 'min');
  const tl = c({ ...o, s1: 0.1, sds: 0.1, sd1: 0.3, T: 9, R: 2 }); near(tl.cs, 0.3 * 8 / (81 * 2), 1e-12); assert.equal(tl.governs, 'tl');
  near(c({ ...o, sds: 0.1, sd1: 0.05, s1: 0.05, T: 3 }).cs, 0.01, 1e-12, 'never below 0.01');
  near(c({ ...o, Ie: 1.5 }).cs, 0.7 / (0.5982028664659826 * 8 / 1.5), 1e-12, 'Ie divides R');
});
test('WO-05 Cs, method 1 (Sa(T) given) keeps the lower bounds', () => {
  const c = fn('bimSeisCs'), o = { sds: 1.46, sd1: 0.7, s1: 0.75, tl: 8, R: 8, Ie: 1, T: 0.5982, method: 1 };
  near(c({ ...o, sa: 1.0439409 }).cs * 8000, 1043.94, 0.01); assert.equal(c({ ...o, sa: 1.0439409 }).governs, 'sa');
  near(c({ ...o, sa: 0.2 }).cs, 0.044 * 1.46, 1e-12); near(c({ ...o, sds: 0.9, sa: 0.2 }).cs, 0.5 * 0.75 / 8, 1e-12); assert.ok(c({ ...o, sa: undefined }).error); assert.ok(c({ ...o, R: 0 }).error);
});
test('WO-06 vertical distribution: k, Cvx, Fx and storey shears', () => {
  const f = fn('bimSeisFx')([2000, 2000, 2000, 2000], [3.5, 7, 10.5, 14], 1170.17, 0.5982028664659826);
  near(f.k, 1.0491, 5e-5);
  [111.3, 230.2, 352.3, 476.4].forEach((v, i) => near(f.F[i], v, 0.05));
  [1170.2, 1058.9, 828.7, 476.4].forEach((v, i) => near(f.shear[i], v, 0.05));
  near(f.cvx.reduce((a, b) => a + b, 0), 1, 1e-12);
  const g = fn('bimSeisFx');
  assert.equal(g([1, 1], [3, 6], 10, 0.4).k, 1); assert.equal(g([1, 1], [3, 6], 10, 3).k, 2); near(g([1, 1], [3, 6], 10, 1.5).k, 1.5, 1e-12);
  near(g([1, 1], [3, 6], 10, 3).F[1], 10 * 36 / 45, 1e-12, 'k = 2 weights by h^2');
  near(g([5, 5], [6, 3], 9, 0.2).shear[1], 9, 1e-12, 'shears follow height, not list order');
  assert.ok(g([1], [3, 6], 10, 1).error); assert.ok(g([0, 0], [3, 6], 10, 1).error); assert.ok(g([1, 1], [0, 6], 10, 1).error);
});
test('WO-07 the USGS request: the new address, a check of every field', () => {
  const u = fn('bimSeisUsgsUrl');
  assert.equal(u(34, -118, 'II', 'C', 'A b&c').url,
    'https://earthquake.usgs.gov/ws/building-codes/asce7-22/calculate?latitude=34&longitude=-118&riskCategory=II&siteClass=C&title=A%20b%26c');
  assert.ok(u(34, -118, 'II', 'BC', 't').url.indexOf('siteClass=BC') > 0); assert.ok(u(34, -118, 'IV', 'Default', 't').url);
  assert.ok(u(91, 0, 'II', 'C', 't').error); assert.ok(u(0, 181, 'II', 'C', 't').error); assert.ok(u(0, 0, 'V', 'C', 't').error);
  assert.ok(u(0, 0, 'II', 'F', 't').error); assert.ok(u(0, 0, 'II', 'C', '').error);
});
test('WO-08 reading the USGS answer, and its error that comes back with HTTP 200', () => {
  const r = fn('bimSeisUsgsRead');
  const a = r(LA);
  assert.deepEqual([a.sds, a.sd1, a.ss, a.s1, a.tl, a.ts, a.t0, a.sdc], [1.46, 0.7, 2.15, 0.75, 8, 0.479, 0.0958, 'D']);
  assert.equal(a.periods.length, 22); assert.equal(a.sa.length, 22); assert.equal(a.sa[8], 1.62);
  a.sa[0] = 99; assert.equal(LA.response.data.multiPeriodDesignSpectrum.ordinates[0], 0.65, 'the answer is not changed');
  assert.deepEqual(r(OCEAN), { error: 'Location [-140.0, 30.0] out of bounds' });
  assert.ok(r(null).error); assert.ok(r({ request: { status: 'success' }, response: { data: { sds: 1 } } }).error);
  const noSpec = r({ request: { status: 'success' }, response: { data: { sds: 1, sd1: 1, ss: 1, s1: 1, tl: 8, ts: 1, t0: 0.2 } } });
  assert.deepEqual([noSpec.periods, noSpec.sa, noSpec.sdc], [[], [], '']);
});
test('WO-09 storey drift: Cd delta / Ie per storey against a limit times its height', () => {
  const d = fn('bimSeisDrift')([0.002382, 0.006525, 0.011820, 0.017671], [3.5, 7, 10.5, 14], 5.5, 1, 0.02);
  [13.101, 22.7865, 29.1225, 32.1805].forEach((v, i) => near(d[i].drift * 1000, v, 1e-6));
  assert.ok(d.every((x) => x.ok)); near(d[3].ratio, 0.0321805 / 3.5, 1e-12);
  const e = fn('bimSeisDrift')([0.02], [3], 5.5, 1.25, 0.025); near(e[0].drift, 0.088, 1e-12); assert.equal(e[0].ok, false);
  assert.ok(fn('bimSeisDrift')([0.01, 0.02], [3, 3], 5.5, 1, 0.02).error); assert.ok(fn('bimSeisDrift')([0.01], [3], 0, 1, 0.02).error);
});
