/* V177's JavaScript work orders (docs/work-orders/v177/SPEC.md, WO-09 to WO-17): the pure functions of
   src/js/engine/io/ifc-export.js that turn the app's model into the plain model bim_ifcos_save_model writes.

   Outside tests/unit/ while the work orders are open, so `npm test` and CI stay green on main. Run them with:
     node --test docs/work-orders/v177/v177-js.test.mjs
   One work order's cases only (WO-12, say):
     node --test --test-name-pattern="WO-12" docs/work-orders/v177/v177-js.test.mjs
   A function not built yet fails its own cases and no others. The functions use no name from another file: the file
   is read as text. Claude moves this file to tests/unit/ifc-export.test.mjs when all pass (WO-18). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimIfcxPlan', 'bimIfcxLevels', 'bimIfcxLevelOf', 'bimIfcxWalls', 'bimIfcxSlab', 'bimIfcxColumn',
  'bimIfcxOpening', 'bimIfcxMesh', 'bimIfcxModel'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/io/ifc-export.js'), 'utf8');
  if (process.env.V177_REF_JS) src += fs.readFileSync(process.env.V177_REF_JS, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/io/ifc-export.js'); return X[n]; };
const near = (a, b) => assert.ok(Math.abs(a - b) < 1e-9, a + ' is not ' + b);

const LV = [{ id: 'L1', name: 'First', elev: 3, height: 3 }, { id: 'L0', name: 'Ground', elev: 0, height: 3 }];
const LEVELS = [{ id: 'L0', name: 'Ground', elevation: 0 }, { id: 'L1', name: 'First', elevation: 3 }];

/* ---------------- WO-09 bimIfcxPlan ---------------- */
test('WO-09 the plan point [x, z] is IFC [x, -z], never -0', () => {
  assert.deepEqual(fn('bimIfcxPlan')([2, 5]), [2, -5]);
  assert.deepEqual(fn('bimIfcxPlan')([2, -5]), [2, 5]);
  assert.ok(Object.is(fn('bimIfcxPlan')([1, 0])[1], 0));
});

/* ---------------- WO-10 bimIfcxLevels ---------------- */
test('WO-10 levels by elevation, names kept, bad ones left out', () => {
  assert.deepEqual(fn('bimIfcxLevels')(LV), LEVELS);
  assert.deepEqual(fn('bimIfcxLevels')([{ id: 7, elev: 1 }, { id: 'x', elev: NaN }, null]), [{ id: '7', name: 'Level 0', elevation: 1 }]);
  assert.deepEqual(fn('bimIfcxLevels')(null), []);
});

/* ---------------- WO-11 bimIfcxLevelOf ---------------- */
test('WO-11 by its id, else the highest level at or below y, else the first', () => {
  assert.equal(fn('bimIfcxLevelOf')(LEVELS, 'L1', 0), 'L1');
  assert.equal(fn('bimIfcxLevelOf')(LEVELS, 'gone', 3.2), 'L1');
  assert.equal(fn('bimIfcxLevelOf')(LEVELS, null, 2.9), 'L0');
  assert.equal(fn('bimIfcxLevelOf')(LEVELS, null, -1), 'L0');
  assert.equal(fn('bimIfcxLevelOf')([], 'L0', 0), '');
});

