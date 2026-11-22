// V257 (D5): an object's own colour, linetype and lineweight, ByLayer when unset (engine/layers/object-look.js).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const layer = { id: 'L', color: '#336699', linetype: 'DASHED', lineweight: 0.5 };

test('unset is ByLayer; set wins over the layer', () => {
  assert.deepEqual(E.bimObjLook({}, layer), { color: '#336699', linetype: 'DASHED', lineweight: 0.5 });
  assert.deepEqual(E.bimObjLook({ color: '#ff0000', linetype: 'CENTER', lineweight: 0.13 }, layer),
    { color: '#ff0000', linetype: 'CENTER', lineweight: 0.13 });
  assert.equal(E.bimObjLook({ linetype: 'NOT-A-LINETYPE' }, layer).linetype, 'DASHED', 'an unknown linetype is ByLayer');
});

test('setting one, and ByLayer clearing it', () => {
  const o = {};
  assert.equal(E.bimObjLookSet(o, 'color', '#FF8800'), '');
  assert.equal(o.color, '#ff8800');
  assert.equal(E.bimObjLookSet(o, 'linetype', 'hidden'), '');
  assert.equal(o.linetype, 'HIDDEN');
  assert.equal(E.bimObjLookSet(o, 'lineweight', '0.35'), '');
  assert.equal(o.lineweight, 0.35);
  assert.match(E.bimObjLookSet(o, 'lineweight', '0.33'), /lineweights/);
  assert.match(E.bimObjLookSet(o, 'color', 'red'), /colour/);
  for (const f of ['color', 'linetype', 'lineweight']) assert.equal(E.bimObjLookSet(o, f, 'ByLayer'), '');
  assert.deepEqual(o, {});
});

test('a DXF entity\'s own true colour, linetype and lineweight are read', () => {
  const r = E.dxfParse('0\nSECTION\n2\nENTITIES\n0\nLINE\n8\nA\n6\nHIDDEN\n62\n1\n420\n16746496\n370\n35\n10\n0\n20\n0\n11\n1\n21\n0\n' +
    '0\nLINE\n8\nA\n6\nBYLAYER\n370\n-1\n10\n0\n20\n0\n11\n1\n21\n0\n0\nENDSEC\n0\nEOF\n');
  assert.equal(r.entities[0].color, '#ff8800', '420 wins over 62');
  assert.equal(r.entities[0].linetype, 'HIDDEN');
  assert.equal(r.entities[0].lineweight, 0.35);
  assert.equal(r.entities[1].linetype, undefined, 'BYLAYER is ByLayer');
  assert.equal(r.entities[1].lineweight, undefined, '-1 is ByLayer');
});
