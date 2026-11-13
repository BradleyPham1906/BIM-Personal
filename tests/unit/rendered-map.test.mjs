// V198, the map in the rendered view (render/rendered-map.js): the shaded view's tiles laid side by side on one canvas,
// the ground's squares and a terrain's corners placed on it, and the frame asking for tiles and keeping the store as
// the shaded view does. The picture itself is checked in a browser (tests/e2e/bim_phase198_rendered_map_browser_tests.py).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const F = globalThis.__a3dRvMap;
const near = (a, b, eps = 1e-6) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);
// the map's plan reads the view's own camera and canvas (groundPoint), so the tests set both
const V = () => E.camVecs(E.A3D.cam);
const TPL = 'https://tiles.example.org/{z}/{x}/{y}.png';
const img = (w = 256) => ({ naturalWidth: w, naturalHeight: w, w });

function withSite(fn) {
  const keep = { cam: E.A3D.cam, flat: E.A3D.flat, cv: E.el.cv, objs: E.A3D.objs, site: E.A3D.site, sel: E.A3D.sel, selSet: E.A3D.selSet, cache: E.A3D_MAP.cache, n: E.A3D_MAP.n, last: E.A3D.lastMapDrawn };
  try {
    E.bimSceneRelease();
    E.A3D.objs = []; E.A3D.sel = null; E.A3D.selSet = [];
    E.A3D.site = { name: 'Site', sun: { lat: 51.5, lon: -0.12, tz: 0 }, map: { style: 'custom', url: TPL } };
    E.A3D_MAP.cache = {}; E.A3D_MAP.n = 0; E.A3D_MAP.inflight = 0;
    E.A3D.cam = { yaw: 0.7, pitch: 0.9, dist: 120, tx: 0, ty: 0, tz: 0 }; E.A3D.flat = false;
    E.el.cv = Object.assign(document.createElement('canvas'), { width: 1500, height: 900, __a3dScale: 1 });
    return fn();
  } finally {
    E.el.cv = keep.cv;
    Object.assign(E.A3D, { cam: keep.cam, flat: keep.flat, objs: keep.objs, site: keep.site, sel: keep.sel, selSet: keep.selSet, lastMapDrawn: keep.last });
    E.A3D_MAP.cache = keep.cache; E.A3D_MAP.n = keep.n; E.A3D_MAP.inflight = 0;
    E.bimSceneRelease();
  }
}
// every tile of a list in the store, loaded
function loaded(tiles, w) {
  for (const t of tiles) {
    const url = F.tileUrl(TPL, t.x, t.y, t.z);
    E.A3D_MAP.cache[url] = { url, host: 'tiles.example.org', state: 'ok', img: img(w), seen: 0 };
    E.A3D_MAP.n++;
  }
}

test('tiles side by side: each in its own cell, a parent standing in drawn from its right quarter', () => {
  const tiles = [{ x: 10, y: 20, z: 5 }, { x: 11, y: 20, z: 5 }, { x: 10, y: 21, z: 5 }, { x: 11, y: 21, z: 5 }];
  const a = { img: img() }, p = { img: img() };
  const L = F.layout(tiles, [{ e: a, u0: 0, v0: 0, u1: 1, v1: 1, up: 0 }, null, null, { e: p, u0: 0.5, v0: 0.5, u1: 1, v1: 1, up: 1 }]);
  assert.deepEqual([L.x0, L.y0, L.cols, L.rows, L.z, L.cell], [10, 20, 2, 2, 5, 256]);
  assert.equal(L.draws.length, 2, 'a tile with nothing to show is not drawn');
  assert.deepEqual(L.draws[0], { img: a.img, sx: 0, sy: 0, sw: 256, sh: 256, cx: 0, cy: 0 });
  assert.deepEqual(L.draws[1], { img: p.img, sx: 128, sy: 128, sw: 128, sh: 128, cx: 1, cy: 1 }, 'the parent\'s south-east quarter, in the south-east cell');
  assert.deepEqual(F.uv(L, 10, 20), [0, 0], 'a tile\'s north-west corner is its cell\'s top left');
  assert.deepEqual(F.uv(L, 12, 22), [1, 1]);
  assert.deepEqual(F.uv(L, 11, 20.5), [0.5, 0.25]);
  assert.equal(F.layout(tiles, [{ e: { img: img(512) }, u0: 0, v0: 0, u1: 1, v1: 1, up: 0 }, null, null, null]).cell, 512, 'tiles at twice the density keep it');
  assert.equal(F.layout([], []), null);
});

test('the frame asks for the shaded view\'s tiles and keeps the store; nothing until they are in', () => withSite(() => {
  let M = F.frame(V(), 1500, 900, '#cbc6bb');
  assert.ok(M && M.plan.tiles.length > 0, 'the map is on: its tiles');
  assert.equal(M.drawn, 0, 'none loaded yet');
  assert.equal(E.A3D.lastMapDrawn.path, 'rendered', 'recorded as the rendered view\'s');
  assert.ok(E.A3D_MAP.n > 0, 'the tiles were asked for');
  assert.equal(F.flat(M), null, 'nothing to draw yet: the ground stays plain');
  E.A3D_MAP.cache = {}; E.A3D_MAP.n = 0; E.A3D_MAP.inflight = 0;
  loaded(M.plan.tiles);
  M = F.frame(V(), 1500, 900, '#cbc6bb');
  assert.equal(M.drawn, M.plan.tiles.length);
  const it = F.flat(M);
  assert.equal(it.key, 'mflat');
  assert.equal(it.map.n, M.plan.tiles.length * 6, 'two triangles a tile');
  assert.equal(it.map.atlas.alpha, 1); assert.equal(it.map.atlas.bg, '#cbc6bb');
  // each square's corners where the shaded view puts them, at the lowest level, and its uv at its cell's corners
  const t = M.plan.tiles[0], k = F.corners(t, M.plan.org, M.plan.ground), L = it.map.atlas.layout;
  const i = M.plan.tiles.indexOf(t) * 6;
  near(it.map.pos[i * 3], k.nw[0], 1e-3); near(it.map.pos[i * 3 + 2], k.nw[2], 1e-3); near(it.map.pos[i * 3 + 1], 0);
  near(it.map.uv[i * 2], (t.x - L.x0) / L.cols); near(it.map.uv[i * 2 + 1], (t.y - L.y0) / L.rows);
  E.A3D.site.map.style = 'off';
  assert.equal(F.frame(V(), 1500, 900, '#cbc6bb'), null, 'off: no map');
}));

