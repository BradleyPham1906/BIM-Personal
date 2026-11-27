# V229 work orders: A split grammar for facades

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/split-grammar.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v229/v229.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v229/v229.test.mjs
    node --check src/js/engine/bim/split-grammar.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [x] WO-01 [Cline] `bimSgSizes(len, sizes)`

- **It must:** SPEC 5 WO-01: sizes: a number is absolute; {rel: r} is r times len; {fl: f} is floating. Negative numbers, rel and fl count as 0; anything else is 0. The floating parts share max(0, len - the absolute and relative sizes) in proportion to their f (0 each when the f sum to 0). The resolved sizes, in order; nothing is cut here.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/split-grammar.js`, `docs/work-orders/v229/v229.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v229/v229.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-02 [Cline] `bimSgSplit(len, sizes)`

- **It must:** SPEC 5 WO-02: the sizes from bimSgSizes placed end to end from 0: [{i (the part's position in sizes), at, size}], each size cut to what is left of len; a part of 1e-9 or less (after cutting) is left out and does not advance; parts after the scope is full are therefore left out.
- **May use:** bimSgSizes (WO-01).
- **Files:** `src/js/engine/bim/split-grammar.js`, `docs/work-orders/v229/v229.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v229/v229.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimSgRepeat(len, size)`

- **It must:** SPEC 5 WO-03: {n: 0, size: 0} unless len and size are both over 0; else n = max(1, floor(len / size + 0.5 + 1e-9)) (the nearest count, a half going up, at least one) and {n, size: len / n}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/split-grammar.js`, `docs/work-orders/v229/v229.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v229/v229.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimSgValidate(rules, start)`

- **It must:** SPEC 5 WO-04: rules {name: rule}; a rule is {op: 'split', axis: 'x'|'y', parts: [[size, ruleName], ...]}, {op: 'repeat', axis, size, rule: ruleName} or {op: 'element', kind}. In this order: start not an own key of rules {error: 'no start rule S'}; then for names in sorted order, the first of: op not one of the three 'unknown op in N'; a split or repeat whose axis is not 'x' or 'y' 'bad axis in N'; a split with no parts 'no parts in N'; an element whose kind is not a non-empty string 'no kind in N'; a split's part or a repeat's rule naming no rule 'missing rule R in N' (a split's parts in order); then a depth-first walk from each name in sorted order following a split's parts in order and a repeat's rule: a rule met again while still being walked gives {error: 'cycle at R'}, R that rule. Else {ok: true}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/split-grammar.js`, `docs/work-orders/v229/v229.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v229/v229.test.mjs`. **Score:** 0+1+0+0+1+0 = 2.

---

## [ ] WO-05 [Cline] `bimSgDerive(rules, start, scope, params, limit)`

- **It must:** SPEC 5 WO-05: bimSgValidate's error as it is. scope {x, y, w, h} (x and y 0 when absent); a shape is {rule, path, x, y, w, h}, the first {rule: start, path: [[start, 0]]} over the scope. Shapes are taken depth first, a shape's children in order; each shape taken counts one step, and more than limit (100000 unless limit is over 0) gives {error: 'more than L shapes'}. A size is a number, or a string naming a number in params, or {rel: ...} or {fl: ...} whose value is one of those. An element rule gives a leaf {rule, kind, path, x, y, w, h}. A split resolves its sizes (any size not a number of 0 or more: {error: 'bad size in N'}, N the shape's rule) and uses bimSgSplit along its axis (x: along w from x; y: along h from y); each cut gives a child of the part's rule whose path adds [ruleName, k], k the count of earlier parts of the same split with that rule name (so the second 'Pier' of a split is index 1 whether or not anything before it was cut). A repeat (size not over 0: 'bad size in N') uses bimSgRepeat and gives n children of its rule with path [ruleName, i]. {leaves (in the order met), steps}.
- **May use:** bimSgValidate (WO-04), bimSgSplit (WO-02), bimSgRepeat (WO-03).
- **Files:** `src/js/engine/bim/split-grammar.js`, `docs/work-orders/v229/v229.test.mjs`
- **Budget:** 90
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v229/v229.test.mjs`. **Score:** 0+1+0+0+2+0 = 3.

---

## [ ] WO-06 [Claude] Wiring into the app

Claude's: the facade generator on V228's records (a wall face as the scope, leaves made into walls and openings), its form and its rules as text; saving with the project and undo; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 229, Notion.
