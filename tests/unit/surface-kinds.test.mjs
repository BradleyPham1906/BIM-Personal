// V197, colours by surface kind (render/surface-kinds.js, render/gpu-batches.js): an object's kind, the palette's
// colour for it, and a map building's roof drawn from a second row of the scene's table, in both views.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const K = globalThis.__a3dKinds;

// a 4 m box, 3 m high, as quads: bottom, top, four sides
function box() {
  const v = [[0, 0, 0], [4, 0, 0], [4, 0, 4], [0, 0, 4], [0, 3, 0], [4, 3, 0], [4, 3, 4], [0, 3, 4]];
  const f = [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]];
  return { v, f };
}
const hex = (rgb) => '#' + rgb.map((x) => Math.round(x * 255).toString(16).padStart(2, '0')).join('');

function withModel(objs, fn) {
  const keep = { objs: E.A3D.objs, sel: E.A3D.sel, sel2: E.A3D.sel2, selSet: E.A3D.selSet, site: E.A3D.site };
  try {
    E.bimSceneRelease();
    E.A3D.objs = objs; E.A3D.sel = null; E.A3D.sel2 = null; E.A3D.selSet = [];
    E.A3D.site = { name: 'Site' };
    if (E.A3D_LENS) E.A3D_LENS.cur = null;
    return fn();
  } finally { Object.assign(E.A3D, keep); if (E.A3D_LENS) E.A3D_LENS.cur = null; E.bimSceneRelease(); }
}
const building = () => ({ id: 'b1', t: 'solid', name: 'B', col: '#123456', pos: [0, 0, 0], mesh: box(), context: { kind: 'buildings' } });
// the colours of the triangles that look up and of those that do not, as the table gives them
function colours() {
  const B = K.sync().S, d = B.data, c = B.chunks[0], up = new Set(), side = new Set(), sl = new Set();
  for (let i = 0; i < c.count; i += 3) {
    const s = c.tri[i * 7 + 6], ny = c.tri[i * 7 + 4], col = hex([d[s * 8 + 4], d[s * 8 + 5], d[s * 8 + 6]]);
    sl.add(s);
    if (ny > 0.5) up.add(col); else side.add(col);
  }
  return { up: [...up], side: [...side], slots: sl.size, B };
}

test('an object\'s kind, from what the app records on it', () => {
  assert.equal(K.key({ context: { kind: 'buildings' } }), 'walls');
  assert.equal(K.key({ context: { kind: 'terrain' } }), 'ground');
  assert.equal(K.key({ t: 'terrain' }), 'ground');
  assert.equal(K.key({ bim: { type: 'roof' } }), 'roofs');
  assert.equal(K.key({ bim: { type: 'column' } }), 'structure');
  assert.equal(K.key({ bim: { type: 'wall', ifcType: 'IfcWindow' } }), 'glass', 'the IFC class first');
  assert.equal(K.key({ bim: { ifcType: 'IfcStairFlight' } }), 'stair');
  assert.equal(K.key({ bim: { ifcType: 'IfcFurnishingElement' } }), null, 'no known kind: its own colour');
  assert.equal(K.key({ gltf: { file: 'a.glb' }, bim: { type: 'wall' } }), null, 'an import keeps its materials');
  assert.equal(K.key({ t: 'solid' }), null);
  for (const p of Object.values(K.pal)) for (const k of ['walls', 'roofs', 'ground', 'water', 'green', 'trees', 'roads', 'glass', 'rail', 'airports', 'power', 'landuse', 'floor', 'door', 'structure', 'stair', 'ceiling'])
    assert.match(p[k], /^#[0-9a-f]{6}$/, p.name + ' ' + k);
});

test('own colours by default: a building, roof and walls, in its own colour', () => withModel([building()], () => {
  const C = colours();
  assert.deepEqual(C.up, ['#123456']); assert.deepEqual(C.side, ['#123456']);
  assert.equal(Object.keys(C.B.slots).length, 1, 'one row an object in B.slots');
  assert.equal(Object.keys(C.B.roof).length, 1, 'the roof row kept apart');
}));

test('Study model: the roof grey, the walls white; Natural: terracotta and stone', () => withModel([building()], () => {
  K.set('study');
  let C = colours();
  assert.deepEqual(C.up, [K.pal.study.roofs]); assert.deepEqual(C.side, [K.pal.study.walls]);
  K.set('natural');
  C = colours();
  assert.deepEqual(C.up, [K.pal.natural.roofs]); assert.deepEqual(C.side, [K.pal.natural.walls]);
  assert.equal(C.slots, 2);
}));

test('a BIM wall\'s top is not a roof: only map and city buildings have one', () => withModel(
  [{ id: 'w1', t: 'solid', col: '#123456', pos: [0, 0, 0], mesh: box(), bim: { type: 'wall' } }], () => {
    K.set('study');
    const C = colours();
    assert.deepEqual(C.up, [K.pal.study.walls]); assert.deepEqual(C.side, [K.pal.study.walls]);
    assert.equal(C.slots, 1);
  }));

test('a lens comes first: roof and walls in the lens colour', () => withModel([building()], () => {
  K.set('study');
  E.A3D.site.lens = { by: 'height' };
  const C = colours();
  assert.equal(C.up.length, 1);
  assert.deepEqual(C.up, C.side, 'the roof row takes the lens colour too');
  assert.notEqual(C.up[0], K.pal.study.roofs);
}));

test('selected, the roof row is selected too; removed, both rows are freed', () => withModel([building()], () => {
  K.set('study');
  E.A3D.sel = 'b1';
  let B = K.sync().S;
  assert.equal(B.data[B.slots.b1 * 8 + 7], 1);
  assert.equal(B.data[B.roof.b1 * 8 + 7], 1);
  const rows = [B.slots.b1, B.roof.b1];
  E.A3D.objs = [];
  B = K.sync().S;
  assert.equal(Object.keys(B.slots).length, 0); assert.equal(Object.keys(B.roof).length, 0);
  rows.forEach((r) => { assert.equal(B.data[r * 8 + 3], -1, 'hidden'); assert.ok(B.free.includes(r)); });
}));

test('the rendered view redraws when only the roof row changes', () => withModel([building()], () => {
  const a = E.bimRvPlan(false).items.map((i) => i.sig).join('|');
  K.set('study');
  const b = E.bimRvPlan(false).items.map((i) => i.sig).join('|');
  assert.notEqual(a, b);
}));
