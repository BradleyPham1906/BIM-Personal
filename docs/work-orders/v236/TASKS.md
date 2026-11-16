# V236 work orders: The layout view: rooms on a bay grid, corridors from user paths, the scorecard

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/program-layout.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v236/v236.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v236/v236.test.mjs
    node --check src/js/engine/bim/program-layout.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimPlBayWidth(areas, depth, bmin, bmax, step)`

- **It must:** SPEC 5 WO-01: null unless depth is above 0 and the areas sum above 0. For b = bmin + n step (rounded to 1e-6; bmin 3, step 0.3 unless above 0; bmax at least bmin) up to bmax: each room takes k = max(1, round(area / (b depth))) bays; error = sum |k b depth - area| / sum of areas. The b with the least error (a later b replaces it only when smaller by over 1e-12): {bay, bays: [k per room], error}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-layout.js`, `docs/work-orders/v236/v236.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v236/v236.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimPlSmall(rooms, links, bay, depth, t, maxPer)`

- **It must:** SPEC 5 WO-02: rooms [{id, area}] in programme order; small when area < t bay depth (t 0.6, maxPer 3 unless above 0). A link's strength between two rooms is the least (strongest) over links not rejected (2 when none given). In order: a room not small is its own cluster; a small room joins the cluster of its most strongly linked earlier small room (ties to the lower id) whose cluster has fewer than maxPer rooms, else starts a cluster. Clusters in order of creation: {ids, area: their sum, small}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-layout.js`, `docs/work-orders/v236/v236.test.mjs`
- **Budget:** 36
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v236/v236.test.mjs`. **Score:** 0+1+0+0+1+0 = 2.

---

## [ ] WO-03 [Cline] `bimPlBands(units, bay, depth, corridor)`

- **It must:** SPEC 5 WO-03: units [{ids, k, areas}] in order. Side A takes units while its bays are below ceil(total bays / 2), the rest go to side B. K = the larger side's bays; length L = K bay. Side A from x = 0 rightwards at y 0 to depth; side B from x = L leftwards at y depth + corridor to 2 depth + corridor. A unit is k bay wide; its rooms are stacked across the band in proportion to their areas (1 each when areas are missing or not above 0), the first room against the corridor. {rooms: [{id, x, y, w, h}], length: L, spare: [K - side A's bays, K - side B's bays], corridor: {x: 0, y: depth, w: L, h: corridor}}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-layout.js`, `docs/work-orders/v236/v236.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v236/v236.test.mjs`. **Score:** 0+1+0+0+2+0 = 3.

---

## [ ] WO-04 [Cline] `bimPlWallGraph(rects, ext)`

- **It must:** SPEC 5 WO-04: vertices: every rectangle corner, and every corner of any rectangle lying on another's side strictly between its ends (a T-junction), coordinates rounded to 1e-6, numbered in order of first use (rectangles in order; each side from corner 0 to 3 round (x, y), (x + w, y), (x + w, y + h), (x, y + h); along a side, its pieces in order). Edges: one per wall piece between consecutive vertices along a side, {a, b (a < b), len, ext: true when only one rectangle side covers it, cost: len, times ext (3 unless above 0) when exterior}, numbered in order of first use. roomV and roomE: each rectangle id's vertices and edges, ascending.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-layout.js`, `docs/work-orders/v236/v236.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v236/v236.test.mjs`. **Score:** 0+1+0+0+2+0 = 3.

---

## [ ] WO-05 [Cline] `bimPlRoute(g, from, to, allowed)`

- **It must:** SPEC 5 WO-05: Dijkstra by cost from every vertex of room `from` (cost 0) to the first vertex of room `to` taken (the unvisited vertex of least cost, ties to the lowest index; an update only when cheaper by over 1e-12), over the edges whose index is a key of `allowed` (all when allowed is not given). {cost, edges: the edge indices from the start to that vertex, end: that vertex}; null when either room has no vertices or none of `to`'s is reached.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-layout.js`, `docs/work-orders/v236/v236.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v236/v236.test.mjs`. **Score:** 0+1+0+0+2+0 = 3.

