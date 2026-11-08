/* V174b to V174d: arranging a board's objects (sheets/board-arrange.js, the stacks in board-objects.js), pages from
   the registry (sheets/page-sizes.js) and the scale bar (sheets/board-map.js).
   docs/research/research-presentation-boards.md, 4.4 to 4.6, D7 to D18. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const A3D = E.A3D;
const D = globalThis.window.__a3dBoardDesign;
const near = (a, b, msg) => assert.ok(Math.abs(a - b) < 1e-6, (msg || '') + ' ' + a + ' vs ' + b);
const box = (x, y, w, h) => ({ x, y, w, h });

/* ---- V174b ---- */
test('align: to the selection\'s bounds; one box to the page', () => {
  const B = [box(10, 0, 20, 10), box(40, 5, 10, 10)];
  assert.deepEqual(E.bimBalAlign(B, 'left').map((p) => p.x), [10, 10]);
  assert.deepEqual(E.bimBalAlign(B, 'right').map((p) => p.x), [30, 40]);
  assert.deepEqual(E.bimBalAlign(B, 'vcenter').map((p) => p.y), [2.5, 2.5]);
  assert.deepEqual(E.bimBalAlign([box(10, 10, 20, 10)], 'hcenter', box(0, 0, 400, 300))[0], { x: 190, y: 10 });
});

test('distribute keeps the outermost two and spaces the rest in equal gaps; fewer than three stay (D9)', () => {
  const r = E.bimBalDistribute([box(0, 0, 10, 10), box(15, 0, 10, 10), box(90, 0, 10, 10)], 'x');
  assert.deepEqual(r.pos.map((p) => p.x), [0, 45, 90]);
  near(r.step, 35);
  assert.equal(E.bimBalDistribute([box(0, 0, 10, 10), box(50, 0, 10, 10)], 'x').step, null);
  /* a wide box: the least left edge and the greatest right edge stay */
  const w = E.bimBalDistribute([box(0, 0, 100, 10), box(20, 0, 10, 10), box(50, 0, 10, 10), box(110, 0, 10, 10)], 'x');
  assert.equal(w.pos[0].x, 0);
  near(w.pos[3].x, 110);
});

test('tidy up uses the most common gap', () => {
  const r = E.bimBalTidy([box(0, 0, 10, 10), box(15, 0, 10, 10), box(30, 0, 10, 10), box(70, 0, 10, 10)], 'x');
  assert.equal(r.gap, 5);
  assert.deepEqual(r.pos.map((p) => p.x), [0, 15, 30, 45]);
});

test('smart spacing: an equal gap after a pair, and an edge (the research\'s own check)', () => {
  const G = E.bimBalGaps([box(0, 0, 50, 50), box(150, 0, 50, 50), box(300, 0, 50, 50)]);
  assert.equal(G.H.length, 3);
  let r = E.bimBalSnap(box(455, 10, 50, 30), G, 12);
  assert.equal(r.x.kind, 'after');
  near(r.x.d, -5);
  r = E.bimBalSnap(box(352, 10, 50, 30), G, 12);
  assert.equal(r.x.kind, 'point');
  near(r.x.d, -2);
  assert.equal(E.bimBalSnap(box(600, 400, 10, 10), G, 12).x, null, 'nothing within the threshold');
});

test('auto layout: a hugging row with a gap and padding; Fill shares a fixed width; Auto spreads (D7, D8)', () => {
  let r = E.bimBalLayout({ dir: 'row', gap: 5, pad: 2, sizeW: 'hug', sizeH: 'hug', children: [{ w: 10, h: 4 }, { w: 20, h: 8 }] });
  assert.deepEqual(r.kids, [{ x: 2, y: 2, w: 10, h: 4 }, { x: 17, y: 2, w: 20, h: 8 }]);
  assert.equal(r.w, 39); assert.equal(r.h, 12);
  r = E.bimBalLayout({ dir: 'row', gap: 0, pad: 0, sizeW: 'fixed', w: 100, sizeH: 'hug', children: [{ w: 30, h: 5 }, { w: 0, h: 5, sizeW: 'fill' }] });
  assert.equal(r.kids[1].w, 70);
  r = E.bimBalLayout({ dir: 'row', gap: 'auto', pad: 0, sizeW: 'fixed', w: 100, sizeH: 'hug', children: [{ w: 10, h: 5 }, { w: 10, h: 5 }, { w: 10, h: 5 }] });
  assert.deepEqual(r.kids.map((k) => k.x), [0, 45, 90]);
  r = E.bimBalLayout({ dir: 'row', wrap: true, gap: 5, pad: 0, sizeW: 'fixed', w: 30, sizeH: 'hug', children: [{ w: 20, h: 5 }, { w: 20, h: 5 }] });
  assert.deepEqual(r.kids.map((k) => [k.x, k.y]), [[0, 0], [0, 10]], 'wrap breaks before the item that would not fit');
  r = E.bimBalLayout({ dir: 'column', gap: 2, pad: 0, sizeW: 'hug', sizeH: 'hug', alignCross: 'center', children: [{ w: 10, h: 5 }, { w: 30, h: 5 }] });
  assert.deepEqual(r.kids.map((k) => [k.x, k.y]), [[10, 0], [0, 7]]);
});

