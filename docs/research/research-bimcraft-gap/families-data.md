# BimCraft gap: families, parameters and BIM data

- Upstream: BimCraft (github.com/getcadcraft/bimcraft), Apache-2.0 (`LICENSE`; `NOTICE` present), pinned clone at
  commit `79b603f6683f2f000b9e8346c1fc92cf466ab01d` (2026-11-23 07:10 UTC), read as text only; no code of it was run.
- Date: 2026-11-28. Area: the parametric and data side of BIM (families, parameters, formulas, schedules, tags, phasing,
  design options, worksharing, stairs, railings and roofs as parametric elements).
- Levels (docs/research/research-protocol.md): P = read in the primary source here (file:line); S = a dependable secondary
  reading with the gap said; U = a pointer only. No U fact is used in a recommendation below.
- Paths: BimCraft files are under `app/` of the clone; ours under `src/js/engine/`.
- Every BimCraft file named here starts with the line `SPDX-License-Identifier: Apache-2.0` (P, line 1 of each file read).

## 1. Summary

BimCraft has a real family system: a family is a JSON "recipe" (parameters with kinds, formulas, instance or type flag,
solids bound to expressions, Booleans, nested families, hotspots, a 2D symbol with detail levels) stored inside the IFC
file as an IfcGroup with one IFC type object per size (`family-model.js` 1-45). A safe expression language with units and
`if()` drives it (`expr.js`). Schedules are one host-free layout engine (`tables/table.js`) with grouping, totals and
headings, fed by per-category readers; tags and phases are typed IFC properties that schedules and filters read.
What it does NOT have (P, by grep of `app/`): reference planes with dimension constraints in the family editor, Revit-style
shared parameters inside the model (only a writer and reader of Revit's shared parameter file, `prop-map.js` 137-153),
editable schedule cells that write back, phase objects with created/demolished pairs (it has one status per element),
design options for anything but massing, and worksets (its live session has element holds, not worksets).

Ours has types for seven structural/enclosure categories with propagation (`bim/type-instance-params.js` 117-125,
600-660), a fixed-column schedule list (`structure/analysis-properties.js` 265-330, `bim/usages-live-areas.js` 276-330),
three separate expression readers, mesh-only library families (`assets/family-library.js` 118-131), record blocks with
attributes (`assets/blocks.js`, `assets/block-attribs.js`), path stairs with guards (`bim/stairs.js`), one-pitch hip or
shed roofs (`bim/roofs.js` 254, 373), and room tags only (`bim/room-tags.js`). Doors and windows are holes in a wall with
a marker record and no leaf, frame or type (`bim/columns-openings.js` 406-437). That last point is the largest gap and the
first thing to build: parametric door and window families with types.

Because BimCraft's code is ES2020 (arrow functions, spread, `**`, optional chaining) and tied to its IFC writer
(`ModelWriter`, `ifc-util.js`), almost nothing is vendorable as is; its METHODS port well into small pure ES5 functions
over our JSON model. Only `tables/table.js` (no imports, P line 4) and `res-skeleton.js` (no imports, P) are
self-contained; even those are cheaper to port than to vendor under the library rule (runtime/, MANIFEST, on-demand load,
research and approval) for a core, always-on feature.

## 2. The data-model mismatch (P)

| Aspect | BimCraft | Ours |
|---|---|---|
| Store | The IFC file is the model; every edit is IFC lines through `ModelWriter` (`family-model.js` 6-12, `live.js` 9-15) | `A3D.objs` JSON records, `o.bim` per element; IFC is an export (`io/`) |
| Units, axes | mm, Z up (`family-model.js` 29-31, `libitem.js` 8-10) | metres, Y up, plan in XZ (`bim/columns-openings.js` 412-413 stores `center`, `dir` in XZ) |
| Family | IfcGroup + pset CadCraft_Family (recipe JSON in one IfcText) | library entry with a mesh, outside the project (`assets/family-library.js` 6-11, 118-131) |
| Type | one IfcDoorType / IfcWindowType / IfcFurnitureType per size, pset CadCraft_FamilySize (`family-model.js` 9-10) | `A3D.types[cat][i]` {id, name, params} (`bim/type-instance-params.js` 546-571); V307 will write them as IFC types |
| Instance | IfcRelDefinesByType to the size; instance values in pset CadCraft_FamilyInstance (`family-model.js` 368-404) | `o.bim.typeId`, `o.bim.typeCat`, the instance keeps its own copy of type values (`bim/type-instance-params.js` 19-28) |
| Language | ES modules, ES2020 | ES5 in one closure, modules joined by the build |

So a port keeps BimCraft's recipe shape (which is plain JSON and maps well) and drops its IFC storage: the recipe lives in
`A3D.families`, sizes become our `A3D.types` entries, and IFC export (V307's type objects) writes them out.

## 3. Feature table

Gap: NONE (we match), PARTIAL, MISSING. Close by: V vendor unchanged behind an adapter, P port the method into ES5,
X leave out. Effort: S (a day or less of pure functions), M (a few days), L (a phase).

| Feature | BimCraft (what, file:lines) | Ours (file) | Gap | Close by | Effort | Level |
|---|---|---|---|---|---|---|
| Family as a parametric recipe | Recipe: params, solids (box, extrude, revolve, sweep), Booleans, connectors; untrusted reader `readFamily` (`family-model.js` 14-35, 130-330); evaluator `evaluateFamily` (429-593) | Mesh families only (`assets/family-library.js` 118-131); V204 Pad/Pocket features (`bim/parametric.js` 5-222) | MISSING | P: recipe reader and evaluator, box and extrude first | L | P |
| Parameter kinds | length, angle, number, integer, yesno, pen, text, material, fill (`family-model.js` 66-68, `cleanValue` 100) | type params are bare numbers per category (`bim/type-instance-params.js` 117-125) | PARTIAL | P: kinds list and clean rule | S | P |
| Formulas (driven parameters) | A param with `formula` is driven; evaluated in the order inputs become known, cycle refused (`family-model.js` 437-449) | Usage formulas (`bim/usages-live-areas.js` 131-215); V204 `bimPfExpr` (`bim/parametric.js` 36); sheet formulas (`views/spreadsheet-eval.js` 44) | PARTIAL | P: the resolve loop over our `bimExprParse` | S | P |
| Expression language | Units in literals (mm cm m in ft, deg rad), comparisons, `if()`, trig in degrees, never eval (`expr.js` 1-23, 32-63, parse 105, evaluate 195) | `bimExprParse` / `bimExprEval`: + - * / ^, seven functions, no comparisons or units (`bim/usages-live-areas.js` 28, 131-215) | PARTIAL | P: add comparisons, `if`, unit suffixes to our one reader | S | P |
| Instance vs type parameters | `instance: true` params are per element and not part of a size (`family-model.js` 365-404) | Type params fixed per category in `TYPE_CATS[cat].typeParams`; everything else is instance (`bim/type-instance-params.js` 117-125) | PARTIAL | P: per-param flag in a family's params | S | P |
| Family types (sizes) | A size is the input values; `sizeKey` makes equal sizes one type; `sizeTypeFor` finds or makes it (`family-model.js` 406-427, 858-874) | `bimEnsureObjType` matches equal values to one type (`bim/type-instance-params.js` 575-599) | PARTIAL (same idea, no families) | P: `sizeKey` over a family's size params | S | P |
| Type propagation | A size is an IFC type; elements drawn from its RepresentationMaps, `writeSizeMaps` remakes them (`family-model.js` 904-932); retype `setFamilySize` (`family-ops.js` 597) | Write-through: the type's value copied into each instance and rebuilt, locked ones skipped (`bim/type-instance-params.js` 600-660) | NONE for our categories; MISSING for doors and windows | P: extend our propagation to family types | S | P |
| Type catalogs | Sizes from a CSV: columns by key or label, units in cells, 200 rows, 1 MB, errors reported (`family-csv.js` 1-16); Revit .txt type catalog `parseTypeCatalog` (`libitem.js` 2380-2405), but its own test says no real catalog was read yet (`tests/tools/bimcraft-test/family-types-test.mjs` 6-7) | none | MISSING | P: CSV sizes reader; the Revit .txt reader after a real file is tested | S | P |
| Nested families | `parts`: child family by key, values passed as expressions, quarter turns, cycle and depth (4) refused (read `family-model.js` 238-280, evaluated 507-548, joined 579) | none (blocks carry records, not parameters, `assets/blocks.js` 25-60) | MISSING | P, after box families work | M | P |
| Reference planes and dimension constraints | Not found: no reference planes, locks or flex in `family-*.js` (grep). Instead fields are expressions and drag handles solve the input that drives them (`family-edit.js` 18-22, `inputsOf` 706, `solve1` 720, `dragHandle` 755; `expr.js` `solveFor` 271-303) | 2D sketch solver with distance, equal, parallel and others (`drawing/sketch-constraints.js` 1-30, 187) | PARTIAL both | P: BimCraft's handle-solve (simpler than planes); X reference planes for now | M | P |
| Visibility and detail level per solid | `visible` expression, `detail` medium/fine (read `family-model.js` 187-188, applied 463; `family-symbol.js` 30-31) | none for families | MISSING | P | S | P |
| Arrays as parameters | `array {count, dx, dy, dz}` expressions (read `family-model.js` 190-199, applied 491-500) | none | MISSING | P | S | P |
| Family 2D plan symbol | line, rect, circle, arc, poly, text with parameters; cut-plane rule (`family-symbol.js` 1-23, `evalSymbol` 103) | Plan drawing of openings is the wall cut only | MISSING | P, after the 3D recipe | M | P |
| Starter door and window families | Door and window recipes written as boxes bound to Width, Height, WallThickness, Face, with driven Frame, Inner, Top (`family-starters.js` 26-111, doorRecipe 41-82, windowRecipe 83-111) | Doors and windows are holes plus a marker {width, height, sillHeight, hostWallId} (`bim/columns-openings.js` 406-437) | MISSING | P: the method (expression-built boxes), our own numbers | M | P |
| Hosted families | `host: wall`, the wall gives WallThickness and Face; door Width and Height required as size params (`family-model.js` 146-152, 172-176, 432) | Openings cut into a host wall and re-cut on rebuild (`bim/columns-openings.js` 208-300) | PARTIAL (host yes, family no) | P | M | P |
| Shared parameters | Writes and reads Revit's shared parameter file (`prop-map.js` 61, 137-153); no shared parameter object in the model | none | MISSING (both lack the in-model idea) | P: project parameter definitions as in tags (below), with a stable GUID per definition (V305's id) | S | P |
| Project parameters, tags | Tag definitions on the project (name, kind, pick list, classes); values per element; bulk tagging one undo step (`tags.js` 1-32, readTagDefs 98, checkValue 86, tagOp 260) | none on elements (`o.bim` keys only); block attributes for inserts (`assets/block-attribs.js` 1-12) | MISSING | P | S | P |
| Tags reading parameters | Tags are properties; tag schedule groups and filters by them (`tags.js` 315-340) | Room tag shows number and name only (`bim/room-tags.js` 29-33) | PARTIAL | P: a tag text template over any parameter | S | P |
| Schedules: fields | Per-category column specs with kind, role, sums (`schedule-layouts.js` 34-50); property columns read from element, then type (`propReader` 122, `withProps` 153) | Fixed `cols` per registered schedule (`structure/analysis-properties.js` 270-279) | PARTIAL | P | S | P |
| Schedules: grouping, totals, headings | `applyLayout`: groupBy, totals source/none/grand/groups, heading case, natural sort of groups (`tables/table.js` 14-40, 100-156) | none (`refreshSchedule`, `structure/analysis-properties.js` 307-325) | MISSING | P (or V, see 4.6) | S | P |
| Schedules: filters, sorting | Filters by find rules in the tag schedule (`tags.js` 312-340); rows sorted only within groups (`tables/table.js` 131) | none | MISSING | P: filter and sort keys as data | S | P |
| Schedules: figure links | Every line and figure keeps its element ids (`tables/table.js` 4-6, `figureIds` 157) | none | MISSING | P | S | P |
| Editable cells write back | Not found: schedule UI and agents set layouts, not values (`schedule-agents.js` 1-25; `mui-schedules.js` grep) | Our spreadsheet bindings write x, y, z, height, thickness, text into objects (`views/spreadsheet.js` 18-27, 68-114) | PARTIAL ours ahead | P from ours: route a schedule cell edit through the spreadsheet's apply | M | P |
| Phasing | One status per element: existing, demolish, new; hosted follow their wall; views all, existing, demolish, new, demo with ghosting; demolition schedule (`phases.js` 1-22, phaseOp 95, phaseView 164) | none (grep: no phase field on `o.bim`) | MISSING | P; Revit's created/demolished phase pair is a later step | S | P |
| Design options | Massing option sets only: one current per set, develop an option into levels and walls (`mass-options.js` 1-38); compared to a brief (`stages/options-side.js` 1-25) | none | MISSING | P for a general option set on any element (later) | M | P |
| Worksets, central model | None. Its live session has element holds and locks (`live-client.js` 318-319, 575-579) and reads Revit's worksharing flags only (`revit-card-ui.js` 132) | none | MISSING both | X (no server in this app's contract) | L | P |
| Stairs by component | Straight, L, U, winder, spiral; risers from height and limits; flights, landings, stairwell void; checks (`res-stair.js` 1-24, stairLayout 59-187); stair as a family with arrays (`stair-family.js` 1-16, 21) | Path stairs with landings at each turn, guard rails (`bim/stairs.js` 11-22, 41, 450) | PARTIAL (no winders, spiral, code checks, well) | P: stairLayout's checks and winders | M | P |
| Railings on a path | Path railing: posts at ends and corners, balusters under a gap rule (`res-railing.js` 1-18, railingParts 29-50) | Only on stairs (`bimBuildStairGuardMesh`, `bim/stairs.js` 225) | PARTIAL | P: railingParts (pure, 22 lines) | S | P |
| Roof by footprint and slopes | Per-edge pitch / gable / none, overhang and rake per edge, fascia, soffit, plate height (`res-roof.js` 1-21; pure part `res-roofplan.js` 1-10, roofGeometry 30-134; skeleton `res-skeleton.js` 30) | One pitch, gable edges, no overhang (`bim/roofs.js` 254, 373; "overhang" 0 matches) | PARTIAL | P: per-edge pitch and overhang into our skeleton | M | P |

