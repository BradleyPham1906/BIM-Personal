# V235 spec: Graph analysis and user paths

Research: `docs/research/research-program-to-plan.md`, `research-program-to-plan/anthropocity-features.md` and `research-program-to-plan/algorithms.md`. The owner's decisions, 2026-11-16: all ten as recommended ("just do as recommended"), and the owner's request that the programme, bubble diagram and adjacency matrix work as an engine with every feature Anthropocity documents (anthropocity-features.md maps them to phases). Implementation target: local `main`. Written by Claude, 2026-11-16.

## 1. The decisions this spec follows

- The programme is read as a network of V179's relations: primary links weigh 3, secondary 2, tertiary 1 (algorithms.md 2.3, 2.4).
- Clusters by Louvain with a resolution slider, deterministic (sorted ids, no shuffle), with communities in two pieces split (algorithms.md 2.3); Leiden only if users meet badly connected clusters.
- User paths are named, ordered rooms with a frequency; a suggested path is breadth first from the entrance, marked suggested until approved (decision 9; algorithms.md 2.10).
- Walk-through rooms are open, closed or guessed from the name.

## 2. What it does for the user

Graph Lab: clusters drawn on the bubble diagram with their resolution, bridges and articulation points marked, the top hub, average and maximum depth, each building's aspect; user paths drawn in colour with their frequency, added by hand or suggested, their coverage and the rooms left out; walk-through rooms set open, closed or auto; zone diagrams (functional spaces) from the clusters and groups. Features 25 to 31 of anthropocity-features.md.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/program-graph-lab.js` | new, after `js/engine/bim/program-graph.js` in `src/index.html` (header done) | 9 pure functions (part 5) | Cline, WO-01 to WO-09 |
| `docs/work-orders/v235/v235.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, the tasks after Cline's |

## 4. Data

Ids are V179 programme ids (or V234 node ids, one per copy); links are V179 relations. A path {name, rooms: [ids], freq: 'primary'|'secondary'|'occasional', status}. Points [x, y] in metres.

## 5. Functions, `src/js/engine/bim/program-graph-lab.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimGlEdges(ids, links)`**: the network's edges: for each link in order that is an object, not rejected, joins two different ids both in `ids`, one edge per unordered pair (the first met): {a, b (a < b), w: 3, 2 or 1 for strength 1, 2 or 3, else 2}.
- **WO-02 `bimGlBlocks(ids, links, minSep)`**: Tarjan's depth-first search with low-links over bimGlEdges, neighbours sorted, roots taken in sorted id order: {articulation: the articulation points sorted, bridges: [{a, b (a < b), sides: [rooms on a's side, rooms on b's side] within that connected part]}] keeping those whose smaller side is at least minSep (1 unless above 0), sorted by 'a|b'}.
- **WO-03 `bimGlHubs(ids, links)`**: hub score = the sum of a room's edge weights (bimGlEdges); {hub: {id: score} for every id, top: the highest (ties to the first in sorted order; null when no ids), max, avg: the mean over all ids (0 when none)}.
- **WO-04 `bimGlDepth(ids, links)`**: hops by breadth-first search over bimGlEdges. The largest connected part (ties to the one holding the earliest sorted id); its centre the room of least eccentricity (ties to the earliest sorted id); depth: hops from the centre for every room of that part; avg and max over those rooms other than the centre (0 when none). {centre, depth, avg, max}; centre null when there are no ids.
- **WO-05 `bimGlLouvain(ids, links, gamma)`**: Louvain with resolution gamma (1 unless above 0), deterministic: ids sorted, weights from bimGlEdges, m their sum. Level loop: each node's degree k (self-loop weight counted twice); every node starts alone; passes visit nodes 0 to n-1, take the node out of its community, and move it to the community with the greatest gain w(C) - gamma tot(C) k / 2m among its own and its neighbours' (the community numbers ascending, a candidate replacing the best only when greater by over 1e-12), until a pass moves nothing. Nothing moved: stop. Else renumber communities by first appearance, collapse each to one node (internal weight to its self-loop), and repeat unless the count did not fall. Then split every community into its connected parts (breadth first in the original graph) and number the parts in order of their earliest sorted member. modularity = sum over parts of in(c) / m - gamma (K(c) / 2m)^2 (0 when m is 0). {community: {id: number}, count, modularity}.
- **WO-06 `bimGlCoverage(paths, ids)`**: {covered, total: ids.length, missing: the ids on no path's rooms, in ids order}; paths without rooms skipped.
- **WO-07 `bimGlOpenGuess(name)`**: 'open' when any word of the name (lower case, split on anything not a to z) is one of lobby, foyer, waiting, reception, atrium, entrance, entry, concourse, lounge, corridor, circulation, vestibule; else 'closed'.
- **WO-08 `bimGlAxes(points)`**: principal axes of the finite points: the angle 0.5 atan2(2 sxy, sxx - syy) of the covariance; extents of the points along that direction (major) and across it (minor); when minor is the larger they are swapped and the angle turned a quarter (minus when it was above 0, plus otherwise). {major, minor, aspect: major / minor (null when minor is not above 1e-12), angle}; {0, 0, null, 0} for fewer than two points.
- **WO-09 `bimGlSuggestPath(ids, links, start)`**: null when start is not in ids. Else breadth first from start over the links that are not rejected and join two different ids, each room's neighbours taken strongest first (strength 1 before 2 before 3; none counts as 2), then by id: {name: 'Suggested from ' + start, rooms: the visiting order, freq: 'primary', status: 'suggested'}.

## 6. Order of the work

WO-01 to WO-09 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-10** Graph Lab on phone, tablet and desktop: the measures, clusters and paths drawn on V234's diagram, path editing, walk-through settings, zone diagrams, saved with the project and undone; the test to tests/unit/; npm run modules; the browser check. **WO-11** the records.

## 7. Not in this phase

The corridors routed from paths and the stair (V236); Leiden; paths between levels.