test('a layer\'s stack on a board places its objects in Draw order; a phone shows a row as a column (D11)', () => {
  A3D.layers.length = 0;
  [{ id: 'layer-0', name: 'Model' }, { id: 'ly-a', name: 'A' }].forEach((l) => A3D.layers.push({ visible: true, ...l }));
  const mk = () => ({ objs: E.bimBobValid([
    { id: 'e1', t: 'rect', layer: 'ly-a', x: 50, y: 50, w: 10, h: 4 },
    { id: 'e2', t: 'rect', layer: 'ly-a', x: 0, y: 0, w: 20, h: 8 },
    { id: 'e3', t: 'rect', x: 300, y: 300, w: 5, h: 5 },
    { id: 'e4', t: 'rect', layer: 'ly-a', x: 0, y: 0, w: 5, h: 5, la: true }], []), figs: [],
  lay: E.bimBobLayValid({ 'ly-a': { dir: 'row', gap: 5, pad: 2, x: 10, y: 10 } }) });
  let W = mk();
  const bx = E.bimBobLayApply(W, null, null, false);
  assert.deepEqual(W.objs.slice(0, 2).map((o) => [o.x, o.y]), [[12, 12], [27, 12]]);
  assert.deepEqual([W.objs[2].x, W.objs[3].x], [300, 0], 'another layer, and an object out of the stack, stay');
  assert.deepEqual(bx['ly-a'], { x: 10, y: 10, w: 39, h: 12 });
  W = mk();
  E.bimBobLayApply(W, null, null, true);
  assert.deepEqual(W.objs.slice(0, 2).map((o) => [o.x, o.y]), [[12, 12], [12, 21]]);
  assert.equal(E.bimBobLayValid({ 'ly-a': { dir: 'diagonal' } }), null);
});

/* ---- V174c ---- */
test('pages come from the registry: ISO 216\'s table, ASME Y14.1\'s inches, the Architectural sizes (D12, D13)', () => {
  assert.deepEqual(E.bimPgDims('iso-A3', 'l'), { w: 420, h: 297 });
  assert.deepEqual(E.bimPgDims('iso-A4', 'p'), { w: 210, h: 297 });
  assert.deepEqual(E.bimPgDims('ansi-D', 'l'), { w: 863.6, h: 558.8 });
  assert.deepEqual(E.bimPgDims('arch-D', 'p'), { w: 609.6, h: 914.4 });
  assert.deepEqual(E.bimPgDims('arch-E1', 'l'), { w: 1066.8, h: 762 });
  assert.equal(D.pgSize('iso-A5'), null, 'not in the gallery (D13)');
  assert.equal(D.pgSize('nope'), null);
  assert.match(E.bimPgLabel('ansi-D', 'l'), /ANSI D landscape \(34 x 22 in\)/);
});

test('ISO 5457: A0 to A3 landscape and A4 portrait (D14)', () => {
  assert.equal(E.bimPgIso5457Ok('iso-A3', 'l'), true);
  assert.equal(E.bimPgIso5457Ok('iso-A3', 'p'), false);
  assert.equal(E.bimPgIso5457Ok('iso-A4', 'p'), true);
  assert.equal(E.bimPgIso5457Ok('iso-A4', 'l'), false);
  assert.equal(E.bimPgIso5457Ok('ansi-B', 'l'), false);
});

