/* V175a: live text on a board. The pure functions of sheets/live-text.js, one group of cases per work order
   (docs/work-orders/v175/TASKS.md), then what Claude built on them: the record, the sources, what a live text shows,
   the units kept with the project. docs/research/research-presentation-live.md, D1 to D16. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const A3D = E.A3D;
const L = globalThis.window.__a3dLive;
const DASH = '—';

/* ---------------- WO-01 bimLvTokens ---------------- */
test('WO-01 a string with no field gives an empty list', () => {
  assert.deepEqual(L.tokens('Site plan'), []);
  assert.deepEqual(L.tokens(''), []);
});
test('WO-01 one field: where it starts, its length, its key, no decimals', () => {
  assert.deepEqual(L.tokens('GFA {{gfa}} total'), [{ i: 4, n: 7, key: 'gfa', dp: null }]);
});
test('WO-01 a field with decimals after a bar', () => {
  assert.deepEqual(L.tokens('{{site.area|2}}'), [{ i: 0, n: 15, key: 'site.area', dp: 2 }]);
});
test('WO-01 spaces inside the braces are allowed', () => {
  assert.deepEqual(L.tokens('a {{ gfa | 1 }} b'), [{ i: 2, n: 13, key: 'gfa', dp: 1 }]);
});
test('WO-01 several fields come in order', () => {
  const T = L.tokens('{{project.name}}, {{date}}');
  assert.equal(T.length, 2);
  assert.deepEqual(T.map((t) => t.key), ['project.name', 'date']);
  assert.deepEqual(T.map((t) => t.i), [0, 18]);
});
test('WO-01 what is not a field is left out', () => {
  assert.deepEqual(L.tokens('{gfa}'), [], 'single braces');
  assert.deepEqual(L.tokens('{{}}'), [], 'no key');
  assert.deepEqual(L.tokens('{{1abc}}'), [], 'a key starts with a letter');
  assert.deepEqual(L.tokens('{{a b}}'), [], 'no space inside a key');
  assert.deepEqual(L.tokens('{{gfa|12}}'), [], 'decimals are one digit');
  assert.deepEqual(L.tokens('{{gfa|7}}'), [], 'decimals are 0 to 6');
});
test('WO-01 not a string gives an empty list', () => {
  assert.deepEqual(L.tokens(null), []);
  assert.deepEqual(L.tokens(undefined), []);
  assert.deepEqual(L.tokens(42), []);
});
test('WO-01 calling it twice gives the same answer', () => {
  assert.deepEqual(L.tokens('{{gfa}}'), L.tokens('{{gfa}}'));
});

/* ---------------- WO-02 bimLvGroup ---------------- */
test('WO-02 thousands are grouped with commas', () => {
  assert.equal(L.group('1234'), '1,234');
  assert.equal(L.group('1234567'), '1,234,567');
  assert.equal(L.group('12345.6'), '12,345.6');
});
test('WO-02 short numbers are unchanged', () => {
  assert.equal(L.group('0'), '0');
  assert.equal(L.group('999'), '999');
  assert.equal(L.group('12.5'), '12.5');
});
test('WO-02 the decimals are never grouped', () => {
  assert.equal(L.group('1.23456'), '1.23456');
  assert.equal(L.group('1000.12345'), '1,000.12345');
});
test('WO-02 a minus sign stays in front', () => {
  assert.equal(L.group('-1234'), '-1,234');
  assert.equal(L.group('-123'), '-123');
});
test('WO-02 what is not a plain number is returned as it is', () => {
  assert.equal(L.group(DASH), DASH);
  assert.equal(L.group('abc'), 'abc');
  assert.equal(L.group(''), '');
});

