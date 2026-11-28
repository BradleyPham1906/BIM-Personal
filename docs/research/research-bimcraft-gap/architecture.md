# BimCraft gap study: architecture and how to integrate

- Upstream: BimCraft, github.com/getcadcraft/bimcraft, Apache-2.0.
- Pinned commit: 79b603f6683f2f000b9e8346c1fc92cf466ab01d (2026-11-23, "README: links to the 0.11.0 release and
  zip"), local clone in the session scratchpad, deepened to its full history (48 commits, the first 2026-10-13).
  Read as text only. No BimCraft code was run; the one experiment (section 7) only bundled its files with esbuild.
- Date of this note: 2026-11-28. Area: how BimCraft stores and edits its model, its modules and their dependencies,
  which parts could ship in this app and how, licence and names, tests, release rhythm, and the integration options.
- Levels: P = read in the primary source here (file:line, or a command's output on the pinned clone). S = a
  dependable secondary reading, with the gap said. U = not read, a pointer only. Every recommendation rests on P facts.
- Decision (the owner, 2026-11-28): "copy their code ... reuse the codes, dont write new stuff". Option A below
  (vendor BimCraft's authoring core unchanged, behind an adapter) is chosen. Sections 1 to 7 are the evidence the
  options were weighed on; section 8 records the decision and what proves it; section 11 is the integration plan.
- State of this repository (P, `git status`, 2026-11-28): `vendor/bimcraft/` (151 files of `app/` at 79b603f6, copied
  by `tools/bimcraft/copy_upstream.mjs` from the roots in `tools/bimcraft/roots.mjs`; each was compared here with the
  clone byte for byte, 0 differ), `tools/bimcraft/build_bimcraft.mjs`, and
  `runtime/bimcraft/79b603f6/bim-craft.min.js` (1,276,393 bytes, global `BIMCRAFT`, pinned in
  `runtime/MANIFEST.json`). Uncommitted when read.

## Summary

BimCraft keeps no element model of its own beside the file: its model is IFC. Every authoring tool (walls, doors and
windows, slabs, roofs, curtain walls, levels, grids, families, views, sheets) writes IFC entities straight into the
open cc-ifc model through one journaled writer, `ModelWriter`, and reads them back from the same entities and from
property sets named `CadCraft_*`. Undo is a journal of lines made and lines changed. The authoring core is plain ES
modules with no DOM and no global state worth the name: BimCraft's own tests and its headless command-line core run
it in Node. Bundled with esbuild it is about 627 KB minified (216 KB gzipped) for 135 files, with no external library
on its static path. So BimCraft's core can ship here the way cc-ifc already does, as one pinned classic script
behind an ES5 adapter. The hard part is not the code but the data: our elements are JSON records (`A3D.objs`, `bim`
fields, metres, Y up), BimCraft's are IFC lines (millimetres, Z up, storey-local, types with layer sets, join
relations). The owner chose option A on 2026-11-28, and experiment e05 shows the unchanged bundle building
BimCraft's own test house in Chromium, 11 of 11 hand-worked checks passing over http and from `file://`. The
integration plan (section 11): BimCraft's IFC model is a design model of its own, edited in a BIM design workspace
with BimCraft's operations, and its results reach our JSON model only through our existing IFC import, replaced by
file and GlobalId on each send. No code translates our walls into BimCraft's and back.

## 1. How the model is stored and edited

**The model is the IFC file in memory, and the tools write IFC directly.** (P)

- `ifc/api.js:18` is cc-ifc's write surface: `CreateIFCGloballyUniqueId`, `WriteLine(mid, line)` (a new line gets the
  next free id, `api.js:213`), `DeleteLine` (`api.js:266`), `SaveModel` returns the bytes (`api.js:270`). It copies
  web-ifc's `IfcAPI` calls, which is why `IfcEditor` is constructed as `new IfcEditor(WebIFC, ifcModel)`
  (`ifc-edit.js:19-22`, `ifc-edit.js:54-56`): the "WebIFC" passed in is cc-ifc's `api.js` (`ifc-model.js:8`).
- `ifc-edit.js` is the editor for a model opened from a file. Its header (`ifc-edit.js:2-17`) says it edits attributes
  and single property values copy-on-write, because exporters share entities: a property set related to several
  elements is copied for the edited element, and a property shared by several sets is copied before it changes, so an
  edit only touches what the person picked. Library placements, deletes, copy and paste, and "building tools" are
  each one recorded change (`ifc-edit.js:24-39`): `ed.modelChange(op, { label, verb })` takes an op that returns a
  journal; redo runs the op again and names elements by GlobalId (`ifc-edit.js:35-37`).
- `ifc-place.js` (`IfcPlacer`, `ifc-place.js:135`) places items and keeps the journal: it writes with
  `this.api.WriteLine` (`ifc-place.js:149`, `157`), and `undoJournal` deletes what an action made and writes back what
  it changed (`ifc-place.js:25`, `841`). Geometry is stored once per type (`ifc-place.js:27-31`).
- `model-write.js` (`ModelWriter`) is "an IfcPlacer" whose journal makes each tool action one undo step
  (`model-write.js:6-8`); it offers placements in millimetres, profiles, extrusions, boxes, representations, property
  set and quantity set upserts, containment and type relations (`model-write.js:10-23`). Everything the tools write
  is the element's own lines, so a shape can be replaced without asking who else points at it (`model-write.js:24-27`).
- `model-ops.js` turns each tool into an op for `modelChange` (`model-ops.js:2-11`): `drawWalls`, `changeWall`,
  `removeWalls`, `newLevel`, `changeLevel`; `op(fn)` is at `model-ops.js:36`, `drawWalls` at `model-ops.js:155`,
  `snapshotModel(ed)` (what schedules read) at `model-ops.js:493`. Every op ends by regenerating the walls it touched.

**Walls** (`model-walls.js`, P). Written as IfcWall placed on its storey at its start point, an Axis IfcPolyline, a
Body IfcExtrudedAreaSolid of the joined outline, an IfcMaterialLayerSetUsage of the type's layer set, an IfcWallType
per wall type, Pset_WallCommon, Qto_WallBaseQuantities with openings taken off the net values, and a `CadCraft_Wall`
set (TypeKey, Length, Thickness, Height, BaseOffset, TopLevel as a level's GlobalId, TopOffset, ExteriorSide)
(`model-walls.js:21-27`). `readWalls` reads back only "the walls the tools made (pset CadCraft_Wall)"
(`model-walls.js:12`), so a wall imported from another program is an IFC element but not a BimCraft wall. Joins are
kept as IfcRelConnectsPathElements (`model-walls.js:695`, `720`). `addWall`, `updateWall`, `deleteWalls` (with what
they host), `regenWalls` are its interface (`model-walls.js:15-19`).

**Doors and windows** (`model-openings.js`, P). An IfcOpeningElement voids the host wall through IfcRelVoidsElement,
then an IfcDoor or IfcWindow is written (`model-openings.js:159-169`); they are read back with offset along the
wall, width, height, sill, hand and face (`model-openings.js:6-10`).

**Families** (`family-model.js`, P). "A family is BimCraft's idea; the file holds only plain IFC"
(`family-model.js:6`): a family is an IfcGroup with a `CadCraft_Family` set holding its recipe as JSON; each size is
an IfcDoorType, IfcWindowType, IfcFurnitureType and so on, whose representation maps are the size's solids; an
element relates to its size by IfcRelDefinesByType (`family-model.js:7-11`). Solids stay IFC's own: extrusions,
revolutions, swept disks, booleans in IfcCsgSolid (`family-model.js:11-12`). The recipe is read as untrusted data
(format "cadcraft-family" version 1, with parameters, formulas in `expr.js`, solids, booleans, connectors)
(`family-model.js:14-33`).

**Curtain walls** (`model-curtain.js`, P). IfcCurtainWall aggregating IfcPlate panels and IfcMember mullions, with a
`CadCraft_CurtainSystem` set carrying the frame, outline and grid (`model-curtain.js:9-21`); the layout itself is a
separate host-free module, `curtain/layout.js` ("no DOM, no IFC", `curtain/layout.js:3-5`).

**Views and sheets.** Plan view ranges, templates and sheets are kept as property sets on the levels
(`views-model.js:4-10`). A plan is cut from the meshes the viewer already has: `planCut(model, { M, storey, cutZ })`
(`model-plan.js:9`, `38`).

**What "host" means.** Two things, both P. (a) `host.js` is the file-access adapter every CadCraft app calls instead
of a browser picker or the desktop shell: open, drop, save, save as, recent files, folders (`host.js:3-30`); on the
desktop it uses a bridge the Tauri shell puts on the page, `window.cadcraftDesktop` (`host.js:47-60`, `358-359`); it
also carries the assistants' control channel (`host.js:64-66`, `1036-1046`) and Studio Live (`host.js:68-69`). It is
"DOM-optional", byte-identical across the apps (`host.js:6-9`). It is not part of BIM authoring. (b) In the model,
"hosted" means a door, window or family placed in a wall (`family-model.js:15-19`, `model-openings.js:2`).

**Both, then?** No. There is no second element model. What the tools hold in memory beside the IFC is derived and
throwaway: snapshots for schedules (`model-ops.js:493`), the viewer's mesh batches (`ifc-model.js:2-6`). (P)

## 2. Modules and dependency graph

**Plain ES modules, no build step.** "There is nothing to compile: BimCraft is plain ES modules"
(`BUILDING.md:3`). The page loads one entry module through an import map (`app/manifest.json`: `"module":
"bimcraft.js"`, imports for three, manifold-3d, proj4, pdfjs-dist, delaunator, robust-predicates and others). (P)

**Import graph** (P: a script in the scratchpad read every `import` and `export ... from` line under `app/` as text and
followed the relative ones; "closure" is the static import closure, files and lines):

| Root | Direct imports | Static closure | Notes |
|---|---|---|---|
| `ifc/api.js` (cc-ifc) | 7 | 21 files, 6,428 lines | the engine; nothing outside `ifc/` |
| `ifc-place.js` | 4 (`ifc-util`, `libitem`, `i18n`, `geom-vec`) | 7 files, 4,116 lines | |
| `model-write.js` | 2 (`ifc-place`, `ifc-util`) | 8 files, 4,520 lines | |
| `ifc-edit.js` | 5 (`report-as-core`, `ifc-place`, `ifc-elements`, `ifc-util`, `i18n`) | 10 files, 4,890 lines | cc-ifc is injected, not imported |
| `model-walls.js` | 14 (`project-materials`, `ifc-util`, `model-write`, `model-levels`, `model-rooms`, `i18n`, `model-arcs`, `wall-assemblies`, `wall-joins`, `wall-square`, `quantities/rules`, `new-policy`, `walls/joinstyle`, `geom-vec`) | 26 files, 7,399 lines | |
| `model-openings.js` | 11 | 34 files, 10,003 lines | |
| `family-model.js` | 9 (`expr`, `family-starters`, `opening-types`, `model-write`, `project-materials`, `family-symbol`, `ifc-util`, `i18n`, `mep/fixtures`) | 16 files, 6,615 lines | |
| `model-ops.js` | 18 | 90 files, 21,905 lines | pulls in finishes, classification, spaces, residential framing |
| `family-ops.js` | 12 | 106 files, 25,857 lines | |
| `model-curtain.js` | 7 | 95 files, 22,823 lines | imports `op` from `model-ops.js` |
| `model-schedule.js` | 6 | 37 files, 10,331 lines | |
| `schedule-data.js` | 14 | 102 files, 23,702 lines | |
| `model-plan.js` | 4 | 12 files, 5,236 lines | |
| `wall-plan-graphics.js` / `wall-section-graphics.js` | 7 / 8 | 95 / 96 files | |
| `views-model.js` | 7 | 97 files, 23,636 lines | |
| `views-ui.js` (the Views panel) | 19 | 125 files, 28,126 lines | DOM: `ui-util`, `drafting-ui`, `title-designer`, `sheet-notes-ui` |
| `bimcraft.js` (the app) | 219 | 798 files, 159,474 lines | three.js, `cc-workspace`, 77 dynamic imports, 6 files that start workers |

Once `model-ops.js` is reached, most authoring modules share one large closure (90 to 108 files), because the ops
keep every derived thing current after each change (`model-ops.js:16-33`: finishes, dimensions, classification,
spaces, rooms, residential framing). The ops and some of their dependants import each other (`model-curtain.js` and
`model-grids.js:35` import `op` from `model-ops.js`). (P)

**External libraries** (P, `THIRD_PARTY.md:7-31`): CoolProp, Delaunator, geotiff.js, Kiri:Moto, laz-perf, Liberation
Sans, Manifold 3.5.4, the noble libraries, OIDN weights, PDF.js, Proj4js, RDKit, robust-predicates (Unlicense,
`THIRD_PARTY.md:22`), three.js 0.186.1, three-gpu-pathtracer, three-mesh-bvh, the WebGPU build of three.js, web-e57,
Bootstrap and its icons, Archivo. On the authoring core's path only Manifold (through cc-ifc, for openings and
booleans) and, on one dynamic path, `tin.js` with Delaunator and robust-predicates (terrain under a house,
`res-terrain.js:37-40`) appear; three.js is not imported by any authoring module, only by the app and its viewer. (P)

**Its own renderer, `m3d/`.** ModelCraft's geometry kernel, shared as an identical copy by the apps with a 3D view
(`PROVENANCE.md:44-46`). Not on the authoring core's import path (P: absent from the closure above).

**Browser-only APIs and workers.** The cc-ifc open and mesh passes run in workers when the page has them
(`ifc-model.js:19-22`, `ifc/open-async.js`, `ifc/mesh-stream.js`) and fall back to the page's thread in Node and
without workers. In the authoring closure the only browser touches are guarded: `i18n.js:39-52` checks for
`document`, `unit-prefs.js:26` reads `localStorage` inside a try, `model-units.js:49`, `69` likewise, and
`util.js:37-42` creates a link only when `download()` is called. (P)

## 3. Self-containment

**Pure, by its own headers and by its tests.** 253 of 1,229 `.js` files under `app/` (help excluded) say "No DOM" in
their header and name the Node test that runs them (P, grep). Among them every authoring module this note looked
at: `ifc-edit.js:3`, `ifc-place.js:4`, `model-write.js:4`, `model-walls.js:4`, `model-openings.js:3`,
`model-ops.js:6`, `family-model.js:4`, `model-curtain.js:4`, `model-schedule.js:2-3`, `schedule-data.js:3`,
`model-plan.js:2`, `views-model.js:4`, `new-model.js:3` ("No DOM, no engine"), `ifc-model.js:6` ("No DOM and no
three.js").

The strongest evidence is BimCraft's own headless core: `tests/tools/cli/headless/ifc.mjs:9-15` creates a blank
building "as BimCraft's File > New building makes it", gets the `IfcEditor`, applies ops as undo steps and saves
bytes, in Node, with no page. (P)

A second, smaller layer is host-free: no IFC, no DOM, no app imports, plain numbers in and out.
`curtain/layout.js:3-5`, `walls/joins.js:3-6` (the join record; "No DOM, no model: walls in, records out"),
`walls/layerjoin.js:3-5` (layer priority at junctions, display only), `model-rooms.js:2-9` (rooms and outlines from
wall outlines), `model-roof.js:2-9` (roof planes from an outline), `quantities/rules.js:3-6` (gross minus deductions
equals net, one rule everywhere), `expr.js:2-7` (the parameter language, no `eval`). These can be called on our own
data without any IFC. (P)

**Global state.** Small and explicit. `model-walls.js:753-759` holds two module-level hooks (`SHAPE_HOOKS`,
`QUANTITY_HOOK`) that `wall-shape.js:415` sets when it is loaded: which behaviour a wall has depends on which modules
are in the bundle. `i18n.js` holds the language catalog; with none given, `t(key)` returns the key itself and records
it as missing (`i18n.js:20`, `103`), so error messages arrive as keys such as `model.err.cw.outline`
(`model-curtain.js:31-32`) unless the adapter passes strings to `init` (`i18n.js:36`). The English catalog is
873,093 bytes for all of BimCraft (P, `app/lang/en.json`). (P)

**Tangled with the UI.** The panels and the canvas: `views-ui.js` (imports `el` from `ui-util.js`, mounts
`drafting-ui.js`, `title-designer.js`, `sheet-notes-ui.js`; `views-ui.js:2-55`), `model-planview.js` (a 2D canvas
class, `model-planview.js:4-8`), `model-ui.js` and every `*-ui.js` and `*-wire.js` file, and `bimcraft.js`. These are
not candidates. (P)

**Experiment (P, run here 2026-11-28).** esbuild 0.28.2 (the version `tools/ifc/package.json` pins) bundled the
authoring roots `ifc-edit.js`, `model-ops.js`, `family-ops.js`, `model-curtain.js`, `schedule-data.js`,
`views-model.js`, `model-plan.js`, `wall-section-graphics.js`, `new-model.js` as one IIFE, three.js and the terrain
libraries external: 135 input files, 627,005 bytes minified, 216,120 gzipped, no unresolved import, and the only
browser-touching inputs were the five guarded files above. With cc-ifc's `api.js` added: 1,243,278 bytes. Per root:
`ifc-edit.js` alone 93,096 bytes (11 files); `model-ops.js` 449,765 (92); `family-ops.js` with `family-model.js`
464,638 (108); `model-curtain.js` 424,222 (97); `schedule-data.js` 290,391 (104). The script lives in the session
scratchpad (`bc-esb/measure.mjs`, `bc-esb/inputs.mjs`), not in the repository, because this task edits only this
note; it should move to `docs/research/experiments/` if the phase goes ahead.

## 4. Licence and provenance

- **Licence.** Apache-2.0 for the repository (`LICENSE`, `NOTICE:4`). Every app `.js` file outside the compiled
  help starts with an SPDX line: 1,531 `Apache-2.0`, one `Apache-2.0 AND ISC` (P, grep of 1,546 files). The ISC one is
  `app/usd/earcut.js`, which "follows" Mapbox's earcut (`THIRD_PARTY.md:35-39`); it is not on the authoring path (P:
  absent from the experiment's inputs). No authoring file names another project in its SPDX line. (P)
- **Provenance.** "We do not copy code from other projects" (`PROVENANCE.md:3`); copyleft programs (LibreDWG,
  web-ifc under MPL-2.0, occt-import-js) are used only as black-box test oracles, never shipped, never read
  (`PROVENANCE.md:9-14`, `38`). cc-ifc is written from ISO 10303-21 and the buildingSMART schemas
  (`PROVENANCE.md:36-38`). The repository's own statement; this note did not audit it line by line (S for the claim
  that nothing was copied; P that the statement is made).
- **NOTICE** must ship with any copy (Apache-2.0 section 4(d)); it says CadCraft and the app names are trademarks and
  "a fork must use another name" (`NOTICE:6-7`).
- **Trademarks** (`TRADEMARKS.md`). The names CadCraft, BimCraft, ModelCraft, MarkupCraft, TakeoffCraft, CivilCraft,
  DetailCraft, PartCraft, SuperCad Studio and the CadCraft logo are trademarks of The Data Design Group, Inc.
  (`TRADEMARKS.md:7`). Allowed: use and change the code; say truthfully "based on" or "works with"
  (`TRADEMARKS.md:11-13`). Required of a fork: its own name, not confusingly similar; no CadCraft logo; no suggestion
  of endorsement; the name shows in the app bar, page title, `devshell/app.json`, `lang/` and the help
  (`TRADEMARKS.md:15-19`). For this app: never show BimCraft's name or logo as ours, keep its name only in credits,
  licence files and comments that say where code comes from (as `vendor/cc-ifc/README.md` already does), and never
  ship its `lang/` or help text as our UI. Its `CadCraft_*` property set names are data written into IFC files, not a
  product name shown to a person; whether writing them in our files is fine is an open question below.
- **Libraries on the path, against our rule** (CLAUDE.md "Third-party libraries"). Manifold, Apache-2.0: already
  shipped (`runtime/cc-ifc/cfbd948/MANIFOLD-LICENSE`). Delaunator, ISC: allowed. robust-predicates, Unlicense: not in
  our rule's list (MIT, BSD, ISC, Apache-2.0, MPL-2.0, LGPL), so it needs the owner's decision or must stay out; the
  working-tree build already leaves `tin.js`, Delaunator and robust-predicates out as modules that throw if reached
  (`tools/bimcraft/build_bimcraft.mjs:6-8`, `22-26`). (P)

## 5. Tests

- **Layout.** `tests/bin/` has 8 runners (`test-bimcraft.mjs`, 3,165 lines, and seven narrower ones);
  `tests/tools/bimcraft-test/` has 296 files, of which 111 are `*-test.mjs` Node suites and 119 are `browser-*.mjs`
  Playwright scripts (`browser-04.mjs:76-83` launches a cached Chromium); `tests/lib/` holds shared libraries'
  tests. (P)
- **How they run.** `npm test` runs `devshell/test.mjs`: it fetches the pinned libraries, builds `.cc-test/`, "a copy
  of tests/ laid out like the getcadcraft.com repo the tests were written in", installs any npm or Python packages a
  test folder declares, then runs each runner (`devshell/test.mjs:5-16`). `--oracles` adds web-ifc, occt-import-js
  and LibreDWG as test-only references (`devshell/test.mjs:9-11`, `35`). CI runs `npm test -- --oracles` on Node 22
  (`.github/workflows/test.yml:26`, `41`). Development happens in another repository and arrives as "Sync from
  development" commits (P, `git log`), so the tests assume that other layout.
- **Coverage of the authoring core** (P, `tests/bin/test-bimcraft.mjs`): `--new` (145), `--walls` (148), `--plans`
  (163), `--schedule` (190), `--model` (195: units, joins L/T/X, levels, walls through `modelChange`, undo and redo,
  saved and reopened in cc-ifc and in web-ifc, `model-test.mjs:2-7`), `--draw06` (211), `--families` (236),
  `--views2` (239), `--views09` (251), `--schedules` (286), `--tools-b` (290, curtain walls), `--house` (303),
  `--edit` (316, copy-on-write, save, reopen, undo). Each mode imports the app's own modules from the build folder
  (`model-test.mjs:13-19`), so the same tests could be pointed at a vendored copy. Many need public sample files that
  live outside the repository and skip without them (`test-bimcraft.mjs` lines 63-80, `TESTFILES`).

## 6. Releases and how fast it changes

- **Tags** (P, `git ls-remote --tags`): bimcraft-v0.4.0, v0.5.0, v0.6.0 (also as bimcraft-v0.6.0), bimcraft-v0.7.0,
  v0.8.0, v0.8.1, v0.9.0, v0.10.0, v0.11.0. Their commits' dates (P, `git log`): 0.4 2026-10-13, 0.5 2026-10-15, 0.6
  2026-10-19, 0.7 2026-10-25, 0.8 2026-11-01, 0.8.1 2026-11-02, 0.9 2026-11-09, 0.10 2026-11-17, 0.11 2026-11-23.
  About one release a week. The 0.11.0 release ships `bimcraft-browser-edition-v0.11.0.zip` (`README.md:16`).
- **Volume.** 0.10 to 0.11: 2,174 files under `app/` changed, +172,597 / -33,769 lines (P, `git diff --shortstat
  4b570925 403686d0 -- app`). From `cfbd948` (the revision of our `runtime/cc-ifc`) to 79b603f6, eleven core files
  changed by 831 added and 46 removed lines, among them `model-walls.js` (127), `model-curtain.js` (216),
  `ifc/model.js` (123), and two new cc-ifc files for the mesh worker (P, `git diff --stat`). But from 0.10 to 0.11 the
  core changed little: `model-walls.js` +1/-6, `model-ops.js` +11/-1, `ifc-edit.js`, `model-write.js` and
  `family-model.js` not at all (P, `git diff --numstat`). The churn is mostly outside the authoring core.
- **Authors** (P): 24 commits by "CadCraft", 13 by Richard M. Davis, 8 by Renan Escoqui Meyer, 3 by Joel; one merged
  outside pull request (`aa77872a`, 2026-10-17).
- **npm.** None. `npm view` returned 404 for `bimcraft`, `@cadcraft/bimcraft`, `cadcraft`, `@getcadcraft/bimcraft`,
  `cc-ifc` and `@cadcraft/ifc` (P, run 2026-11-28). The root `package.json` is `"private": true` with no
  dependencies. Any reuse is a pinned copy of the repository's files, as cc-ifc already is.

## 7. Options

### Criteria, set before scoring

1. **What it adds**: Revit-like authoring the owner asked for (typed layered walls with joins, hosted openings,
   families with parameters, curtain walls, levels, plan and section views, schedules, sheets).
2. **Offline from `file://`**: `canvas_v10.html` must work from `file://`; a library loads on demand
   (CLAUDE.md, "Third-party libraries").
3. **Size**: bytes added to `runtime/` and loaded when the feature is used.
4. **ES5 adapter fit**: our code stays ES5 and calls a library through one narrow adapter in
   `src/js/engine/<feature>/`.
5. **Data-model fit**: with our JSON model, `A3D.objs` with `bim` records in metres and Y up (P,
   `src/js/engine/bim/columns-openings.js:136`, `413`, `430`; `src/js/engine/io/ifc-save.js:6-8`), walls as a
   centre-line polyline with one thickness and an alignment (`src/js/engine/bim/import-compliance.js:151`), doors by
   `hostWallId`, centre and direction.
6. **Churn risk**: cost of following a project that releases weekly.
7. **Licence and trademark**: Apache-2.0 obligations, the name rule, libraries outside our licence list.

### The table

| | A. Vendor the authoring core as a runtime bundle, adapter maps our model | B. Port selected methods into our ES5 engine | C. Switch our element model to BimCraft's (IFC-centred) | D. BimCraft as a separate app, files handed over |
|---|---|---|---|---|
| Adds | All of section 1 at once, as tested upstream; its pure modules (joins, layer clean-up, rooms, roof planes, curtain layout, quantity rules, expressions) are usable on our own records directly | Only what is ported, one method at a time; each port must be re-tested here | Everything in A, and IFC fidelity on save | Everything BimCraft has, in its own UI, not in ours |
| Offline `file://` | Yes: a classic script, as `runtime/cc-ifc` is (`src/js/engine/io/ifc-full.js:46-52`); its workers fall back to the page (`ifc-model.js:19-22`) | Yes | Yes, as A | No: its browser edition is ES modules and refuses `file://` (`devshell/edition/INSTALL.md:83-84`); it needs a web server or CadCraft Studio |
| Size | 627 KB minified for the core measured here (216 KB gzipped); the working-tree bundle with its own cc-ifc is 1,276,393 bytes, and duplicates `runtime/cc-ifc` (662,318 bytes, older revision) unless the import moves to it | Small, per method | As A, plus migration code | None in our app |
| ES5 adapter fit | Good: one global, plain objects, Maps and Uint8Array out; the same pattern as V196's cc-ifc | Native | Poor: every tool, panel, save path and test of ours would call IFC through the adapter | Good: a button and a file |
| Data-model fit | Partial. Pure modules fit with a unit change (mm and Z up). IFC-writing ops fit only if the elements they make live in a BimCraft IFC model; translating our walls in and out on every edit is lossy both ways (types and layer sets, join relations, `CadCraft_*` sets, top constraints) | Good: ported code is rewritten onto our records | Replaces ours: every element type, the project file, undo, history (`engine/history/`), layers and every feature that reads `bim` records | None: the hand-over is an IFC file, which we already read (cc-ifc) and write (IfcOpenShell, `src/js/engine/io/ifc-save.js:5-10`) |
| Churn risk | Medium: re-vendor on our schedule; the core changed little from 0.10 to 0.11, but upstream reorganises freely and is not a library with a stable API | Low after the port; we lose upstream fixes | High: our whole model tracks theirs | Low for us; their changes are theirs |
| Licence, names | Apache-2.0 with NOTICE; names only in credits; leave out robust-predicates (Unlicense) or ask | Apache-2.0 still applies to ported code: NOTICE and a statement of changes in each derived file | As A | Nothing shipped. Their handoff (`handoff.js:9-11`) works only between pages on one origin through IndexedDB, so a link from our Pages to getcadcraft.com cannot pass a file; the person saves and opens the IFC by hand |

## 8. Decision and evidence

**Decision.** The owner, 2026-11-28: "copy their code ... reuse the codes, dont write new stuff". Option A is chosen:
BimCraft's authoring core is copied unchanged and shipped as a pinned runtime bundle behind an ES5 adapter, as cc-ifc
was in V196. B (port), C (switch our model) and D (separate app) are not pursued. The table in section 7 supports
the choice on its own terms: A is the only option that adds the whole authoring set, runs from `file://`, and keeps
our model; its costs are size and the meeting of two models (section 11).

**What is in place** (P, read in the working tree 2026-11-28):

- `tools/bimcraft/roots.mjs`: `REV = '79b603f6'` and 34 roots (while `runtime/MANIFEST.json:430` describes the bundle as
  made from 33: the bundle may predate the last root added, so `build_bimcraft.mjs --check` should be run before commit): cc-ifc's `ifc/api.js`, `ifc-model.js`, `ifc-edit.js`,
  `model-write.js`, walls, joins, assemblies, openings, opening types, slabs, roofs, curtain walls, levels, rooms, plan
  and plan view, plan symbols, wall plan and section graphics, families and family symbols, phases, schedules, stairs,
  `new-model.js`, `model-ops.js`, grids, `res-views.js`, `res-sheets.js`, `comforts-views.js`, the annotation
  standard and scale, `spaces-geom.js`.
- `vendor/bimcraft/`: those roots and everything they import, 151 files, each identical to the pinned clone (checked
  here with `cmp`, 0 differ), with LICENSE, NOTICE, PROVENANCE.md, THIRD_PARTY.md, TRADEMARKS.md and `FILES.txt`
  (SHA-256 per file).
- `tools/bimcraft/build_bimcraft.mjs`: esbuild 0.28.2, one IIFE, global `BIMCRAFT`, one namespace per root
  (`build_bimcraft.mjs:1-5`). Left out as modules that throw if reached: manifold-3d (the app's own Manifold 3.5.4
  from `runtime/cc-ifc` is handed to the engine), `tin.js`, Delaunator and robust-predicates
  (`build_bimcraft.mjs:6-8`, `22-26`). No `import.meta`, so cc-ifc's workers fall back to the page
  (`build_bimcraft.mjs:9-10`). `--check` proves the committed bundle is what the script builds (`build_bimcraft.mjs`
  `--check` branch).
- `runtime/bimcraft/79b603f6/bim-craft.min.js`, 1,276,393 bytes, with LICENSE and NOTICE, pinned in
  `runtime/MANIFEST.json` (lines 412-432).

**What proves it works** (P for what the record says; this note read `docs/research/experiments/bimcraft/e05/`
`results.txt`, `run.mjs` and `page.html` and did not re-run them). e05 loads the bundle in Chromium (build 1243, by
Playwright), builds BimCraft's own test house with the calls of
`tests/tools/bimcraft-test/make-small-house.mjs`, saves it, reopens it and checks what `house-test.mjs` checks
against numbers worked by hand. Over http: 11 of 11 pass, Manifold loaded, a 90,989-byte IFC, built in 256 ms and
checked in 831 ms, no page errors; five walls, two doors, three windows, two rooms of 32.16 m2 each with floor and
ceiling, four 300 mm outer walls 10,000 and 7,000 long and one 100 mm partition, marks D1, D2, W1 to W3, grids and
section lines, elevations of the right widths, sections cutting 2 and 3 walls, and a four-sheet PDF drawing set.
From `file://`: 11 of 11 pass, but Manifold's wasm cannot be fetched there, so openings are not cut in the 3D meshes;
drawings, symbols and schedules do not need it (`results.txt`). This is the same limit the app's IFC import already
has and handles (`src/js/engine/io/ifc-full.js:33-38`, the `runtime/` source first off http).

**Still not shown** (open): no adapter in `src/` yet; the plan sheet is missing from e05's PDF ("the plan scene is
the page's, a later step", `results.txt`); the bundle's load time, memory and interactive speed on a larger model;
a second reader re-checking the P facts in this note.

## 9. Risks of the chosen option

- **Two models in one project** (section 11): undo, selection, layers, history branches
  (`src/js/engine/history/`) and our project save must each know which model owns an element.
- **Unit and axis conversion**: BimCraft works in millimetres, Z up, storey-local plan axes (`model-plan.js:2-4`,
  `ifc-place.js:11`); we work in metres, Y up. Through the IFC import this conversion is already done once, by code we
  have (`ifc-full.js:85`: "metres with +Y up"); any direct call on pure modules must do it again.
- **Hidden behaviour by import**: `wall-shape.js:415` installs hooks into `model-walls.js` at load; a root removed
  from `roots.mjs` can silently change what a wall does. Change roots only with BimCraft's tests in mind.
- **Messages as keys**: without a catalog, errors read `model.err...` (`i18n.js:103`); the adapter words them in our
  own language and never ships BimCraft's `lang/` text (trademark and copyright).
- **Left-out libraries**: a path that reaches `tin.js` throws (`build_bimcraft.mjs:22-26`); the adapter catches it and
  says that terrain under a house is not available.
- **Two copies of cc-ifc**: the bundle carries cc-ifc at 79b603f6 while the import uses `runtime/cc-ifc/cfbd948`.
  A file written by one and read by the other could differ; move the import to one revision.
- **Weekly releases**: re-vendor on our schedule, with `copy_upstream.mjs`, `build_bimcraft.mjs --check` and e05
  re-run, never by hand edits to `vendor/bimcraft`.
- **Main thread**: with no workers in the classic script, a large model meshes on the page (S: from the fallback code;
  e05's house is small).

## 10. Open questions for the owner

1. The meeting of the models, section 11: accept a separate BIM design model whose results are sent to our model as
   an IFC import (recommended), or ask for more (live two-way editing)?
2. Writing BimCraft's `CadCraft_*` property set names into the design model's IFC: acceptable as data (they are how
   BimCraft reads its own elements back, `model-walls.js:12`), with the names never shown as ours?
3. robust-predicates (Unlicense, not in the library rule): keep terrain-under-a-house out, or add the Unlicense?
4. Re-vendor rhythm: each BimCraft release, or only when a needed fix lands?
5. Size: 1.28 MB (about 395 KB compressed, `results.txt`) on demand when the BIM design workspace opens: acceptable?

## 11. Integration plan: how our JSON model and BimCraft's IFC model meet

**The two models** (P). Ours: `A3D.objs`, records with `bim` fields in metres, Y up; walls as centre-line polylines
with one thickness (`src/js/engine/bim/import-compliance.js:151`), doors by `hostWallId`
(`src/js/engine/bim/columns-openings.js:413`). BimCraft's: IFC lines in cc-ifc's memory, millimetres, Z up, walls as
two-point segments with layered types and join relations, read back only from `CadCraft_*` sets (section 1). Neither
can hold the other without translation code, and the owner's rule is to reuse, not write new stuff.

**Ways they could meet**

| | M1. Design model in a workspace; results sent through our IFC import | M2. Live mirror of BimCraft's meshes in our scene | M3. Translate our elements into BimCraft ops and back |
|---|---|---|---|
| New code | Small: the workspace, the bundle's loader, a send that replaces by file and GlobalId | Medium: draw cc-ifc batches beside `A3D.objs`, keep both in picking and layers | Large: mapping both ways for every element type |
| Reuse | BimCraft's ops, plans, sheets, schedules unchanged; our import unchanged (`ifc-full.js:210-260`) | BimCraft's ops; our renderer extended | Little: the mapping is new |
| Fidelity | IFC is the exchange both sides already trust: e05 saves and reopens it; our import keeps class, GlobalId, storey, property sets per element (`ifc-full.js:242-243`) | Exact (same meshes) | Lossy: types, layer sets, joins, top constraints have no place in our records |
| Undo | Two stacks: BimCraft's journal inside the workspace (`ifc-edit.js:35-39`), ours for the send (one `pushUndo`, `ifc-full.js:219`) | Two stacks, live: confusing | One stack, but over translated data |
| Fits the owner's rule | Yes | Partly | No |

**Recommended: M1.**

1. **A BIM design workspace.** A workspace of its own (like Analyze) holds one BimCraft design model per project:
   created with `BIMCRAFT.newModel` (`new-model.js:5-10`, `newBuilding`), opened in the bundle's cc-ifc, edited only
   through `IfcEditor.modelChange` with BimCraft's ops (`model-ops.js:2-11`), so BimCraft's undo, redo, joins,
   regenerations, views, sheets and schedules work exactly as its tests prove. Its IFC text is saved inside our project
   file (its own key beside `A3D.objs`), so the project opens, edits and saves offline as before; the bundle loads only
   when the workspace opens (CLAUDE.md, "Loaded on demand").
2. **Send to model.** A command saves the design model's bytes (`ed.save()`, `ifc-edit.js:21-22`) and passes them to
   our IFC import, `bimIfcImportBuffer(bytes, name)` (`ifc-full.js:210`). The import already makes one locked solid per
   element on a layer per IFC class, with `bim.imported`, `bim.guid`, `bim.ifcType`, `bim.storey`, `bim.file` and its
   property sets (`ifc-full.js:236-247`), as one undo step (`ifc-full.js:219`). Before importing again, the send removes
   the objects whose `bim.file` names the design model, so a second send replaces rather than duplicates. That removal
   is the only new logic on our side (a unit test, Rule #1). Element identity across sends is the GlobalId: BimCraft
   names elements by GlobalId through undo and redo (`ifc-edit.js:35-37`, `model-write.js:12`), so a link, a schedule
   row or a note of ours tied to a `bim.guid` survives a send.
3. **One direction for editing.** Elements that came from the design model stay locked in our editors (the import
   already sets `locked:true`, `ifc-full.js:250`); to change one, the person goes back to the workspace. Our own
   elements stay ours and are untouched. Bringing an existing wall of ours into the design model is not offered in the
   first phase; if the owner wants it later, it is the narrow "convert" of M3 for walls only, written as BimCraft's
   `drawWalls` input (`model-ops.js:155`), one way.
4. **Levels.** The import adds a level named "<storey> (IFC)" when none of that name exists
   (`ifc-full.js:226-230`); BimCraft's storeys come from `model-levels.js`. On a second send the levels match by name
   and are not repeated.
5. **Our other features see the results**: sections, saved views, sheets, analysis and export read `A3D.objs`, so they
   work on what was sent, as on any imported IFC. BimCraft's own plans, sections and sheets stay inside the workspace;
   whether they are also offered as our sheets is a later phase.
6. **One cc-ifc.** The import should use the bundle's cc-ifc (`BIMCRAFT.ifc`) or `runtime/cc-ifc` rebuilt at
   79b603f6, so the file BimCraft writes is read by the same engine.
7. **Tests for the phase**: e05 kept as the bundle's browser check; unit tests for the adapter's send and replace and
   for unit conversion; one browser check of the workspace before the phase closes (Rule #1).

**Risks of M1.**

- **Stale copies.** The sent elements are a snapshot; a design change not yet sent is not in our model. The workspace
  must show when the design model has changed since the last send.
- **Edits lost.** Anything a person does to a sent element in our model (a material, a layer move) is replaced on the
  next send. Locking prevents most of it; properties we add must be keyed by GlobalId outside the element, or be lost.
- **Size of a send.** The import meshes the whole design model each time; for a large building that is seconds, and
  without Manifold from `file://` openings are not cut (e05, `results.txt`).
- **Two undo stacks.** Undo inside the workspace undoes design changes; undo outside undoes a send. The workspace must
  say which one is active.
- **Project file growth.** The design model's IFC text is stored as well as the sent meshes (e05's small house: 90,989
  bytes of IFC).
- **What would change this plan**: if the owner wants to edit BimCraft elements from our own tools, M2 or a wider M3 is
  needed and is new code; if IFC should become the app's native model, this workspace is the first step toward
  option C.

## Ten-line summary

1. BimCraft's model is IFC itself: its tools write IFC entities into cc-ifc's in-memory model through `ModelWriter`.
2. Each tool action is one journaled undo step; edits to imported files are copy-on-write; elements are named by GlobalId.
3. Its authoring core is plain ES modules, DOM-free, tested in Node and driven headless by BimCraft itself.
4. Bundled, the core is 627 KB minified; with its cc-ifc the app's bundle is 1,276,393 bytes, no library on its path.
5. Licence Apache-2.0 throughout; BimCraft's names are trademarks, credits only; robust-predicates is left out.
6. Upstream releases weekly (0.4 to 0.11 in six weeks), has no npm package, so reuse is a pinned copy.
7. Decision (owner, 2026-11-28): option A, copied unchanged: 151 files, `runtime/bimcraft/79b603f6`, global `BIMCRAFT`.
8. Evidence: e05 builds BimCraft's test house in Chromium through the bundle, 11 of 11 checks, http and `file://`.
9. Plan: a BIM design workspace holds BimCraft's model; "Send to model" passes its IFC through our existing import.
10. Main risks: stale or overwritten sent elements, two undo stacks, two cc-ifc revisions; owner questions in section 10.
