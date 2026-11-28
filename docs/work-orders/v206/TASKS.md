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

## [x] WO-01 [Cline] `bimTorMesh(pos, idx, scale)`

- **It must:** SPEC 5 WO-01: null unless pos has a multiple of 3 values; vertices [x s, z s, (0 - y) s] (s = scale when positive, else 1; written 0 - y so 0 stays 0); faces of each 3 indices.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [x] WO-02 [Cline] `bimTorGuidValid(g)`

- **It must:** SPEC 5 WO-02: with BIM_TOR_B64 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$' just above it: a string of 22 characters, the first one of 0 to 3, the rest in the alphabet.
- **May use:** BIM_TOR_B64 (this task).
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [x] WO-03 [Cline] `bimTorGuidFromHex(hex)`

- **It must:** SPEC 5 WO-03: 32 hex digits (dashes removed, any case; else null) as 128 bits; the first character from the top 2 bits, then 21 characters of 6 bits each, by BIM_TOR_B64.
- **May use:** BIM_TOR_B64 (WO-02).
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-04 [Cline] `bimTorGuidToHex(g)`

- **It must:** SPEC 5 WO-04: the inverse of WO-03, lower-case hex; null for an invalid GUID.
- **May use:** bimTorGuidValid (WO-02).
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [x] WO-05 [Cline] `bimTorCompare(a, b)`

- **It must:** SPEC 5 WO-05: two {class: count} maps: every class in either, sorted; {same: [classes with equal counts], diff: [{cls, a, b}] with absent as 0}.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [x] WO-06 [Cline] `bimTorArea(pts)`

- **It must:** SPEC 5 WO-06: the area of a planar polygon in 3D: half the length of its Newell normal; 0 for none.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [x] WO-07 [Cline] `bimTorClip(p, plane)`

- **It must:** SPEC 5 WO-07: true when (p - plane.p) . plane.n > 1e-9 (the clipped-away side); a point on the plane is kept.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-review.js`, `docs/work-orders/v206/v206.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v206/v206.test.mjs`. **Score:** 0.

---

## [x] WO-08 [Claude] The Review view

Claude's: That Open pinned in runtime/ under the library rule, the Review view (look, clip with bimTorClip, measure with bimTorArea), loaded on demand; the test to tests/unit/; npm run modules; the browser check.

**Done 2026-11-28 (Claude).** That Open 3.6 and web-ifc 0.0.79 pinned in `runtime/thatopen/3.6.0/` by
`tools/thatopen/build_thatopen.mjs`; the loader `io/thatopen-runtime.js`; the view `io/thatopen-review.js` and
`css/workspace/review.css`, command REVIEW (several files, select for IFC data, section planes counted by bimTorClip,
length, area checked by bimTorArea, hide, isolate, show all, a storey and class tree, Import). Tests:
`tests/unit/thatopen.test.mjs`, `tests/unit/ifc-review.test.mjs` (this file's cases, moved); the browser check
`tests/e2e/bim_phase206_review_check.mjs`, 18 of 18 over http and from file://, desktop and phone.

---

## [x] WO-09 [Claude] IFC import through That Open

Claude's: fragments to meshes per element with GlobalIds, storeys and psets; compared with V196 on the 13 files by bimTorCompare; cc-ifc retired when they match; records, PIPELINE row 206, Notion.

**Done 2026-11-28 (Claude), but for cc-ifc's retirement, which is the owner's call** (`research-thatopen-gap.md`
part 11, decision 1). `bimToeRead` in `io/thatopen-runtime.js` gives the import's data; `io/ifc-full.js` reads through
That Open first, then cc-ifc, then the walls-and-slabs reader. e03 (`docs/research/experiments/thatopen/e03/`): 12 of
13 files agree with cc-ifc class by class (bimTorCompare), with every GlobalId; the 13th, FM_ARC_DigitalHub, reads
all 705 elements where cc-ifc stops at the triangle cap. That Open is 2.5 to 5 times slower on large files.
WO-01's bimTorMesh is not on this path: That Open's output is already +Y up (e02).