/* ---------------- WO-03 bimLvFormat ---------------- */
test('WO-03 an area: one decimal unless given, grouped, with m2', () => {
  assert.equal(L.format(4389.04, 'area', null), '4,389 m²');
  assert.equal(L.format(4389.26, 'area', null), '4,389.3 m²');
  assert.equal(L.format(4389.257, 'area', 2), '4,389.26 m²');
  assert.equal(L.format(12.5, 'area', 0), '13 m²');
});
test('WO-03 a volume with m3', () => {
  assert.equal(L.format(1520.44, 'vol', null), '1,520.4 m³');
});
test('WO-03 a count has no decimals and no unit', () => {
  assert.equal(L.format(3, 'count', null), '3');
  assert.equal(L.format(12000, 'count', null), '12,000');
});
test('WO-03 text is returned as text', () => {
  assert.equal(L.format('Riverside House', 'text', null), 'Riverside House');
  assert.equal(L.format(7, 'text', null), '7');
});
test('WO-03 no value is a dash, with no unit', () => {
  assert.equal(L.format(null, 'area', null), DASH);
  assert.equal(L.format(NaN, 'vol', 1), DASH);
  assert.equal(L.format(undefined, 'count', null), DASH);
  assert.equal(L.format(null, 'text', null), DASH);
});
test('WO-03 a kind it does not know is treated as text', () => {
  assert.equal(L.format(5, 'banana', null), '5');
});

/* ---------------- WO-04 bimLvSubst ---------------- */
const look = (key, dp) => (key === 'gfa' ? (dp === null ? 'G' : 'G' + dp) : key === 'date' ? '2026-11-11' : key === 'loop' ? '{{gfa}}' : null);
test('WO-04 a known field is replaced', () => {
  assert.deepEqual(L.subst('GFA {{gfa}}', look), { s: 'GFA G', keys: ['gfa'], unknown: [] });
});
test('WO-04 the decimals reach look', () => {
  assert.equal(L.subst('{{gfa|2}}', look).s, 'G2');
});
test('WO-04 an unknown field is left exactly as typed', () => {
  assert.deepEqual(L.subst('a {{ nope }} b', look), { s: 'a {{ nope }} b', keys: [], unknown: ['nope'] });
});
test('WO-04 several fields, the text between them kept', () => {
  assert.deepEqual(L.subst('{{gfa}} on {{date}}, {{nope}}.', look), { s: 'G on 2026-11-11, {{nope}}.', keys: ['gfa', 'date'], unknown: ['nope'] });
});
test('WO-04 a key is listed once', () => {
  const R = L.subst('{{gfa}} {{gfa}} {{x}} {{x}}', look);
  assert.equal(R.s, 'G G {{x}} {{x}}');
  assert.deepEqual(R.keys, ['gfa']);
  assert.deepEqual(R.unknown, ['x']);
});
test('WO-04 the result is never scanned again', () => {
  assert.equal(L.subst('{{loop}}', look).s, '{{gfa}}');
});
test('WO-04 no field, or not a string', () => {
  assert.deepEqual(L.subst('plain', look), { s: 'plain', keys: [], unknown: [] });
  assert.deepEqual(L.subst(null, look), { s: '', keys: [], unknown: [] });
});

/* ---------------- WO-05 bimLvOvSet ---------------- */
test('WO-05 words that differ from the source become the override, with the source kept beside', () => {
  const n = { bind: { k: 'tok' } };
  assert.equal(L.ovSet(n, 's', 'About 4,400 m2', '4,389 m2'), true);
  assert.deepEqual(n.ov, { s: 'About 4,400 m2' });
  assert.deepEqual(n.ovAt, { s: '4,389 m2' });
});
test('WO-05 words equal to the source are no override', () => {
  const n = { bind: { k: 'tok' } };
  assert.equal(L.ovSet(n, 's', 'same', 'same'), false);
  assert.equal(n.ov, undefined);
  assert.equal(n.ovAt, undefined);
});
test('WO-05 typing the source\'s words over an override takes it off', () => {
  const n = { bind: { k: 'tok' }, ov: { s: 'x' }, ovAt: { s: 'y' } };
  assert.equal(L.ovSet(n, 's', 'now', 'now'), true);
  assert.equal(n.ov, undefined);
  assert.equal(n.ovAt, undefined);
});
test('WO-05 the same override again changes nothing', () => {
  const n = { bind: { k: 'tok' }, ov: { s: 'x' }, ovAt: { s: 'old' } };
  assert.equal(L.ovSet(n, 's', 'x', 'new'), false);
  assert.deepEqual(n.ovAt, { s: 'old' });
});
test('WO-05 a new override over an old one replaces both values', () => {
  const n = { bind: { k: 'tok' }, ov: { s: 'x' }, ovAt: { s: 'old' } };
  assert.equal(L.ovSet(n, 's', 'z', 'new'), true);
  assert.deepEqual(n.ov, { s: 'z' });
  assert.deepEqual(n.ovAt, { s: 'new' });
});
test('WO-05 an object that is not live is never overridden', () => {
  const n = { s: 'plain' };
  assert.equal(L.ovSet(n, 's', 'a', 'b'), false);
  assert.equal(n.ov, undefined);
});

