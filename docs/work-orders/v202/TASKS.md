# V202 work orders

Spec: `SPEC.md` in this folder. Implementation target: local `main`. One task at a time, top to bottom.
`[ ]` open, `[x]` done (its required checks pass), `[skipped]` left for Claude.

**Status: ready.** The owner chose D1 to D5 as recommended (2026-11-13). WO-00 is built; WO-01 to
WO-05 are independent pure functions, in any order.

**Part C (2026-11-21):** heights on one datum and the surface model (SPEC part C). geotiff.js is vendored;
WO-22 to WO-26 are independent pure functions in `cog-datum.js` and `surface-model.js`, tested by
`v202-datum.test.mjs` and `v202-surface.test.mjs`.

**Part B (2026-11-21):** the Site and Map interface (SPEC part B). WO-11 is built; WO-12 to WO-14 are
independent pure functions in `src/js/engine/map/site-ui.js`, tested by `v202-ui.test.mjs`.

Every task: change only the file named, only inside the function named. Never touch the
`import`/`export` lines, `canvas_v10.html`, or another task's function. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed.
Do not add a deliberate `WO-` throw stub; implement complete behavior.

Tests: `node --test docs/work-orders/v202/v202.test.mjs` (outside `npm test` until WO-06 moves them
into `tests/unit/`).

---

## [x] WO-00 [Claude] Scaffold `src/js/engine/map/measured-context.js`

Done 2026-11-13: the file (with `BIM_NBI_URL` and `bimCityRecs` too), its include line, the registry's
`ctx.heights`, `window.__a3dMeasured`; `npm run check` passes, `npm test` 259 of 259.

- Create the file and add its `<!-- @include js/engine/map/measured-context.js -->` line after `site-context.js` in `src/index.html`.
- Declare `BIM_3DEP_URL` and the five functions of WO-01 to WO-05, each returning `null` or `NaN`, with its spec comment.
- Add the registry record `ctx.heights` (Philadelphia, edition read 2026-11-13) per D2.
- Reference the five functions from `src/js/engine/testing/hooks-commands-site.js` (`window.__a3dMeasured`), so the engine exports them.
- Run `npm run modules`, the build and `npm test`.

---

## [x] WO-01 [Cline] `bimTiffF32` in `src/js/engine/map/measured-context.js`

- **Implement:** a reader for a single-band, uncompressed, float32 TIFF (strips or tiles, either byte order), as SPEC part 4 says.
- **It must:**
  - Return `{w, h, data}`, with `data` a `Float32Array(w*h)` in rows from the top.
  - Return `null` for: not a TIFF, compressed, not 32-bit float, more than one sample, a zero size, more than 16,777,216 pixels, or data past the end of the bytes.
  - Read tag values stored at an offset when they do not fit in 4 bytes.
  - Skip the padding of edge tiles.
- **Example:** an 'II' TIFF 2 x 1, one strip of the floats 1.5 and -2, returns `{w:2,h:1,data:[1.5,-2]}`.
- **May use:** `DataView`, `Float32Array` (built in)
- **Files:** `src/js/engine/map/measured-context.js`, `docs/work-orders/v202/v202.test.mjs`
- **Budget:** 70
- **Test:** `node --test --test-name-pattern="WO-01" docs/work-orders/v202/v202.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-01` passes; then `ship` it.

---

## [x] WO-02 [Cline] `bimDep3Url` in `src/js/engine/map/measured-context.js`

- **Implement:** the 3DEP `exportImage` address for an area and a grid size, exactly as SPEC part 4 writes it.
- **It must:**
  - Write the Web Mercator bbox with R = 6378137, each number `toFixed(2)`, in the order W, S, E, N.
  - Return `null` when the area is missing, or when `cols` or `rows` is not a whole number from 2 to 2000.
- **Example:** `bimDep3Url({w:1,s:1,e:2,n:2},2,2)` contains `bbox=111319.49,111325.14,222638.98,222684.21&` and `size=2,2&`.
- **May use:** `BIM_3DEP_URL` (`measured-context.js`)
- **Files:** `src/js/engine/map/measured-context.js`, `docs/work-orders/v202/v202.test.mjs`
- **Budget:** 25
- **Test:** `node --test --test-name-pattern="WO-02" docs/work-orders/v202/v202.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-02` passes; then `ship` it.

---

## [x] WO-03 [Cline] `bimDep3ElevAt` in `src/js/engine/map/measured-context.js`

