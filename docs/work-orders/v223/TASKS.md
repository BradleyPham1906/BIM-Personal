# V223 work orders: 4D/5D construction planning, CP4 and CP5: procurement and drawing intake

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/procurement.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v223/v223.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v223/v223.test.mjs
    node --check src/js/engine/bim/procurement.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimCpDate(s)`

- **It must:** SPEC 5 WO-01: 'YYYY-MM-DD' as Date.UTC(year, month - 1, day); null for anything else. Write bimCpIso(t), the inverse ('YYYY-MM-DD' from UTC), with it.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/procurement.js`, `docs/work-orders/v223/v223.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v223/v223.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimCpWorkdayBefore(need, n, holidays)`

- **It must:** SPEC 5 WO-02: null for a bad date or n under 0; n times: one day back, then further back while the day is Saturday, Sunday or in holidays ('YYYY-MM-DD' strings); the result as 'YYYY-MM-DD'.
- **May use:** bimCpDate, bimCpIso (WO-01).
- **Files:** `src/js/engine/bim/procurement.js`, `docs/work-orders/v223/v223.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v223/v223.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimCpScores(tp, fp, fn)`

- **It must:** SPEC 5 WO-03: {precision: tp / (tp + fp), recall: tp / (tp + fn)}, each null when its denominator is 0.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/procurement.js`, `docs/work-orders/v223/v223.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v223/v223.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Claude] Procurement dates and intake review

Claude's: lead times per line, the order-by column, the intake sample and its review screen. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-05 [Claude] The records

PIPELINE row 223, Notion.