/* ---------------- WO-06 bimLvOvReset ---------------- */
test('WO-06 one key reset: gone from both, and the empty objects with it', () => {
  const n = { bind: { k: 'tok' }, ov: { s: 'x' }, ovAt: { s: 'y' } };
  assert.equal(L.ovReset(n, 's'), true);
  assert.equal('ov' in n, false);
  assert.equal('ovAt' in n, false);
});
test('WO-06 the other keys stay', () => {
  const n = { bind: { k: 'tok' }, ov: { s: 'x', col: '#ff0000' }, ovAt: { s: 'y', col: '#000000' } };
  assert.equal(L.ovReset(n, 's'), true);
  assert.deepEqual(n.ov, { col: '#ff0000' });
  assert.deepEqual(n.ovAt, { col: '#000000' });
});
test('WO-06 a null key resets every override', () => {
  const n = { bind: { k: 'tok' }, ov: { s: 'x', col: '#ff0000' }, ovAt: { s: 'y' } };
  assert.equal(L.ovReset(n, null), true);
  assert.equal('ov' in n, false);
  assert.equal('ovAt' in n, false);
});
test('WO-06 nothing to reset is false', () => {
  assert.equal(L.ovReset({ bind: { k: 'tok' } }, 's'), false);
  assert.equal(L.ovReset({ bind: { k: 'tok' } }, null), false);
  assert.equal(L.ovReset({ bind: { k: 'tok' }, ov: { col: '#ff0000' } }, 's'), false);
});

/* ---------------- WO-07 bimLvOvState ---------------- */
test('WO-07 none, set and changed', () => {
  assert.equal(L.ovState({ bind: { k: 'tok' } }, 's', 'a'), 'none');
  assert.equal(L.ovState({ ov: { col: '#ff0000' } }, 's', 'a'), 'none');
  assert.equal(L.ovState({ ov: { s: 'x' }, ovAt: { s: 'a' } }, 's', 'a'), 'set');
  assert.equal(L.ovState({ ov: { s: 'x' }, ovAt: { s: 'a' } }, 's', 'b'), 'changed');
});
test('WO-07 an override with no kept source is set, never changed', () => {
  assert.equal(L.ovState({ ov: { s: 'x' } }, 's', 'b'), 'set');
  assert.equal(L.ovState({ ov: { s: 'x' }, ovAt: {} }, 's', 'b'), 'set');
});

/* ---------------- WO-08 bimLvOvKeep ---------------- */
test('WO-08 Keep moves the kept source to what it is now', () => {
  const n = { ov: { s: 'x' }, ovAt: { s: 'a' } };
  assert.equal(L.ovKeep(n, 's', 'b'), true);
  assert.deepEqual(n.ovAt, { s: 'b' });
  assert.deepEqual(n.ov, { s: 'x' });
});
test('WO-08 already the same, or not overridden: nothing changes', () => {
  const n = { ov: { s: 'x' }, ovAt: { s: 'a' } };
  assert.equal(L.ovKeep(n, 's', 'a'), false);
  const m = { bind: { k: 'tok' } };
  assert.equal(L.ovKeep(m, 's', 'a'), false);
  assert.equal('ovAt' in m, false);
});
test('WO-08 an override with no kept source gets one', () => {
  const n = { ov: { s: 'x' } };
  assert.equal(L.ovKeep(n, 's', 'b'), true);
  assert.deepEqual(n.ovAt, { s: 'b' });
});

