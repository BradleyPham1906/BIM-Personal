// V269: the spreadsheet (engine/views/spreadsheet-eval.js, spreadsheet.js): formulas, aliases, ranges, errors, the
// model read with obj(), and cells bound to properties.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const ev = (cells, aliases = {}, read = null) => E.bimSheetEvaluate(cells, aliases, read);

test('numbers, text and formulas with cells, aliases and functions', () => {
  const v = ev({ A1: '2', A2: '3.5', A3: '=A1*A2+1', B1: '=sum(A1:A3)', B2: '=width*2', C1: 'Width', C2: '=round(10/3, 2)',
    C3: '=if(A1>1, 10, 20)', C4: '=sin(30)', C5: '=-2^2', C6: '=max(A1:A2, 7)', C7: '=average(A1:A2)', C8: '=$A$1+mod(7, 3)' }, { A2: 'width' });
  assert.equal(v.A1, 2); assert.equal(v.A3, 8); assert.equal(v.B1, 13.5); assert.equal(v.B2, 7);
  assert.equal(v.C1, 'Width'); assert.equal(v.C2, 3.33); assert.equal(v.C3, 10);
  assert.ok(Math.abs(v.C4 - 0.5) < 1e-12); assert.equal(v.C5, -4); assert.equal(v.C6, 7); assert.equal(v.C7, 2.75); assert.equal(v.C8, 3);
});

test('an empty cell reads 0; text, a cycle and a bad formula are errors, carried to the cells that read them', () => {
  const v = ev({ A1: '=L40+1', A2: '=A3', A3: '=A2', A4: '=A2+1', B1: 'hello', B2: '=B1*2', B3: '=1/0', B4: '=foo(1)', B5: '=(1+2', B6: '=nosuch' });
  assert.equal(v.A1, 1);
  for (const k of ['A2', 'A3', 'A4', 'B2', 'B3', 'B4', 'B5', 'B6']) assert.ok(v[k] && v[k].error, k + ' is an error');
  assert.match(v.A2.error, /cycle|error/);
  assert.match(v.B3.error, /Division by zero/);
});

test('obj() reads the model through the reader given', () => {
  const read = (name, prop) => { if (name === 'Wall_1' && prop === 'height') return 3; throw new Error('no ' + prop); };
  const v = ev({ A1: '=obj("Wall_1", "height")*2', A2: '=obj("Wall_1", "colour")' }, {}, read);
  assert.equal(v.A1, 6);
  assert.ok(v.A2.error);
});

test('a sheet kept in a project is checked', () => {
  const s = E.bimSheetValid({ cells: { A1: '1', ZZ9: '2', B2: '' }, aliases: { A1: 'width', A2: 'B3', A3: '9x' }, binds: [{ cell: 'A1', obj: 'o1', prop: 'z' }, { cell: 'Q1' }] });
  assert.deepEqual(s.cells, { A1: '1' });
  assert.deepEqual(s.aliases, { A1: 'width' });
  assert.equal(s.binds.length, 1);
});

test('a bound cell sets the property: position, and a text\'s words', () => {
  const o = { id: 'o1', name: 'Box', t: 'solid', pos: [1, 0, 2] };
  assert.equal(E.bimSheetApplyOne(o, 'y', 4), true);
  assert.deepEqual(o.pos, [1, 4, 2]);
  assert.equal(E.bimSheetApplyOne(o, 'y', 4), false, 'no change, no step');
  const t = { id: 't1', t: 'text', text: 'a' };
  assert.equal(E.bimSheetApplyOne(t, 'text', 2.5), true);
  assert.equal(t.text, '2.5');
  assert.deepEqual(E.bimSheetTargets({ t: 'sketch', constraints: [{ id: 'c1', type: 'distance', refs: [0, 1], value: 2 }] }).map((x) => x[0]), ['x', 'y', 'z', 'con:c1']);
});
