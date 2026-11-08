/* V174a: a board's element tree (sheets/board-tree.js), its drawing (sheets/board-design.js) and its images' names
   (sheets/board-images.js). docs/research/research-presentation-boards.md, 4.1 to 4.3, D2 to D5, D19. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const D = globalThis.window.__a3dBoardDesign;

const rect = (id, o = {}) => ({ id, t: 'rect', x: 10, y: 10, w: 20, h: 10, ...o });

test('the blend list is the W3C 16 under Figma\'s names, with Pass through for frames and groups', () => {
  const L = E.bimBtrBlends();
  assert.equal(L.length, 17);
  assert.deepEqual(L[0], ['pass', 'Pass through', '']);
  assert.deepEqual(L.slice(1).map((b) => b[2]), ['normal', 'darken', 'multiply', 'color-burn', 'lighten', 'screen',
    'color-dodge', 'overlay', 'soft-light', 'hard-light', 'difference', 'exclusion', 'hue', 'saturation', 'color', 'luminosity']);
  assert.equal(E.bimBtrBlend('plus-darker'), null);
});

test('an element is kept good: defaults, limits, and what a kind may have', () => {
  const T = E.bimBtrValid([
    rect('e1', { op: 3, bm: 'pass', fill: 'red', sw: -1 }),
    { id: 'e2', t: 'group', ch: [rect('e3')] },
    { id: 'e4', t: 'group', ch: [] },
    { id: 'e1', t: 'ellipse', x: 0, y: 0, w: 5, h: 5 },
    { id: 'e5', t: 'blob' },
    { id: 'e6', t: 'text', x: 0, y: 0, w: 50, h: 10, s: 'Hi', mask: 'alpha', fw: 900 },
    { id: 'e7', t: 'frame', x: 0, y: 0, w: 100, h: 50, ch: [] },
  ], []);
  assert.deepEqual(T.map((n) => n.id), ['e1', 'e2', 'e6', 'e7']);
  assert.equal(T[2].fw, 400);
  const r = T[0];
  assert.equal(r.op, 1);
  assert.equal(r.bm, 'normal', 'Pass through is for frames and groups only');
  assert.equal(r.fill, '#c3c2b7');
  assert.equal(r.sw, 0);
  assert.equal(T[1].bm, 'pass', 'a group passes through by default (D3)');
  assert.equal(T[3].bm, 'pass');
  assert.equal(T[3].clip, true);
  assert.equal(T[3].fill, '#ffffff');
});

test('text cannot be a mask; shapes and images can', () => {
  const T = E.bimBtrValid([
    { id: 'e1', t: 'text', x: 0, y: 0, w: 50, h: 10, s: 'Hi', mask: 'alpha' },
    rect('e2', { mask: 'lum' }),
    { id: 'e3', t: 'image', x: 0, y: 0, w: 10, h: 10, src: 'h0123456789abcdef', mask: 'vector' },
    { id: 'e4', t: 'image', x: 0, y: 0, w: 10, h: 10, src: 'not-a-hash' },
  ], []);
  assert.equal(T[0].mask, undefined);
  assert.equal(T[1].mask, 'lum');
  assert.equal(T[2].mask, 'vector');
  assert.equal(T[3].src, '');
});

test('a tree deeper than eight levels loses the part below', () => {
  let n = rect('e99');
  for (let i = 1; i <= 10; i++) n = { id: 'e' + i, t: 'group', ch: [n] };
  const T = E.bimBtrValid([n], []);
  assert.equal(T.length, 0, 'the innermost group is too deep, so every group above it is empty');
});

test('the tree agrees with the figures: gone ones dropped, new ones on top, a figure named twice kept once', () => {
  const figs = [{ k: 'f1' }, { k: 'f2' }, { k: 'f3' }];
  const T = E.bimBtrValid([
    { id: 'e1', t: 'fig', k: 'f2' },
    { id: 'e2', t: 'fig', k: 'f9' },
    { id: 'e3', t: 'group', ch: [{ id: 'e4', t: 'fig', k: 'f1' }, { id: 'e5', t: 'fig', k: 'f2' }] },
  ], figs);
  const ks = [];
  E.bimBtrWalk(T, (n) => { if (n.t === 'fig') ks.push(n.k); });
  assert.deepEqual(ks, ['f2', 'f1', 'f3']);
  assert.equal(T[T.length - 1].k, 'f3');
});

test('a figure\'s columns to millimetres and back are the same (D19)', () => {
  const P = E.BIM_BRD_P0, G = E.BIM_BRD_G;
  for (const F of [{ x: 0, y: 0, w: 12, h: 4 }, { x: 3.25, y: 17.5, w: 4.5, h: 0.25 }, { x: 7, y: 2, w: 5, h: 6.125 }]) {
    const back = D.figCols(E.bimBtrFigBox(F, P, G), P, G);
    for (const k of ['x', 'y', 'w', 'h']) assert.ok(Math.abs(back[k] - F[k]) < 1e-9, k);
  }
  assert.ok(Math.abs(E.bimBtrFigBox({ x: 0, y: 0, w: 12, h: 1 }, P, G).w - 1408 * 25.4 / 96) < 1e-9, 'twelve columns are 1408 px, 372.5 mm on paper');
});

test('reordering stays within the parent', () => {
  const L = E.bimBtrValid([rect('e1'), rect('e2'), { id: 'e3', t: 'group', ch: [rect('e4'), rect('e5')] }], []);
  assert.equal(E.bimBtrReorder(L, 'e1', 'front'), true);
  assert.deepEqual(L.map((n) => n.id), ['e2', 'e3', 'e1']);
  assert.equal(E.bimBtrReorder(L, 'e4', 'forward'), true);
  assert.deepEqual(L[1].ch.map((n) => n.id), ['e5', 'e4']);
  assert.equal(E.bimBtrReorder(L, 'e4', 'forward'), false, 'already in front within its group');
  assert.equal(E.bimBtrReorder(L, 'e2', 'back'), false);
});

test('group and ungroup keep the drawing order and the place', () => {
  const L = E.bimBtrValid([rect('e1'), rect('e2'), rect('e3'), rect('e4')], []);
  const g = E.bimBtrGroup(L, ['e3', 'e1'], false);
  assert.deepEqual(L.map((n) => n.id), ['e2', g, 'e4']);
  assert.deepEqual(L[1].ch.map((n) => n.id), ['e1', 'e3']);
  assert.equal(L[1].bm, 'pass');
  L[1].op = 0.5;
  L[1].ch[0].op = 0.5;
  assert.equal(E.bimBtrUngroup(L, g), true);
  assert.deepEqual(L.map((n) => n.id), ['e2', 'e1', 'e3', 'e4']);
  assert.equal(L[1].op, 0.25, 'the group\'s opacity goes into its elements');
  assert.equal(L[2].op, 0.5);
  assert.equal(E.bimBtrGroup(L, ['e1', 'e99'], false), null);
});

test('a frame around elements takes their bounds', () => {
  const L = E.bimBtrValid([rect('e1', { x: 5, y: 5, w: 10, h: 10 }), rect('e2', { x: 30, y: 2, w: 5, h: 40 })], []);
  const f = E.bimBtrGroup(L, ['e1', 'e2'], true);
  const F = E.bimBtrFind(L, f).n;
  assert.deepEqual([F.x, F.y, F.w, F.h], [5, 2, 30, 40]);
  assert.equal(F.clip, false);
});

test('elements of different parents are not grouped', () => {
  const L = E.bimBtrValid([rect('e1'), { id: 'e2', t: 'group', ch: [rect('e3')] }], []);
  assert.equal(E.bimBtrGroup(L, ['e1', 'e3'], false), null);
});

test('moving into a group, never into itself; out puts it just above its group; an emptied group is gone', () => {
  const L = E.bimBtrValid([rect('e1'), { id: 'e2', t: 'group', ch: [rect('e3'), { id: 'e4', t: 'group', ch: [rect('e5')] }] }], []);
  assert.equal(E.bimBtrMoveTo(L, 'e2', 'e4'), false);
  assert.equal(E.bimBtrMoveTo(L, 'e2', 'e2'), false);
  assert.equal(E.bimBtrMoveTo(L, 'e1', 'e4'), true);
  assert.deepEqual(E.bimBtrFind(L, 'e4').n.ch.map((n) => n.id), ['e5', 'e1']);
  assert.equal(E.bimBtrOut(L, 'e5'), true);
  assert.deepEqual(E.bimBtrFind(L, 'e2').n.ch.map((n) => n.id), ['e3', 'e4', 'e5']);
  assert.equal(E.bimBtrOut(L, 'e1'), true);
  assert.equal(E.bimBtrFind(L, 'e4'), null, 'the group left empty is removed');
});

test('masks: a mask masks the siblings above it, to the next mask; a hidden one masks nothing', () => {
  const L = [rect('e1'), rect('e2', { mask: 'alpha' }), rect('e3'), rect('e4'), rect('e5', { mask: 'vector', hide: true }), rect('e6')];
  const R = E.bimBtrRuns(L);
  assert.deepEqual(R.map((r) => [r.mask && r.mask.id, r.items.map((n) => n.id)]),
    [[null, ['e1']], ['e2', ['e3', 'e4']], [null, ['e6']]]);
});

test('a click picks the outermost unlocked, visible element in the group one is in; Ctrl picks deep', () => {
  const L = E.bimBtrValid([{ id: 'e1', t: 'group', ch: [{ id: 'e2', t: 'group', ch: [rect('e3')] }, rect('e4')] }, rect('e5', { lock: true })], []);
  assert.equal(E.bimBtrPick(L, 'e3', null, false), 'e1');
  assert.equal(E.bimBtrPick(L, 'e3', 'e1', false), 'e2');
  assert.equal(E.bimBtrPick(L, 'e3', 'e2', false), 'e3');
  assert.equal(E.bimBtrPick(L, 'e3', null, true), 'e3');
  assert.equal(E.bimBtrPick(L, 'e5', null, false), null);
  L[0].hide = true;
  assert.equal(E.bimBtrPick(L, 'e4', null, false), null, 'hide cascades to the children');
  assert.equal(E.bimBtrEff(L, 'e3').hide, true);
});

test('a copy has new ids and leaves the figures out', () => {
  const L = E.bimBtrValid([{ id: 'e1', t: 'group', ch: [rect('e2'), { id: 'e3', t: 'fig', k: 'f1' }] }], [{ k: 'f1' }]);
  const c = E.bimBtrCopy(L, L[0]);
  assert.equal(c.ch.length, 1);
  assert.notEqual(c.id, 'e1');
  assert.notEqual(c.ch[0].id, 'e2');
  assert.equal(E.bimBtrCopy(L, E.bimBtrFind(L, 'e3').n), null);
});

test('a board made before V174 keeps no tree, and a tree is kept with its board (D19)', () => {
  const P = E.bimPresValid({ boards: [
    { id: 'board-c1', kind: 'custom', name: 'Old', figs: [{ k: 'f1', f: 'text', x: 0, y: 0, w: 12, h: 1 }] },
    { id: 'board-c2', kind: 'custom', name: 'New', figs: [], els: [rect('e1', { bm: 'multiply' })] },
  ], order: [] });
  assert.equal('els' in P.boards[0], false);
  assert.equal(P.boards[1].els[0].bm, 'multiply');
});

/* ---- drawing: the compositing rules of D3 in CSS ---- */
function draw(els) {
  const B = { id: 'board-c1', kind: 'custom', figs: [], els: E.bimBtrValid(els, []) };
  return E.bimBdsHtml(B, [], { edit: false, narrow: false, caps: {}, no: 0 });
}

