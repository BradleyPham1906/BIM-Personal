# V181 work orders: Interiors I3, circulation and escape routes

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/interiors-routes.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v181/v181.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v181/v181.test.mjs
    node --check src/js/engine/bim/interiors-routes.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimEgGrid(poly, obstacles, cell)`

- **It must:** SPEC 5 WO-01: the grid over the room's bounding box: x0, z0 its minimum corner, nx = ceil((maxX - x0)/cell - 1e-9), nz likewise; free[j*nx + i] is 1 when the cell centre (x0 + (i+0.5)cell, z0 + (j+0.5)cell) is inside the room and inside no obstacle polygon (even-odd test, written in this file as bimEgInside(p, poly)), else 0. null for fewer than 3 points or a cell not above 0. Answers {x0, z0, cell, nx, nz, free (Uint8Array)}.
- **May use:** bimEgInside (this task).
- **Files:** `src/js/engine/bim/interiors-routes.js`, `docs/work-orders/v181/v181.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v181/v181.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimEgCell(g, p)`

- **It must:** SPEC 5 WO-02: the index j*nx + i of the cell holding p, or -1 when outside the grid or not free.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors-routes.js`, `docs/work-orders/v181/v181.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v181/v181.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimEgPath(g, a, b)`

- **It must:** SPEC 5 WO-03: Dijkstra from a's cell to b's over free cells, 8 neighbours, a step cell long straight and cell*sqrt(2) diagonal; a diagonal only when both cells it passes beside are free; ties by the lower cell index. {len, cells from a's to b's} or null when either end is not free or b cannot be reached.
- **May use:** bimEgCell (WO-02).
- **Files:** `src/js/engine/bim/interiors-routes.js`, `docs/work-orders/v181/v181.test.mjs`
- **Budget:** 90
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v181/v181.test.mjs`. **Score:** 0+1+0+0+2+0 = 3, tier B.

---

## [ ] WO-04 [Cline] `bimEgNearest(routes)`

- **It must:** SPEC 5 WO-04: from {exitName: {len} or null}, the shortest {exit, len}; ties to the name first in sort order; null when none.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors-routes.js`, `docs/work-orders/v181/v181.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v181/v181.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimEgStatus(route, limit)`

- **It must:** SPEC 5 WO-05: no route: {status: 'blocked', why: 'no route to an exit'}; no positive limit: 'not evaluated', 'no travel limit chosen'; else 'within' with why '12.3 m of 30 m' (len to one decimal), or 'over' with '45.0 m, over 30 m'.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors-routes.js`, `docs/work-orders/v181/v181.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v181/v181.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Claude] Exits, routes on the plan, the registry's limits

Claude's: exits marked on doors, the room outlines and obstacles from the model, the routes drawn, limits in standards/registry.js with editions; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 181, Notion.
