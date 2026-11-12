// V195, glTF in and out (io/gltf.js): welding, the edges worth drawing, and a hand-built GLB read through three.js's
// own GLTFLoader into the model. Export needs a browser's FileReader; it is checked in the browser.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const G = globalThis.__a3dGltf;
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

// a unit cube as glTF gives it: 24 corners (each face its own four), 12 triangles
function cubeArrays() {
  const P = [], I = [];
  const faces = [
    [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], [[0, 0, 1], [0, 1, 1], [1, 1, 1], [1, 0, 1]],
    [[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1]], [[1, 0, 0], [1, 0, 1], [1, 1, 1], [1, 1, 0]],
    [[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]], [[0, 1, 0], [1, 1, 0], [1, 1, 1], [0, 1, 1]]];
  faces.forEach((f) => { const b = P.length / 3; f.forEach((p) => P.push(...p)); I.push(b, b + 1, b + 2, b, b + 2, b + 3); });
  return { pos: new Float32Array(P), index: I };
}

test('corners on one point are made one, triangles of no area left out', () => {
  const { pos, index } = cubeArrays();
  const m = G.weld(pos, index);
  assert.equal(m.v.length, 8);
  assert.equal(m.f.length, 12);
  const flat = G.weld(new Float32Array([0, 0, 0, 1, 0, 0, 1, 0, 0]), null);
  assert.equal(flat.f.length, 0, 'two corners of a triangle on one point: no triangle');
  const near = G.weld(new Float32Array([0, 0, 0, 1, 0, 0, 0, 0, 1, 0.000001, 0, 0, 1, 0, 0, 0, 1, 0]), null);
  assert.equal(near.v.length, 4, 'a hundredth of a millimetre apart is one point');
});

test('a cube draws its 12 edges, not the diagonals of its 12 triangles', () => {
  const { pos, index } = cubeArrays();
  const m = G.weld(pos, index), e = G.edges(m);
  assert.equal(e.length, 12);
  const len = (a) => Math.hypot(m.v[a[0]][0] - m.v[a[1]][0], m.v[a[0]][1] - m.v[a[1]][1], m.v[a[0]][2] - m.v[a[1]][2]);
  e.forEach((x) => assert.equal(len(x), 1, 'an edge of the cube, not a diagonal'));
});

test('the edges of an open surface are drawn, and a gentle fold is not', () => {
  // two triangles folded by 10 degrees along their shared edge
  const s = Math.sin(10 * Math.PI / 180), c = Math.cos(10 * Math.PI / 180);
  const m = { v: [[0, 0, 0], [1, 0, 0], [0, 0, 1], [-c, s, 0]], f: [[0, 1, 2], [0, 2, 3]] };
  assert.equal(G.edges(m, 20).length, 4, 'the four border edges; the fold is under 20 degrees');
  assert.equal(G.edges(m, 5).length, 5, 'over 5 degrees it is drawn');
  // wound against each other: still the same surface
  const w = { v: m.v, f: [[0, 1, 2], [0, 3, 2]] };
  assert.equal(G.edges(w, 20).length, 4);
});

test('colours and the reasons a file is refused', () => {
  assert.equal(G.hex(1, 0, 0.5), '#ff0080');
  assert.equal(G.hex(-1, 2, 0), '#00ff00');
  assert.match(G.why(new Error('THREE.GLTFLoader: Unknown extension "KHR_texture_basisu".'), 'a.glb'), /KTX2/);
  assert.match(G.why(new Error('Failed to fetch'), 'a.gltf'), /one \.glb/);
  assert.match(G.why(new Error('Unexpected token'), 'a.glb'), /could not be read as glTF/);
});

test('an element as triangles for the file: fans, placed where it stands', () => {
  const A = G.arrays({ v: [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]], f: [[0, 1, 2, 3]] }, [10, 2, 0]);
  assert.deepEqual(Array.from(A.pos), [10, 2, 0, 11, 2, 0, 11, 2, 1, 10, 2, 1]);
  assert.deepEqual(A.index, [0, 1, 2, 0, 2, 3]);
});

// a GLB by hand: a red unit square, two triangles, its node moved 2 m along x
function glb() {
  const pos = new Float32Array([0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1]), idx = new Uint16Array([0, 2, 1, 0, 3, 2]);
  const bin = Buffer.concat([Buffer.from(pos.buffer), Buffer.from(idx.buffer)]);
  const json = {
    asset: { version: '2.0' }, scene: 0, scenes: [{ nodes: [0] }], nodes: [{ mesh: 0, translation: [2, 0, 0], name: 'Square' }],
    meshes: [{ primitives: [{ attributes: { POSITION: 0 }, indices: 1, material: 0 }] }],
    materials: [{ name: 'Red paint', pbrMetallicRoughness: { baseColorFactor: [1, 0, 0, 1] } }],
    buffers: [{ byteLength: bin.length }],
    bufferViews: [{ buffer: 0, byteOffset: 0, byteLength: 48 }, { buffer: 0, byteOffset: 48, byteLength: 12 }],
    accessors: [{ bufferView: 0, componentType: 5126, count: 4, type: 'VEC3', min: [0, 0, 0], max: [1, 0, 1] },
      { bufferView: 1, componentType: 5123, count: 6, type: 'SCALAR' }]
  };
  let js = Buffer.from(JSON.stringify(json));
  js = Buffer.concat([js, Buffer.alloc((4 - js.length % 4) % 4, 0x20)]);
  const b2 = Buffer.concat([bin, Buffer.alloc((4 - bin.length % 4) % 4, 0)]);
  const head = Buffer.alloc(12), c1 = Buffer.alloc(8), c2 = Buffer.alloc(8);
  head.writeUInt32LE(0x46546C67, 0); head.writeUInt32LE(2, 4); head.writeUInt32LE(12 + 8 + js.length + 8 + b2.length, 8);
  c1.writeUInt32LE(js.length, 0); c1.writeUInt32LE(0x4E4F534A, 4); c2.writeUInt32LE(b2.length, 0); c2.writeUInt32LE(0x004E4942, 4);
  const all = Buffer.concat([head, c1, js, c2, b2]);
  return all.buffer.slice(all.byteOffset, all.byteOffset + all.length);
}

test('a GLB is read by three.js own loader into a part where it stands, in its colour, with its outline', async () => {
  // three.js, as the browser has it once the rendered view or an import has loaded it. Placing the parts in the model
  // and in Assets is the SketchUp import's way, and draws the Layers panel: it is checked in the browser.
  if (!globalThis.BIMTHREE) vm.runInThisContext(fs.readFileSync(path.join(ROOT, 'runtime', 'three', '0.186.1', 'bim-three.min.js'), 'utf8'));
  const T = globalThis.BIMTHREE;
  const g = await new Promise((res, rej) => new T.GLTFLoader().parse(glb(), '', res, rej));
  const R = G.parts(T, g.scene);
  assert.equal(R.parts.length, 1);
  assert.equal(R.tris, 2); assert.equal(R.cut, 0);
  const q = R.parts[0];
  assert.equal(q.col, '#ff0000');
  assert.equal(q.name, 'Red paint');
  assert.equal(q.opacity, 1);
  const xs = q.mesh.v.map((p) => p[0]).sort();
  assert.deepEqual([xs[0], xs[xs.length - 1]], [2, 3], 'moved 2 m by its node, metres as the file gives them');
  assert.equal(q.mesh.v.length, 4);
  assert.equal(q.mesh.fe.length, 4, 'the four sides of the square, not its diagonal');
});
