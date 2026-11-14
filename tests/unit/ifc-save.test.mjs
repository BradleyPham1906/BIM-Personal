// V177 step 2, the model as the data Save as IFC hands IfcOpenShell (src/js/engine/io/ifc-save.js;
// docs/work-orders/v177/SPEC.md parts 3 and 7). The file written from this data is checked by
// docs/work-orders/v177/v177.test.mjs (the adapter) and the phase's browser check.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const F = globalThis.__a3dIfcSave;
const LEVELS = [{ id: 'lvl-0', name: 'Ground', elev: 0, height: 3 }, { id: 'lvl-1', name: 'First', elev: 3.2, height: 3 }];
// a work order's cases wait, skipped, until its function is in the file's list (BIM_IFC_SAVE); the gate does not
// count a skipped case as run
const todo = (k, wo) => (typeof F[k] === 'function' ? false : wo + ' is not built yet');
const GUID = '1kTvXnbbzCWw8lcMd1dR4o';
const wall = (over) => Object.assign({ id: 'w1', t: 'solid', name: 'Wall_1', pos: [0, 0, 0],
  bim: { type: 'wall', thickness: 0.2, height: 3, align: 'center', baseY: 0, closed: false, centerline: [[0, 0], [6, 0]] } }, over || {});
const box = { v: [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1], [0, 2, 0], [1, 2, 0], [1, 2, 1], [0, 2, 1]],
  f: [[0, 1, 2, 3], [7, 6, 5, 4], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]] };

test('the file\'s own parts: numbers to a tenth of a millimetre, the plan and the mesh turned to IFC\'s axes', () => {
  assert.equal(F.num(1.23456789), 1.2346);
  assert.ok(Object.is(F.num(-0.00001), 0), 'never a minus zero');
  assert.deepEqual(F.pt([2, 3]), [2, -3], 'the plan\'s z is IFC\'s minus Y');
  assert.deepEqual(F.pt3([2, 5, 3]), [2, -3, 5], 'up is Z');
  assert.equal(F.cls.roof, 'IfcRoof');
});

test('WO-09 bimIfcSaveLevels and bimIfcSaveLevel: the levels in their order, and the level an element belongs to', { skip: todo('levels', 'WO-09') }, () => {
  const lv = F.levels(LEVELS);
  assert.deepEqual(lv.list, [{ name: 'Ground', elev: 0 }, { name: 'First', elev: 3.2 }]);
  assert.deepEqual(lv.at, { 'lvl-0': 0, 'lvl-1': 1 });
  assert.deepEqual(F.levels([]).list, []);
  assert.deepEqual(F.levels(null).list, []);
  assert.equal(F.level({ bim: { levelId: 'lvl-1' } }, lv, 0), 1, 'its own level, whatever its height');
  assert.equal(F.level({ bim: { levelId: 'gone' } }, lv, 3.3), 1, 'a level that is not there: by height');
  assert.equal(F.level({ bim: {} }, lv, 3.2), 1, 'at a level\'s elevation: that level');
  assert.equal(F.level({ bim: {} }, lv, 3.1), 0, 'the highest level at or under it');
  assert.equal(F.level({}, lv, -5), 0, 'under every level: the first');
  assert.equal(F.level({}, F.levels([]), 1), 0);
});

