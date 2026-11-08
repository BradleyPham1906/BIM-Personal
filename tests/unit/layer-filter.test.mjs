// V173b: a data layer's filter (map/layer-filter.js, a CQL2 Text subset), its labels (map/data-labels.js,
// polylabel's method) and how both apply (map/data-filter-ui.js), with the owner's D9 to D12. Cases from
// docs/research/experiments/v173-filter/run.js, and the semantics in filter-and-labels.md part 5.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const A3D = E.A3D;
globalThis.document.querySelector = () => null;   // no Layers panel: the stand-in's element loops in bimRenderInto

const pass = (src, props) => { const p = E.bimFltParse(src); assert.ok(!p.error, `${src}: ${p.error}`); return E.bimFltTest(p.tree, props); };

test('comparisons, AND before OR, NOT first, grouping', () => {
  const f = { ZONE: 'CMX-3', AREA: 700, NAME: 'Pine St' };
  assert.equal(pass("ZONE = 'CMX-3'", f), true);
  assert.equal(pass("ZONE <> 'CMX-3'", f), false);
  assert.equal(pass('AREA >= 700 AND AREA < 701', f), true);
  assert.equal(pass("ZONE = 'X' OR AREA > 500 AND NAME = 'no'", f), false);
  assert.equal(pass("(ZONE = 'X' OR AREA > 500) AND NAME = 'Pine St'", f), true);
  assert.equal(pass("NOT ZONE = 'X' AND AREA = 700", f), true);
  assert.equal(pass('AREA BETWEEN 700 AND 800 AND TRUE', f), true);
  assert.equal(pass("ZONE IN ('RSA-5', 'CMX-3')", f), true);
  assert.equal(pass("ZONE NOT IN ('RSA-5', 'CMX-3')", f), false);
});

test('three-valued: a missing field is NULL, and only TRUE keeps a feature', () => {
  const f = { A: 1, B: null };
  assert.equal(pass('C = 1', f), false);
  assert.equal(pass('NOT C = 1', f), false);
  assert.equal(pass('C <> 1', f), false);
  assert.equal(pass('C IS NULL AND B IS NULL', f), true);
  assert.equal(pass('A IS NOT NULL', f), true);
  assert.equal(pass('C = 1 OR A = 1', f), true);
  const p = E.bimFltParse("A NOT IN ('x', NULL)");
  assert.match(p.warn, /NULL in a list/);
  assert.equal(E.bimFltTest(p.tree, { A: 'y' }), false);
});

test('D9: values that both read as numbers compare as numbers', () => {
  assert.equal(pass('AREA > 9', { AREA: '10' }), true);
  assert.equal(pass("AREA = '1500'", { AREA: 1500 }), true);
  assert.equal(pass("AREA > '9'", { AREA: '10' }), true);
  assert.equal(pass("AREA = 'big'", { AREA: 5 }), false);
  assert.equal(pass("AREA <> 'big'", { AREA: 5 }), true);
  assert.equal(pass("Z > 'abc'", { Z: 'abd' }), true);
});

test('D10: != , ILIKE, UPPER and LOWER read, written back as CQL2', () => {
  assert.equal(E.bimFltParse("A != 1").text, 'A <> 1');
  assert.equal(E.bimFltParse("NAME ILIKE 'pine%'").text, "CASEI(NAME) LIKE CASEI('pine%')");
  assert.equal(E.bimFltParse("UPPER(NAME) = 'PINE'").text, "CASEI(NAME) = 'PINE'");
  assert.equal(pass("NAME ILIKE 'pine%'", { NAME: 'Pine St' }), true);
  assert.equal(pass("NAME LIKE 'pine%'", { NAME: 'Pine St' }), false);
});

test('LIKE: % and _, D11 a backslash makes the next plain, and no RegExp blow-up', () => {
  assert.equal(pass("C LIKE 'A_1'", { C: 'AX1' }), true);
  assert.equal(pass("C LIKE 'A\\_1'", { C: 'AX1' }), false);
  assert.equal(pass("C LIKE 'A\\_1'", { C: 'A_1' }), true);
  assert.equal(pass("C LIKE '100\\%'", { C: '100%' }), true);
  assert.equal(pass("C LIKE '%st'", { C: 'Pine st' }), true);
  const t0 = Date.now();
  assert.equal(pass("C LIKE '%a%a%a%a%a%a%a%b'", { C: 'a'.repeat(20000) }), false);
  assert.ok(Date.now() - t0 < 1000);
});

test('quotes, spaced and keyword names, prototype names, and the round trip', () => {
  assert.equal(pass("N = 'O''Brien'", { N: "O'Brien" }), true);
  assert.equal(pass("\"Land use\" = 'park'", { 'Land use': 'park' }), true);
  assert.equal(pass("\"AND\" = 1", { AND: 1 }), true);
  assert.equal(pass('constructor IS NULL AND toString IS NULL', {}), true);
  for (const s of ["A = 1 AND (B = 'x' OR C <> 2)", "N = 'O''Brien'", "\"Land use\" IN ('a', 'b')", 'NOT (A = 1 OR B = 2)', "A NOT LIKE 'x%'", 'A IS NOT NULL', 'A NOT BETWEEN 1 AND 2'])
    assert.equal(E.bimFltParse(E.bimFltParse(s).text).text, E.bimFltParse(s).text, s);
});

