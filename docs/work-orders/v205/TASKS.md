# V205 work orders: LOD-G, Gaussian splats as a backdrop

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/render/splats.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v205/v205.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v205/v205.test.mjs
    node --check src/js/engine/render/splats.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimSplatParse(buf)`

- **It must:** SPEC 5 WO-01: an ArrayBuffer of 32-byte splats, little-endian: position float32 x3 at 0, scale float32 x3 at 12, colour uint8 x4 at 24, rotation uint8 x4 at 28 read as (b - 128) / 128. {n, pos, scale (Float32Array n*3), rgba (Uint8Array n*4), rot (Float32Array n*4)}; a length not a multiple of 32 gives {error: 'not a .splat file (its length is not a multiple of 32)'}.
- **May use:** nothing.
- **Files:** `src/js/engine/render/splats.js`, `docs/work-orders/v205/v205.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v205/v205.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimSplatBounds(pos)`

- **It must:** SPEC 5 WO-02: {min, max, centre} of the [x, y, z] triples; null for none.
- **May use:** nothing.
- **Files:** `src/js/engine/render/splats.js`, `docs/work-orders/v205/v205.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v205/v205.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimSplatFit2(a0, a1, b0, b1)`

- **It must:** SPEC 5 WO-03: in plan (x, z): s = |b1 - b0| / |a1 - a0|, rot = the difference of their headings (atan2(dz, dx)), t = b0 - s R a0 in plan and b0[1] - s a0[1] in height. {s, rot, t}; null when either pair's plan length is under 1e-9.
- **May use:** nothing.
- **Files:** `src/js/engine/render/splats.js`, `docs/work-orders/v205/v205.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v205/v205.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimSplatApply(T, p)`

- **It must:** SPEC 5 WO-04: [s (cos x - sin z) + t0, s y + t1, s (sin x + cos z) + t2].
- **May use:** nothing.
- **Files:** `src/js/engine/render/splats.js`, `docs/work-orders/v205/v205.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v205/v205.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimSplatOrder(pos, eye)`

- **It must:** SPEC 5 WO-05: the indices sorted by squared distance from the eye, farthest first, ties by index; [] for none.
- **May use:** nothing.
- **Files:** `src/js/engine/render/splats.js`, `docs/work-orders/v205/v205.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v205/v205.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Claude] Splats in the rendered view

Claude's: import, the layer, the placement tool with its error, drawing in three.js (the rendered view) back to front, the size limit; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 205 (the old row 200), Notion.