## 4. Notes per gap

### 4.1 Families as recipes (the core)
BimCraft's recipe is the right shape for us because it is JSON and pure: `readFamily` treats the recipe as untrusted and
returns errors as `{key, fill}` (`family-model.js` 130-133), with hard limits on params, solids, expressions and sizes
(87). `evaluateFamily` does three things in order: (1) builds the value set from size and instance values plus host
context (432-435); (2) resolves formulas by repeated passes until no progress, which detects a cycle (437-449); (3)
evaluates each solid's fields as expressions and refuses flat or degenerate solids (461-505), then builds the Boolean
tree (561-578). Port those three steps; the
IFC parts (`bodyItems` 747, `writeSizeMaps` 904, `storeFamily` 834) are replaced by our mesh builders and `A3D` records.
Mismatch: mm and Z-up versus metres and Y-up; keep the recipe in metres from the start (our expressions then carry `m`
as the base unit, the unit suffixes convert).

### 4.2 One expression reader, not four
We already have three: `bimExprParse/bimExprEval` (usages), `bimPfExpr` (V204), `bimSheetEvaluate` (spreadsheet). The
usage reader is closest to BimCraft's (an AST, named functions, error strings). Extend it with BimCraft's grammar
additions (`expr.js` 9-15: comparisons giving 1 or 0, lazy `if(c, a, b)`; unit suffixes 16-19, 28-29; trig in degrees
32-40) and a `uses` list of names read (BimCraft's `parse` returns `uses`, used at `family-model.js` 444). Note a
counter-finding: `expr.js` says "import-free" (line 3) but imports `i18n.js` (line 25); vendoring it would need that stub.

### 4.3 Types for doors and windows
`TYPE_CATS` has no door or window (`bim/type-instance-params.js` 117-125), and the marker record carries only width,
height and sill (`bim/columns-openings.js` 412-413). Add `door` and `window` categories whose type is a family key plus
size values; `bimRebuildInstanceForType` (600) gains a case that re-cuts the opening and rebuilds the leaf mesh from the
family. BimCraft's `sizeKey` (`family-model.js` 417-421) gives the "same values, same type" rule our
`bimEnsureObjType` already uses (575-599).

### 4.4 Constraints: handles, not reference planes
BimCraft never built reference planes. Its editor binds fields to parameters and, on a drag, solves for the input
parameter through the formulas (`family-edit.js` 18-22, 706-745; `expr.js` `solveFor` 265-303: secant, then bracket and
bisection). That gives "flex the family" without a constraint solver. We also own a 2D solver (`drawing/sketch-constraints.js`
187) for a later reference-plane step. Recommend the handle method first.

### 4.5 Parameters and tags
`tags.js` is a good model for project and shared parameters: a definition list on the project (name, kind from the same
kinds list, pick list, classes it applies to; 11-16), values per element, typed checks (`checkValue` 86), rename that
renames values (`saveDefsOp` 244). For us: `A3D.paramDefs` and `o.params`; give each definition a stable GUID (V305's
`bimIfcGuidNew`) so it acts as a shared parameter and exports as a property set.

### 4.6 Schedules
`tables/table.js` is BimCraft's cleanest module: no imports, no DOM, no units (line 4); a TABLE plus a LAYOUT gives LAID
lines (group, row, subtotal, total) that keep element ids (14-40, 100-156). It is the only module that could be vendored
unchanged, but it is ES2020 and our schedules are core, so the library rule's on-demand loading does not fit; port it
(about 200 lines) as pure ES5 functions. Our registry (`bimRegisterSchedule`, `structure/analysis-properties.js` 270)
then hands rows plus column kinds to it. Editable cells: BimCraft has none; our spreadsheet already applies values to
objects as one undo step (`views/spreadsheet.js` 98-114), so a schedule cell edit should reuse that apply path.

### 4.7 Phasing
BimCraft's phasing is one status (existing, demolish, new) with hosted elements following their host and a view filter
(`phases.js` 6-21). It is small and maps directly to `o.bim.phase`. Revit's model (phase created and phase demolished
against an ordered phase list, plus phase filters) is richer; start with BimCraft's three-state status, keep the field
names open for a created/demolished pair later.

