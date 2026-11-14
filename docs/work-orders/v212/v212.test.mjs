/* V212's work-order tests (docs/work-orders/v212/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/survey/traverse-control.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v212/v212.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v212/v212.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimSvDms", "bimSvLatDep", "bimSvClosure", "bimSvCompass", "bimSvAngular"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/survey/traverse-control.js'), 'utf8');
  if (process.env.V212_REF) src += fs.readFileSync(process.env.V212_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/survey/traverse-control.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// the research's fixture (docs/research/experiments/notion-later-20261113/results.json): a closed square that misses by 0.02 m
const LEGS = [[0, 100], [90, 80], [180, 100], [270, 79.98]];
test('WO-01 degrees-minutes-seconds and decimal degrees', () => {
  const f = fn('bimSvDms');
  near(f('123-45-30'), 123 + 45 / 60 + 30 / 3600, 1e-12);
  near(f('10 30'), 10.5, 1e-12);
  near(f('-0-30-0'), -0.5, 1e-12);
  assert.equal(f(12.5), 12.5);
  assert.equal(f('12-60-00'), null); assert.equal(f('north'), null);
});
test('WO-02 latitudes, departures, their sums and the perimeter (azimuth from north, clockwise)', () => {
  const r = fn('bimSvLatDep')(LEGS);
  near(r.sumE, 0.02, 1e-9); near(r.sumN, 0, 1e-9); near(r.perimeter, 359.98, 1e-9);
  near(r.lat[0], 100, 1e-12); near(r.dep[1], 80, 1e-12);
});
test('WO-03 closure: computed for a loop or a link, never for an open traverse', () => {
  const c = fn('bimSvClosure')(LEGS, 'closed');
  assert.equal(c.status, 'computed'); near(c.misclosure, 0.02, 1e-9); near(c.ratio, 17999, 1e-3);
  assert.deepEqual(fn('bimSvClosure')(LEGS, 'open'), { status: 'not assessable', why: 'an open traverse has no independent closure' });
  const l = fn('bimSvClosure')([[90, 100]], 'link', [1000, 2000], [1100.03, 2000]);
  near(l.misclosure, 0.03, 1e-9);
  assert.equal(fn('bimSvClosure')([[90, 100]], 'link', [0, 0]).status, 'not assessable');
});
test('WO-04 the compass (Bowditch) rule: corrections by leg length, the loop closes', () => {
  const p = fn('bimSvCompass')(LEGS, [1000, 5000]);
  assert.equal(p.length, 5);
  near(p[4][0], 1000, 1e-9); near(p[4][1], 5000, 1e-9);
  near(p[1][0], 1000 - 0.02 * 100 / 359.98, 1e-9); near(p[1][1], 5100, 1e-9);
});
test('WO-05 angular misclosure: the interior angles against (n - 2) 180', () => {
  near(fn('bimSvAngular')([90, 90, 90, 90.0125]), 0.0125, 1e-9);
  assert.equal(fn('bimSvAngular')([90, 90]), null);
});
