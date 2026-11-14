# V214 work orders: Costs and pro forma

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/proforma.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v214/v214.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v214/v214.test.mjs
    node --check src/js/engine/bim/proforma.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimPfmLine(l)`

- **It must:** SPEC 5 WO-01: gross = qty rate periods (periods 1 unless positive; missing qty or rate 0); vacancy used when 0 <= v < 1, else 0; {name (or ''), gross, effective: gross (1 - v)}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/proforma.js`, `docs/work-orders/v214/v214.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v214/v214.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimPfmTotals(lines, opex)`

- **It must:** SPEC 5 WO-02: {gross, effective (sums of the lines), opex (0 unless positive), noi: effective - opex}.
- **May use:** bimPfmLine (WO-01).
- **Files:** `src/js/engine/bim/proforma.js`, `docs/work-orders/v214/v214.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v214/v214.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimPfmCost(items)`

- **It must:** SPEC 5 WO-03: the sum of the items' finite numeric amounts.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/proforma.js`, `docs/work-orders/v214/v214.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v214/v214.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimPfmMetrics(noi, cost, cap)`

- **It must:** SPEC 5 WO-04: {yieldOnCost: noi / cost (null unless cost > 0), value: noi / cap (null unless cap > 0), profit: value - cost, marginOnCost: profit / cost} with nulls carried.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/proforma.js`, `docs/work-orders/v214/v214.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v214/v214.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] Wiring into the app

Claude's: the interface on phone, tablet and desktop, saving with the project and undo; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 214, Notion.
