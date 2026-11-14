/* V186's work-order tests (docs/work-orders/v186/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/analysis/surface-analysis.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v186/v186.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v186/v186.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimAnFaceNormal", "bimAnVertexNormals", "bimAnDraft", "bimAnZebra", "bimAnGauss"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/analysis/surface-analysis.js'), 'utf8');
  if (process.env.V186_REF) src += fs.readFileSync(process.env.V186_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/analysis/surface-analysis.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// a unit cube, faces outward (counter-clockwise seen from outside)
const CUBE = { v: [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]],
  f: [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]] };
test('WO-01 a face normal and area by Newell\'s method', () => {
  const r = fn('bimAnFaceNormal')(CUBE.v, CUBE.f[1]);
  assert.deepEqual(r.n, [0, 0, 1]); near(r.area, 1);
  assert.deepEqual(fn('bimAnFaceNormal')(CUBE.v, CUBE.f[0]).n, [0, 0, -1]);
  const t = fn('bimAnFaceNormal')([[0, 0, 0], [2, 0, 0], [0, 2, 0]], [0, 1, 2]); near(t.area, 2);
  assert.deepEqual(fn('bimAnFaceNormal')([[0, 0, 0], [1, 0, 0], [2, 0, 0]], [0, 1, 2]).n, [0, 0, 0]);
});
test('WO-02 vertex normals, area-weighted: a cube corner points along its diagonal', () => {
  const N = fn('bimAnVertexNormals')(CUBE);
  for (const c of N[6]) near(c, 1 / Math.sqrt(3), 1e-12);
  for (const c of N[0]) near(c, -1 / Math.sqrt(3), 1e-12);
});
test('WO-03 draft angle against the pull direction, in degrees', () => {
  near(fn('bimAnDraft')([0, 0, 1], [0, 0, 1]), 90);
  near(fn('bimAnDraft')([1, 0, 0], [0, 0, 5]), 0);
  near(fn('bimAnDraft')([Math.SQRT1_2, 0, -Math.SQRT1_2], [0, 0, 1]), -45, 1e-9);
});
test('WO-04 zebra stripes from the reflected view: alternating 0 and 1', () => {
  assert.equal(fn('bimAnZebra')([0, 0, 1], [0, 0, 1], 10), 1, 'r = (0,0,1): r.y 0 is stripe 5');
  assert.equal(fn('bimAnZebra')([0, 1, 0], [0, 1, 0], 10), 1, 'r.y 1 clamps to the last stripe, 9');
  assert.equal(fn('bimAnZebra')([0, 1, 0], [0, -1, 0], 10), 0, 'r = (0,-1,0): stripe 0');
  assert.equal(fn('bimAnZebra')([0, 0, 1], [0, 0, 1]), 1, 'ten stripes by default');
});
test('WO-05 Gaussian curvature as angle deficits: a cube\'s add up to 4 pi', () => {
  const g = fn('bimAnGauss')(CUBE);
  near(g.deficit.reduce((a, b) => a + b, 0), 4 * Math.PI, 1e-9, 'Gauss-Bonnet');
  near(g.deficit[0], Math.PI / 2, 1e-12);
  near(g.area[0], 0.75, 1e-12, 'a quarter of each of three faces');
  const flat = fn('bimAnGauss')({ v: [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0.5, 0.5, 0]], f: [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]] });
  near(flat.deficit[4], 0, 1e-12, 'an inner vertex of a plane is flat');
});
