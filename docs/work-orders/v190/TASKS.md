# V190 work orders: LOD-C point clouds, local LAS and PLY

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function to `src/js/engine/map/pointcloud.js`, below the file's header comment, and change nothing else: not
another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`, `function`; no `let`,
`const`, arrow functions, classes or template strings. Use only the names listed; never a name from another file.
Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v190/v190.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task run its
own cases, then the file's syntax check and the unit tests (Rule #1, one file of logic):

    node --test --test-name-pattern="WO-01" docs/work-orders/v190/v190.test.mjs
    node --check src/js/engine/map/pointcloud.js
    npm test

Nothing calls these functions until Claude's first task after them, so rebuilding `canvas_v10.html` is not needed
after each one. Scores are from `../ROUTING.md` (files, logic, understanding, judgment, trickiness, check).

---

## [ ] WO-01 [Cline] `bimPcSniff(b)`

- **It must:** SPEC 4 WO-01.
- **May use:** nothing.
- **Files:** `src/js/engine/map/pointcloud.js`, `docs/work-orders/v190/v190.test.mjs`
- **Budget:** 28
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v190/v190.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimPcLasHeader(dv)`

- **It must:** SPEC part 3's byte offsets and SPEC 4 WO-02's errors in order, with `BIM_PC_MINLEN` (`{0:20,1:28,2:26,3:34,6:30,7:36,8:38}`) just above the function. Every read little-endian (`getUint16(at, true)` ...).
- **May use:** `BIM_PC_MINLEN` (this task).
- **Files:** `src/js/engine/map/pointcloud.js`, `docs/work-orders/v190/v190.test.mjs`
- **Budget:** 80
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v190/v190.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-03 [Cline] `bimPcStep(count, max)`

- **It must:** SPEC 4 WO-03.
- **May use:** nothing.
- **Files:** `src/js/engine/map/pointcloud.js`, `docs/work-orders/v190/v190.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v190/v190.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimPcLasPoints(dv, h, max, origin)`

- **It must:** SPEC 4 WO-04, with `BIM_PC_RGB` (`{2:20,3:28,7:30,8:30}`) just above the function: subtract the origin from the double-precision coordinate before storing it in the Float32Array.
- **May use:** `bimPcStep` (WO-03), `BIM_PC_RGB` (this task).
- **Files:** `src/js/engine/map/pointcloud.js`, `docs/work-orders/v190/v190.test.mjs`
- **Budget:** 70
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v190/v190.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-05 [Cline] `bimPcOrigin(h)`

- **It must:** SPEC 4 WO-05.
- **May use:** nothing.
- **Files:** `src/js/engine/map/pointcloud.js`, `docs/work-orders/v190/v190.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v190/v190.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Cline] `bimPcPlyHeader(text)`

- **It must:** SPEC part 3 and SPEC 4 WO-06.
- **May use:** nothing.
- **Files:** `src/js/engine/map/pointcloud.js`, `docs/work-orders/v190/v190.test.mjs`
- **Budget:** 70
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v190/v190.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-07 [Cline] `bimPcPlyRead(dv, at, type)`

- **It must:** SPEC 4 WO-07, with `BIM_PC_PLYSIZE` (each type's size in bytes) just above the function.
- **May use:** `BIM_PC_PLYSIZE` (this task).
- **Files:** `src/js/engine/map/pointcloud.js`, `docs/work-orders/v190/v190.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v190/v190.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-08 [Cline] `bimPcPlyPoints(bytes, h, max, origin)`

- **It must:** SPEC 4 WO-08: ASCII by lines, binary by a fixed stride; sampled and rebased as WO-04.
- **May use:** `bimPcStep` (WO-03), `bimPcPlyRead` (WO-07), `BIM_PC_PLYSIZE` (WO-07).
- **Files:** `src/js/engine/map/pointcloud.js`, `docs/work-orders/v190/v190.test.mjs`
- **Budget:** 100
- **Test:** the cases named `WO-08 ...` in `docs/work-orders/v190/v190.test.mjs`. **Score:** 0+1+0+0+2+0 = 3, tier B.

---

## [ ] WO-09 [Cline] `bimPcClassName(c)`

- **It must:** SPEC 4 WO-09, with `BIM_PC_CLASS` just above the function.
- **May use:** `BIM_PC_CLASS` (this task).
- **Files:** `src/js/engine/map/pointcloud.js`, `docs/work-orders/v190/v190.test.mjs`
- **Budget:** 28
- **Test:** the cases named `WO-09 ...` in `docs/work-orders/v190/v190.test.mjs`. **Score:** 0.

---

## [ ] WO-10 [Cline] `bimPcHeightColour(z, zmin, zmax)`

- **It must:** SPEC 4 WO-10.
- **May use:** nothing.
- **Files:** `src/js/engine/map/pointcloud.js`, `docs/work-orders/v190/v190.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-10 ...` in `docs/work-orders/v190/v190.test.mjs`. **Score:** 0.

---

## [ ] WO-11 [Cline] `bimPcGround(cloud, cell)`

- **It must:** SPEC 4 WO-11.
- **May use:** nothing.
- **Files:** `src/js/engine/map/pointcloud.js`, `docs/work-orders/v190/v190.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-11 ...` in `docs/work-orders/v190/v190.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-12 [Claude] Import and drawing

Claude's (score 2+2+2+1+2+1 = 10): SPEC part 5 WO-12. Moves `v190.test.mjs` into `tests/unit/pointcloud.test.mjs`; `npm run modules`.

---

## [ ] WO-13 [Claude] Colour modes, ground to surface, the browser check

Claude's: SPEC part 5 WO-13, the check's script in `tests/e2e/`.

---

## [ ] WO-14 [Claude] laz-perf, COPC and EPT: the next slice

Claude's: SPEC part 5 WO-14, a research note per the library rule before any order.
