// tools/openskp/make_fixtures.mjs -- V163: the SketchUp files the import is tested on.
//
// Written with openskp's own writer (the same pinned commit as build_reader.mjs), from geometry
// defined here, so the repo holds no SketchUp file of unknown origin. What the test expects -- every
// object's bounding box, area and colour, every layer and block -- is worked out below from these
// same definitions, not read back through the reader, so a reader that got them wrong would fail.
//
//   OPENSKP=/path/to/openskp node make_fixtures.mjs
//
// The writer writes the 2013-2020 container; files from SketchUp 2021 and later (a ZIP) are read by
// the same reader and were checked by hand on openskp's own samples (reference/research-sketchup-import.md).
import * as esbuild from 'esbuild';
import { zlibSync } from 'fflate';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { execSync } from 'child_process';

const COMMIT = '359d1836c9665484c193635796a54aef004babac';
const SRC = process.env.OPENSKP;
if (!SRC) { console.error('Set OPENSKP to a checkout of github.com/iamahsanmehmood/openskp'); process.exit(2); }
const head = execSync('git -C "' + SRC + '" rev-parse HEAD').toString().trim();
if (head !== COMMIT) { console.error('openskp is at ' + head + ', expected ' + COMMIT); process.exit(2); }

const here = path.dirname(new URL(import.meta.url).pathname);
const outDir = path.resolve(here, '../../tests/skp');
fs.mkdirSync(outDir, { recursive: true });
const tmp = path.join(here, '.writer.mjs');
await esbuild.build({
  entryPoints: [path.join(SRC, 'packages/typescript/src/create.ts')], bundle: true, format: 'esm',
  platform: 'node', target: 'node18', outfile: tmp, nodePaths: [path.join(here, 'node_modules')],
  absWorkingDir: here, logLevel: 'warning'
});
const { create } = await import(tmp);
fs.unlinkSync(tmp);
// The writer gives each definition a random GUID and the time it was written; a seeded sequence and
// a fixed time (2026-10-10) make the file the same bytes on every run, so its hash can be checked.
Date.now = () => Date.UTC(2026, 9, 10, 12, 0, 0);
let seed = 163;
Object.defineProperty(globalThis, 'crypto', { configurable: true, value: { getRandomValues(a) {
  for (let i = 0; i < a.length; i++) { seed = (seed * 1103515245 + 12345) >>> 0; a[i] = seed >>> 24; }
  return a;
} } });

// ---- a 4 x 4 PNG: two colours in a checkerboard, so its average is known ----
function crc32(b) {
  let c, crc = 0xffffffff;
  for (let n = 0; n < b.length; n++) {
    c = (crc ^ b[n]) & 0xff;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    crc = (crc >>> 8) ^ c;
  }
  return (crc ^ 0xffffffff) >>> 0;
}
function chunk(type, data) {
  const out = Buffer.alloc(12 + data.length);
  out.writeUInt32BE(data.length, 0);
  out.write(type, 4, 'ascii');
  Buffer.from(data).copy(out, 8);
  out.writeUInt32BE(crc32(Buffer.concat([Buffer.from(type, 'ascii'), Buffer.from(data)])), 8 + data.length);
  return out;
}
function checkerPng(a, b) {
  const W = 4, rows = [];
  for (let y = 0; y < W; y++) {
    const r = [0];
    for (let x = 0; x < W; x++) r.push(...((x + y) % 2 ? b : a));
    rows.push(...r);
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(W, 0); ihdr.writeUInt32BE(W, 4); ihdr[8] = 8; ihdr[9] = 2;
  return Buffer.concat([Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr), chunk('IDAT', zlibSync(Uint8Array.from(rows))), chunk('IEND', Buffer.alloc(0))]);
}

