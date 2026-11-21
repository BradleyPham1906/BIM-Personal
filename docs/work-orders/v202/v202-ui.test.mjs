// V202 part B, the Site and Map interface (docs/work-orders/v202/SPEC.md, part B).
// The pure functions of WO-12 to WO-14, in src/js/engine/map/site-ui.js.
//
//   node --test docs/work-orders/v202/v202-ui.test.mjs
//   node --test --test-name-pattern="WO-12" docs/work-orders/v202/v202-ui.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from '../../../tests/unit/helpers/engine.mjs';

const F = loadEngine();
const KINDS = ['buildings', 'roads', 'water', 'green', 'trees', 'rail', 'airports', 'power', 'landuse', 'terrain'];
const LABELS = { buildings: 'Buildings', roads: 'Roads', water: 'Water', green: 'Green', trees: 'Trees', rail: 'Railways', airports: 'Airports', power: 'Power', landuse: 'Land use', terrain: 'Terrain' };
const near = (a, b, msg) => assert.ok(Math.abs(a - b) < 1e-6, (msg || '') + ' ' + a + ' vs ' + b);

// ---- WO-12 bimCtxCards ----
test('WO-12 one card per labelled kind, in order, with its state and count', () => {
  const st = { kinds: { buildings: true, roads: false, terrain: true } };
  const c = F.bimCtxCards(KINDS, LABELS, st, { buildings: 36, roads: 388 });
  assert.equal(c.length, 10);
  assert.deepEqual(c.map((x) => x.kind), KINDS);
  assert.equal(c[0].title, 'Buildings');
  assert.equal(c[0].on, true);
  assert.equal(c[1].on, false);
  assert.equal(c[2].on, false, 'a kind missing from st.kinds is off');
  assert.equal(c[0].count, 36);
  assert.equal(c[2].count, null, 'no count for a kind the fetch did not report');
});
test('WO-12 the sources and the sentences', () => {
  const c = F.bimCtxCards(KINDS, LABELS, { kinds: {} }, null);
  for (const x of c) {
    assert.equal(typeof x.say, 'string');
    assert.ok(x.say.length > 10 && x.say.length <= 90, x.kind + ': ' + x.say);
    assert.ok(!/[\u{1F300}-\u{1FAFF}]/u.test(x.say), 'no emojis');
    assert.equal(x.count, null);
    assert.equal(x.source, x.kind === 'terrain' ? 'AWS Terrain Tiles (Terrarium)' : 'OpenStreetMap');
  }
});
test('WO-12 a kind without a label is left out; bad input gives []', () => {
  assert.deepEqual(F.bimCtxCards(['buildings', 'mystery'], { buildings: 'Buildings' }, { kinds: {} }, null).map((x) => x.kind), ['buildings']);
  assert.deepEqual(F.bimCtxCards(null, LABELS, null, null), []);
  assert.equal(F.bimCtxCards(['roads'], LABELS, null, null)[0].on, false);
});

