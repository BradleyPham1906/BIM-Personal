# The work-order queue

Claude keeps this list full; Cline takes from the top. A phase is listed here only when its research
is done, the owner's decisions are made, and every `[Cline]` task has its test and names its file(s).
Claude's aim is to keep two or more phases ready ahead, so Cline never waits for a spec.

Cline: `/ship-task.md` with no arguments takes the first open `[Cline]` task below.

The owner's decisions for every phase below and in the outlines (2026-11-14): all as each research note
recommends, except V177's D1, chosen directly: (a), GPL and AGPL libraries allowed as separate files run only in
the Python worker. Each SPEC's opening lists what that means for its phase; overrule any of them there.

## Ready for Cline (in this order)

| Phase | Tasks | Where | Tests |
|---|---|---|---|
| v177 Save as IFC | WO-01 to WO-17 (17) | `v177/TASKS.md` | `v177/v177.test.mjs` (Python, the app's Pyodide; the first run downloads the pinned wheels), `v177/v177-js.test.mjs` |
| v178 the report | WO-01 to WO-12 (12) | `v178/TASKS.md` | `v178/v178.test.mjs` |
| v179 Interiors I1 | WO-01 to WO-09 (9) | `v179/TASKS.md` | `v179/v179.test.mjs` |
| v190 point clouds | WO-01 to WO-11 (11) | `v190/TASKS.md` | `v190/v190.test.mjs` |
| v201 MEP runs | WO-01 to WO-07 (7) | `v201/TASKS.md` | `v201/v201.test.mjs` |

56 Cline tasks. Every test was run against a reference version that was not committed (all passing) and against
the empty files (every case failing), so a task is done exactly when its own cases pass. Each phase's new file is
already in the build order with its header only; `npm test` and `npm run check` are green.

## Claude's next (research and specs, not blocked on Cline)

| Phase | Next step |
|---|---|
| v175c | Step 1 built. Next: step 2's spec and work orders (one editor, the viewport an object) |
| v202 | Walkthrough W1 (PR #104) and Site context C3 (branch `worktree-site-context-accuracy`): their own work orders, on their branches |
| v194 | T-06, the app's own browser check, when the owner asks |
| v177 to v201 | After Cline's tasks: Claude's own tasks in each TASKS file (wiring, the browser check of the new interface, the next slice) |
| That Open | Research done; e02 then the spec, after V176-V177 |
| Outlines, next spec sprint | `v183` (Freeform F1 NURBS curves), `v192` (facade rectification), `v193` (facade openings), `survey-control` (traverses), `generators`, `costs-proforma`, `later-gltf-assets`, `hub-h4-sync`, `flows-sdk`, `walkthrough-w2-w5` (after V202), `water-presentation`, `lod-g`, `v191` (after V190), `streaming-3d-tiles` (after the LOD track), `hub-h3-ifc` (folded into V177 and That Open). Each SPEC names its first slice's functions and tests |

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
