/* V244's work-order tests (docs/work-orders/v244/SPEC.md): the pure functions of src/js/engine/structure/steel-checks.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v244/v244.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v244/v244.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text.
   Expected numbers come from the research's worked examples (docs/research/research-physical-world/ and
   docs/research/experiments/physical-world/), not from the implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimStIProps', 'bimStCompact', 'bimStPhiPn', 'bimStLpLr', 'bimStPhiMn', 'bimStCb', 'bimStH1'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/structure/steel-checks.js'), 'utf8');
  if (process.env.V244_REF) src += fs.readFileSync(process.env.V244_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/structure/steel-checks.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const IN = 25.4;
/* W10x49 from the AISC Shapes Database as the research read it (member-checks-cracking.md 4.2), in mm */
const W = { A: 14.4 * IN ** 2, rx: 4.35 * IN, ry: 2.54 * IN, Zx: 60.4 * IN ** 3, Sx: 54.6 * IN ** 3, J: 1.39 * IN ** 4, rts: 2.84 * IN, ho: 9.44 * IN };
test('WO-01 an I section from its plates (no fillets): within 2% of the table, J lower', () => {
  const p = fn('bimStIProps')(10 * IN, 10 * IN, 0.56 * IN, 0.34 * IN);
  near(p.A / W.A, 1, 0.015); near(p.Zx / W.Zx, 1, 0.015); near(p.Sx / W.Sx, 1, 0.015); near(p.ry / W.ry, 1, 0.01);
  near(p.rts / W.rts, 1, 0.01); near(p.ho, W.ho, 1e-9); assert.ok(p.J < W.J && p.J > 0.9 * W.J);
  const q = fn('bimStIProps')(200, 100, 10, 6);
  near(q.A, 2 * 100 * 10 + 180 * 6, 1e-9); near(q.Zx, 100 * 10 * 190 + 6 * 180 * 180 / 4, 1e-9);
  near(q.Ix, (100 * 200 ** 3 - 94 * 180 ** 3) / 12, 1e-6); near(q.Iy, (2 * 10 * 100 ** 3 + 180 * 6 ** 3) / 12, 1e-6);
  near(q.J, (2 * 100 * 1000 + 190 * 216) / 3, 1e-9); near(q.Cw, q.Iy * 190 * 190 / 4, 1e-3); assert.equal(q.h, 180);
  assert.ok(fn('bimStIProps')(20, 100, 10, 6).error); assert.ok(fn('bimStIProps')(200, 100, 10, 0).error);
});
test('WO-02 compactness (B4.1a and b) of the W10x49 and of thin plates', () => {
  const c = fn('bimStCompact');
  assert.deepEqual(c(10, 0.56, 23.1 * 0.34, 0.34, 345, 200000), { flange: 'compact', web: 'compact', flangeComp: 'nonslender', webComp: 'nonslender' });
  const s = Math.sqrt(200000 / 345);
  assert.equal(c(2 * 0.38 * s * 10 + 0.01, 10, 100, 10, 345, 200000).flange, 'noncompact');
  assert.equal(c(2 * s * 10 + 0.01, 10, 100, 10, 345, 200000).flange, 'slender');
  assert.equal(c(100, 10, 3.76 * s * 5, 5, 345, 200000).web, 'compact'); assert.equal(c(100, 10, 3.77 * s * 5, 5, 345, 200000).web, 'noncompact');
  assert.equal(c(100, 10, 5.71 * s * 5, 5, 345, 200000).web, 'slender'); assert.equal(c(100, 10, 1.5 * s * 5, 5, 345, 200000).webComp, 'slender');
  assert.ok(c(0, 1, 1, 1, 345, 200000).error);
});
test('WO-03 compression, E3: the research\'s W10x49 column, 4 m, phi Pn 2178 kN', () => {
  const r = fn('bimStPhiPn')(W.A, W.ry, 4000, 345, 200000);
  near(r.slender, 62.0, 0.01); near(r.Fe, 513.5, 0.05); near(r.Fn, 260.4, 0.05); near(r.Pn, 2419.5, 0.1); near(r.phiPn, 2177.5, 0.1);
  const e = fn('bimStPhiPn')(W.A, W.ry, 12000, 345, 200000);
  assert.ok(e.slender > 4.71 * Math.sqrt(200000 / 345)); near(e.Fn, 0.877 * e.Fe, 1e-9, 'elastic buckling above 4.71 sqrt(E/Fy)');
  assert.ok(fn('bimStPhiPn')(W.A, 0, 4000, 345, 200000).error);
});
test('WO-04 Lp and Lr, F2-5 and F2-6', () => {
  const r = fn('bimStLpLr')(W.ry, W.rts, W.J, W.Sx, W.ho, 345, 200000);
  near(r.Lp, 2733.9, 0.1); near(r.Lr, 9631.3, 0.1); assert.ok(fn('bimStLpLr')(W.ry, W.rts, 0, W.Sx, W.ho, 345, 200000).error);
});
test('WO-05 flexure, F2: plastic, inelastic and elastic lateral-torsional buckling', () => {
  const m = fn('bimStPhiMn'), o = { Zx: W.Zx, Sx: W.Sx, Fy: 345, E: 200000, Lp: 2733.92, Lr: 9631.34, rts: W.rts, J: W.J, ho: W.ho };
  near(m({ ...o, Lb: 2000 }).Mn, 341.474, 1e-3); assert.equal(m({ ...o, Lb: 2000 }).zone, 'plastic');
  const r = m({ ...o, Lb: 4000, Cb: 1 }); near(r.Mn, 318.456, 1e-3); near(r.phiMn, 286.611, 1e-3); assert.equal(r.zone, 'inelastic');
  near(m({ ...o, Lb: 4000, Cb: 1.67 }).Mn, 341.474, 1e-3, 'Cb raises it to Mp, never above');
  near(m({ ...o, Lb: 4000 }).Mn, 318.456, 1e-3, 'Cb defaults to 1');
  near(m({ ...o, Lb: 8000, Cb: 1 }).Mn, 245.7, 0.05);
  const e = m({ ...o, Lb: 12000, Cb: 1 }), s = 12000 / W.rts;
  near(e.Mn, Math.PI ** 2 * 200000 / s ** 2 * Math.sqrt(1 + 0.078 * W.J / (W.Sx * W.ho) * s * s) * W.Sx / 1e6, 1e-9); assert.equal(e.zone, 'elastic');
  assert.ok(m({ ...o, Lb: 4000, Lr: 1000 }).error);
});
test('WO-06 Cb from the quarter-point moments (F1-1)', () => {
  const c = fn('bimStCb');
  near(c(1, 1, 1, 1), 1, 1e-12); near(c(1, 0.25, 0.5, 0.75), 1.6667, 5e-5); near(c(1, 0.75, 1, 0.75), 1.13636, 5e-6);
  near(c(-1, -0.25, 0.5, -0.75), c(1, 0.25, 0.5, 0.75), 1e-12, 'absolute values'); assert.equal(c(0, 0, 0, 0), 1);
});
test('WO-07 combined forces, H1-1a and H1-1b, the research\'s three cases', () => {
  const h = fn('bimStH1');
  const a = h(1000, 2177.54, 100, 286.611, 0, 100); near(a.ratio, 0.7694, 5e-5); assert.equal(a.eq, 'H1-1a');
  const Mcy = 0.9 * Math.min(345 * 28.3 * IN ** 3, 1.6 * 345 * 18.7 * IN ** 3) / 1e6;
  const b = h(200, 2177.54, 150, 286.611, 20, Mcy); near(b.ratio, 0.708, 5e-4); assert.equal(b.eq, 'H1-1b');
  near(h(1800, 2177.54, 60, 286.611, 10, Mcy).ratio, 1.074, 5e-4);
  near(h(-1000, 2177.54, -100, 286.611, 0, 100).ratio, a.ratio, 1e-12); assert.equal(h(400, 2000, 0, 1, 0, 1).eq, 'H1-1a', 'Pr/Pc = 0.2 uses H1-1a'); assert.equal(h(399, 2000, 0, 1, 0, 1).eq, 'H1-1b');
  assert.ok(h(1, 0, 1, 1, 1, 1).error);
});