test('the sheets\' old ANSI D is Arch D, keeping its size; a gallery size becomes a sheet size', () => {
  assert.match(E.SHEET_SIZES['ANSI-D'].label, /^Arch D/);
  assert.equal(E.SHEET_SIZES['ANSI-D'].w, 609.6);
  assert.equal(E.bimPgEnsureSheetSize('pg:iso-A1:l'), true);
  assert.equal(E.SHEET_SIZES['pg:iso-A1:l'].w, 841);
  assert.equal(E.bimPgEnsureSheetSize('pg:iso-A9:l'), false);
  assert.equal(E.bimPgSheetKey('ansi-B', 'l'), 'ANSI-B-L', 'a size the sheets already know keeps its V116 key');
  assert.equal(E.bimPgSheetKey('arch-D', 'l'), 'ANSI-D-L', 'the old ANSI D was always Arch D');
  assert.equal(E.bimPgSheetKey('ansi-E', 'p'), 'pg:ansi-E:p');
});

test('a board\'s page is kept with it, and only a good one', () => {
  assert.deepEqual(E.bimPgValid({ key: 'arch-D', o: 'p' }), { key: 'arch-D', o: 'p' });
  assert.equal(E.bimPgValid({ key: 'iso-A7' }), null);
  assert.deepEqual(E.bimPgBoardPage({ page: { key: 'iso-A3', o: 'l' } }).w, 420);
});

/* ---- V174d ---- */
test('the scale bar: the largest 1-2-5 number whose two divisions fit 15 to 40 per cent of the frame (D15)', () => {
  assert.deepEqual(D.bar(120, 1000, 'm'), { seg: 20, label: 'm', segs: 2, barMm: 40 });
  const k = D.bar(200, 50000, 'm');
  assert.equal(k.label, 'km'); assert.equal(k.seg, 2); near(k.barMm, 80);
  const f = D.bar(120, 1200, 'ft');
  assert.equal(f.label, 'ft'); assert.equal(f.seg, 50); near(f.barMm, 25.4);
  const mi = D.bar(200, 100000, 'ft');
  assert.equal(mi.label, 'mi');
});

test('a scale near a value is one of the sheets\' scales, or 1, 2, 2.5 or 5 times a power of ten', () => {
  assert.equal(D.niceDen(180), 200);
  assert.equal(D.niceDen(5000), 5000);
  assert.equal(D.niceDen(6100), 10000);
  assert.equal(D.niceDen(21000), 25000);
});

test('the surround\'s objects are kept good', () => {
  const T = E.bimBobValid([
    { id: 'e1', t: 'map', x: 0, y: 0, w: 100, h: 80, src: 'plan:lv-1', den: 0.2 },
    { id: 'e2', t: 'north', x: 0, y: 0, w: 10, h: 10, fr: 'e1', nk: 'magnetic', off: 500 },
    { id: 'e3', t: 'sbar', x: 0, y: 0, w: 40, h: 10, fr: 'bad', un: 'yd' },
    { id: 'e4', t: 'tblock', x: 0, y: 0, w: 180, h: 36, st: 'jis' },
  ], []);
  assert.equal(T[0].den, 1);
  assert.equal(T[1].nk, 'true'); assert.equal(T[1].off, 360);
  assert.equal(T[2].fr, undefined); assert.equal(T[2].un, 'm');
  assert.equal(T[3].st, 'iso');
});

test('a board one draws on gets the smallest standard page that holds it (the owner, 2026-11-08)', () => {
  assert.deepEqual(E.bimPgFit(200, 150, false), { key: 'iso-A4', o: 'l', fits: true });
  assert.deepEqual(E.bimPgFit(372.5, 200, false), { key: 'iso-A3', o: 'l', fits: true }, 'a board\'s 12 columns fit A3');
  assert.deepEqual(E.bimPgFit(372.5, 400, false), { key: 'iso-A2', o: 'l', fits: true });
  assert.deepEqual(E.bimPgFit(2000, 2000, false), { key: 'iso-A0', o: 'l', fits: false });
  assert.deepEqual(E.bimPgFit(372.5, 200, true), { key: 'ansi-B', o: 'l', fits: true }, 'an imperial project: ANSI B, 17 x 11 in');
});
