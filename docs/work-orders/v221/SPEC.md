# V221 spec: Wind around buildings: the lattice Boltzmann reference

Notion: Later: Structural and wind analysis. Research: `docs/research/research-wind-lbm.md`, `docs/research/research-field-autonomy-supplement.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- The frame solver is done; wind starts as a CPU lattice Boltzmann reference (D2Q9 here, D3Q19 on the GPU later) that conserves mass and momentum exactly, before any GPU kernel (V219's rule).
- Results are labelled qualitative until a published benchmark (a cube in a channel) is reproduced and an expert reviews it.
- Memory planned from the research's figures: a 128-cube D3Q19 grid needs 152 MiB a buffer.

## 2. What it does for the user

Analyze, Wind: a 2D slice of the wind around the model's footprint at a height, as streamlines and a speed colour, labelled qualitative.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/analysis/lbm-ref.js` | new, after `js/engine/analysis/gpu-compute-ref.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v221/v221.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/analysis/lbm-ref.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimLbmEq(rho, ux, uy)`**: with BIM_LBM_E (the nine D2Q9 directions [0,0],[1,0],[0,1],[-1,0],[0,-1],[1,1],[-1,1],[-1,-1],[1,-1]) and BIM_LBM_W (4/9, four 1/9, four 1/36) just above it: w_i rho (1 + 3 e.u + 4.5 (e.u)^2 - 1.5 u.u) for each direction.
- **WO-02 `bimLbmMoments(f)`**: {rho: the sum, ux, uy: the sums of f e divided by rho (0 when rho is 0)}.
- **WO-03 `bimLbmStep(F, nx, ny, tau)`**: BGK collision f - (f - eq)/tau at each cell (from its moments), then streaming each direction to the neighbour cell, periodic in both axes, into a new grid of nx ny cells of 9 values.
- **WO-04 `bimLbmBytes(n, q, bytes, buffers)`**: n^3 q bytes buffers (buffers 1 unless positive).

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** the wind analysis; **WO-06** the records.

## 7. Not in this phase

3d wind before the benchmark; comfort criteria; structural wind loads.
