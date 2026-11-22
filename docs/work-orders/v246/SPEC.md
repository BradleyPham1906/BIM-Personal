# V246 spec: Form-finding

Research: `docs/research/research-physical-world.md` (part 4.6) and `docs/research/research-physical-world/formfinding-runoff.md`; the independent check in `docs/research/research-physical-world/independent-check.md`. The owner's decisions: as the research recommends, answered 2026-11-22 (standard and scalable) (part 11 of the note; the owner, 2026-11-21: "Do your research first, properly. And then develop the work orders"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-21.

## 1. The decisions this spec follows

- The force density method first (one linear solve; Schek 1974, as compas_fd and jax_fdm implement it), dynamic relaxation with kinetic damping second (it reaches the same shape and allows rest lengths) (decision 13).
- Our own dense solve in this file; a net of a few hundred free nodes is the first target (larger nets wait for a sparse solve).
- The forms are studies; a form-found gridshell can be handed to the frame solver as members (Claude's wiring); cable nets need a truss element and tension-only iteration (later).
- As a V230 graph node later: a net in, a shape out.

## 2. What it does for the user

Model, Form-find: pick a grid of lines (or a mesh), its fixed points, a load and a force density, and the net settles into a hanging shape (negative q: a vault); dynamic relaxation shows it settle step by step; the result can become lines or members.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/analysis/form-finding.js` | new, after `js/engine/analysis/lbm-ref.js` in `src/index.html` (header done) | 3 pure functions (part 5) | Cline, WO-01 to WO-03 |
| `docs/work-orders/v246/v246.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, C-04, C-05 |

## 4. Units

m for coordinates, kN for loads, kN/m for force densities and spring stiffness, kN for edge forces.

## 5. Functions, `src/js/engine/analysis/form-finding.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file. A later function may use an earlier one of this file, as its task says.

- **WO-01 `bimFfSolve(A, B)`**: solves A X = B for several right-hand sides (B an array of rows, one per row of A) by Gaussian elimination with partial pivoting on a copy; null when a pivot's absolute value is not above 1e-12. Returns X as rows. Example: [[0, 2], [1, 1]] and [[2, 4], [3, 3]] give [[2, 1], [1, 2]].
- **WO-02 `bimFdm(o)`**: o {xyz: [[x, y, z]] per node, edges: [[i, j]], q: [one force density per edge], fixed: [node indexes], loads: [[px, py, pz]] per node (missing: 0)}. {error: 'bad input'} without nodes, edges, or with q not one per edge. Free nodes are the others, in index order. Assemble D (free x free) and the right-hand side R (free x 3, starting at the free nodes' loads): for each edge and each of its ends s with other end t, when s is free: D[s][s] += q; then D[s][t] -= q when t is free, else R[s] += q xyz[t]. X = bimFfSolve(D, R); when null, {error: 'singular: a free node has no path to a support, or q is zero'}. The result: a copy of xyz with the free nodes from X; lengths of the edges; forces = q length. Returns {xyz, lengths, forces}; the input is not changed. Example: one node on the four corners of a 2 x 2 square, q 1, load -1 in z: (1, 1, -0.25).
- **WO-03 `bimDr(o)`**: dynamic relaxation of springs: o {xyz, edges, k (stiffness per edge), rest (rest length per edge, 0 when missing), fixed, loads, tol (1e-9 when not finite), kmax (10000 unless positive)}. Work on a copy of xyz. Mass of a node: half the sum of k over its edges (1 when it has none). Residual R of a node: its load plus, for each edge to another node, fd (x_other - x_this), fd = k (L - rest) / L (k when L is 0). Start with R, velocities 0, a fresh start, previous kinetic energy 0. Each iteration: for every free node and axis, v = R/(2 m) on a fresh start, else v + R/m; x += v; sum the kinetic energy 0.5 m |v|^2. When it is below the previous: kinetic damping: for every free node and axis x = x - 1.5 v + 0.5 R/m and v = 0, the energy is 0, the next iteration is a fresh start. Keep the energy as the previous, recompute R, and when the largest |R| over the free nodes is below tol return {xyz, iterations, residual, converged: true}. After kmax iterations {xyz, iterations: kmax, residual, converged: false}. Example: the 5 x 5 net with k 1, unit loads down, reaches the centre at -1.125 in about 81 iterations.

## 6. Order of the work

WO-01 to WO-03 in order. Then Claude: **C-04** Form-find in Model: picking lines or a mesh as the net, fixed points, q and the load; the FDM result drawn, the DR settling animated, the result kept as lines or members (gridshells only to the frame solver); the test to tests/unit/; npm run modules; **C-05** the records.

## 7. Not in this phase

Thrust network analysis; prescribed lengths or forces (constrained FDM); a truss element and tension-only analysis; sparse solves for large nets; Kangaroo-style goals.
