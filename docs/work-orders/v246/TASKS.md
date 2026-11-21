# V246 work orders: Form-finding

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/analysis/form-finding.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v246/v246.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v246/v246.test.mjs
    node --check src/js/engine/analysis/form-finding.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimFfSolve(A, B)`

- **It must:** SPEC 5 WO-01: solves A X = B for several right-hand sides (B an array of rows, one per row of A) by Gaussian elimination with partial pivoting on a copy; null when a pivot's absolute value is not above 1e-12. Returns X as rows. Example: [[0, 2], [1, 1]] and [[2, 4], [3, 3]] give [[2, 1], [1, 2]].
- **May use:** nothing.
- **Files:** `src/js/engine/analysis/form-finding.js`, `docs/work-orders/v246/v246.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v246/v246.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimFdm(o)`

- **It must:** SPEC 5 WO-02: o {xyz: [[x, y, z]] per node, edges: [[i, j]], q: [one force density per edge], fixed: [node indexes], loads: [[px, py, pz]] per node (missing: 0)}. {error: 'bad input'} without nodes, edges, or with q not one per edge. Free nodes are the others, in index order. Assemble D (free x free) and the right-hand side R (free x 3, starting at the free nodes' loads): for each edge and each of its ends s with other end t, when s is free: D[s][s] += q; then D[s][t] -= q when t is free, else R[s] += q xyz[t]. X = bimFfSolve(D, R); when null, {error: 'singular: a free node has no path to a support, or q is zero'}. The result: a copy of xyz with the free nodes from X; lengths of the edges; forces = q length. Returns {xyz, lengths, forces}; the input is not changed. Example: one node on the four corners of a 2 x 2 square, q 1, load -1 in z: (1, 1, -0.25).
- **May use:** bimFfSolve (WO-01).
- **Files:** `src/js/engine/analysis/form-finding.js`, `docs/work-orders/v246/v246.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v246/v246.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-03 [Cline] `bimDr(o)`

- **It must:** SPEC 5 WO-03: dynamic relaxation of springs: o {xyz, edges, k (stiffness per edge), rest (rest length per edge, 0 when missing), fixed, loads, tol (1e-9 when not finite), kmax (10000 unless positive)}. Work on a copy of xyz. Mass of a node: half the sum of k over its edges (1 when it has none). Residual R of a node: its load plus, for each edge to another node, fd (x_other - x_this), fd = k (L - rest) / L (k when L is 0). Start with R, velocities 0, a fresh start, previous kinetic energy 0. Each iteration: for every free node and axis, v = R/(2 m) on a fresh start, else v + R/m; x += v; sum the kinetic energy 0.5 m |v|^2. When it is below the previous: kinetic damping: for every free node and axis x = x - 1.5 v + 0.5 R/m and v = 0, the energy is 0, the next iteration is a fresh start. Keep the energy as the previous, recompute R, and when the largest |R| over the free nodes is below tol return {xyz, iterations, residual, converged: true}. After kmax iterations {xyz, iterations: kmax, residual, converged: false}. Example: the 5 x 5 net with k 1, unit loads down, reaches the centre at -1.125 in about 81 iterations.
- **May use:** nothing.
- **Files:** `src/js/engine/analysis/form-finding.js`, `docs/work-orders/v246/v246.test.mjs`
- **Budget:** 45
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v246/v246.test.mjs`. **Score:** 0+1+0+0+2+0 = 3.

---

## [ ] C-04 [Claude] The wiring

The tool, the drawing, the hand-over. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] C-05 [Claude] The records

PIPELINE row 246, the engineering log, Notion.
