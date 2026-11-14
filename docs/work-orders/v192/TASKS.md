# V192 work orders: LOD-E, facade images rectified onto walls

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/map/facade-rectify.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v192/v192.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v192/v192.test.mjs
    node --check src/js/engine/map/facade-rectify.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimFacSolve(A, b)`

- **It must:** SPEC 5 WO-01: x with A x = b by Gaussian elimination with partial pivoting on a copy; null when a pivot is under 1e-14.
- **May use:** nothing.
- **Files:** `src/js/engine/map/facade-rectify.js`, `docs/work-orders/v192/v192.test.mjs`
- **Budget:** 22
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v192/v192.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimFacNorm(pts)`

- **It must:** SPEC 5 WO-02: Hartley's normalising matrix [[s, 0, -s cx], [0, s, -s cy], [0, 0, 1]]: c the centroid, s = sqrt(2) / the mean distance from it (1 when that is under 1e-15).
- **May use:** nothing.
- **Files:** `src/js/engine/map/facade-rectify.js`, `docs/work-orders/v192/v192.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v192/v192.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimFacMul(A, B)`

- **It must:** SPEC 5 WO-03: the 3x3 product.
- **May use:** nothing.
- **Files:** `src/js/engine/map/facade-rectify.js`, `docs/work-orders/v192/v192.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v192/v192.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimFacApply(H, p)`

- **It must:** SPEC 5 WO-04: [(h00 x + h01 y + h02)/w, (h10 x + h11 y + h12)/w], w = h20 x + h21 y + h22.
- **May use:** nothing.
- **Files:** `src/js/engine/map/facade-rectify.js`, `docs/work-orders/v192/v192.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v192/v192.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimFacHomography(src, dst)`

- **It must:** SPEC 5 WO-05: null unless 4 or more pairs of equal count. Normalise both sets (WO-02), build the two rows per pair of the DLT with h22 = 1 ([x, y, 1, 0, 0, 0, -x u, -y u | u] and [0, 0, 0, x, y, 1, -x v, -y v | v]), solve the normal equations (A^T A) h = A^T b (WO-01), then H = Td^-1 Hn Ts and divide by H[2][2]. null when the solve fails.
- **May use:** bimFacSolve, bimFacNorm, bimFacMul, bimFacApply (WO-01 to WO-04).
- **Files:** `src/js/engine/map/facade-rectify.js`, `docs/work-orders/v192/v192.test.mjs`
- **Budget:** 35
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v192/v192.test.mjs`. **Score:** 0+1+0+0+2+0 = 3, tier B.

---

## [ ] WO-06 [Cline] `bimFacError(H, src, dst)`

- **It must:** SPEC 5 WO-06: {rms, max} of the distances between H(src[i]) and dst[i]; {rms: 0, max: 0} for none.
- **May use:** bimFacApply (WO-04).
- **Files:** `src/js/engine/map/facade-rectify.js`, `docs/work-orders/v192/v192.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v192/v192.test.mjs`. **Score:** 0.

---

## [ ] WO-07 [Claude] The rectify tool on walls

Claude's: picking a wall and a photo, clicking pairs and check points, the rectified texture on the wall in the rendered view, the error and the 'not for measuring' label; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-08 [Claude] The records

PIPELINE row 192, Notion.
