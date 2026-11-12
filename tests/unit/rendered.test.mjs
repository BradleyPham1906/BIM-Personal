// V194, the rendered view: its sampling (render/rendered-core.js), what it draws as plain numbers
// (render/rendered-scene.js) and how three.js is asked for (render/rendered-view.js). The picture itself needs a
// graphics card: docs/research/experiments/v194-rendered draws it in a browser.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);
const len = (v) => Math.hypot(v[0], v[1], v[2]);
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
// a column-major 4x4 times a point, as clip coordinates
const clip = (m, p) => [0, 1, 2, 3].map((r) => m[r] * p[0] + m[4 + r] * p[1] + m[8 + r] * p[2] + m[12 + r]);
const V = () => E.camVecs({ yaw: 0.7, pitch: 0.5, dist: 40, tx: 3, ty: 1, tz: -2 });

test('the sequence the passes are placed by', () => {
  near(E.bimRvHalton(1, 2), 0.5); near(E.bimRvHalton(2, 2), 0.25); near(E.bimRvHalton(3, 2), 0.75);
  near(E.bimRvHalton(1, 3), 1 / 3); near(E.bimRvHalton(4, 3), 4 / 9);
});

test('the sky is sampled over the hemisphere, cosine-weighted and off the horizon', () => {
  let sum = 0;
  for (let i = 0; i < 256; i++) {
    const d = E.bimRvHemisphere(i, [0, 1, 0]);
    near(len(d), 1, 1e-9);
    assert.ok(d[1] >= Math.sqrt(0.03) - 1e-9, 'pass ' + i + ' is under ten degrees');
    sum += d[1];
  }
  assert.ok(sum / 256 > 0.62 && sum / 256 < 0.72, 'the mean height ' + sum / 256 + ' is not a cosine weighting');
  assert.ok(E.bimRvHemisphere(0, [0, 1, 0])[1] > 0.9, 'the first pass, the one seen while the view moves, is near the zenith');
});

test('the sun is moved inside its cone and no further', () => {
  const s = E.bimRvUnit([0.3, 0.8, -0.5]);
  for (let i = 0; i < 64; i++) {
    const d = E.bimRvSunDisc(s, i, 1.5);
    near(len(d), 1, 1e-9);
    assert.ok(Math.acos(Math.min(1, dot(d, s))) <= 1.5 * Math.PI / 180 + 1e-9);
  }
});

test('the far plane is moved out and the near plane kept, in both projections', () => {
  const P = Array.from(E.bimGlProjMatrix(1500, 900, false, 40));
  const Q = E.bimRvFarPlane(P, 50000);
  // the shaded view's matrices are 32-bit: the near plane read back from one is 0.5 to four places
  near(Q[14] / (Q[10] - 1), 0.5, 1e-3); near(Q[14] / (Q[10] + 1), 50000, 1e-3);
  [0, 5, 11, 15].forEach((k) => assert.equal(Q[k], P[k]));
  assert.deepEqual(E.bimRvFarPlane(P, 10), P, 'a nearer far plane changes nothing');
  const O = Array.from(E.bimGlProjMatrix(1500, 900, true, 40)), R = E.bimRvFarPlane(O, 50000);
  const fn = -2 / R[10], sum = -R[14] * fn;
  near((sum - fn) / 2, 0.5, 1e-3); near((sum + fn) / 2, 50000, 1e-3);
});

test('a pass moves the picture by the part of it asked for, in both projections', () => {
  for (const flat of [false, true]) {
    const P = Array.from(E.bimGlProjMatrix(1500, 900, flat, 40)), J = E.bimRvJitter(P, 0.001, -0.002), p = [3, -2, -25];
    const a = clip(P, p), b = clip(J, p);
    near(b[0] / b[3] - a[0] / a[3], 0.001, 1e-12); near(b[1] / b[3] - a[1] / a[3], -0.002, 1e-12);
    near(b[2], a[2]); near(b[3], a[3]);
  }
});