test('WO-10 bimIfcSaveBase: what every element carries: its id, name, kept GlobalId and property sets', { skip: todo('base', 'WO-10') }, () => {
  const b = F.base({ id: 'a1', t: 'solid', name: 'Wall_1', bim: { type: 'wall' } }, 'Walls');
  assert.deepEqual(b, { id: 'a1', name: 'Wall_1', psets: [{ name: 'BIM_Personal', props: { Type: 'wall', Layer: 'Walls' } }] });
  const i = F.base({ id: 'a2', t: 'solid', bim: { type: 'ifc', imported: true, guid: GUID,
    psets: [{ name: 'Pset_WallCommon', rows: [['IsExternal', 'true'], ['FireRating', null], ['', 'x']] }, { name: 'Empty', rows: [] }, { name: 'BIM_Personal', rows: [['Layer', 'old']] }] } }, null);
  assert.equal(i.guid, GUID);
  assert.equal(i.name, 'a2', 'no name: its id');
  assert.deepEqual(i.psets, [{ name: 'BIM_Personal', props: { Type: 'ifc', Layer: '' } },
    { name: 'Pset_WallCommon', props: { IsExternal: 'true', FireRating: '' } }], 'the imported sets with rows, as text; not an empty one, not a second BIM_Personal');
  assert.equal(F.base({ id: 'a3', t: 'box', bim: { guid: 'short' } }, 'L').guid, undefined, 'a GlobalId is 22 characters');
  assert.equal(F.base({ id: 'a4', t: 'box' }, 'L').psets[0].props.Type, 'box', 'no bim record: its primitive type');
});

test('WO-11 bimIfcSaveWalls: a straight wall as one IFC wall for each segment, or null when it is not one', { skip: todo('walls', 'WO-11') }, () => {
  const lv = F.levels(LEVELS), o = wall(), base = F.base(Object.assign(o, { bim: Object.assign(o.bim, { guid: GUID }) }), 'Walls');
  const one = F.walls(o, lv, base);
  assert.equal(one.length, 1);
  assert.deepEqual(one[0], { id: 'w1', name: 'Wall_1', psets: base.psets, guid: GUID, level: 0, x0: 0, y0: 0, x1: 6, y1: 0, base: 0, height: 3, thickness: 0.2, offset: -0.1 });
  // the sides: the app's left of the line is whatever bimSegNormal says; the body must cover the same ground
  const n = E.bimSegNormal([0, 0], [6, 0]), leftY = -n[1];   // the app's left, as IFC's Y
  const L = F.walls(wall({ bim: Object.assign({}, o.bim, { align: 'left' }) }), lv, base)[0];
  assert.equal(L.thickness, 0.2);
  assert.equal(L.offset, leftY > 0 ? -0.2 : 0, 'align left: the body is all on the right of the line (dLeft 0)');
  const R = F.walls(wall({ bim: Object.assign({}, o.bim, { align: 'right' }) }), lv, base)[0];
  assert.equal(R.offset, leftY > 0 ? 0 : -0.2, 'align right: all on the left');
  const X = F.walls(wall({ bim: Object.assign({}, o.bim, { align: { dLeft: 0.3, dRight: 0.1 } }) }), lv, base)[0];
  assert.equal(X.thickness, 0.4);
  assert.equal(X.offset, leftY > 0 ? -0.1 : -0.3, 'explicit side distances');
  // more segments: one wall each, the first keeps the id and the GlobalId
  const many = F.walls(wall({ bim: Object.assign({}, o.bim, { baseY: 3.2, centerline: [[0, 0], [6, 0], [6, 4], [6, 4], [0, 4]] }) }), lv, base);
  assert.deepEqual(many.map((w) => w.id), ['w1', 'w1#1', 'w1#3'], 'a segment of no length is passed over');
  assert.deepEqual(many.map((w) => w.name), ['Wall_1 1', 'Wall_1 2', 'Wall_1 3']);
  assert.deepEqual(many.map((w) => w.guid), [GUID, undefined, undefined]);
  assert.deepEqual([many[1].x0, many[1].y0, many[1].x1, many[1].y1], [6, 0, 6, -4]);
  assert.equal(many[0].level, 1, 'by its base, with no level of its own');
  assert.equal(many[0].base, 3.2);
  const ring = F.walls(wall({ bim: Object.assign({}, o.bim, { closed: true, centerline: [[0, 0], [6, 0], [6, 4]] }) }), lv, base);
  assert.equal(ring.length, 3, 'closed: the segment back to the start too');
  assert.deepEqual([ring[2].x0, ring[2].y0, ring[2].x1, ring[2].y1], [6, -4, 0, 0]);
  // not a straight wall: null, and the caller sends its triangles
  assert.equal(F.walls(wall({ bim: Object.assign({}, o.bim, { bulges: [0.5] }) }), lv, base), null, 'an arc');
  assert.equal(F.walls(wall({ pos: [1, 0, 0] }), lv, base), null, 'moved by its pos');
  assert.equal(F.walls(wall({ bim: Object.assign({}, o.bim, { centerline: [[0, 0]] }) }), lv, base), null);
  assert.equal(F.walls(wall({ bim: Object.assign({}, o.bim, { centerline: [[1, 1], [1, 1]] }) }), lv, base), null, 'no segment with a length');
  assert.equal(F.walls(wall({ bim: Object.assign({}, o.bim, { thickness: 0 }) }), lv, base), null);
  assert.equal(F.walls({ id: 'f', t: 'solid', bim: { type: 'floor' } }, lv, base), null);
  assert.equal(F.walls({ id: 'b', t: 'box' }, lv, base), null);
});