### 4.8 Design options and worksharing
BimCraft's options are massing only (`mass-options.js` 6-11). A general option set (each element in the main model or in
one option of a set; one primary per set) is ours to design; BimCraft gives the "exactly one current per set" rule
(`setCurrentOption`, `mass-options.js` 18). Worksets need a central model and a server; neither project has them, and the
owner's delivery contract has no server: X.

### 4.9 Stairs, railings, roofs
`railingParts` (`res-railing.js` 29-50) is pure and short: posts at path ends and corners, balusters spaced so no clear
gap exceeds the limit. Port it to give free path railings. `stairLayout` (`res-stair.js` 59-187) adds winders, spiral,
and code checks with limits as data (`STAIR_LIMITS` 37, `useStairLimits` 44) that fit our standards registry. The roof's
per-edge kinds and overhangs (`res-roofplan.js` 30-134 over `res-skeleton.js` 30, whose edges take a speed, 0 for a
gable) generalise our one-pitch skeleton (`bim/roofs.js` 89, 254).

## 5. Proposed build order (small pure functions, ES5, our names)

Each is a pure function with a unit test in `tests/unit/`; lengths in metres. Steps 1 to 6 give parametric door and
window families with types; the rest follow.

1. `bimExprParse(src)` extended: comparisons, `if`, unit suffixes, and `uses` on the result; `bimExprUses(ast)` gives
   the names read. Method: `expr.js` 9-19, 105-188. S.