test('the sky a picture takes', () => {
  assert.equal(E.bimRvSkyFor('clear', true, 40), E.BIM_RV_SKIES.clear);
  assert.equal(E.bimRvSkyFor('clear', true, 5), E.BIM_RV_SKIES.dusk, 'a low sun in a clear sky');
  assert.equal(E.bimRvSkyFor('overcast', true, 5), E.BIM_RV_SKIES.overcast);
  assert.equal(E.bimRvSkyFor('clear', false, -10), E.BIM_RV_NIGHT);
  assert.equal(E.bimRvSkyFor('white', false, -10), E.BIM_RV_SKIES.white, 'the studio has no night');
  assert.equal(E.bimRvSkyFor('nothing', true, null), E.BIM_RV_SKIES.clear);
  assert.ok(E.BIM_RV_NIGHT.sky > 0.5, 'a night with no lamps must still be read');
});

test('colours go to the picture linear', () => {
  near(E.bimRvLin(0), 0); near(E.bimRvLin(1), 1); near(E.bimRvLin(0.5), 0.2140411, 1e-6); near(E.bimRvLin(0.04), 0.04 / 12.92);
});

test('the camera is the view\'s own: its matrix undoes the view matrix, its projection is the shaded view\'s', () => {
  const v = V(), C = E.bimRvCamera(v, 1500, 900, false, 40), M = E.bimGlViewMatrix(v);
  for (const p of [[0, 0, 0], [1, 2, 3], [-4, 0.5, 7]]) {
    const w = clip(C.world, p), back = clip(M, w);
    near(back[0], p[0], 1e-5); near(back[1], p[1], 1e-5); near(back[2], p[2], 1e-5);
  }
  assert.deepEqual(C.world.slice(12, 15), v.eye);
  assert.deepEqual(C.proj, Array.from(E.bimGlProjMatrix(1500, 900, false, 40)));
  assert.deepEqual(E.bimRvCamera(v, 1500, 900, true, 40).proj, Array.from(E.bimGlProjMatrix(1500, 900, true, 40)));
});

// a description of three objects, one triangle each: opaque, see-through, hidden
function fake() {
  const data = new Float32Array(3 * 8);
  data.set([10, 0, 0, 1, 1, 0, 0, 0], 0);       // at x 10, opaque, red
  data.set([0, 5, 0, 0.4, 0, 0, 1, 0], 8);      // at y 5, 40% opaque, blue
  data.set([0, 0, 0, -1, 0, 1, 0, 0], 16);      // hidden
  const tri = [], ed = [];
  for (let s = 0; s < 3; s++) {
    [[0, 0, 0], [1, 0, 0], [0, 1, 0]].forEach((p) => tri.push(p[0], p[1], p[2], 0, 0, 1, s));
    [[0, 0, 0], [1, 0, 0]].forEach((p) => ed.push(p[0], p[1], p[2], s));
  }
  return { B: { data, slots: { a: 0, b: 1, c: 2 } }, c: { ids: ['a', 'b', 'c'], tri: new Float32Array(tri), ed: new Float32Array(ed), count: 9, ecount: 6, ver: 1 } };
}

test('a chunk\'s triangles: where they stand, opaque and see-through apart, the hidden left out', () => {
  const { B, c } = fake(), A = E.bimRvChunkArrays(B, c, false);
  assert.equal(A.op.n, 3); assert.equal(A.tr.n, 3); assert.equal(A.ed, null, 'no edges unless asked');
  assert.deepEqual(Array.from(A.op.pos), [10, 0, 0, 11, 0, 0, 10, 1, 0]);
  assert.deepEqual(Array.from(A.op.col), [1, 0, 0, 1, 0, 0, 1, 0, 0]);
  assert.deepEqual(Array.from(A.tr.pos), [0, 5, 0, 1, 5, 0, 0, 6, 0]);
  near(A.tr.col[2], 1); near(A.tr.col[3], 0.4, 1e-6); assert.equal(A.tr.col.length, 12, 'see-through colours carry their transparency');
  const Ed = E.bimRvChunkArrays(B, c, true).ed;
  assert.equal(Ed.n, 4, 'the hidden object\'s edge is left out');
  assert.deepEqual(Array.from(Ed.pos), [10, 0, 0, 11, 0, 0, 0, 5, 0, 1, 5, 0]);
});

