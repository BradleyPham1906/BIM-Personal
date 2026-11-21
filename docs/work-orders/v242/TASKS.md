# V242 work orders: Modes and the response spectrum

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/structure/modal.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v242/v242.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v242/v242.test.mjs
    node --check src/js/engine/structure/modal.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimEigJacobi(A)`

- **It must:** SPEC 5 WO-01: the eigenvalues and unit eigenvectors of a real symmetric matrix A (an array of rows) by cyclic Jacobi rotations: {error: 'not square'} unless every row has A.length entries; {error: 'not symmetric'} when some |A[i][j] - A[j][i]| exceeds 1e-9 (|A[i][j]| + |A[j][i]|). Work on a copy; sweep until the sum of squares above the diagonal is at most 1e-30 times that of the diagonal (at most 100 sweeps). Returns {values: ascending, vectors: vectors[r] the unit eigenvector of values[r]}. Example: [[2, 0], [0, 1]] gives values [1, 2].
- **May use:** nothing.
- **Files:** `src/js/engine/structure/modal.js`, `docs/work-orders/v242/v242.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v242/v242.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-02 [Cline] `bimModalLumped(K, m)`

- **It must:** SPEC 5 WO-02: the modes of K phi = w2 M phi with M diagonal, m the masses: {error: 'bad input'} unless m is non-empty and K has m.length rows; {error: 'every mass must be positive'}. A[i][j] = K[i][j] / sqrt(m[i] m[j]); bimEigJacobi(A) (its error returned as it is); for each eigenpair in order {w2, w = sqrt(max(w2, 0)), T = 2 pi / w (Infinity when w is 0), phi[i] = v[i] / sqrt(m[i])} (so phi' M phi = 1). Example: K [[80000, -40000], [-40000, 40000]], m [100, 100] gives T 0.50832 and 0.19416 s.
- **May use:** bimEigJacobi (WO-01).
- **Files:** `src/js/engine/structure/modal.js`, `docs/work-orders/v242/v242.test.mjs`
- **Budget:** 18
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v242/v242.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimModalPart(modes, m, iota)`

- **It must:** SPEC 5 WO-03: for each mode {phi}: L = sum phi_i m_i iota_i, Mn = sum phi_i m_i phi_i; gamma = L / Mn, mEff = L^2 / Mn (both 0 when Mn is 0), ratio = mEff / (sum m_i iota_i^2) (0 when that is 0). Returns [{gamma, mEff, ratio}] in the modes' order. iota is the influence vector (1 for a dof in the direction, 0 else). Example: the two-storey modes give ratios 0.9472 and 0.0528.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/modal.js`, `docs/work-orders/v242/v242.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v242/v242.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimCqcRho(wi, wj, z)`

- **It must:** SPEC 5 WO-04: Der Kiureghian's CQC coefficient for equal damping z: NaN unless wi > 0, wj > 0 and z >= 0; r = wj / wi; 8 z^2 (1 + r) r^1.5 / ((1 - r^2)^2 + 4 z^2 r (1 + r)^2). Example: (10, 5, 0.05) gives 0.01849.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/modal.js`, `docs/work-orders/v242/v242.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v242/v242.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimModalCombine(v, w, z, how)`

- **It must:** SPEC 5 WO-05: combines modal peak values v (one per mode, w their circular frequencies): how 'srss': sqrt(sum v_i^2); otherwise CQC: sqrt(max(0, sum over i and j of bimCqcRho(w_i, w_j, z) v_i v_j)). Example: [3, 4] with 'srss' gives 5.
- **May use:** bimCqcRho (WO-04).
- **Files:** `src/js/engine/structure/modal.js`, `docs/work-orders/v242/v242.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v242/v242.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Cline] `bimShearK(k)`

- **It must:** SPEC 5 WO-06: the stiffness matrix of a shear building from its storey stiffnesses k (the ground storey first): K[i][i] = k[i] + k[i+1] (k[i] alone for the top), K[i][i+1] = K[i+1][i] = -k[i+1], zeros elsewhere; [] for an empty k. Example: [3, 2, 1] gives [[5, -2, 0], [-2, 3, -1], [0, -1, 1]].
- **May use:** nothing.
- **Files:** `src/js/engine/structure/modal.js`, `docs/work-orders/v242/v242.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v242/v242.test.mjs`. **Score:** 0.

---

## [ ] WO-07 [Cline] `bimRsaScale(Vt, V)`

- **It must:** SPEC 5 WO-07: the factor applied to the spectrum's results: NaN unless Vt > 0 and V > 0; V / Vt when Vt < V, else 1. Example: (900, 1170.2) gives 1.3002.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/modal.js`, `docs/work-orders/v242/v242.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v242/v242.test.mjs`. **Score:** 0.

---

## [ ] C-08 [Claude] The wiring

The storey model, modes, the spectrum. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] C-09 [Claude] The records

PIPELINE row 242, the engineering log, Notion.