test('errors name the place, and nothing is ever run as code', () => {
  assert.match(E.bimFltParse("A = 'x").error, /not closed.*character 5/);
  assert.match(E.bimFltParse('A = = 1').error, /character 5/);
  assert.match(E.bimFltParse('A = 1 B').error, /Unexpected B/);
  assert.match(E.bimFltParse('NOT '.repeat(100) + 'A = 1').error, /nests more than 64/);
  assert.match(E.bimFltParse('x'.repeat(4001)).error, /longer than 4000/);
  assert.match(E.bimFltParse('alert(1)').error, /Expected a comparison/);
  globalThis.__pwned = false;
  assert.ok(E.bimFltParse("A = '`;globalThis.__pwned=true;`'").tree);
  assert.equal(globalThis.__pwned, false);
});

test('the clause builder writes CQL2', () => {
  assert.equal(E.bimFltClause('ZONE', '=', 'CMX-3'), "ZONE = 'CMX-3'");
  assert.equal(E.bimFltClause('AREA', '>', ' 500 '), 'AREA > 500');
  assert.equal(E.bimFltClause('Land use', 'in', 'park, 3'), "\"Land use\" IN ('park', 3)");
  assert.equal(E.bimFltClause('N', 'contains', '50%'), "CASEI(N) LIKE CASEI('%50\\%%')");
  assert.equal(pass(E.bimFltClause('N', 'contains', '50%'), { N: 'Up 50% now' }), true);
  assert.equal(pass(E.bimFltClause('N', 'contains', '50%'), { N: 'Up 500 now' }), false);
  assert.equal(E.bimFltClause('N', 'null', ''), 'N IS NULL');
  assert.equal(E.bimFltClause('', '=', '1'), '');
});

test('polylabel: an L-shaped lot is labelled inside it, where its centroid is not', () => {
  const L = [[0, 0], [100, 0], [100, 20], [20, 20], [20, 100], [0, 100]];
  const p = E.bimPolyLabel([L], 0.5);
  assert.ok(E.bimPointInPoly([p.x, p.y], L));
  // against a brute-force search on a 0.25 grid: the best inside distance, within the precision
  const seg = (px, py, a, b) => { const dx = b[0] - a[0], dy = b[1] - a[1]; let t = ((px - a[0]) * dx + (py - a[1]) * dy) / (dx * dx + dy * dy); t = Math.max(0, Math.min(1, t)); return Math.hypot(px - a[0] - t * dx, py - a[1] - t * dy); };
  const dist = (x, y) => Math.min(...L.map((q, i) => seg(x, y, q, L[(i + 1) % L.length])));
  let best = 0;
  for (let x = 0; x <= 100; x += 0.25) for (let y = 0; y <= 100; y += 0.25) if (E.bimPointInPoly([x, y], L)) best = Math.max(best, dist(x, y));
  assert.ok(Math.abs(p.d - best) <= 0.5, `${p.d} vs ${best}`);
  assert.ok(Math.abs(p.d - dist(p.x, p.y)) < 1e-9);
  const sq = E.bimPolyLabel([[[0, 0], [10, 0], [10, 10], [0, 10]], [[4, 4], [6, 4], [6, 6], [4, 6]]], 0.1);
  assert.ok(!E.bimPointInPoly([sq.x, sq.y], [[4, 4], [6, 4], [6, 6], [4, 6]]), 'not in the hole');
});

test('D12: a label is a field or a template; a missing field is blank', () => {
  const p = { NAME: 'Pine', AREA: 512.3456 };
  assert.equal(E.bimDataLabelText('NAME', p), 'Pine');
  assert.equal(E.bimDataLabelText('{NAME} ({AREA} m2)', p), 'Pine (512.35 m2)');
  assert.equal(E.bimDataLabelText('{NOPE}', p), null);
  assert.equal(E.bimDataLabelText('{__proto__}', p), null);
  assert.equal(E.bimDataLabelText('', p), null);
});

test('a filter limits what a layer classifies; a bad one is refused; each an undo step', () => {
  const id = 'data-flt';
  A3D.site = A3D.site || { name: 'Site' };
  A3D.site.dataLayers = [{ id, name: 'Zoning', kind: 'geojson', url: 'u', color: '#3366ff', visible: true, credit: 'x', by: 'AREA', cls: { method: 'equal', k: 2 } }];
  A3D.dataFeatures = { [id]: [100, 400, 700, 250].map((v, i) => ({ g: { type: 'Point', coordinates: [0, 0] }, p: { AREA: v, ZONE: i % 2 ? 'R' : 'C' } })) };
  const L = A3D.site.dataLayers[0];
  assert.deepEqual(E.bimDataLensScale(L).scale.breaks, [400, 700]);
  assert.equal(E.bimDataSet(id, 'filter', "zone = 'C' AND"), false);
  assert.equal(L.filter, undefined);
  assert.equal(E.bimDataSet(id, 'filter', "ZONE != 'R'"), true);
  assert.equal(L.filter, "ZONE <> 'R'");
  assert.deepEqual(E.bimDataMask(L).pass, [true, false, true, false]);
  assert.deepEqual(E.bimDataLensScale(L).scale.breaks, [400, 700]);
  assert.equal(E.bimDataLensScale(L).scale.cls.n, 2);
  assert.equal(E.bimDataFilterText(L), 'Filter: 2 of 4 features');
  assert.equal(E.bimDataSet(id, 'filter', ''), true);
  assert.equal(L.filter, undefined);
  assert.equal(E.bimDataMask(L), null);
  assert.equal(E.bimDataSet(id, 'label', '{ZONE}'), true);
  assert.equal(L.label, '{ZONE}');
  L.filter = 'A = ';
  assert.equal(E.bimDataMask(L), null);
  assert.match(E.bimDataFilterText(L), /^Filter not applied: /);
});