test('WO-12 bimIfcSavePrism: a floor and a rectangular column as an outline and a depth, or null', { skip: todo('prism', 'WO-12') }, () => {
  const lv = F.levels(LEVELS), base = { id: 'f1', name: 'Floor_1', psets: [] };
  const fl = F.prism({ id: 'f1', t: 'solid', pos: [0, 0, 0], bim: { type: 'floor', thickness: 0.25, baseY: 3.2, levelId: 'lvl-1', profile: [[0, 0], [6, 0], [6, 4], [0, 4]] } }, lv, base);
  assert.deepEqual(fl, { cls: 'IfcSlab', id: 'f1', name: 'Floor_1', psets: [], level: 1, pts: [[0, 0], [6, 0], [6, -4], [0, -4]], base: 2.95, depth: 0.25 }, 'a floor hangs under its baseY');
  const col = { id: 'c1', t: 'solid', pos: [0, 0, 0], bim: { type: 'column', width: 0.4, depth: 0.6, height: 3, baseY: 0, levelId: 'lvl-0', center: [2, 3], rotation: 0 } };
  const c = F.prism(col, lv, base);
  assert.equal(c.cls, 'IfcColumn');
  assert.deepEqual([c.base, c.depth, c.level], [0, 3, 0]);
  assert.deepEqual(c.pts, E.bimRectFootprint([2, 3], 0.4, 0.6, 0).map((p) => F.pt(p)), 'the corners the app builds the column from');
  assert.equal(c.pts.length, 4);
  assert.equal(F.prism(Object.assign({}, col, { bim: Object.assign({}, col.bim, { section: { shape: 'I' } }) }), lv, base), null, 'a column with a section goes as triangles');
  assert.equal(F.prism(Object.assign({}, col, { pos: [0, 1, 0] }), lv, base), null, 'moved by its pos');
  assert.equal(F.prism({ id: 'f2', t: 'solid', bim: { type: 'floor', thickness: 0.2, baseY: 0, profile: [[0, 0], [1, 0]] } }, lv, base), null, 'an outline needs three points');
  assert.equal(F.prism({ id: 'f3', t: 'solid', bim: { type: 'floor', thickness: 0, baseY: 0, profile: [[0, 0], [1, 0], [1, 1]] } }, lv, base), null);
  assert.equal(F.prism(wall(), lv, base), null);
  assert.equal(F.prism({ id: 'b', t: 'box' }, lv, base), null);
});

