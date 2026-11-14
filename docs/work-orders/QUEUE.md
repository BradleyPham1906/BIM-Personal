# The work-order queue

Claude keeps this list full; Cline takes from the top. A phase is listed here only when its research
is done, the owner's decisions are made, and every `[Cline]` task has its test and names its file(s).
Claude's aim is to keep two or more phases ready ahead, so Cline never waits for a spec.

Cline: `/ship-task.md` with no arguments takes the first open `[Cline]` task below.

## Ready for Cline

| Phase | Tasks | Where |
|---|---|---|
| v194 | T-07 (`[Cline]`) | `v194/TASKS.md`, test in `tests/unit/rendered.test.mjs` |
| v177 | WO-01 to WO-07 (`[Cline]`), in order | `v177/TASKS.md`, tests in `v177/v177.test.mjs` (outside `npm test`; about 30 s a run; the first run fetches about 16 MB of pinned wheels) |
| v203 | WO-01 to WO-08 (`[Cline]`), any order | `v203/TASKS.md`, tests in `v203/v203.test.mjs` (outside `npm test`) |

## Claude's next (research and specs, not blocked on Cline)

| Phase | Next step |
|---|---|
| v175c | Step 1 built (WO-01 to WO-05 by Cline, WO-06 by Claude). Next: step 2's spec and work orders (one editor, the viewport an object), in the next spec sprint |
| v194 | T-08 done as V198 (PR #99), T-09 done as V195 (PR #91); T-06 covered by V198's browser check of the rendered view. Left: Claude wires T-07's look into the materials after Cline ships it |
| v177 | V176 built and audited. V177 researched (`docs/research/research-ifcopenshell-app.md`), the owner's D1 to D4 answered 2026-11-13. Step 1 (the adapter that writes a model as IFC) is ready for Cline. Next Claude: audit it, then step 2's spec (the wheels in `runtime/`, the worker, `io/ifc-save.js`, File > Export > IFC, Make editable) |
| That Open | Research done (`docs/research/research-thatopen.md`); the owner's decisions 2026-11-13: a Review view, on the app's three.js without WebGPU paths, That Open also for IFC import (replacing cc-ifc), after V176-V177. Next Claude: e02 (draw, clip, measure in a canvas; import fragments into the editable model), then the spec; phase number with PIPELINE.md |
| v203 | WO-01 to WO-08 are Cline's; C-02 done (Jolt pinned); then Claude's C-03 to C-08 (the registry's riser records, the adapter, `WALK`, the controls, the rendered view's moving mode, tests and the browser check) |
| next phases | Research and specs from `docs/research/plan-v167-v170.md` and `docs/dev/PIPELINE.md`, in a spec sprint |
