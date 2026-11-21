# V242 work orders

Spec: `SPEC.md` in this folder. Implementation target: local `main`. One task at a time, top to bottom.
`[ ]` open, `[x]` done (its required checks pass), `[skipped]` left for Claude.

**Status: ready (written 2026-11-21).** Water on the ground: where it runs and where it gathers. Needs no new data; the owner placed it after V202 (D4, 2026-11-21). WO-00 is built;
the Cline tasks are independent pure functions, in any order.

Every task: change only the file named, only inside the function named. Never touch the
`import`/`export` lines, `canvas_v10.html`, or another task's function. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed.
Do not add a deliberate `WO-` throw stub; implement complete behavior.

Tests: `node --test docs/work-orders/v242/v242.test.mjs` (outside `npm test` until Claude's audit moves them
into `tests/unit/`).

---

## [x] WO-00 [Claude] Scaffold `src/js/engine/terrain/ground-water.js`

Done 2026-11-21: the file with each function returning its empty value and its spec comment, its include line
in `src/index.html`, and `window.__a3dGroundData` in `src/js/engine/testing/hooks-commands-site.js`. The tests
were checked against a reference implementation (all pass); against the scaffold they fail, as they should.

---

## [ ] WO-01 [Cline] `bimFill` in `src/js/engine/terrain/ground-water.js`

- **Implement:** the ground with its hollows filled by priority-flood with epsilon, as SPEC part 4 says.
- **It must:**
  - Seed every cell with ground on the edge or beside missing ground.
  - Pop the lowest (ties: the one pushed first); give each new neighbour `max(H, popped + eps)`.
  - Return a Float64Array; NaN where there is no ground; nothing lower than its ground.
- **Example:** the test's 5 x 5 pit with its outlet at 4 fills the pit to 5 when `eps` is 0.
- **May use:** `Math`, `Float64Array` (built in); write a small binary heap in the function
- **Files:** `src/js/engine/terrain/ground-water.js`, `docs/work-orders/v242/v242.test.mjs`
- **Budget:** 60
- **Test:** `node --test --test-name-pattern="WO-01" docs/work-orders/v242/v242.test.mjs`
- **Done when:** `python3 tools/gate.py check v242 WO-01` passes; then `ship` it.

---

## [ ] WO-02 [Cline] `bimD8` in `src/js/engine/terrain/ground-water.js`

- **Implement:** each cell's steepest way down, as SPEC part 4 says.
- **It must:**
  - Directions 0 E to 7 NE as SPEC part 3 lists; diagonals over `cell * sqrt 2`.
  - -1 at a pit, a flat or without ground; ties go to the lowest direction.
- **Example:** a centre 5 with the east neighbour 3 and the south-east 2.4 falls east (0).
- **May use:** `Math`, `Int8Array` (built in)
- **Files:** `src/js/engine/terrain/ground-water.js`, `docs/work-orders/v242/v242.test.mjs`
- **Budget:** 30
- **Test:** `node --test --test-name-pattern="WO-02" docs/work-orders/v242/v242.test.mjs`
- **Done when:** `python3 tools/gate.py check v242 WO-02` passes; then `ship` it.

---

## [ ] WO-03 [Cline] `bimFlowAcc` in `src/js/engine/terrain/ground-water.js`

- **Implement:** how many cells drain through each cell, as SPEC part 4 says.
- **It must:**
  - Count each cell's inflows; process cells with none first, adding each to the cell it drains to.
  - NaN where there is no ground.
- **Example:** a row falling 4, 3, 2, 1 gives 1, 2, 3, 4.
- **May use:** `Float64Array`, `Int32Array` (built in)
- **Files:** `src/js/engine/terrain/ground-water.js`, `docs/work-orders/v242/v242.test.mjs`
- **Budget:** 35
- **Test:** `node --test --test-name-pattern="WO-03" docs/work-orders/v242/v242.test.mjs`
- **Done when:** `python3 tools/gate.py check v242 WO-03` passes; then `ship` it.

---

## [ ] WO-04 [Cline] `bimCatchment` in `src/js/engine/terrain/ground-water.js`

- **Implement:** the cells whose water reaches a cell, as SPEC part 4 says.
- **It must:**
  - Walk the reversed directions from `k`.
  - All 0 when `k` is off the grid or has no ground.
- **Example:** on the test's V-shaped valley every cell drains to the bottom middle, so its catchment is all nine.
- **May use:** `Uint8Array` (built in)
- **Files:** `src/js/engine/terrain/ground-water.js`, `docs/work-orders/v242/v242.test.mjs`
- **Budget:** 30
- **Test:** `node --test --test-name-pattern="WO-04" docs/work-orders/v242/v242.test.mjs`
- **Done when:** `python3 tools/gate.py check v242 WO-04` passes; then `ship` it.

---

## [ ] WO-05 [Claude] Audit WO-01 to WO-04; the Water flow run (hollows, flow lines, the registry's threshold) in `land-water.js`; move the tests into `tests/unit/ground-water.test.mjs`

## [ ] WO-06 [Claude] The catchment click; the browser check on a site with a known low point (`tests/e2e/`)
