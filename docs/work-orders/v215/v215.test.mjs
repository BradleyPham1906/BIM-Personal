/* V215's work-order tests (docs/work-orders/v215/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/commands/flows.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v215/v215.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v215/v215.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimFlowOrder", "bimFlowEval", "bimSdkCheck", "bimSdkSnapshot"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/commands/flows.js'), 'utf8');
  if (process.env.V215_REF) src += fs.readFileSync(process.env.V215_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/commands/flows.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// the research's fixture (docs/research/fixtures/flows-dag-fixture.py): A=2, B=3, C=A+B, D=2C
const G = () => ({ A: { op: 'value', value: 2 }, B: { op: 'value', value: 3 }, C: { op: 'sum', in: ['A', 'B'] }, D: { op: 'double', in: ['C'] } });
test('WO-01 evaluation order (Kahn, names sorted); duplicate, missing and cyclic inputs refused', () => {
  assert.deepEqual(fn('bimFlowOrder')(G()), { order: ['A', 'B', 'C', 'D'] });
  const d = G(); d.C.in = ['A', 'A']; assert.deepEqual(fn('bimFlowOrder')(d), { error: 'duplicate input edge: C' });
  const m = G(); m.C.in = ['A', 'Z']; assert.deepEqual(fn('bimFlowOrder')(m), { error: 'missing node: C' });
  const c = G(); c.A = { op: 'double', in: ['C'] }; assert.deepEqual(fn('bimFlowOrder')(c), { error: 'cycle' });
});
test('WO-02 values through the graph: 10, then 14 when A is 4, unknown propagated', () => {
  assert.equal(fn('bimFlowEval')(G()).values.D, 10);
  const g = G(); g.A.value = 4; assert.equal(fn('bimFlowEval')(g).values.D, 14);
  g.B.value = null; assert.equal(fn('bimFlowEval')(g).values.D, null);
  const u = G(); u.D.op = 'eval'; assert.deepEqual(fn('bimFlowEval')(u), { error: 'unsupported op: D' });
  const x = G(); x.D = { op: 'mul', in: ['A', 'C'] }; assert.equal(fn('bimFlowEval')(x).values.D, 10);
});
test('WO-03 an app\'s message checked: its origin, a known command, object arguments', () => {
  const A = { 'select': 1, 'snapshot': 1 }, O = ['https://app.example'];
  assert.deepEqual(fn('bimSdkCheck')({ cmd: 'select', args: { id: 'w1' } }, A, 'https://app.example', O), { ok: true });
  assert.deepEqual(fn('bimSdkCheck')({ cmd: 'select' }, A, 'https://evil.example', O), { ok: false, why: 'origin not allowed' });
  assert.deepEqual(fn('bimSdkCheck')({ cmd: 'deleteAll' }, A, 'https://app.example', O), { ok: false, why: 'unknown command deleteAll' });
  assert.deepEqual(fn('bimSdkCheck')({ cmd: 'select', args: [1] }, A, 'https://app.example', O), { ok: false, why: 'args must be an object' });
  assert.deepEqual(fn('bimSdkCheck')('select', A, 'https://app.example', O), { ok: false, why: 'not a command message' });
  assert.deepEqual(fn('bimSdkCheck')({ cmd: 'toString' }, A, 'https://app.example', O), { ok: false, why: 'unknown command toString' });
});
test('WO-04 a read-only snapshot: only the listed fields, deep copies', () => {
  const st = { levels: [{ id: 'L0' }], secret: 'x', sel: 'w1' };
  const s = fn('bimSdkSnapshot')(st, ['levels', 'sel', 'nope']);
  assert.deepEqual(s, { levels: [{ id: 'L0' }], sel: 'w1' });
  s.levels[0].id = 'changed'; assert.equal(st.levels[0].id, 'L0');
});
