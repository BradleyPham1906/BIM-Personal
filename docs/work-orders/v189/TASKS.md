# V189 work orders: Freeform F7, Make2D (hidden-line drawings)

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/drawing/make2d.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v189/v189.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v189/v189.test.mjs
    node --check src/js/engine/drawing/make2d.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimM2Project(p, view)`

- **It must:** SPEC 5 WO-01: [p . right, p . up, p . dir].
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/make2d.js`, `docs/work-orders/v189/v189.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v189/v189.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimM2Edges(m, dir, creaseDeg)`

- **It must:** SPEC 5 WO-02: each face's unit normal by Newell's method; each edge (smaller index first) with the faces using it, in first-met order: not exactly two faces: [a, b, 'boundary']; the two normals' dot products with dir of different sign (one < 0, one not): 'silhouette'; else the normals' dot under cos(creaseDeg) (30 when not positive): 'crease'; else left out.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/make2d.js`, `docs/work-orders/v189/v189.test.mjs`
- **Budget:** 80
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v189/v189.test.mjs`. **Score:** 0+1+0+0+2+0 = 3, tier B.

---

## [ ] WO-03 [Cline] `bimM2Hidden(p, tris, view, eps)`

- **It must:** SPEC 5 WO-03: true when some triangle, projected, contains p's projection strictly (all three barycentric weights >= eps, 1e-6 by default; degenerate ones skipped) and its interpolated depth there is less than p's depth - eps.
- **May use:** bimM2Project (WO-01).
- **Files:** `src/js/engine/drawing/make2d.js`, `docs/work-orders/v189/v189.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v189/v189.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-04 [Cline] `bimM2Visible(a, b, tris, view, samples)`

- **It must:** SPEC 5 WO-04: the segment in samples (16 when under 1) equal pieces, each kept when its midpoint is not hidden; consecutive kept pieces joined into runs; each run as its two ends projected [[x, y], [x, y]].
- **May use:** bimM2Project (WO-01), bimM2Hidden (WO-03).
- **Files:** `src/js/engine/drawing/make2d.js`, `docs/work-orders/v189/v189.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v189/v189.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-05 [Claude] The Make2D command

Claude's: the command on selected objects (meshes triangulated, edges from WO-02, runs from WO-04), lines on layers, placed or sent to a sheet; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 189, Notion.
