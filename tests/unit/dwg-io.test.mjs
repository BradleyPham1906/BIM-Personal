// V252: DWG open and save through cc-dwg (engine/io/dwg-io.js). The conversion both ways, and a write and read of a
// real DWG through the pinned runtime (runtime/cc-dwg/<rev>/bim-dwg.min.js) run in Node.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);
const ent = (o) => Object.assign({ layer: 'A-WALL', color: { index: 256 }, invisible: false, extrusion: { x: 0, y: 0, z: 1 } }, o);

function ccdwg() {
  const ctx = { console, TextDecoder, TextEncoder, performance, Uint8Array, ArrayBuffer, DataView };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(new URL('../../runtime/cc-dwg/e36a94d/bim-dwg.min.js', import.meta.url), 'utf8') + ';this.D=BIMDWG;', ctx);
  return ctx.D;
}

test('a cc-dwg model becomes the DXF reader\'s entities, blocks expanded', () => {
  const m = {
    version: 'AC1032', header: { INSUNITS: 4 },
    tables: { layers: [{ name: 'A-WALL', color: { index: 1 }, off: false, frozen: false, locked: false, lineweight: 50, plot: true }] },
    blocks: [
      { name: '*Model_Space', base: { x: 0, y: 0 }, entities: [
        ent({ type: 'LWPOLYLINE', closed: true, vertices: [{ x: 0, y: 0, bulge: 0 }, { x: 1000, y: 0, bulge: 0.5 }, { x: 1000, y: 500, bulge: 0 }] }),
        ent({ type: 'ARC', center: { x: 0, y: 0, z: 0 }, radius: 100, startAngle: 0, endAngle: Math.PI / 2 }),
        ent({ type: 'MTEXT', insert: { x: 5, y: 5, z: 0 }, value: '{\\fArial;A}\\PB', height: 2.5, xAxis: { x: 0, y: 1, z: 0 } }),
        ent({ type: 'INSERT', block: 'CHAIR', insert: { x: 2000, y: 0, z: 0 }, scale: { x: 1, y: 1, z: 1 }, rotation: Math.PI / 2,
          attribs: [ent({ type: 'ATTRIB', value: 'C1', insert: { x: 2000, y: 100, z: 0 }, height: 2, rotation: 0 })] }),
        ent({ type: 'HATCH', loops: [{ edges: [{ type: 'line', start: { x: 0, y: 0 }, end: { x: 10, y: 0 } },
          { type: 'line', start: { x: 10, y: 0 }, end: { x: 10, y: 10 } }, { type: 'line', start: { x: 10, y: 10 }, end: { x: 0, y: 0 } }] }] }),
        ent({ type: 'MULTILEADER' }),
      ] },
      { name: '*Paper_Space', base: { x: 0, y: 0 }, entities: [ent({ type: 'LINE', start: { x: 0, y: 0 }, end: { x: 1, y: 1 } })] },
      { name: 'CHAIR', base: { x: 0, y: 0 }, entities: [ent({ type: 'LINE', layer: '0', start: { x: 0, y: 0, z: 0 }, end: { x: 400, y: 0, z: 0 } })] },
    ],
  };
  const r = E.bimDwgToParsed(m);
  assert.equal(r.scale, 0.001, 'millimetres');
  assert.equal(r.layers['A-WALL'].lineweight, 0.5);
  const types = r.entities.map((e) => e.type).sort();
  // V261: a hatch arrives as a HATCH (filled), not as its outline
  assert.deepEqual(types, ['ARC', 'HATCH', 'LINE', 'LWPOLYLINE', 'TEXT', 'TEXT']);
  const pl = r.entities.find((e) => e.type === 'LWPOLYLINE');
  assert.deepEqual(pl.bulges, [0, 0.5, 0]);
  near(r.entities.find((e) => e.type === 'ARC').a2, 90);
  const chair = r.entities.find((e) => e.type === 'LINE');
  near(chair.p2[0], 2000); near(chair.p2[1], 400);   // turned 90 degrees at the insert
  assert.equal(chair.layer, 'A-WALL', 'layer 0 in the block takes the insert\'s');
  const mt = r.entities.find((e) => e.type === 'TEXT' && /A/.test(e.text));
  assert.equal(mt.text, 'A\nB'); near(mt.rot, 90);
  assert.equal(r.skipped.MULTILEADER, 1);
});

test('a true colour arrives as hex, an index as its number, ByLayer as null', () => {
  assert.equal(E.bimDwgColor({ rgb: 0x12ab34 }), '#12ab34');
  assert.equal(E.bimDwgColor({ index: 3 }), 3);
  assert.equal(E.bimDwgColor({ index: 256 }), null);
});

test('a mirrored entity (extrusion 0,0,-1) comes in mirrored in x', () => {
  const o = E.bimDwgEntity(ent({ type: 'LINE', start: { x: 1, y: 2, z: 0 }, end: { x: 3, y: 2, z: 0 }, extrusion: { x: 0, y: 0, z: -1 } }));
  assert.deepEqual([o.p1[0], o.p2[0]], [-1, -3]);
});

test('a plan saved as DWG and read back by cc-dwg keeps its geometry, text and layers', () => {
  const D = ccdwg();
  const res = {
    layers: { 'A-WALL': { name: 'A-WALL', color: '#ff0000', lineweight: 0.35 } }, insUnits: 6,
    entities: [
      { type: 'LWPOLYLINE', layer: 'A-WALL', closed: true, pts: [[0, 0], [5, 0], [5, 4], [0, 4]], bulges: [0, 0.4142, 0, 0] },
      { type: 'LINE', layer: 'A-WALL', p1: [0, 0, 0], p2: [5, 4, 0] },
      { type: 'TEXT', layer: 'A-WALL', p: [1, 1, 0], h: 0.3, text: 'Living', rot: 0 },
    ],
  };
  for (const v of ['AC1015', 'AC1027', 'AC1032']) {
    const model = E.bimDwgModelFrom(res, v);
    const w = D.writeDwg(model, { version: v });
    assert.equal(String.fromCharCode(...w.bytes.subarray(0, 6)), v);
    const back = D.readDwg(w.bytes);
    assert.equal(back.report.error, undefined, v + ': ' + back.report.error);
    const ms = back.blocks.find((b) => b.name === '*Model_Space').entities;
    // compared as JSON: arrays made inside the vm context have that context's prototype
    assert.equal(JSON.stringify(ms.map((e) => e.type).sort()), JSON.stringify(['LINE', 'LWPOLYLINE', 'TEXT']), v);
    const pl = ms.find((e) => e.type === 'LWPOLYLINE');
    assert.equal(pl.closed, true);
    near(pl.vertices[1].bulge, 0.4142, 1e-9);
    assert.equal(ms.find((e) => e.type === 'TEXT').value, 'Living');
    assert.ok(back.tables.layers.some((l) => l.name === 'A-WALL'), v + ': the layer');
    // and back through this app's own reader
    const r = E.bimDwgToParsed(back);
    assert.equal(r.entities.length, 3, v);
  }
});

test('a file that is not a DWG is refused with a reason, not thrown', () => {
  const D = ccdwg();
  const m = D.readDwg(new TextEncoder().encode('AC1027fake'));
  assert.match(m.report.error, /too short/);
});