test('a pass-through group is drawn with no element of its own; a group with a mode or opacity is isolated', () => {
  let h = draw([{ id: 'e1', t: 'group', ch: [rect('e2', { bm: 'multiply' })] }]);
  assert.equal(h.includes('a3d-clb-dgrp'), false);
  assert.ok(h.includes('mix-blend-mode:multiply'));
  h = draw([{ id: 'e1', t: 'group', bm: 'normal', ch: [rect('e2')] }]);
  assert.ok(/class="a3d-clb-dgrp"[^>]*style="[^"]*isolation:isolate/.test(h));
  h = draw([{ id: 'e1', t: 'group', op: 0.5, ch: [rect('e2')] }]);
  assert.ok(/class="a3d-clb-dgrp"[^>]*style="[^"]*opacity:0.5;[^"]*isolation:isolate/.test(h));
});

test('the canvas is one isolated root, and paint order is the tree\'s order', () => {
  const h = draw([rect('e1'), rect('e2'), rect('e3')]);
  assert.ok(h.includes('<div class="a3d-clb-dcv">'));
  assert.ok(h.indexOf('data-bde="e1"') < h.indexOf('data-bde="e2"'));
  assert.ok(h.indexOf('data-bde="e2"') < h.indexOf('data-bde="e3"'));
  assert.equal(/z-index/.test(h), false);
});

