/* V174a: a board's objects on the one layer table (sheets/board-objects.js), drawn (sheets/board-design.js); the
   layers' blend mode and order (layers/). docs/research/research-presentation-boards.md, 11a (R1 to R4). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const A3D = E.A3D;
const D = globalThis.window.__a3dBoardDesign;

const rect = (id, o = {}) => ({ id, t: 'rect', x: 10, y: 10, w: 20, h: 10, ...o });
function layers(list) {
  A3D.layers.length = 0;
  list.forEach((l) => A3D.layers.push({ visible: true, locked: false, ...l }));
  A3D.activeLayer = A3D.layers[0].id;
}
const L0 = () => layers([{ id: 'layer-0', name: 'Model' }, { id: 'ly-a', name: 'A', transparency: 40, blend: 'multiply' }, { id: 'ly-b', name: 'B' }]);

test('the blend list is the W3C 16 under Figma\'s names', () => {
  const L = E.bimBobBlends();
  assert.equal(L.length, 16);
  assert.deepEqual(L.map((b) => b[2]), ['normal', 'darken', 'multiply', 'color-burn', 'lighten', 'screen',
    'color-dodge', 'overlay', 'soft-light', 'hard-light', 'difference', 'exclusion', 'hue', 'saturation', 'color', 'luminosity']);
  assert.equal(E.bimBobBlend('pass'), null, 'no Pass through: nothing is composited as a group');
});

test('an object is kept good; Transparency and Blend are ByLayer unless set', () => {
  const T = E.bimBobValid([
    rect('e1', { layer: 'ly-a', tr: 120, bm: 'multiply', fill: 'red' }),
    rect('e2'),
    { id: 'e1', t: 'ellipse', x: 0, y: 0, w: 5, h: 5 },
    { id: 'e3', t: 'group' },
    { id: 'e4', t: 'text', x: 0, y: 0, w: 50, h: 10, s: 'Hi', mask: 'alpha', bm: 'pass' },
  ], []);
  assert.deepEqual(T.map((n) => n.id), ['e1', 'e2', 'e4']);
  assert.equal(T[0].tr, 90);
  assert.equal(T[0].bm, 'multiply');
  assert.equal(T[0].fill, '#c3c2b7');
  assert.equal('tr' in T[1], false);
  assert.equal('bm' in T[1], false);
  assert.equal(T[2].mask, undefined, 'text is not a mask');
  assert.equal(T[2].bm, undefined);
});

test('ByLayer: an object takes its layer\'s transparency and blend; its own wins; no layer is layer 0', () => {
  L0();
  assert.equal(E.bimBobTr({ layer: 'ly-a' }), 40);
  assert.equal(E.bimBobBm({ layer: 'ly-a' }), 'multiply');
  assert.equal(E.bimBobTr({ layer: 'ly-a', tr: 0 }), 0);
  assert.equal(E.bimBobBm({ layer: 'ly-a', bm: 'screen' }), 'screen');
  assert.equal(E.bimBobLayer({}).id, 'layer-0');
  assert.equal(E.bimBobLayer({ layer: 'gone' }).id, 'layer-0');
  assert.equal(E.bimLayerBlend({}), 'normal', 'a layer without a blend mode is Normal');
});

test('layer 0 is found by its id, wherever it is in the list', () => {
  layers([{ id: 'ly-x', name: 'X' }, { id: 'layer-0', name: 'Model' }]);
  assert.equal(E.bimLayerZero().id, 'layer-0');
  assert.equal(E.bimLayerOf({ layer: 'missing' }).id, 'layer-0');
});

test('paint order is the layer list read from the bottom up, then the list\'s order within a layer', () => {
  layers([{ id: 'layer-0', name: 'Model' }, { id: 'top', name: 'Top' }, { id: 'bot', name: 'Bottom' }, { id: 'sub', name: 'Sub', parent: 'top' }]);
  const L = E.bimBobValid([rect('e1', { layer: 'top' }), rect('e2', { layer: 'bot' }), rect('e3', { layer: 'top' }), rect('e4'), rect('e5', { layer: 'sub' })], []);
  /* the tree: Model, Top, Sub, Bottom; painted from the bottom: Bottom, Sub, Top, Model */
  assert.deepEqual(E.bimBobPaint(L).map((p) => p.n.id), ['e2', 'e5', 'e1', 'e3', 'e4']);
});

