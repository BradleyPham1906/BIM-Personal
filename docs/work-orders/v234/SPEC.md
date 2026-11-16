# V234 spec: The programme graph engine: bubble diagram, adjacency matrix, links from parameters

Research: `docs/research/research-program-to-plan.md`, `research-program-to-plan/anthropocity-features.md` and `research-program-to-plan/algorithms.md`. The owner's decisions, 2026-11-16: all ten as recommended ("just do as recommended"), and the owner's request that the programme, bubble diagram and adjacency matrix work as an engine with every feature Anthropocity documents (anthropocity-features.md maps them to phases). Implementation target: local `main`. Written by Claude, 2026-11-16.

## 1. The decisions this spec follows

- The programme, its relations and its parameters are V179's records (amended 2026-11-16); this phase draws and edits them, it keeps no data of its own beyond positions and pins (research-program-to-plan decisions 1 and 2).
- The bubble diagram is a force simulation in the app's own ES5, after d3-force's model (ISC; read as text, not vendored): deterministic (a phyllotaxis start, no random numbers, a fixed tick schedule), rooms contained in their building's circle or polygon, pinned nodes held (algorithms.md 2.1).
- Links from parameters use Gower's weighted similarity, each room's top k above a floor and a maximum spanning tree; they are suggested until the owner approves them (algorithms.md 2.2; decision 9).
- The adjacency matrix writes strength 1 (primary) to 3, as practice and Anthropocity do; "close all" shows building-level links.

## 2. What it does for the user

The Programme workspace: the bubble diagram on the map or a blank canvas (rooms as bubbles sized by area inside their buildings, links thicker when stronger), the adjacency matrix beside it (split screen, edits live), the program table with parameters and weights and their radar charts, the program map of scaled blocks, Manage Elements, groups with colours, merge copies, levels, building outlines as bubbles or editable polygons with grid and snap and their target, current and delta areas, display modes (architecture, hybrid, planning), pins and freeze, underlays, and export of each view to SVG, PDF and DXF. Features 2 to 24, 42 and 44 of anthropocity-features.md.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/program-graph.js` | new, after `js/engine/bim/interiors-views.js` in `src/index.html` (header done) | 7 pure functions (part 5) | Cline, WO-01 to WO-07 |
| `docs/work-orders/v234/v234.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, the tasks after Cline's |

## 4. Data

A node {id, item, building, area, r, x, y, vx, vy, fx, fy}; a link {a, b, strength}; a parent {cx, cy, R} or {poly: [[x, y], ...]}; a sim {nodes, links, parents: {building: parent}, opts, alpha}. Relations are V179's (`bimIntRelation`). Positions in metres on the plan.

