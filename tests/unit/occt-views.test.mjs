// V272: drawing views of solids (engine/solids/occt-views.js) on OpenCASCADE's exact hidden-line removal.
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-6) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);
let R;
before(async () => {
  const DIR = fileURLToPath(new URL('../../runtime/occt/1.2.1/', import.meta.url));
  const Module = (await import(pathToFileURL(DIR + 'replicad_single.js').href)).default;
  const oc = await Module({ locateFile: () => DIR + 'replicad_single.wasm' });
  const ctx = { console, TextDecoder, TextEncoder, Blob, performance, setTimeout, clearTimeout };
  ctx.globalThis = ctx; vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(DIR + 'bim-replicad.min.js', 'utf8') + ';globalThis.R=BIMREPLICAD;', ctx);
  R = ctx.R; R.setOC(oc);
});
// a 2 (east) x 1 (north) x 3 (up) box with a cylinder r 0.3 standing on its top, in OpenCASCADE's frame
const part = () => R.makeBox([0, 0, 0], [2, 1, 3]).fuse(R.makeCylinder(0.3, 1, [1, 0.5, 3], [0, 0, 1]));
const view = (k, hidden = true) => {
  const v = E.BIM_VIEWBASE_VIEWS[k], r = R.makeProjectedEdges(part(), new R.ProjectionCamera([0, 0, 0], E.bimVbUnit(v.dir), E.bimVbUnit(v.x)), hidden);
  return { vis: E.bimVbPolylines(r.visible, 24), hid: E.bimVbPolylines(r.hidden, 24) };
};

test('the top view sees the cylinder\'s circle; the front view sees the part\'s full height', () => {
  const top = view('top');
  const b = E.bimVbBox(top.vis);
  near(b[0], 0); near(b[2], 2); near(b[1], 0); near(b[3], 1);   // north up, east right
  assert.ok(top.vis.some((L) => L.length > 2), 'the circle, sampled');
  const fr = E.bimVbBox(view('front').vis);
  near(fr[2] - fr[0], 2); near(fr[3] - fr[1], 4);
  const rt = E.bimVbBox(view('right').vis);
  near(rt[2] - rt[0], 1); near(rt[3] - rt[1], 4);
});

test('hidden lines: the right view hides edges behind the box', () => {
  assert.ok(view('right').hid.length > 0);
  assert.equal(view('right', false).hid.length, 0);
});

test('third-angle layout: top above front, right beside it, the isometric up and right', () => {
  const L = E.bimVbLayout({ front: [0, 0, 2, 4], top: [0, 0, 2, 1], right: [-1, 0, 0, 4], iso: [-2, -1, 2, 3] }, 1);
  assert.deepEqual(L.front, [0, 0]);
  assert.deepEqual(L.top, [0, 5]);      // above the front's 4, a gap of 1
  assert.deepEqual(L.right, [4, 0]);    // its left edge (-1) at 2 + 1
  assert.deepEqual(L.iso, [7, 6]);      // its left edge (-2) at 5, beyond the right view (width 1, gap 1); above the front
});