/* ---------------- WO-09 bimLvPrintNote ---------------- */
test('WO-09 nothing out of date says nothing', () => {
  assert.equal(L.printNote([]), '');
  assert.equal(L.printNote(null), '');
});
test('WO-09 one object', () => {
  assert.equal(L.printNote([{ nm: 'Cut volume', why: 'Out of date: a pad has changed' }]),
    'Printed with 1 live object not up to date: Cut volume (Out of date: a pad has changed)');
});
test('WO-09 an object with no reason has no brackets', () => {
  assert.equal(L.printNote([{ nm: 'A', why: '' }, { nm: 'B', why: 'gone' }]), 'Printed with 2 live objects not up to date: A, B (gone)');
});
test('WO-09 more than three: three named, the rest counted', () => {
  const I = ['A', 'B', 'C', 'D', 'E'].map((nm) => ({ nm, why: '' }));
  assert.equal(L.printNote(I), 'Printed with 5 live objects not up to date: A, B, C and 2 more');
});

/* ---------------- WO-10 bimLvMenuItems ---------------- */
test('WO-10 rows become [label, key], a rule between groups', () => {
  const rows = [['project.name', 'Project name', 'text', 'Project'], ['date', 'Today\'s date', 'text', 'Project'], ['gfa', 'Gross floor area', 'area', 'Building'],
    ['site.area', 'Site area', 'area', 'Site']];
  assert.deepEqual(L.menuItems(rows), [['Project name', 'project.name'], ['Today\'s date', 'date'], '-', ['Gross floor area', 'gfa'], '-', ['Site area', 'site.area']]);
});
test('WO-10 one group has no rule; no rows, no items', () => {
  assert.deepEqual(L.menuItems([['gfa', 'Gross floor area', 'area', 'Building']]), [['Gross floor area', 'gfa']]);
  assert.deepEqual(L.menuItems([]), []);
});

/* ================= Claude's part: these pass once WO-01 to WO-10 are built ================= */
function fresh() {
  A3D.objs.length = 0;
  A3D.titleBlock = { project: 'Riverside House', client: '', drawnBy: 'BP', checkedBy: '' };
  L.bump();
}

test('the record keeps a binding and its overrides, and drops what is not one', () => {
  const T = E.bimBobValid([
    { id: 'e1', t: 'text', x: 0, y: 0, w: 10, h: 5, s: '{{gfa}}', bind: { k: 'num', src: 'gfa', dp: 9, nm: '  x  ', junk: 1 }, ov: { s: 'About', z: 1 }, ovAt: { s: '4,389 m2', col: 'x' } },
    { id: 'e2', t: 'text', x: 0, y: 0, w: 10, h: 5, s: 'a {{date}}', bind: { k: 'tok' }, ovAt: { s: 'orphan' } },
    { id: 'e3', t: 'text', x: 0, y: 0, w: 10, h: 5, s: 'plain', bind: { k: 'weird' }, ov: { s: 'x' } },
    { id: 'e4', t: 'rect', x: 0, y: 0, w: 10, h: 5, bind: { k: 'tok' } },
    { id: 'e5', t: 'text', x: 0, y: 0, w: 10, h: 5, s: '{{future.key}}', bind: { k: 'num', src: 'future.key' } },
  ], []);
  assert.deepEqual(T[0].bind, { k: 'num', src: 'gfa', nm: 'x', dp: 6 });
  assert.deepEqual(T[0].ov, { s: 'About' });
  assert.deepEqual(T[0].ovAt, { s: '4,389 m2' });
  assert.deepEqual(T[1].bind, { k: 'tok' });
  assert.equal('ov' in T[1], false);
  assert.equal('ovAt' in T[1], false, 'no kept source without an override');
  assert.equal('bind' in T[2], false);
  assert.equal('ov' in T[2], false, 'no override without a binding');
  assert.equal('bind' in T[3], false, 'only text is live in V175a');
  assert.deepEqual(T[4].bind, { k: 'num', src: 'future.key' }, 'a newer build\'s key is kept');
});

