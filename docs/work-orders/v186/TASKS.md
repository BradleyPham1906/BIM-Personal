# V186 work orders: Freeform F4, surface analysis

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/analysis/surface-analysis.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v186/v186.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v186/v186.test.mjs
    node --check src/js/engine/analysis/surface-analysis.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimAnFaceNormal(v, face)`

- **It must:** SPEC 5 WO-01: Newell's method over the face's vertex indices: n = sum over edges a to b of ((ay - by)(az + bz), (az - bz)(ax + bx), (ax - bx)(ay + by)); {n: n normalised ([0, 0, 0] when its length is under 1e-15), area: |n| / 2}.
- **May use:** nothing.
- **Files:** `src/js/engine/analysis/surface-analysis.js`, `docs/work-orders/v186/v186.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v186/v186.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimAnVertexNormals(m)`

- **It must:** SPEC 5 WO-02: for each vertex, the sum of n * area of the faces using it, normalised (left as is when under 1e-15).
- **May use:** bimAnFaceNormal (WO-01).
- **Files:** `src/js/engine/analysis/surface-analysis.js`, `docs/work-orders/v186/v186.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v186/v186.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimAnDraft(n, pull)`

- **It must:** SPEC 5 WO-03: 90 - the angle in degrees between the unit normal and the pull direction (normalised; the cosine clamped to -1..1).
- **May use:** nothing.
- **Files:** `src/js/engine/analysis/surface-analysis.js`, `docs/work-orders/v186/v186.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v186/v186.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimAnZebra(n, view, stripes)`

- **It must:** SPEC 5 WO-04: the reflected view r = 2 (n . view) n - view; k = floor((r[1] + 1) / 2 * stripes) clamped to 0 .. stripes - 1; k % 2. stripes 10 when under 1 (floored).
- **May use:** nothing.
- **Files:** `src/js/engine/analysis/surface-analysis.js`, `docs/work-orders/v186/v186.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v186/v186.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimAnGauss(m)`

- **It must:** SPEC 5 WO-05: {deficit, area} per vertex: 2 pi minus the sum of the corner angles at it over every face (the angle between the edges to the previous and next vertex of the face), and the sum of each face's area / its vertex count.
- **May use:** bimAnFaceNormal (WO-01).
- **Files:** `src/js/engine/analysis/surface-analysis.js`, `docs/work-orders/v186/v186.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v186/v186.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-06 [Claude] The analyses in Analyze

Claude's: the three analyses as result layers on surfaces, their legends and settings; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 186, Notion.
