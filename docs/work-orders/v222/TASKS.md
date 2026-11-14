# V222 work orders: 4D/5D construction planning, CP0 to CP3: quantities, cost lines, allocation

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/cost-plan.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v222/v222.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v222/v222.test.mjs
    node --check src/js/engine/bim/cost-plan.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimCpSlabNet(w, l, t, holes)`

- **It must:** SPEC 5 WO-01: w l t less each hole's w l times its depth (its t when positive, capped at t; else t); never under 0.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/cost-plan.js`, `docs/work-orders/v222/v222.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v222/v222.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimCpLine(q, P)`

- **It must:** SPEC 5 WO-02: order = q (1 + waste) (waste 0 unless 0 or more), material = order matRate, hours = q hoursPer, labour = hours labRate (missing rates 0); {order, material, hours, labour, total: material + labour}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/cost-plan.js`, `docs/work-orders/v222/v222.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v222/v222.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimCpAllocate(amount, splits)`

- **It must:** SPEC 5 WO-03: any share not 0 or more, or a total over 1 (by 1e-12): {error: 'invalid allocation'}; else {assigned: amount times each share, unallocated: amount - amount times the total}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/cost-plan.js`, `docs/work-orders/v222/v222.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v222/v222.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimCpBuckets(items)`

- **It must:** SPEC 5 WO-04: items [{amount, split: {bucket: share}}]: each bucket's sum of amount times share.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/cost-plan.js`, `docs/work-orders/v222/v222.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v222/v222.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] Quantities and the plan

Claude's: quantities from the model's slabs and footings with provenance, the cost-line table, allocations to days, the 4D colour by planned day. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 222, Notion.
