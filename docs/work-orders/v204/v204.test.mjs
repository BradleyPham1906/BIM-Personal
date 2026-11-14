/* V204's work-order tests (docs/work-orders/v204/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/bim/parametric.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v204/v204.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v204/v204.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimPfOrder", "bimPfDownstream", "bimPfExpr", "bimPfRebuild"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/parametric.js'), 'utf8');
  if (process.env.V204_REF) src += fs.readFileSync(process.env.V204_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/parametric.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

const FS = [
  { id: 'pocket1', kind: 'pocket', refs: ['pad1'], inputs: { w: '1', l: '0.5', depth: '0.1' } },
  { id: 'sk1', kind: 'sketch', refs: [], inputs: { w: 'width', l: '3' } },
  { id: 'pad1', kind: 'pad', refs: ['sk1'], inputs: { depth: '0.3' } }
];
test('WO-01 features in dependency order; a cycle is named, never built', () => {
  assert.deepEqual(fn('bimPfOrder')(FS), { order: ['sk1', 'pad1', 'pocket1'] });
  assert.deepEqual(fn('bimPfOrder')([{ id: 'a', refs: ['b'] }, { id: 'b', refs: ['a'] }]), { error: 'cycle', ids: ['a', 'b', 'a'] });
  assert.deepEqual(fn('bimPfOrder')([{ id: 'a', refs: ['gone'] }]), { order: ['a'] });
});
test('WO-02 what a change reaches: every feature downstream, in order', () => {
  assert.deepEqual(fn('bimPfDownstream')(FS, 'sk1'), ['pad1', 'pocket1']);
  assert.deepEqual(fn('bimPfDownstream')(FS, 'pocket1'), []);
});
test('WO-03 safe expressions: numbers, names, + - * / and brackets, nothing else', () => {
  const e = fn('bimPfExpr');
  assert.deepEqual(e('width * 2 + (3 - 1) / 4', { width: 5 }), { value: 10.5 });
  assert.deepEqual(e('-width', { width: 5 }), { value: -5 });
  assert.deepEqual(e('.5*2'), { value: 1 });
  assert.deepEqual(e('depth', { width: 5 }), { error: 'unknown name depth' });
  assert.deepEqual(e('1/0'), { error: 'division by zero' });
  assert.deepEqual(e('alert(1)', { alert: 1 }), { error: 'unexpected (' });
  assert.deepEqual(e('(1+2'), { error: 'expected )' });
});
test('WO-04 rebuild: the research\'s worked example (3.6 m3, 4.5 m3, then 4.45 m3)', () => {
  const r4 = fn('bimPfRebuild')(FS.slice(1), { width: 4 });
  near(r4.results.pad1.volume, 3.6, 1e-12);
  const r5 = fn('bimPfRebuild')(FS, { width: 5 });
  near(r5.results.pad1.volume, 4.5, 1e-12);
  near(r5.results.pocket1.volume, 4.45, 1e-12);
  assert.deepEqual(r5.order, ['sk1', 'pad1', 'pocket1']);
});
test('WO-04 a failed feature says why and keeps its last valid result; a cycle builds nothing', () => {
  const ok = X.bimPfRebuild(FS, { width: 5 }).results;
  const bad = fn('bimPfRebuild')(FS, { width: 0.5 }, ok).results;
  assert.equal(bad.pocket1.status, 'failed');
  assert.equal(bad.pocket1.why, 'the pocket does not fit in its pad');
  near(bad.pocket1.kept.volume, 4.45, 1e-12);
  assert.equal(fn('bimPfRebuild')(FS, {}).results.sk1.why, 'the sketch needs a positive width and length');
  assert.equal(fn('bimPfRebuild')(FS, {}).results.pad1.status, 'failed');
  assert.equal(fn('bimPfRebuild')([{ id: 'a', kind: 'pad', refs: ['a'], inputs: {} }], {}).error, 'cycle');
});