test('the look of the ground follows the opacity, the Analyze look and the site\'s place', () => withSite(() => {
  let M = F.frame(V(), 1500, 900, '#cbc6bb');
  loaded(M.plan.tiles);
  const a = F.flat(F.frame(V(), 1500, 900, '#cbc6bb')).sig;
  E.A3D.site.map.opacity = 0.5;
  const b = F.flat(F.frame(V(), 1500, 900, '#cbc6bb'));
  assert.notEqual(b.sig, a); assert.equal(b.map.atlas.alpha, 0.5);
  E.A3D.site.map.opacity = 1;
  assert.notEqual(F.flat(F.frame(V(), 1500, 900, '#f4f4f2')).sig, a, 'the plain sky\'s ground under it');
  assert.equal(F.flat(F.frame(V(), 1500, 900, '#cbc6bb')).sig, a, 'nothing changed: the same');
}));

test('the map draped on a terrain: each corner on the canvas from its place, the picture begun again as a tile comes', () => withSite(() => {
  const o = { id: 'T1', t: 'terrain', pos: [0, 0, 0], col: '#808080', survey: [[-40, -40, 1], [40, -40, 2], [40, 40, 3], [-40, 40, 4], [0, 0, 6]] };
  E.A3D.objs = [o];
  let P = F.plan(false, { V: V(), W: 1500, H: 900, bg: '#cbc6bb' });
  const t0 = P.items.find((i) => i.terrain);
  assert.ok(t0, 'the terrain'); assert.equal(t0.drape, undefined, 'no tile in yet: plain');
  const M = F.frame(V(), 1500, 900, '#cbc6bb');
  const D = F.meshData(o, M.plan.org);
  const tiles = F.drapeTiles(D.ext, M.plan.z, 19);
  loaded(tiles.slice(0, 1));
  P = F.plan(false, { V: V(), W: 1500, H: 900, bg: '#cbc6bb' });
  const t1 = P.items.find((i) => i.terrain);
  assert.ok(t1.drape, 'one tile in: draped');
  loaded(tiles.slice(1));
  P = F.plan(false, { V: V(), W: 1500, H: 900, bg: '#cbc6bb' });
  const t2 = P.items.find((i) => i.terrain);
  assert.notEqual(t2.sig, t1.sig, 'more tiles: the picture begun again');
  assert.equal(t2.drape.atlas.bg, '#808080', 'the opacity mixes toward the terrain\'s own colour');
  // the arrays: as many corners on the canvas as in the surface, in its order, each inside the canvas
  const A = F.build(P, t2);
  assert.equal(A.map.flat, false);
  assert.equal(A.map.uv.length / 2, A.map.n); assert.equal(A.map.pos.length / 3, A.map.n);
  for (let i = 0; i < A.map.uv.length; i++) assert.ok(A.map.uv[i] >= 0 && A.map.uv[i] <= 1, 'inside the canvas');
  // a corner's place: from its longitude and latitude, the tile it lies in
  const L = t2.drape.atlas.layout, g = E.bimModelToGeo(A.map.pos[0], A.map.pos[2], M.plan.org);
  near(A.map.uv[0] * L.cols + L.x0, E.bimLonToTileX(g[0], L.z), 1e-4);
  near(A.map.uv[1] * L.rows + L.y0, E.bimLatToTileY(g[1], L.z), 1e-4);
  E.A3D.site.map.style = 'off';
  P = F.plan(false, { V: V(), W: 1500, H: 900, bg: '#cbc6bb' });
  assert.equal(P.items.find((i) => i.terrain).drape, undefined, 'the map off: plain again');
  assert.equal(P.items.find((i) => i.key === 'mflat'), undefined);
}));

test('the frame draws the map against a stand-in for three.js, and gives its pictures back', () => withSite(() => {
  const R = E.A3D_RV;
  try {
    R.T = document.standInForThree; R.st = 'ready'; R.on = true; R.sig = '';
    E.bimRvRender(V(), 1500, 900);
    loaded(E.A3D.lastMapDrawn.tiles);
    const sig = R.sig;
    assert.equal(E.bimRvRender(V(), 1500, 900), true);
    assert.notEqual(R.sig, sig, 'the tiles came: the picture begun again');
    assert.match(R.sig, /mflat=/);
    assert.equal(E.A3D.lastMapDrawn.drawn, E.A3D.lastMapDrawn.tiles.length);
  } finally { R.on = false; E.bimRvDrop(); R.T = null; R.st = 'idle'; R.load = null; }
  assert.equal(R.core, null);
}));
