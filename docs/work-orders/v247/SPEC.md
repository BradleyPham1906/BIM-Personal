# V247 spec: Stormwater runoff on the site

Research: `docs/research/research-physical-world.md` (part 4.7) and `docs/research/research-physical-world/formfinding-runoff.md`; the independent check in `docs/research/research-physical-world/independent-check.md`. The owner's decisions: as the research recommends (part 11 of the note; the owner, 2026-11-21: "Do your research first, properly. And then develop the work orders"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-21.

## 1. The decisions this spec follows

- The terrain TIN sampled onto a grid of about 200 cells across the site (at least 0.5 m), cells outside the TIN as NoData (Claude's wiring) (decision 14).
- Depressions filled by Priority-Flood with epsilon (Barnes, Lehman and Mulla 2014), so every cell drains; the filled areas shown as ponding, not hidden.
- D8 flow directions with diagonals at sqrt 2 (ties to the first in the order N, NE, E, SE, S, SW, W, NW), accumulation in topological order.
- Peak flow by the rational method of HEC-22 4th edition (2024), Q = C i A / 360, with a composite C; above 80 ha a warning; C ranges as a registry record with its edition and place.
- Rainfall intensity typed, or read from a NOAA Atlas 14 CSV the user pastes (no CORS: the server is named, not proxied); minimum tc 5 minutes.

## 2. What it does for the user

Analyze, Site, Runoff: flow paths and accumulation drawn on the terrain, ponding areas, and for a chosen outlet its catchment, composite C from the surfaces in it, and the peak flow for a typed rainfall intensity.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/terrain/runoff.js` | new, after `js/engine/terrain/grading.js` in `src/index.html` (header done) | 6 pure functions and the tables BIM_RUN_DR and BIM_RUN_DC (part 5) | Cline, WO-01 to WO-06 |
| `docs/work-orders/v247/v247.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, C-06, C-07 |

## 4. Units

cell size in m; elevations in m; i in mm/h; areas in ha; Q in m3/s.

## 5. Functions, `src/js/engine/terrain/runoff.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file. A later function may use an earlier one of this file, as its task says.

- **WO-01 `bimRunFill(z, nx, ny, eps)`**: with BIM_RUN_DR = [-1, -1, 0, 1, 1, 1, 0, -1] and BIM_RUN_DC = [0, 1, 1, 1, 0, -1, -1, -1] just above it (the neighbours N, NE, E, SE, S, SW, W, NW; z is row by row, row 0 north, nx columns, ny rows; z[r nx + c]). null unless z has nx ny entries. eps is 0 unless positive. Works on a copy. NoData cells (null or not finite) are left as they are and never visited. Seed a priority queue (lowest elevation first, ties in the order pushed: write a small binary heap inside the function) with every cell on the grid's edge or next to a NoData cell, marking them closed. Pop the lowest; for each unclosed neighbour inside the grid: close it, raise it to the popped cell's value + eps when it is not above it, push it. Returns the filled copy. Example: the research's 4 x 4 plane with a pit of 6.0 gives 7.001 there with eps 0.001.
- **WO-02 `bimRunD8(z, nx, ny, cell)`**: null unless z has nx ny entries; cell is 1 unless positive. For each cell, row by row: -1 when it is NoData; else the index k (0 to 7, BIM_RUN_DR and BIM_RUN_DC) of the neighbour inside the grid and not NoData with the largest drop (z - z_neighbour) / (cell, times sqrt 2 for a diagonal), only when that drop is above 0 and a later neighbour must be strictly steeper to win; -1 when no neighbour is lower. Returns the array of directions.
- **WO-03 `bimRunAccum(dir, nx, ny)`**: null unless dir has nx ny entries. Each cell starts at 1. A cell's target is the neighbour its direction points to (none for -1 or off the grid). Count each cell's inflows; start from the cells with none; take one, add its count to its target, and when the target has no inflow left take it too. null when not every cell was taken (a cycle). Returns the counts.
- **WO-04 `bimRunC(parts)`**: the composite runoff coefficient of parts [{C, area}]: NaN when a part has C outside 0 to 1 or an area below 0, or the total area is 0 (or there are no parts); else sum(C area) / sum(area).
- **WO-05 `bimRunRational(C, i, A)`**: {error: 'bad input'} unless 0 <= C <= 1, i >= 0 and A >= 0. {Q: C i A / 360 (m3/s, i in mm/h, A in ha), warn: 'over 80 ha: the rational method does not apply' when A is above 80, else ''}. Example: (0.6, 100, 2) gives Q 0.3333.

- **WO-06 `bimRunCatchment(dir, nx, ny, k)`** (added 2026-11-21, the owner's choice; `docs/research/research-terrain-surface.md`): null unless dir has nx ny entries. An array of nx ny numbers: 1 for k and every cell whose path along dir reaches k (targets as in WO-03), 0 elsewhere; walked upstream, each cell once; all 0 when k is not a whole number from 0 to nx ny - 1. Example: on WO-02's directions for the research's plane, cell 5 (the pit) gathers 8 cells, as WO-03 counts.

## 6. Order of the work

WO-01 to WO-06 in order. Then Claude: **C-06** the TIN sampled to the grid (NoData outside), the fill and its ponding, flow lines drawn by accumulation, an outlet's catchment with WO-06, C per surface from the registry's HEC-22 record, the intensity field and the pasted PFDS CSV reader, Q and its warning; the test to tests/unit/; npm run modules; **C-07** the records.

## 7. Not in this phase

D-infinity; breaching; time of concentration by the velocity method (its equation 4.3 grouping still to confirm); hydrographs; pipe networks; NOAA Atlas 15.