test('WO-13 bimIfcSaveOpening: a door or a window on the wall segment it stands in, or null', { skip: todo('opening', 'WO-13') }, () => {
  const walls = [
    { id: 'w1', x0: 0, y0: 0, x1: 6, y1: 0, base: 0, height: 3, thickness: 0.2, offset: -0.1 },
    { id: 'w1#1', x0: 6, y0: 0, x1: 6, y1: -4, base: 0, height: 3, thickness: 0.2, offset: -0.1 },
    { id: 'w2', x0: 0, y0: -10, x1: 6, y1: -10, base: 3.2, height: 3, thickness: 0.3, offset: 0 }];
  const base = { id: 'd1', name: 'Door_1', psets: [] };
  const door = { id: 'd1', t: 'opening', name: 'Door_1', bim: { type: 'door', hostWallId: 'w1', center: [2, 0.05], dir: [1, 0], width: 0.9, height: 2.1, sillHeight: 0 } };
  assert.deepEqual(F.opening(door, walls, base), { id: 'd1', name: 'Door_1', psets: [], cls: 'IfcDoor', host: 'w1', x: 2, y: 0, a: 0, base: 0, width: 0.9, height: 2.1, depth: 0.4 },
    'on the wall\'s line (its centre drawn onto it), cut 0.2 deeper than the wall is thick');
  const win = { id: 'n1', t: 'opening', bim: { type: 'window', hostWallId: 'w1', center: [6, 2], width: 1.2, height: 1.2, sillHeight: 0.9 } };
  const w = F.opening(win, walls, base);
  assert.equal(w.cls, 'IfcWindow');
  assert.equal(w.host, 'w1#1', 'the segment of its wall it is nearest');
  assert.deepEqual([w.x, w.y, w.base], [6, -2, 0.9]);
  assert.ok(Math.abs(w.a + Math.PI / 2) < 1e-9, 'the segment\'s direction');
  const up = F.opening({ id: 'n2', t: 'opening', bim: { type: 'window', hostWallId: 'w2', center: [3, 10], width: 1, height: 1, sillHeight: 1 } }, walls, base);
  assert.deepEqual([up.host, up.base, up.depth], ['w2', 4.2, 0.5], 'its sill above its wall\'s base');
  assert.equal(F.opening(Object.assign({}, door, { bim: Object.assign({}, door.bim, { hostWallId: 'w9' }) }), walls, base), null, 'its wall is not among the straight walls');
  assert.equal(F.opening(Object.assign({}, door, { bim: Object.assign({}, door.bim, { hostWallId: 'w' }) }), walls, base), null, 'w is not w1');
  assert.equal(F.opening(Object.assign({}, door, { bim: Object.assign({}, door.bim, { width: 0 }) }), walls, base), null);
  assert.equal(F.opening(Object.assign({}, door, { t: 'solid' }), walls, base), null, 'only an opening marker');
  assert.equal(F.opening({ id: 'x', t: 'opening', bim: { type: 'note' } }, walls, base), null);
});

test('WO-14 bimIfcSaveMesh: any element as its corners and triangles in IFC\'s axes, with its IFC class', { skip: todo('mesh', 'WO-14') }, () => {
  const lv = F.levels(LEVELS), base = { id: 'm1', name: 'Roof_1', psets: [] };
  const m = F.mesh({ id: 'm1', t: 'solid', pos: [10, 3.2, 0], bim: { type: 'roof' } }, box, lv, base);
  assert.equal(m.cls, 'IfcRoof');
  assert.equal(m.level, 1, 'by its lowest corner');
  assert.equal(m.verts.length, 8);
  assert.deepEqual(m.verts[6], [11, -1, 5.2], 'moved by its pos, then turned: [x, -z, y]');
  assert.equal(m.faces.length, 12, 'each four-cornered face as two triangles');
  assert.deepEqual(m.faces.slice(0, 2), [[0, 1, 2], [0, 2, 3]], 'a fan from the face\'s first corner');
  assert.equal(m.id, 'm1');
  assert.equal(F.mesh({ id: 'i1', t: 'solid', bim: { type: 'ifc', imported: true, ifcType: 'IfcWallStandardCase' } }, box, lv, base).cls, 'IfcWall', 'an imported element keeps its class');
  assert.equal(F.mesh({ id: 'i2', t: 'solid', bim: { type: 'ifc', imported: true, ifcType: 'IfcFurniture' } }, box, lv, base).cls, 'IfcFurniture');
  assert.equal(F.mesh({ id: 'i3', t: 'solid', bim: { type: 'ifc', imported: true, ifcType: 'not a class' } }, box, lv, base).cls, 'IfcBuildingElementProxy');
  assert.equal(F.mesh({ id: 'b1', t: 'box' }, box, lv, base).cls, 'IfcBuildingElementProxy', 'no bim record');
  assert.equal(F.mesh({ id: 'b1', t: 'box' }, box, lv, base).level, 0);
  assert.equal(F.mesh({ id: 'e1', t: 'solid' }, null, lv, base), null);
  assert.equal(F.mesh({ id: 'e2', t: 'solid' }, { v: [[0, 0, 0], [1, 0, 0]], f: [[0, 1]] }, lv, base), null, 'no triangle');
});

