# V202 work orders

Spec: `SPEC.md` in this folder. Implementation target: local `main`. One task at a time, top to bottom.
`[ ]` open, `[x]` done (its required checks pass), `[skipped]` left for Claude.

**Status: ready.** The owner chose D1 to D5 as recommended (2026-11-13). WO-00 is built; WO-01 to
WO-05 are independent pure functions, in any order.

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

## [ ] WO-01 [Cline] `bimTiffF32` in `src/js/engine/map/measured-context.js`

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

## [ ] WO-02 [Cline] `bimDep3Url` in `src/js/engine/map/measured-context.js`

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

## [ ] WO-03 [Cline] `bimDep3ElevAt` in `src/js/engine/map/measured-context.js`

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