- **Implement:** bilinear height from a DEM grid at a longitude and latitude, between pixel centres in Web Mercator, as SPEC part 4 says.
- **It must:**
  - Return NaN outside the grid's area.
  - Return NaN when any of the four samples used is not finite or is below -1000.
  - Clamp the neighbours at the edges.
- **Example:** at the centre of pixel (0,0) it returns `g.data[0]`; at the centre of a 2 x 2 grid, the mean of the four.
- **May use:** nothing beyond `Math`
- **Files:** `src/js/engine/map/measured-context.js`, `docs/work-orders/v202/v202.test.mjs`
- **Budget:** 30
- **Test:** `node --test --test-name-pattern="WO-03" docs/work-orders/v202/v202.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-03` passes; then `ship` it.

---

## [ ] WO-04 [Cline] `bimCityHeightPick` in `src/js/engine/map/measured-context.js`

- **Implement:** the city's measured height for an OSM footprint: the smallest city ring holding the footprint's vertex mean, in metres through `rec.unit`, as SPEC part 4 says.
- **It must:**
  - Return `null` when no ring holds the centre, or when the roof value is missing or not above 0.
  - Set `top` to null when it is not above `h`.
  - Round each number to 0.01.
- **Example:** `approx_hgt:170, max_hgt:558.2, base_elevation:34.5` at `unit:0.3048` returns `{h:51.82, top:170.14, base:10.52, from:'city', id:rec.id}`.
- **May use:** nothing beyond `Math`; write the crossing test inside the function (the gate refuses new import lines)
- **Files:** `src/js/engine/map/measured-context.js`, `docs/work-orders/v202/v202.test.mjs`
- **Budget:** 35
- **Test:** `node --test --test-name-pattern="WO-04" docs/work-orders/v202/v202.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-04` passes; then `ship` it.

---

## [ ] WO-05 [Cline] `bimNbiPick` in `src/js/engine/map/measured-context.js`

- **Implement:** the nearest NBI structure within `maxD` (30 by default) of a bridge's centreline, as its NBI record, as SPEC part 4 says.
- **It must:**
  - Measure the distance to the polyline's segments, not to its vertices.
  - Treat a value as measured only when it is finite and above 0; a clearance of 99 or more counts as none.
  - Keep the first structure on a tie.
  - Return `null` when no structure lies within `maxD`.
- **Example:** line (0,0)-(100,0) and a structure at (40,12) with clearance 6.43 returns it, with `dist:12, clear:6.43`.
- **May use:** nothing beyond `Math`
- **Files:** `src/js/engine/map/measured-context.js`, `docs/work-orders/v202/v202.test.mjs`
- **Budget:** 45
- **Test:** `node --test --test-name-pattern="WO-05" docs/work-orders/v202/v202.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-05` passes; then `ship` it.

---

## [ ] WO-06 [Claude] Audit WO-01 to WO-05; move the tests into `tests/unit/measured-context.test.mjs`

## [ ] WO-07 [Claude] The ground: `bimDep3Fetch`; 3DEP first in `bimCtxTerrain`'s caller, Terrarium as the fallback (D1)

## [ ] WO-08 [Claude] Heights: `bimCityFetch`; the precedence in `surroundings-3d.js` (D3); Properties rows; credits

## [ ] WO-09 [Claude] Bridges: `bimNbiFetch`; level decks from NBI clearance in `bimCtxSurface`; Properties rows

## [ ] WO-10 [Claude] The browser check of the site-context fetch on the Dilworth Park site (`tests/e2e/`)

---

# Part B: the Site and Map interface

## [x] WO-11 [Claude] The geometry: roads follow the ground, level bridge decks, piers to the deck; scaffold `site-ui.js`