2. `bimFamRead(obj)` returns {ok, family, errors}: the recipe's params (key, kind, value, formula, instance, label) and
   box solids (x0..z1 as expressions, style, visible). Method: `family-model.js` 130-210. S.
3. `bimFamResolve(fam, values, ctx)` returns {ok, env} or {ok: false, error}: size plus instance values, host context
   (wallThickness, face), formulas by passes, cycle refused. Method: `family-model.js` 429-449. S.
4. `bimFamBoxes(fam, env)` returns {ok, boxes: [{id, style, min, max}]} or the error, refusing flat boxes. Method:
   `family-model.js` 461-469. S.
5. `bimFamSizeKey(fam, values)` and `bimFamSizeValues(fam, values)`: the type identity. Method: `family-model.js`
   406-421. S.
6. `bimFamDoorRecipe(spec)` and `bimFamWindowRecipe(spec)`: our starter recipes (frame, leaf, glazing as boxes bound to
   Width, Height, WallThickness, Face). Method only: `family-starters.js` 26-111; our own dimensions. Then wiring (Claude):
   `door` and `window` in `TYPE_CATS`, the marker gains `typeId` and a leaf mesh from `bimFamBoxes`. M.
7. `bimFamSizesFromCsv(fam, text)` returns {sizes, errors, notes}: type catalogs. Method: `family-csv.js` 1-16. S.
8. `bimParamDefsRead(raw)`, `bimParamCheck(def, value)`, `bimParamApplies(def, obj)`: project and shared parameters.
   Method: `tags.js` 86-133. S.
