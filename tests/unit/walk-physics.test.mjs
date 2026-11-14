/* V203 C-04: the Jolt adapter (src/js/engine/walk/walk-physics.js), driven with the committed runtime
   (runtime/jolt/1.1.1/bim-jolt.min.js) on experiment e01's course (docs/research/experiments/w1-walk/).
   The bundle runs in its own context without `process`, so Jolt's loader takes the path a browser page takes
   (in Node's own context it takes its Node path, which needs a module URL a classic script does not have).
   walk-physics.js uses no other engine name, so it is loaded by itself, as walk-math.js is in the work-order tests. */
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const NAMES = ['bimWalkPhys', 'bimWalkPhysMesh', 'bimWalkPhysDrop', 'bimWalkPhysBuild', 'bimWalkPhysSync', 'bimWalkPhysChar',
  'bimWalkPhysCharFree', 'bimWalkPhysStep', 'bimWalkPhysRay', 'bimWalkPhysFree'];
let J = null, P = null;

before(async () => {
  const ctx = vm.createContext({ WebAssembly, console, setTimeout, clearTimeout, TextDecoder, TextEncoder, Uint8Array, atob, performance });
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'runtime/jolt/1.1.1/bim-jolt.min.js'), 'utf8') + '\n;this.BIMJOLT=BIMJOLT;', ctx);
  J = await ctx.BIMJOLT.default();
  let t = fs.readFileSync(path.join(ROOT, 'src/js/engine/walk/walk-physics.js'), 'utf8');
  t = t.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  P = new Function(t + '\nreturn {' + NAMES.map((n) => n + ':' + n).join(',') + '};')();
});

