// V263: binary DXF (engine/io/dxf-entities.js), written here byte by byte as the DXF Reference lays it out.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const SENT = 'AutoCAD Binary DXF\r\n\u001a\u0000';
function binDxf(groups, wide) {
  const parts = [Buffer.from(SENT, 'latin1')];
  for (const [code, type, v] of groups) {
    if (wide) { const b = Buffer.alloc(2); b.writeUInt16LE(code); parts.push(b); }
    else if (code < 255) parts.push(Buffer.from([code]));
    else { const b = Buffer.alloc(3); b[0] = 255; b.writeInt16LE(code, 1); parts.push(b); }
    if (type === 's') parts.push(Buffer.from(v + '\0', 'utf8'));
    else if (type === 'd') { const b = Buffer.alloc(8); b.writeDoubleLE(v); parts.push(b); }
    else if (type === 'h') { const b = Buffer.alloc(2); b.writeInt16LE(v); parts.push(b); }
    else if (type === 'i') { const b = Buffer.alloc(4); b.writeInt32LE(v); parts.push(b); }
    else if (type === 'b') parts.push(Buffer.from([v]));
    else if (type === 'x') parts.push(Buffer.from([v.length, ...v]));
  }
  return new Uint8Array(Buffer.concat(parts));
}
const LINE = [[0, 's', 'SECTION'], [2, 's', 'ENTITIES'], [0, 's', 'LINE'], [8, 's', 'WALLS'], [62, 'h', 1], [370, 'h', 35],
  [310, 'x', [0xde, 0xad]], [290, 'b', 1], [90, 'i', 7], [10, 'd', 1.5], [20, 'd', -2.25], [30, 'd', 0], [11, 'd', 4], [21, 'd', 2], [31, 'd', 0],
  [0, 's', 'ENDSEC'], [0, 's', 'EOF']];

test('a binary DXF (R13 and later, 2-byte codes) reads as its ASCII form does', () => {
  const b = binDxf(LINE, true);
  assert.equal(E.dxfIsBinary(b), true);
  const r = E.dxfParse(E.dxfTextFromBytes(b.buffer));
  assert.equal(r.entities.length, 1);
  const l = r.entities[0];
  assert.equal(l.type, 'LINE'); assert.equal(l.layer, 'WALLS'); assert.equal(l.lineweight, 0.35);
  assert.deepEqual(l.p1, [1.5, -2.25, 0]); assert.deepEqual(l.p2, [4, 2, 0]);
});

test('an R12 binary DXF (1-byte codes, 255 then a 2-byte code) too', () => {
  const r = E.dxfParse(E.dxfTextFromBytes(binDxf(LINE, false).buffer));
  assert.equal(r.entities[0].layer, 'WALLS');
  assert.equal(r.entities[0].lineweight, 0.35);
});

test('an ASCII DXF is passed through, and a binary one with an unknown code is refused', () => {
  const t = '0\nSECTION\n2\nENTITIES\n0\nENDSEC\n0\nEOF\n';
  assert.equal(E.dxfTextFromBytes(new TextEncoder().encode(t).buffer), t);
  const bad = binDxf([[0, 's', 'SECTION']], true), more = new Uint8Array(bad.length + 2);
  more.set(bad); more[bad.length] = 0x0f; more[bad.length + 1] = 0x27;   // code 9999
  assert.throws(() => E.dxfBinaryToText(more), /unknown group code 9999/);
});
