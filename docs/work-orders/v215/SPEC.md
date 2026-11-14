# V215 spec: Flows and an app SDK

Notion: Later: Flows and an app SDK. Research: `docs/research/research-notion-flows-sdk.md`, `docs/research/research-giraffe.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Per-object node graphs evaluated as a DAG: duplicate inputs, missing nodes and cycles refused before anything runs; unknown values propagate as unknown, never as 0.
- The plugin API: an app in a sandboxed iframe talks only by postMessage; its origin must be on the owner's list, its command on the allowed list, its arguments a plain object; it reads only whitelisted read-only snapshots.
- No third-party code runs in the engine; ops are a fixed list (value, sum, double, mul to start).

## 2. What it does for the user

Attach a small node graph to an object (inputs, sums, products) whose result drives a property; install an app in the right panel that can read the model's snapshot and call the allowed commands.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/commands/flows.js` | new, after `js/engine/commands/command-map.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v215/v215.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/commands/flows.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimFlowOrder(nodes)`**: nodes {name: {op, in: [names]}}; for names in sorted order: a repeated input 'duplicate input edge: N', an input not a node 'missing node: N' (as {error}); then Kahn's algorithm from the sorted nodes with no inputs, releasing dependants in sorted order: {order}, or {error: 'cycle'} when not all are ordered.
- **WO-02 `bimFlowEval(nodes)`**: the error from WO-01, else in order: any input null or undefined makes the node null; 'value' its numeric value (else null); 'sum' the inputs' sum; 'double' twice its one input; 'mul' their product; any other {error: 'unsupported op: N'}. {values}.
- **WO-03 `bimSdkCheck(msg, allowed, origin, origins)`**: in order: origin not in origins 'origin not allowed'; msg not an object with a string cmd 'not a command message'; cmd not an own key of allowed 'unknown command C'; args present but not a non-null, non-array object 'args must be an object'; else {ok: true}. Failures {ok: false, why}.
- **WO-04 `bimSdkSnapshot(state, fields)`**: the listed fields that are state's own, each a deep copy (JSON).

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** wiring into the app; **WO-06** the records.

## 7. Not in this phase

Code from apps running in the engine; a visual node editor's look (claude's task); a marketplace.