test('a selected object is drawn toward its selection colour', () => {
  const { B, c } = fake();
  B.data[7] = 1;
  const col = E.bimRvChunkArrays(B, c, false).op.col;
  near(col[0], E.bimRvLin(0.55 + 0.45 * 0.306), 1e-6); near(col[1], E.bimRvLin(0.45 * 0.631), 1e-6); near(col[2], E.bimRvLin(0.45), 1e-6);
});

test('a chunk\'s look changes when anything seen of it changes, and only then', () => {
  const { B, c } = fake(), s0 = E.bimRvChunkSig(B, c);
  assert.equal(E.bimRvChunkSig(B, c), s0);
  B.data[0] = 10.5; const moved = E.bimRvChunkSig(B, c); assert.notEqual(moved, s0, 'moved');
  B.data[5] = 0.5; const recoloured = E.bimRvChunkSig(B, c); assert.notEqual(recoloured, moved, 'recoloured');
  B.data[19] = 1; const shown = E.bimRvChunkSig(B, c); assert.notEqual(shown, recoloured, 'shown');
  B.data[7] = 1; const picked = E.bimRvChunkSig(B, c); assert.notEqual(picked, shown, 'selected');
  c.ver = 2; assert.notEqual(E.bimRvChunkSig(B, c), picked, 'its triangles rebuilt');
});

test('the shadows are kept sharp around what the camera looks at, never wider than the model', () => {
  near(E.bimRvReach(100, null), 60);
  near(E.bimRvReach(1, null), 2, 1e-12);
  near(E.bimRvReach(100, [0, 0, 0, 10, 10, 10]), Math.sqrt(300) / 2 * 1.2, 1e-9);
  near(E.bimRvReach(4, [0, 0, 0, 100, 100, 100]), 2.4, 1e-12);
});

test('the model as the shaded view describes it becomes the picture\'s parts', () => {
  const keep = { objs: E.A3D.objs, sel: E.A3D.sel, sel2: E.A3D.sel2, selSet: E.A3D.selSet };
  try {
    E.bimStressModel(4);
    const plan = E.bimRvPlan(false);
    assert.ok(plan.items.length >= 1);
    let n = 0, lo = Infinity, hi = -Infinity;
    for (const it of plan.items) {
      const A = E.bimRvBuild(plan, it);
      n += A.op.n;
      for (let i = 0; i < A.op.pos.length; i += 3) { lo = Math.min(lo, A.op.pos[i]); hi = Math.max(hi, A.op.pos[i]); }
      assert.equal(A.tr.n, 0);
    }
    assert.equal(n, 4 * 12 * 3, 'four boxes, twelve triangles each');
    assert.ok(lo < 0 && hi > 1.5, 'the boxes stand where their objects are: x from ' + lo + ' to ' + hi);
    assert.ok(plan.box && plan.box[3] > plan.box[0]);
    const sig = plan.items.map((i) => i.sig).join('|');
    assert.equal(E.bimRvPlan(false).items.map((i) => i.sig).join('|'), sig, 'nothing changed, nothing to redraw');
    E.A3D.objs[0].pos[0] += 1;
    assert.notEqual(E.bimRvPlan(false).items.map((i) => i.sig).join('|'), sig, 'an object moved');
  } finally { Object.assign(E.A3D, keep); E.bimSceneRelease(); }
});

