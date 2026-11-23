// V268: material cards (engine/assets/material-cards.js): FreeCAD's .FCMat read and written, units, the library
// with the project's own cards.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
// the shape of FreeCAD 1.0's cards (src/Mod/Material/Resources/Materials), values of our own
const FC10 = `---
# File created by ConvertFCMat.py
General:
  UUID: "11111111-2222-4333-8444-555555555555"
  Name: "Test Alloy"
  Description: "a test card"
Models:
  Father:
    UUID: '9cdda8b6-b606-4778-8f13-3934d8668e67'
    Father: "Metal"
  LinearElastic:
    UUID: '7b561d1d-fb9b-44f6-9da9-56a4f74d7536'
    Density: "2700 kg/m^3"
    PoissonRatio: "0.3"
    UltimateTensileStrength: "250 MPa"
    YieldStrength: "180 MPa"
    YoungsModulus: "70000 MPa"
  Thermal:
    UUID: '9959d007-a970-4ea7-bae4-3eb1b8b883c7'
    SpecificHeat: "900 J/kg/K"
    ThermalConductivity: "150 W/m/K"
    ThermalExpansionCoefficient: "23 µm/m/K"
AppearanceModels:
  BasicRendering:
    UUID: 'f006c7e4-35b7-43d5-bbf9-c5d572309e6e'
    DiffuseColor: "(1.0000, 0.5000, 0.0000, 1.0)"
    Transparency: "0.25"
`;

test('a FreeCAD 1.0 card is read with its units into the app\'s', () => {
  const c = E.bimFcmatParse(FC10);
  assert.equal(c.name, 'Test Alloy');
  assert.equal(c.kind, 'Metal');
  assert.equal(c.density, 2700);
  assert.equal(c.youngsModulus, '70 GPa');
  assert.equal(c.poissonRatio, 0.3);
  assert.equal(c.yieldStrength, 180);
  assert.equal(c.tensileStrength, 250);
  assert.equal(c.conductivity, 150);
  assert.equal(c.specificHeat, 900);
  assert.equal(c.expansion, 23);
  assert.equal(c.color, '#ff8000');
  assert.equal(c.transparency, 0.25);
});

test('an older INI card and other units', () => {
  const c = E.bimFcmatParse('; Steel\n[General]\nName = Old Steel\n[Mechanical]\nDensity = 7.85 g/cm^3\nYoungsModulus = 210 GPa\n' +
    '[Thermal]\nThermalExpansionCoefficient = 0.000012 m/m/K\nSpecificHeat = 0.46 kJ/kg/K\n');
  assert.equal(c.name, 'Old Steel');
  assert.equal(c.density, 7850);
  assert.equal(c.youngsModulus, '210 GPa');
  assert.ok(Math.abs(c.expansion - 12) < 1e-9);
  assert.ok(Math.abs(c.specificHeat - 460) < 1e-9);
  assert.ok(E.bimFcmatParse('Density = 1').error, 'a card needs a name');
});

test('written and read back, a card is the same', () => {
  const card = E.bimMatCardValid({ name: 'Brick "red"', kind: 'Masonry', density: '1800', youngsModulus: '5', poissonRatio: '0.2', conductivity: '0.77', color: '#aa4422', transparency: '0' });
  assert.equal(card.youngsModulus, '5 GPa');
  const text = E.bimFcmatWrite(card, 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee');
  assert.match(text, /LinearElastic:\n {4}UUID: '7b561d1d-fb9b-44f6-9da9-56a4f74d7536'/);
  assert.match(text, /Thermal:\n {4}UUID: '9959d007-a970-4ea7-bae4-3eb1b8b883c7'/);
  const back = E.bimFcmatParse(text);
  for (const k of ['name', 'kind', 'density', 'youngsModulus', 'poissonRatio', 'conductivity', 'color']) assert.equal(back[k], card[k], k);
});

test('a card typed by the user is checked', () => {
  assert.ok(E.bimMatCardValid({ name: ' ' }).error);
  assert.ok(E.bimMatCardValid({ name: 'X', density: '-3' }).error);
  assert.ok(E.bimMatCardValid({ name: 'X', poissonRatio: '0.6' }).error);
  assert.deepEqual(E.bimMatCardsValid([{ name: 'A' }, { name: 'A' }, null, { name: 'B', density: 5 }]).map((c) => c.name), ['A', 'B']);
});

test('the library: built-ins with FreeCAD\'s generic additions, then the project\'s cards, which stand in for a built-in of their name', () => {
  const built = [{ name: 'Steel', kind: 'Metal', density: 7900, hatch: { angle: 45, gap: 9 } }, { name: 'Wood', kind: 'Organic', density: 700 }];
  const proj = [{ name: 'Wood', kind: 'Organic', density: 450, custom: true }, { name: 'Cork', kind: 'Organic', density: 120, custom: true }];
  const L = E.bimMatLibrary(built, proj);
  assert.deepEqual(L.map((c) => c.name), ['Steel', 'Wood', 'Cork']);
  assert.equal(L[0].conductivity, 50);
  assert.equal(L[1].density, 450);
  assert.equal(built[0].conductivity, undefined, 'the built-in array is not changed');
});