9. `bimTagText(template, obj, defs)`: a tag reading any parameter, for door, window and room tags. S.
10. `bimSchedLayout(table, layout)` returns laid lines (group, row, subtotal, total, ids); `bimSchedFilter(rows, rules)`;
    `bimSchedSort(rows, keys)`. Method: `tables/table.js` 100-156. S.
11. `bimPhaseView(objs, mode)` returns {show, ghost}; `bimPhaseOf(o, objs)` with hosted openings following their wall.
    Method: `phases.js` 95-175. S.
12. `bimRailingParts(path, opts)` returns {rails, posts, balusters, length}. Method: `res-railing.js` 29-50. S.
13. `bimRoofEdgeKinds(outline, spec)` and per-edge pitch and overhang in the skeleton. Method: `res-roofplan.js` 30-134. M.
14. `bimFamArrayed(solid, env)`, `bimFamVisible(solid, env, detail)`, then nested parts `bimFamParts(fam, env, resolve,
    stack)` with cycle and depth refusal. Method: `family-model.js` 187-199, 463, 491-548. M.
15. `bimFamSolveHandle(fam, values, field, target)`: drag to flex. Method: `expr.js` 271-303, `family-edit.js` 706-760. M.

Order fit: steps 1 to 6 sit beside V204 (`bim/parametric.js`) and before V307 (types as IFC type objects), so V307 can
write door and window types too.

## 6. Open questions and limits

- Not read: BimCraft's UI files (`family-editor.js`, `family-ui.js`) beyond their headers; their behaviour is not claimed.
- Not run: no BimCraft test was run (the brief forbids running its code); its tests are listed as evidence of intent
  only: `tests/tools/bimcraft-test/families-test.mjs`, `families-more-test.mjs`, `family-types-test.mjs`,
  `schedules-test.mjs`, `tags-test.mjs`, `phases-test.mjs`, `mass-options-test.mjs`, `stairsketch-test.mjs`.
- Absences ("not found") are from grep over `app/` at the pinned commit; a feature under another name may exist.
- A second reader should re-check every line number in section 3 before a work order cites it.
- Owner decisions needed: (D1) families stored in the project (`A3D.families`) as BimCraft does, while the mesh library
  stays separate; (D2) one expression reader for usages, V204 and families; (D3) phasing as a three-state status first.
