# V179 work orders: Interiors I1, programme and adjacency

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function to `src/js/engine/bim/interiors.js`, below the file's header comment, and change nothing else: not
another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`, `function`; no `let`,
`const`, arrow functions, classes or template strings. Use only the names listed; never a name from another file.
Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v179/v179.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task run its
own cases, then the file's syntax check and the unit tests (Rule #1, one file of logic):

    node --test --test-name-pattern="WO-01" docs/work-orders/v179/v179.test.mjs
    node --check src/js/engine/bim/interiors.js
    npm test

Nothing calls these functions until Claude's first task after them, so rebuilding `canvas_v10.html` is not needed
after each one. Scores are from `../ROUTING.md` (files, logic, understanding, judgment, trickiness, check).

---

## [ ] WO-01 [Cline] `bimIntProgramItem(raw)`

- **It must:** SPEC 4 WO-01. Example: `{use: ' Bedroom ', count: 2.7, areaMin: 14, areaMax: 10}` gives `use: 'Bedroom'`, `count: 2`, `areaMin: 10`, `areaMax: 14`.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimIntRelation(raw)`

- **It must:** SPEC 4 WO-02.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimIntInside(p, poly)`

- **It must:** SPEC 4 WO-03: the even-odd crossing test, true in the room, false in a concave notch.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimIntSharedLength(pa, pb, tol)`

- **It must:** SPEC 4 WO-04. Example: two 4 m deep rooms either side of a 0.2 m wall share 4 with `tol` 0.3, 0 with `tol` 0.1.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-05 [Cline] `bimIntDoorLinks(rooms, doors, reach)`

- **It must:** SPEC 4 WO-05: the left side is `center + (-dir[1], dir[0]) / length * reach`.
- **May use:** `bimIntInside` (WO-03).
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-06 [Cline] `bimIntDistances(links, from, cost)`

- **It must:** SPEC 4 WO-06: Dijkstra; a room not reached is absent from the answer, never 0.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-07 [Cline] `bimIntCheck(rel, facts)`

- **It must:** SPEC 4 WO-07, every status and reason word for word.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-08 [Cline] `bimIntMatch(items, rooms)`

- **It must:** SPEC 4 WO-08: `{id, use, need, have, rooms, offArea, status}` per item.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-08 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-09 [Cline] `bimIntMinWidth(widthM, minIn)`

- **It must:** SPEC 4 WO-09.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-09 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0.

---

## [ ] WO-10 [Claude] The facts from the live model; the Programme table

Claude's (score 2+2+2+1+2+1 = 10): SPEC part 5 WO-10. Moves `v179.test.mjs` into `tests/unit/interiors.test.mjs` and runs `npm run modules`.

---

## [ ] WO-11 [Claude] The bubble diagram; the browser check

Claude's: SPEC part 5 WO-11, the check's script in `tests/e2e/`.

---

## [ ] WO-12 [Claude] I2 to I4's next orders; the records

Claude's: SPEC part 5 WO-12.
