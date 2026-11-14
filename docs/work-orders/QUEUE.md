# The work-order queue

Claude keeps this list full; Cline takes from the top. A phase is listed here only when its research
is done, the owner's decisions are made, and every `[Cline]` task has its test and names its file(s).
Claude's aim is to keep two or more phases ready ahead, so Cline never waits for a spec.

Cline: `/ship-task.md` with no arguments takes the first open `[Cline]` task below.

## Ready for Cline

| Phase | Tasks | Where |
|---|---|---|
| v194 | T-07 (`[Cline]`) | `v194/TASKS.md`, test in `tests/unit/rendered.test.mjs` |
| v176 | WO-01 to WO-04 (`[Cline]`), in order | `v176/TASKS.md`, tests in `v176/v176.test.mjs` (outside `npm test`; the first run fetches about 7 MB of pinned wheels) |

## Claude's next (research and specs, not blocked on Cline)

| Phase | Next step |
|---|---|
| v175c | Step 1 built (WO-01 to WO-05 by Cline, WO-06 by Claude). Next: step 2's spec and work orders (one editor, the viewport an object), in the next spec sprint |
| v194 | T-08 done as V198 (PR #99), T-09 done as V195 (PR #91); T-06 covered by V198's browser check of the rendered view. Left: Claude wires T-07's look into the materials after Cline ships it |
| v176-v177 | IfcOpenShell (the owner, 2026-11-13: V176 and V177; the DA report is now V178). V176's orders are ready; next Claude: review them (WO-05), then V177's research and spec |
| That Open | Research done (`docs/research/research-thatopen.md`); the owner's decisions 2026-11-13: a Review view, on the app's three.js without WebGPU paths, That Open also for IFC import (replacing cc-ifc), after V176-V177. Next Claude: e02 (draw, clip, measure in a canvas; import fragments into the editable model), then the spec; phase number with PIPELINE.md |
| v202 | Walkthrough W1 researched (`docs/research/research-walkthrough.md`, 2026-11-14). Waiting on the owner's D1 to D7; then the spec and work orders |
| next phases | Research and specs from `docs/research/plan-v167-v170.md` and `docs/dev/PIPELINE.md`, in a spec sprint |