test('WO-15 bimIfcSaveModel: the whole model, each element once, and what could not be written', { skip: todo('model', 'WO-15') }, () => {
  const entries = [
    { o: wall(), mesh: box, layer: 'Walls' },
    { o: { id: 'd1', t: 'opening', name: 'Door_1', bim: { type: 'door', hostWallId: 'w1', center: [2, 0], width: 0.9, height: 2.1, sillHeight: 0 } }, mesh: null, layer: 'Walls' },
    { o: { id: 'f1', t: 'solid', name: 'Floor_1', pos: [0, 0, 0], bim: { type: 'floor', thickness: 0.2, baseY: 0, levelId: 'lvl-0', profile: [[0, 0], [6, 0], [6, 4], [0, 4]] } }, mesh: box, layer: 'Floors' },
    { o: wall({ id: 'w2', name: 'Arc wall', bim: Object.assign({}, wall().bim, { bulges: [0.4] }) }), mesh: box, layer: 'Walls' },
    { o: { id: 'd2', t: 'opening', name: 'Door_2', bim: { type: 'door', hostWallId: 'w2', center: [2, 0], width: 0.9, height: 2.1 } }, mesh: null, layer: 'Walls' },
    { o: { id: 'r1', t: 'solid', name: 'Roof_1', bim: { type: 'roof' } }, mesh: box, layer: 'Roofs' },
    { o: { id: 'g1', t: 'solid', name: 'Ghost' }, mesh: null, layer: '0' }];
  const r = F.model('House', LEVELS, entries);
  assert.equal(r.model.name, 'House');
  assert.deepEqual(r.model.levels, [{ name: 'Ground', elev: 0 }, { name: 'First', elev: 3.2 }]);
  assert.deepEqual(r.model.walls.map((w) => w.id), ['w1']);
  assert.deepEqual(r.model.prisms.map((p) => [p.id, p.cls]), [['f1', 'IfcSlab']]);
  assert.deepEqual(r.model.openings.map((o) => [o.id, o.host]), [['d1', 'w1']]);
  assert.deepEqual(r.model.meshes.map((m) => [m.id, m.cls]), [['w2', 'IfcWall'], ['r1', 'IfcRoof']], 'the arc wall goes as its triangles, still a wall');
  assert.deepEqual(r.left, [{ id: 'g1', why: 'no shape' }, { id: 'd2', why: 'its wall is not written as a straight wall' }]);
  assert.equal(r.model.walls[0].psets[0].props.Layer, 'Walls');
  assert.doesNotThrow(() => JSON.stringify(r.model), 'plain data');
  const e = F.model('', [], []);
  assert.deepEqual(e, { model: { name: 'Project', levels: [], walls: [], prisms: [], openings: [], meshes: [] }, left: [] });
});
