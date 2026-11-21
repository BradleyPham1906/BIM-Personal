# V240 spec: the surface model (GEM-15), levelled, and heights from it

Research: `docs/research/research-terrain-surface.md` parts 4.1, 4.4 and 6. **Status: written 2026-11-21. The
owner's decision D2 (the note's part 11) is still to be answered.** Builds on V239 (the COG reader and the
datums). Implementation target: local `main`. Written by Claude.

## 1. What it does for the user

- **Site context** gains a kind, *Surface (GEM-15)*: Google's 15 m surface and terrain models, anywhere from 61 S
  to 84 N, apart from the countries it leaves out. Credit: "GEM-15: This dataset is produced by Google (CC BY 4.0)".
- **Levelled.** Where 3DEP's ground is there (the US), GEM-15's terrain is first levelled to it by the median
  offset over open cells. At 30th Street that is -3.4 m after the datum shift. The toast says *GEM-15 levelled to
  3DEP: -3.38 m over 214 open cells*. Elsewhere it says *GEM-15 not levelled (no local ground to level it to)*.
- **Heights (D2).** A building with no measured (city) and no OSM `height` takes GEM-15's: the median of the 95th
  percentile over its footprint, less the levelled ground. Then come levels, then the default. Properties says
  *34.0 m, from GEM-15 (15 m), 9 cells, spread 0.2 m*. A building whose OSM levels say over 15 storeys keeps its
  levels, because GEM-15 misses tall buildings (Google's warning, seen at two towers here).
- **Trees** with no tagged height take the 95th percentile less the ground at their point, when the cell's spread
  is over 1 m.
- **In the Analyze workspace,** a layer *Surface and canopy* shows the height above ground (p95 less the ground) as
  a tint, and the spread as a second tint: *rough (trees, edges)* against *smooth (roofs, paving)*.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/map/surface-model.js` | new (scaffolded) | the three pure functions below, then the fetch | Cline (WO-01 to WO-03), Claude (WO-04 to WO-06) |
| `src/js/engine/map/surroundings-3d.js` | changed | the height precedence (D2), trees | Claude (WO-05) |
| `docs/work-orders/v240/v240.test.mjs` | new | the tests of WO-01 to WO-03 | Claude (written, checked against a reference) |

## 3. Functions, in `surface-model.js`

### `bimGemCell(lon, lat)` - WO-01
- `x = floor(lon)`, `y = floor(lat)`, `gx = floor(lon / 10) * 10`, `gy = floor(lat / 10) * 10`.
- `group` is `s(gy) + '_' + s(gx)`, where `s(v)` is `'m' + (-v)` for a negative `v`, else `'p' + v`.
- `cell` is `'w' + c(x) + 's' + c(y)`, where `c(v)` is `'m' + (-v)` for a negative `v`, else `'' + v`.
- `dsm` and `dtm` are `'https://storage.googleapis.com/climate-and-sustainability/gem-15/' + group + '/' + cell + '/dsm/zall/mosaic.tif'`
  (and `/dtm/`).
- `null` when either input is not finite, `lat < -61` or `lat >= 84`, or `lon` is outside `[-180, 180)`.
- **Checked** against the catalog, 2026-11-21: `p30_m80/wm76s39`, `p50_m10/wm10s51`, `p50_p0/w0s50`,
  `m40_p170/w172sm35`, `m10_m80/wm71sm1`.

### `bimSurfaceOffset(pairs)` - WO-02
- **Takes:** `[{ref, dtm, dsm, std}]`: the local ground (3DEP, on the project's datum) and GEM-15's terrain, surface
  and spread at the same points, GEM-15 already moved to the project's datum.
- Keeps only pairs whose four values are finite numbers, with `|dsm - dtm| <= 1` and `std <= 1` (open ground: nothing
  stands on it).
- **Returns:** `{offset, n, mad}`. `offset` is the median of `ref - dtm`, `mad` the median of `|d - offset|`, both
  rounded to 0.01. The median of an even count is the mean of the middle two. `null` under five pairs kept.

### `bimFootprintHeight(cells, ground)` - WO-03
- **Takes:** the GEM-15 cells whose centres fall inside a footprint, `[{p95, ...}]` (levelled), and the ground at the
  footprint (levelled, on the project's datum).
- Keeps the cells whose `p95` is a finite number. `h` is the median of their `p95`, less `ground`. `spread` is the
  median of `|p95 - median|`. Both are rounded to 0.1.
- **Returns:** `{h, n, spread, from:'gem15'}`; `null` when `ground` is not finite, under three cells are kept, or
  `h < 2`.

### Claude's work (WO-04 to WO-06)
- `bimGemFetch(area)`: the cell or cells of the area. For each, the DSM's and DTM's tiles over the area, through
  V239's `bimCogRead`, in the cell's UTM zone (its `epsg`). Moved from EGM96 to the project's datum (V239).
- The levelling: 3DEP sampled at every fourth GEM-15 cell's centre, with `bimSurfaceOffset`.
- `surroundings-3d.js`: the cells inside each footprint (centre in the ring) and `bimFootprintHeight`. Trees take the
  same rule at their point. The precedence follows D2.
- The Analyze layer and the browser check at 30th Street (WO-06): the station's height against GEM-15's, and the
  toast.

## 4. Not in this phase

- Roof shapes from the surface model: 15 m is too coarse. V191 does it from LiDAR.
- Copernicus GLO-30 and Meta/WRI's canopy maps: their buckets send no CORS header (measured). They are named in the
  research, not proxied.
- Procedural detail inside a cell scaled by its spread: the app draws measured ground, not invented ground.
