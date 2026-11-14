# V201 work orders: MEP runs, a checked tree and straight friction

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function to `src/js/engine/bim/mep-flow.js`, below the file's header comment, and change nothing else: not
another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`, `function`; no `let`,
`const`, arrow functions, classes or template strings. Use only the names listed; never a name from another file.
Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v201/v201.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task run its
own cases, then the file's syntax check and the unit tests (Rule #1, one file of logic):

    node --test --test-name-pattern="WO-01" docs/work-orders/v201/v201.test.mjs
    node --check src/js/engine/bim/mep-flow.js
    npm test

Nothing calls these functions until Claude's first task after them, so rebuilding `canvas_v10.html` is not needed
after each one. Scores are from `../ROUTING.md` (files, logic, understanding, judgment, trickiness, check).

---

## [ ] WO-01 [Cline] `bimMepSection(p)`

- **It must:** SPEC 4 WO-01 and part 3's formulas.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/mep-flow.js`, `docs/work-orders/v201/v201.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v201/v201.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimMepColebrook(re, rr)`

- **It must:** SPEC 4 WO-02: exactly 100 bisection steps on [1, 100]; `Math.log(x) / Math.LN10` for log10 (ES5).
- **May use:** nothing.
- **Files:** `src/js/engine/bim/mep-flow.js`, `docs/work-orders/v201/v201.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v201/v201.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-03 [Cline] `bimMepFriction(q, sec, len, fluid)`

- **It must:** SPEC 4 WO-03: each state and reason word for word; Darcy's factor, never Fanning.
- **May use:** `bimMepColebrook` (WO-02).
- **Files:** `src/js/engine/bim/mep-flow.js`, `docs/work-orders/v201/v201.test.mjs`
- **Budget:** 35
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v201/v201.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-04 [Cline] `bimMepJoin(runs, tol)`

- **It must:** SPEC 4 WO-04: nodes by 3D distance and system; the warnings word for word, in the order met.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/mep-flow.js`, `docs/work-orders/v201/v201.test.mjs`
- **Budget:** 45
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v201/v201.test.mjs`. **Score:** 0+1+0+0+2+0 = 3, tier B.

---

## [ ] WO-05 [Cline] `bimMepTree(nodeCount, edges, source)`

- **It must:** SPEC 4 WO-05: breadth first, each edge used once; loop, not connected, no source.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/mep-flow.js`, `docs/work-orders/v201/v201.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v201/v201.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-06 [Cline] `bimMepFlows(tree, edges, demand)`

- **It must:** SPEC 4 WO-06: from the terminals toward the source; a terminal without a demand refuses.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/mep-flow.js`, `docs/work-orders/v201/v201.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v201/v201.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-07 [Cline] `bimMepPaths(tree, edges, loss)`

- **It must:** SPEC 4 WO-07: the trunk counted once per path, never the branches added together.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/mep-flow.js`, `docs/work-orders/v201/v201.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v201/v201.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-08 [Claude] The run tool

Claude's (score 2+2+2+1+2+1 = 10): SPEC part 5 WO-08. Moves `v201.test.mjs` into `tests/unit/mep-flow.test.mjs`; `npm run modules`.

---

## [ ] WO-09 [Claude] Joins, flows, the Flow table, the browser check

Claude's: SPEC part 5 WO-09, the check's script in `tests/e2e/`.

---

## [ ] WO-10 [Claude] Fittings, tees, elevation, IFC: the next slice's research

Claude's: SPEC part 5 WO-10.
