# V191 work orders: LOD-D, LOD1.3 and LOD2.2 roofs from LiDAR

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/map/roofs-lidar.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v191/v191.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v191/v191.test.mjs
    node --check src/js/engine/map/roofs-lidar.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimRoofJacobi(A)`

- **It must:** SPEC 5 WO-01: the eigen-decomposition of a symmetric 3x3 by cyclic Jacobi rotations (at most 50; stop when the largest off-diagonal is under 1e-15): {values: the diagonal, vectors: the columns of the accumulated rotation, as three [x, y, z]}; the input unchanged.
- **May use:** nothing.
- **Files:** `src/js/engine/map/roofs-lidar.js`, `docs/work-orders/v191/v191.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v191/v191.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-02 [Cline] `bimRoofPlane(pts)`

- **It must:** SPEC 5 WO-02: centroid c, the covariance (divided by n), its eigenvector of the smallest eigenvalue as n, flipped so n[2] >= 0; rms the root mean square of the points' signed distances to the plane. {c, n, rms}; null for fewer than 3 points.
- **May use:** bimRoofJacobi (WO-01).
- **Files:** `src/js/engine/map/roofs-lidar.js`, `docs/work-orders/v191/v191.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v191/v191.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimRoofInRing(pts, ring)`

- **It must:** SPEC 5 WO-03: the points whose (x, y) is inside the ring (even-odd), in order.
- **May use:** nothing.
- **Files:** `src/js/engine/map/roofs-lidar.js`, `docs/work-orders/v191/v191.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v191/v191.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimRoofCoverage(pts, ring, cell)`

- **It must:** SPEC 5 WO-04: cells of size cell (1 when not positive) from the ring's minimum corner, kept while their centre is before the maximum; those whose centre is in the ring are the footprint's; the share of them holding at least one point (by floor((x - x0)/cell), floor((y - y0)/cell)); 0 for none.
- **May use:** bimRoofInRing (WO-03).
- **Files:** `src/js/engine/map/roofs-lidar.js`, `docs/work-orders/v191/v191.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v191/v191.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-05 [Cline] `bimRoofZ(pl, x, y)`

- **It must:** SPEC 5 WO-05: c[2] - (n[0](x - c[0]) + n[1](y - c[1])) / n[2]; null when |n[2]| < 1e-12.
- **May use:** nothing.
- **Files:** `src/js/engine/map/roofs-lidar.js`, `docs/work-orders/v191/v191.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v191/v191.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Claude] Region growing and the rebuilt buildings

Claude's: region growing into planes on V190's points (a work order of its own once the neighbour grid is set), the partition, LOD1.3 blocks and LOD2.2 faces, per-building RMSE and coverage in Properties; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 191, Notion.