test('a terrain\'s surface is in the picture, in its colour, and follows its heights', () => {
  const o = { id: 'T1', t: 'terrain', pos: [0, 0, 0], col: '#808080', survey: [[0, 0, 1], [10, 0, 2], [10, 10, 3], [0, 10, 4]] };
  const it = E.bimRvTerrainItem(o);
  assert.ok(it, 'four points make a surface');
  assert.equal(it.key, 'tT1');
  assert.deepEqual(it.box, [0, 1, 0, 10, 4, 10]);
  const A = E.bimRvTerrainArrays(it);
  assert.equal(A.op.n, 6, 'two triangles');
  const ys = [];
  for (let i = 1; i < A.op.pos.length; i += 3) ys.push(A.op.pos[i]);
  assert.deepEqual([...new Set(ys)].sort(), [1, 2, 3, 4], 'each corner at its own height');
  near(A.op.col[0], E.bimRvLin(128 / 255), 1e-6);
  o.survey[2][2] = 7;
  assert.notEqual(E.bimRvTerrainItem(o).sig, it.sig, 'a height changed');
  assert.equal(E.bimRvTerrainItem({ id: 'T2', t: 'terrain', pos: [0, 0, 0], survey: [[0, 0, 1]] }), null, 'one point is no surface');
});

test('the picture is lit by the site\'s sun, and by the shaded view\'s light where the site has no place', () => {
  const site = E.A3D.site;
  try {
    E.A3D.site = { name: 'Site' };
    let s = E.bimRvSun();
    assert.equal(s.site, false); assert.equal(s.up, true); assert.deepEqual(s.dir, Array.from(E.LIGHT));
    E.A3D.site = { name: 'Site', sun: { lat: 40, lon: -75, tz: -5, date: '2026-06-21', time: '12:00' } };
    s = E.bimRvSun();
    assert.equal(s.site, true); assert.equal(s.up, true);
    assert.ok(s.elev > 72 && s.elev < 74, 'noon on the June solstice at 40 N: ' + s.elev);
    near(len(s.dir), 1, 1e-9); near(s.dir[1], Math.sin(s.elev * Math.PI / 180), 1e-9);
    assert.ok(s.dir[2] > 0, 'the noon sun is to the south, the model\'s +z');
    E.A3D.site.sun.time = '23:30';
    s = E.bimRvSun();
    assert.equal(s.up, false); assert.match(s.text, /night/);
  } finally { E.A3D.site = site; }
});

test('three.js is asked for from the page\'s folder, and from a disk copy first beside it, then from Pages', () => {
  const web = E.bimRvSources('https:', 'https://example.org/app/runtime/');
  assert.equal(web.length, 1); assert.equal(web[0].sri, true);
  assert.equal(web[0].u, 'https://example.org/app/runtime/three/' + E.BIM_RV_VER + '/bim-three.min.js');
  const disk = E.bimRvSources('file:', E.BIM_LB_PAGES);
  assert.equal(disk.length, 2);
  assert.deepEqual(disk[0], { u: 'runtime/three/' + E.BIM_RV_VER + '/bim-three.min.js', sri: false });
  assert.equal(disk[1].sri, true); assert.equal(disk[1].u, E.BIM_LB_PAGES + E.BIM_RV_FILE);
});

test('the hash the browser checks three.js against is the committed file\'s and the manifest\'s', () => {
  const man = JSON.parse(fs.readFileSync(path.join(ROOT, 'runtime', 'MANIFEST.json'), 'utf8'));
  assert.equal(man.three, E.BIM_RV_VER);
  const row = man.files.find((f) => f.path === E.BIM_RV_FILE);
  assert.ok(row, 'the manifest pins ' + E.BIM_RV_FILE);
  const bytes = fs.readFileSync(path.join(ROOT, 'runtime', E.BIM_RV_FILE));
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), row.sha256);
  assert.equal('sha256-' + crypto.createHash('sha256').update(bytes).digest('base64'), E.BIM_RV_SRI);
});