## 5. Functions, `src/js/engine/bim/program-graph.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimPgNodes(items, opts)`**: one node per copy of each programme item with a non-empty string id (an item with count c over 1 gives ids `id#1` to `id#c`, count floored), sorted by id. area: the mean of areaMin and areaMax when both are numbers, else the one that is, else 10 (and 10 when not above 0); r = sqrt(area / pi) times opts.scale (1 unless above 0). Position: opts.saved[id] when it is two numbers; else on the phyllotaxis spiral round opts.centers[building] (default [0, 0]): for the j-th node of that building in id order, radius m sqrt(0.5 + j) and angle j pi (3 - sqrt 5), m the mean r of all nodes (1 when none), each coordinate rounded to 1e-6. opts.pins[id] (two numbers) sets fx, fy and the position. Each node {id, item, building ('' unless a string), area, r, x, y, vx: 0, vy: 0, fx, fy} (fx, fy null unless pinned).
- **WO-02 `bimPgGower(a, b, weights, ranges)`**: Gower's weighted similarity of two rooms' parameter values: over the keys of weights whose weight is a number above 0 and where both a[k] and b[k] are finite numbers, sum w (1 - |a[k] - b[k]| / ranges[k]) (a term of w when ranges[k] is not above 0) and divide by the sum of those w. null when no key counts or either room is missing.
- **WO-03 `bimPgParamLinks(items, weights, opts)`**: suggested links from weighted parameters. Rooms: the items with a non-empty string id and at least one params key, sorted by id. ranges[k]: max minus min of the finite values of parameter k over those rooms (0 when fewer than two differ). For each pair (ids in order, a before b) S = bimPgGower; pairs with S null are left out. Keep: for each room, its first k pairs by S descending (ties by the key 'a|b' ascending) whose S is at least floor; then a maximum spanning tree: all pairs by S descending (ties by key), joined by union-find, every pair joining two components kept. Each kept pair, by key ascending: {a, b, kind: 'desired', rel: 'next', nearM: 15, strength, reason: 'similar parameters ' + S to two decimals, status: 'suggested'}, strength 1 when S is at least bands[0], 2 when at least bands[1], else 3. opts: k 2, floor 0.7, bands [0.9, 0.8] by default.
- **WO-04 `bimPgCollapse(relations, buildingOf)`**: building-level links (the matrix's 'close all'): for each relation not rejected whose two rooms' buildings (buildingOf[a], buildingOf[b]) are non-empty strings and differ, one entry per building pair (names in order, a < b): {a, b, strength: the smallest strength met (2 when a relation has none), count}; sorted by 'a|b'.
- **WO-05 `bimPgContain(p, r, poly)`**: p unchanged (a new array) when poly has fewer than 3 points, or when p is inside poly (even-odd) and at least r from every edge. Otherwise: the nearest point on the polygon's edges (each edge clamped to its ends; edges shorter than 1e-9 skipped; the first nearest wins), moved r along that edge's inward normal. The winding comes from the sign of the sum over edges (from point i-1 to i) of (x[i-1] - x[i]) (y[i-1] + y[i]): positive is anticlockwise, whose inward normal is (-dy, dx) / length for an edge (dx, dy).
- **WO-06 `bimPgTick(sim)`**: one step of the force simulation (the d3-force model), returning a new sim {nodes (copies), links, parents, opts, alpha} and changing nothing given. opts: charge -5, gap 0.5, pull 0.05, decay 0.0228, keep 0.6 by default. alpha becomes alpha (1 - decay). Links whose ends both exist and differ; degree counts them. Link force, per link in order: d = (b + b.v) - (a + a.v) (d = (1e-6 (i + 1), 0) when zero); s = {1: 1, 2: 0.5, 3: 0.25}[strength] (0.5 otherwise) / min(degree a, degree b); w = (|d| - (a.r + b.r + gap)) / |d| alpha s; bias = degree a / (degree a + degree b); b.v -= d w bias; a.v += d w (1 - bias). Repulsion, for every ordered pair i != j: d = b - a (d = (1e-6 (j - i), 0) when zero), l = |d|^2 at least 1, a.v += d charge alpha / l. Pull toward the building: for each node whose building is a key of parents, toward its centre (cx, cy, or the mean of the polygon's points) by (centre - p) pull alpha. Collision, for i < j: d = (b + b.v) - (a + a.v) (as above when zero), skipped when |d| >= a.r + b.r; else ov = (rsum - |d|) / |d|, f = b.r^2 / (a.r^2 + b.r^2) (0.5 when both 0); a.v -= d ov f; b.v += d ov (1 - f). Then each node: pinned (fx not null): x = fx, y = fy, v = 0; else v *= keep, p += v, and when its building has a parent, contained: a circle {cx, cy, R} holds the centre within R - r (at least 0) of (cx, cy) by moving it radially; a polygon {poly} by bimPgContain; a node moved by containment gets v = 0.
- **WO-07 `bimPgSettle(sim, max)`**: tick (bimPgTick) while the tick count is below max (300 unless above 0, floored) and alpha is at least opts.alphaMin (0.001 by default). {sim, ticks, settled: alpha below the minimum}.

## 6. Order of the work

WO-01 to WO-07 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-08** the Programme workspace on phone, tablet and desktop (features 2 to 24, 42, 44): the views, the solver run on animation frames with the same tick, pins, the matrix, the parameter table and radar charts, the program map, building outlines, display modes, groups and merge copies, CSV import of a programme sheet (RFC 4180) and the .xlsx reader if its experiment passes (algorithms.md 2.8), pattern library as data, SVG, PDF and DXF export of each view; positions and pins saved with the project, undo; the test to tests/unit/; npm run modules; the browser check. **WO-09** the records.

## 7. Not in this phase

Graph analysis, user paths and zone diagrams (V235); the layout view (V236); BIM spaces and IFC (V237); Excel's old .xls and PDF import (libraries, not now).
