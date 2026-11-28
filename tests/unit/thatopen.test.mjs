// V206: That Open's data as the IFC import's (io/ifc-review.js, the pure part of io/thatopen-runtime.js), the GlobalId
// codec without BigInt, and the loader's pins against runtime/MANIFEST.json.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

test('GlobalIds: hex to the 22 characters and back, without BigInt', () => {
  assert.equal(E.bimTorGuidFromHex('00000000000000000000000000000000'), '0000000000000000000000');
  assert.equal(E.bimTorGuidFromHex('ffffffff-ffff-ffff-ffff-ffffffffffff'), '3$$$$$$$$$$$$$$$$$$$$$');
  // a GlobalId from a real file (e02: the wall of wall-with-opening-and-window.ifc) survives the round trip
  const g = '3ZYW59sxj8lei475l7EhLU', h = E.bimTorGuidToHex(g);
  assert.match(h, /^[0-9a-f]{32}$/);
  assert.equal(E.bimTorGuidFromHex(h), g);
  assert.equal(E.bimTorGuidFromHex(h.toUpperCase()), g, 'any case');
  for (let i = 0; i < 200; i++) {
    let x = ''; for (let k = 0; k < 32; k++) x += '0123456789abcdef'[(i * 7 + k * 13 + (i >> 2) * k) % 16];
    assert.equal(E.bimTorGuidToHex(E.bimTorGuidFromHex(x)), x);
  }
  assert.equal(E.bimTorGuidFromHex('xyz'), null);
  assert.equal(E.bimTorGuidToHex('4$$$$$$$$$$$$$$$$$$$$$'), null, 'the first character is 0 to 3');
  const src = fs.readFileSync(path.join(ROOT, 'src/js/engine/io/ifc-review.js'), 'utf8');
  assert.doesNotMatch(src.replace(/\/\*[\s\S]*?\*\//g, ''), /BigInt\s*\(|\b\d+n\b/, 'ES5: no BigInt in the engine');
});

test('That Open values: {value, type} unwrapped as text', () => {
  assert.equal(E.bimToeVal({ value: 'Wall', type: 'IFCLABEL' }), 'Wall');
  assert.equal(E.bimToeVal({ value: 0.24, type: 'IFCTHERMALTRANSMITTANCEMEASURE' }), '0.24');
  assert.equal(E.bimToeVal({ value: false, type: 'IFCBOOLEAN' }), 'No');
  assert.equal(E.bimToeVal([{ value: 1 }, { value: 2.5 }]), '1, 2.5');
  assert.equal(E.bimToeVal(1 / 3), '0.333333');
  assert.equal(E.bimToeVal(null), '');
  assert.equal(E.bimToeVal({ value: 'a\n  b' }), 'a b');
  // ids are never formatted (e03, schependomlaan: 1007971 shown as 1.00797e+6 lost 195 elements' data)
  assert.equal(E.bimToeRaw({ value: 1007971 }), 1007971);
  assert.equal(E.bimToeRaw(1008267), 1008267);
  assert.equal(E.bimToeRaw(null), null);
  assert.notEqual(E.bimToeRaw({ value: 1007971 }), E.bimToeRaw({ value: 1007972 }), 'neighbouring large ids stay apart');
});

test('the length unit is read from the unit assignment IfcProject names', () => {
  const head = (units, extra = '') =>
    "ISO-10303-21;\nDATA;\n#1=IFCPROJECT('x',$,'P',$,$,$,$,(#20),#9);\n" + extra +
    "#9=IFCUNITASSIGNMENT((" + units + "));\n#10=IFCSIUNIT(*,.LENGTHUNIT.,.MILLI.,.METRE.);\n" +
    "#11=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);\n#12=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);\n" +
    "#13=IFCCONVERSIONBASEDUNIT(#14,.LENGTHUNIT.,'FOOT',#15);\nENDSEC;";
  assert.equal(E.bimToeUnit(head('#12,#10')), 0.001);
  assert.equal(E.bimToeUnit(head('#12,#11')), 1);
  assert.equal(E.bimToeUnit(head('#12,#13')), 0.3048);
  // a second assignment that IfcProject does not name is not used
  assert.equal(E.bimToeUnit(head('#11', "#8=IFCUNITASSIGNMENT((#10));\n")), 1);
  assert.equal(E.bimToeUnit(''), 1);
  assert.equal(E.bimToeUnit("#1= IFCSIUNIT(*,.LENGTHUNIT.,.CENTI.,.METRE.);\n#2= IFCUNITASSIGNMENT((#1));"), 0.01);
});

test('the spatial tree: storeys, what each holds, each item\'s class', () => {
  // the shape e02 measured: category nodes and item nodes alternate
  const item = (id, kids = []) => ({ category: null, localId: id, children: kids });
  const cat = (c, kids) => ({ category: c, localId: null, children: kids });
  const root = cat('IFCPROJECT', [item(1, [cat('IFCSITE', [item(2, [cat('IFCBUILDING', [item(3, [
    cat('IFCBUILDINGSTOREY', [item(10, [cat('IFCWALL', [item(100), item(101)]), cat('IFCSPACE', [item(110, [cat('IFCFURNITURE', [item(111)])])])]),
      item(20, [cat('IFCSLAB', [item(200)])])])])])])])])]);
  const t = E.bimToeTree(root);
  assert.deepEqual(t.storeys, [10, 20]);
  assert.equal(t.holder[100], 10);
  assert.equal(t.holder[101], 10);
  assert.equal(t.holder[111], 10, 'a space inside a storey: the storey holds its contents');
  assert.equal(t.holder[200], 20);
  assert.equal(t.holder[3], undefined, 'above the storeys: no holder');
  assert.equal(t.cats[100], 'IFCWALL');
  assert.equal(t.cats[10], 'IFCBUILDINGSTOREY');
  assert.equal(t.cats[110], 'IFCSPACE');
  // a space with no storey above it holds its contents (an infrastructure file, e02's bridge: no storeys)
  const t2 = E.bimToeTree(cat('IFCSPACE', [item(5, [cat('IFCDOOR', [item(6)])])]));
  assert.equal(t2.holder[6], 5);
  assert.deepEqual(E.bimToeTree(null).storeys, []);
});

test('property and quantity sets as named rows', () => {
  const it = { IsDefinedBy: [
    { Name: { value: 'Pset_WallCommon' }, HasProperties: [
      { Name: { value: 'IsExternal' }, NominalValue: { value: true, type: 'IFCBOOLEAN' } },
      { Name: { value: 'ThermalTransmittance' }, NominalValue: { value: 0.24 } },
      { Name: { value: 'Status' }, EnumerationValues: [{ value: 'NEW' }] },
      { NominalValue: { value: 1 } }] },
    { Name: { value: 'Qto_WallBaseQuantities' }, Quantities: [
      { Name: { value: 'Length' }, LengthValue: { value: 3 } }, { Name: { value: 'NetVolume' }, VolumeValue: { value: 1.5 } }] },
    { Name: { value: 'Empty' }, HasProperties: [] }] };
  assert.deepEqual(E.bimToeSets(it), [
    { name: 'Pset_WallCommon', rows: [['IsExternal', 'Yes'], ['ThermalTransmittance', '0.24'], ['Status', 'NEW']] },
    { name: 'Qto_WallBaseQuantities', rows: [['Length', '3'], ['NetVolume', '1.5']] }]);
  assert.deepEqual(E.bimToeSets({}), []);
});

test('an item\'s parts as one mesh, each moved by its column-major transform', () => {
  // e02's wall: local z becomes world y (the transform That Open gave), then moved by (-0.5, -0.5, -0.15)
  const tr = [1, 0, 0, 0, 0, 0, -1, 0, 0, 1, 0, 0, -0.5, -0.5, -0.15, 1];
  const r = E.bimToeMesh([
    { positions: new Float32Array([0, 0, 0, 1, 0, 0, 0, 0, 2]), indices: new Uint16Array([0, 1, 2]), transform: { elements: tr } },
    { positions: new Float32Array([0, 0, 0]), indices: new Uint16Array([]), transform: tr },
    { positions: new Float32Array([5, 5, 5, 6, 5, 5, 5, 6, 5]), indices: new Uint16Array([0, 1, 2]) }]);
  assert.deepEqual(r.pos.map((x) => +x.toFixed(6)), [-0.5, -0.5, -0.15, 0.5, -0.5, -0.15, -0.5, 1.5, -0.15, 5, 5, 5, 6, 5, 5, 5, 6, 5]);
  assert.deepEqual(r.idx, [0, 1, 2, 3, 4, 5], 'the part without triangles is left out and the indices follow on');
  assert.deepEqual(E.bimToeMesh(null), { pos: [], idx: [] });
});

test('colours and opacity per item, from the material definitions', () => {
  // That Open's colours are linear; the app's are sRGB (the file's): 0.291771 linear is 0x93 = 147 in sRGB, cc-ifc's value
  assert.equal(E.bimToeHex({ r: 1, g: 0, b: 0 }), '#ff0000');
  assert.equal(E.bimToeHex({ r: 0.291771, g: 0.291771, b: 0.291771 }), '#939393');
  assert.equal(E.bimToeHex({ r: 0.215861, g: 0.502886, b: 0.001518 }), '#80bc05', 'the linear segment near black');
  assert.equal(E.bimToeHex(null), '#b8b8b0');
  const L = E.bimToeLook([
    { localIds: [1, 2], definition: { color: { r: 1, g: 1, b: 1 }, opacity: 1 } },
    { localIds: [2], definition: { color: { r: 0, g: 0.5, b: 0 }, opacity: 0.2 } },
    { localIds: [3], definition: { color: { r: 0, g: 0, b: 1 }, opacity: 0.4 } }]);
  assert.deepEqual(L[1], { col: '#ffffff', opacity: 1 });
  assert.equal(L[2].col, '#ffffff', 'the opaque material gives the colour');
  assert.ok(Math.abs(L[2].opacity - 0.6) < 1e-9, 'the mean of 1 and 0.2');
  assert.deepEqual(L[3], { col: '#0000ff', opacity: 0.4 }, 'all see-through: the first colour');
});

test('the loader\'s pins are runtime/MANIFEST.json\'s, and every file is there', () => {
  const man = JSON.parse(fs.readFileSync(path.join(ROOT, 'runtime/MANIFEST.json'), 'utf8'));
  assert.equal(man.thatopen, E.BIM_TOE.ver);
  for (const f of E.BIM_TOE.files) {
    const m = man.files.find((x) => x.path === E.BIM_TOE.dir + f.f);
    assert.ok(m, f.f + ' is pinned');
    assert.equal(f.sri, 'sha256-' + Buffer.from(m.sha256, 'hex').toString('base64'), f.f + ': the loader checks the pinned hash');
  }
  assert.deepEqual(E.bimToeSources('file:', 'https://x/runtime/', E.BIM_TOE.files[0]).map((s) => s.sri), [false, true]);
  assert.deepEqual(E.bimToeSources('https:', 'https://x/runtime/', E.BIM_TOE.files[0]),
    [{ u: 'https://x/runtime/thatopen/3.6.0/bim-webifc.min.js', sri: true }]);
});

test('class names in the schema\'s spelling, from web-ifc\'s class lists', () => {
  const lists = [['IfcWall', 'IfcRoadPart'], ['IfcWall', 'IfcWallStandardCase', 'IfcBuildingElementProxy']];
  assert.equal(E.bimToeClassName('IFCWALLSTANDARDCASE', lists), 'IfcWallStandardCase');
  assert.equal(E.bimToeClassName('IFCROADPART', lists), 'IfcRoadPart');
  assert.equal(E.bimToeClassName('ifcbuildingelementproxy', lists), 'IfcBuildingElementProxy', 'any case');
  assert.equal(E.bimToeClassName('IFCWALL', lists), 'IfcWall');
  assert.equal(E.bimToeClassName('IFCUNKNOWNTHING', lists), 'IfcUnknownthing', 'not in the lists: a guess');
  assert.equal(E.bimToeClassName('', lists), 'IfcProduct');
});

test('the Review tree: each storey\'s classes, and what no storey holds', () => {
  const item = (id, kids = []) => ({ category: null, localId: id, children: kids });
  const cat = (c, kids) => ({ category: c, localId: null, children: kids });
  const root = cat('IFCPROJECT', [item(1, [cat('IFCSITE', [item(2, [cat('IFCGEOGRAPHICELEMENT', [item(9)]), cat('IFCBUILDING', [item(3, [
    cat('IFCBUILDINGSTOREY', [item(10, [cat('IFCWALL', [item(101), item(100)]), cat('IFCSPACE', [item(110, [cat('IFCFURNITURE', [item(111)])])])]),
      item(20, [cat('IFCSLAB', [item(200)])])])])])])])])]);
  assert.deepEqual(E.bimToeStoreyClasses(root), [
    { storey: 10, classes: { IFCWALL: [100, 101], IFCSPACE: [110], IFCFURNITURE: [111] } },
    { storey: 20, classes: { IFCSLAB: [200] } },
    { storey: null, classes: { IFCGEOGRAPHICELEMENT: [9] } }]);
  assert.deepEqual(E.bimToeStoreyClasses(cat('IFCPROJECT', [item(1)])), [], 'nothing but spatial elements: no rows');
});

test('an item\'s colour by cc-ifc\'s rule: the opaque material over most triangles; opacity weighted by triangles', () => {
  const tri = (n) => ({ length: 3 * n });
  const mats = { 1: { r: 200, g: 100, b: 50, a: 255 }, 2: { r: 0, g: 128, b: 255, a: 51 }, 3: { r: 10, g: 10, b: 10, a: 255 } };
  const sm = { 11: 1, 12: 2, 13: 3 };
  // a window: frame (opaque, 10 triangles), glass (20 percent, 30 triangles), handle (opaque, 2)
  const w = E.bimToePartsLook([{ sampleId: 11, indices: tri(10) }, { sampleId: 12, indices: tri(30) }, { sampleId: 13, indices: tri(2) }], sm, mats);
  assert.equal(w.col, '#c86432', 'the opaque material over most triangles, not the glass');
  assert.ok(Math.abs(w.opacity - (10 + 30 * 0.2 + 2) / 42) < 1e-9);
  // all see-through: the one over most triangles
  const g = E.bimToePartsLook([{ sampleId: 12, indices: tri(4) }], sm, mats);
  assert.equal(g.col, '#0080ff');
  assert.ok(Math.abs(g.opacity - 0.2) < 1e-9);
  // the same material in two parts adds up
  const t = E.bimToePartsLook([{ sampleId: 13, indices: tri(3) }, { sampleId: 11, indices: tri(4) }, { sampleId: 13, indices: tri(3) }], sm, mats);
  assert.equal(t.col, '#0a0a0a');
  // nothing known: null, so the definitions are used
  assert.equal(E.bimToePartsLook([{ sampleId: 99, indices: tri(3) }], sm, mats), null);
  assert.equal(E.bimToePartsLook([], sm, mats), null);
  assert.equal(E.bimToePartsLook(null, null, null), null);
});
