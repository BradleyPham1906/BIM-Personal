/* V178's work-order tests (docs/work-orders/v178/SPEC.md, WO-01 to WO-12): the pure functions of
   src/js/engine/sheets/report-model.js: a report's data states and provenance, its board plan, its frozen manifest,
   legends without silent truncation, and components with overrides.

   Outside tests/unit/ while the work orders are open, so `npm test` and CI stay green on main. Run them with:
     node --test docs/work-orders/v178/v178.test.mjs
     node --test --test-name-pattern="WO-03" docs/work-orders/v178/v178.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text; its functions use no name
   from another file. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimRptFromLive', 'bimRptDatum', 'bimRptText', 'bimRptRings', 'bimRptPlan', 'bimRptIssue', 'bimRptManifest',
  'bimRptStale', 'bimRptLegend', 'bimCompResolve', 'bimCompSync', 'bimCompDetach'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/sheets/report-model.js'), 'utf8');
  if (process.env.V178_REF) src += fs.readFileSync(process.env.V178_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const R = load();
const fn = (n) => { assert.equal(typeof R[n], 'function', n + ' is not built yet in src/js/engine/sheets/report-model.js'); return R[n]; };
const BLANK = { value: null, unit: '', state: 'unavailable', source: '', vintage: '', retrieved: '', method: '', license: '' };

test('WO-01 a live field outcome as a report state', () => {
  const f = fn('bimRptFromLive');
  assert.deepEqual(['ok', 'stale', 'gone', 'none', undefined, 'x'].map(f), ['available', 'stale', 'failed', 'unavailable', 'unavailable', 'unavailable']);
});

test('WO-02 a datum: every field kept as text, zero stays zero', () => {
  const d = fn('bimRptDatum')({ value: 0, unit: 'people', state: 'available', source: 'ACS 5-year', vintage: '2023', retrieved: '2026-11-14', method: 'area-weighted', license: 'public domain', extra: 1 });
  assert.deepEqual(d, { value: 0, unit: 'people', state: 'available', source: 'ACS 5-year', vintage: '2023', retrieved: '2026-11-14', method: 'area-weighted', license: 'public domain' });
});
test('WO-02 no value is never available; an unknown state is unavailable; unavailable and failed carry no value', () => {
  const f = fn('bimRptDatum');
  assert.deepEqual(f({ value: NaN, state: 'available' }), BLANK);
  assert.deepEqual(f({ value: '', state: 'partial' }), BLANK);
  assert.deepEqual(f({ value: 5, state: 'guess' }), BLANK);
  assert.deepEqual(f({ value: 5, state: 'failed', source: 3 }), Object.assign({}, BLANK, { state: 'failed' }));
  assert.equal(f({ value: 'R-4', state: 'stale' }).value, 'R-4');
  assert.deepEqual(f(null), BLANK);
});

test('WO-03 a datum as text: its state always shows', () => {
  const t = fn('bimRptText');
  assert.equal(t({ value: 0, unit: 'm', state: 'available' }), '0 m');
  assert.equal(t({ value: 12.345, unit: 'm', state: 'available' }, 1), '12.3 m');
  assert.equal(t({ value: 3400, unit: '', state: 'partial' }), '3400 (partial)');
  assert.equal(t({ value: 'R-4', unit: '', state: 'stale' }, 2), 'R-4 (out of date)');
  assert.equal(t({ value: null, unit: 'm', state: 'unavailable' }), 'Not available');
  assert.equal(t({ value: null, unit: 'm', state: 'failed' }), 'Failed');
  assert.equal(t(null), 'Not available');
  assert.equal(t({ value: 1.5, unit: '', state: 'available' }, 9), '2');
});

test('WO-04 rings: positive, once each, smallest first, labelled as cumulative', () => {
  assert.deepEqual(fn('bimRptRings')([3, 1, 2, 2, -1, 0, NaN, 'x']), [
    { km: 1, label: 'Within 1 km', cumulative: true }, { km: 2, label: 'Within 2 km', cumulative: true }, { km: 3, label: 'Within 3 km', cumulative: true }]);
  assert.deepEqual(fn('bimRptRings')(null), []);
});

test('WO-05 the plan: the eight site boards then the six DA sheets, numbered in one series', () => {
  const p = fn('bimRptPlan')({ sa: true, da: true });
  assert.equal(p.length, 14);
  assert.deepEqual(p[0], { id: 'SA-01', family: 'sa', title: 'Location and context', n: 1 });
  assert.deepEqual(p[7], { id: 'SA-08', family: 'sa', title: 'Buildable area and yield', n: 8 });
  assert.deepEqual(p[8], { id: 'DA-01', family: 'da', title: 'Context plan, sun and wind', n: 9 });
  assert.deepEqual(p[13], { id: 'DA-06', family: 'da', title: 'Perspectives', n: 14 });
  assert.deepEqual(fn('bimRptPlan')({ da: true }).map((b) => b.n), [1, 2, 3, 4, 5, 6]);
  assert.deepEqual(fn('bimRptPlan')(null), []);
});

test('WO-06 issue status: complete only when every datum is available; never blocked', () => {
  const i = fn('bimRptIssue');
  assert.deepEqual(i({ a: { value: 1, state: 'available' }, b: { value: 0, state: 'available' } }),
    { status: 'complete', counts: { available: 2, partial: 0, stale: 0, unavailable: 0, failed: 0 }, marked: [] });
  assert.deepEqual(i({ z: { value: 1, state: 'stale' }, a: { value: null, state: 'available' }, m: { state: 'failed' } }),
    { status: 'marked', counts: { available: 0, partial: 0, stale: 1, unavailable: 1, failed: 1 }, marked: ['a', 'm', 'z'] });
  assert.equal(i(null).status, 'complete');
});

test('WO-07 the frozen manifest: copies, keys in order, each datum cleaned', () => {
  const data = { pop: { value: 1200, unit: 'people', state: 'partial' }, area: { value: 5000, unit: 'm2', state: 'available' } };
  const m = fn('bimRptManifest')({ id: 'rep-1', boards: ['SA-01', 7, 'DA-02'], data }, 42, '2026-11-14T10:00:00-05:00');
  assert.deepEqual(Object.keys(m), ['id', 'revision', 'generated', 'boards', 'data']);
  assert.equal(m.revision, 42);
  assert.equal(m.generated, '2026-11-14T10:00:00-05:00');
  assert.deepEqual(m.boards, ['SA-01', 'DA-02']);
  assert.deepEqual(Object.keys(m.data), ['area', 'pop']);
  data.pop.value = 9;
  assert.equal(m.data.pop.value, 1200, 'a copy, not the live object');
  assert.deepEqual(fn('bimRptManifest')(null, 1, 't'), { id: '', revision: 1, generated: 't', boards: [], data: {} });
});
test('WO-08 a manifest is out of date when the model revision moved on', () => {
  assert.equal(fn('bimRptStale')({ revision: 42 }, 42), false);
  assert.equal(fn('bimRptStale')({ revision: 42 }, 43), true);
  assert.equal(fn('bimRptStale')(null, 1), true);
});

test('WO-09 a legend keeps its first rows and says how many more', () => {
  const rows = Array.from({ length: 15 }, (_, i) => ({ c: '#000', t: 'Class ' + i }));
  assert.deepEqual(fn('bimRptLegend')(rows, 12).more, 3);
  assert.equal(fn('bimRptLegend')(rows, 12).rows.length, 12);
  assert.deepEqual(fn('bimRptLegend')(rows.slice(0, 12)), { rows: rows.slice(0, 12), more: 0 });
  assert.deepEqual(fn('bimRptLegend')(rows.slice(0, 3), 0).rows.length, 3, 'a bad max is 12');
  assert.deepEqual(fn('bimRptLegend')(null, 5), { rows: [], more: 0 });
});

const DEF = { id: 'cmp-title', version: 2, props: { text: 'Site Analysis', color: '#111', size: 24 } };
test('WO-10 an instance shows the definition with its own overrides on top; unknown overrides ignored', () => {
  assert.deepEqual(fn('bimCompResolve')(DEF, { id: 'i1', defId: 'cmp-title', overrides: { color: '#c00', font: 'x' } }),
    { text: 'Site Analysis', color: '#c00', size: 24 });
  assert.deepEqual(fn('bimCompResolve')(DEF, null), DEF.props);
  assert.notEqual(fn('bimCompResolve')(DEF, null), DEF.props, 'a new object');
});
test('WO-11 sync to a new version keeps the overrides the new version still has', () => {
  const v3 = { id: 'cmp-title', version: 3, props: { text: 'Site Analysis report', size: 28 } };
  const inst = { id: 'i1', defId: 'cmp-title', version: 2, overrides: { color: '#c00', size: 30 } };
  assert.deepEqual(fn('bimCompSync')(inst, v3), { id: 'i1', defId: 'cmp-title', version: 3, overrides: { size: 30 } });
  assert.deepEqual(inst.overrides, { color: '#c00', size: 30 }, 'the old instance unchanged');
});
test('WO-12 detach: a plain copy of what it shows, no link to the definition', () => {
  assert.deepEqual(fn('bimCompDetach')(DEF, { id: 'i1', defId: 'cmp-title', overrides: { size: 30 } }),
    { id: 'i1', props: { text: 'Site Analysis', color: '#111', size: 30 } });
});
