/* V206's work-order tests (docs/work-orders/v206/SPEC.md, WO-01 to WO-07): the pure functions of src/js/engine/io/ifc-review.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v206/v206.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v206/v206.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimTorMesh", "bimTorGuidValid", "bimTorGuidFromHex", "bimTorGuidToHex", "bimTorCompare", "bimTorArea", "bimTorClip"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/io/ifc-review.js'), 'utf8');
  if (process.env.V206_REF) src += fs.readFileSync(process.env.V206_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/io/ifc-review.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

// the IFC GUID: 128 bits as 22 characters of IFC's alphabet, big-endian, the first character carrying 2 bits;
// computed here independently with BigInt
const ALPHA = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$';
const ref = (hex) => { let n = BigInt('0x' + hex), s = ''; for (let i = 0; i < 22; i++) { s = ALPHA[Number(n % 64n)] + s; n /= 64n; } return s; };
test('WO-01 fragments\' geometry as the app\'s mesh: Z-up to Y-up, scaled', () => {
  const m = fn('bimTorMesh')(new Float32Array([1000, 2000, 3000, 0, 0, 0, 1000, 0, 0]), new Uint32Array([0, 1, 2]), 0.001);
  assert.deepEqual(m.v, [[1, 3, -2], [0, 0, 0], [1, 0, 0]]);
  assert.deepEqual(m.f, [[0, 1, 2]]);
  assert.ok(Object.is(m.v[1][2], 0), 'never -0');
  assert.equal(fn('bimTorMesh')([1, 2], [], 1), null);
});
test('WO-02 an IFC GUID is 22 characters of the alphabet, the first 0 to 3', () => {
  assert.equal(fn('bimTorGuidValid')('3$$$$$$$$$$$$$$$$$$$$$'), true);
  assert.equal(fn('bimTorGuidValid')('0000000000000000000000'), true);
  assert.equal(fn('bimTorGuidValid')('4000000000000000000000'), false);
  assert.equal(fn('bimTorGuidValid')('000000000000000000000'), false);
  assert.equal(fn('bimTorGuidValid')('00000000000000000000-0'), false);
});
test('WO-03 a UUID in hex to the IFC GUID', () => {
  for (const h of ['00000000000000000000000000000000', 'ffffffffffffffffffffffffffffffff', '0123456789abcdef0fedcba987654321', '7c9e6679742540de944be07fc1f90ae7']) assert.equal(fn('bimTorGuidFromHex')(h), ref(h), h);
  assert.equal(fn('bimTorGuidFromHex')('7c9e6679-7425-40de-944b-e07fc1f90ae7'), ref('7c9e6679742540de944be07fc1f90ae7'));
  assert.equal(fn('bimTorGuidFromHex')('xyz'), null);
});
test('WO-04 and back: the GUID to hex', () => {
  const h = '0123456789abcdef0fedcba987654321';
  assert.equal(fn('bimTorGuidToHex')(ref(h)), h);
  assert.equal(fn('bimTorGuidToHex')('not a guid'), null);
});
test('WO-05 two imports compared class by class (That Open against V196)', () => {
  assert.deepEqual(fn('bimTorCompare')({ IfcWall: 4, IfcSlab: 2, IfcDoor: 1 }, { IfcWall: 4, IfcSlab: 3, IfcWindow: 2 }),
    { same: ['IfcWall'], diff: [{ cls: 'IfcDoor', a: 1, b: 0 }, { cls: 'IfcSlab', a: 2, b: 3 }, { cls: 'IfcWindow', a: 0, b: 2 }] });
});
test('WO-06 a planar polygon\'s area in 3D', () => {
  near(fn('bimTorArea')([[0, 0, 0], [4, 0, 0], [4, 3, 3], [0, 3, 3]]), 4 * Math.hypot(3, 3), 1e-12);
  assert.equal(fn('bimTorArea')([]), 0);
});
test('WO-07 which side of a clipping plane', () => {
  const pl = { p: [0, 1, 0], n: [0, 1, 0] };
  assert.equal(fn('bimTorClip')([5, 2, 5], pl), true);
  assert.equal(fn('bimTorClip')([5, 1, 5], pl), false, 'on the plane is kept');
});
