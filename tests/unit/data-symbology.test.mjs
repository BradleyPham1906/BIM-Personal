// V173a: a data layer's graduated colours (map/data-symbology.js, map/colour-ramps.js): ColorBrewer's
// ramps as its schemes file gives them, the owner's defaults (natural breaks, 5 classes), each setting
// one undo step through bimDataSet, and the classes the features are drawn in.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const A3D = E.A3D;
// no Layers panel on the page: the stand-in's element would let bimRenderInto loop forever
globalThis.document.querySelector = () => null;

function layer(values, cls) {
  const id = 'data-test-' + Math.random().toString(36).slice(2);
  A3D.site = A3D.site || { name: 'Site' };
  A3D.site.dataLayers = [{ id, name: 'Test', kind: 'geojson', url: 'https://x.example/' + id, color: '#3366ff', visible: true, credit: 'x', by: 'V', cls }];
  A3D.dataFeatures = A3D.dataFeatures || {};
  A3D.dataFeatures[id] = values.map((v) => ({ g: { type: 'Point', coordinates: [0, 0] }, p: { V: v } }));
  return A3D.site.dataLayers[0];
}
const cols = (L) => A3D.dataFeatures[L.id].map((_, fi) => E.bimDataFeatCol(L, E.bimDataLensScale(L), fi));

