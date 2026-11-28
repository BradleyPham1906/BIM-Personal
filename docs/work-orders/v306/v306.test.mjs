/* V306's work-order tests (docs/work-orders/v306/SPEC.md): the pure functions of src/js/engine/bim/ifc-class.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v306/v306.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v306/v306.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. The predefined type lists are
   checked against IFC4's enumerations as web-ifc's schema has them
   (docs/research/experiments/thatopen-gap/ifc4-predefined.json, made by ifc4-predefined.cjs), not against a copy. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimIfcRoofPredefined', 'bimIfcPredefinedOptions', 'bimIfcPredefinedValid', 'bimIfcClassOf'];
function strip(t) { return t.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n'); }
function load() {
  let src = strip(fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/ifc-class.js'), 'utf8'));
  if (process.env.V306_REF) src += fs.readFileSync(process.env.V306_REF, 'utf8');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/bim/ifc-class.js'); return X[n]; };
const IFC4 = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/research/experiments/thatopen-gap/ifc4-predefined.json'), 'utf8')).enums;

test('WO-01 a roof\'s predefined type from its style and pitch', () => {
  const f = fn('bimIfcRoofPredefined');
  assert.equal(f('shed', 20), 'SHED_ROOF');
  assert.equal(f('gable', 35), 'GABLE_ROOF');
  assert.equal(f('hip', 30), 'HIP_ROOF');
  assert.equal(f('shed', 0), 'FLAT_ROOF', 'under half a degree is flat, whatever the style');
  assert.equal(f('gable', 0.49), 'FLAT_ROOF');
  assert.equal(f('hip', -0.2), 'FLAT_ROOF');
  assert.equal(f('shed', 0.5), 'SHED_ROOF', 'half a degree is not flat');
  assert.equal(f('dome', 10), 'NOTDEFINED');
  assert.equal(f(undefined, 10), 'NOTDEFINED');
  assert.equal(f('gable', undefined), 'GABLE_ROOF', 'no pitch: the style decides');
  assert.equal(f('gable', 'x'), 'GABLE_ROOF');
});

test('WO-02 the predefined types of each class are IFC4\'s, as web-ifc\'s schema lists them', () => {
  const f = fn('bimIfcPredefinedOptions');
  assert.equal(Object.keys(IFC4).length, 12);
  for (const cls of Object.keys(IFC4)) assert.deepEqual(f(cls), IFC4[cls], cls);
  const a = f('IfcWall');
  a.push('MINE');
  assert.deepEqual(f('IfcWall'), IFC4.IfcWall, 'a copy: changing it changes nothing');
  assert.deepEqual(f('IfcCurtainWall'), []);
  assert.deepEqual(f(''), []);
  assert.deepEqual(f(null), []);
});

test('WO-03 a predefined type is valid for its class', () => {
  const f = fn('bimIfcPredefinedValid');
  assert.equal(f('IfcWall', 'SHEAR'), true);
  assert.equal(f('IfcWall', 'FLOOR'), false);
  assert.equal(f('IfcSlab', 'FLOOR'), true);
  assert.equal(f('IfcSlab', 'floor'), false, 'case matters, as in the schema');
  assert.equal(f('IfcRoof', 'HIP_ROOF'), true);
  assert.equal(f('IfcDoor', 'NOTDEFINED'), true);
  assert.equal(f('IfcCurtainWall', 'NOTDEFINED'), false, 'a class without a list');
  assert.equal(f('IfcWall', ''), false);
  assert.equal(f('IfcWall', null), false);
});

test('WO-04 each element\'s IFC class and predefined type', () => {
  const f = fn('bimIfcClassOf');
  const of = (t, bim) => f({ t: t || 'solid', bim });
  assert.deepEqual(of('solid', { type: 'wall' }), { cls: 'IfcWall', predefined: 'STANDARD' });
  assert.deepEqual(of('solid', { type: 'floor' }), { cls: 'IfcSlab', predefined: 'FLOOR' });
  assert.deepEqual(of('solid', { type: 'ceiling' }), { cls: 'IfcCovering', predefined: 'CEILING' });
  assert.deepEqual(of('solid', { type: 'column' }), { cls: 'IfcColumn', predefined: 'COLUMN' });
  assert.deepEqual(of('solid', { type: 'beam' }), { cls: 'IfcBeam', predefined: 'BEAM' });
  assert.deepEqual(of('solid', { type: 'footing' }), { cls: 'IfcFooting', predefined: 'PAD_FOOTING' });
  assert.deepEqual(of('solid', { type: 'stripfooting' }), { cls: 'IfcFooting', predefined: 'STRIP_FOOTING' });
  assert.deepEqual(of('solid', { type: 'stair' }), { cls: 'IfcStair', predefined: 'NOTDEFINED' });
  assert.deepEqual(of('opening', { type: 'door' }), { cls: 'IfcDoor', predefined: 'DOOR' });
  assert.deepEqual(of('opening', { type: 'window' }), { cls: 'IfcWindow', predefined: 'WINDOW' });
  assert.deepEqual(f({ t: 'room' }), { cls: 'IfcSpace', predefined: 'SPACE' }, 'rooms have no bim record');
  assert.deepEqual(of('solid', { type: 'roof', style: 'hip', pitch: 30 }), { cls: 'IfcRoof', predefined: 'HIP_ROOF' });
  assert.deepEqual(of('solid', { type: 'roof', style: 'shed', pitch: 0 }), { cls: 'IfcRoof', predefined: 'FLAT_ROOF' });
  // the element's own predefined type, when valid for its class, overrides the default (the instance overrides)
  assert.deepEqual(of('solid', { type: 'wall', ifc: { predefined: 'SHEAR' } }), { cls: 'IfcWall', predefined: 'SHEAR' });
  assert.deepEqual(of('solid', { type: 'wall', ifc: { predefined: 'FLOOR' } }), { cls: 'IfcWall', predefined: 'STANDARD' }, 'not valid for IfcWall: the default');
  assert.deepEqual(of('solid', { type: 'roof', style: 'gable', pitch: 40, ifc: { predefined: 'MANSARD_ROOF' } }), { cls: 'IfcRoof', predefined: 'MANSARD_ROOF' });
  // the element's own class: its predefined type when valid for that class, else NOTDEFINED
  assert.deepEqual(of('solid', { type: 'wall', ifc: { cls: 'IfcBuildingElementProxy', predefined: 'COMPLEX' } }), { cls: 'IfcBuildingElementProxy', predefined: 'COMPLEX' });
  assert.deepEqual(of('solid', { type: 'floor', ifc: { cls: 'IfcSlab', predefined: 'LANDING' } }), { cls: 'IfcSlab', predefined: 'LANDING' });
  assert.deepEqual(of('solid', { type: 'floor', ifc: { cls: 'IfcCurtainWall', predefined: 'X' } }), { cls: 'IfcCurtainWall', predefined: 'NOTDEFINED' });
  assert.deepEqual(of('solid', { type: 'floor', ifc: { cls: '' } }), { cls: 'IfcSlab', predefined: 'FLOOR' }, 'an empty class is no class');
  // an imported element keeps its file's class
  assert.deepEqual(of('solid', { type: 'ifc', ifcType: 'IfcCurtainWall', guid: '3ZYW59sxj8lei475l7EhLU' }), { cls: 'IfcCurtainWall', predefined: 'NOTDEFINED' });
  // anything else is a proxy
  assert.deepEqual(of('solid', { type: 'mass' }), { cls: 'IfcBuildingElementProxy', predefined: 'NOTDEFINED' });
  assert.deepEqual(f({ t: 'solid' }), { cls: 'IfcBuildingElementProxy', predefined: 'NOTDEFINED' });
  assert.equal(f(null), null);
});
