// V266: more of FreeCAD's PartDesign on OpenCASCADE (engine/solids/occt-features.js, occt-adapter.js), run against
// the pinned runtime (runtime/occt/1.2.1/) in Node.
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-6) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);
const DIR = fileURLToPath(new URL('../../runtime/occt/1.2.1/', import.meta.url));
let R;
before(async () => {
  const Module = (await import(pathToFileURL(DIR + 'replicad_single.js').href)).default;
  const oc = await Module({ locateFile: () => DIR + 'replicad_single.wasm' });
  const ctx = { console, TextDecoder, TextEncoder, Blob, performance, setTimeout, clearTimeout };
  ctx.globalThis = ctx; vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(DIR + 'bim-replicad.min.js', 'utf8') + ';globalThis.R=BIMREPLICAD;', ctx);
  R = ctx.R; R.setOC(oc);
});
const volume = (s) => R.measureVolume(s);
// a box from plan (0,0) to (w,-d) (d north), h high, as EXTRUDE makes it
const box = (w, d, h, x0 = 0, z0 = 0) => E.bimOcctDrawing(R, [[x0, z0], [x0 + w, z0], [x0 + w, z0 - d], [x0, z0 - d]], null).sketchOnPlane('XY').extrude(h);
const solidObj = (shape) => { const mesh = E.bimOcctMesh(shape); return { name: 'S', mesh, occt: { brep: shape.serialize(), sig: E.bimOcctSig(mesh) } }; };

test('the affine map between two point sets: a turn, a mirror and a scale fit; a stretch is not a similarity', () => {
  const P = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 2, 3]];
  const c = Math.cos(0.3), s = Math.sin(0.3);
  const f = (p) => [-(c * p[0] - s * p[2]) * 2 + 5, p[1] * 2 - 1, (s * p[0] + c * p[2]) * 2];
  const fit = E.bimOcctFitAffine(P, P.map(f));
  assert.ok(fit.ok && fit.similar, 'a mirrored, turned, doubled copy is a similarity');
  near(fit.s, 2); assert.ok(fit.det < 0, 'a mirror turns the determinant negative');
  const st = E.bimOcctFitAffine(P, P.map((p) => [p[0] * 2, p[1], p[2]]));
  assert.ok(st.ok && !st.similar, 'stretching one way is affine but not similar');
  // in OpenCASCADE's frame the same map moves (x, -z, y) points the same way
  const F = E.bimOcctAffineToOcc(fit.A, fit.t), q = [1, 2, 3], app = f(q), toOcc = (p) => [p[0], -p[2], p[1]], Q = toOcc(q);
  const got = [0, 1, 2].map((i) => F.A[i][0] * Q[0] + F.A[i][1] * Q[1] + F.A[i][2] * Q[2] + F.t[i]);
  toOcc(app).forEach((v, i) => near(got[i], v, 1e-9));
});

test('a solid a mesh tool turned and scaled is still a solid: its B-rep follows the mesh', () => {
  const o = solidObj(box(2, 1, 3));
  // the mesh turned a quarter about the vertical and doubled, as ROTATE and SCALE leave it
  o.mesh = { v: o.mesh.v.map((v) => [-v[2] * 2 + 1, v[1] * 2, v[0] * 2]), f: o.mesh.f };
  assert.equal(E.bimOcctIsSolid(o), true);
  const s = E.bimOcctShapeOf(R, o);
  near(volume(s), 6 * 8, 1e-6);
  const xs = o.mesh.v.map((v) => v[0]), ys = o.mesh.v.map((v) => v[1]), zs = o.mesh.v.map((v) => v[2]);
  const b = s.boundingBox.bounds;   // OpenCASCADE (X, Y, Z) = app (x, -z, y)
  near(b[0][0], Math.min(...xs)); near(b[1][0], Math.max(...xs));
  near(b[0][1], -Math.max(...zs)); near(b[1][1], -Math.min(...zs));
  near(b[0][2], Math.min(...ys)); near(b[1][2], Math.max(...ys));
  assert.equal(o.occt.sig, E.bimOcctSig(o.mesh), 'the B-rep is stored again, matching the mesh');
  // stretched one way, it is no longer a solid
  const t = solidObj(box(1, 1, 1));
  t.mesh = { v: t.mesh.v.map((v) => [v[0] * 3, v[1], v[2]]), f: t.mesh.f };
  assert.throws(() => E.bimOcctShapeOf(R, t), /stretched/);
  assert.equal(E.bimOcctIsSolid(t), false);
});

test('the edge nearest a click on the screen', () => {
  const edges = [[[0, 0], [100, 0]], [[0, 50], [100, 50]], [[200, 0], [200, 100]]];
  assert.equal(E.bimOcctNearestEdge(edges, [50, 4], 14), 0);
  assert.equal(E.bimOcctNearestEdge(edges, [50, 40], 14), 1);
  assert.equal(E.bimOcctNearestEdge(edges, [195, 60], 14), 2);
  assert.equal(E.bimOcctNearestEdge(edges, [150, 25], 14), -1, 'nothing within reach');
});

