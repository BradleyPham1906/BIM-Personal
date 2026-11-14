# V181 spec: Interiors I3, circulation and escape routes

Notion: Interiors I1-I4 (V179-V182). Research: `docs/research/research-notion-v177-v180-interiors.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Routes are measured on a walkable grid inside the rooms around obstacles (walls, furniture), 8-way with no corner cutting, not centre to centre (the research: centre lines cut across obstacles).
- Exits are the doors the owner marks as exits; the travel limit is the owner's, from the standards registry with its edition, never a default law.
- Blocked (no route), not evaluated (no limit) and within/over are separate states with reasons; never a compliance finding.
- Grid cell 0.25 m by default, editable.

## 2. What it does for the user

Mark exits; each room shows its route to the nearest exit drawn on the plan with its length, and whether it is within the travel limit chosen, blocked or not evaluated.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/interiors-routes.js` | new, after `js/engine/bim/interiors-clearance.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v181/v181.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 5. Functions, `src/js/engine/bim/interiors-routes.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimEgGrid(poly, obstacles, cell)`**: the grid over the room's bounding box: x0, z0 its minimum corner, nx = ceil((maxX - x0)/cell - 1e-9), nz likewise; free[j*nx + i] is 1 when the cell centre (x0 + (i+0.5)cell, z0 + (j+0.5)cell) is inside the room and inside no obstacle polygon (even-odd test, written in this file as bimEgInside(p, poly)), else 0. null for fewer than 3 points or a cell not above 0. Answers {x0, z0, cell, nx, nz, free (Uint8Array)}.
- **WO-02 `bimEgCell(g, p)`**: the index j*nx + i of the cell holding p, or -1 when outside the grid or not free.
- **WO-03 `bimEgPath(g, a, b)`**: Dijkstra from a's cell to b's over free cells, 8 neighbours, a step cell long straight and cell*sqrt(2) diagonal; a diagonal only when both cells it passes beside are free; ties by the lower cell index. {len, cells from a's to b's} or null when either end is not free or b cannot be reached.
- **WO-04 `bimEgNearest(routes)`**: from {exitName: {len} or null}, the shortest {exit, len}; ties to the name first in sort order; null when none.
- **WO-05 `bimEgStatus(route, limit)`**: no route: {status: 'blocked', why: 'no route to an exit'}; no positive limit: 'not evaluated', 'no travel limit chosen'; else 'within' with why '12.3 m of 30 m' (len to one decimal), or 'over' with '45.0 m, over 30 m'.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** exits, routes on the plan, the registry's limits; **WO-07** the records.

## 7. Not in this phase

Exit capacity and occupant load; stairs and levels (routes stay on one level); fire compliance.
