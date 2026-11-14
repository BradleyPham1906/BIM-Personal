# The work-order queue

Claude keeps this list full; Cline takes from the top. A phase is listed here only when its research
is done, the owner's decisions are made, and every `[Cline]` task has its test and names its file(s).
Claude's aim is to keep two or more phases ready ahead, so Cline never waits for a spec.

Cline: `/ship-task.md` with no arguments takes the first open `[Cline]` task below.

The owner's decisions for v178 to v201 and the outlines (2026-11-14): all as each research note recommends.
Each SPEC's opening lists what that means for its phase; overrule any of them there. (V177's D1 to D4 were
answered 2026-11-13, in its own SPEC.)

## Ready for Cline (in this order)

| Phase | Tasks | Where | Tests |
|---|---|---|---|
| v178 the report | WO-01 to WO-12 (12) | `v178/TASKS.md` | `v178/v178.test.mjs` |
| v179 Interiors I1 | WO-01 to WO-09 (9) | `v179/TASKS.md` | `v179/v179.test.mjs` |
| v190 point clouds | WO-01 to WO-11 (11) | `v190/TASKS.md` | `v190/v190.test.mjs` |
| v201 MEP runs | WO-01 to WO-07 (7) | `v201/TASKS.md` | `v201/v201.test.mjs` |

39 Cline tasks. Every test was run against a reference version that was not committed (all passing) and against
the empty files (every case failing), so a task is done exactly when its own cases pass. Each phase's new file is
already in the build order with its header only; `npm test` and `npm run check` are green. (V177's and V203's
first Cline orders are shipped; their next steps are Claude's, below.)

## Claude's next (research and specs, not blocked on Cline)

| Phase | Next step |
|---|---|
| v175c | Step 1 built (WO-01 to WO-05 by Cline, WO-06 by Claude). Next: step 2's spec and work orders (one editor, the viewport an object), in the next spec sprint |
| v194 | T-08 done as V198 (PR #99), T-09 done as V195 (PR #91); T-06 covered by V198's browser check of the rendered view. Left: Claude wires T-07's look (shipped) into the materials |
| v177 | V176 built and audited. V177 researched (`docs/research/research-ifcopenshell-app.md`), the owner's D1 to D4 answered 2026-11-13. Step 1 (the adapter that writes a model as IFC) shipped by Cline (WO-01 to WO-07). Next Claude: audit it, then step 2's spec (the wheels in `runtime/`, the worker, `io/ifc-save.js`, File > Export > IFC, Make editable) |
| That Open | Research done (`docs/research/research-thatopen.md`); the owner's decisions 2026-11-13: a Review view, on the app's three.js without WebGPU paths, That Open also for IFC import (replacing cc-ifc), after V176-V177. Next Claude: e02 (draw, clip, measure in a canvas; import fragments into the editable model), then the spec; phase number with PIPELINE.md |
| v203 | WO-01 to WO-08 shipped by Cline; C-02 done (Jolt pinned); then Claude's C-03 to C-08 (the registry's riser records, the adapter, `WALK`, the controls, the rendered view's moving mode, tests and the browser check) |
| v178 to v201 | After Cline's tasks: Claude's own tasks in each TASKS file (wiring, the browser check of the new interface, the next slice) |
| Outlines, next spec sprint | `v183` (Freeform F1 NURBS curves), `v192` (facade rectification), `v193` (facade openings), `survey-control` (traverses), `generators`, `costs-proforma`, `later-gltf-assets`, `hub-h4-sync`, `flows-sdk`, `walkthrough-w2-w5` (after V203 W1), `water-presentation`, `lod-g`, `v191` (after V190), `streaming-3d-tiles` (after the LOD track), `hub-h3-ifc` (folded into V177 and That Open). Each SPEC names its first slice's functions and tests |

## Blocked (no Cline work until the gate in each SPEC part 0 clears)

| Folder | The gate |
|---|---|
| `hub-h5-server` | A backend: the owner's choice of a host and a threat model |
| `webgpu-compute` | GPU hardware tests against a CPU reference; only when a simulation is too slow |
| `wind-lbm` | A published benchmark reproduced, physical validation, expert review |
| `track-e-field` | A field test plan, hardware and licensed data |
| `4d-5d` | Qualified reviewers nominated, jurisdiction and measurement edition chosen, a fixture approved |
| `openbridge` | Out of Pending in Notion |
| `tracks-c-d` | Parked by the owner |