test('one edge filleted, picked by its midpoint, and the edges as the app draws them', () => {
  const b = box(2, 1, 3);
  const lines = E.bimOcctEdgeLines(b, [0, 0, 0]);
  assert.equal(lines.length, 12);
  // the vertical edge at plan (0, 0): app points x = 0, z = 0, y from 0 to 3
  const k = lines.findIndex((l) => l.pts.every((p) => Math.abs(p[0]) < 1e-9 && Math.abs(p[2]) < 1e-9));
  assert.ok(k >= 0, 'the edge at the origin is drawn upright');
  near(Math.max(...lines[k].pts.map((p) => p[1])), 3);
  const mid = lines[k].mid;
  const f = b.fillet((e) => (E.bimOcctSameMid(e.pointAt(0.5).toTuple(), mid) ? 0.2 : null));
  near(volume(f), 6 - 0.04 * (1 - Math.PI / 4) * 3, 1e-6);
});

test('a draft angle tilts the sides about the bottom', () => {
  const b = box(2, 1, 3), bb = b.boundingBox.bounds;
  const d = b.draft(5, (fc) => fc.atAngleWith('Z', 90), R.makePlane('XY', [0, 0, bb[0][2]]));
  const k = 2 * 3 * Math.tan(5 * Math.PI / 180), A0 = 2, A1 = (2 - k) * (1 - k), Am = (2 - k / 2) * (1 - k / 2);
  near(volume(d), 3 / 6 * (A0 + 4 * Am + A1), 1e-6);   // a prismatoid
});

test('a sweep along a straight path is the section times its length; a bend keeps it close', () => {
  const sec = E.bimOcctCentred([[10, 10], [10.4, 10], [10.4, 9.8], [10, 9.8]]);
  near(Math.min(...sec.map((p) => p[0])), -0.2); near(Math.max(...sec.map((p) => p[1])), 0.1);
  const path = (pts) => E.bimOcctPathDrawing(R, { pts, y: 0 });
  const sw = path([[0, 0], [5, 0]]).sweepSketch((plane, origin) => E.bimOcctDrawing(R, sec, null).sketchOnPlane(plane, origin));
  near(volume(sw), 0.4 * 0.2 * 5, 1e-6);
  const bent = path([[0, 0], [5, 0], [5, -4]]).sweepSketch((plane, origin) => E.bimOcctDrawing(R, sec, null).sketchOnPlane(plane, origin), { transitionMode: 'round' });
  assert.ok(Math.abs(volume(bent) - 0.08 * 9) < 0.08 * 9 * 0.05, 'within 5 % of the section times the path');
});

test('pattern placements: linear, polar shared round a full turn, mirrored', () => {
  assert.deepEqual(E.bimOcctPatternSteps({ type: 'linear', count: 3, dx: 2, dz: 0, dy: 1 }).map((s) => s.move), [[2, 1, 0], [4, 2, 0]]);
  assert.deepEqual(E.bimOcctPatternSteps({ type: 'polar', count: 4, angle: 360, cx: 1, cz: 2 }).map((s) => s.turn), [90, 180, 270]);
  assert.deepEqual(E.bimOcctPatternSteps({ type: 'polar', count: 3, angle: 90 }).map((s) => s.turn), [45, 90]);
  assert.deepEqual(E.bimOcctPatternSteps({ type: 'mirror', axis: 'z', at: 3 }), [{ mirror: 'z', at: 3 }]);
});

test('pattern copies land where the plan says, and join', () => {
  const b = box(1, 1, 1);   // plan x 0..1, z -1..0
  const moved = E.bimOcctPlace(b, { move: [3, 0, 2] }).boundingBox.bounds;
  near(moved[0][0], 3); near(moved[1][1], -2 + 1);   // z -1..0 moved south by 2 is 1..2: Y = -z is -2..-1
  // a quarter turn counter-clockwise on the plan about (0, 0): east (x 0..1) goes north (z -1..0 to x -1..0, z ... )
  const t = E.bimOcctPlace(b, { turn: 90, about: [0, 0] }).boundingBox.bounds;
  near(t[0][0], -1); near(t[1][0], 0); near(t[0][1], 0); near(t[1][1], 1);   // Y 0..1 is z -1..0
  const m = E.bimOcctPlace(b, { mirror: 'z', at: 0 }).boundingBox.bounds;
  near(m[0][1], -1); near(m[1][1], 0);   // z -1..0 mirrored in z = 0 is 0..1: Y -1..0
  let shape = b;
  for (const st of E.bimOcctPatternSteps({ type: 'linear', count: 3, dx: 2, dz: 0, dy: 0 })) shape = shape.fuse(E.bimOcctPlace(b, st));
  near(volume(shape), 3, 1e-6);
});

test('thickness opens the top, the bottom or both', () => {
  const b = () => box(2, 2, 2);
  near(volume(b().shell(0.1, (fc) => fc.inPlane('XY', 0))), 8 - 1.8 * 1.8 * 1.9, 1e-6);
  near(volume(b().shell(0.1, (fc) => fc.either([(f) => f.inPlane('XY', 0), (f) => f.inPlane('XY', 2)]))), 8 - 1.8 * 1.8 * 2, 1e-6);
});
