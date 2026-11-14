/* V175c's work-order tests (docs/work-orders/v175c/SPEC.md, WO-11 to WO-17): the pure functions of src/js/engine/sheets/layout-merge.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v175c/v175c-step2.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v175c/v175c-step2.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimLmVpToFrame", "bimLmFrameToVp", "bimLmSheetToLayout", "bimLmDrawMenu", "bimLmN", "bimLmSvgOpen", "bimLmSvgRect"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/sheets/layout-merge.js'), 'utf8');
  if (process.env.V175c_REF) src += fs.readFileSync(process.env.V175c_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/sheets/layout-merge.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const VP = { id: 'vp-1', kind: 'view', refId: 'plan-L0', label: 'Ground', x: 20, y: 30, w: 120, h: 90, scaleMode: 'fixed', scaleDenom: 100 };
test('WO-11 a sheet viewport as the one viewport object (the board\'s map frame)', () => {
  assert.deepEqual(fn('bimLmVpToFrame')(VP), { t: 'map', id: 'vp-1', x: 20, y: 30, w: 120, h: 90, src: 'view:plan-L0', den: 100, fit: false, px: 0, py: 0, label: 'Ground' });
  const f = fn('bimLmVpToFrame')(Object.assign({}, VP, { scaleMode: 'fit', label: undefined }));
  assert.equal(f.den, null); assert.equal(f.fit, true); assert.equal(f.label, '');
});
test('WO-12 and back: a frame as a sheet viewport', () => {
  assert.deepEqual(fn('bimLmFrameToVp')(X.bimLmVpToFrame(VP)), VP);
  const v = fn('bimLmFrameToVp')({ id: 'm', src: 'schedule:doors:all', x: 0, y: 0, w: 10, h: 10, den: null });
  assert.deepEqual([v.kind, v.refId, v.scaleMode, v.scaleDenom], ['schedule', 'doors:all', 'fit', 100]);
});
test('WO-13 a sheet opens as a layout: a title block and a frame per viewport, its number kept', () => {
  const L = fn('bimLmSheetToLayout')({ id: 's1', number: 'A101', name: 'Plans', w: 420, h: 297, viewports: [VP] });
  assert.deepEqual([L.id, L.num, L.name, L.w, L.h, L.drawing], ['s1', 'A101', 'Plans', 420, 297, true]);
  assert.deepEqual(L.objs[0], { t: 'tblock', id: 'tb-s1', x: 0, y: 0, w: 420, h: 297 });
  assert.equal(L.objs[1].src, 'view:plan-L0');
  assert.equal(fn('bimLmSheetToLayout')({ id: 's2', w: 297, h: 210 }).objs.length, 1);
});
test('WO-14 a drawing sheet\'s Draw menu leaves out live values, figures and charts', () => {
  const items = [{ kind: 'text' }, { kind: 'live' }, { kind: 'figure' }, { kind: 'line' }, { kind: 'chart' }];
  assert.deepEqual(fn('bimLmDrawMenu')(items, true).map((x) => x.kind), ['text', 'line']);
  assert.equal(fn('bimLmDrawMenu')(items, false).length, 5);
});
test('WO-15 numbers for print: three decimals, never -0', () => {
  assert.equal(fn('bimLmN')(1.23456), '1.235'); assert.equal(fn('bimLmN')(-0.0001), '0'); assert.equal(fn('bimLmN')(420), '420');
});
test('WO-16 one vector print: the SVG page in millimetres', () => {
  assert.equal(fn('bimLmSvgOpen')(420, 297), '<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">');
});
test('WO-17 a frame\'s outline on the print', () => {
  assert.equal(fn('bimLmSvgRect')({ x: 20, y: 30.12345, w: 120, h: 90 }), '<rect x="20" y="30.123" width="120" height="90" fill="none" stroke="#000000" stroke-width="0.25"/>');
  assert.equal(fn('bimLmSvgRect')({ x: 0, y: 0, w: 1, h: 1 }, '#ff0000', 0.5), '<rect x="0" y="0" width="1" height="1" fill="none" stroke="#ff0000" stroke-width="0.5"/>');
});
