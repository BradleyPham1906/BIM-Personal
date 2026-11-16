# V236 spec: The layout view: rooms on a bay grid, corridors from user paths, the scorecard

Research: `docs/research/research-program-to-plan.md`, `research-program-to-plan/anthropocity-features.md` and `research-program-to-plan/algorithms.md`. The owner's decisions, 2026-11-16: all ten as recommended ("just do as recommended"), and the owner's request that the programme, bubble diagram and adjacency matrix work as an engine with every feature Anthropocity documents (anthropocity-features.md maps them to phases). Implementation target: local `main`. Written by Claude, 2026-11-16.

## 1. The decisions this spec follows

- Layouts are studies, not answers: deterministic, every one carrying its scorecard (adjacency met, area deviation, corridor share, rooms with no access, forbidden pairs broken); one level and simple outlines first; no solver library (research-program-to-plan decision 4; e01: about 50% adjacency with a corridor to every room).
- Rooms take whole bays in two bands; small rooms cluster first (algorithms.md 2.7). The user chooses the typology: a spine between the bands (bimPlBands with a corridor) or corridors routed from user paths over the packed rooms (bimPlBands with none, then bimPlCorridors).
- Corridors follow walls, from user paths: direct legs need no corridor, walls walked by at least the spine threshold of paths take the main width, the remaining rooms get the shortest spur (algorithms.md 2.5; Takahashi and Matsuyama's step). Widths come from the standards registry (BB103's 1.8 and 1.2 m as the first entries).
- The stair is the corridor corner that is the weighted 1-median ('path priority') or 1-centre ('balance the worst leg') (algorithms.md 2.6).

## 2. What it does for the user

