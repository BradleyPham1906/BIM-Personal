// V173d: McHarg's layer cake (map/layer-cake.js), the owner's D13: the shown data layers, then the site
// analysis layers, each lifted to its own height; the lift reaches every analysis point through bimDgW.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const A3D = E.A3D;
globalThis.document.querySelector = () => null;   // no Layers panel: the stand-in's element loops in bimRenderInto

function setup() {
  A3D.site = { name: 'Site', context: { radius: 250 } };
  A3D.site.dataLayers = [
    { id: 'd1', name: 'Parcels', kind: 'geojson', url: 'u1', color: '#3366ff', visible: true, credit: 'x' },
    { id: 'd2', name: 'Hidden', kind: 'geojson', url: 'u2', color: '#3366ff', visible: false, credit: 'x' }];
  A3D.layers = [{ id: 'L0', name: 'Model', visible: true }, { id: 'Ls', name: 'Site analysis - Slope', visible: true }, { id: 'Le', name: 'Site analysis - Empty', visible: true }];
  A3D.objs = [{ id: 'g1', t: 'diag', layer: 'Ls', pos: [0, 0, 0], dg: { a: 'slope', g: {} } }];
}

test('off: nothing is lifted', () => {
  setup();
  E.A3D_CAKE.on = false;
  assert.deepEqual(E.bimCakeTiers(), []);
  assert.equal(E.bimCakeLift('data', 'd1'), 0);
});

test('on: shown data layers, then analysis layers holding an analysis, a fifth of the radius apart', () => {
  setup();
  assert.ok(E.bimIsDiag(A3D.objs[0]));
  E.bimCakeSet(true);
  const T = E.bimCakeTiers();
  assert.deepEqual(T.map((t) => [t.kind, t.id, t.name, t.lift]), [['data', 'd1', 'Parcels', 50], ['analysis', 'Ls', 'Slope', 100]]);
  A3D.frames = (A3D.frames || 0) + 1;
  assert.equal(E.bimCakeLift('data', 'd1'), 50);
  assert.equal(E.bimCakeLift('data', 'd2'), 0);
  assert.equal(E.bimDgW(A3D.objs[0], [1, 2, 3])[1] - E.bimDgW({ ...A3D.objs[0], layer: 'L0' }, [1, 2, 3])[1], 100);
  E.bimCakeSet(false);
  assert.equal(E.bimCakeLift('data', 'd1'), 0);
});

test('the gap is held to 10 to 200 m', () => {
  setup();
  E.A3D_CAKE.on = true; E.A3D_CAKE.memo = null;
  A3D.site.dataLayers[1].visible = true;
  A3D.site.context.radius = 50;
  assert.deepEqual(E.bimCakeTiers().filter((t) => t.kind === 'data').map((t) => t.lift), [10, 20]);
  A3D.site.context.radius = 1000;
  assert.deepEqual(E.bimCakeTiers().filter((t) => t.kind === 'data').map((t) => t.lift), [200, 400]);
  E.A3D_CAKE.on = false;
});

test('the toggle in the Layers header says whether it is on', () => {
  E.A3D_CAKE.on = false;
  assert.match(E.bimCakeBtnHtml(), /aria-pressed="false"/);
  E.A3D_CAKE.on = true;
  assert.match(E.bimCakeBtnHtml(), /class="a3d-lycake on"/);
  E.A3D_CAKE.on = false;
});
