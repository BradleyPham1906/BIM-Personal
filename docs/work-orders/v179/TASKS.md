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

## [x] WO-01 [Cline] `bimIntProgramItem(raw)`

- **It must:** SPEC 4 WO-01 (amended 2026-11-16: the brief fields). Example: `{use: ' Bedroom ', count: 2.7, areaMin: 14, areaMax: 10}` gives `use: 'Bedroom'`, `count: 2`, `areaMin: 10`, `areaMax: 14`, and the new fields at their defaults.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 70
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-02 [Cline] `bimIntRelation(raw)`

- **It must:** SPEC 4 WO-02 (amended 2026-11-16: eight relation kinds, strength, reason, status).
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-03 [Cline] `bimIntInside(p, poly)`

- **It must:** SPEC 4 WO-03: the even-odd crossing test, true in the room, false in a concave notch.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-04 [Cline] `bimIntSharedLength(pa, pb, tol)`

- **It must:** SPEC 4 WO-04. Example: two 4 m deep rooms either side of a 0.2 m wall share 4 with `tol` 0.3, 0 with `tol` 0.1.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [x] WO-05 [Cline] `bimIntDoorLinks(rooms, doors, reach)`

- **It must:** SPEC 4 WO-05: the left side is `center + (-dir[1], dir[0]) / length * reach`.
- **May use:** `bimIntInside` (WO-03).
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-06 [Cline] `bimIntDistances(links, from, cost)`

- **It must:** SPEC 4 WO-06: Dijkstra; a room not reached is absent from the answer, never 0.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [x] WO-07 [Cline] `bimIntCheck(rel, facts)`

- **It must:** SPEC 4 WO-07, every status and reason word for word (amended 2026-11-16: rejected relations, access, four kinds not measured).
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 70
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-08 [Cline] `bimIntMatch(items, rooms)`

- **It must:** SPEC 4 WO-08: `{id, use, need, have, rooms, offArea, status}` per item.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-08 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-09 [Cline] `bimIntMinWidth(widthM, minIn)`

- **It must:** SPEC 4 WO-09.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors.js`, `docs/work-orders/v179/v179.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-09 ...` in `docs/work-orders/v179/v179.test.mjs`. **Score:** 0.

---

## [x] WO-10 [Claude] The facts from the live model; the Programme table

Claude's (score 2+2+2+1+2+1 = 10): SPEC part 5 WO-10. Moves `v179.test.mjs` into `tests/unit/interiors.test.mjs` and runs `npm run modules`.

Done 2026-11-16. Audit first: WO-01, WO-02 and WO-07 had been built before the 2026-11-16 amendment (3 of 9 tests
failed) and are brought to it; WO-07 also said "over 5 m" whatever `nearM` was, and WO-08 did not count a room with no
area as off its range. `bim/interiors-model.js` (new): the building's programme (`b.programme`, saved and undone with
the buildings), the rooms and doors read per level (an open region left out as missing; a door no longer cut into its
wall left out with a warning), the facts by use (`bimIntFactsFrom`), the report. Relations name uses, not room ids
(the choice this order left open): a programme is written before its rooms. A room's use is its usage's name, else
its own. A route costs, per door, room centre to door to room centre (an estimate; I3 measures walking). The
Programme group in Properties, Project tab (`properties/programme.js`): uses and relations, each with what the model
says, one undo step an edit. Tests: `tests/unit/interiors.test.mjs`, the nine orders' and three new.

---

## [x] WO-11 [Claude] The bubble diagram; the browser check

Claude's: SPEC part 5 WO-11, the check's script in `tests/e2e/`.

Done 2026-11-16. The board figure `int.bubble` (group Interiors in Add a figure): circles by area (dashed with none
set, amber when count or area is not as programmed), lines coloured met, not met, not evaluated, dashed when not
evaluated or only suggested, rejected relations left out; a fixed layout, so the same programme draws the same
(`bimIntBubbleLayout`). Browser check `tests/e2e/bim_phase179_programme_browser_tests.py`: 19 of 19.

---

## [x] WO-12 [Claude] I2 to I4's next orders; the records

Claude's: SPEC part 5 WO-12.

Done 2026-11-16. I2 to I4's orders were already written (`v180/`, `v181/`, `v182/`, 2026-11-14), each `[Cline]` task
naming its file and test. The records: PIPELINE row 179, the engineering log, QUEUE. Notion: the tasks already carry
the new names (V179 to V182); V179's and V180's tasks are In Progress with PR #113 under Pull requests.
