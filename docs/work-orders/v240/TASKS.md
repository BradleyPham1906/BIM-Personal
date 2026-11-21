# V240 work orders

Spec: `SPEC.md` in this folder. Implementation target: local `main`. One task at a time, top to bottom.
`[ ]` open, `[x]` done (its required checks pass), `[skipped]` left for Claude.

**Status: ready (written 2026-11-21).** The surface model (GEM-15), levelled, and heights from it. D2 is still to be answered; the tasks follow the recommendation. Needs V239 built first for WO-04 to WO-06 (not for WO-01 to WO-03). WO-00 is built;
the Cline tasks are independent pure functions, in any order.

Every task: change only the file named, only inside the function named. Never touch the
`import`/`export` lines, `canvas_v10.html`, or another task's function. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed.
Do not add a deliberate `WO-` throw stub; implement complete behavior.

Tests: `node --test docs/work-orders/v240/v240.test.mjs` (outside `npm test` until Claude's audit moves them
into `tests/unit/`).

---

## [x] WO-00 [Claude] Scaffold `src/js/engine/map/surface-model.js`

Done 2026-11-21: the file with each function returning its empty value and its spec comment, its include line
in `src/index.html`, and `window.__a3dGroundData` in `src/js/engine/testing/hooks-commands-site.js`. The tests
were checked against a reference implementation (all pass); against the scaffold they fail, as they should.

---

## [ ] WO-01 [Cline] `bimGemCell` in `src/js/engine/map/surface-model.js`

- **Implement:** the GEM-15 cell and its two files for a longitude and latitude, as SPEC part 3 says.
- **It must:**
  - Name the group from the 10-degree tile (`p`/`m`) and the cell from the 1-degree south-west corner (`m` for negative, nothing for positive).
  - Return `null` outside 61 S to 84 N, off `[-180, 180)`, or for bad input.
- **Example:** `bimGemCell(-75.1822, 39.9557)` gives group `p30_m80`, cell `wm76s39`.
- **May use:** `Math` (built in)
- **Files:** `src/js/engine/map/surface-model.js`, `docs/work-orders/v240/v240.test.mjs`
- **Budget:** 25
- **Test:** `node --test --test-name-pattern="WO-01" docs/work-orders/v240/v240.test.mjs`
- **Done when:** `python3 tools/gate.py check v240 WO-01` passes; then `ship` it.

---

## [ ] WO-02 [Cline] `bimSurfaceOffset` in `src/js/engine/map/surface-model.js`

- **Implement:** the median offset of the local ground less GEM-15's terrain over open cells, as SPEC part 3 says.
- **It must:**
  - Keep pairs with four finite numbers, `|dsm - dtm| <= 1` and `std <= 1`.
  - Return `{offset, n, mad}` rounded to 0.01; `null` under five kept pairs; an even count takes the mean of the middle two.
- **Example:** five open pairs with ref - dtm of -2, -2.5, -1.6, -2 and -2.4 give `{offset: -2, n: 5, mad: 0.4}`.
- **May use:** `Math` (built in)
- **Files:** `src/js/engine/map/surface-model.js`, `docs/work-orders/v240/v240.test.mjs`
- **Budget:** 35
- **Test:** `node --test --test-name-pattern="WO-02" docs/work-orders/v240/v240.test.mjs`
- **Done when:** `python3 tools/gate.py check v240 WO-02` passes; then `ship` it.

---

## [ ] WO-03 [Cline] `bimFootprintHeight` in `src/js/engine/map/surface-model.js`

- **Implement:** a footprint's height: the median p95 of its cells less the ground, as SPEC part 3 says.
- **It must:**
  - Skip cells without a finite `p95`.
  - Return `{h, n, spread, from:'gem15'}` rounded to 0.1; `null` without ground, under three cells, or under 2 m.
- **Example:** five cells with p95 47.2, 46.8, 47.6, 45.1 and 47.0 over ground 13.2 give `{h: 33.8, n: 5, spread: 0.2, from: 'gem15'}`.
- **May use:** `Math` (built in)
- **Files:** `src/js/engine/map/surface-model.js`, `docs/work-orders/v240/v240.test.mjs`
- **Budget:** 30
- **Test:** `node --test --test-name-pattern="WO-03" docs/work-orders/v240/v240.test.mjs`
- **Done when:** `python3 tools/gate.py check v240 WO-03` passes; then `ship` it.

---

## [ ] WO-04 [Claude] Audit WO-01 to WO-03; `bimGemFetch` through V239's reader, in the cell's UTM zone, moved to the project's datum; move the tests into `tests/unit/surface-model.test.mjs`

## [ ] WO-05 [Claude] The levelling against 3DEP; footprint and tree heights in `surroundings-3d.js` by D2's precedence; Properties rows; the toast; the credit

## [ ] WO-06 [Claude] The *Surface and canopy* layer in Analyze; the browser check at 30th Street Station (`tests/e2e/`)
