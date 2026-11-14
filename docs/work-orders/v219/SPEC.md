# V219 spec: WebGPU compute: the CPU reference first

Notion: Later: Rendering on WebGPU. Research: `docs/research/research-notion-later-webgpu-compute.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- A GPU kernel ships only when it matches its CPU reference within a stated tolerance on the owner's devices; the renderer already uses WebGPU with a WebGL fallback, and WebGL stays the fallback here.
- The first kernel is explicit diffusion (the research's fixture: an 18 x 18 grid, 100 steps, alpha 0.24): single precision matches double to about 6e-10 at most.
- Workgroups of 8 by 8.

## 2. What it does for the user

Nothing visible at first: the simulations gain a measured GPU path, switched on only where it matches the CPU.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/analysis/gpu-compute-ref.js` | new, after `js/engine/analysis/surface-analysis.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v219/v219.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/analysis/gpu-compute-ref.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimGcDiffuse(a, n, alpha, steps, f32)`**: on an n x n grid (row-major) with a zero boundary, each step: interior c + alpha (up + down + left + right - 4 c) into a new grid; with f32 every operation rounded by Math.fround in the order ((((up + down) + left) + right) - 4c), times alpha, plus c. Returns the grid after the steps; the input unchanged.
- **WO-02 `bimGcCompare(a, b)`**: {max: the largest |a - b|, rms: the root mean square of the differences} (0 for none).
- **WO-03 `bimGcSum(a)`**: the sum.
- **WO-04 `bimGcWorkgroups(n, size)`**: ceil(n / size), size 8 unless positive.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** the gpu kernel; **WO-06** the records.

## 7. Not in this phase

The rendering layer (done); multi-gpu; webgl compute.
