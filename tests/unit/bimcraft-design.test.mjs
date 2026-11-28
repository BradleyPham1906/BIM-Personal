// V308: Design (bim/bimcraft-design.js), the app's side of BimCraft's authoring core: the pure helpers, and the loader's
// pin against runtime/MANIFEST.json and vendor/bimcraft.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

test('the building starts on the app\'s levels: count, floor-to-floor height in mm, names in elevation order', () => {
  assert.deepEqual(E.bimDsnLevelsSpec([{ name: 'Level 1', elev: 3.2, height: 3.2 }, { name: 'Level 0', elev: 0, height: 3.2 }]),
    { count: 2, height: 3200, names: ['Level 0', 'Level 1'] });
  assert.deepEqual(E.bimDsnLevelsSpec([{ name: 'Ground', elev: 0 }]), { count: 1, height: 3000, names: ['Ground'] }, 'no height: 3000 mm');
  assert.deepEqual(E.bimDsnLevelsSpec([]), { count: 1, height: 3000, names: ['Ground floor'] });
  assert.deepEqual(E.bimDsnLevelsSpec(null), { count: 1, height: 3000, names: ['Ground floor'] });
});

test('the wall tool\'s clicks as segments: a double-click\'s repeat dropped, a ring closed on its first corner', () => {
  assert.deepEqual(E.bimDsnWallSegs([[0, 0], [5000, 0], [5000, 0], [5000, 3000]], 1),
    [{ a: [0, 0], b: [5000, 0] }, { a: [5000, 0], b: [5000, 3000] }]);
  // a fourth click 40 mm from the first closes the ring exactly on it
  assert.deepEqual(E.bimDsnWallSegs([[0, 0], [4000, 0], [4000, 3000], [0, 3000], [40, 30]], 1),
    [{ a: [0, 0], b: [4000, 0] }, { a: [4000, 0], b: [4000, 3000] }, { a: [4000, 3000], b: [0, 3000] }, { a: [0, 3000], b: [0, 0] }]);
  assert.deepEqual(E.bimDsnWallSegs([[0, 0]], 1), [], 'one corner is no wall');
  assert.deepEqual(E.bimDsnWallSegs([[0, 0], [NaN, 1], [2000, 0]], 1), [{ a: [0, 0], b: [2000, 0] }], 'a bad point is skipped');
  assert.deepEqual(E.bimDsnWallSegs(null, 1), []);
});

test('a click on the plan finds the nearest wall within reach, and where along it', () => {
  const walls = [{ guid: 'S', a: [0, 0], b: [10000, 0] }, { guid: 'P', a: [5000, 0], b: [5000, 7000] }];
  const s = E.bimDsnWallAt(walls, [2500, 120], 600);
  assert.equal(s.guid, 'S'); assert.equal(s.offset, 2500); assert.equal(s.d, 120);
  const p = E.bimDsnWallAt(walls, [5080, 3500], 600);
  assert.equal(p.guid, 'P'); assert.equal(p.offset, 3500);
  assert.equal(E.bimDsnWallAt(walls, [2500, 2000], 600), null, 'too far from every wall');
  assert.equal(E.bimDsnWallAt(walls, [-300, 0], 600).offset, 0, 'beyond an end: the end');
  assert.equal(E.bimDsnWallAt([{ guid: 'Z', a: [1, 1], b: [1, 1] }], [1, 1], 600), null, 'a wall of no length is no wall');
});

test('section lines are named A to Z, then AA, after the names in use', () => {
  assert.equal(E.bimDsnNextSection([]), 'A');
  assert.equal(E.bimDsnNextSection(['A', 'B']), 'C');
  assert.equal(E.bimDsnNextSection(['A', 'C']), 'B');
  assert.equal(E.bimDsnNextSection('ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')), 'AA');
});

test('the design engine is pinned: the loader checks runtime/MANIFEST.json\'s hash; the vendored copy is BimCraft @ the same revision', () => {
  const man = JSON.parse(fs.readFileSync(path.join(ROOT, 'runtime/MANIFEST.json'), 'utf8'));
  const m = man.files.find((f) => f.path === E.BIM_CRAFT.dir + E.BIM_CRAFT.file);
  assert.ok(m, 'pinned');
  assert.equal(E.BIM_CRAFT.sri, 'sha256-' + Buffer.from(m.sha256, 'hex').toString('base64'));
  assert.equal(man.bimcraft, E.BIM_CRAFT.rev);
  assert.match(fs.readFileSync(path.join(ROOT, 'vendor/bimcraft/FILES.txt'), 'utf8'), new RegExp('^# BimCraft @ ' + E.BIM_CRAFT.rev));
  assert.deepEqual(E.bimDsnSources('https:', 'https://x/runtime/'), [{ u: 'https://x/runtime/bimcraft/' + E.BIM_CRAFT.rev + '/bim-craft.min.js', sri: true }]);
  assert.equal(E.bimDsnSources('file:', 'https://x/runtime/')[0].sri, false, 'beside a copy on a disk first');
});
