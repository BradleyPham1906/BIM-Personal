// V271: FreeCAD's Mesh workbench: repair (engine/editing/mesh-repair.js), and a mesh sewn into an OpenCASCADE solid.
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
// a unit cube as an STL leaves it: every triangle with its own three points, some wound the wrong way
function soup() {
  const P = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]];
  const quads = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [3, 0, 4, 7]];   // outward
  const v = [], f = [];
  quads.forEach((q, k) => {
    for (const t of [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]) {
      const tt = k === 2 ? t.slice().reverse() : t;   // one side turned inward
      f.push([v.length, v.length + 1, v.length + 2]);
      tt.forEach((i) => v.push(P[i].map((c) => c + (Math.random() - 0.5) * 1e-8)));
    }
  });
  f.push([0, 0, 1]);   // a collapsed face
  f.push([0, 1, 2]);   // the first face again
  return { v, f };
}
const vol = (m) => m.f.reduce((s, [a, b, c]) => { const A = m.v[a], B = m.v[b], C = m.v[c];
  return s + (A[0] * (B[1] * C[2] - B[2] * C[1]) - A[1] * (B[0] * C[2] - B[2] * C[0]) + A[2] * (B[0] * C[1] - B[1] * C[0])) / 6; }, 0);

test('a triangle soup is welded, cleaned and turned outward: a closed cube of volume 1', () => {
  const r = E.bimMeshRepair(soup(), 1e-6);
  assert.equal(r.mesh.v.length, 8);
  assert.equal(r.mesh.f.length, 12);
  assert.equal(r.report.degenerate, 1);
  assert.equal(r.report.duplicates, 1);
  assert.ok(r.report.turned >= 2);
  assert.equal(r.report.closed, true);
  assert.ok(Math.abs(vol(r.mesh) - 1) < 1e-6);
});

test('an open mesh reports its holes; an all-inward mesh is turned outward', () => {
  const s = soup(); s.f = s.f.slice(0, 10);   // the last side (two triangles) missing, and the extras
  const r = E.bimMeshRepair(s, 1e-6);
  assert.equal(r.report.closed, false);
  assert.equal(r.report.openEdges, 4);
  const inward = E.bimMeshRepair(soup(), 1e-6).mesh; inward.f = inward.f.map((t) => t.slice().reverse());
  assert.ok(Math.abs(vol(E.bimMeshRepair(inward, 1e-6).mesh) - 1) < 1e-6);
});

test('a closed mesh sewn into an OpenCASCADE solid keeps its volume', async () => {
  const DIR = fileURLToPath(new URL('../../runtime/occt/1.2.1/', import.meta.url));
  const Module = (await import(pathToFileURL(DIR + 'replicad_single.js').href)).default;
  const oc = await Module({ locateFile: () => DIR + 'replicad_single.wasm' });
  const ctx = { console, TextDecoder, TextEncoder, Blob, performance, setTimeout, clearTimeout };
  ctx.globalThis = ctx; vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(DIR + 'bim-replicad.min.js', 'utf8') + ';globalThis.R=BIMREPLICAD;', ctx);
  const R = ctx.R; R.setOC(oc);
  const m = E.bimMeshRepair(soup(), 1e-6).mesh;
  m.v = m.v.map((p) => [p[0] * 2, p[1] * 3, p[2]]);   // a 2 x 3 x 1 box
  const s = E.bimMeshToSolidShape(R, m);
  assert.ok(Math.abs(R.measureVolume(s) - 6) < 1e-6);
});
