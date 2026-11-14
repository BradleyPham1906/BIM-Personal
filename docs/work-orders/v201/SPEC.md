# V201 spec: MEP runs, first slice (a checked tree, straight friction only)

Research: `docs/research/research-notion-v193-mep.md` (Notion's task "V193 MEP runs"; PIPELINE orders it 201) and
the earlier `docs/research/research-mep-runs.md`. The owner's decisions, 2026-11-14, as recommended: (1) the first
deliverable is a user-checked tree analysis, one source, no loops, straight-run friction only; (2) connections are
hybrid: the app proposes joins from run ends within a tolerance (10 mm by default) and the owner confirms them, kept
with the project; (3) fittings are not generated and their losses are not invented; (4) water and air with editable
properties (water at 20 C: 998.2 kg/m3, 0.001002 Pa s; air at 20 C: 1.204 kg/m3, 1.81e-5 Pa s), roughness by
material, the transition from Re 2300 to 4000 shown as "transitional, not evaluated"; (5) rectangular ducts by
hydraulic diameter in turbulent flow only, risers counted by their 3D length, elevation (static) effects, equipment
and IFC systems deferred; (6) every result says "friction only, not the system pressure" and is not a design or
compliance figure. Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. What it does for the user

The MEP discipline gets Duct and Pipe runs: a polyline in 3D with a system (Supply air, Cold water, ...), a round
(diameter) or rectangular (width by height) inside section, and a material. Where two runs of one system end within
10 mm the app proposes a join, drawn as a node; the owner confirms. Pick the source and give each terminal its flow:
the Flow table shows each run's flow, velocity, Reynolds number, regime, Darcy factor and friction loss, and each
path from source to terminal with its friction total, the largest marked. Anything the app cannot evaluate says why.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/mep-flow.js` | new, after `dependency-graph.js` (header done) | seven pure functions (part 4) | Cline, WO-01 to WO-07 |
| `docs/work-orders/v201/v201.test.mjs` | new | their tests, on the research's published checks | Claude (done) |
| `bim/`, `drawing/`, `properties/`, `layers/` | changed | the run tool, confirmed joins, the Flow table | Claude, WO-08 to WO-10 |

## 3. Data

- **A section** `{shape: 'round'|'rect', area, perimeter, dh}` in metres: round `area = pi d^2 / 4`, `perimeter =
  pi d`, `dh = d`; rectangular `area = w h`, `perimeter = 2 (w + h)`, `dh = 2 w h / (w + h)` (`4A/P`).
- **A fluid** `{rho (kg/m3), mu (Pa s, dynamic), eps (m, roughness)}`.
- **A friction result** `{state, v, re, f, dp, why}`: `state` one of `laminar`, `turbulent`, `transitional`,
  `no flow`, `not evaluated`; `dp` in Pa (Darcy factor, never Fanning) or `null` when not evaluated.
- **A run** `{id, sys, pts: [[x, y, z], ...]}`; **a node** `{id, p: [x, y, z], sys}`; **an edge** `{run, a, b, len}`.
- **A tree** `{source, parent: {node: parent or -1}, via: {node: edge index}, order: [nodes, breadth first]}`.

## 4. Functions, `src/js/engine/bim/mep-flow.js`

- **WO-01 `bimMepSection(p)`**: part 3 for `{shape: 'round', d}` or `{shape: 'rect', w, h}` with finite positive
  sizes; else `null`.
- **WO-02 `bimMepColebrook(re, rr)`**: `null` unless `re > 4000` and `0 <= rr < 1`. With `x = 1 / sqrt(f)` and
  `g(x) = x + 2 log10(rr / 3.7 + 2.51 x / re)`: `null` unless `g(1) < 0 < g(100)`; else 100 bisection steps on
  [1, 100] (`g(mid) > 0` moves the top), `x` the midpoint, answer `{f: 1 / x^2, residual: g(x)}`.
- **WO-03 `bimMepFriction(q, sec, len, fluid)`**: `{state: 'not evaluated', why: 'bad input'}` (only those two keys)
  unless `sec` is given, `q` and `len` are finite and 0 or more, `rho > 0`, `mu > 0`, `eps >= 0`. Else `v = q / area`,
  `re = rho v dh / mu`, and the result object with `f` and `dp` `null` and `why` `''` unless set: `q === 0`: `no flow`,
  `dp` 0. `re < 2300`: round `laminar`, `f = 64 / re`; rectangular `not evaluated`, `why` `'laminar flow in a
  rectangular duct'`. `re <= 4000`: `transitional`, `why` `'Reynolds number between 2300 and 4000'`. Else
  Colebrook on `eps / dh`: `turbulent` with its `f`, or `not evaluated`, `'Colebrook did not converge'`. With an `f`:
  `dp = f (len / dh) rho v^2 / 2`.
- **WO-04 `bimMepJoin(runs, tol)`**: `tol` 0.01 m unless positive. For each run in order: fewer than 2 points:
  warning `'run <id> has fewer than 2 points'`; 3D length (sum of its segments) under 1e-9: `'run <id> has no
  length'`; its first and last points become nodes: the first existing node within `tol` (3D) of the same `sys`, else
  a new node; a node within `tol` of another `sys` adds `'different systems meet at node <n>'` and is passed over;
  start and end on one node: `'run <id> starts and ends at one node'`; else an edge `{run: id, a, b, len}`. Answers
  `{nodes, edges, warnings}`; `null` runs give all three empty.
- **WO-05 `bimMepTree(nodeCount, edges, source)`**: `{error: 'no source'}` unless `source` is a node index. Breadth
  first from the source, taking each edge once: an edge reaching a node already seen is `{error: 'loop'}`; fewer
  nodes reached than `nodeCount` is `{error: 'not connected'}`; else the tree of part 3.
- **WO-06 `bimMepFlows(tree, edges, demand)`**: from the end of `order` back to the source: a terminal (a node no
  other node has as parent) needs `demand[node]` finite and 0 or more, else `{error: 'no demand at node <n>'}`; a
  branch node adds its own positive demand, if any, to the sum of its children; each node's flow is the flow of its
  edge to its parent (`via`). Answers `{flow: {edge index: m3/s}}`.
- **WO-07 `bimMepPaths(tree, edges, loss)`**: the terminals in ascending order; for each, the runs from the source
  (first) to it and the sum of `loss[edge]` along them, `null` when any is missing. `critical`: the terminal of the
  largest non-null sum, the lower node on a tie, `null` when none. Answers `{paths: [{to, runs, dp}], critical}`.

## 5. Order of the work

WO-01 to WO-07 in order (WO-03 uses WO-02). Then Claude: **WO-08** the Duct and Pipe run tool in the MEP discipline,
its section and material in Properties, saved and undone like walls; **WO-09** proposed joins drawn and confirmed
(kept as a pair of run ends), source and terminal flows, the Flow table with its "friction only" label, and the one
browser check; **WO-10** the next slice's research: fittings from a source whose licence allows it, tees at
mid-run, elevation, IFC `IfcDistributionSystem` and ports through V177's adapter.

## 6. Not in this phase

Fitting and equipment losses; loops and looped networks; sizing; pumps and fans; drainage, refrigerant, gas;
Hazen-Williams; IFC export of systems.
