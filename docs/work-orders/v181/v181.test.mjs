/* V181's work-order tests (docs/work-orders/v181/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/bim/interiors-routes.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v181/v181.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v181/v181.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimEgGrid", "bimEgCell", "bimEgPath", "bimEgNearest", "bimEgStatus"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/interiors-routes.js'), 'utf8');
  if (process.env.V181_REF) src += fs.readFileSync(process.env.V181_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/interiors-routes.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const ROOM = [[0, 0], [10, 0], [10, 4], [0, 4]];
const WALL = [[4, 0], [5, 0], [5, 3], [4, 3]];
test('WO-01 a walkable grid: cell centres inside the room and outside every obstacle', () => {
  const g = fn('bimEgGrid')(ROOM, [WALL], 1);
  assert.deepEqual([g.x0, g.z0, g.cell, g.nx, g.nz], [0, 0, 1, 10, 4]);
  assert.deepEqual(Array.from(g.free.slice(0, 10)), [1, 1, 1, 1, 0, 1, 1, 1, 1, 1]);
  assert.equal(g.free[3 * 10 + 4], 1, 'above the wall end');
  assert.equal(fn('bimEgGrid')(ROOM, [], 0), null);
  assert.equal(fn('bimEgGrid')([[0, 0], [1, 1]], [], 1), null);
});
test('WO-02 the free cell under a point, or -1', () => {
  const g = X.bimEgGrid(ROOM, [WALL], 1);
  assert.equal(fn('bimEgCell')(g, [0.5, 0.5]), 0);
  assert.equal(fn('bimEgCell')(g, [4.5, 0.5]), -1, 'in the wall');
  assert.equal(fn('bimEgCell')(g, [12, 1]), -1, 'outside');
});
test('WO-03 the shortest 8-way route around an obstacle, no corner cutting', () => {
  const g = X.bimEgGrid(ROOM, [WALL], 1);
  const r = fn('bimEgPath')(g, [0.5, 0.5], [9.5, 0.5]);
  near(r.len, 3 + 6 * Math.SQRT2, 1e-9, 'three diagonals up, two along row 3, three down, one along: 3 + 6 sqrt 2');
  assert.equal(r.cells[0], 0); assert.equal(r.cells[r.cells.length - 1], 9);
  const shut = X.bimEgGrid(ROOM, [[[4, 0], [5, 0], [5, 4], [4, 4]]], 1);
  assert.equal(fn('bimEgPath')(shut, [0.5, 0.5], [9.5, 0.5]), null);
  assert.equal(fn('bimEgPath')(g, [4.5, 0.5], [9.5, 0.5]), null);
});
test('WO-04 the nearest exit by route; unreachable exits ignored; ties by name', () => {
  assert.deepEqual(fn('bimEgNearest')({ east: { len: 9 }, west: { len: 4 }, north: null }), { exit: 'west', len: 4 });
  assert.deepEqual(fn('bimEgNearest')({ b: { len: 4 }, a: { len: 4 } }), { exit: 'a', len: 4 });
  assert.equal(fn('bimEgNearest')({ a: null }), null);
});
test('WO-05 a route against a travel limit the owner chose; blocked and unknown kept apart', () => {
  const s = fn('bimEgStatus');
  assert.deepEqual(s({ exit: 'a', len: 12.34 }, 30), { status: 'within', why: '12.3 m of 30 m' });
  assert.deepEqual(s({ exit: 'a', len: 45 }, 30), { status: 'over', why: '45.0 m, over 30 m' });
  assert.deepEqual(s(null, 30), { status: 'blocked', why: 'no route to an exit' });
  assert.deepEqual(s({ exit: 'a', len: 5 }, null), { status: 'not evaluated', why: 'no travel limit chosen' });
});
