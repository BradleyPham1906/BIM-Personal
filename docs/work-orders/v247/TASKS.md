# V247 work orders: Stormwater runoff on the site

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/terrain/runoff.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v247/v247.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v247/v247.test.mjs
    node --check src/js/engine/terrain/runoff.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimRunFill(z, nx, ny, eps)`

- **It must:** SPEC 5 WO-01: with BIM_RUN_DR = [-1, -1, 0, 1, 1, 1, 0, -1] and BIM_RUN_DC = [0, 1, 1, 1, 0, -1, -1, -1] just above it (the neighbours N, NE, E, SE, S, SW, W, NW; z is row by row, row 0 north, nx columns, ny rows; z[r nx + c]). null unless z has nx ny entries. eps is 0 unless positive. Works on a copy. NoData cells (null or not finite) are left as they are and never visited. Seed a priority queue (lowest elevation first, ties in the order pushed: write a small binary heap inside the function) with every cell on the grid's edge or next to a NoData cell, marking them closed. Pop the lowest; for each unclosed neighbour inside the grid: close it, raise it to the popped cell's value + eps when it is not above it, push it. Returns the filled copy. Example: the research's 4 x 4 plane with a pit of 6.0 gives 7.001 there with eps 0.001.
- **May use:** BIM_RUN_DR, BIM_RUN_DC (this task).
- **Files:** `src/js/engine/terrain/runoff.js`, `docs/work-orders/v247/v247.test.mjs`
- **Budget:** 45
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v247/v247.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-02 [Cline] `bimRunD8(z, nx, ny, cell)`

- **It must:** SPEC 5 WO-02: null unless z has nx ny entries; cell is 1 unless positive. For each cell, row by row: -1 when it is NoData; else the index k (0 to 7, BIM_RUN_DR and BIM_RUN_DC) of the neighbour inside the grid and not NoData with the largest drop (z - z_neighbour) / (cell, times sqrt 2 for a diagonal), only when that drop is above 0 and a later neighbour must be strictly steeper to win; -1 when no neighbour is lower. Returns the array of directions.
- **May use:** BIM_RUN_DR, BIM_RUN_DC (WO-01).
- **Files:** `src/js/engine/terrain/runoff.js`, `docs/work-orders/v247/v247.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v247/v247.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimRunAccum(dir, nx, ny)`

- **It must:** SPEC 5 WO-03: null unless dir has nx ny entries. Each cell starts at 1. A cell's target is the neighbour its direction points to (none for -1 or off the grid). Count each cell's inflows; start from the cells with none; take one, add its count to its target, and when the target has no inflow left take it too. null when not every cell was taken (a cycle). Returns the counts.
- **May use:** BIM_RUN_DR, BIM_RUN_DC (WO-01).
- **Files:** `src/js/engine/terrain/runoff.js`, `docs/work-orders/v247/v247.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v247/v247.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimRunC(parts)`

- **It must:** SPEC 5 WO-04: the composite runoff coefficient of parts [{C, area}]: NaN when a part has C outside 0 to 1 or an area below 0, or the total area is 0 (or there are no parts); else sum(C area) / sum(area).
- **May use:** nothing.
- **Files:** `src/js/engine/terrain/runoff.js`, `docs/work-orders/v247/v247.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v247/v247.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimRunRational(C, i, A)`

- **It must:** SPEC 5 WO-05: {error: 'bad input'} unless 0 <= C <= 1, i >= 0 and A >= 0. {Q: C i A / 360 (m3/s, i in mm/h, A in ha), warn: 'over 80 ha: the rational method does not apply' when A is above 80, else ''}. Example: (0.6, 100, 2) gives Q 0.3333.
- **May use:** nothing.
- **Files:** `src/js/engine/terrain/runoff.js`, `docs/work-orders/v247/v247.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v247/v247.test.mjs`. **Score:** 0.

---

## [ ] C-06 [Claude] The wiring

The grid, the drawing, the catchment and Q. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] C-07 [Claude] The records

PIPELINE row 247, the engineering log, Notion.
