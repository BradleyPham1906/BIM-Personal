# V219 work orders: WebGPU compute: the CPU reference first

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/analysis/gpu-compute-ref.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v219/v219.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v219/v219.test.mjs
    node --check src/js/engine/analysis/gpu-compute-ref.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimGcDiffuse(a, n, alpha, steps, f32)`

- **It must:** SPEC 5 WO-01: on an n x n grid (row-major) with a zero boundary, each step: interior c + alpha (up + down + left + right - 4 c) into a new grid; with f32 every operation rounded by Math.fround in the order ((((up + down) + left) + right) - 4c), times alpha, plus c. Returns the grid after the steps; the input unchanged.
- **May use:** nothing.
- **Files:** `src/js/engine/analysis/gpu-compute-ref.js`, `docs/work-orders/v219/v219.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v219/v219.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-02 [Cline] `bimGcCompare(a, b)`

- **It must:** SPEC 5 WO-02: {max: the largest |a - b|, rms: the root mean square of the differences} (0 for none).
- **May use:** nothing.
- **Files:** `src/js/engine/analysis/gpu-compute-ref.js`, `docs/work-orders/v219/v219.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v219/v219.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimGcSum(a)`

- **It must:** SPEC 5 WO-03: the sum.
- **May use:** nothing.
- **Files:** `src/js/engine/analysis/gpu-compute-ref.js`, `docs/work-orders/v219/v219.test.mjs`
- **Budget:** 4
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v219/v219.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimGcWorkgroups(n, size)`

- **It must:** SPEC 5 WO-04: ceil(n / size), size 8 unless positive.
- **May use:** nothing.
- **Files:** `src/js/engine/analysis/gpu-compute-ref.js`, `docs/work-orders/v219/v219.test.mjs`
- **Budget:** 4
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v219/v219.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] The GPU kernel

Claude's: the WGSL kernel, readback, the comparison on the owner's devices, the switch per simulation. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 219, Notion.
