// V177 Make editable: the plan of the rebuild from an imported wall's or floor's kept parameters (io/ifc-editable.js).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
// a box mesh from its two corners
const boxMesh = (a, b) => ({ v: [[a[0], a[1], a[2]], [b[0], b[1], b[2]], [a[0], b[1], a[2]], [b[0], a[1], b[2]]], f: [] });
// a 4 m wall along IFC's x, 0.2 thick, centred on y = 1 (north): in the app it stands at z = -1
const WALL = { profile: [[0, 0.9], [4, 0.9], [4, 1.1], [0, 1.1]], baseY: 0, height: 3, voided: false,
  wall: { centerline: [[0, 1], [4, 1]], thickness: 0.2, baseY: 0, height: 3 } };
const wallObj = (mesh, edit) => ({ name: 'W', mesh, bim: { type: 'wall', imported: true, guid: '0123456789abcdefghijkl', edit } });

test('V177 Make editable: a wall is placed where the imported shape is, in the app\'s axes (z = -north)', () => {
  const P = E.bimIfcEditPlan(wallObj(boxMesh([0, 0, -1.1], [4, 3, -0.9]), WALL));
  assert.equal(P.kind, 'wall');
  assert.deepEqual(P.pts, [[0, -1], [4, -1]]);
  assert.equal(P.thickness, 0.2); assert.equal(P.height, 3);
});
test('V177 Make editable: the reader\'s own axes are taken when that is where the shape is', () => {
  const P = E.bimIfcEditPlan(wallObj(boxMesh([0, 0, 0.9], [4, 3, 1.1]), WALL));
  assert.deepEqual(P.pts, [[0, 1], [4, 1]]);
});
test('V177 Make editable: refused with a reason', () => {
  assert.match(E.bimIfcEditPlan(wallObj(boxMesh([0, 0, -1.1], [4, 3, -0.9]), { ...WALL, voided: true })).why, /opening/);
  assert.match(E.bimIfcEditPlan(wallObj(boxMesh([0, 0, -1.1], [4, 3, -0.9]), { ...WALL, wall: null })).why, /rectangle/);
  assert.match(E.bimIfcEditPlan(wallObj(boxMesh([10, 0, 10], [14, 3, 11]), WALL)).why, /elsewhere/);
  assert.match(E.bimIfcEditPlan(wallObj(boxMesh([0, 0, 0], [1, 1, 1]), null)).why, /vertical extrusion/);
  assert.match(E.bimIfcEditPlan({ name: 'C', bim: { type: 'ifc', imported: true } }).why, /only imported walls and floors/);
  assert.match(E.bimIfcEditPlan({ name: 'X', bim: { type: 'wall' } }).why, /not imported/);
});
test('V177 Make editable: a floor takes its top and thickness', () => {
  const F = { profile: [[0, 0], [5, 0], [5, 4], [0, 4]], baseY: -0.25, height: 0.25, voided: false };
  const P = E.bimIfcEditPlan({ name: 'F', mesh: boxMesh([0, -0.25, -4], [5, 0, 0]), bim: { type: 'floor', imported: true, edit: F } });
  assert.equal(P.kind, 'floor'); assert.equal(P.top, 0); assert.equal(P.thickness, 0.25);
  assert.deepEqual(P.pts[2], [5, -4]);
});

// a 6 m wall, 0.3 thick, as IfcOpenShell 0.8.5 writes it through Save as IFC (an IfcIndexedPolyCurve profile)
test('V177 the walls-and-slabs reader follows IfcOpenShell\'s indexed curve profile', async () => {
  const fs = await import('node:fs'), path = await import('node:path'), { fileURLToPath } = await import('node:url');
  const f = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'fixtures', 'ifc', 'v177_wall_ifcos.ifc');
  const P = E.bimIfcEditParams(fs.readFileSync(f, 'utf8')), keys = Object.keys(P);
  assert.equal(keys.length, 1);
  const w = P[keys[0]];
  assert.equal(w.kind, 'wall'); assert.equal(w.voided, false); assert.equal(w.profile.length, 4);
  assert.ok(Math.abs(w.wall.thickness - 0.3) < 1e-9); assert.equal(w.height, 3);
});

test('V177 Make editable: the import\'s shift to the origin is added, so the element stays among its neighbours', () => {
  // measured 2026-11-21: a wall from (10, 20) to (16, 20) in the app, imported with the coordination matrix's shift
  const e = { profile: [[10, -20.15], [10, -19.85], [16, -19.85], [16, -20.15]], baseY: 0, height: 3, voided: false, shift: [-13, -1.5, -20],
    wall: { centerline: [[16, -20], [10, -20]], thickness: 0.3, baseY: 0, height: 3 } };
  const P = E.bimIfcEditPlan(wallObj(boxMesh([-3, -1.5, -0.15], [3, 1.5, 0.15]), e));
  assert.equal(P.kind, 'wall');
  assert.deepEqual(P.pts, [[3, 0], [-3, 0]]); assert.equal(P.y0, -1.5);
});
