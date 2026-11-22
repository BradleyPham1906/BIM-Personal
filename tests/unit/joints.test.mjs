// V273: assemblies (engine/assembly/joints.js): the joint tree, the hinge arithmetic, the bill of materials.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);
const objs = [{ id: 'base' }, { id: 'door', joint: { parent: 'base' } }, { id: 'handle', joint: { parent: 'door' } }, { id: 'other', joint: { parent: 'base' } }];

test('the tree: a part and everything joined below it; a loop is refused; the root', () => {
  assert.deepEqual(E.bimJointSubtree(objs, 'door'), ['door', 'handle']);
  assert.deepEqual(E.bimJointSubtree(objs, 'base').sort(), ['base', 'door', 'handle', 'other']);
  assert.equal(E.bimJointWouldLoop(objs, 'handle', 'door'), true, 'the door under its own handle');
  assert.equal(E.bimJointWouldLoop(objs, 'other', 'door'), false);
  assert.equal(E.bimJointRoot(objs, 'handle'), 'base');
});

test('a hinge turns counter-clockwise on the plan for a positive angle (north is -z); limits hold', () => {
  const p = E.bimJointTurnPt([1, 0], [0, 0], 90);   // east, turned a quarter counter-clockwise: north
  near(p[0], 0); near(p[1], -1);
  const d = E.bimJointTurnDir([1, 0.5, 0], 90);
  near(d[0], 0); near(d[1], 0.5); near(d[2], -1);
  assert.equal(E.bimJointClamp({ min: -90, max: 90 }, 120), 90);
  assert.equal(E.bimJointClamp({ min: 0, max: 1 }, -2), 0);
});

test('the bill of materials counts parts by name and material', () => {
  const parts = [{ name: 'Leg 1', m: 'Wood' }, { name: 'Leg 2', m: 'Wood' }, { name: 'Leg_3 copy', m: 'Wood' }, { name: 'Top', m: 'Glass' }, { name: 'Leg 4', m: 'Steel' }];
  const rows = E.bimBomRows(parts, (o) => ({ material: o.m, volume: 0.01, mass: o.m === 'Wood' ? 7 : 2 }));
  assert.deepEqual(rows.map((r) => [r.part, r.material, r.count]), [['Leg', 'Wood', 3], ['Leg', 'Steel', 1], ['Top', 'Glass', 1]]);
  const csv = E.bimBomCsv([{ part: 'A, "big"', material: '', count: 2, volume: 1, mass: null }]);
  assert.equal(csv.split('\n')[1], '"A, ""big""",,2,1,');
});
