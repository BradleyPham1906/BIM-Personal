# V226 work orders: Track C, the PennDOT LRFD input writer

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/structure/penndot-input.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v226/v226.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v226/v226.test.mjs
    node --check src/js/engine/structure/penndot-input.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimPdName(program, code)`

- **It must:** SPEC 5 WO-01: with BIM_PD_PS (the 44 PSLRFD codes and names of the spec's inventory) and BIM_PD_ST (the 57 STLRFD codes in section order, 5.3 CFG to 5.59 ORF) just above it: for 'PS' the name or null; for 'ST' 'Design Plate Location' for DPL, else the code when it is an STLRFD command, else null; any other program null.
- **May use:** BIM_PD_PS, BIM_PD_ST (this task).
- **Files:** `src/js/engine/structure/penndot-input.js`, `docs/work-orders/v226/v226.test.mjs`
- **Budget:** 130
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v226/v226.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimPdShared()`

- **It must:** SPEC 5 WO-02: the STLRFD codes that PSLRFD also has, sorted (23).
- **May use:** BIM_PD_PS, BIM_PD_ST (WO-01).
- **Files:** `src/js/engine/structure/penndot-input.js`, `docs/work-orders/v226/v226.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v226/v226.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimPdStOrder(codes)`

- **It must:** SPEC 5 WO-03: {ok: false, why: 'not an STLRFD command: C'} for the first unknown code; else the codes that come before an earlier one's section, as {ok: false, why: "out of the manual's order: A, B"}; else {ok: true}.
- **May use:** BIM_PD_ST (WO-01).
- **Files:** `src/js/engine/structure/penndot-input.js`, `docs/work-orders/v226/v226.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v226/v226.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Claude] Field definitions and the writer

Claude's: extract PSLRFD 5.2's order and each command's fields from the manuals, then the record writer's orders, the girder model's mapping, an export compared with a manual example. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-05 [Claude] The records

PIPELINE row 226, Notion.
