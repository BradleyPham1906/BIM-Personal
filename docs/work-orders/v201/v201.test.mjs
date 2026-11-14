/* V201's work-order tests (docs/work-orders/v201/SPEC.md, WO-01 to WO-07): the pure functions of
   src/js/engine/bim/mep-flow.js, MEP runs' first slice: sections, Darcy-Weisbach friction with Colebrook, joins
   between runs, a single-source tree, flows from the terminals' demand, and friction-only paths.

   The expected numbers are the research's checks (docs/research/research-notion-v193-mep.md part 7, its script
   docs/research/experiments/notion-v193/checks.py): Purdue's Moody exercise, TU Delft's example 1, the laminar
   identity and the branch paths. Outside tests/unit/ while the work orders are open:
     node --test docs/work-orders/v201/v201.test.mjs
     node --test --test-name-pattern="WO-03" docs/work-orders/v201/v201.test.mjs */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimMepSection', 'bimMepColebrook', 'bimMepFriction', 'bimMepJoin', 'bimMepTree', 'bimMepFlows', 'bimMepPaths'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/bim/mep-flow.js'), 'utf8');
  if (process.env.V201_REF) src += fs.readFileSync(process.env.V201_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const M = load();
const fn = (n) => { assert.equal(typeof M[n], 'function', n + ' is not built yet in src/js/engine/bim/mep-flow.js'); return M[n]; };
const rel = (a, b, r, msg) => assert.ok(Math.abs(a - b) <= r * Math.abs(b), (msg || '') + ' ' + a + ' is not ' + b);
const WATER = { rho: 998.2, mu: 0.001002, eps: 0.0000015 };

test('WO-01 round and rectangular sections: area, perimeter, hydraulic diameter', () => {
  const r = fn('bimMepSection')({ shape: 'round', d: 0.1 });
  rel(r.area, Math.PI * 0.0025, 1e-12); rel(r.perimeter, Math.PI * 0.1, 1e-12); assert.equal(r.dh, 0.1); assert.equal(r.shape, 'round');
  const q = fn('bimMepSection')({ shape: 'rect', w: 0.4, h: 0.2 });
  assert.equal(q.shape, 'rect'); rel(q.area, 0.08, 1e-12); rel(q.perimeter, 1.2, 1e-12); rel(q.dh, 0.16 / 0.6, 1e-12, 'dh = 4A/P = 2wh/(w+h)');
  for (const bad of [{ shape: 'round', d: 0 }, { shape: 'rect', w: 0.4 }, { shape: 'oval', d: 1 }, { shape: 'round', d: NaN }, null]) assert.equal(fn('bimMepSection')(bad), null);
});

test('WO-02 Colebrook by bisection: Purdue Moody exercise (research check A)', () => {
  const c = fn('bimMepColebrook')(100000, 0.001);
  rel(c.f, 0.0221745359, 1e-8, 'f_D');
  assert.ok(Math.abs(c.residual) < 1e-12);
  assert.equal(fn('bimMepColebrook')(3000, 0.001), null, 'only above Re 4000');
  assert.equal(fn('bimMepColebrook')(1e5, 1), null);
  assert.equal(fn('bimMepColebrook')(1e5, -0.1), null);
});

test('WO-03 straight friction: TU Delft example 1 as head (research check B)', () => {
  const sec = M.bimMepSection({ shape: 'round', d: 0.593 });
  for (const [nu, head] of [[1.52e-6, 0.624412], [0.9e-6, 0.595222]]) {
    const r = fn('bimMepFriction')(0.3, sec, 400, { rho: 1000, mu: 1000 * nu, eps: 0.0001 });
    assert.equal(r.state, 'turbulent');
    rel(r.dp / (1000 * 9.81), head, 2e-6, 'head');
  }
});
test('WO-03 laminar circular equals Poiseuille (research check C); the regimes the app refuses', () => {
  const sec = M.bimMepSection({ shape: 'round', d: 0.1 }), rho = 998.2, mu = 0.001002;
  const q = 1000 * mu / (rho * 0.1) * sec.area;
  const r = fn('bimMepFriction')(q, sec, 10, { rho, mu, eps: 0 });
  assert.equal(r.state, 'laminar'); rel(r.re, 1000, 1e-12); rel(r.dp, 0.321860629, 1e-8);
  const t = fn('bimMepFriction')(q * 3, sec, 10, { rho, mu, eps: 0 });
  assert.deepEqual([t.state, t.dp, t.why], ['transitional', null, 'Reynolds number between 2300 and 4000']);
  const rect = M.bimMepSection({ shape: 'rect', w: 0.1, h: 0.1 });
  const l = fn('bimMepFriction')(0.0001, rect, 10, { rho, mu, eps: 0 });
  assert.deepEqual([l.state, l.dp, l.why], ['not evaluated', null, 'laminar flow in a rectangular duct']);
  assert.deepEqual(fn('bimMepFriction')(0, sec, 10, WATER).state, 'no flow');
  assert.deepEqual(fn('bimMepFriction')(0, sec, 10, WATER).dp, 0);
  assert.deepEqual(fn('bimMepFriction')(-1, sec, 10, WATER), { state: 'not evaluated', why: 'bad input' });
  assert.deepEqual(fn('bimMepFriction')(0.01, null, 10, WATER), { state: 'not evaluated', why: 'bad input' });
  assert.deepEqual(fn('bimMepFriction')(0.01, sec, 10, { rho: 1000, mu: 0, eps: 0 }), { state: 'not evaluated', why: 'bad input' });
});

// a tee: trunk from the source S to J, branch A and branch B from J
const RUNS = [
  { id: 'trunk', sys: 'CW', pts: [[0, 0, 0], [10, 0, 0]] },
  { id: 'A', sys: 'CW', pts: [[10, 0, 0], [10, 5, 0]] },
  { id: 'B', sys: 'CW', pts: [[10.004, 0, 0], [10, 0, 3], [18, 0, 3]] }
];
test('WO-04 runs joined end to end within the tolerance; 3D lengths', () => {
  const g = fn('bimMepJoin')(RUNS, 0.01);
  assert.deepEqual(g.nodes.map((n) => n.id), [0, 1, 2, 3]);
  assert.deepEqual(g.edges.map((e) => [e.run, e.a, e.b]), [['trunk', 0, 1], ['A', 1, 2], ['B', 1, 3]]);
  rel(g.edges[2].len, Math.sqrt(0.004 * 0.004 + 9) + 8, 1e-12);
  assert.deepEqual(g.warnings, []);
});
test('WO-04 crossings at another height do not join; other systems do not join; bad runs are named', () => {
  const g = fn('bimMepJoin')([
    { id: 'a', sys: 'CW', pts: [[0, 0, 0], [4, 0, 0]] },
    { id: 'b', sys: 'CW', pts: [[4, 0, 1], [8, 0, 1]] },
    { id: 'c', sys: 'HW', pts: [[4, 0, 0], [4, 4, 0]] },
    { id: 'd', sys: 'CW', pts: [[1, 1, 1]] },
    { id: 'e', sys: 'CW', pts: [[2, 2, 2], [2, 2, 2]] }
  ], 0.01);
  assert.equal(g.nodes.length, 6);
  assert.deepEqual(g.warnings, ['different systems meet at node 1', 'run d has fewer than 2 points', 'run e has no length']);
  assert.deepEqual(fn('bimMepJoin')(null), { nodes: [], edges: [], warnings: [] });
});

test('WO-05 a tree from the source; a loop or a part not connected is refused', () => {
  const g = M.bimMepJoin(RUNS, 0.01);
  const t = fn('bimMepTree')(g.nodes.length, g.edges, 0);
  assert.deepEqual(t.order, [0, 1, 2, 3]);
  assert.deepEqual(t.parent, { 0: -1, 1: 0, 2: 1, 3: 1 });
  assert.deepEqual(t.via, { 1: 0, 2: 1, 3: 2 });
  assert.deepEqual(fn('bimMepTree')(3, [{ a: 0, b: 1 }, { a: 1, b: 2 }, { a: 2, b: 0 }], 0), { error: 'loop' });
  assert.deepEqual(fn('bimMepTree')(3, [{ a: 0, b: 1 }], 0), { error: 'not connected' });
  assert.deepEqual(fn('bimMepTree')(3, [], 5), { error: 'no source' });
});

test('WO-06 flows summed from the terminals toward the source; a terminal without demand refuses', () => {
  const g = M.bimMepJoin(RUNS, 0.01), t = M.bimMepTree(g.nodes.length, g.edges, 0);
  assert.deepEqual(fn('bimMepFlows')(t, g.edges, { 2: 0.004, 3: 0.006 }), { flow: { 0: 0.01, 1: 0.004, 2: 0.006 } });
  assert.deepEqual(fn('bimMepFlows')(t, g.edges, { 2: 0.004 }), { error: 'no demand at node 3' });
  assert.deepEqual(fn('bimMepFlows')(t, g.edges, { 1: 0.002, 2: 0.004, 3: 0.006 }).flow[0], 0.012, 'a draw at a branch point adds to the trunk');
});

test('WO-07 friction-only paths: the trunk once per path, the critical one (research check D)', () => {
  const sec = M.bimMepSection({ shape: 'round', d: 0.1 });
  const edges = [{ run: 'trunk', a: 0, b: 1, len: 10 }, { run: 'A', a: 1, b: 2, len: 5 }, { run: 'B', a: 1, b: 3, len: 8 }];
  const t = M.bimMepTree(4, edges, 0), q = M.bimMepFlows(t, edges, { 2: 0.004, 3: 0.006 }).flow;
  const loss = {}; for (const i of [0, 1, 2]) loss[i] = M.bimMepFriction(q[i], sec, edges[i].len, WATER).dp;
  rel(loss[0], 1393.399, 1e-6); rel(loss[1], 135.142, 1e-5); rel(loss[2], 445.722, 1e-6);
  const p = fn('bimMepPaths')(t, edges, loss);
  assert.deepEqual(p.paths.map((x) => [x.to, x.runs]), [[2, ['trunk', 'A']], [3, ['trunk', 'B']]]);
  rel(p.paths[0].dp, 1528.541, 1e-6); rel(p.paths[1].dp, 1839.121, 1e-6);
  assert.equal(p.critical, 3);
  const miss = fn('bimMepPaths')(t, edges, { 0: 1, 1: 2 });
  assert.equal(miss.paths[1].dp, null);
  assert.equal(miss.critical, 2, 'a path with a missing loss is never critical');
  assert.equal(fn('bimMepPaths')(t, edges, { 0: 1, 1: 2, 2: 2 }).critical, 2, 'a tie goes to the lower node');
});
