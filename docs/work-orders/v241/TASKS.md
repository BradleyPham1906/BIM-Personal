# V241 work orders

Spec: `SPEC.md` in this folder. Implementation target: local `main`. One task at a time, top to bottom.
`[ ]` open, `[x]` done (its required checks pass), `[skipped]` left for Claude.

**Status: ready (written 2026-11-21).** The shape of the ground: curvature, ruggedness and a viewshed. Needs no new data; the owner placed it after V202 (D4, 2026-11-21). WO-00 is built;
the Cline tasks are independent pure functions, in any order.

Every task: change only the file named, only inside the function named. Never touch the
`import`/`export` lines, `canvas_v10.html`, or another task's function. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed.
Do not add a deliberate `WO-` throw stub; implement complete behavior.

Tests: `node --test docs/work-orders/v241/v241.test.mjs` (outside `npm test` until Claude's audit moves them
into `tests/unit/`).

---

## [x] WO-00 [Claude] Scaffold `src/js/engine/terrain/terrain-shape.js`

Done 2026-11-21: the file with each function returning its empty value and its spec comment, its include line
in `src/index.html`, and `window.__a3dGroundData` in `src/js/engine/testing/hooks-commands-site.js`. The tests
were checked against a reference implementation (all pass); against the scaffold they fail, as they should.

---

## [ ] WO-01 [Cline] `bimCurvature` in `src/js/engine/terrain/terrain-shape.js`

- **Implement:** plan and profile curvature at every cell by Zevenbergen and Thorne (1987), as SPEC part 4 says.
- **It must:**
  - Use the nine-cell window with the formulas of SPEC part 4, `L = G.cell`.
  - Give 0 for both where `G'^2 + H'^2 < 1e-12`; NaN where any of the nine has no ground or is off the grid.
  - Return `{plan, profile}` as Float64Arrays.
- **Example:** on `z = 0.05 x^2 + 0.3 x` with a 2 m cell, the centre's profile curvature is -0.1 and its plan curvature 0.
- **May use:** `Math`, `Float64Array` (built in)
- **Files:** `src/js/engine/terrain/terrain-shape.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 40
- **Test:** `node --test --test-name-pattern="WO-01" docs/work-orders/v241/v241.test.mjs`
- **Done when:** `python3 tools/gate.py check v241 WO-01` passes; then `ship` it.

---

## [ ] WO-02 [Cline] `bimTri` in `src/js/engine/terrain/terrain-shape.js`

- **Implement:** the terrain ruggedness index at every cell, as SPEC part 4 says.
- **It must:**
  - Sum the squared differences to all eight neighbours and take the root.
  - NaN where the cell or any neighbour has no ground or is off the grid.
- **Example:** a 3 x 3 grid of 0 with the centre 2 and one corner 3 gives `sqrt(29)` at the centre.
- **May use:** `Math`, `Float64Array` (built in)
- **Files:** `src/js/engine/terrain/terrain-shape.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 25
- **Test:** `node --test --test-name-pattern="WO-02" docs/work-orders/v241/v241.test.mjs`
- **Done when:** `python3 tools/gate.py check v241 WO-02` passes; then `ship` it.

---

## [ ] WO-03 [Cline] `bimViewshed` in `src/js/engine/terrain/terrain-shape.js`

- **Implement:** what can be seen from a cell over the ground, by sight lines sampled at half-cell steps, as SPEC part 4 says.
- **It must:**
  - Fill with 255; leave all 255 when the observer has no ground.
  - Within `maxR` metres, mark 1 or 0 by the rule of SPEC part 4 (bilinear samples at `f = s / ceil(2 dc)`; a sample hides the target when its slope is at least the target's).
  - A sample over missing ground hides nothing.
- **Example:** on a 9-cell row with a 5 m wall at cell 4 and the eye 1.6 m up at cell 0, cells 5 to 8 are 0.
- **May use:** `Math`, `Uint8Array` (built in)
- **Files:** `src/js/engine/terrain/terrain-shape.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 55
- **Test:** `node --test --test-name-pattern="WO-03" docs/work-orders/v241/v241.test.mjs`
- **Done when:** `python3 tools/gate.py check v241 WO-03` passes; then `ship` it.

---

## [ ] WO-04 [Claude] Audit WO-01 to WO-03; the Curvature and Ruggedness runs, legends and boards in `land-water.js`; Riley's classes read in the paper; move the tests into `tests/unit/terrain-shape.test.mjs`

## [ ] WO-05 [Claude] The Viewshed run, its click and its eye and target heights in the Site bar; the browser check (`tests/e2e/`)
