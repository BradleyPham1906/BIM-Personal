# BimCraft: Revit-style design on its authoring core, copied unchanged

Research and integration, 2026-11-28 (V308). Levels as in `research-protocol.md`. The owner: "we need to update to
bridge the gap for BIM design features like revit. Check BIMCraft repo also" and, on how, "copy their code ... reuse the
codes, dont write new stuff". The evidence is in four parts and two experiments:

| Part | What it covers | File |
|---|---|---|
| Walls and openings | joins (L, T, X), layered types, location lines, doors and windows by type, curtain walls, against the app's walls | `research-bimcraft-gap/walls-openings.md` |
| Views and drawings | plan cut and view range, poche, door swings, elevations and sections from the model, sheets, against the app's plan (the 3D camera looking down) | `research-bimcraft-gap/views-drawings.md` |
| Families and data | families with parameters and formulas, schedules, phases, design options, against the app's types and schedules | `research-bimcraft-gap/families-data.md` |
| Architecture | how BimCraft stores its model (IFC itself, one writer with an undo journal), its module graph, self-containment, licence and trademarks, tests and churn; the integration plan | `research-bimcraft-gap/architecture.md` |
| e05 | BimCraft's own test house built through the copied core in this app's runtime: 11 of 11 of their hand-worked checks, http and file:// | `experiments/bimcraft/e05/` |
| Browser check | DESIGN driven by clicks on BimCraft's plan view: 17 of 17, http and file:// | `tests/e2e/bim_phase308_design_check.mjs` |

## 1. Findings

- The app's floor plan is the 3D renderer looking down: no cut plane, no view range, no door swing; its doors and windows
  are holes with a marker, without type or leaf; its walls have one thickness and do not join (views-drawings.md 1,
  families-data.md, walls-openings.md). That is the gap with Revit's design core.
- BimCraft (Apache-2.0, our IFC engine's source) is a BIM authoring app whose core does exactly that: compound walls by
  type that join at L, T and X; doors and windows by type with plan symbols; floors, ceilings and roofs by room; rooms with
  numbers and areas; curtain walls; levels and grids; families with formulas; phases; and the drawing set (plans, four
  elevations, sections, schedules on sheets with title blocks, PDF, and the plan as DWG and DXF). Its model is IFC itself,
  written through one writer whose journal gives one undo step per action (architecture.md 1-2).
- The core has no DOM in its model path and runs headless in BimCraft's own Node tests (architecture.md 3); the four
  part notes recommended porting methods, before the owner's decision to copy. e05 settles it: copied unchanged and
  bundled, it runs in this app's runtime and passes their own checks.

## 2. The decision and what was built

The owner chose option A, copy unchanged (2026-11-28). Built:

- `vendor/bimcraft/`: 181 files of BimCraft @ 79b603f6 (the 35 roots of `tools/bimcraft/roots.mjs` and all they import,
  with their English wording `lang/en.json`), byte-identical (`copy_upstream.mjs --check`), with LICENSE, NOTICE,
  PROVENANCE, TRADEMARKS and THIRD_PARTY.
- `runtime/bimcraft/79b603f6/bim-craft.min.js`: one classic script (global BIMCRAFT, 1.78 MB, 554 KB compressed),
  pinned in `runtime/MANIFEST.json`, loaded only by DESIGN. Left out: manifold-3d (the app's own is handed over, over
  http), and `tin.js` with delaunator and robust-predicates (the Unlicense is not in the library rule's list); English
  strings cut to the 3,926 of 12,997 whose key families the copied code names.
- DESIGN (`bim/bimcraft-design.js`, `css/workspace/design.css`): the building starts on the app's levels; Wall (by
  type, joined), Door and Window (by type, on a click on a wall), Floor, Ceiling, Roof (on a click in a room), Section
  line; BimCraft's own live plan view (PlanView, its scene from planSceneOf: cut walls in layers, door swings, window
  symbols, rooms with areas); lists of walls, doors, windows and rooms; Undo and Redo (BimCraft's journal); Plan PDF;
  Drawing set PDF; Save IFC; Send to model, through the app's IFC import (GlobalIds, storeys, property sets kept; a second
  send replaces the first).

## 3. Edges and risks

- Two models: the design lives in BimCraft's IFC model; Send brings a copy into the app's model, locked (Make editable
  works for walls and slabs). Changes made in the app are not sent back (architecture.md, the plan).
- From file:// the browser refuses Manifold's WebAssembly, so openings are not cut in 3D meshes there; the plan, the
  drawings and the send do not need them (e05, the browser check).
- Upstream releases about weekly; the pin moves only with e05 and the browser check re-run (architecture.md 6).
- The design session is not yet saved with the project file (it is saved as IFC, and its result is sent to the model).

## 4. What is next (in this pull request or after)

Keep the design in the project file and reopen it; Open IFC into DESIGN; curtain walls, stairs and families in the panel
(the code is in the bundle: model-curtain, stair-family, family-model); grids; phases; the plan in the app's sheets.

## 5. References

BimCraft @ 79b603f6683f2f000b9e8346c1fc92cf466ab01d, https://github.com/getcadcraft/bimcraft, read and copied
2026-11-28 (P). The four part notes list every file and line read.
