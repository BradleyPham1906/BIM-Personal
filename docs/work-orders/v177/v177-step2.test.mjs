/* V177's work-order tests (docs/work-orders/v177/SPEC.md, WO-11 to WO-19): the pure functions of src/js/engine/io/ifc-save.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v177/v177-step2.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v177/v177-step2.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimIfsPlan", "bimIfsLevels", "bimIfsLevelIndex", "bimIfsWalls", "bimIfsSlab", "bimIfsColumn", "bimIfsOpening", "bimIfsMesh", "bimIfsModel"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/io/ifc-save.js'), 'utf8');
  if (process.env.V177_REF) src += fs.readFileSync(process.env.V177_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/io/ifc-save.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const LV = [{ id: 'L1', name: 'First', elev: 3 }, { id: 'L0', name: 'Ground', elev: 0 }];
const SORTED = [{ id: 'L0', name: 'Ground', elev: 0 }, { id: 'L1', name: 'First', elev: 3 }];
const wall = (x) => ({ id: 'w1', t: 'solid', name: 'Wall_1', bim: Object.assign({ type: 'wall', thickness: 0.2, height: 3, align: 'center', baseY: 0, closed: false, centerline: [[0, 0], [5, 0]] }, x) });
test('WO-11 the plan point [x, z] as IFC [x, -z], never -0', () => {
  assert.deepEqual(fn('bimIfsPlan')([2, 5]), [2, -5]); assert.ok(Object.is(fn('bimIfsPlan')([1, 0])[1], 0));
});
test('WO-12 levels by elevation, names kept, bad ones left out', () => {
  assert.deepEqual(fn('bimIfsLevels')(LV), SORTED);
  assert.deepEqual(fn('bimIfsLevels')([{ id: 7, elev: 1 }, { elev: NaN }]), [{ id: '7', name: 'Level 0', elev: 1 }]);
});
test('WO-13 a level\'s index: by id, else the highest at or below y, else 0', () => {
  const f = fn('bimIfsLevelIndex');
  assert.deepEqual([f(SORTED, 'L1', 0), f(SORTED, 'x', 3.2), f(SORTED, null, 2.9), f(SORTED, null, -1), f([], 'L0', 5)], [1, 1, 0, 0, 0]);
});
test('WO-14 walls by straight segment, with the side as V177\'s offset (0 - dLeft)', () => {
  assert.deepEqual(fn('bimIfsWalls')(wall({ centerline: [[0, 0], [0, 4]], guid: '0abcdefghijklmnopqrstu' }), SORTED),
    [{ id: 'w1', host: 'w1', name: 'Wall_1', level: 0, x0: 0, y0: 0, x1: 0, y1: -4, base: 0, height: 3, thickness: 0.2, offset: -0.1, guid: '0abcdefghijklmnopqrstu' }]);
  near(fn('bimIfsWalls')(wall({ align: 'right' }), SORTED)[0].offset, -0.2);
  assert.equal(fn('bimIfsWalls')(wall({ centerline: [[0, 0], [4, 0], [4, 3]], closed: true }), SORTED).length, 3);
  assert.deepEqual(fn('bimIfsWalls')(wall({ bulges: [1, 0] }), SORTED), []);
});
test('WO-15 a floor as a slab prism: its bottom and depth', () => {
  assert.deepEqual(fn('bimIfsSlab')({ id: 'f1', name: 'F', bim: { type: 'floor', thickness: 0.25, baseY: 3, levelId: 'L1', profile: [[0, 0], [6, 0], [6, 4]] } }, SORTED),
    { id: 'f1', name: 'F', level: 1, cls: 'IfcSlab', pts: [[0, 0], [6, 0], [6, -4]], base: 2.75, depth: 0.25 });
});
test('WO-16 a rectangular column as a prism: its corners in IFC plan, anticlockwise', () => {
  const c = fn('bimIfsColumn')({ id: 'c1', name: 'C', bim: { type: 'column', width: 0.4, depth: 0.2, height: 3, baseY: 0, center: [1, 1], rotation: 0 } }, SORTED);
  assert.deepEqual(c.pts, [[0.8, -0.9], [1.2, -0.9], [1.2, -1.1], [0.8, -1.1]].reverse().map((p) => p));
  let s = 0; for (let i = 0; i < 4; i++) { const a = c.pts[i], b = c.pts[(i + 1) % 4]; s += a[0] * b[1] - b[0] * a[1]; }
  assert.ok(s > 0, 'anticlockwise in IFC plan');
  assert.deepEqual([c.cls, c.base, c.depth], ['IfcColumn', 0, 3]);
  assert.equal(fn('bimIfsColumn')({ id: 'c', bim: { type: 'column', center: [0, 0], section: {} } }, SORTED), null);
});
test('WO-17 a door on its wall\'s segment: the middle on the line, the wall\'s direction, its foot and cut depth', () => {
  const ws = X.bimIfsWalls(wall({ centerline: [[0, 0], [4, 0], [4, 3]], baseY: 3 }), SORTED);
  const d = fn('bimIfsOpening')({ id: 'd1', name: 'D', bim: { type: 'door', hostWallId: 'w1', center: [4.05, 1], width: 0.9, height: 2.1 } }, ws);
  assert.equal(d.host, 'w1#1'); near(d.x, 4); near(d.y, -1); near(d.a, -Math.PI / 2); near(d.base, 3); near(d.depth, 0.3);
  assert.equal(d.cls, 'IfcDoor');
  assert.equal(fn('bimIfsOpening')({ id: 'n', bim: { type: 'window', hostWallId: 'w1', center: [9, 9], width: 1, height: 1, sillHeight: 0.9 } }, ws), null);
});
test('WO-18 any other solid as a triangle mesh: Y-up to Z-up, faces fanned, class by type', () => {
  const m = fn('bimIfsMesh')({ id: 'r', name: 'R', pos: [10, 3, 0], mesh: { v: [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]], f: [[0, 1, 2, 3]] }, bim: { type: 'roof' } }, SORTED);
  assert.deepEqual(m.faces, [[0, 1, 2], [0, 2, 3]]); assert.deepEqual(m.verts[2], [11, -1, 3]); assert.equal(m.cls, 'IfcRoof'); assert.equal(m.level, 1);
});
test('WO-19 the whole model in V177\'s format; openings after walls', () => {
  const m = fn('bimIfsModel')([wall({}), { id: 'd1', t: 'opening', name: 'D', bim: { type: 'door', hostWallId: 'w1', center: [2, 0], width: 0.9, height: 2.1 } },
    { id: 'f1', t: 'solid', name: 'F', bim: { type: 'floor', thickness: 0.2, baseY: 0, profile: [[0, 0], [5, 0], [5, 4]] } }, { id: 'l', t: 'line' }, null], LV, 'House');
  assert.deepEqual(m.levels, [{ name: 'Ground', elev: 0 }, { name: 'First', elev: 3 }]);
  assert.deepEqual([m.walls.length, m.prisms.length, m.openings.length, m.meshes.length], [1, 1, 1, 0]);
  assert.equal(m.openings[0].host, 'w1'); assert.equal(m.name, 'House');
});