test('an old board\'s text is untouched: no binding, no field read', () => {
  const T = E.bimBobValid([{ id: 'e1', t: 'text', x: 0, y: 0, w: 10, h: 5, s: 'Total {{gfa}}' }], []);
  assert.equal('bind' in T[0], false);
  assert.equal(L.show(T[0], null, false).s, 'Total {{gfa}}');
});

test('the key table: every key is one, an alias finds its key, anything else is not a field', () => {
  L.keys().forEach((k) => assert.equal(L.key(k[0])[0], k[0]));
  assert.equal(L.key('gba')[0], 'gfa');
  assert.equal(L.key('constructor'), null);
  assert.equal(L.key('toString'), null);
  assert.equal(L.key(null), null);
});

test('a text with fields shows the project\'s values, and follows them', () => {
  fresh();
  const n = { id: 'e1', t: 'text', s: '{{project.name}}, drawn by {{project.drawnBy}}', bind: { k: 'tok' } };
  assert.equal(L.show(n, null, false).s, 'Riverside House, drawn by BP');
  A3D.titleBlock.drawnBy = 'KL';
  assert.equal(L.show(n, null, false).s, 'Riverside House, drawn by BP', 'computed once per revision');
  L.bump();
  const R = L.show(n, null, false);
  assert.equal(R.s, 'Riverside House, drawn by KL');
  assert.equal(R.st, 'ok');
  assert.deepEqual(R.keys, ['project.name', 'project.drawnBy']);
});

test('an empty source is a dash and says why; an unknown key stays as typed and is marked', () => {
  fresh();
  const R = L.show({ id: 'e1', t: 'text', s: 'Client: {{project.client}} {{nope}}', bind: { k: 'tok' } }, null, true);
  assert.equal(R.s, 'Client: ' + DASH + ' {{nope}}');
  assert.equal(R.st, 'none');
  assert.deepEqual(R.unknown, ['nope']);
  assert.match(R.why[0], /Client is not filled in/);
  assert.match(L.marks(R), /a3d-clb-dlv gone/);
  assert.match(L.marks(R), /Not a field: nope/);
});

test('a number counts the model; with nothing to measure it says so in Edit and is a dash on paper', () => {
  fresh();
  const n = { id: 'e1', t: 'text', s: '{{rooms}}', bind: { k: 'num', src: 'rooms' } };
  assert.equal(L.show(n, null, false).s, '0');
  A3D.objs.push({ id: 'r1', t: 'room', area: 20.26, levelId: 'x' }, { id: 'r2', t: 'room', area: 1200, levelId: 'x' });
  L.bump();
  assert.equal(L.show(n, null, false).s, '2');
  assert.equal(L.show({ t: 'text', s: '{{rooms.area}}', bind: { k: 'num', src: 'rooms.area' } }, null, false).s, '1,220.3 m²');
  assert.equal(L.show({ t: 'text', s: '{{rooms.area}}', bind: { k: 'num', src: 'rooms.area', dp: 0 } }, null, false).s, '1,220 m²');
  const cut = { t: 'text', s: '{{cut}}', bind: { k: 'num', src: 'cut' } };
  assert.equal(L.show(cut, null, false).s, DASH);
  assert.match(L.show(cut, null, true).s, /^Not computed: GRADE a pad/);
  assert.equal(L.show(cut, null, true).src, DASH, 'the source\'s words are the paper\'s');
  fresh();
});

