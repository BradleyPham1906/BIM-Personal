// V173c: the Layers tab listed by drawing order, source or selection (layers/list-by.js), with the owner's
// D1 (List by in the Layers tab), D2 (reorder within a kind) and D3 (a data layer's top row draws on top).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const A3D = E.A3D;
globalThis.document.querySelector = () => null;   // no Layers panel: the stand-in's element loops in bimRenderInto

function setup() {
  A3D.site = A3D.site || { name: 'Site' };
  A3D.site.dataLayers = [
    { id: 'd1', name: 'Parcels', kind: 'geojson', url: 'https://data.example.org/a.geojson', color: '#3366ff', visible: true, credit: 'x' },
    { id: 'd2', name: 'Zoning', kind: 'arcgis', url: 'https://maps.example.com/FeatureServer/0', color: '#33aa66', visible: true, credit: 'y', status: { error: 'The server said 500' } },
    { id: 'd3', name: 'Trees', kind: 'geojson', url: 'https://data.example.org/t.geojson', color: '#aa3366', visible: true, credit: 'x' }];
  A3D.dataFeatures = {};
  A3D.resultLayers = [];
}
const order = (h, re) => [...h.matchAll(re)].map((m) => m[1]);

test('drawing order: the data layers listed top-first, the last stored at the top (D3)', () => {
  setup();
  E.bimLyListBySet('order');
  const h = E.bimLayersPanelHtml();
  assert.match(h, /data-lylistby="1"/);
  assert.deepEqual(order(h, /data-lyres="data:(d\d)"/g), ['d3', 'd2', 'd1']);
  assert.deepEqual(E.bimDataListTopFirst().map((L) => L.id), ['d3', 'd2', 'd1']);
  assert.deepEqual(A3D.site.dataLayers.map((L) => L.id), ['d1', 'd2', 'd3'], 'the stored order is kept');
});

test('a data layer dragged to another\'s place: the stored order changes, one undo step (D2)', () => {
  setup();
  assert.equal(E.bimDataLayerMove('d3', 'd1'), true);
  assert.deepEqual(A3D.site.dataLayers.map((L) => L.id), ['d3', 'd1', 'd2']);
  assert.deepEqual(order(E.bimLayersPanelHtml(), /data-lyres="data:(d\d)"/g), ['d2', 'd1', 'd3']);
  assert.equal(E.bimDataLayerMove('d3', 'd3'), false);
  assert.equal(E.bimDataLayerMove('nope', 'd1'), false);
});

test('Up and Down, for touch screens: one step in the list, refused at the ends', () => {
  setup();
  assert.equal(E.bimDataLayerStep('d2', 'up'), true);
  assert.deepEqual(E.bimDataListTopFirst().map((L) => L.id), ['d2', 'd3', 'd1']);
  assert.equal(E.bimDataLayerStep('d2', 'up'), false);
  assert.equal(E.bimDataLayerStep('d1', 'down'), false);
  assert.equal(E.bimDataLayerStep('d3', 'down'), true);
  assert.deepEqual(E.bimDataListTopFirst().map((L) => L.id), ['d2', 'd1', 'd3']);
});

test('by source: data layers grouped by their server, a failed one counted', () => {
  setup();
  E.bimLyListBySet('source');
  const h = E.bimLayersPanelHtml();
  assert.match(h, /data\.example\.org/);
  assert.match(h, /maps\.example\.com \(1 failed\)/);
  assert.ok(h.indexOf('data.example.org') < h.indexOf('data:d1'));
  assert.match(h, /The model/);
  assert.equal(E.bimLyListBy(), 'source');
});

test('by selection: nothing selected says so; a picked feature lists its layer', () => {
  setup();
  E.bimLyListBySet('selection');
  A3D.sel = null; A3D.selSet = [];
  E.A3D_DATA.sel = null;
  assert.match(E.bimLayersPanelHtml(), /Nothing is selected/);
  E.A3D_DATA.sel = { layer: 'd2', fi: 0 };
  const h = E.bimLayersPanelHtml();
  assert.match(h, /data-lyres="data:d2"/);
  assert.doesNotMatch(h, /data-lyres="data:d1"/);
  E.A3D_DATA.sel = null;
});

test('an unknown view reads as drawing order', () => {
  assert.equal(E.bimLyListBySet('bogus'), 'order');
});
