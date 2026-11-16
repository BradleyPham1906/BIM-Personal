# V234 work orders: The programme graph engine: bubble diagram, adjacency matrix, links from parameters

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/program-graph.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v234/v234.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v234/v234.test.mjs
    node --check src/js/engine/bim/program-graph.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimPgNodes(items, opts)`

- **It must:** SPEC 5 WO-01: one node per copy of each programme item with a non-empty string id (an item with count c over 1 gives ids `id#1` to `id#c`, count floored), sorted by id. area: the mean of areaMin and areaMax when both are numbers, else the one that is, else 10 (and 10 when not above 0); r = sqrt(area / pi) times opts.scale (1 unless above 0). Position: opts.saved[id] when it is two numbers; else on the phyllotaxis spiral round opts.centers[building] (default [0, 0]): for the j-th node of that building in id order, radius m sqrt(0.5 + j) and angle j pi (3 - sqrt 5), m the mean r of all nodes (1 when none), each coordinate rounded to 1e-6. opts.pins[id] (two numbers) sets fx, fy and the position. Each node {id, item, building ('' unless a string), area, r, x, y, vx: 0, vy: 0, fx, fy} (fx, fy null unless pinned).
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-graph.js`, `docs/work-orders/v234/v234.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v234/v234.test.mjs`. **Score:** 0+1+0+0+1+0 = 2.

---

## [ ] WO-02 [Cline] `bimPgGower(a, b, weights, ranges)`

- **It must:** SPEC 5 WO-02: Gower's weighted similarity of two rooms' parameter values: over the keys of weights whose weight is a number above 0 and where both a[k] and b[k] are finite numbers, sum w (1 - |a[k] - b[k]| / ranges[k]) (a term of w when ranges[k] is not above 0) and divide by the sum of those w. null when no key counts or either room is missing.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-graph.js`, `docs/work-orders/v234/v234.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v234/v234.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimPgParamLinks(items, weights, opts)`

- **It must:** SPEC 5 WO-03: suggested links from weighted parameters. Rooms: the items with a non-empty string id and at least one params key, sorted by id. ranges[k]: max minus min of the finite values of parameter k over those rooms (0 when fewer than two differ). For each pair (ids in order, a before b) S = bimPgGower; pairs with S null are left out. Keep: for each room, its first k pairs by S descending (ties by the key 'a|b' ascending) whose S is at least floor; then a maximum spanning tree: all pairs by S descending (ties by key), joined by union-find, every pair joining two components kept. Each kept pair, by key ascending: {a, b, kind: 'desired', rel: 'next', nearM: 15, strength, reason: 'similar parameters ' + S to two decimals, status: 'suggested'}, strength 1 when S is at least bands[0], 2 when at least bands[1], else 3. opts: k 2, floor 0.7, bands [0.9, 0.8] by default.
- **May use:** bimPgGower (WO-02).
- **Files:** `src/js/engine/bim/program-graph.js`, `docs/work-orders/v234/v234.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v234/v234.test.mjs`. **Score:** 0+1+0+0+2+0 = 3.

---

## [ ] WO-04 [Cline] `bimPgCollapse(relations, buildingOf)`

- **It must:** SPEC 5 WO-04: building-level links (the matrix's 'close all'): for each relation not rejected whose two rooms' buildings (buildingOf[a], buildingOf[b]) are non-empty strings and differ, one entry per building pair (names in order, a < b): {a, b, strength: the smallest strength met (2 when a relation has none), count}; sorted by 'a|b'.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-graph.js`, `docs/work-orders/v234/v234.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v234/v234.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-05 [Cline] `bimPgContain(p, r, poly)`

- **It must:** SPEC 5 WO-05: p unchanged (a new array) when poly has fewer than 3 points, or when p is inside poly (even-odd) and at least r from every edge. Otherwise: the nearest point on the polygon's edges (each edge clamped to its ends; edges shorter than 1e-9 skipped; the first nearest wins), moved r along that edge's inward normal. The winding comes from the sign of the sum over edges (from point i-1 to i) of (x[i-1] - x[i]) (y[i-1] + y[i]): positive is anticlockwise, whose inward normal is (-dy, dx) / length for an edge (dx, dy).
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-graph.js`, `docs/work-orders/v234/v234.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v234/v234.test.mjs`. **Score:** 0+1+0+0+2+0 = 3.

---

## [ ] WO-06 [Cline] `bimPgTick(sim)`

- **It must:** SPEC 5 WO-06: one step of the force simulation (the d3-force model), returning a new sim {nodes (copies), links, parents, opts, alpha} and changing nothing given. opts: charge -5, gap 0.5, pull 0.05, decay 0.0228, keep 0.6 by default. alpha becomes alpha (1 - decay). Links whose ends both exist and differ; degree counts them. Link force, per link in order: d = (b + b.v) - (a + a.v) (d = (1e-6 (i + 1), 0) when zero); s = {1: 1, 2: 0.5, 3: 0.25}[strength] (0.5 otherwise) / min(degree a, degree b); w = (|d| - (a.r + b.r + gap)) / |d| alpha s; bias = degree a / (degree a + degree b); b.v -= d w bias; a.v += d w (1 - bias). Repulsion, for every ordered pair i != j: d = b - a (d = (1e-6 (j - i), 0) when zero), l = |d|^2 at least 1, a.v += d charge alpha / l. Pull toward the building: for each node whose building is a key of parents, toward its centre (cx, cy, or the mean of the polygon's points) by (centre - p) pull alpha. Collision, for i < j: d = (b + b.v) - (a + a.v) (as above when zero), skipped when |d| >= a.r + b.r; else ov = (rsum - |d|) / |d|, f = b.r^2 / (a.r^2 + b.r^2) (0.5 when both 0); a.v -= d ov f; b.v += d ov (1 - f). Then each node: pinned (fx not null): x = fx, y = fy, v = 0; else v *= keep, p += v, and when its building has a parent, contained: a circle {cx, cy, R} holds the centre within R - r (at least 0) of (cx, cy) by moving it radially; a polygon {poly} by bimPgContain; a node moved by containment gets v = 0.
- **May use:** bimPgContain (WO-05).
- **Files:** `src/js/engine/bim/program-graph.js`, `docs/work-orders/v234/v234.test.mjs`
- **Budget:** 110
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v234/v234.test.mjs`. **Score:** 0+2+0+0+2+0 = 4.

---

## [ ] WO-07 [Cline] `bimPgSettle(sim, max)`

- **It must:** SPEC 5 WO-07: tick (bimPgTick) while the tick count is below max (300 unless above 0, floored) and alpha is at least opts.alphaMin (0.001 by default). {sim, ticks, settled: alpha below the minimum}.
- **May use:** bimPgTick (WO-06).
- **Files:** `src/js/engine/bim/program-graph.js`, `docs/work-orders/v234/v234.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v234/v234.test.mjs`. **Score:** 0.

---

## [ ] WO-08 [Claude] Wiring into the app

Claude's: **WO-08** the Programme workspace on phone, tablet and desktop (features 2 to 24, 42, 44): the views, the solver run on animation frames with the same tick, pins, the matrix, the parameter table and radar charts, the program map, building outlines, display modes, groups and merge copies, CSV import of a programme sheet (RFC 4180) and the .xlsx reader if its experiment passes (algorithms.md 2.8), pattern library as data, SVG, PDF and DXF export of each view; positions and pins saved with the project, undo; the test to tests/unit/; npm run modules; the browser check. **WO-09** the records.

---

## [ ] WO-09 [Claude] The records

PIPELINE row 234, QUEUE, Notion.
