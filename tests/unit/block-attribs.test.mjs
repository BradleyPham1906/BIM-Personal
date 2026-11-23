// V260: block attributes (engine/assets/block-attribs.js), the definition's checks and the values an insert takes.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();

test('an attribute definition: a tag in capitals, a prompt, a default', () => {
  const a = E.bimAttdefValid({ tag: ' door mark ', prompt: '', def: 'D1' });
  assert.deepEqual(a, { tag: 'DOOR_MARK', prompt: 'DOOR_MARK', def: 'D1' });
  assert.match(E.bimAttdefValid({ tag: '' }).error, /tag/);
  assert.match(E.bimAttdefValid({ tag: 'A/B' }).error, /letters/);
});

test('an insert takes the typed values, else the defaults', () => {
  const defs = [{ tag: 'NO', def: '01' }, { tag: 'TITLE', def: 'Plan' }];
  assert.deepEqual(E.bimAttribFill(defs, { TITLE: 'Ground floor' }), [{ tag: 'NO', value: '01' }, { tag: 'TITLE', value: 'Ground floor' }]);
  assert.deepEqual(E.bimAttribFill(defs, null).map((v) => v.value), ['01', 'Plan']);
});

test('a DXF insert\'s attribute keeps its tag', () => {
  const r = E.dxfParse('0\nSECTION\n2\nENTITIES\n0\nATTRIB\n8\n0\n10\n1\n20\n2\n40\n0.2\n1\nA-101\n2\nSHEET\n70\n0\n0\nENDSEC\n0\nEOF\n');
  assert.equal(r.entities[0].type, 'TEXT');
  assert.equal(r.entities[0].tag, 'SHEET');
  assert.equal(r.entities[0].text, 'A-101');
});

test('a copy keeps a text\'s height, rotation and attribute, and a line\'s own look, but not its insert', () => {
  const t = { id: 't1', t: 'text', text: 'D1', pt: [1, 2], y: 0, pos: [0, 0, 0], height: 0.3, rot: 45, attrib: { tag: 'MARK' }, blockRef: { name: 'B', ins: 'i1' } };
  const c = E.bimDuplicateObject(t, 5, 0);
  assert.equal(c.height, 0.3); assert.equal(c.rot, 45); assert.deepEqual(c.attrib, { tag: 'MARK' });
  assert.equal(c.blockRef, undefined);
  assert.deepEqual(c.pt, [6, 2]);
  const s = { id: 's1', t: 'sketch', pts: [[0, 0], [1, 0]], closed: false, y: 0, pos: [0, 0, 0], color: '#ff0000', linetype: 'HIDDEN', lineweight: 0.5 };
  const c2 = E.bimDuplicateObject(s, 1, 1);
  assert.equal(c2.color, '#ff0000'); assert.equal(c2.linetype, 'HIDDEN'); assert.equal(c2.lineweight, 0.5);
});