// ---- the model, in SketchUp's own frame: inches, Z up, +Y north ----
const IN = 0.0254;
const toApp = (p) => [p[0] * IN, p[2] * IN, -p[1] * IN];   // the app: metres, Y up, north is -Z
const MAT = {
  Brick: { rgb: [178, 34, 34] }, Oak: { rgb: [139, 90, 43] }, Glass: { rgb: [120, 170, 220], opacity: 0.35 },
  // SketchUp keeps its own materials' names in brackets, and shows them without
  '[Concrete]': { rgb: [160, 160, 160] }, Walnut: { rgb: [92, 64, 42] }
};
const TILE_A = [200, 60, 40], TILE_B = [240, 220, 200];
const TAGS = {
  Walls: { rgb: [200, 80, 60] }, Furniture: { rgb: [90, 140, 60] }, Windows: { rgb: [80, 140, 220] },
  'Hidden stuff': { rgb: [128, 128, 128], hidden: true }
};
function boxFaces(dx, dy, dz, z0 = 0) {
  if (z0) return boxFaces(dx, dy, dz).map((f) => f.map((p) => [p[0], p[1], p[2] + z0]));
  return [
    [[0, 0, 0], [0, dy, 0], [dx, dy, 0], [dx, 0, 0]], [[0, 0, dz], [dx, 0, dz], [dx, dy, dz], [0, dy, dz]],
    [[0, 0, 0], [dx, 0, 0], [dx, 0, dz], [0, 0, dz]], [[0, dy, 0], [0, dy, dz], [dx, dy, dz], [dx, dy, 0]],
    [[0, 0, 0], [0, 0, dz], [0, dy, dz], [0, dy, 0]], [[dx, 0, 0], [dx, dy, 0], [dx, dy, dz], [dx, 0, dz]]
  ];
}
const boxArea = (dx, dy, dz) => 2 * (dx * dy + dy * dz + dx * dz) * IN * IN;
const rotZ = (a) => (p) => [p[0] * Math.cos(a) - p[1] * Math.sin(a), p[0] * Math.sin(a) + p[1] * Math.cos(a), p[2]];
const mirX = (p) => [-p[0], p[1], p[2]];
function placedBox(dims, at, rot, z0 = 0) {
  const pts = [];
  for (const x of [0, dims[0]]) for (const y of [0, dims[1]]) for (const z of [z0, z0 + dims[2]]) {
    const q = (rot || ((p) => p))([x, y, z]);
    pts.push(toApp([q[0] + at[0], q[1] + at[1], q[2] + at[2]]));
  }
  const mn = [0, 1, 2].map((k) => Math.min(...pts.map((p) => p[k])));
  const mx = [0, 1, 2].map((k) => Math.max(...pts.map((p) => p[k])));
  return { min: mn, max: mx };
}
const hex = (rgb) => '#' + rgb.map((c) => c.toString(16).padStart(2, '0')).join('');

const b = create();
const mat = {};
for (const [n, m] of Object.entries(MAT)) mat[n] = b.addMaterial(n, m.rgb, m.opacity);
const png = checkerPng(TILE_A, TILE_B);
mat.Tiles = b.addTextureMaterial('Tiles', new Uint8Array(png), 'tiles.png', 12, 12);
const tag = {};
for (const [n, t] of Object.entries(TAGS)) tag[n] = b.addLayer(n, { color: [...t.rgb, 255], hidden: !!t.hidden });

