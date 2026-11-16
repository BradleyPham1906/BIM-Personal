# V235 work orders: Graph analysis and user paths

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/program-graph-lab.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v235/v235.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v235/v235.test.mjs
    node --check src/js/engine/bim/program-graph-lab.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimGlEdges(ids, links)`

- **It must:** SPEC 5 WO-01: the network's edges: for each link in order that is an object, not rejected, joins two different ids both in `ids`, one edge per unordered pair (the first met): {a, b (a < b), w: 3, 2 or 1 for strength 1, 2 or 3, else 2}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-graph-lab.js`, `docs/work-orders/v235/v235.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v235/v235.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimGlBlocks(ids, links, minSep)`

- **It must:** SPEC 5 WO-02: Tarjan's depth-first search with low-links over bimGlEdges, neighbours sorted, roots taken in sorted id order: {articulation: the articulation points sorted, bridges: [{a, b (a < b), sides: [rooms on a's side, rooms on b's side] within that connected part]}] keeping those whose smaller side is at least minSep (1 unless above 0), sorted by 'a|b'}.
- **May use:** bimGlEdges (WO-01).
- **Files:** `src/js/engine/bim/program-graph-lab.js`, `docs/work-orders/v235/v235.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v235/v235.test.mjs`. **Score:** 0+1+0+0+2+0 = 3.

---

## [ ] WO-03 [Cline] `bimGlHubs(ids, links)`

- **It must:** SPEC 5 WO-03: hub score = the sum of a room's edge weights (bimGlEdges); {hub: {id: score} for every id, top: the highest (ties to the first in sorted order; null when no ids), max, avg: the mean over all ids (0 when none)}.
- **May use:** bimGlEdges (WO-01).
- **Files:** `src/js/engine/bim/program-graph-lab.js`, `docs/work-orders/v235/v235.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v235/v235.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimGlDepth(ids, links)`

- **It must:** SPEC 5 WO-04: hops by breadth-first search over bimGlEdges. The largest connected part (ties to the one holding the earliest sorted id); its centre the room of least eccentricity (ties to the earliest sorted id); depth: hops from the centre for every room of that part; avg and max over those rooms other than the centre (0 when none). {centre, depth, avg, max}; centre null when there are no ids.
- **May use:** bimGlEdges (WO-01).
- **Files:** `src/js/engine/bim/program-graph-lab.js`, `docs/work-orders/v235/v235.test.mjs`
- **Budget:** 36
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v235/v235.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-05 [Cline] `bimGlLouvain(ids, links, gamma)`

- **It must:** SPEC 5 WO-05: Louvain with resolution gamma (1 unless above 0), deterministic: ids sorted, weights from bimGlEdges, m their sum. Level loop: each node's degree k (self-loop weight counted twice); every node starts alone; passes visit nodes 0 to n-1, take the node out of its community, and move it to the community with the greatest gain w(C) - gamma tot(C) k / 2m among its own and its neighbours' (the community numbers ascending, a candidate replacing the best only when greater by over 1e-12), until a pass moves nothing. Nothing moved: stop. Else renumber communities by first appearance, collapse each to one node (internal weight to its self-loop), and repeat unless the count did not fall. Then split every community into its connected parts (breadth first in the original graph) and number the parts in order of their earliest sorted member. modularity = sum over parts of in(c) / m - gamma (K(c) / 2m)^2 (0 when m is 0). {community: {id: number}, count, modularity}.
- **May use:** bimGlEdges (WO-01).
- **Files:** `src/js/engine/bim/program-graph-lab.js`, `docs/work-orders/v235/v235.test.mjs`
- **Budget:** 110
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v235/v235.test.mjs`. **Score:** 0+2+0+0+2+0 = 4.

---

## [ ] WO-06 [Cline] `bimGlCoverage(paths, ids)`

- **It must:** SPEC 5 WO-06: {covered, total: ids.length, missing: the ids on no path's rooms, in ids order}; paths without rooms skipped.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-graph-lab.js`, `docs/work-orders/v235/v235.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v235/v235.test.mjs`. **Score:** 0.

---

## [ ] WO-07 [Cline] `bimGlOpenGuess(name)`

- **It must:** SPEC 5 WO-07: 'open' when any word of the name (lower case, split on anything not a to z) is one of lobby, foyer, waiting, reception, atrium, entrance, entry, concourse, lounge, corridor, circulation, vestibule; else 'closed'.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-graph-lab.js`, `docs/work-orders/v235/v235.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v235/v235.test.mjs`. **Score:** 0.

---

## [ ] WO-08 [Cline] `bimGlAxes(points)`

- **It must:** SPEC 5 WO-08: principal axes of the finite points: the angle 0.5 atan2(2 sxy, sxx - syy) of the covariance; extents of the points along that direction (major) and across it (minor); when minor is the larger they are swapped and the angle turned a quarter (minus when it was above 0, plus otherwise). {major, minor, aspect: major / minor (null when minor is not above 1e-12), angle}; {0, 0, null, 0} for fewer than two points.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-graph-lab.js`, `docs/work-orders/v235/v235.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-08 ...` in `docs/work-orders/v235/v235.test.mjs`. **Score:** 0+1+0+0+1+0 = 2.

---

## [ ] WO-09 [Cline] `bimGlSuggestPath(ids, links, start)`

- **It must:** SPEC 5 WO-09: null when start is not in ids. Else breadth first from start over the links that are not rejected and join two different ids, each room's neighbours taken strongest first (strength 1 before 2 before 3; none counts as 2), then by id: {name: 'Suggested from ' + start, rooms: the visiting order, freq: 'primary', status: 'suggested'}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/program-graph-lab.js`, `docs/work-orders/v235/v235.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-09 ...` in `docs/work-orders/v235/v235.test.mjs`. **Score:** 0+1+0+0+1+0 = 2.

---

## [ ] WO-10 [Claude] Wiring into the app

Claude's: **WO-10** Graph Lab on phone, tablet and desktop: the measures, clusters and paths drawn on V234's diagram, path editing, walk-through settings, zone diagrams, saved with the project and undone; the test to tests/unit/; npm run modules; the browser check. **WO-11** the records.

---

## [ ] WO-11 [Claude] The records

PIPELINE row 235, QUEUE, Notion.
