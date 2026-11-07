// V172f, core/project-store.js: which records are kept from older keys, which copy of a project wins, and what the
// older keys hold (docs/research/research-local-storage.md, part 13).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const fresh = () => ({ objs: [], grids: [], sheets: [], views: [], levels: [{ id: 'lvl-0' }], layers: [{ id: 'layer-0' }],
  buildings: [{ id: 'bldg-0' }], site: { name: 'Site' }, titleBlock: { project: '', client: '', drawnBy: '', checkedBy: '' },
  history: null, resultLayers: [], pres: null, classifications: [], dataFeatures: {} });

test('an older build\'s fresh project is empty; anything done in it is not', () => {
  assert.equal(E.bimRecordEmpty(fresh()), true);
  assert.equal(E.bimRecordEmpty(null), true);
  for (const [what, change] of [
    ['an object', (r) => r.objs.push({ id: 'a' })],
    ['a name', (r) => { r.titleBlock.project = 'Tower'; }],
    ['a sheet', (r) => r.sheets.push({ id: 's' })],
    ['a second level', (r) => r.levels.push({ id: 'lvl-1' })],
    ['a place on the site', (r) => { r.site.lat = 40; }],
    ['a commit', (r) => { r.history = { commits: [{ id: 'c' }] }; }],
    ['a board', (r) => { r.pres = { boards: [{ id: 'b' }] }; }],
  ]) {
    const r = fresh(); change(r);
    assert.equal(E.bimRecordEmpty(r), false, what);
  }
});

test('the journal wins only when it is newer than the database\'s record', () => {
  assert.equal(E.bimJournalNewer(null, null), false);
  assert.equal(E.bimJournalNewer(null, { saved: 5 }), true, 'no record: the journal');
  assert.equal(E.bimJournalNewer({ saved: 4 }, { saved: 5 }), true);
  assert.equal(E.bimJournalNewer({ saved: 5 }, { saved: 5 }), false, 'the same write committed: the record');
  assert.equal(E.bimJournalNewer({ saved: 6 }, { saved: 5 }), false);
});

test('the older keys are read by kind: records, V172d pointers, templates, the library, the list', () => {
  localStorage.clear();
  localStorage.setItem('acad3dV1', JSON.stringify({ docId: 'd1', objs: [{ id: 'w' }] }));
  localStorage.setItem('acad3dDocV1:d2', JSON.stringify({ objs: [] }));
  localStorage.setItem('acad3dDocV1:d3', JSON.stringify({ idb: 1, docId: 'd3', count: 4 }));
  localStorage.setItem('acad3dTemplateV1:t1', '{"objs":[]}');
  localStorage.setItem('acad3dFamilyLibrary', '[{"id":"fam-1"}]');
  localStorage.setItem('acad3dDocsV1', '{"v":1}');
  localStorage.setItem('acad3dTheme', 'dark');
  const L = E.bimLegacyScan();
  assert.deepEqual(L.projects.map((p) => [p.id, p.active]).sort(), [['d1', true], ['d2', false]]);
  assert.deepEqual(L.pointers.map((p) => p.id), ['d3']);
  assert.deepEqual(L.templates.map((p) => p.id), ['t1']);
  assert.deepEqual(L.library.arr, [{ id: 'fam-1' }]);
  assert.equal(L.list.key, 'acad3dDocsV1');
  localStorage.clear();
});

test('an older key is removed only while it still holds what was copied', () => {
  localStorage.setItem('acad3dV1', 'A');
  E.bimRetire('acad3dV1', 'B');
  assert.equal(localStorage.getItem('acad3dV1'), 'A', 'changed since the copy: kept');
  E.bimRetire('acad3dV1', 'A');
  assert.equal(localStorage.getItem('acad3dV1'), null);
});