/* triangles, nine numbers each */
function box(out, x0, y0, z0, x1, y1, z1) {
  const v = [[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]];
  for (const f of [[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[3,7,6],[3,6,2],[0,4,7],[0,7,3],[1,2,6],[1,6,5]])
    for (const k of f) out.push(...v[k]);
}
function quad(out, a, b, c, d) { out.push(...a, ...b, ...c, ...a, ...c, ...d); }
const ground = () => { const t = []; quad(t, [-5, 0, -3], [-5, 0, 3], [30, 0, 3], [30, 0, -3]); return new Float32Array(t); };
function obstacle(kind) {
  const t = [];
  if (kind === 'step') box(t, 3, 0, -3, 30, 0.18, 3);
  if (kind === 'curb') box(t, 3, 0, -3, 30, 0.40, 3);
  if (kind === 'wall') box(t, 3, 0, -3, 3.2, 3, 3);
  if (kind === 'ramp' || kind === 'slope') {
    const g = kind === 'ramp' ? 1 / 12 : Math.tan(40 * Math.PI / 180);
    quad(t, [3, 0, -3], [3, 0, 3], [15, 12 * g, 3], [15, 12 * g, -3]);
  }
  return new Float32Array(t);
}
const CAP = { half: 0.645, r: 0.23, step: 0.206, slope: 35 * Math.PI / 180 };
/* a world with the ground and one obstacle; the walker at the origin; `sec` seconds at v; answers the feet */
function walk(kind, v, sec, mode) {
  const W = P.bimWalkPhys(J);
  P.bimWalkPhysMesh(W, 'ground', 1, ground());
  P.bimWalkPhysMesh(W, kind, 1, obstacle(kind));
  P.bimWalkPhysChar(W, CAP, [0, 0.02, 0]);
  let r = null;
  for (let i = 0; i < Math.round(sec * 60); i++) r = P.bimWalkPhysStep(W, v, 1 / 60, mode || 'walk', false);
  P.bimWalkPhysFree(W);
  return r;
}

test('C-04 bimWalkPhysStep: climbs a 0.18 m step (a code riser)', () => {
  const r = walk('step', [1.4, 0, 0], 5);
  assert.ok(r.p[0] > 6 && Math.abs(r.p[1] - 0.18) < 0.05, JSON.stringify(r));
  assert.equal(r.ground, true);
});
test('C-04 bimWalkPhysStep: stopped by a 0.40 m curb, and by a wall at 10 m/s', () => {
  const c = walk('curb', [1.4, 0, 0], 5), w = walk('wall', [10, 0, 0], 5);
  assert.ok(c.p[0] < 3, 'curb ' + JSON.stringify(c));
  assert.ok(w.p[0] < 3, 'wall ' + JSON.stringify(w));
});
test('C-04 bimWalkPhysStep: climbs a 1:12 ramp, refuses a 40 degree slope', () => {
  const r = walk('ramp', [1.4, 0, 0], 5);
  assert.ok(r.p[0] > 6 && r.p[1] > 0.2, JSON.stringify(r));
  assert.ok(walk('slope', [1.4, 0, 0], 5).p[1] < 1);
});
test('C-04 bimWalkPhysStep: a wheelchair user (step 0) is stopped by the 0.18 m step', () => {
  const W = P.bimWalkPhys(J);
  P.bimWalkPhysMesh(W, 'ground', 1, ground()); P.bimWalkPhysMesh(W, 'step', 1, obstacle('step'));
  P.bimWalkPhysChar(W, { half: 0.4, r: 0.25, step: 0, slope: Math.atan(1 / 12) }, [0, 0.02, 0]);
  let r; for (let i = 0; i < 300; i++) r = P.bimWalkPhysStep(W, [1.4, 0, 0], 1 / 60, 'walk', false);
  P.bimWalkPhysFree(W);
  assert.ok(r.p[0] < 3, JSON.stringify(r));
});
test('C-04 bimWalkPhysStep: ghost passes through the wall; fly rises with no gravity', () => {
  assert.ok(walk('wall', [1.4, 0, 0], 5, 'ghost').p[0] > 6);
  const f = walk('wall', [0, 1, 0], 2, 'fly');
  assert.ok(Math.abs(f.p[1] - 2.02) < 0.05, JSON.stringify(f));
});
test('C-04 bimWalkPhysStep: falls under gravity, and a jump leaves the floor', () => {
  const W = P.bimWalkPhys(J);
  P.bimWalkPhysMesh(W, 'ground', 1, ground());
  P.bimWalkPhysChar(W, CAP, [0, 2, 0]);
  let r; for (let i = 0; i < 120; i++) r = P.bimWalkPhysStep(W, [0, 0, 0], 1 / 60, 'walk', false);
  assert.ok(Math.abs(r.p[1]) < 0.05 && r.ground, JSON.stringify(r));
  let top = 0;
  for (let i = 0; i < 60; i++) { r = P.bimWalkPhysStep(W, [0, 0, 0], 1 / 60, 'walk', i === 0); top = Math.max(top, r.p[1]); }
  assert.ok(top > 0.4 && top < 0.8, String(top));
  P.bimWalkPhysFree(W);
});
test('C-04 bimWalkPhysRay: the distance to the wall, Infinity past it', () => {
  const W = P.bimWalkPhys(J);
  P.bimWalkPhysMesh(W, 'wall', 1, obstacle('wall'));
  assert.ok(Math.abs(P.bimWalkPhysRay(W, [0, 1, 0], [1, 0, 0], 50) - 3) < 1e-3);
  assert.equal(P.bimWalkPhysRay(W, [0, 1, 0], [-1, 0, 0], 50), Infinity);
  assert.equal(P.bimWalkPhysRay(W, [0, 1, 0], [1, 0, 0], 2), Infinity);   // beyond its reach
  P.bimWalkPhysFree(W);
});
test('C-04 bimWalkPhysStep: climbs a stair of seven 0.178 m risers, each its own element', () => {
  const W = P.bimWalkPhys(J);
  P.bimWalkPhysMesh(W, 'ground', 1, ground());
  for (let i = 0; i < 7; i++) { const t = []; box(t, 3 + i * 0.28, 0, -3, 30, 0.178 * (i + 1), 3); P.bimWalkPhysMesh(W, 'tread' + i, 1, new Float32Array(t)); }
  P.bimWalkPhysChar(W, CAP, [0, 0.02, 0]);
  let r; for (let i = 0; i < 360; i++) r = P.bimWalkPhysStep(W, [1.4, 0, 0], 1 / 60, 'walk', false);
  P.bimWalkPhysFree(W);
  assert.ok(r.p[0] > 6 && Math.abs(r.p[1] - 1.246) < 0.02, JSON.stringify(r));
});
test('C-04 bimWalkPhysSync: keeps an unchanged signature, rebuilds on a change, drops what is gone', () => {
  const W = P.bimWalkPhys(J), tris = { a: ground(), b: obstacle('wall'), c: obstacle('curb') };
  let asked = 0;
  const pos = (it) => { asked++; return tris[it.key]; };
  const items = [{ key: 'a', sig: 1 }, { key: 'b', sig: 1 }, { key: 'c', sig: 1 }];
  assert.equal(P.bimWalkPhysSync(W, items, pos), true);
  assert.equal(W.n, 3); assert.equal(asked, 3); assert.equal(W.tris, 2 + 12 + 12);
  const body = W.body;
  assert.equal(P.bimWalkPhysSync(W, items, pos), false);   // nothing changed: no rebuild, no triangles asked for
  assert.equal(asked, 3); assert.equal(W.body, body);
  assert.equal(P.bimWalkPhysSync(W, [{ key: 'a', sig: 2 }], pos), true);
  assert.deepEqual(Object.keys(W.parts), ['a']);
  assert.equal(W.tris, 2);
  assert.ok(Math.abs(P.bimWalkPhysRay(W, [0, 1, 0], [0, -1, 0], 5) - 1) < 1e-3);   // the ground is there
  assert.equal(P.bimWalkPhysRay(W, [0, 1, 0], [1, 0, 0], 50), Infinity);           // the wall is not
  assert.equal(P.bimWalkPhysMesh(W, 'e', 1, new Float32Array(0)), 0);
  assert.equal(W.n, 1);
  P.bimWalkPhysFree(W);
});
