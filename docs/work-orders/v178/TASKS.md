# V178 work orders: the report, the pure part

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function to `src/js/engine/sheets/report-model.js`, below the file's header comment, and change nothing else: not
another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`, `function`; no `let`,
`const`, arrow functions, classes or template strings. Use only the names listed; never a name from another file.
Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v178/v178.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task run its
own cases, then the file's syntax check and the unit tests (Rule #1, one file of logic):

    node --test --test-name-pattern="WO-01" docs/work-orders/v178/v178.test.mjs
    node --check src/js/engine/sheets/report-model.js
    npm test

Nothing calls these functions until Claude's first task after them, so rebuilding `canvas_v10.html` is not needed
after each one. Scores are from `../ROUTING.md` (files, logic, understanding, judgment, trickiness, check).

---

## [ ] WO-01 [Cline] `bimRptFromLive(st)`

- **It must:** SPEC 4 WO-01: `'ok'` to `'available'`, `'stale'` to `'stale'`, `'gone'` to `'failed'`, anything else `'unavailable'`.
- **May use:** nothing.
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 28
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimRptDatum(raw)`

- **It must:** SPEC 4 WO-02, with `var BIM_RPT_STATES=['available','partial','stale','unavailable','failed'];` just above the function. Example: `bimRptDatum({value: NaN, state: 'available'})` is the blank datum (`value: null`, `state: 'unavailable'`, every text field `''`).
- **May use:** `BIM_RPT_STATES` (this task).
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 70
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimRptText(d, digits)`

- **It must:** SPEC 4 WO-03. Example: `bimRptText({value: 0, unit: 'm', state: 'available'})` is `'0 m'`.
- **May use:** nothing.
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimRptRings(radiiKm)`

- **It must:** SPEC 4 WO-04. Example: `bimRptRings([3, 1, 2, 2, -1])` gives the rings 1, 2 and 3 km, each `cumulative: true`.
- **May use:** nothing.
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-05 [Cline] `bimRptPlan(families)`

- **It must:** SPEC 4 WO-05 and the titles of SPEC part 3, with `BIM_RPT_SA` and `BIM_RPT_DA` (lists of `[id, title]`) just above the function.
- **May use:** `BIM_RPT_SA`, `BIM_RPT_DA` (this task).
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0+0+0+0+0+0 = 0.

---

## [ ] WO-06 [Cline] `bimRptIssue(data)`

- **It must:** SPEC 4 WO-06: never blocks, only marks.
- **May use:** `bimRptDatum` (WO-02).
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-07 [Cline] `bimRptManifest(report, revision, when)`

- **It must:** SPEC 4 WO-07: keys of the result in the order `id, revision, generated, boards, data`; every datum a copy.
- **May use:** `bimRptDatum` (WO-02).
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-08 [Cline] `bimRptStale(manifest, revision)`

- **It must:** SPEC 4 WO-08.
- **May use:** nothing.
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-08 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0.

---

## [ ] WO-09 [Cline] `bimRptLegend(rows, max)`

- **It must:** SPEC 4 WO-09.
- **May use:** nothing.
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 28
- **Test:** the cases named `WO-09 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0.

---

## [ ] WO-10 [Cline] `bimCompResolve(def, inst)`

- **It must:** SPEC 4 WO-10: a new object; an override for a key the definition lacks is ignored.
- **May use:** nothing.
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 32
- **Test:** the cases named `WO-10 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-11 [Cline] `bimCompSync(inst, def)`

- **It must:** SPEC 4 WO-11.
- **May use:** nothing.
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 32
- **Test:** the cases named `WO-11 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-12 [Cline] `bimCompDetach(def, inst)`

- **It must:** SPEC 4 WO-12.
- **May use:** `bimCompResolve` (WO-10).
- **Files:** `src/js/engine/sheets/report-model.js`, `docs/work-orders/v178/v178.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-12 ...` in `docs/work-orders/v178/v178.test.mjs`. **Score:** 0.

---

## [ ] WO-13 [Claude] The report on the boards

Claude's (score 2+2+2+2+2+1 = 11): SPEC part 5 WO-13. Moves `v178.test.mjs` into `tests/unit/report-model.test.mjs`; runs `npm run modules`; one browser check of New report, its states and Sync, on phone, tablet and desktop, its script in `tests/e2e/`.

---

## [ ] WO-14 [Claude] Export: PDF and PNG with their manifest

Claude's: SPEC part 5 WO-14, and the measurements for decision 6 written into the research note.

---

## [ ] WO-15 [Claude] The archiMap additions and PowerPoint: the next work orders

Claude's: SPEC part 5 WO-15, as a TASKS-2 file with its own Cline orders once each source is checked.
