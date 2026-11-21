/* Interiors I2 (V180, docs/work-orders/v180/SPEC.md): the pure functions of src/js/engine/bim/interiors-clearance.js
   (WO-01 to WO-06, read as text), then the body, the turning circle and the rules of
   src/js/engine/bim/interiors-clearance-model.js (WO-07, through the engine). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const NAMES = ["bimClrRect", "bimClrZone", "bimClrOverlap", "bimClrConflicts", "bimClrCircleFits", "bimClrRule"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/interiors-clearance.js'), 'utf8');
  if (process.env.V180_REF) src += fs.readFileSync(process.env.V180_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/interiors-clearance.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const SQ = (x, z, s) => [[x, z], [x + s, z], [x + s, z + s], [x, z + s]];
test('WO-01 a rectangle turned about its centre, counter-clockwise corners', () => {
  const r = fn('bimClrRect')([1, 2], 2, 1, 0);
  assert.deepEqual(r, [[0, 1.5], [2, 1.5], [2, 2.5], [0, 2.5]]);
  const q = fn('bimClrRect')([0, 0], 2, 1, Math.PI / 2);
  near(q[0][0], 0.5, 1e-12); near(q[0][1], -1, 1e-12); near(q[2][0], -0.5, 1e-12); near(q[2][1], 1, 1e-12);
});
test('WO-02 the clearance zone in front of an item (its local +z side), widened by side', () => {
  const z = fn('bimClrZone')({ center: [0, 0], w: 1, d: 0.6, rot: 0 }, 0.9, 0.1);
  assert.deepEqual(z.map((p) => p.map((v) => Math.round(v * 1e9) / 1e9)), [[-0.6, 0.3], [0.6, 0.3], [0.6, 1.2], [-0.6, 1.2]]);
  assert.equal(fn('bimClrZone')({ center: [0, 0], w: 1, d: 0.6 }, 0, 0), null);
});
test('WO-03 convex overlap by separating axes; touching is not overlapping', () => {
  const f = fn('bimClrOverlap');
  assert.equal(f(SQ(0, 0, 1), SQ(0.5, 0.5, 1)), true);
  assert.equal(f(SQ(0, 0, 1), SQ(1, 0, 1)), false);
  assert.equal(f(SQ(0, 0, 1), SQ(2, 2, 1)), false);
  assert.equal(f(SQ(0, 0, 1), [[1.2, 0.5], [2, -1], [2, 2]]), false);
  assert.equal(f(SQ(0, 0, 1), null), false);
});
test('WO-04 a zone blocked by another item\'s body or an obstacle; zones may overlap each other', () => {
  const items = [
    { id: 'bed', body: SQ(0, 0, 2), zone: SQ(0, 2, 1) },
    { id: 'desk', body: SQ(0.5, 2.5, 0.4), zone: SQ(0.4, 2.2, 0.3) },
    { id: 'chair', body: SQ(5, 5, 0.5), zone: null }
  ];
  assert.deepEqual(fn('bimClrConflicts')(items, [{ id: 'wall', poly: [[0.8, 2.8], [3, 2.8], [3, 3.5], [0.8, 3.5]] }]),
    [{ item: 'bed', with: 'desk' }, { item: 'bed', with: 'wall' }]);
  assert.deepEqual(fn('bimClrConflicts')(null, []), []);
});
test('WO-05 a turning circle fits a room only inside and clear of every edge', () => {
  const room = SQ(0, 0, 2);
  assert.equal(fn('bimClrCircleFits')(room, [1, 1], 0.762), true);
  assert.equal(fn('bimClrCircleFits')(room, [0.5, 1], 0.762), false);
  assert.equal(fn('bimClrCircleFits')(room, [1, 1], 1), true, 'exactly touching');
  assert.equal(fn('bimClrCircleFits')(room, [5, 1], 0.1), false);
  assert.equal(fn('bimClrCircleFits')([[0, 0], [4, 0], [4, 4], [2, 1], [0, 4]], [2, 2], 0.3), false, 'outside a concave notch');
});
test('WO-06 a measurement against a registry rule, with its clause and edition', () => {
  const rule = { minIn: 32, clause: '404.2.3', edition: '2010 ADA Standards' };
  assert.deepEqual(fn('bimClrRule')(rule, 0.8128), { clause: '404.2.3', edition: '2010 ADA Standards', status: 'meets', measuredIn: 32 });
  assert.equal(fn('bimClrRule')(rule, 31.9 * 0.0254).status, 'below');
  assert.deepEqual(fn('bimClrRule')(rule, null), { clause: '404.2.3', edition: '2010 ADA Standards', status: 'not evaluated' });
  assert.deepEqual(fn('bimClrRule')(null, 1), { clause: '', edition: '', status: 'not evaluated' });
});

// ---- WO-07: bim/interiors-clearance-model.js, through the engine ----
import { loadEngine } from './helpers/engine.mjs';
const E = loadEngine();

test('WO-07 the clearance file is ES5, as the build contract asks', () => {
  for (const f of ['interiors-clearance.js', 'interiors-clearance-model.js']) {
    const t = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim', f), 'utf8').replace(/^(import|export)[^;]*;$/gm, '');
    assert.ok(!/\b(const|let)\s|=>|`|\.\.\.[a-zA-Z\[]/.test(t), f + ' uses ES2015 syntax');
  }
});

test('WO-07 a body is the box of its points in the frame it faces', () => {
  const pts = [[1, 1], [3, 1], [3, 2], [1, 2]];
  const B = E.bimClrBodyOf(pts, 0);
  near(B.center[0], 2); near(B.center[1], 1.5); near(B.w, 2); near(B.d, 1);
  const T = E.bimClrBodyOf(pts, Math.PI / 2);
  near(T.w, 1); near(T.d, 2); near(T.center[0], 2); near(T.center[1], 1.5);
  assert.equal(E.bimClrBodyOf([], 0), null);
});

test('WO-07 the widest turning circle: a room, then a body in it', () => {
  const room = SQ(0, 0, 2);
  const f = E.bimClrTurnFit(room, [], 0.05, 3);
  near(f.d, 2, 0.01, 'a 2 m room holds a circle 2 m across');
  const g = E.bimClrTurnFit(room, [SQ(0, 0, 1)], 0.05, 3);
  assert.ok(g.d < 2 - 0.1 && g.d > 0.8, 'a body in a corner takes room: ' + g.d);
  assert.deepEqual(E.bimClrTurnFit([[0, 0], [1, 0]], [], 0.05, 3), { d: 0, at: null });
  const R = E.bimClrRule({ clause: '304.3.1', edition: 'x', minIn: 60 }, f.d);
  assert.equal(R.status, 'meets', '2 m is 78.74 in, over 60 in');
  const small = E.bimClrTurnFit(SQ(0, 0, 1.2), [], 0.05, 3);
  assert.equal(E.bimClrRule({ clause: '304.3.1', edition: 'x', minIn: 60 }, small.d).status, 'below', 'a 1.2 m room is under 60 in');
});