/* ---------------- WO-12 bimIfcxWalls ---------------- */
const wall = (extra) => ({ id: 'w1', t: 'solid', name: 'Wall_1', bim: Object.assign({ type: 'wall', thickness: 0.2, height: 3, align: 'center', baseY: 0, closed: false, centerline: [[0, 0], [5, 0]] }, extra) });
test('WO-12 a straight wall: one entry, the line in IFC plan, centred', () => {
  assert.deepEqual(fn('bimIfcxWalls')(wall({ centerline: [[0, 0], [0, 4]] }), LEVELS),
    [{ id: 'w1', host: 'w1', name: 'Wall_1', level: 'L0', x0: 0, y0: 0, x1: 0, y1: -4, z: 0, height: 3, thickness: 0.2, offset: -0.1 }]);
});
test('WO-12 left and right alignment, and explicit offsets', () => {
  const l = fn('bimIfcxWalls')(wall({ align: 'left' }), LEVELS)[0];
  near(l.thickness, 0.2); near(l.offset, 0);
  const r = fn('bimIfcxWalls')(wall({ align: 'right' }), LEVELS)[0];
  near(r.thickness, 0.2); near(r.offset, -0.2);
  const o = fn('bimIfcxWalls')(wall({ align: { dLeft: 0.05, dRight: 0.25 } }), LEVELS)[0];
  near(o.thickness, 0.3); near(o.offset, -0.05);
});
test('WO-12 a polyline: one entry per segment; closed adds the last; arcs and non-walls give none', () => {
  const s = fn('bimIfcxWalls')(wall({ centerline: [[0, 0], [4, 0], [4, 3]], baseY: 3 }), LEVELS);
  assert.deepEqual(s.map((e) => [e.id, e.name, e.level]), [['w1#0', 'Wall_1 1', 'L1'], ['w1#1', 'Wall_1 2', 'L1']]);
  assert.equal(fn('bimIfcxWalls')(wall({ centerline: [[0, 0], [4, 0], [4, 3]], closed: true }), LEVELS).length, 3);
  assert.deepEqual(fn('bimIfcxWalls')(wall({ bulges: [0.5, 0] }), LEVELS), []);
  assert.deepEqual(fn('bimIfcxWalls')({ id: 'x', bim: { type: 'floor' } }, LEVELS), []);
  assert.deepEqual(fn('bimIfcxWalls')(null, LEVELS), []);
});

/* ---------------- WO-13 bimIfcxSlab ---------------- */
test('WO-13 a floor: its outline in IFC plan, its bottom and depth', () => {
  const f = { id: 'f1', name: 'Floor_1', bim: { type: 'floor', thickness: 0.25, baseY: 3, levelId: 'L1', profile: [[0, 0], [6, 0], [6, 4], [0, 4]] } };
  assert.deepEqual(fn('bimIfcxSlab')(f, LEVELS), { id: 'f1', name: 'Floor_1', level: 'L1', points: [[0, 0], [6, 0], [6, -4], [0, -4]], z: 2.75, depth: 0.25 });
  assert.equal(fn('bimIfcxSlab')({ id: 'f', bim: { type: 'floor', thickness: 0.2, baseY: 0, profile: [[0, 0], [1, 0]] } }, LEVELS), null);
  assert.equal(fn('bimIfcxSlab')(wall({}), LEVELS), null);
});

/* ---------------- WO-14 bimIfcxColumn ---------------- */
test('WO-14 a rectangular column: centre in IFC plan, the turn reversed', () => {
  const c = { id: 'c1', name: 'Column_1', bim: { type: 'column', width: 0.4, depth: 0.3, height: 3, baseY: 0, levelId: 'L0', center: [2, 3], rotation: 0.5 } };
  assert.deepEqual(fn('bimIfcxColumn')(c, LEVELS), { id: 'c1', name: 'Column_1', level: 'L0', x: 2, y: -3, z: 0, width: 0.4, depth: 0.3, height: 3, rotation: -0.5 });
  assert.ok(Object.is(fn('bimIfcxColumn')(Object.assign({}, c, { bim: Object.assign({}, c.bim, { rotation: undefined }) }), LEVELS).rotation, 0));
  assert.equal(fn('bimIfcxColumn')(Object.assign({}, c, { bim: Object.assign({}, c.bim, { section: { kind: 'I' } }) }), LEVELS), null);
});

/* ---------------- WO-15 bimIfcxOpening ---------------- */
test('WO-15 a door on its host wall: the segment it lies on and the distance along it', () => {
  const ws = fn('bimIfcxWalls') ? X.bimIfcxWalls(wall({ centerline: [[0, 0], [4, 0], [4, 3]] }), LEVELS) : [];
  const d = { id: 'd1', t: 'opening', name: 'Door_1', bim: { type: 'door', hostWallId: 'w1', center: [4, 1], dir: [0, 1], width: 0.9, height: 2.1, sillHeight: 0 } };
  const r = fn('bimIfcxOpening')(d, ws);
  assert.deepEqual(r, { id: 'd1', name: 'Door_1', kind: 'door', wall: 'w1#1', along: 1, sill: 0, width: 0.9, height: 2.1 });
});
test('WO-15 a window keeps its sill; no host, off every segment or not an opening: null', () => {
  const ws = [{ id: 'w1', host: 'w1', x0: 0, y0: 0, x1: 5, y1: 0 }];
  const w = { id: 'n1', name: 'Window_1', bim: { type: 'window', hostWallId: 'w1', center: [2, 0], width: 1.2, height: 1, sillHeight: 0.9 } };
  assert.deepEqual(fn('bimIfcxOpening')(w, ws), { id: 'n1', name: 'Window_1', kind: 'window', wall: 'w1', along: 2, sill: 0.9, width: 1.2, height: 1 });
  assert.equal(fn('bimIfcxOpening')(Object.assign({}, w, { bim: Object.assign({}, w.bim, { hostWallId: 'w9' }) }), ws), null);
  assert.equal(fn('bimIfcxOpening')(Object.assign({}, w, { bim: Object.assign({}, w.bim, { center: [7, 0] }) }), ws), null);
  assert.equal(fn('bimIfcxOpening')({ id: 'x', bim: { type: 'wall' } }, ws), null);
});

