// V175c steps 2 and 3: one editor, one print. WO-11 to WO-17 (sheets/layout-merge.js, moved here from the work order
// at WO-18) and WO-18's own pure parts (sheets/layout-open.js): a sheet as a drawing layout, its Draw menu, its vector page.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const fn = (n) => { assert.equal(typeof E[n], 'function', n + ' is not in the engine'); return E[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const VP = { id: 'vp-1', kind: 'view', refId: 'plan-L0', label: 'Ground', x: 20, y: 30, w: 120, h: 90, scaleMode: 'fixed', scaleDenom: 100 };
test('WO-11 a sheet viewport as the one viewport object (the board\'s map frame)', () => {
  assert.deepEqual(E.bimLmVpToFrame(VP), { t: 'map', id: 'vp-1', x: 20, y: 30, w: 120, h: 90, src: 'view:plan-L0', den: 100, fit: false, px: 0, py: 0, label: 'Ground' });
  const f = E.bimLmVpToFrame(Object.assign({}, VP, { scaleMode: 'fit', label: undefined }));
  assert.equal(f.den, null); assert.equal(f.fit, true); assert.equal(f.label, '');
});
test('WO-12 and back: a frame as a sheet viewport', () => {
  assert.deepEqual(E.bimLmFrameToVp(E.bimLmVpToFrame(VP)), VP);
  const v = E.bimLmFrameToVp({ id: 'm', src: 'schedule:doors:all', x: 0, y: 0, w: 10, h: 10, den: null });
  assert.deepEqual([v.kind, v.refId, v.scaleMode, v.scaleDenom], ['schedule', 'doors:all', 'fit', 100]);
});
test('WO-13 a sheet opens as a layout: a title block and a frame per viewport, its number kept', () => {
  const L = E.bimLmSheetToLayout({ id: 's1', number: 'A101', name: 'Plans', w: 420, h: 297, viewports: [VP] });
  assert.deepEqual([L.id, L.num, L.name, L.w, L.h, L.drawing], ['s1', 'A101', 'Plans', 420, 297, true]);
  assert.deepEqual(L.objs[0], { t: 'tblock', id: 'tb-s1', x: 0, y: 0, w: 420, h: 297 });
  assert.equal(L.objs[1].src, 'view:plan-L0');
  assert.equal(E.bimLmSheetToLayout({ id: 's2', w: 297, h: 210 }).objs.length, 1);
});
test('WO-14 a drawing sheet\'s Draw menu leaves out live values, figures and charts', () => {
  const items = [{ kind: 'text' }, { kind: 'live' }, { kind: 'figure' }, { kind: 'line' }, { kind: 'chart' }];
  assert.deepEqual(E.bimLmDrawMenu(items, true).map((x) => x.kind), ['text', 'line']);
  assert.equal(E.bimLmDrawMenu(items, false).length, 5);
});
test('WO-15 numbers for print: three decimals, never -0', () => {
  assert.equal(E.bimLmN(1.23456), '1.235'); assert.equal(E.bimLmN(-0.0001), '0'); assert.equal(E.bimLmN(420), '420');
});
test('WO-16 one vector print: the SVG page in millimetres', () => {
  assert.equal(E.bimLmSvgOpen(420, 297), '<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">');
});
test('WO-17 a frame\'s outline on the print', () => {
  assert.equal(E.bimLmSvgRect({ x: 20, y: 30.12345, w: 120, h: 90 }), '<rect x="20" y="30.123" width="120" height="90" fill="none" stroke="#000000" stroke-width="0.25"/>');
  assert.equal(E.bimLmSvgRect({ x: 0, y: 0, w: 1, h: 1 }, '#ff0000', 0.5), '<rect x="0" y="0" width="1" height="1" fill="none" stroke="#ff0000" stroke-width="0.5"/>');
});

/* ---------------- WO-18 sheets/layout-open.js ---------------- */
const SHEET = { id: 'sheet-1', number: 'A104', name: 'Ground floor', sizeKey: 'ANSI-B', w: 431.8, h: 279.4, viewports: [
  { id: 'vp-a', kind: 'plan', refId: 'lvl-0', label: 'Ground', x: 20, y: 25, w: 200, h: 150, scaleMode: 'ratio', scaleDenom: 100, pan: [1.5, -2] },
  { id: 'vp-b', kind: 'elevation', refId: 'front', label: 'Front', x: 230, y: 25, w: 150, h: 100, scaleMode: 'fit', scaleDenom: 100 },
  { id: 'vp-c', kind: 'schedule', refId: 'rooms', label: 'Rooms', x: 230, y: 140, w: 150, h: 60, scaleMode: 'fit', scaleDenom: 100 }] };
