# V193 work orders: LOD-F, LOD3 openings on rectified facades

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/facade-openings.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v193/v193.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v193/v193.test.mjs
    node --check src/js/engine/bim/facade-openings.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimOpnCluster(values, tol)`

- **It must:** SPEC 5 WO-01: indices sorted by value (then index); a new cluster starts when a value is more than tol (0.05 when negative or absent) above the previous member; each {members (indices, ascending), mean}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/facade-openings.js`, `docs/work-orders/v193/v193.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v193/v193.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimOpnSnap(values, tol)`

- **It must:** SPEC 5 WO-02: a copy of the values with each replaced by its cluster's mean.
- **May use:** bimOpnCluster (WO-01).
- **Files:** `src/js/engine/bim/facade-openings.js`, `docs/work-orders/v193/v193.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v193/v193.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimOpnRegularise(rects, tol)`

- **It must:** SPEC 5 WO-03: sills (y), heads (y + h) and centres (x + w/2) each snapped (WO-02); each new rect {x: centre - w/2, y: sill, w, h: head - sill, moved: the largest of the changes of x, y and the head}.
- **May use:** bimOpnSnap (WO-02).
- **Files:** `src/js/engine/bim/facade-openings.js`, `docs/work-orders/v193/v193.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v193/v193.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimOpnOverlap(rects)`

- **It must:** SPEC 5 WO-04: pairs [i, j], i < j, whose interiors overlap (strictly, by 1e-9).
- **May use:** nothing.
- **Files:** `src/js/engine/bim/facade-openings.js`, `docs/work-orders/v193/v193.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v193/v193.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimOpnToWall(r, len, height)`

- **It must:** SPEC 5 WO-05: null unless w and h are positive and the rect lies within 0..len along and 0..height up (height checked when positive); else {along: x + w/2, sill: y, width: w, height: h, kind: 'door' when y <= 0.05, else 'window'}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/facade-openings.js`, `docs/work-orders/v193/v193.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v193/v193.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Claude] Drawing, Regularise and Apply on the facade

Claude's: the opening tool on V192's rectified facade, Regularise, Apply through the app's opening code (bim/columns-openings.js) with the source kept; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 193, Notion.