/* ---------------- WO-16 bimIfcxMesh ---------------- */
const BOX = { v: [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1], [0, 1, 0], [1, 1, 0], [1, 1, 1], [0, 1, 1]], f: [[0, 1, 2, 3], [4, 5], [7, 6, 5, 4]] };
test('WO-16 a solid as a mesh: moved by pos, Y-up to Z-up, short faces dropped, class by type', () => {
  const r = fn('bimIfcxMesh')({ id: 'r1', name: 'Roof_1', t: 'solid', pos: [10, 3, 0], mesh: BOX, bim: { type: 'roof' } }, LEVELS);
  assert.equal(r.ifcClass, 'IfcRoof');
  assert.equal(r.level, 'L1');
  assert.deepEqual(r.vertices[2], [11, -1, 3]);
  assert.deepEqual(r.faces, [[0, 1, 2, 3], [7, 6, 5, 4]]);
  assert.notEqual(r.faces[0], BOX.f[0], 'the faces are copies');
});
test('WO-16 an imported IFC type is kept; anything else is a proxy; no mesh: null', () => {
  assert.equal(fn('bimIfcxMesh')({ id: 'a', mesh: BOX, bim: { ifcType: 'IfcStairFlight' } }, LEVELS).ifcClass, 'IfcStairFlight');
  assert.equal(fn('bimIfcxMesh')({ id: 'b', mesh: BOX, bim: { ifcType: 'not a class' } }, LEVELS).ifcClass, 'IfcBuildingElementProxy');
  assert.equal(fn('bimIfcxMesh')({ id: 'c', mesh: BOX }, LEVELS).ifcClass, 'IfcBuildingElementProxy');
  assert.equal(fn('bimIfcxMesh')({ id: 'd', mesh: { v: [], f: [] } }, LEVELS), null);
});

/* ---------------- WO-17 bimIfcxModel ---------------- */
test('WO-17 the whole model, each kind in its list, openings last, a pset for every element', () => {
  const objs = [
    wall({}),
    { id: 'f1', t: 'solid', name: 'Floor_1', bim: { type: 'floor', thickness: 0.2, baseY: 0, profile: [[0, 0], [5, 0], [5, 4]] } },
    { id: 'c1', t: 'solid', name: 'Column_1', bim: { type: 'column', width: 0.3, depth: 0.3, height: 3, baseY: 0, center: [1, 1] } },
    { id: 'd1', t: 'opening', name: 'Door_1', bim: { type: 'door', hostWallId: 'w1', center: [2, 0], width: 0.9, height: 2.1 } },
    { id: 'r1', t: 'solid', name: 'Roof_1', pos: [0, 0, 0], mesh: BOX, bim: { type: 'roof' } },
    { id: 'l1', t: 'line', name: 'Line', pts: [[0, 0, 0], [1, 0, 0]] },
    null
  ];
  const m = fn('bimIfcxModel')(objs, LV, 'House');
  assert.equal(m.name, 'House');
  assert.deepEqual(m.levels, LEVELS);
  assert.deepEqual([m.walls.length, m.slabs.length, m.columns.length, m.openings.length, m.meshes.length], [1, 1, 1, 1, 1]);
  assert.equal(m.openings[0].wall, 'w1');
  assert.deepEqual(m.psets.map((p) => p.id), ['w1', 'f1', 'c1', 'r1']);
  assert.deepEqual(m.psets[0], { id: 'w1', name: 'BIM_Personal', props: { AppId: 'w1', Name: 'Wall_1' } });
  assert.deepEqual(fn('bimIfcxModel')(null, null, ''), { name: 'Project', levels: [], walls: [], slabs: [], columns: [], openings: [], meshes: [], psets: [] });
});
