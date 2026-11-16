/* V229's work-order tests (docs/work-orders/v229/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/bim/split-grammar.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v229/v229.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v229/v229.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimSgSizes", "bimSgSplit", "bimSgRepeat", "bimSgValidate", "bimSgDerive"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/split-grammar.js'), 'utf8');
  if (process.env.V229_REF) src += fs.readFileSync(process.env.V229_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/split-grammar.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// the research's e02 facade: a ground floor, storeys, bays, and in each bay a pier, a window column, a pier
const RULES = () => ({
  Facade: { op: 'split', axis: 'y', parts: [['ground', 'Ground'], [{ fl: 1 }, 'Upper']] },
  Ground: { op: 'repeat', axis: 'x', size: 'bay', rule: 'Shopfront' },
  Upper: { op: 'repeat', axis: 'y', size: 'floor', rule: 'Floor' },
  Floor: { op: 'repeat', axis: 'x', size: 'bay', rule: 'Bay' },
  Bay: { op: 'split', axis: 'x', parts: [[{ fl: 1 }, 'Pier'], ['win', 'Col'], [{ fl: 1 }, 'Pier']] },
  Col: { op: 'split', axis: 'y', parts: [['sill', 'Spandrel'], ['winH', 'Window'], [{ fl: 1 }, 'Spandrel']] },
  Shopfront: { op: 'element', kind: 'opening' }, Pier: { op: 'element', kind: 'wall' },
  Spandrel: { op: 'element', kind: 'wall' }, Window: { op: 'element', kind: 'window' }
});
const P = () => ({ ground: 4.5, floor: 3.5, bay: 1.2, win: 0.8, sill: 0.9, winH: 1.6 });
test('WO-01 sizes in a split: absolute, relative to the scope, floating shares of what is left', () => {
  const sz = fn('bimSgSizes');
  assert.deepEqual(sz(10, [2, { fl: 1 }, 3]), [2, 5, 3]);
  assert.deepEqual(sz(10, [{ rel: 0.25 }, { fl: 1 }, { fl: 3 }]), [2.5, 1.875, 5.625]);
  assert.deepEqual(sz(10, [6, 6, { fl: 1 }]), [6, 6, 0]);
  assert.deepEqual(sz(10, [-2, { fl: -1 }, { rel: -1 }, 4]), [0, 0, 0, 4]);
  assert.deepEqual(sz(10, []), []);
  assert.deepEqual(sz(10, [{ fl: 2 }]), [10]);
});
test('WO-02 a split cut at the scope: parts placed in order, the overrun cut, empty parts left out', () => {
  const sp = fn('bimSgSplit');
  assert.deepEqual(sp(10, [2, { fl: 1 }, 3]), [{ i: 0, at: 0, size: 2 }, { i: 1, at: 2, size: 5 }, { i: 2, at: 7, size: 3 }]);
  assert.deepEqual(sp(10, [6, 6, { fl: 1 }, 1]), [{ i: 0, at: 0, size: 6 }, { i: 1, at: 6, size: 4 }]);
  assert.deepEqual(sp(10, [0, 4]), [{ i: 1, at: 0, size: 4 }]);
  assert.deepEqual(sp(0, [1, 2]), []);
});
test('WO-03 a repeat to the nearest count, at least one, a half going up', () => {
  const rp = fn('bimSgRepeat');
  assert.deepEqual(rp(35, 3.5), { n: 10, size: 3.5 });
  const a = rp(35.1, 3.5); assert.equal(a.n, 10); near(a.size, 3.51);
  const b = rp(36.8, 3.5); assert.equal(b.n, 11); near(b.size, 36.8 / 11);
  assert.deepEqual(rp(1, 3.5), { n: 1, size: 1 });
  assert.equal(rp(8.75, 3.5).n, 3);
  assert.deepEqual(rp(0, 3.5), { n: 0, size: 0 });
  assert.deepEqual(rp(10, 0), { n: 0, size: 0 });
  assert.deepEqual(rp(10, -1), { n: 0, size: 0 });
});
test('WO-04 the rules checked before anything runs', () => {
  const va = fn('bimSgValidate');
  assert.deepEqual(va(RULES(), 'Facade'), { ok: true });
  assert.deepEqual(va(RULES(), 'Roof'), { error: 'no start rule Roof' });
  let r = RULES(); r.Bay.op = 'extrude'; assert.deepEqual(va(r, 'Facade'), { error: 'unknown op in Bay' });
  r = RULES(); r.Floor.axis = 'z'; assert.deepEqual(va(r, 'Facade'), { error: 'bad axis in Floor' });
  r = RULES(); r.Col.parts = []; assert.deepEqual(va(r, 'Facade'), { error: 'no parts in Col' });
  r = RULES(); delete r.Window.kind; assert.deepEqual(va(r, 'Facade'), { error: 'no kind in Window' });
  r = RULES(); delete r.Pier; assert.deepEqual(va(r, 'Facade'), { error: 'missing rule Pier in Bay' });
  r = RULES(); r.Shopfront = { op: 'repeat', axis: 'x', size: 1, rule: 'Ground' }; assert.deepEqual(va(r, 'Facade'), { error: 'cycle at Ground' });
});
test('WO-05 a facade derived into leaves with their paths; sizes by parameter name; refusals', () => {
  const de = fn('bimSgDerive');
  const out = de(RULES(), 'Facade', { w: 9.6, h: 39.5 }, P());
  const by = {}; out.leaves.forEach((l) => { by[l.rule] = (by[l.rule] || 0) + 1; });
  assert.deepEqual(by, { Shopfront: 8, Pier: 160, Spandrel: 160, Window: 80 });
  assert.equal(out.steps, 581);
  assert.deepEqual(out.leaves[0], { rule: 'Shopfront', kind: 'opening', path: [['Facade', 0], ['Ground', 0], ['Shopfront', 0]], x: 0, y: 0, w: 1.2, h: 4.5 });
  const w = out.leaves.filter((l) => l.rule === 'Window' && l.path[2][1] === 3 && l.path[3][1] === 2)[0];
  assert.deepEqual(w.path, [['Facade', 0], ['Upper', 0], ['Floor', 3], ['Bay', 2], ['Col', 0], ['Window', 0]]);
  near(w.x, 2.4 + 0.2); near(w.y, 4.5 + 3 * 3.5 + 0.9); near(w.w, 0.8); near(w.h, 1.6);
  // the second pier of a bay and the upper spandrel are index 1 of their rule, whatever is cut before them
  const piers = out.leaves.filter((l) => l.rule === 'Pier' && l.path[2][1] === 0 && l.path[3][1] === 0);
  assert.deepEqual(piers.map((p) => p.path[4]), [['Pier', 0], ['Pier', 1]]);
  // an origin is carried; a change that keeps the counts keeps every path
  const o2 = de(RULES(), 'Facade', { x: 5, y: 1, w: 9.6, h: 39.5 }, Object.assign(P(), { win: 1.0 }));
  assert.equal(o2.leaves[0].x, 5); assert.equal(o2.leaves[0].y, 1);
  assert.deepEqual(o2.leaves.map((l) => l.path), out.leaves.map((l) => l.path));
  // refusals
  assert.deepEqual(de(RULES(), 'Roof', { w: 1, h: 1 }, P()), { error: 'no start rule Roof' });
  const p = P(); delete p.bay; assert.deepEqual(de(RULES(), 'Facade', { w: 9.6, h: 39.5 }, p), { error: 'bad size in Ground' });
  const q = P(); q.sill = -1; assert.deepEqual(de(RULES(), 'Facade', { w: 9.6, h: 39.5 }, q), { error: 'bad size in Col' });
  assert.deepEqual(de(RULES(), 'Facade', { w: 9.6, h: 39.5 }, P(), 100), { error: 'more than 100 shapes' });
});
