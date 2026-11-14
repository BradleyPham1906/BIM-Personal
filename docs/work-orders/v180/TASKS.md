# V180 work orders: Interiors I2, clearance and ergonomics

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/interiors-clearance.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v180/v180.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v180/v180.test.mjs
    node --check src/js/engine/bim/interiors-clearance.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimClrRect(c, w, d, rot)`

- **It must:** SPEC 5 WO-01: the corners of a w by d rectangle centred on c=[x,z], turned by rot radians, in the order (-w/2,-d/2), (w/2,-d/2), (w/2,d/2), (-w/2,d/2) of its own axes, each turned by (x cos - z sin, x sin + z cos).
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors-clearance.js`, `docs/work-orders/v180/v180.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v180/v180.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimClrZone(it, front, side)`

- **It must:** SPEC 5 WO-02: the zone in front of an item {center, w, d, rot}: a rectangle 'front' deep along the item's local +z, starting at its front face, as wide as the item plus 'side' each side, turned with it: centre = center + (-sin rot, cos rot) * (d/2 + front/2). null when front is not above 0.
- **May use:** bimClrRect (WO-01).
- **Files:** `src/js/engine/bim/interiors-clearance.js`, `docs/work-orders/v180/v180.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v180/v180.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimClrOverlap(a, b)`

- **It must:** SPEC 5 WO-03: true when two convex polygons overlap, by the separating axis test on every edge normal of both; projections that only touch (within 1e-9) do not overlap. false when either has fewer than 3 points.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors-clearance.js`, `docs/work-orders/v180/v180.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v180/v180.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-04 [Cline] `bimClrConflicts(items, obstacles)`

- **It must:** SPEC 5 WO-04: for each item {id, body, zone} with a zone, in order: each other item whose body overlaps the zone, then each obstacle {id, poly} that does, as {item, with}. Zones are never tested against zones.
- **May use:** bimClrOverlap (WO-03).
- **Files:** `src/js/engine/bim/interiors-clearance.js`, `docs/work-orders/v180/v180.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v180/v180.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-05 [Cline] `bimClrCircleFits(poly, c, r)`

- **It must:** SPEC 5 WO-05: true when the centre is inside the polygon (even-odd) and its distance to every edge segment is at least r - 1e-9; false for r not above 0 or fewer than 3 points.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors-clearance.js`, `docs/work-orders/v180/v180.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v180/v180.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-06 [Cline] `bimClrRule(rule, m)`

- **It must:** SPEC 5 WO-06: {clause, edition} (strings, else '') plus status: 'not evaluated' unless rule.minIn and m are numbers; else 'meets' when m / 0.0254 >= minIn - 1e-9, else 'below', and measuredIn rounded to 2 places.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors-clearance.js`, `docs/work-orders/v180/v180.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v180/v180.test.mjs`. **Score:** 0.

---

## [ ] WO-07 [Claude] Registry rules, item kinds and the check on the model

Claude's: the ADA rules and clearance kinds in standards/registry.js, item bodies and zones from Assets models, the check in Properties and drawn on the plan; moves the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-08 [Claude] The records

PIPELINE row 180, Notion, the research note's page.