const CHAIR = [20, 20, 40], WALL = [200, 20, 100], PANE = [40, 60];
const chair = b.addComponentDefinition('Chair', (d) => {
  for (const f of boxFaces(...CHAIR)) d.addFace(f, { material: mat.Oak });
});
// a component inside a component: a desk, its top, and a chair placed in it turned round
const TOP = [40, 20, 2], TOP_Z = 28, DESK_CHAIR = { at: [10, 25, 0], angle: Math.PI };
const desk = b.addComponentDefinition('Desk', (d) => {
  for (const f of boxFaces(...TOP, TOP_Z)) d.addFace(f, { material: mat.Walnut });
  d.addInstance(chair, { name: 'Desk chair', translation: DESK_CHAIR.at, rotation: { axis: [0, 0, 1], angleRadians: DESK_CHAIR.angle } });
});
const pane = b.addComponentDefinition('Pane', (d) => {
  d.addFace([[0, 0, 0], [PANE[0], 0, 0], [PANE[0], 0, PANE[1]], [0, 0, PANE[1]]], { material: mat.Glass });
});
const WALL_AT = [0, -100, 0];
// SketchUp names a group's definition Group#N, and the Outliner shows an unnamed group as Group:
// that name is how the import tells a group, which is not a block, from a component
b.addGroup((g) => { for (const f of boxFaces(...WALL)) g.addFace(f, { material: mat.Brick }); },
  { name: 'Group#1', translation: WALL_AT, layer: tag.Walls });
const PLACE = [
  { def: chair, name: 'Chair A', at: [50, 50, 0], layer: 'Furniture' },
  { def: chair, name: 'Chair B', at: [150, 50, 0], layer: 'Furniture', angle: Math.PI / 2 },
  { def: chair, name: 'Chair C', at: [300, 300, 0], layer: 'Hidden stuff' },
  // mirrored in x: a placement that turns its faces inside out unless the import turns them back
  { def: chair, name: 'Chair D', at: [350, 50, 0], layer: 'Furniture', mirror: true },
  { def: pane, name: 'Pane 1', at: [100, -110, 20], layer: 'Windows' },
  { def: desk, name: 'Desk 1', at: [200, 300, 0], layer: 'Furniture', angle: Math.PI / 2 }
];
for (const p of PLACE) {
  b.addInstance(p.def, { name: p.name, translation: p.at, layer: tag[p.layer],
    rotation: p.angle ? { axis: [0, 0, 1], angleRadians: p.angle } : undefined,
    matrix3x3: p.mirror ? [-1, 0, 0, 0, 1, 0, 0, 0, 1] : undefined });
}
const SLAB = [[0, 0, 0], [400, 0, 0], [400, 400, 0], [0, 400, 0]], HOLE = [[150, 150, 0], [150, 250, 0], [250, 250, 0], [250, 150, 0]];
b.addFace(SLAB, { material: mat['[Concrete]'], holes: [HOLE] });
const TILE_FACE = [[420, 0, 0], [470, 0, 0], [470, 50, 0], [420, 50, 0]];
b.addFace(TILE_FACE, { material: mat.Tiles });
// a face nobody painted: SketchUp draws its default white
const BARE = [[0, 450, 0], [50, 450, 0], [50, 500, 0], [0, 500, 0]];
b.addFace(BARE);
const bytes = b.toBytes();
fs.writeFileSync(path.join(outDir, 'site_kit.skp'), bytes);

