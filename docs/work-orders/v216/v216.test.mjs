/* V216's work-order tests (docs/work-orders/v216/SPEC.md, WO-01 to WO-05): the pure functions of src/js/engine/history/hub-files.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v216/v216.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v216/v216.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimHubCanonical", "bimHubHash", "bimHubPath", "bimHubManifest", "bimHubOrphans"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/history/hub-files.js'), 'utf8');
  if (process.env.V216_REF) src += fs.readFileSync(process.env.V216_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/history/hub-files.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 canonical JSON: keys sorted, numbers to 12 significant digits, undefined left out', () => {
  assert.equal(fn('bimHubCanonical')({ b: 1, a: [0.1 + 0.2, 'x', null], c: undefined, d: { z: true, y: NaN } }), '{"a":[0.3,"x",null],"b":1,"d":{"y":null,"z":true}}');
  assert.equal(fn('bimHubCanonical')({ a: 1, b: 2 }), fn('bimHubCanonical')({ b: 2, a: 1 }));
});
test('WO-02 FNV-1a, 32 bits, 8 hex digits', () => {
  assert.equal(fn('bimHubHash')(''), '811c9dc5');
  assert.equal(fn('bimHubHash')('a'), 'e40c292c');
  assert.equal(fn('bimHubHash')('foobar'), 'bf9cf968');
});
test('WO-03 one file per element: elements/<kind>/<id>.json, characters made safe', () => {
  assert.equal(fn('bimHubPath')({ id: 'a3d-1', bim: { type: 'wall' } }), 'elements/wall/a3d-1.json');
  assert.equal(fn('bimHubPath')({ id: 'x/y', t: 'line' }), 'elements/line/x_y.json');
});
test('WO-04 the manifest: schema and each element\'s hash, by id', () => {
  const m = fn('bimHubManifest')([{ id: 'b', v: 1 }, { id: 'a', v: 2 }], 3);
  assert.deepEqual(Object.keys(m.elements), ['a', 'b']);
  assert.equal(m.schema, 3);
  assert.equal(m.elements.a, X.bimHubHash(X.bimHubCanonical({ id: 'a', v: 2 })));
});
test('WO-05 after a merge: references to elements that are gone (the research\'s door on a deleted wall)', () => {
  const els = [{ id: 'd1', t: 'opening', bim: { type: 'door', hostWallId: 'w1' } }, { id: 'f1', bim: { type: 'floor', levelId: 'L0' } }, { id: 'L0', t: 'level' }];
  assert.deepEqual(fn('bimHubOrphans')(els), [{ id: 'd1', field: 'hostWallId', missing: 'w1' }]);
  assert.deepEqual(fn('bimHubOrphans')([]), []);
});
