# V215 work orders: Flows and an app SDK

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/commands/flows.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v215/v215.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v215/v215.test.mjs
    node --check src/js/engine/commands/flows.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimFlowOrder(nodes)`

- **It must:** SPEC 5 WO-01: nodes {name: {op, in: [names]}}; for names in sorted order: a repeated input 'duplicate input edge: N', an input not a node 'missing node: N' (as {error}); then Kahn's algorithm from the sorted nodes with no inputs, releasing dependants in sorted order: {order}, or {error: 'cycle'} when not all are ordered.
- **May use:** nothing.
- **Files:** `src/js/engine/commands/flows.js`, `docs/work-orders/v215/v215.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v215/v215.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-02 [Cline] `bimFlowEval(nodes)`

- **It must:** SPEC 5 WO-02: the error from WO-01, else in order: any input null or undefined makes the node null; 'value' its numeric value (else null); 'sum' the inputs' sum; 'double' twice its one input; 'mul' their product; any other {error: 'unsupported op: N'}. {values}.
- **May use:** bimFlowOrder (WO-01).
- **Files:** `src/js/engine/commands/flows.js`, `docs/work-orders/v215/v215.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v215/v215.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimSdkCheck(msg, allowed, origin, origins)`

- **It must:** SPEC 5 WO-03: in order: origin not in origins 'origin not allowed'; msg not an object with a string cmd 'not a command message'; cmd not an own key of allowed 'unknown command C'; args present but not a non-null, non-array object 'args must be an object'; else {ok: true}. Failures {ok: false, why}.
- **May use:** nothing.
- **Files:** `src/js/engine/commands/flows.js`, `docs/work-orders/v215/v215.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v215/v215.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimSdkSnapshot(state, fields)`

- **It must:** SPEC 5 WO-04: the listed fields that are state's own, each a deep copy (JSON).
- **May use:** nothing.
- **Files:** `src/js/engine/commands/flows.js`, `docs/work-orders/v215/v215.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v215/v215.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] Wiring into the app

Claude's: the interface on phone, tablet and desktop, saving with the project and undo; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 215, Notion.