// ---- what the import must make of it ----
const flat = (pts) => {
  const P = pts.map(toApp);
  return { min: [0, 1, 2].map((k) => Math.min(...P.map((p) => p[k]))), max: [0, 1, 2].map((k) => Math.max(...P.map((p) => p[k]))) };
};
const expect = {
  file: 'site_kit.skp', stem: 'site_kit', format: 'SketchUp 2017', zip: false,   // the writer's header says {17.0.1}
  sha256: crypto.createHash('sha256').update(bytes).digest('hex'),
  inch: IN,
  tags: Object.fromEntries(Object.entries(TAGS).map(([n, t]) => [n, { color: hex(t.rgb), hidden: !!t.hidden }])),
  seeThrough: { layer: 'site_kit - Windows - 65% see-through', parent: 'site_kit - Windows', transparency: 65 },
  objects: [
    { name: 'Group', tag: 'Walls', kind: 'group', definition: 'Group#1', material: 'Brick', color: hex(MAT.Brick.rgb),
      bounds: placedBox(WALL, WALL_AT), area: boxArea(...WALL) },
    { name: 'Desk 1', tag: 'Furniture', kind: 'component', definition: 'Desk', material: 'Walnut', color: hex(MAT.Walnut.rgb),
      bounds: placedBox(TOP, [200, 300, 0], rotZ(Math.PI / 2), TOP_Z), area: boxArea(...TOP) },
    // the chair in the desk: its own placement in the desk, then the desk's, so the order they are
    // applied in matters; untagged inside a tagged desk, it goes with the desk's tag, as in SketchUp
    { name: 'Desk chair', tag: 'Furniture', kind: 'component', definition: 'Chair', material: 'Oak', color: hex(MAT.Oak.rgb),
      inside: 'Desk 1', bounds: placedBox(CHAIR, [0, 0, 0], (p) => {
        const q = rotZ(DESK_CHAIR.angle)(p), r = [q[0] + DESK_CHAIR.at[0], q[1] + DESK_CHAIR.at[1], q[2]];
        const t = rotZ(Math.PI / 2)(r);
        return [t[0] + 200, t[1] + 300, t[2]];
      }), area: boxArea(...CHAIR) },
    ...PLACE.filter((p) => p.def === chair).map((p) => ({ name: p.name, tag: p.layer, kind: 'component', definition: 'Chair',
      material: 'Oak', color: hex(MAT.Oak.rgb), bounds: placedBox(CHAIR, p.at, p.angle ? rotZ(p.angle) : (p.mirror ? mirX : null)),
      area: boxArea(...CHAIR), volume: CHAIR[0] * CHAIR[1] * CHAIR[2] * IN * IN * IN, mirrored: !!p.mirror, hidden: !!TAGS[p.layer].hidden })),
    { name: 'Pane 1', tag: 'Windows', kind: 'component', definition: 'Pane', material: 'Glass', color: hex(MAT.Glass.rgb),
      opacity: MAT.Glass.opacity, bounds: flat([[100, -110, 20], [140, -110, 20], [140, -110, 80], [100, -110, 80]]),
      area: PANE[0] * PANE[1] * IN * IN },
    { name: 'Concrete faces', tag: null, kind: 'loose', material: 'Concrete', color: hex(MAT['[Concrete]'].rgb),
      bounds: flat(SLAB), area: (400 * 400 - 100 * 100) * IN * IN },
    { name: 'Tiles faces', tag: null, kind: 'loose', material: 'Tiles', texture: 'tiles.png',
      // openskp's writer stores white as a textured material's colour (SketchUp itself stores the
      // image's average there); the import takes the colour the file stores, so white is expected
      color: '#ffffff', bounds: flat(TILE_FACE), area: 50 * 50 * IN * IN },
    { name: 'Unpainted faces', tag: null, kind: 'loose', material: '', color: '#ffffff', bounds: flat(BARE), area: 50 * 50 * IN * IN }
  ],
  blocks: [
    { name: 'Chair', bounds: placedBox(CHAIR, [0, 0, 0]), area: boxArea(...CHAIR) },
    { name: 'Pane', bounds: flat([[0, 0, 0], [40, 0, 0], [40, 0, 60], [0, 0, 60]]), area: PANE[0] * PANE[1] * IN * IN },
    // the desk's top and its chair, in the desk's own frame
    { name: 'Desk', count: 2, bounds: flat([[-10, 0, 0], [40, 25, 40]]), area: boxArea(...TOP) + boxArea(...CHAIR) }
  ],
  textureAverage: hex([0, 1, 2].map((k) => Math.round((TILE_A[k] + TILE_B[k]) / 2)))
};
fs.writeFileSync(path.join(outDir, 'site_kit.expected.json'), JSON.stringify(expect, null, 1) + '\n');
console.log('wrote tests/skp/site_kit.skp (' + bytes.length + ' bytes, sha256 ' + expect.sha256 + ') and site_kit.expected.json');
