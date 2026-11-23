// V264: the solid tools on OpenCASCADE (engine/solids/occt-adapter.js), run against the pinned runtime
// (runtime/occt/1.2.1/: replicad and its OpenCASCADE build) in Node.
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

test('a plan outline becomes an OpenCASCADE face: lines and an arc, the area as the app measures it', () => {
  // a 4 x 2 rectangle whose east side bulges out by 0.5 (the app's sign: right of travel)
  const pts = [[0, 0], [4, 0], [4, -2], [0, -2]], bulges = [0, -0.5, 0, 0];
  const s = E.bimOcctDrawing(R, pts, bulges).sketchOnPlane('XY').extrude(3);
  near(volume(s), E.bimBulgedArea(pts, bulges, true) * 3, 1e-6);
  assert.ok(E.bimBulgedArea(pts, bulges, true) > 8, 'the arc adds area: it bulges out, as drawn');
});

test('a circle (two arcs, the last closing it) and an arc on the closing side', () => {
  const c = E.bimOcctDrawing(R, [[1, 0], [-1, 0]], [1, 1]).sketchOnPlane('XY').extrude(1);
  near(volume(c), Math.PI, 1e-6);
  const pts = [[0, 0], [2, 0], [2, 2], [0, 2]], b = [0, 0, 0, 0.4];
  near(volume(E.bimOcctDrawing(R, pts, b).sketchOnPlane('XY').extrude(1)), E.bimBulgedArea(pts, b, true), 1e-6);
});

test('the mesh comes back in the app\'s frame: up is y, north is -z, faces outward', () => {
  // a 1 x 1 square from plan (0,0) to (1,-1), i.e. 1 m north, extruded 2 up from 5
  const s = E.bimOcctDrawing(R, [[0, 0], [1, 0], [1, -1], [0, -1]], null).sketchOnPlane('XY', 5).extrude(2);
  const m = E.bimOcctMeshToApp(s.mesh({ tolerance: 0.01, angularTolerance: 10 }));
  const ys = m.v.map((v) => v[1]), zs = m.v.map((v) => v[2]);
  near(Math.min(...ys), 5); near(Math.max(...ys), 7);
  near(Math.min(...zs), -1); near(Math.max(...zs), 0);
  // the signed volume of the mesh is positive: the triangles wind outward
  let vol = 0;
  for (const [a, b, c] of m.f) { const A = m.v[a], B = m.v[b], C = m.v[c];
    vol += (A[0] * (B[1] * C[2] - B[2] * C[1]) - A[1] * (B[0] * C[2] - B[2] * C[0]) + A[2] * (B[0] * C[1] - B[1] * C[0])) / 6; }
  near(vol, 2, 1e-6);
});

test('fillet, chamfer and shell change the solid as they should', () => {
  const box = E.bimOcctDrawing(R, [[0, 0], [2, 0], [2, -2], [0, -2]], null).sketchOnPlane('XY').extrude(2);
  const z = E.bimOcctZRange(box);
  const f = box.fillet(0.2, E.bimOcctEdgeFilter('vertical', z[0], z[1]));
  near(volume(f), 8 - 4 * (0.04 - Math.PI * 0.01) * 2, 1e-6);   // four vertical edges, each loses r^2 (1 - pi/4) times 2 high
  const c = box.chamfer(0.2, E.bimOcctEdgeFilter('top', z[0], z[1]));
  near(volume(c), 8 - 4 * 2 * 0.02 + 4 * (0.2 ** 3) / 3, 1e-6);   // four top edges, prisms of 0.02 by 2, corners corrected
  const sh = box.shell(0.1, (fc) => fc.inPlane('XY', z[1]));
  near(volume(sh), 8 - 1.8 * 1.8 * 1.9, 1e-6);
});

test('revolve, loft, and the mesh signature that guards the B-rep', () => {
  const ring = E.bimOcctDrawing(R, [[1, 0], [2, 0], [2, -1], [1, -1]], null).sketchOnPlane('XY')
    .revolve([0, 1, 0], { origin: [0, 0, 0], angle: 360 });
  near(volume(ring), Math.PI * (4 - 1) * 1, 1e-6);   // a 1 x 1 square from 1 to 2 off the axis: a ring
  const lo = R.drawCircle(1).sketchOnPlane('XY').loftWith([R.drawCircle(2).sketchOnPlane('XY', 3)], { ruled: true });
  near(volume(lo), Math.PI * 3 * (1 + 2 + 4) / 3, 1e-3);   // a frustum
  const mesh = E.bimOcctMeshToApp(ring.mesh());
  const o = { occt: { brep: ring.serialize(), sig: E.bimOcctSig(mesh) }, mesh };
  assert.equal(E.bimOcctIsSolid(o), true);
  near(volume(R.deserializeShape(o.occt.brep)), volume(ring), 1e-9);
  // V266: a mesh moved by a mesh tool still carries its B-rep (the map is found when it is used); a mesh with other
  // sizes (rebuilt) does not
  o.mesh = { v: mesh.v.map((v) => [v[0] + 1, v[1], v[2]]), f: mesh.f };
  assert.equal(E.bimOcctIsSolid(o), true);
  o.mesh = { v: mesh.v.slice(1), f: mesh.f };
  assert.equal(E.bimOcctIsSolid(o), false, 'a rebuilt mesh is no longer the B-rep\'s');
});

test('STEP out and back in keeps the solid', async () => {
  const box = E.bimOcctDrawing(R, [[0, 0], [3, 0], [3, -1], [0, -1]], null).sketchOnPlane('XY').extrude(2);
  const blob = R.exportSTEP([{ shape: box, name: 'box' }], { unit: 'M', modelUnit: 'M' });
  const back = await R.importSTEP(new Blob([await blob.arrayBuffer()]));
  near(volume(back), 6, 1e-6);
});

test('a moved solid\'s offset is the turn of the plan: app (x, y, z) to (x, -z, y)', () => {
  assert.deepEqual(E.bimOcctOffsetXYZ([2, 3, 4]), [2, -4, 3]);
});

test('a clockwise outline is walked counter-clockwise, so booleans on its solid are right', () => {
  // the plan rectangles V264's browser check drew: clockwise once turned north-up
  const box = (x0, z0) => E.bimOcctDrawing(R, [[x0, z0], [x0 + 2, z0], [x0 + 2, z0 + 2], [x0, z0 + 2]], null).sketchOnPlane('XY').extrude(1);
  const A = box(4, 0), B = box(5, 1);
  near(volume(A.fuse(B)), 7, 1e-6);
  near(volume(A.cut(B)), 3, 1e-6);
  // the same outline with an arc keeps its area and its arc either way round
  const pts = [[0, 0], [0, 2], [2, 2], [2, 0]], b = [0, 0, 0.4, 0];
  const O = E.bimOcctOutline(pts, b);
  near(E.bimBulgedSignedArea(O.pts, O.bulges, true), E.bimBulgedArea(pts, b, true), 1e-9);
  near(volume(E.bimOcctDrawing(R, pts, b).sketchOnPlane('XY').extrude(1)), E.bimBulgedArea(pts, b, true), 1e-6);
});