Done 2026-11-21 (PR #116, SPEC B1): `bimCtxDense`, `bimCtxDeckProfile`, `bimCtxBridgeEnds` in
`surroundings-3d.js`, tested in `tests/unit/context-bridges.test.mjs`; `site-ui.js` with its include
line and `window.__a3dSiteUi`. The part B tests were checked against a reference implementation.

---

## [x] WO-12 [Cline] `bimCtxCards` in `src/js/engine/map/site-ui.js`

- **Implement:** the Data layers dialog's cards, as SPEC B3 says, with the table's sentences word for word.
- **It must:**
  - Return one `{kind, title, say, source, on, count}` per kind `labels` names, in `kinds`' order; `[]` for missing or empty `kinds`.
  - Set `on` only from a truthy `st.kinds[kind]` (`st` may be null); `count` only from a number in `counts` (which may be null).
- **Example:** `bimCtxCards(['buildings'], {buildings:'Buildings'}, {kinds:{buildings:true}}, {buildings:36})` returns one card, `on` true, `count` 36, `source` 'OpenStreetMap'.
- **May use:** nothing outside the file.
- **Files:** `src/js/engine/map/site-ui.js`, `docs/work-orders/v202/v202-ui.test.mjs`
- **Budget:** 30
- **Test:** `node --test --test-name-pattern="WO-12" docs/work-orders/v202/v202-ui.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-12` passes; then `ship` it.

---

## [x] WO-13 [Cline] `bimPlaceFacts` in `src/js/engine/map/site-ui.js`

- **Implement:** a context object's place card, as SPEC B3 says: title, kind, the rows in their order, credit and the OpenStreetMap link.
- **It must:**
  - Return `null` for a missing `ctx`; treat a missing `ctx.tags` as `{}`.
  - Add each row only when its value exists, in the order Height, Levels, Address, Use, Width, Deck, Built, Operator, Fetched.
  - Skip `'yes'` when choosing Use, and turn underscores into spaces.
- **Example:** a building with `height` 24.5, `heightFrom` 'height', `tags.name` '30th Street Station' gives title '30th Street Station', kind 'Building', first row `['Height','24.5 m (OpenStreetMap height)']`.
- **May use:** nothing outside the file.
- **Files:** `src/js/engine/map/site-ui.js`, `docs/work-orders/v202/v202-ui.test.mjs`
- **Budget:** 45
- **Test:** `node --test --test-name-pattern="WO-13" docs/work-orders/v202/v202-ui.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-13` passes; then `ship` it.

---

## [x] WO-14 [Cline] `bimCompass` in `src/js/engine/map/site-ui.js`

- **Implement:** the compass's needle angle, heading and letter, as SPEC B3 says.
- **It must:**
  - Return `null` when `yaw` or `trueNorth` is not finite.
  - Keep `needle` and `heading` in 0 to under 360, whatever turns `yaw` holds.
- **Example:** `bimCompass(-Math.PI/2, 0)` returns needle 270, heading 90, letter 'E'.
- **May use:** `Math` (built in)
- **Files:** `src/js/engine/map/site-ui.js`, `docs/work-orders/v202/v202-ui.test.mjs`
- **Budget:** 15
- **Test:** `node --test --test-name-pattern="WO-14" docs/work-orders/v202/v202-ui.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-14` passes; then `ship` it.

---

## [ ] WO-15 [Claude] The Site bar in the Site and Map workspace (SPEC B2.1, B2.6)

## [ ] WO-16 [Claude] The Data layers dialog from `bimCtxCards`; Properties > Site Context keeps Remove, LODs and CityJSON (B2.2)

## [ ] WO-17 [Claude] The place card from `bimPlaceFacts`; a bottom sheet on a phone (B2.3)

## [ ] WO-18 [Claude] The map controls: compass from `bimCompass`, 2D / 3D, zoom (B2.4)

## [ ] WO-19 [Claude] A quieter view: context edges off by default, the Views legend folded, view labels on hover (B2.5)

## [ ] WO-20 [Claude] The browser check of the Site and Map workspace at desktop, tablet and phone (`tests/e2e/`)

---

# Part C: heights on one datum, and the surface model

## [x] WO-21 [Claude] Vendor geotiff.js 3.0.5; scaffold `cog-datum.js` and `surface-model.js`

Done 2026-11-21: `runtime/geotiff/3.0.5/` (the browser build unchanged, LICENSE, THIRD-PARTY.txt), pinned in
`runtime/MANIFEST.json` (`tools/check_runtime.py` passes). It read GEM-15 and GEOID18 exactly as rasterio and NGS do.
The two files are scaffolded with their include lines, and `window.__a3dGroundData` is added. The tests were checked
against a reference implementation (all pass).

---

## [ ] WO-22 [Cline] `bimGeoidAt` in `src/js/engine/map/cog-datum.js`

- **Implement:** a geoid grid sampled bilinearly at a longitude and latitude, as SPEC part C3 says.
- **It must:**
  - Bring `lon` into `[x0, x0 + 360)`.
  - Return NaN off the grid, at a NaN node, or for bad input; on the last row or column use that node.
- **Example:** on the test's 3 x 2 grid, `bimGeoidAt(g, -129.5, 57.5)` is 5.5.
- **May use:** `Math` (built in)
- **Files:** `src/js/engine/map/cog-datum.js`, `docs/work-orders/v202/v202-datum.test.mjs`
- **Budget:** 30
- **Test:** `node --test --test-name-pattern="WO-22" docs/work-orders/v202/v202-datum.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-22` passes; then `ship` it.

---

## [ ] WO-23 [Cline] `bimDatumShift` in `src/js/engine/map/cog-datum.js`

- **Implement:** a height moved between datums, `h + N[from] - N[to]`, as SPEC part C3 says.
- **It must:**
  - Take `ellipsoid` as 0.
  - Return NaN for a bad height, a missing `N`, or a datum whose N is not a finite number.
- **Example:** `bimDatumShift(10, 'egm96', 'navd88', {egm96: -34.274, navd88: -32.979})` is 8.705.
- **May use:** nothing
- **Files:** `src/js/engine/map/cog-datum.js`, `docs/work-orders/v202/v202-datum.test.mjs`
- **Budget:** 12
- **Test:** `node --test --test-name-pattern="WO-23" docs/work-orders/v202/v202-datum.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-23` passes; then `ship` it.

---

## [ ] WO-24 [Cline] `bimGemCell` in `src/js/engine/map/surface-model.js`

- **Implement:** the GEM-15 cell and its two files for a longitude and latitude, as SPEC part C3 says.
- **It must:**
  - Name the group from the 10-degree tile (`p`/`m`) and the cell from the 1-degree south-west corner (`m` for negative, nothing for positive).
  - Return `null` outside 61 S to 84 N, off `[-180, 180)`, or for bad input.
- **Example:** `bimGemCell(-75.1822, 39.9557)` gives group `p30_m80`, cell `wm76s39`.
- **May use:** `Math` (built in)
- **Files:** `src/js/engine/map/surface-model.js`, `docs/work-orders/v202/v202-surface.test.mjs`
- **Budget:** 25
- **Test:** `node --test --test-name-pattern="WO-24" docs/work-orders/v202/v202-surface.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-24` passes; then `ship` it.

---

## [ ] WO-25 [Cline] `bimSurfaceOffset` in `src/js/engine/map/surface-model.js`

- **Implement:** the median offset of the local ground less GEM-15's terrain over open cells, as SPEC part C3 says.
- **It must:**
  - Keep pairs with four finite numbers, `|dsm - dtm| <= 1` and `std <= 1`.
  - Return `{offset, n, mad}` rounded to 0.01; `null` under five kept pairs; an even count takes the mean of the middle two.
- **Example:** five open pairs with ref - dtm of -2, -2.5, -1.6, -2 and -2.4 give `{offset: -2, n: 5, mad: 0.4}`.
- **May use:** `Math` (built in)
- **Files:** `src/js/engine/map/surface-model.js`, `docs/work-orders/v202/v202-surface.test.mjs`
- **Budget:** 35
- **Test:** `node --test --test-name-pattern="WO-25" docs/work-orders/v202/v202-surface.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-25` passes; then `ship` it.

---

## [ ] WO-26 [Cline] `bimFootprintHeight` in `src/js/engine/map/surface-model.js`

- **Implement:** a footprint's height: the median p95 of its cells less the ground, as SPEC part C3 says.
- **It must:**
  - Skip cells without a finite `p95`.
  - Return `{h, n, spread, from:'gem15'}` rounded to 0.1; `null` without ground, under three cells, or under 2 m.
- **Example:** five cells with p95 47.2, 46.8, 47.6, 45.1 and 47.0 over ground 13.2 give `{h: 33.8, n: 5, spread: 0.2, from: 'gem15'}`.
- **May use:** `Math` (built in)
- **Files:** `src/js/engine/map/surface-model.js`, `docs/work-orders/v202/v202-surface.test.mjs`
- **Budget:** 30
- **Test:** `node --test --test-name-pattern="WO-26" docs/work-orders/v202/v202-surface.test.mjs`
- **Done when:** `python3 tools/gate.py check v202 WO-26` passes; then `ship` it.

---

## [ ] WO-27 [Claude] Audit WO-22 to WO-26; the registry's `geo.datums`; move the tests into `tests/unit/`

## [ ] WO-28 [Claude] `bimGeotiffLoad`, `bimCogRead`, `bimGeoidFetch`; each source's datum; the project's datum from its location (D3); the Project row; credits

## [ ] WO-29 [Claude] `bimGemFetch`; the levelling against 3DEP; the height order (D2); trees; Properties rows; the toast; the credit

## [ ] WO-30 [Claude] The *Surface and canopy* layer in Analyze; the browser check at 30th Street Station (`tests/e2e/`)
