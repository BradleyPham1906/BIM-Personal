// V181: the pure grid, path, exit and travel-limit functions (bim/interiors-routes.js).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const ROOM = [[0, 0], [10, 0], [10, 4], [0, 4]];
const WALL = [[4, 0], [5, 0], [5, 3], [4, 3]];
const near = (a, b, e = 1e-9, m = '') => assert.ok(Math.abs(a - b) <= e, `${m} ${a} is not ${b}`);

test('V181 grid cells are inside the room and outside obstacles', () => {
  const g = E.bimEgGrid(ROOM, [WALL], 1);
  assert.deepEqual([g.x0, g.z0, g.cell, g.nx, g.nz], [0, 0, 1, 10, 4]);
  assert.deepEqual(Array.from(g.free.slice(0, 10)), [1, 1, 1, 1, 0, 1, 1, 1, 1, 1]);
  assert.equal(g.free[3 * 10 + 4], 1);
  assert.equal(E.bimEgGrid(ROOM, [], 0), null);
  assert.equal(E.bimEgGrid([[0, 0], [1, 1]], [], 1), null);
});

test('V181 cell lookup rejects blocked and outside points', () => {
  const g = E.bimEgGrid(ROOM, [WALL], 1);
  assert.equal(E.bimEgCell(g, [0.5, 0.5]), 0);
  assert.equal(E.bimEgCell(g, [4.5, 0.5]), -1);
  assert.equal(E.bimEgCell(g, [12, 1]), -1);
});

test('V181 shortest grid routes avoid obstacles without cutting corners', () => {
  const g = E.bimEgGrid(ROOM, [WALL], 1);
  const r = E.bimEgPath(g, [0.5, 0.5], [9.5, 0.5]);
  near(r.len, 3 + 6 * Math.SQRT2, 1e-9, 'route length');
  assert.equal(r.cells[0], 0);
  assert.equal(r.cells[r.cells.length - 1], 9);
  const shut = E.bimEgGrid(ROOM, [[[4, 0], [5, 0], [5, 4], [4, 4]]], 1);
  assert.equal(E.bimEgPath(shut, [0.5, 0.5], [9.5, 0.5]), null);
  assert.equal(E.bimEgPath(g, [4.5, 0.5], [9.5, 0.5]), null);
});

test('V181 chooses the nearest reachable exit, breaking ties by name', () => {
  assert.deepEqual(E.bimEgNearest({ east: { len: 9 }, west: { len: 4 }, north: null }), { exit: 'west', len: 4 });
  assert.deepEqual(E.bimEgNearest({ b: { len: 4 }, a: { len: 4 } }), { exit: 'a', len: 4 });
  assert.equal(E.bimEgNearest({ a: null }), null);
});

test('V181 distinguishes blocked, unassessed and within-limit routes', () => {
  assert.deepEqual(E.bimEgStatus({ exit: 'a', len: 12.34 }, 30), { status: 'within', why: '12.3 m of 30 m' });
  assert.deepEqual(E.bimEgStatus({ exit: 'a', len: 45 }, 30), { status: 'over', why: '45.0 m, over 30 m' });
  assert.deepEqual(E.bimEgStatus(null, 30), { status: 'blocked', why: 'no route to an exit' });
  assert.deepEqual(E.bimEgStatus({ exit: 'a', len: 5 }, null), { status: 'not evaluated', why: 'no travel limit chosen' });
});

test('V181 routes from rooms to marked doors with no default limit', () => {
  const oldObjs = E.A3D.objs;
  const oldSite = E.A3D.site;
  try {
    E.A3D.site = { name: 'Test site', std: { ov: {}, pick: {}, packs: [] } };
    E.A3D.objs = [
      { id: 'room-1', t: 'room', name: 'Room 1', pts: [[0, 0], [4, 0], [4, 4], [0, 4]], y: 0 },
      { id: 'wall-1', t: 'solid', bim: { type: 'wall', centerline: [[0, 0], [4, 0]], thickness: 0.15, baseY: 0, height: 3 } },
      { id: 'door-1', t: 'opening', name: 'North door', bim: { type: 'door', center: [2, 0], width: 1, hostWallId: 'wall-1', exit: true } }
    ];
    const result = E.bimEgRouteRun();
    assert.equal(result.state, 'on');
    assert.match(result.status, /1 rooms: 0 within, 0 over, 0 blocked, 1 not evaluated/);
    const card = E.bimEgRouteCard();
    assert.match(card.extra, /Not chosen/);
    assert.match(card.extra, /not an egress-compliance finding/);
    assert.match(card.extra, /not evaluated: North door/);
    assert.equal(card.hideDisabled, false);
    E.bimEgRouteHide();
    const hidden = E.bimEgRouteCard();
    assert.equal(hidden.state, 'off');
    assert.equal(hidden.hideDisabled, true);
  } finally {
    E.A3D.objs = oldObjs;
    E.A3D.site = oldSite;
  }
});

test('V181 circulation and exits is listed in Model and enabled with no rooms', () => {
  const oldObjs = E.A3D.objs;
  try {
    E.A3D.objs = [];
    const card = E.bimAnzCards().find((item) => item.id === 'egress');
    assert.ok(card);
    assert.ok(E.BIM_ANZ_MODEL.includes('egress'));
    assert.equal(card.acts.find((act) => act.act === 'egress:run').off, false);
  } finally {
    E.A3D.objs = oldObjs;
  }
});

test('V181 registry limit is explicitly unset and can be overridden by the project', () => {
  assert.equal(E.bimStd('app.egress', 'limit'), 0);
  const edition = E.bimStdEdition('app.egress');
  assert.match(edition.name, /Owner-selected/);
  const oldSite = E.A3D.site;
  try {
    E.A3D.site = { name: 'Test site', std: { ov: { 'app.egress|limit': { v: 10, why: 'project test', at: '2026-01-01' } }, pick: {}, packs: [] } };
    assert.equal(E.bimStd('app.egress', 'limit'), 10);
  } finally {
    E.A3D.site = oldSite;
  }
});

// The audit (2026-11-21): a point within one cell below or left of the grid used to truncate into cell 0.
test('V181 a point just outside the low corner is outside the grid; a non-number cell gives no grid', () => {
  const g = E.bimEgGrid(ROOM, [], 1);
  assert.equal(E.bimEgCell(g, [-0.5, 0.5]), -1);
  assert.equal(E.bimEgCell(g, [0.5, -0.5]), -1);
  assert.equal(E.bimEgGrid(ROOM, [], undefined), null);
  assert.equal(E.bimEgGrid(ROOM, [], NaN), null);
});