---

## [ ] WO-06 [Cline] `bimPlCorridors(g, paths, opts)`

- **It must:** SPEC 5 WO-06: opts: spine 2 and door 0.9 unless given. A room's wall length on a set of edges: the sum of len of its edges in the set. For each path's consecutive rooms A, B: when B's wall length on A's edges is at least door, the leg is direct (listed, not routed). Else route A to B (bimPlRoute; none: listed as failed); then attach each end: when the room's wall length on the route's edges is below door, add the room's edge meeting the route's vertex at that end (its start for A, its end for B) preferring an interior edge, then the longest, then the first. Each path counts each edge once: use[edge] = {count, weight (primary 3, secondary 2, occasional 1, else 1)}; spine when count is at least the threshold. Spurs: the rooms (sorted ids of roomE) whose wall length on the network is below door are joined one at a time, the cheapest route from the network's vertices first (ties to the earlier in that order), with the end attached as above; each {room, edges, length: of the edges new to the network}; rooms then reached are dropped. {edges: use, direct, spurs, noAccess: the rooms left (all when there is no network), failed}.
- **May use:** bimPlRoute (WO-05).
- **Files:** `src/js/engine/bim/program-layout.js`, `docs/work-orders/v236/v236.test.mjs`
- **Budget:** 100
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v236/v236.test.mjs`. **Score:** 0+2+1+0+2+0 = 5.

---

## [ ] WO-07 [Cline] `bimPlStair(g, net, cands, demand, mode)`

- **It must:** SPEC 5 WO-07: over the edges listed in net only: for each candidate vertex, the route cost (bimPlRoute) to every room with a demand weight above 0 (sorted ids); a candidate that cannot reach one is skipped. sum = sum of weight cost, worst = the largest weight cost. mode 'centre' ranks by worst then sum, otherwise by sum then worst (differences within 1e-9 equal), then the lower vertex. {vertex, sum, worst} or null.
- **May use:** bimPlRoute (WO-05).
- **Files:** `src/js/engine/bim/program-layout.js`, `docs/work-orders/v236/v236.test.mjs`
- **Budget:** 36
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v236/v236.test.mjs`. **Score:** 0+1+0+0+1+0 = 2.

---

## [ ] WO-08 [Cline] `bimPlScore(rects, items, relations, corridorArea, floorArea)`

- **It must:** SPEC 5 WO-08: the scorecard. A room's target: the mean of areaMin and areaMax, else the one given, else none. area per id summed over its rectangles; deviation[id] = area / target - 1 for ids with a target above 0; worst: the deviation largest in size (0 when none). Relations not rejected whose rel is 'next' or absent: required ones count, and are met when their two rooms' rectangles share a wall of at least 1 m; forbidden ones broken when they do. {fill: room area / floorArea, corridorShare: corridorArea / floorArea (both null when floorArea is not above 0), deviation, worst, required, met, adjacency: met / required (null when none), forbidden}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-layout.js`, `docs/work-orders/v236/v236.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-08 ...` in `docs/work-orders/v236/v236.test.mjs`. **Score:** 0+1+0+0+1+0 = 2.

---

## [ ] WO-09 [Claude] Wiring into the app

Claude's: **WO-09** the Layout view on phone, tablet and desktop: order along the bands (follow the bubble diagram, or V234's adjacency order with swaps as e01's method B), spare floor or growth, corridor bands drawn from the edges with the registry's widths, the stair and entrances (entrance suggested by name, else highest betweenness, algorithms.md 2.10), doors, the settings and problems; every layout keyed by V228's generated-element keys so a re-run updates in place; the scorecard; the test to tests/unit/; npm run modules; the browser check. **WO-10** the records.

---

## [ ] WO-10 [Claude] The records

PIPELINE row 236, QUEUE, Notion.
