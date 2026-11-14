# Flows and an app SDK (outline)

Notion: Later: Flows and an app SDK. PIPELINE: later. Research: `docs/research/research-notion-flows-sdk.md`, `docs/research/research-giraffe.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

Spec sprint after a security review of the postMessage boundary (the research's fixture).

## 1. The owner's decisions, 2026-11-14, as recommended

- per-object node graphs evaluated as a DAG with cycle refusal;
- the plugin API: read-only state snapshots and named commands over postMessage to a sandboxed iframe, origins checked, no direct access to the engine;
- the engine's `__a3dRegisterCommand`, `__a3dRegisterDiscipline` and `__a3dRegisterTab` are the start.

## 2. What it does for the user

Small node graphs on an object (a light Grasshopper); a documented API for apps in the right panel.

## 3. The first slice (pure functions in `src/js/engine/commands/flows.js`, ES5, no other file's names)

- `bimFlowTopo(nodes, links)`: the evaluation order, or the cycle.
- `bimFlowEval(graph, ops)`: values through the graph in order.
- `bimSdkCheck(msg, allowed)`: a message's shape and command checked against the allowed list.

Tests: The research's DAG fixture.

## 4. Not in this phase

Third-party code running in the engine.
