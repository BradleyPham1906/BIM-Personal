# V175c work orders (step 1: one list)

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every task: add one function to `src/js/engine/sheets/layouts.js`, below the file's header comment, and change
nothing else: not another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed. Implement
the whole function; never a placeholder.

The tests are in `docs/work-orders/v175c/v175c.test.mjs`, outside `npm test` until the end, so main stays green.
After each task run its own cases, then the file's syntax check and the unit tests (Rule #1, one file of logic):

    node --test --test-name-pattern="WO-01" docs/work-orders/v175c/v175c.test.mjs
    node --check src/js/engine/sheets/layouts.js
    npm test

Nothing calls these functions until WO-06, so rebuilding `canvas_v10.html` is not needed after each task.
Scores are from `../ROUTING.md` (files, logic, understanding, judgment, trickiness, check).

---

## [ ] WO-01 [Cline] `bimLyNextNumber(numbers, prefix)`

- **It must:** return `prefix` plus one more than the highest number among the trimmed strings matching
  `new RegExp('^' + prefix + '(\\d+)$', 'i')`; `prefix + '101'` when there is none or the highest is below 101, or
  when `numbers` is not an array. Non-strings are left out.
- **Example:** `bimLyNextNumber(['A101', 'A103', 'A102'], 'A')` returns `'A104'`.
- **May use:** nothing.
- **Test:** the cases named `WO-01 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimLyNumberValid(s)`

- **It must:** collapse runs of spaces to one and trim; return `''` when empty or not matching
  `/^[A-Za-z0-9 ._-]+$/`, or when `s` is not a string; else its first 12 characters.
- **Example:** `bimLyNumberValid('S  2.1')` returns `'S 2.1'`.
- **May use:** nothing.
- **Test:** the cases named `WO-02 ...`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimLyLabel(number, name)`

- **It must:** trim both (`null`/`undefined` as `''`); `number + ' - ' + name` when both; else the one there; else `'Layout'`.
- **Example:** `bimLyLabel(null, '  Site plan ')` returns `'Site plan'`.
- **May use:** nothing.
- **Test:** the cases named `WO-03 ...`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimLyTabs(entries, activeId)`

- **It must:** return a new array `{id, t, label: bimLyLabel(num, name), on: id === activeId}` for each entry, in
  order; `[]` when `entries` is not an array; never change the entries.
- **May use:** `bimLyLabel` (this file).
- **Test:** the cases named `WO-04 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-05 [Cline] `bimLyDupNumbers(entries)`

- **It must:** return each number used by more than one entry (compared trimmed, without case) once, in the order
  in which each one's second use appears, written as first written (trimmed); empty numbers never count; `[]` for
  none or for a non-array.
- **Example:** numbers `'A102', 'A101', 'a102 ', 'A101', 'A103'` give `['A102', 'A101']`.
- **May use:** nothing.
- **Test:** the cases named `WO-05 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-06 [Claude] Build step 1 on them, and write step 2's spec

Claude's because it crosses files and touches what is saved (ROUTING: always D):
- review WO-01 to WO-05 against SPEC part 4; move `v175c.test.mjs` to `tests/unit/layouts.test.mjs`;
- a board's `num` kept (`bimBrdKeep`) and given at load when missing; one series (`bimNextSheetNumber`);
- the tabs from the whole set; + and + Layout's menu; renumbering a board; numbers and duplicates in the panel;
- `npm run modules`, the build, `npm test`, `npm run check`; the browser check, kept in `tests/e2e/`;
- the guide, the log, PIPELINE, Notion; step 2's spec and work orders; ask the owner before merging.
