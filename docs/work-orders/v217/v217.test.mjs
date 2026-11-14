/* V217's work-order tests (docs/work-orders/v217/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/history/hub-access.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v217/v217.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v217/v217.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimSrvRole", "bimSrvCan", "bimSrvRedact", "bimSrvAudit"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/history/hub-access.js'), 'utf8');
  if (process.env.V217_REF) src += fs.readFileSync(process.env.V217_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/history/hub-access.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const ACL = [{ user: 'ann', role: 'editor' }, { user: 'bob', role: 'viewer' }, { user: 'bob', role: 'editor', element: 'w1' }, { user: 'ann', element: 'secret', role: 'viewer', deny: true }];
test('WO-01 the role a user has on an element: the project role, raised by an element grant, removed by a denial', () => {
  const r = fn('bimSrvRole');
  assert.equal(r(ACL, 'ann', 'w1'), 'editor');
  assert.equal(r(ACL, 'bob', 'w1'), 'editor');
  assert.equal(r(ACL, 'bob', 'w2'), 'viewer');
  assert.equal(r(ACL, 'ann', 'secret'), null);
  assert.equal(r(ACL, 'eve', 'w1'), null);
});
test('WO-02 whether a role allows an action; unknown actions never', () => {
  const c = fn('bimSrvCan');
  assert.equal(c(ACL, 'bob', 'w2', 'read'), true);
  assert.equal(c(ACL, 'bob', 'w2', 'edit'), false);
  assert.equal(c(ACL, 'bob', 'w1', 'edit'), true);
  assert.equal(c(ACL, 'ann', 'w1', 'delete'), false);
  assert.equal(c(ACL, 'ann', 'w1', 'format'), false);
});
test('WO-03 a private check returns only the fields allowed out', () => {
  assert.deepEqual(fn('bimSrvRedact')({ passed: false, clashes: 3, geometry: [1, 2] }, ['passed', 'clashes', 'missing']), { passed: false, clashes: 3 });
});
test('WO-04 an audit entry for every decision', () => {
  assert.deepEqual(fn('bimSrvAudit')('ann', 'edit', 'w1', 1, '2026-11-14T10:00:00Z'), { at: '2026-11-14T10:00:00Z', user: 'ann', action: 'edit', element: 'w1', allowed: true });
});