test('a level that was deleted is named, never rebound; the binding is kept', () => {
  fresh();
  const n = { t: 'text', s: '{{level.area}}', bind: { k: 'num', src: 'level.area', id: 'no-such-level', nm: 'Level 2' } };
  const R = L.show(n, null, true);
  assert.equal(R.st, 'gone');
  assert.equal(R.s, 'Source removed: Level 2');
  assert.equal(L.show(n, null, false).s, DASH);
  assert.deepEqual(n.bind, { k: 'num', src: 'level.area', id: 'no-such-level', nm: 'Level 2' });
  assert.equal(L.show({ t: 'text', s: '{{level.area}}', bind: { k: 'tok' } }, null, false).s, '{{level.area}}', 'a source by id is not a typed field');
});

test('an override is shown in place of the source, and says when the source has moved since', () => {
  fresh();
  const n = { t: 'text', s: '{{project.name}}', bind: { k: 'tok' } };
  assert.equal(L.ovSet(n, 's', 'The House', L.show(n, null, false).src), true);
  let R = L.show(n, null, false);
  assert.equal(R.s, 'The House');
  assert.equal(R.src, 'Riverside House');
  assert.equal(R.ov, true);
  assert.equal(R.changed, false);
  assert.match(L.marks(R), /a3d-clb-dlv ov/);
  A3D.titleBlock.project = 'Hillside House';
  L.bump();
  R = L.show(n, null, false);
  assert.equal(R.s, 'The House', 'a refresh never overwrites an override');
  assert.equal(R.changed, true);
  assert.equal(L.ovKeep(n, 's', R.src), true);
  assert.equal(L.show(n, null, false).changed, false);
  assert.equal(L.ovReset(n, null), true);
  assert.equal(L.show(n, null, false).s, 'Hillside House');
  fresh();
});

test('setting a text\'s words binds it when they hold a field, and unbinds it when they do not', () => {
  assert.deepEqual(L.textPatch({ t: 'text', s: 'a' }, 'GFA {{gfa}}'), { s: 'GFA {{gfa}}', bind: { k: 'tok' } });
  assert.deepEqual(L.textPatch({ t: 'text', s: 'a' }, 'GFA {{nope}}'), { s: 'GFA {{nope}}' });
  assert.deepEqual(L.textPatch({ t: 'text', s: 'a', bind: { k: 'tok' } }, 'plain'), { s: 'plain', bind: null, ov: null, ovAt: null });
  assert.deepEqual(L.textPatch({ t: 'text', s: 'a', bind: { k: 'tok' } }, '{{date}}'), { s: '{{date}}' });
});

test('Print lists the live objects that are not up to date', () => {
  fresh();
  const B = { id: 'b1', objs: [
    { id: 'e1', t: 'text', s: '{{project.name}}', bind: { k: 'tok' } },
    { id: 'e2', t: 'text', s: '{{cut}}', nm: 'Cut volume', bind: { k: 'num', src: 'cut' } },
    { id: 'e3', t: 'text', s: 'plain {{cut}}' },
  ] };
  const I = L.stale(B);
  assert.equal(I.length, 1);
  assert.equal(I[0].nm, 'Cut volume');
  assert.match(L.printNote(I), /^Printed with 1 live object not up to date: Cut volume \(Not computed/);
});

test('the display units are a field of the project (D10)', () => {
  E.bimSetUnits('mm', 1);
  assert.deepEqual(E.bimProjectRecord().units, { key: 'mm', dp: 1 });
  L.applyUnits(null);
  assert.deepEqual(L.unitState(), { key: 'm', dp: null }, 'a project with none is in metres');
  L.applyUnits({ key: 'cm', dp: 2 });
  assert.deepEqual(L.unitState(), { key: 'cm', dp: 2 });
  assert.deepEqual(A3D.units, { key: 'cm', dp: 2 });
  L.applyUnits({ key: 'furlong', dp: 99 });
  assert.deepEqual(L.unitState(), { key: 'm', dp: 4 });
  L.applyUnits(null);
});
