# The work-order queue

Claude keeps this list full; Cline takes from the top. A phase is listed here only when its research
is done, the owner's decisions are made, and every `[Cline]` task has its test and names its file(s).
Claude's aim is to keep two or more phases ready ahead, so Cline never waits for a spec.

Cline: `/ship-task.md` with no arguments takes the first open `[Cline]` task below.

## Ready for Cline

| Phase | Tasks | Where |
|---|---|---|
| v194 | T-07 (`[Cline]`) | `v194/TASKS.md`, test in `tests/unit/rendered.test.mjs` |

## Claude's next (research and specs, not blocked on Cline)

| Phase | Next step |
|---|---|
| v175c | Step 1 built (WO-01 to WO-05 by Cline, WO-06 by Claude). Next: step 2's spec and work orders (one editor, the viewport an object), in the next spec sprint |
| v194 | T-08 done as V198 (PR #99), T-09 done as V195 (PR #91); T-06 covered by V198's browser check of the rendered view. Left: Claude wires T-07's look into the materials after Cline ships it |
| IfcOpenShell | Research begun 2026-11-13: the LGPL wasm wheel `ifcopenshell-0.9.0.post1` (4.6 MB, cp313, pyodide_2025_0) matches our Pyodide 0.29.5. Phase numbers and order wait on the owner |
| next phases | Research and specs from `docs/research/plan-v167-v170.md` and `docs/dev/PIPELINE.md`, in a spec sprint |
