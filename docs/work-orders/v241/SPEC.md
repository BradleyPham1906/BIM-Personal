# V241 spec: the shape of the ground, curvature, ruggedness and a viewshed

Research: `docs/research/research-terrain-surface.md` parts 4.5 and 7. **Status: written 2026-11-21. No owner's
decision needed beyond D4 (the order).** Needs no new data: it runs on the ground the app already has (and on
3DEP's from V202, GEM-15's surface from V240). Implementation target: local `main`. Written by Claude.

## 1. What it does for the user

The Site bar's *Site analysis* menu (V202 part B) gains three entries beside Contours, Slope and Aspect:
- **Curvature:** where the ground is convex (ridges, shoulders: water speeds up and spreads) or concave (hollows,
  toes of slopes: water slows and gathers). Plan and profile curvature in two tints, in 1/100 m as GIS tools show it.
- **Ruggedness:** the terrain ruggedness index in metres, in a sequential tint. Riley's seven named classes were set
  for a coarse national grid (S, to be read in the paper at WO-04). They are shown only if they hold at the app's
  2 to 25 m cells; otherwise the board shows the values with quantile breaks.
- **Viewshed:** click a point. The ground it can see from 1.6 m (an editable eye height, and a target height) within
  a radius is tinted, and the rest is greyed. On the surface model (V240) buildings and trees hide what lies behind
  them. On the bare terrain, only the ground does.

Each has its legend, its method and its source in the board, as the existing analyses do.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/terrain/terrain-shape.js` | new (scaffolded) | the three pure functions below | Cline (WO-01 to WO-03) |
| `src/js/engine/site-analysis/land-water.js` | changed | the three runs, their legends, the menu entries | Claude (WO-04, WO-05) |
| `docs/work-orders/v241/v241.test.mjs` | new | the tests of WO-01 to WO-03 | Claude (written, checked against a reference) |

## 3. The grid

`G = {nx, nz, cell, H, ok}`, as `bimLandGround` gives it (`land-water.js:127`). Cell `(i, j)` is `H[j * nx + i]`; rows run
to +z, south when true north is 0. A cell has ground when `ok[k]` is true. `nb(i, j)` is `H` there, or NaN off the grid
or without ground.

## 4. Functions, in `terrain-shape.js`

### `bimCurvature(G)` - WO-01 (Zevenbergen and Thorne 1987)
- At each cell, the 3 x 3 window `z1..z9` is `nb` at (i-1, j-1), (i, j-1), (i+1, j-1), (i-1, j), (i, j), (i+1, j), (i-1, j+1), (i, j+1), (i+1, j+1). `L = G.cell`.
- `D = ((z4 + z6) / 2 - z5) / L^2`, `E = ((z2 + z8) / 2 - z5) / L^2`, `F = (-z1 + z3 + z7 - z9) / (4 L^2)`,
  `G' = (-z4 + z6) / (2 L)`, `H' = (z2 - z8) / (2 L)`, `q = G'^2 + H'^2`.
- `profile = -2 (D G'^2 + E H'^2 + F G' H') / q`; `plan = 2 (D H'^2 + E G'^2 - F G' H') / q`.
- Both are 0 when `q < 1e-12`. Both are NaN when any of the nine is NaN.
- **Signs:** Zevenbergen and Thorne's own. Positive profile curvature is upwardly convex (water speeds up), negative
  is concave (it slows). ArcGIS and RichDEM flip both signs and multiply by 100 (the second reader, 2026-11-21).
  The window's `z2` is the row above, which is north, as ZT's y is.
- **Returns:** `{plan, profile}`, two Float64Arrays of `nx * nz`.

### `bimTri(G)` - WO-02 (Riley, DeGloria and Elliot 1999)
- At each cell, `sqrt(sum over the eight neighbours of (nb - z5)^2)`. NaN when the cell or any neighbour is NaN.
- **Returns:** a Float64Array of `nx * nz`.

### `bimViewshed(G, oi, oj, eyeH, tgtH, maxR)` - WO-03
- **Returns:** a Uint8Array of `nx * nz`, filled with 255. When the observer's cell has no ground, it stays all 255.
- The eye stands at `nb(oi, oj) + eyeH`. For each cell with ground whose distance `dc` (in cells,
  `hypot(i - oi, j - oj)`) times `cell` is at most `maxR`:
  - The observer's own cell is 1.
  - Otherwise the target slope is `st = (nb(i, j) + tgtH - eye) / dc`, and the line is sampled at `m = ceil(2 dc)`
    steps. For each `s` from 1 to `m - 1`, the fraction is `f = s / m`, and `h` is bilinear at `(oi + (i - oi) f, oj + (j - oj) f)`
    from the four cells around it (the next index clamped to the grid; NaN when any of the four is NaN).
  - The cell is 0 when some sample has `h` finite and `(h - eye) / (dc f) >= st`, else 1.
- A sample over missing ground hides nothing.

## 5. Order of the work

1. WO-00 (Claude, done): the scaffold and the hooks.
2. WO-01 to WO-03 (Cline), in any order.
3. WO-04 (Claude): audit; the runs, legends and registry record; the tests move into `tests/unit/`.
4. WO-05 (Claude): the viewshed's click and its controls in the Site bar; one browser check.

## 6. Not in this phase

- Geomorphons (landform classes, Jasiewicz and Stepinski 2013): a later phase if the owner wants landform maps.
- Viewsheds from many points (cumulative visibility): later; one point is the base.
- The horizon for solar exposure from the surface model: the sun and shadow tools already use the model's buildings.