const FIT = () => ({ den: 200, px: 0.25, py: 0.5 });
test('WO-18 a sheet\'s page is the gallery\'s, by its key or its size', () => {
  assert.deepEqual(E.bimLoPage(SHEET), { key: 'ansi-B', o: 'l' });
  assert.deepEqual(E.bimLoPage({ sizeKey: 'pg:iso-A3:p', w: 297, h: 420 }), { key: 'iso-A3', o: 'p' });
  assert.equal(E.bimLoPage({ sizeKey: 'Custom', w: 333, h: 222 }), null);
});
test('WO-18 a sheet as a drawing layout: its frame, title block, viewports as frames at their scales, its schedule', () => {
  const r = E.bimLoFromSheet(SHEET, FIT, 'layer-0').rec;
  assert.equal(r.drawing, true); assert.equal(r.num, 'A104'); assert.equal(r.name, 'Ground floor'); assert.deepEqual(r.page, { key: 'ansi-B', o: 'l' });
  assert.deepEqual(r.objs.map((n) => n.t), ['border', 'tblock', 'map', 'map', 'sched']);
  assert.deepEqual(r.objs.map((n) => n.id), ['e1', 'e2', 'e3', 'e4', 'e5']);
  const a = r.objs[2], b = r.objs[3];
  assert.deepEqual([a.src, a.den, a.px, a.py, a.x, a.y, a.w, a.h, a.nm], ['plan:lvl-0', 100, 1.5, -2, 20, 25, 200, 150, 'Ground']);
  assert.deepEqual([b.src, b.den, b.px, b.py], ['elevation:front', 200, 0.25, 0.5], 'a fitted viewport takes the fitted scale');
  assert.equal(r.objs[1].num, 'A104');
  assert.equal(r.objs[4].src, 'rooms');
});
test('WO-18 a sheet a layout cannot hold yet is refused with the reason', () => {
  assert.match(E.bimLoFromSheet({ ...SHEET, sizeKey: 'Custom', w: 333, h: 222 }, FIT, 'layer-0').why, /page sizes/);
  const doors = { ...SHEET, viewports: [{ id: 'v', kind: 'schedule', refId: 'doors', label: 'Doors', x: 0, y: 0, w: 10, h: 10, scaleMode: 'fit', scaleDenom: 100 }] };
  assert.match(E.bimLoFromSheet(doors, FIT, 'layer-0').why, /Doors schedule/);
});
test('WO-18 a drawing layout\'s Draw menu leaves out the live values and the charts, and no separator is left doubled', () => {
  const L = E.bimBdeDrawKinds();
  const d = E.bimLoDrawKinds(L, true).map((k) => (k === '-' ? '-' : k[0]));
  assert.ok(!d.some((k) => /^lv(field|number|kpi|chart)$/.test(k)), d.join(','));
  assert.ok(d.includes('lvsched') && d.includes('map') && d.includes('rect'));
  assert.ok(!d.some((k, i) => k === '-' && d[i - 1] === '-') && d[d.length - 1] !== '-');
  assert.equal(E.bimLoDrawKinds(L, false).length, L.length, 'a board keeps them all');
});
test('WO-18 the vector page: the frames back as viewports at their scales and pans, shapes and text as SVG', () => {
  const B = { id: 'board-c1', name: 'Ground floor', num: 'A104', drawing: true, page: { key: 'ansi-B', o: 'l' },
    objs: E.bimLoFromSheet(SHEET, FIT, 'layer-0').rec.objs.concat([{ id: 'e9', t: 'text', x: 10, y: 10, w: 50, h: 8, s: 'Note & <b>', fs: 12, al: 'left', col: '#112233' }]) };
  const S = E.bimLoAsSheet(B);
  assert.equal(S.number, 'A104'); assert.ok(Math.abs(S.w - 431.8) < 0.01);
  assert.deepEqual(S.viewports.map((v) => [v.kind, v.refId, v.scaleMode, v.scaleDenom]),
    [['plan', 'lvl-0', 'ratio', 100], ['elevation', 'front', 'ratio', 200], ['schedule', 'rooms', 'fit', 100]]);
  assert.deepEqual(S.viewports[0].pan, [1.5, -2]);
  const svg = E.bimLoShapesSvg(B);
  assert.match(svg, /<text x="10" y="[0-9.]+" font-size="3\.175"[^>]*fill="#112233">Note &amp; &lt;b&gt;<\/text>/);
  assert.match(E.bimLoLayoutSvg({ ...B, objs: B.objs.concat([{ id: 'e10', t: 'kpi', x: 0, y: 0, w: 1, h: 1 }]) }, 'technical').why, /indicator/);
  assert.equal(E.bimLoLayoutSvg({ ...B, drawing: false }, 'technical').why, 'not a drawing layout');
});
