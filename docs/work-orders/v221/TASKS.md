# V221 work orders: Wind around buildings: the lattice Boltzmann reference

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/analysis/lbm-ref.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v221/v221.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v221/v221.test.mjs
    node --check src/js/engine/analysis/lbm-ref.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimLbmEq(rho, ux, uy)`

- **It must:** SPEC 5 WO-01: with BIM_LBM_E (the nine D2Q9 directions [0,0],[1,0],[0,1],[-1,0],[0,-1],[1,1],[-1,1],[-1,-1],[1,-1]) and BIM_LBM_W (4/9, four 1/9, four 1/36) just above it: w_i rho (1 + 3 e.u + 4.5 (e.u)^2 - 1.5 u.u) for each direction.
- **May use:** BIM_LBM_E, BIM_LBM_W (this task).
- **Files:** `src/js/engine/analysis/lbm-ref.js`, `docs/work-orders/v221/v221.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v221/v221.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimLbmMoments(f)`

- **It must:** SPEC 5 WO-02: {rho: the sum, ux, uy: the sums of f e divided by rho (0 when rho is 0)}.
- **May use:** BIM_LBM_E (WO-01).
- **Files:** `src/js/engine/analysis/lbm-ref.js`, `docs/work-orders/v221/v221.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v221/v221.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimLbmStep(F, nx, ny, tau)`

- **It must:** SPEC 5 WO-03: BGK collision f - (f - eq)/tau at each cell (from its moments), then streaming each direction to the neighbour cell, periodic in both axes, into a new grid of nx ny cells of 9 values.
- **May use:** bimLbmEq (WO-01), bimLbmMoments (WO-02).
- **Files:** `src/js/engine/analysis/lbm-ref.js`, `docs/work-orders/v221/v221.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v221/v221.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-04 [Cline] `bimLbmBytes(n, q, bytes, buffers)`

- **It must:** SPEC 5 WO-04: n^3 q bytes buffers (buffers 1 unless positive).
- **May use:** nothing.
- **Files:** `src/js/engine/analysis/lbm-ref.js`, `docs/work-orders/v221/v221.test.mjs`
- **Budget:** 4
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v221/v221.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] The wind analysis

Claude's: the obstacle mask from the footprints, an inlet and outlet, the slice drawn in Analyze, the benchmark reproduced before the label changes. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 221, Notion.
