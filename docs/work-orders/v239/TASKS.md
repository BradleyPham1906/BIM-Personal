# V239 work orders

Spec: `SPEC.md` in this folder. Implementation target: local `main`. One task at a time, top to bottom.
`[ ]` open, `[x]` done (its required checks pass), `[skipped]` left for Claude.

**Status: ready (written 2026-11-21).** Heights on one datum, and a reader for cloud-optimised GeoTIFFs. D1 and D3 are still to be answered; the tasks follow the recommendations. WO-00 is built;
the Cline tasks are independent pure functions, in any order.

Every task: change only the file named, only inside the function named. Never touch the
`import`/`export` lines, `canvas_v10.html`, or another task's function. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed.
Do not add a deliberate `WO-` throw stub; implement complete behavior.

Tests: `node --test docs/work-orders/v239/v239.test.mjs` (outside `npm test` until Claude's audit moves them
into `tests/unit/`).

---

## [x] WO-00 [Claude] Scaffold `src/js/engine/map/cog-datum.js`

Done 2026-11-21: the file with each function returning its empty value and its spec comment, its include line
in `src/index.html`, and `window.__a3dGroundData` in `src/js/engine/testing/hooks-commands-site.js`. The tests
were checked against a reference implementation (all pass); against the scaffold they fail, as they should.

---

## [ ] WO-01 [Cline] `bimTiffIfd` in `src/js/engine/map/cog-datum.js`

- **Implement:** the first IFD of a tiled TIFF, classic or BigTIFF, either byte order, as SPEC part 4 says.
- **It must:**
  - Read types 1, 2, 3, 4, 12 and 16; read an 8-byte integer as `hi * 4294967296 + lo`.
  - Apply the defaults (SamplesPerPixel, BitsPerSample, SampleFormat, Compression, Predictor, PlanarConfiguration all 1).
  - Return `null` for a non-TIFF, a striped TIFF, a BigTIFF whose bytesize is not 8, or any array past the end of `bytes`.
- **Example:** the test's 600 x 300 BigTIFF gives `offsets [1000, 2000, 3000, 4000, 5000, 6000]`, `scale [15, 15]`, `tie [0, 0, 481000, 4425000]`, `epsg 32618`, `nodata NaN`.
- **May use:** `DataView` (built in)
- **Files:** `src/js/engine/map/cog-datum.js`, `docs/work-orders/v239/v239.test.mjs`
- **Budget:** 90
- **Test:** `node --test --test-name-pattern="WO-01" docs/work-orders/v239/v239.test.mjs`
- **Done when:** `python3 tools/gate.py check v239 WO-01` passes; then `ship` it.

---

## [ ] WO-02 [Cline] `bimCogTiles` in `src/js/engine/map/cog-datum.js`

- **Implement:** the tiles a pixel window touches, clipped to the image, as SPEC part 4 says.
- **It must:**
  - Clip the window to `[0, w) x [0, h)`; return `[]` for an empty window or a missing `ifd`.
  - List tiles row by row, then column by column, as `{t, col, row, off, len}` with `t = row * ceil(w / tw) + col`.
- **Example:** for a 600 x 300 image in 256 px tiles, the window 250..260 x 250..260 touches tiles 0, 1, 3, 4.
- **May use:** `Math` (built in)
- **Files:** `src/js/engine/map/cog-datum.js`, `docs/work-orders/v239/v239.test.mjs`
- **Budget:** 25
- **Test:** `node --test --test-name-pattern="WO-02" docs/work-orders/v239/v239.test.mjs`
- **Done when:** `python3 tools/gate.py check v239 WO-02` passes; then `ship` it.

---

## [ ] WO-03 [Cline] `bimTiffUnpredict` in `src/js/engine/map/cog-datum.js`

- **Implement:** a decompressed tile as float32 samples, undoing predictor 1 or 3, as SPEC part 4 says.
- **It must:**
  - Predictor 1: read little-endian float32.
  - Predictor 3: per row, undo the byte differences with a stride of `spp`, then take each sample's four bytes from the four byte planes, most significant first.
  - Return `null` for a short buffer or another predictor.
- **Example:** the test encodes GEOID18-like values with TIFF's floating-point predictor and expects them back exactly.
- **May use:** `DataView`, `Float32Array`, `Uint8Array` (built in)
- **Files:** `src/js/engine/map/cog-datum.js`, `docs/work-orders/v239/v239.test.mjs`
- **Budget:** 40
- **Test:** `node --test --test-name-pattern="WO-03" docs/work-orders/v239/v239.test.mjs`
- **Done when:** `python3 tools/gate.py check v239 WO-03` passes; then `ship` it.

---

## [ ] WO-04 [Cline] `bimGeoidAt` in `src/js/engine/map/cog-datum.js`

- **Implement:** a geoid grid sampled bilinearly at a longitude and latitude, as SPEC part 4 says.
- **It must:**
  - Bring `lon` into `[x0, x0 + 360)`.
  - Return NaN off the grid, at a NaN node, or for bad input; on the last row or column use that node.
- **Example:** on the test's 3 x 2 grid, `bimGeoidAt(g, -129.5, 57.5)` is 5.5.
- **May use:** `Math` (built in)
- **Files:** `src/js/engine/map/cog-datum.js`, `docs/work-orders/v239/v239.test.mjs`
- **Budget:** 30
- **Test:** `node --test --test-name-pattern="WO-04" docs/work-orders/v239/v239.test.mjs`
- **Done when:** `python3 tools/gate.py check v239 WO-04` passes; then `ship` it.

---

## [ ] WO-05 [Cline] `bimDatumShift` in `src/js/engine/map/cog-datum.js`

- **Implement:** a height moved between datums, `h + N[from] - N[to]`, as SPEC part 4 says.
- **It must:**
  - Take `ellipsoid` as 0.
  - Return NaN for a bad height, a missing `N`, or a datum whose N is not a finite number.
- **Example:** `bimDatumShift(10, 'egm96', 'navd88', {egm96: -34.274, navd88: -32.979})` is 8.705.
- **May use:** nothing
- **Files:** `src/js/engine/map/cog-datum.js`, `docs/work-orders/v239/v239.test.mjs`
- **Budget:** 12
- **Test:** `node --test --test-name-pattern="WO-05" docs/work-orders/v239/v239.test.mjs`
- **Done when:** `python3 tools/gate.py check v239 WO-05` passes; then `ship` it.

---

## [ ] WO-06 [Claude] Audit WO-01 to WO-05; the registry's `geo.datums`; move the tests into `tests/unit/cog-datum.test.mjs`

## [ ] WO-07 [Claude] `bimCogRead` and `bimGeoidFetch`; each ground source's datum; Project > Location's *Heights above* row (D3); credits

## [ ] WO-08 [Claude] The browser check at 30th Street Station (`tests/e2e/`)