test('a frame clips and keeps its children inside it; a pass-through frame does not isolate', () => {
  const h = draw([{ id: 'e1', t: 'frame', x: 10, y: 10, w: 50, h: 50, ch: [rect('e2', { x: 20, y: 30 })] }]);
  assert.ok(/class="a3d-clb-dfrm"[^>]*style="[^"]*overflow:hidden/.test(h));
  assert.equal(/class="a3d-clb-dfrm"[^>]*style="[^"]*isolation/.test(h), false);
  assert.ok(h.includes('left:37.795px;top:75.591px'), 'the child at 10, 20 mm inside the frame');
});

test('masks are drawn as CSS: vector by clip-path, alpha and luminance by mask-image', () => {
  let h = draw([rect('e1', { mask: 'vector', r: 2 }), rect('e2')]);
  assert.ok(/class="a3d-clb-dmask"[^>]*clip-path:inset\(0 round 7.559px\)/.test(h));
  assert.equal(h.includes('data-bde="e1"'), false, 'the mask itself is not drawn');
  h = draw([{ id: 'e1', t: 'ellipse', x: 0, y: 0, w: 10, h: 10, mask: 'lum' }, rect('e2')]);
  assert.ok(h.includes("mask-image:url('data:image/svg+xml,"));
  assert.ok(h.includes('mask-mode:luminance'));
  h = draw([{ id: 'e1', t: 'star', x: 0, y: 0, w: 10, h: 10, n: 5, mask: 'vector' }, rect('e2')]);
  assert.ok(/clip-path:polygon\(50% 0%,/.test(h));
});

test('a hidden element is not drawn; a line draws its arrowheads', () => {
  let h = draw([rect('e1', { hide: true })]);
  assert.equal(h.includes('data-bde="e1"'), false);
  h = draw([{ id: 'e1', t: 'line', x: 0, y: 0, w: 50, h: 0, a0: true, a1: true }]);
  assert.equal((h.match(/<polygon/g) || []).length, 2);
});

test('an image is named by its data\'s hash, and only images are taken', () => {
  const d = 'data:image/png;base64,iVBORw0KGgo=';
  assert.match(D.hash(d), /^h[0-9a-f]{16}$/);
  assert.equal(D.hash(d), D.hash(d));
  assert.notEqual(D.hash(d), D.hash(d + 'A'));
  assert.equal(D.imageOk(d), true);
  assert.equal(D.imageOk('data:text/html;base64,PGI+'), false);
  assert.equal(D.imageOk('data:image/svg+xml;base64,PHN2Zz4='), false);
});
