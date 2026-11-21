# V242 spec: water on the ground, where it runs and where it gathers

Research: `docs/research/research-terrain-surface.md` parts 4.5 and 7. **Status: written 2026-11-21. The owner's D4 (2026-11-21): after V202.** Runs on the ground the app already has. Implementation target: local
`main`. Written by Claude.

## 1. What it does for the user

The Site bar's *Site analysis* menu gains **Water flow**:
- **Hollows:** where rain would pond, and how deep: the filled ground less the ground, tinted from 5 cm. The board
  lists each hollow's area and the volume it would hold.
- **Flow lines:** the paths water takes, drawn where at least a threshold area drains through a cell (a registry
  value, 0.5 ha by default, editable in the board), thicker as more drains through.
- **Catchment:** click a point (a drain, a swale, the low corner of a site) and the area whose rain reaches it is
  outlined, with its size in m2 and ha.
- The board says what it is: *Where water would run on this ground, by the steepest-descent rule (D8). It ignores
  pipes, kerbs below the grid's cell and soaking into the ground: a first look, not a drainage design.*

This sits beside FEMA's zones (V172), which say where floods are regulated, not where rain runs.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/terrain/ground-water.js` | new (scaffolded) | the four pure functions below | Cline (WO-01 to WO-04) |
| `src/js/engine/site-analysis/land-water.js` | changed | the Water flow run, its legend, the click | Claude (WO-05, WO-06) |
| `docs/work-orders/v242/v242.test.mjs` | new | the tests of WO-01 to WO-04 | Claude (written, checked against a reference) |

## 3. The grid and the directions

The grid is `G = {nx, nz, cell, H, ok}`, as in V241. The eight directions `d` are 0 E, 1 SE, 2 S, 3 SW, 4 W, 5 NW,
6 N and 7 NE, with steps `DI = [1, 1, 0, -1, -1, -1, 0, 1]` and `DJ = [0, 1, 1, 1, 0, -1, -1, -1]` (rows run to +z, so
`+j` is south).

## 4. Functions, in `ground-water.js`

### `bimFill(G, eps)` - WO-01 (Barnes, Lehman and Mulla 2014, priority-flood with epsilon)
1. The output starts as `H` where there is ground, NaN elsewhere.
2. Every cell with ground that is on the grid's edge, or has one of its eight neighbours without ground, is marked
   done and pushed with its own height.
3. Pop the lowest. Ties go to the one pushed first: compare the height, then the push order. For each of its eight
   neighbours on the grid, with ground and not done: mark it done, set it to `max(H, popped + eps)`, and push it with
   that height.
- **Returns:** a Float64Array. No cell is ever lower than its ground.
- Seeding the cells beside missing ground is RichDEM's choice, not the paper's (which drains no-data through a pit
  queue). The result is the same: missing ground is an outlet. The paper prefers `nextafter` to a fixed `eps`; the
  run uses `1e-4` m in float64 (the second reader, 2026-11-21).

### `bimD8(G)` - WO-02 (O'Callaghan and Mark 1984; diagonal weighting as Jenson and Domingue 1988, ArcGIS, TauDEM)
- For each cell with ground: the direction `d` whose neighbour (on the grid, with ground) gives the greatest
  `(H[k] - H[q]) / (cell * (d odd ? sqrt 2 : 1))` above 0. Ties go to the lowest `d`. -1 when no neighbour is lower,
  or the cell has no ground.
- **Returns:** an Int8Array.

### `bimFlowAcc(G, dir)` - WO-03
- Each cell with ground starts at 1 and adds everything that flows into it, following `dir`, in an order where a
  cell is added only after all its upstream cells (count the inflows; process cells with none first). NaN where
  there is no ground.
- **Returns:** a Float64Array.

### `bimCatchment(G, dir, k)` - WO-04
- 1 for `k` and for every cell whose path along `dir` reaches `k`; 0 elsewhere. All 0 when `k` is off the grid or
  has no ground.
- **Returns:** a Uint8Array.

## 5. Order of the work

1. WO-00 (Claude, done): the scaffold and the hooks.
2. WO-01 to WO-04 (Cline), in any order.
3. WO-05 (Claude): audit; the run, with `eps = 1e-4` m, on the filled ground; hollows, flow lines (marching the
   accumulation over the threshold), the legend and the registry value; the tests move into `tests/unit/`.
4. WO-06 (Claude): the catchment click; one browser check on a site with a known low point.

## 6. Not in this phase

- D-infinity flow (Tarboton 1997), which splits flow between two neighbours: later, if D8's parallel lines on
  planes bother the owner.
- Rainfall depths, runoff coefficients and pipe networks (SWMM): a drainage design, not a site study.
- Breaching instead of filling (cutting through a road embankment where a culvert would be): later, from OSM's
  `culvert` tags.