test('Draw order acts within the layer', () => {
  L0();
  const L = E.bimBobValid([rect('e1', { layer: 'ly-a' }), rect('e2', { layer: 'ly-b' }), rect('e3', { layer: 'ly-a' })], []);
  assert.equal(E.bimBobReorder(L, 'e1', 'forward'), true);
  assert.deepEqual(L.map((n) => n.id), ['e2', 'e3', 'e1']);
  assert.equal(E.bimBobReorder(L, 'e1', 'front'), false, 'already in front within its layer');
  assert.equal(E.bimBobReorder(L, 'e2', 'back'), false, 'alone on its layer');
});

test('a mask clips the objects of its layer drawn above it, up to that layer\'s next mask', () => {
  L0();
  const L = E.bimBobValid([rect('e1', { layer: 'ly-a' }), rect('e2', { layer: 'ly-a', mask: 'alpha' }), rect('e3', { layer: 'ly-a' }),
    rect('e4', { layer: 'ly-b' }), rect('e5', { layer: 'ly-a', mask: 'vector' }), rect('e6', { layer: 'ly-a' })], []);
  const R = E.bimBobRuns(E.bimBobPaint(L));
  assert.deepEqual(R.map((r) => [r.mask && r.mask.id, r.items.map((n) => n.id)]),
    [[null, ['e4']], [null, ['e1']], ['e2', ['e3']], ['e5', ['e6']]]);
});

test('the objects agree with the figures: gone ones dropped, new ones added, a figure named twice kept once', () => {
  const T = E.bimBobValid([{ id: 'e1', t: 'fig', k: 'f2' }, { id: 'e2', t: 'fig', k: 'f9' }, { id: 'e3', t: 'fig', k: 'f2' }], [{ k: 'f1' }, { k: 'f2' }]);
  assert.deepEqual(T.map((n) => n.t === 'fig' && n.k), ['f2', 'f1']);
});

test('a figure\'s columns to millimetres and back are the same; 1408 px are 372.5 mm on paper (D19)', () => {
  const P = E.BIM_BRD_P0, G = E.BIM_BRD_G;
  for (const F of [{ x: 0, y: 0, w: 12, h: 4 }, { x: 3.25, y: 17.5, w: 4.5, h: 0.25 }]) {
    const back = D.figCols(E.bimBobFigBox(F, P, G), P, G);
    for (const k of ['x', 'y', 'w', 'h']) assert.ok(Math.abs(back[k] - F[k]) < 1e-9, k);
  }
  assert.ok(Math.abs(E.bimBobFigBox({ x: 0, y: 0, w: 12, h: 1 }, P, G).w - 1408 * 25.4 / 96) < 1e-9);
});

test('a board made before V174 keeps no objects list; one is kept with its board', () => {
  L0();
  const P = E.bimPresValid({ boards: [
    { id: 'board-c1', kind: 'custom', name: 'Old', figs: [{ k: 'f1', f: 'text', x: 0, y: 0, w: 12, h: 1 }] },
    { id: 'board-c2', kind: 'custom', name: 'New', figs: [], objs: [rect('e1', { layer: 'ly-a' })] },
  ], order: [] });
  assert.equal('objs' in P.boards[0], false);
  assert.equal(P.boards[1].objs[0].layer, 'ly-a');
  A3D.pres = P;
  assert.equal(E.bimBobOnLayer('ly-a'), 1, 'Delete Layer counts every board\'s objects');
  assert.equal(E.bimBobOnLayer('ly-b'), 0);
  A3D.pres = null;
});

/* ---- drawing ---- */
function draw(objs, pres) {
  const B = { id: 'board-c1', kind: 'custom', figs: [], objs: E.bimBobValid(objs, []) };
  A3D.presentMode = !!pres;
  try { return E.bimBdsHtml(B, [], { edit: false, narrow: false, caps: {}, no: 0 }); } finally { A3D.presentMode = false; }
}