// ---- WO-13 bimPlaceFacts ----
const rows = (p) => Object.fromEntries(p.rows);
test('WO-13 a building: title from its name, height with where it came from, address, use', () => {
  const p = F.bimPlaceFacts({ kind: 'buildings', osm: 'way', id: 12345, credit: '© OpenStreetMap contributors (ODbL)', fetched: '2026-11-17', height: 24.5, heightFrom: 'height',
    tags: { name: '30th Street Station', building: 'train_station', 'building:levels': '5', 'addr:housenumber': '2955', 'addr:street': 'Market Street', start_date: '1933', operator: 'Amtrak' } }, 'Building 3');
  assert.equal(p.title, '30th Street Station');
  assert.equal(p.kind, 'Building');
  const r = rows(p);
  assert.equal(r.Height, '24.5 m (OpenStreetMap height)');
  assert.equal(r.Levels, '5');
  assert.equal(r.Address, '2955 Market Street');
  assert.equal(r.Use, 'train station');
  assert.equal(r.Built, '1933');
  assert.equal(r.Operator, 'Amtrak');
  assert.equal(r.Fetched, '2026-11-17');
  assert.deepEqual(p.rows.map((x) => x[0]), ['Height', 'Levels', 'Address', 'Use', 'Built', 'Operator', 'Fetched']);
  assert.equal(p.credit, '© OpenStreetMap contributors (ODbL)');
  assert.equal(p.osmUrl, 'https://www.openstreetmap.org/way/12345');
});
test('WO-13 the height sources say what they are', () => {
  const h = (from) => rows(F.bimPlaceFacts({ kind: 'buildings', height: 6, heightFrom: from, tags: {} }, 'B')).Height;
  assert.equal(h('city'), '6 m (measured)');
  assert.equal(h('levels'), '6 m (storeys x 3 m)');
  assert.equal(h('assumed'), '6 m (assumed)');
  assert.equal(h(undefined), '6 m');
});
test('WO-13 a bridge and a road: kind, width, deck; no name falls back to the object name', () => {
  const b = F.bimPlaceFacts({ kind: 'roads', bridge: true, deck: 7.25, width: 14, tags: { highway: 'primary' } }, 'Bridge: Market Street');
  assert.equal(b.kind, 'Bridge');
  assert.equal(b.title, 'Bridge: Market Street');
  const r = rows(b);
  assert.equal(r.Width, '14 m');
  assert.equal(r.Deck, '7.25 m over the ground');
  assert.equal(r.Use, 'primary');
  const t = F.bimPlaceFacts({ kind: 'rail', tunnel: true, tags: {} }, '');
  assert.equal(t.kind, 'Tunnel');
  assert.equal(t.title, 'Unnamed');
  assert.equal(F.bimPlaceFacts({ kind: 'trees', tags: {} }, 'Tree 4').kind, 'Tree');
});
test('WO-13 no osm link without both type and id; building=yes is no use; missing ctx is null', () => {
  const p = F.bimPlaceFacts({ kind: 'buildings', tags: { building: 'yes' } }, 'B');
  assert.equal(p.osmUrl, null);
  assert.equal(p.credit, null);
  assert.equal(rows(p).Use, undefined);
  assert.deepEqual(p.rows, []);
  assert.equal(F.bimPlaceFacts(null, 'x'), null);
  assert.equal(F.bimPlaceFacts({ kind: 'roads', osm: 'node', id: 7, tags: {} }, 'x').osmUrl, 'https://www.openstreetmap.org/node/7');
});

// ---- WO-14 bimCompass ----
const R = Math.PI / 180;
test('WO-14 facing north, east, south, west', () => {
  let c = F.bimCompass(0, 0);
  near(c.needle, 0); near(c.heading, 0); assert.equal(c.letter, 'N');
  c = F.bimCompass(-90 * R, 0);
  near(c.needle, 270); near(c.heading, 90); assert.equal(c.letter, 'E');
  c = F.bimCompass(180 * R, 0);
  near(c.needle, 180); near(c.heading, 180); assert.equal(c.letter, 'S');
  c = F.bimCompass(90 * R, 0);
  near(c.needle, 90); near(c.heading, 270); assert.equal(c.letter, 'W');
});
test('WO-14 true north turns the needle; letters in between; angles kept in 0 to 360', () => {
  let c = F.bimCompass(0, 30);
  near(c.needle, 30); near(c.heading, 330); assert.equal(c.letter, 'NW');
  c = F.bimCompass(-45 * R, 0);
  assert.equal(c.letter, 'NE');
  c = F.bimCompass(-725 * R, 0);
  near(c.heading, 5); assert.ok(c.needle >= 0 && c.needle < 360);
  c = F.bimCompass(-22 * R, 0);
  assert.equal(c.letter, 'N');
  assert.equal(F.bimCompass(NaN, 0), null);
  assert.equal(F.bimCompass(0, NaN), null);
});