test('the ramps are ColorBrewer\'s: YlOrRd 6 is the lens\'s ramp, 5 and 9 as the schemes file', () => {
  assert.deepEqual(E.bimRampColours('YlOrRd', 6), E.BIM_LENS_RAMP);
  assert.deepEqual(E.bimRampColours('YlOrRd', 5), ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026']);
  assert.deepEqual(E.bimRampColours('Blues', 9)[8], '#08306b');
  assert.deepEqual(E.bimRampColours('RdBu', 11).length, 11);
  assert.deepEqual(E.bimRampColours('YlOrRd', 5, true), ['#bd0026', '#f03b20', '#fd8d3c', '#fecc5c', '#ffffb2']);
});

test('ramps beyond a scheme\'s range: 1 and 2 classes take its ends, 12 mixes its largest evenly', () => {
  assert.deepEqual(E.bimRampColours('YlOrRd', 1), ['#f03b20']);
  assert.deepEqual(E.bimRampColours('YlOrRd', 2), ['#ffeda0', '#f03b20']);
  const c = E.bimRampColours('YlOrRd', 12), nine = E.bimRampColours('YlOrRd', 9);
  assert.equal(c.length, 12);
  assert.equal(c[0], nine[0]);
  assert.equal(c[11], nine[8]);
  c.forEach((h) => assert.match(h, /^#[0-9a-f]{6}$/));
  assert.deepEqual(E.bimRampColours('nope', 5), E.bimRampColours('YlOrRd', 5));
});

test('a number with no settings: natural breaks, 5 classes, every class in the legend', () => {
  const L = layer([1, 2, 3, 10, 11, 12, 20, 21, 40, 41, 80, 81]);
  const ds = E.bimDataLensScale(L);
  assert.equal(ds.scale.cls.method, 'natural');
  assert.equal(ds.scale.breaks.length, 5);
  assert.deepEqual(ds.scale.breaks, [3, 12, 21, 41, 81]);
  const c = cols(L), R = E.bimRampColours('YlOrRd', 5);
  assert.deepEqual([c[0], c[3], c[6], c[8], c[10]], R);
  assert.equal(c[1], R[0]);
  assert.match(E.bimDataLegendTitle(L, ds), /Natural breaks \(Jenks\), 5 classes/);
});

test('V136\'s four districts: 4 distinct values give 4 classes, said so', () => {
  const L = layer([100, 400, 700, 250]);
  const ds = E.bimDataLensScale(L);
  assert.deepEqual(ds.scale.breaks, [100, 250, 400, 700]);
  assert.deepEqual(cols(L), ['#ffffb2', '#fd8d3c', '#e31a1c', '#fecc5c']);
  assert.match(ds.scale.cls.note, /4 classes of the 5 asked/);
});

test('settings from a project file are read safely', () => {
  const L = layer([1, 2, 3, 4, 5, 6], { method: 'eval', k: 'x', ramp: '__proto__', step: 9, breaks: ['a', 2, null, 2] });
  const c = E.bimDataLensScale(L).scale.cls;
  assert.equal(c.st.method, 'natural');
  assert.equal(c.st.k, 5);
  assert.equal(c.st.ramp, 'YlOrRd');
  assert.equal(c.st.step, 1);
  assert.deepEqual(c.st.breaks, [2]);
});

test('each setting through bimDataSet; a refused value changes nothing', () => {
  const L = layer([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
  assert.equal(E.bimDataSet(L.id, 'cls.method', 'quantile'), true);
  assert.equal(E.bimDataSet(L.id, 'cls.k', '4'), true);
  assert.deepEqual(E.bimDataLensScale(L).scale.breaks, [3.25, 5.5, 7.75, 10]);
  assert.equal(E.bimDataSet(L.id, 'cls.k', '13'), false);
  assert.equal(E.bimDataSet(L.id, 'cls.method', 'geometric'), false);
  assert.equal(E.bimDataSet(L.id, 'cls.ramp', 'Rainbow'), false);
  assert.deepEqual(L.cls, { method: 'quantile', k: 4 });
  assert.equal(E.bimDataSet(L.id, 'cls.ramp', 'Blues'), true);
  assert.equal(E.bimDataSet(L.id, 'cls.rev', true), true);
  assert.equal(cols(L)[0], E.bimRampColours('Blues', 4)[3]);
});

test('Manual starts from the breaks shown; typing breaks makes the method Manual', () => {
  const L = layer([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], { method: 'equal', k: 3 });
  E.bimDataLensScale(L);
  assert.equal(E.bimDataSet(L.id, 'cls.method', 'manual'), true);
  assert.deepEqual(L.cls.breaks, [4, 7]);
  assert.deepEqual(E.bimDataLensScale(L).scale.breaks, [4, 7, 10]);
  const M = layer([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
  assert.equal(E.bimDataSet(M.id, 'cls.breaks', '5; 2.5 , 5'), true);
  assert.equal(M.cls.method, 'manual');
  assert.deepEqual(E.bimDataLensScale(M).scale.breaks, [2.5, 5, 10]);
  assert.equal(E.bimDataSet(M.id, 'cls.breaks', '3, five'), false);
  assert.deepEqual(M.cls.breaks, [2.5, 5]);
});

test('a method the values refuse falls back to equal interval and says why', () => {
  const L = layer([-5, 0, 5, 10], { method: 'log', k: 2 });
  const c = E.bimDataLensScale(L).scale.cls;
  assert.equal(c.fellBack, 'log');
  assert.equal(c.method, 'equal');
  assert.match(c.note, /Log interval needs every value above 0.*equal interval instead/);
  assert.match(E.bimDataLegendTitle(L, E.bimDataLensScale(L)), /Equal interval, 2 classes/);
});

test('text keeps V136\'s categories; the swatch and the legend follow the classes', () => {
  const T = layer(['a', 'b', 'a', '']);
  assert.equal(E.bimDataLensScale(T).scale.kind, 'cat');
  const L = layer([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], { method: 'equal', k: 3 });
  assert.equal(E.bimDataSwatch(L), 'linear-gradient(90deg,' + E.bimRampColours('YlOrRd', 3).join(',') + ')');
  const h = E.bimDataLegendHtml(L);
  assert.equal((h.match(/<i /g) || []).length, 3);
  assert.match(h, /1 to 4 \(4\)/);
  L.by = '';
  assert.equal(E.bimDataSwatch(L), '#3366ff');
  assert.equal(E.bimDataLegendHtml(L), '');
});
