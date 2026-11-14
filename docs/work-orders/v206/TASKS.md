# V206 work orders: That Open: the Review view and IFC import (with Hub H3's identity)

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/io/ifc-review.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v206/v206.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v206/v206.test.mjs
    node --check src/js/engine/io/ifc-review.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimTorMesh(pos, idx, scale)`

- **It must:** SPEC 5 WO-01: null unless pos has a multiple of 3 values; vertices [x s, z s, (0 - y) s] (s = scale when positive, else 1; written 0 - y so 0 stays 0); faces of each 3 indices.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimTorGuidValid(g)`

- **It must:** SPEC 5 WO-02: with BIM_TOR_B64 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$' just above it: a string of 22 characters, the first one of 0 to 3, the rest in the alphabet.
- **May use:** BIM_TOR_B64 (this task).
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimTorGuidFromHex(hex)`

- **It must:** SPEC 5 WO-03: 32 hex digits (dashes removed, any case; else null) as 128 bits; the first character from the top 2 bits, then 21 characters of 6 bits each, by BIM_TOR_B64.
- **May use:** BIM_TOR_B64 (WO-02).
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimTorGuidToHex(g)`

- **It must:** SPEC 5 WO-04: the inverse of WO-03, lower-case hex; null for an invalid GUID.
- **May use:** bimTorGuidValid (WO-02).
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimTorCompare(a, b)`

- **It must:** SPEC 5 WO-05: two {class: count} maps: every class in either, sorted; {same: [classes with equal counts], diff: [{cls, a, b}] with absent as 0}.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Cline] `bimTorArea(pts)`

- **It must:** SPEC 5 WO-06: the area of a planar polygon in 3D: half the length of its Newell normal; 0 for none.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [ ] WO-07 [Cline] `bimTorClip(p, plane)`

- **It must:** SPEC 5 WO-07: true when (p - plane.p) . plane.n > 1e-9 (the clipped-away side); a point on the plane is kept.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [ ] WO-08 [Claude] The Review view

Claude's: That Open pinned in runtime/ under the library rule, the Review view (look, clip with bimTorClip, measure with bimTorArea), loaded on demand; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-09 [Claude] IFC import through That Open

Claude's: fragments to meshes per element with GlobalIds, storeys and psets; compared with V196 on the 13 files by bimTorCompare; cc-ifc retired when they match; records, PIPELINE row 206, Notion.