test('every three.js name the picture uses is in the pinned file', () => {
  const src = fs.readFileSync(path.join(ROOT, 'src', 'js', 'engine', 'render', 'rendered-core.js'), 'utf8');
  const names = [...new Set([...src.matchAll(/\bT\.([A-Z][A-Za-z0-9]+)/g)].map((m) => m[1]))];
  assert.ok(names.length > 20, 'the names were found: ' + names.length);
  const ctx = { console, performance, setTimeout, clearTimeout };
  ctx.self = ctx; ctx.window = ctx; ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'runtime', E.BIM_RV_FILE), 'utf8'), ctx);
  assert.equal(ctx.BIMTHREE.REVISION, E.BIM_RV_VER.split('.')[1]);
  assert.deepEqual(names.filter((n) => ctx.BIMTHREE[n] === undefined), []);
});

test('the view is off until asked for, and its settings are this browser\'s', () => {
  assert.equal(E.A3D_RV.on, false);
  assert.equal(E.bimRvRender(V(), 1500, 900), false, 'off: the engines draw');
  assert.deepEqual(E.bimRvSettings(), { sky: 'clear', ground: true, edges: false, quality: 'good' });
  assert.equal(E.bimRvSetting('sky', 'overcast'), true);
  assert.equal(E.bimRvSetting('edges', '1'), true);
  assert.equal(E.bimRvSetting('sky', 'purple'), false, 'a sky there is not');
  assert.equal(E.bimRvSetting('quality', 'endless'), false);
  assert.deepEqual(JSON.parse(localStorage.getItem(E.BIM_RV_KEY)), { sky: 'overcast', ground: true, edges: true, quality: 'good' });
  E.bimRvSetting('sky', 'clear'); E.bimRvSetting('edges', '0');
  assert.match(E.bimRvPropsHtml(), /data-propmodel="rendered"/);
  assert.doesNotMatch(E.bimRvPropsHtml(), /data-propmodel="rvsky"/, 'the settings show only while the view is on');
});

test('the frame runs from end to end against a stand-in for three.js, and gives the view back when it is turned off', () => {
  // the stand-in: every name is there, can be made and called, and does nothing (helpers/browser.mjs)
  const R = E.A3D_RV, keep = { objs: E.A3D.objs, sel: E.A3D.sel, sel2: E.A3D.sel2, selSet: E.A3D.selSet, cv: E.el.cv };
  try {
    E.bimStressModel(9);
    E.el.cv = document.createElement('canvas');
    R.T = document.standInForThree; R.st = 'ready'; R.on = true; R.sig = '';
    assert.equal(E.bimRvRender(V(), 1500, 900), true, 'the picture is what is seen');
    assert.equal(R.drew, true); assert.equal(R.done, 1, 'one pass at once'); assert.equal(R.want, 64);
    assert.ok(R.core && R.cv, 'a picture and its canvas');
    assert.match(E.bimRvStateText(), /^1 of 64 passes; lit by /);
    assert.match(E.bimRvPropsHtml(), /data-propmodel="rvsky"[\s\S]*data-propmodel="rvquality"[\s\S]*data-propmodel="rvground"[\s\S]*data-propmodel="rvedges"/);
    const sig = R.sig;
    assert.equal(E.bimRvRender(V(), 1500, 900), true);
    assert.equal(R.sig, sig); assert.equal(R.done, 1, 'nothing changed: no pass was spent');
    E.A3D.objs[0].pos[1] += 2;
    assert.equal(E.bimRvRender(V(), 1500, 900), true);
    assert.notEqual(R.sig, sig, 'an object moved: the picture is begun again');
    E.bimRvSetting('quality', 'draft');
    assert.equal(E.bimRvRender(V(), 1500, 900), true); assert.equal(R.want, 16);
    E.bimRvSetting('quality', 'good');
    R.hold = true;
    assert.equal(E.bimRvRender(V(), 1500, 900), false, 'held, as while the engines are timed');
    R.hold = false;
  } finally {
    R.on = false; E.bimRvDrop();
    R.T = null; R.st = 'idle'; R.load = null;
    Object.assign(E.A3D, { objs: keep.objs, sel: keep.sel, sel2: keep.sel2, selSet: keep.selSet }); E.el.cv = keep.cv; E.bimSceneRelease();
  }
  assert.equal(R.core, null); assert.equal(R.cv, null); assert.equal(R.drew, false);
});
