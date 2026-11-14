# V204 work orders: The Parametric Design Foundation, sketch to Pad to Pocket

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/parametric.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v204/v204.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v204/v204.test.mjs
    node --check src/js/engine/bim/parametric.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimPfOrder(fs)`

- **It must:** SPEC 5 WO-01: a depth-first post-order over the features in their given order, following refs (refs to absent ids are ignored): {order: [ids]}; a cycle met gives {error: 'cycle', ids: the path from the repeated id back to it, e.g. ['a', 'b', 'a']}.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/parametric.js`, `docs/work-orders/v204/v204.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v204/v204.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-02 [Cline] `bimPfDownstream(fs, id)`

- **It must:** SPEC 5 WO-02: the ids that depend on id directly or through others, in bimPfOrder's order; the cycle error object when there is one.
- **May use:** bimPfOrder (WO-01).
- **Files:** `src/js/engine/bim/parametric.js`, `docs/work-orders/v204/v204.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v204/v204.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimPfExpr(s, params)`

- **It must:** SPEC 5 WO-03: a recursive-descent reader over sum := prod (('+'|'-') prod)*, prod := atom (('*'|'/') atom)*, atom := number | name | '(' sum ')' | '-' atom, spaces skipped: {value} or {error} with the first of 'unknown name N', 'division by zero', 'expected )', 'unexpected C' (C the character, or 'end'). A name must be a number in params. No eval, no Function.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/parametric.js`, `docs/work-orders/v204/v204.test.mjs`
- **Budget:** 90
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v204/v204.test.mjs`. **Score:** 0+1+0+0+2+0 = 3, tier B.

---

## [ ] WO-04 [Cline] `bimPfRebuild(fs, params, last)`

- **It must:** SPEC 5 WO-04: the cycle error as {error: 'cycle', ids}; else in order: sketch {status 'ok', w, l, area} when both expressions are positive, else failed 'the sketch needs a positive width and length'; pad on its first ref: ok {depth, area, w, l, volume: area depth} when its sketch is ok and depth > 0, else failed 'its sketch or depth is not valid'; pocket on its pad: failed 'its pad is not valid', or failed 'the pocket does not fit in its pad' (any size not positive, w or l over the pad's, depth over its depth), else ok {volume: pad volume - w l depth}; any other kind failed 'unknown kind'. A failed feature whose entry in last was ok carries it as kept. {order, results}.
- **May use:** bimPfOrder (WO-01), bimPfExpr (WO-03).
- **Files:** `src/js/engine/bim/parametric.js`, `docs/work-orders/v204/v204.test.mjs`
- **Budget:** 90
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v204/v204.test.mjs`. **Score:** 0+1+0+0+2+0 = 3, tier B.

---

## [ ] WO-05 [Claude] Sketch, Pad and Pocket in the app

Claude's: the feature records saved with the project, the solids built from the results (the app's pad mesh and CSG), parameters in Properties, the failure marks, undo as one step; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 204, Notion.