test('transparency and blend are drawn in the Presentation appearance only, per object, ByLayer', () => {
  L0();
  const objs = [rect('e1', { layer: 'ly-a' }), rect('e2', { layer: 'ly-b', bm: 'screen', tr: 50 })];
  let h = draw(objs, false);
  assert.equal(/mix-blend-mode|opacity/.test(h), false, 'Technical: plain');
  h = draw(objs, true);
  assert.ok(/data-bde="e1"[^>]*style="[^"]*opacity:0.6;mix-blend-mode:multiply/.test(h), 'the layer\'s 40 and Multiply');
  assert.ok(/data-bde="e2"[^>]*style="[^"]*opacity:0.5;mix-blend-mode:screen/.test(h), 'its own');
  assert.equal(/isolation:isolate/.test(h), false, 'nothing is composited as a group');
});

test('a layer that is off or frozen hides its objects; the higher layer is drawn later', () => {
  L0();
  let h = draw([rect('e1', { layer: 'ly-b' }), rect('e2', { layer: 'ly-a' })], false);
  assert.ok(h.indexOf('data-bde="e1"') < h.indexOf('data-bde="e2"'), 'A is above B in the list, so drawn over it');
  A3D.layers[1].visible = false;
  h = draw([rect('e1', { layer: 'ly-b' }), rect('e2', { layer: 'ly-a' })], false);
  assert.equal(h.includes('data-bde="e2"'), false);
  A3D.layers[1].visible = true; A3D.layers[2].frozen = true;
  h = draw([rect('e1', { layer: 'ly-b' })], false);
  assert.equal(h.includes('data-bde="e1"'), false);
});

test('masks are drawn as CSS; a level line\'s box is not 0 high', () => {
  L0();
  let h = draw([rect('e1', { mask: 'vector', r: 2 }), rect('e2')], false);
  assert.ok(/class="a3d-clb-dmask"[^>]*clip-path:inset\(0 round 7.559px\)/.test(h));
  assert.equal(h.includes('data-bde="e1"'), false, 'the mask itself is not drawn');
  h = draw([{ id: 'e1', t: 'ellipse', x: 0, y: 0, w: 10, h: 10, mask: 'lum' }, rect('e2')], false);
  assert.ok(h.includes('mask-mode:luminance'));
  h = draw([{ id: 'e1', t: 'line', x: 0, y: 0, w: 50, h: 0, a0: true, a1: true }], false);
  assert.equal((h.match(/<polygon/g) || []).length, 2);
  assert.ok(/class="a3d-clb-dshp ln"[^>]*style="left:-[\d.]+px;top:-[\d.]+px;width:[\d.]+px;height:[1-9][\d.]*px/.test(h));
});

test('a board image is named by its data\'s hash, and only images are taken', () => {
  const d = 'data:image/png;base64,iVBORw0KGgo=';
  assert.match(D.hash(d), /^h[0-9a-f]{16}$/);
  assert.notEqual(D.hash(d), D.hash(d + 'A'));
  assert.equal(D.imageOk(d), true);
  assert.equal(D.imageOk('data:image/svg+xml;base64,PHN2Zz4='), false);
});

/* bimLayerSet and bimLayerMove redraw the Layers tab when they change something, which the stand-in browser cannot
   (refreshLayers runs out of memory here, on main as well): their refusals are tested here, their changes in the
   browser check */
test('a layer\'s blend mode must be one of the 16; a move into its own branch and a step past the end are refused', () => {
  layers([{ id: 'layer-0', name: 'Model' }, { id: 'ly-a', name: 'A' }, { id: 'ly-s', name: 'S', parent: 'ly-a' }]);
  assert.equal(E.bimLayerSet('ly-a', 'blend', 'plus-lighter'), false);
  assert.equal(E.bimLayerSet('ly-a', 'blend', 'pass'), false);
  assert.equal(E.bimLayerSet('ly-a', 'blend', 'normal'), true, 'what it already is: no change, no redraw');
  assert.equal(D.layerMove('ly-a', 'ly-s', 'before'), false, 'a layer cannot go beside its own sub-layer, inside itself');
  assert.equal(D.layerStep('layer-0', -1), false);
  assert.equal(D.layerStep('ly-s', 1), false, 'alone among its siblings');
});