The Layout view: each building's level as a plan of scaled rooms on its bay grid, coloured by group, labelled with name, area and the change against the programme; corridors as grey bands, wider on the spine; the stair core; entrances on the facade; doors on each wall a room shares with a corridor; open rooms without a wall to the corridor; spare floor shown outside or rooms grown to fill; the layout settings; problems in plain words; the one-line scorecard. Features 32 to 41 of anthropocity-features.md.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/program-layout.js` | new, after `js/engine/bim/program-graph-lab.js` in `src/index.html` (header done) | 8 pure functions (part 5) | Cline, WO-01 to WO-08 |
| `docs/work-orders/v236/v236.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, the tasks after Cline's |

## 4. Data

A rectangle {id, x, y, w, h} in metres (x along the band, y across); a unit {ids, k, areas}; a wall graph {v: [[x, y]], e: [{a, b, len, ext, cost}], roomV, roomE}; a path as V235's. Relations and items are V179's.

## 5. Functions, `src/js/engine/bim/program-layout.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimPlBayWidth(areas, depth, bmin, bmax, step)`**: null unless depth is above 0 and the areas sum above 0. For b = bmin + n step (rounded to 1e-6; bmin 3, step 0.3 unless above 0; bmax at least bmin) up to bmax: each room takes k = max(1, round(area / (b depth))) bays; error = sum |k b depth - area| / sum of areas. The b with the least error (a later b replaces it only when smaller by over 1e-12): {bay, bays: [k per room], error}.
- **WO-02 `bimPlSmall(rooms, links, bay, depth, t, maxPer)`**: rooms [{id, area}] in programme order; small when area < t bay depth (t 0.6, maxPer 3 unless above 0). A link's strength between two rooms is the least (strongest) over links not rejected (2 when none given). In order: a room not small is its own cluster; a small room joins the cluster of its most strongly linked earlier small room (ties to the lower id) whose cluster has fewer than maxPer rooms, else starts a cluster. Clusters in order of creation: {ids, area: their sum, small}.
- **WO-03 `bimPlBands(units, bay, depth, corridor)`**: units [{ids, k, areas}] in order. Side A takes units while its bays are below ceil(total bays / 2), the rest go to side B. K = the larger side's bays; length L = K bay. Side A from x = 0 rightwards at y 0 to depth; side B from x = L leftwards at y depth + corridor to 2 depth + corridor. A unit is k bay wide; its rooms are stacked across the band in proportion to their areas (1 each when areas are missing or not above 0), the first room against the corridor. {rooms: [{id, x, y, w, h}], length: L, spare: [K - side A's bays, K - side B's bays], corridor: {x: 0, y: depth, w: L, h: corridor}}.
- **WO-04 `bimPlWallGraph(rects, ext)`**: vertices: every rectangle corner, and every corner of any rectangle lying on another's side strictly between its ends (a T-junction), coordinates rounded to 1e-6, numbered in order of first use (rectangles in order; each side from corner 0 to 3 round (x, y), (x + w, y), (x + w, y + h), (x, y + h); along a side, its pieces in order). Edges: one per wall piece between consecutive vertices along a side, {a, b (a < b), len, ext: true when only one rectangle side covers it, cost: len, times ext (3 unless above 0) when exterior}, numbered in order of first use. roomV and roomE: each rectangle id's vertices and edges, ascending.
- **WO-05 `bimPlRoute(g, from, to, allowed)`**: Dijkstra by cost from every vertex of room `from` (cost 0) to the first vertex of room `to` taken (the unvisited vertex of least cost, ties to the lowest index; an update only when cheaper by over 1e-12), over the edges whose index is a key of `allowed` (all when allowed is not given). {cost, edges: the edge indices from the start to that vertex, end: that vertex}; null when either room has no vertices or none of `to`'s is reached.
- **WO-06 `bimPlCorridors(g, paths, opts)`**: opts: spine 2 and door 0.9 unless given. A room's wall length on a set of edges: the sum of len of its edges in the set. For each path's consecutive rooms A, B: when B's wall length on A's edges is at least door, the leg is direct (listed, not routed). Else route A to B (bimPlRoute; none: listed as failed); then attach each end: when the room's wall length on the route's edges is below door, add the room's edge meeting the route's vertex at that end (its start for A, its end for B) preferring an interior edge, then the longest, then the first. Each path counts each edge once: use[edge] = {count, weight (primary 3, secondary 2, occasional 1, else 1)}; spine when count is at least the threshold. Spurs: the rooms (sorted ids of roomE) whose wall length on the network is below door are joined one at a time, the cheapest route from the network's vertices first (ties to the earlier in that order), with the end attached as above; each {room, edges, length: of the edges new to the network}; rooms then reached are dropped. {edges: use, direct, spurs, noAccess: the rooms left (all when there is no network), failed}.
- **WO-07 `bimPlStair(g, net, cands, demand, mode)`**: over the edges listed in net only: for each candidate vertex, the route cost (bimPlRoute) to every room with a demand weight above 0 (sorted ids); a candidate that cannot reach one is skipped. sum = sum of weight cost, worst = the largest weight cost. mode 'centre' ranks by worst then sum, otherwise by sum then worst (differences within 1e-9 equal), then the lower vertex. {vertex, sum, worst} or null.
- **WO-08 `bimPlScore(rects, items, relations, corridorArea, floorArea)`**: the scorecard. A room's target: the mean of areaMin and areaMax, else the one given, else none. area per id summed over its rectangles; deviation[id] = area / target - 1 for ids with a target above 0; worst: the deviation largest in size (0 when none). Relations not rejected whose rel is 'next' or absent: required ones count, and are met when their two rooms' rectangles share a wall of at least 1 m; forbidden ones broken when they do. {fill: room area / floorArea, corridorShare: corridorArea / floorArea (both null when floorArea is not above 0), deviation, worst, required, met, adjacency: met / required (null when none), forbidden}.

## 6. Order of the work

WO-01 to WO-08 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-09** the Layout view on phone, tablet and desktop: order along the bands (follow the bubble diagram, or V234's adjacency order with swaps as e01's method B), spare floor or growth, corridor bands drawn from the edges with the registry's widths, the stair and entrances (entrance suggested by name, else highest betweenness, algorithms.md 2.10), doors, the settings and problems; every layout keyed by V228's generated-element keys so a re-run updates in place; the scorecard; the test to tests/unit/; npm run modules; the browser check. **WO-10** the records.

## 7. Not in this phase

Several levels and stairs between them beyond the one core; irregular and sloped outlines; rooms other than rectangles; turning a layout into BIM walls, doors and IFC spaces (V237, after V177).
