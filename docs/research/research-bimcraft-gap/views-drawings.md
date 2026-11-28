# BimCraft gap study: drawings generated from the model

- Upstream: BimCraft, github.com/getcadcraft/bimcraft, Apache-2.0 (LICENSE, every app file starts with an
  SPDX-License-Identifier: Apache-2.0 line, for example app/model-plan.js:1).
- Pinned commit: 79b603f6683f2f000b9e8346c1fc92cf466ab01d (2026-11-23), local clone in the session scratchpad.
  Read as text only. Nothing from it was run.
- Date of this note: 2026-11-28. Area: plan views, cut and projection, poche, door and window symbols, elevations
  and sections, view templates, visibility and graphics, line weights, crop, detail levels, tags, dimensions,
  keynotes, sheets and title blocks.
- Levels: P = read in the primary source here (file:line). S = a dependable secondary reading, with the gap said.
  U = not read, a pointer only. Every recommendation below rests on P facts only. The Revit feature list is the
  owner's request used as a checklist; Revit's own documentation was not read for this note (U), so no Revit
  behaviour is stated as a fact the code would use.

## Summary

BimCraft has the production core this app lacks: a plan view that is a real horizontal cut through the model at a
view range (cut, top, bottom, depth) with three outputs per element (cut loops, edges below, edges above drawn
dashed), drawn as poche on a 2D canvas, on sheets and in PDF from the same scene object. Walls and doors are drawn
from their parameters (walls as joined outlines with openings removed at the cut height; doors with swing arcs and
leaves), and everything else from its mesh. Elevations and sections are computed from the triangles with hidden
lines removed through a software depth buffer. View range, scale, crop, detail level and hidden categories live in
a per-level view record with view templates. Annotation text is sized from paper heights by one rule.

This app draws its floor plan as the 3D renderer looking straight down (toggleFlat sets pitch 1.52 and an
orthographic projection), so there is no cut plane, no poche by cut, no below/above distinction and no symbolic door
swing. A sheet's plan viewport is drawn as vector SVG from the bim records (wall loops broken at openings, rooms,
dimensions, room tags), with no cut height; elevation and section viewports are raster images. The section tool
clips solids' meshes with one live plane, which is the right primitive to grow a plan cut from.

The data models differ in three ways that drive every recommendation: BimCraft is IFC-centred, millimetres, Z up,
plan x/y; ours is A3D.objs in metres (S: inferred from the room label's "m2", bim/room-tags.js:27), Y up, plan
[x, z]. BimCraft walls are one straight or arc segment (a, b, t, bulge); ours are polylines (bim.centerline, which
may be closed, with innerLoop/outerLoop). BimCraft doors carry hand and face; ours do not. Almost nothing should be
vendored: BimCraft modules are ES2020 and import the IFC layer (ifc-util.js, model-ops.js, model-write.js). A few
small pure files can be ported almost line for line. The pure geometry methods (planCut, triCut, chainLoops,
wallPieces, openingSymbol, projectMeshView, effectiveView) are the parts to port into our ES5 engine.

## Gap table

| Feature | BimCraft (what, file:lines) | Ours (file) | Gap | Close by | Effort | Level |
|---|---|---|---|---|---|---|
| Plan as a horizontal cut | planCut cuts every element of a storey at cutZ; cut segments per element; wholly-below elements give 30-degree feature edges; wholly-above-under-top give `above` edges (model-plan.js:32-80); triCut, one triangle against z = h, with edge-order-stable points (model-plan.js:84-99) | Plan = 3D camera from above: toggleFlat sets pitch 1.52 (drawing/plan-mode-sketch.js:408-434), orthographic projection when flat (render/webgl.js:33-37). Sheet plan viewport has no cut height (sheets/viewports.js:541-728) | MISSING | P: port triCut and the classify-by-z-extent logic of planCut; reuse our bimClipTriangle cut edge (views/section-tool.js:33-55) | M | P |
| View range: top, cut, bottom, depth | RANGE_DEFAULTS cut 1200, top 0 (= level height), bottom 0, depth 50; RCP_DEFAULTS cut 2300 (views-model.js:53-55); effectiveView merges template and view (views-model.js:114-125); checkRange bottom <= cut <= top (views-model.js:126-129); stored per level in CadCraft_PlanView (views-model.js:7-12) | None. A3D.levelFilter shows one level or all (views/saved-views.js:277-287) | MISSING | P: port effectiveView and checkRange as pure functions over a plain view record on each level | S | P |
| Cut vs projected vs beyond | Scene arrays cut / below / above; below drawn thin grey 0.13 mm, above dashed, cut filled grey 0.75 with 0.25 mm outline (res-sheets.js:93-103 planItems); canvas draws `above` dashed (model-planview.js:286) | Every plan object drawn the same; walls as loops, floors and roofs as filled outlines (sheets/viewports.js:630-728) | MISSING | P: three line classes in a new plan scene; weights as data | S | P |
| Cut poche of walls | wallPieces: the wall's joined outline with openings removed only where the cut passes through them (sill <= cutZ <= sill + height), Sutherland-Hodgman in the wall frame (model-plan.js:135-173); wallPlanGraphics: coarse = envelope, medium/fine = layer bands with material fills, hatch at fine (wall-plan-graphics.js:87-159); layer priority at junctions (wall-plan-graphics.js:161-198) | Wall poche as even-odd outer minus inner ring, only when no openings and presentation mode with a fill; otherwise runs broken at openings with jambs (sheets/viewports.js:608-629, io/dxf-export.js:22-108) | PARTIAL | P: port wallPieces per centerline segment; keep bimWallOpeningBreaks for the runs; add the sill/height test so a high window does not break the wall at the cut | M | P |
| Cut poche of other elements (slabs, columns, imports) | chainLoops joins cut segments into closed loops, 0.01 mm keys (model-plan.js:101-133); filled even-odd on canvas (model-planview.js:296-299) and on paper (res-sheets.js:99-101) | Floors, roofs, columns drawn as outlines from parameters (sheets/viewports.js:715-727), never cut | MISSING | P: chainLoops, or reuse bimChainEdgesToLoops (views/section-tool.js:56) on the horizontal cut | S | P |
| Material cut pattern | Layer fill from the material, hatch strokes via hatchSegments at fine (wall-plan-graphics.js:91, 136-139; drafting.js:229) | Material supplies the cut pattern, type and instance override it (bim/type-instance-params.js:466-500); pattern registry for SVG (io/export-mappings.js:317) | PARTIAL (ours has the data, not the cut) | Reuse ours; feed the cut loops into the existing pattern path | S | P |
| Door swing and window symbol | openingSymbol: jambs, leaf line and swing arc (short way round), double leaves, slide, pocket, bifold, barn, sidelites; window frame, glass, sash, casement; pick polygon (model-openings.js:492-573); hand 'a'/'b' and face 'left'/'right' (model-openings.js:15-20) | Jambs and one glazing line for windows, no door leaf or arc (io/dxf-export.js:92-106). Door record has no hand or face (bim/columns-openings.js:413) | PARTIAL | P: port the single-leaf, double-leaf, slide and window branches; add bim.hand and bim.face with defaults | M | P |
| Symbolic vs model lines | Plan symbols drawn from a set at the plan's scale, stored as which/where only (plan-symbols.js:2-15); family symbols with per-part detail (family-symbol.js:26-31, 103-113); drafting lines and hatch owned by one view (drafting.js:2-30) | Annotations may carry viewId and show only in that view (views/saved-views.js:268-271); hatch objects (drawing/hatch.js:10-12) | PARTIAL | P: a per-view drafting flag already exists (viewId); symbolic plan geometry per family is later work | M | P |
| Elevations from the model | projectMeshView: triangles to view coordinates, depth buffer raster, feature edges (crease over 25 degrees) sampled against it, collinear merge, box clip (res-views.js:74-164, 198-264); four elevation directions (res-views.js:26); recomputed from the model on each build, so it follows edits | Elevation = orthographic camera preset (views/saved-views.js:142-149); on sheets raster only (sheets/viewports.js:731-733) | MISSING (vector) | P: port projectMeshView, raster and featureEdges as ES5 | L | P |
| Sections from the model | Same projector with cut.o and far; cut triangles give poche loops (res-views.js:96-104); section lines stored as records (res-sheets.js:547-615); wall layers in section (wall-section-graphics.js:95-173) | One live section of solids, mesh clip with capped loops, camera aimed along it (views/section-tool.js:112-200); not saved, not on sheets as vector | PARTIAL | P: keep our clip; add a section-line record and the projector for vector output | L | P |
| View templates | Template = { cut, top, bottom, depth, hidden, scale } in one project property set; a view using one takes its range, scale and categories, keeps its own crop and hidden elements (views-model.js:13-14, 114-125, 157-190) | None | MISSING | P: port effectiveView's merge rule over A3D view records | S | P |
| Visibility by category | hiddenClasses and hiddenGuids per view, applied before the cut (views-model.js:9-10, mui-data.js:79-89, 129-137) | Layers shown/hidden globally (layers/layer-rules.js, bimLayerShown); level filter (views/saved-views.js:277-282) | PARTIAL | P: a per-view hidden category list (our bim.type values) and hidden ids | S | P |
| Graphics overrides by category | View pens: category, type or element scope, weight, dash, colour; most specific wins (pens.js:2-20, 45) | Type and instance graphics (technical / presentation) per object (bim/type-instance-params.js:286-300, 466); layer lineweight (layers/plot-by-layers.js:61-62) | PARTIAL (no per-view override) | P: port the scope precedence of penFor as a per-view list over our graphics dict | S | P |
| Line weights by scale | Fixed paper weights: below 0.13, cut 0.25, section cut outline 0.45 mm (res-sheets.js:96-101, wall-section-graphics.js:171); penMm maps screen px to mm (pen-colors.js:9) | Fixed lineWeight 0.25 mm default (bim/type-instance-params.js:292) | MISSING in both | X for now: no source to port; a scale table is our own design later | - | P |
| Crop region | crop [x0, y0, x1, y1] per view, minimum 100 mm side (views-model.js:9-12, 41); plan veiled outside it (model-planview.js:24); clip items on paper (res-sheets.js:89-91) | Sheet viewport rectangle crops implicitly (sheets/viewports.js:60, 541-551) | PARTIAL | P: crop box on the view record, clip at scene build | S | P |
| Detail level coarse / medium / fine | PLAN_DETAILS (wall-plan-graphics.js:15); coarse = envelope, medium = layers, fine = layers plus hatch (wall-plan-graphics.js:91, 105); projected views carry detail (projected-views.js:9) | None; walls have no layer assembly in our records | MISSING | P: the switch is trivial; it needs wall layer data we do not have (coarse only until then) | S (switch) / L (layers) | P |
| Annotation scale | annoscale.js: one rule, paper height times ratio = model height; KINDS text, dimension, tag, room, grid, title, schedule; no imports (annoscale.js:1-87) | Fixed text sizes in sheet mm, 2.4 and 3.0 (sheets/viewports.js:657, 708-712) | MISSING | P: port fontPt, paperMm, modelHeight (pure, 87 lines) | S | P |
| Door and window tags | Marks on elevations and interiors: tag items with box or hex shape (comforts-views.js:61-104); tag values as IFC properties feeding schedules (tags.js:2-25); a plan door tag drawing was not found (grep "t: 'tag'" hits comforts-views.js only) | Room tags only (bim/room-tags.js:20-45); no door or window tag object | MISSING (BimCraft partial) | P: a tag object type, label read from the host's parameters, drawn at the opening's centre | M | P |
| Room tags | Room label from the space's name and the loop's area (mui-data.js:173-181); rooms from walls by loop walking (model-rooms.js:26, no imports) | Room tags with roomId, text from number and name (bim/room-tags.js:26-45); rooms exist | NONE (ours equal for this purpose) | - | - | P |
| Dimensions in views | wallDims along a face with opening chains (model-plan.js:196-228); saved wall dimensions bound to wall references (wall-dimensions.js:9-30); autodim: overall plus outside chains in one undo step (autodim.js:1-25) | Linear, angular, radius, leader dims as objects, optional viewId (annotation/dimensions.js, sheets/viewports.js:661-692); not bound to wall faces | PARTIAL | P: port wallDims for a generated chain; reference binding later | M | P |
| Keynotes | Numbered legend from layers and classifications, keynote file parser, legend text items; import-free (keynotes.js:1-80) | None | MISSING | P: small pure file, port directly | S | P |
| Sheets and title blocks | Papers (res-sheets.js:53), scale list and scaleFor (res-sheets.js:62-83), sheet view placement by kind and ratio (views-model.js:15-18), arrangeSheet (res-sheets.js:396), title block items or a user SVG (title-block.js:9-30, title-svg.js) | Sheets, viewports with scaleDenom, pan, snapping; title block SVG; print set (sheets/viewports.js:54-123, 763, 873-943); page sizes (sheets/page-sizes.js) | NONE to PARTIAL (ours lacks elevation/section vector content) | Keep ours; feed it the new plan scene | - | P |
| Ceiling plan, callouts, view copies | RCP looks up from 2300 (views-model.js:55, mui-data.js:102); callouts crop a parent view (views-model.js:19-28); duplicate view own or linked (view-copies.js:42-264) | None | MISSING | After the live plan; same scene builder with another range | M | P |

## Notes per gap

1. Plan cut (the root of the rest). BimCraft keeps the batch's vertices in plan axes once, then per element takes the
   z extent; an element that spans cutZ gives cut segments, one wholly below (and not deeper than bottom minus
   depth) gives feature edges, and one wholly above but under top gives `above` edges (model-plan.js:43-79). Edges
   seen end on, shorter than 0.5 mm in plan, are dropped (model-plan.js:73-75). Ours: each solid has o.pos and
   o.mesh {v, f} with faces of three or more indices (views/section-tool.js:112-120, 139-141), Y up, so the cut is
   the plane y = levelElev + cut. bimClipTriangle already returns a cutEdge per straddling triangle
   (views/section-tool.js:33-55); a plan cut needs only those edges, not the kept half or the cap, so a new pure
   function should not call bimClipMeshToPlane (which also welds and caps, views/section-tool.js:126-131).
   BimCraft's feature edges come from runEdges in ifc-vis.js:134 (its body was not read: S) and, for views,
   featureEdges (res-views.js:217-241, read: P); port the latter.
2. Walls by parameters, not mesh. BimCraft skips the meshes of elements its tools drew and draws them from
   parameters (mui-data.js:113-120, ownKeys, and the skip set at mui-data.js:97). Ours already does this on sheets (sheets/viewports.js:608-629). The
   live plan should do the same: walls, doors and windows from records, everything else from the mesh cut. The
   mismatch: wallPieces works in one wall's local frame; our wall is a polyline, so the
   frame is per centerline segment (BimCraft's frame: model-plan.js:142-145), and the outline is the even-odd ring between outerLoop and innerLoop rather
   than one joined polygon.
3. Openings at the cut. BimCraft takes an opening out of the wall only when the cut height lies inside it
   (model-plan.js:149). bimWallOpeningBreaks breaks the wall at every opening regardless of height
   (io/dxf-export.js:32-60). A clerestory window above the cut is therefore drawn as a break today; the port adds
   the sill/height test (our record has sillHeight and height, bim/columns-openings.js:430).
4. Door symbols. Port the plain-leaf branch (model-openings.js:541-553), the double-leaf case (same lines, type
   leaves 2), slide (model-openings.js:508-511) and the window branch (model-openings.js:555-567, frame and
   glass lines). Our door needs two new fields, bim.hand and bim.face, with defaults that reproduce today's look;
   a migration that adds them on load is one small function. Swing arcs come as { c, r, a0, a1 }, which our SVG
   path can draw as an arc or a 16-step polyline as the angular dimension already does (sheets/viewports.js:663-668).
5. Elevations and sections. projectMeshView is self-contained apart from wallSectionGraphics, which projectView
   calls only when walls are passed (res-views.js:65-72). Its parts: clipTri (res-views.js:48), raster
   (res-views.js:198), visible with a 3 by 3 neighbourhood and a depth tolerance (res-views.js:136-143), edge
   sampling at 0.75 px steps (res-views.js:147-157), mergeCollinear and box clipping (res-views.js:160-163). It is a
   software depth buffer at 1600 px on the long side, so its cost grows with triangle count; it runs on demand, not
   per frame. Recommended as P, effort L, after the plan.
6. Templates and per-view visibility. The merge rule is small and clear: a template, when named, supplies range,
   scale, detail and hidden categories; the view keeps crop, underlay and hidden elements (views-model.js:114-125).
   Our A3D.views records saved cameras (views/saved-views.js:24-46); plan view settings belong on the level or on a
   new plan-view record keyed by level id, not on a saved camera.
7. Annotation scale. annoscale.js is import-free and states that it is copied byte for byte between hosts
   (annoscale.js:4-6). It is ES2015 syntax (arrow functions, default parameters), so as our code it must be ported
   to ES5; vendoring it under runtime/ for 87 lines is not worth the manifest entry.
8. Line weights by scale. Neither app has a per-scale weight table; BimCraft prints fixed paper weights
   (res-sheets.js:96-101). Nothing to port; a table keyed by scale and line class is our own design later (X now).
9. Tags. BimCraft's tags.js is the property model (tag values as IFC properties for schedules), not graphics. Its
   graphical marks exist on elevations (comforts-views.js:78, 100). A Revit-like plan door tag reading the opening's
   parameters is new in both; ours should be a sibling of roomtag (bim/room-tags.js), an object with hostId and a
   label template.
10. Vendoring. No BimCraft view module is self-contained enough for (V): model-plan.js imports ifc-vis.js,
    ifc-util.js, model-arcs.js and geom2d.js (model-plan.js:20-23); res-views.js imports wall-section-graphics.js,
    which imports model-walls.js and model-openings.js (wall-section-graphics.js:6-13); views-model.js imports
    model-ops.js, model-write.js, ifc-util.js (views-model.js:45-50). The import-free files are annoscale.js,
    keynotes.js, model-rooms.js and title-svg.js (counted by grep of import lines); all are small and better
    ported than vendored.

## Proposed build order: a live plan view from small pure functions

All in our ES5 engine, a new folder `src/js/engine/views/plan/` (or files in views/), each with a unit test in
tests/unit/. Plan coordinates [x, z] in metres, as our records are. Names follow the bim prefix.

1. `bimPlanViewDefaults()` returns { cut, top, bottom, depth, detail, scale, crop, hiddenCats, hiddenIds }, with the
   cut at 1.2 m and depth 0.05 m (from views-model.js:53, converted). Effort S.
2. `bimEffectiveViewRange(view, templates, levelHeight)` returns the merged range; `bimCheckViewRange(r, levelHeight)`
   returns an error string or null (port views-model.js:114-129). Effort S.
3. `bimTriCutY(A, B, C, h)` returns [x1, z1, x2, z2] or null, ends ordered by position so neighbours match (port
   model-plan.js:84-99). Effort S.
4. `bimMeshCutSegments(mesh, pos, h)` returns a flat segment array for one solid (fan-triangulates faces as
   bimClipMeshToPlane does, views/section-tool.js:115-118). Effort S.
5. `bimMeshYRange(mesh, pos)` returns [ymin, ymax]; `bimPlanClass(yr, levelElev, range)` returns 'cut', 'below',
   'above' or 'out' (port the tests at model-plan.js:59, 61). Effort S.
6. `bimMeshPlanEdges(mesh, pos, creaseDeg)` returns projected crease and boundary edges with end-on edges dropped
   (port res-views.js:217-241 and model-plan.js:73-75). Effort S.
7. `bimChainSegLoops(segs, tol)` returns closed loops (port model-plan.js:101-133, or wrap bimChainEdgesToLoops).
   Effort S.
8. `bimWallPlanPieces(wall, openings, cutH)` returns wall polygons with only the openings the cut passes through
   removed, per centerline segment (port model-plan.js:135-173 with clipX). Effort M.
9. `bimOpeningPlanSymbol(opening, segA, segB, thickness)` returns { lines, arcs, thin, dashed, poly }; door single,
   double, slide; window frame and glass (port model-openings.js:492-567 subset). Needs `bimOpeningHandFace(o)`
   defaults for the two new fields. Effort M.
10. `bimPlanScene(levelId, view)` returns { walls, symbols, cut, below, above, rooms, tags, dims, crop, scale },
    calling 1 to 9: records for walls and openings, mesh cut for other solids, hidden categories and ids applied
    first (pattern of mui-data.js:113-163). Cached by a key of level, range and model revision, as mui-data.js:94
    does. Effort M.
11. `bimPlanSceneSVG(scene, project, mmPerM)` returns SVG for a sheet viewport with three line classes and cut fills
    through our pattern registry (pattern of res-sheets.js:93-103); then `bimBuildPlanViewportSVG` uses it.
    Effort M.
12. `bimAnnoModelHeight(kind, ratio, standard)` and `bimAnnoFontPt(kind, standard)` (port annoscale.js:62-78).
    Effort S.
13. Screen: draw the same scene on a 2D canvas over the WebGL plan when the active view is a plan (the interface
    step; one browser check under Rule #1's table when the phase closes). Effort M.

After this: door and window tags (M), a section-line record and `bimProjectView(tris, dir, cut, far, res)` for
vector elevations and sections (port res-views.js:74-264, L), view templates in the Project Browser (S), keynotes
(S), wall layer assemblies and detail levels (L, a data-model change that needs its own research).

## Open questions for the owner (asked together)

- D1: the live plan as a 2D canvas over the model view (BimCraft's approach, model-planview.js:4-8), or as SVG only
  on sheets first.
- D2: where plan view settings live: on each level, or as plan-view records that a level can have several of.
- D3: door hand and face: add both fields now (needed for swings), with which default.
- D4: wall layer assemblies (needed for medium and fine detail): in scope for this track or not.

## Sources

| Source | What was read | Date | Level |
|---|---|---|---|
| BimCraft app/model-plan.js | whole file (228 lines) | 2026-11-28 | P |
| BimCraft app/views-model.js | 1-60, 110-130, export list | 2026-11-28 | P |
| BimCraft app/wall-plan-graphics.js | 1-25, 60-200 | 2026-11-28 | P |
| BimCraft app/model-openings.js | 1-44, 485-576 | 2026-11-28 | P |
| BimCraft app/res-views.js | 1-27, 60-165, 217-241, function list | 2026-11-28 | P |
| BimCraft app/mui-data.js | 1-20, 80-200 | 2026-11-28 | P |
| BimCraft app/model-planview.js | 1-43, 286-300, 355-372 | 2026-11-28 | P |
| BimCraft app/res-sheets.js | 1-60, 77-103, 164-180, 426-445, export list | 2026-11-28 | P |
| BimCraft app/pens.js, comforts-views.js, keynotes.js, annoscale.js, anno-scale-bim.js, autodim.js, tags.js, title-block.js, drafting.js, plan-symbols.js, family-symbol.js, wall-dimensions.js, wall-section-graphics.js, model-rooms.js, projected-views.js, view-copies.js | headers and export lists; cutFaceItems 166-173 | 2026-11-28 | P |
| BimCraft app/ifc-vis.js runEdges | signature only (134) | 2026-11-28 | S |
| BimCraft tests/tools/bimcraft-test/*.mjs | which file names each function (grep): model-test (planCut, chainLoops, wallPieces, openingSymbol, planLoops), draw06-test and views2-test (effectiveView), res-test and comforts-test (projectView), pens-test (penFor), r47-test (planAutoDimensions) | 2026-11-28 | P (names), tests not run |
| Ours: drawing/plan-mode-sketch.js 400-460; views/section-tool.js 1-62, 96-227; views/saved-views.js 120-192, 262-290; sheets/viewports.js 541-766; io/dxf-export.js 15-108; bim/type-instance-params.js 280-300, 460-500; bim/room-tags.js 1-45; bim/columns-openings.js 408-430; annotation/annotation-pick.js 25-37; render/webgl.js 33-37 | ranges read | 2026-11-28 | P |
| Revit view range, detail levels, view templates, object styles | not read | - | U (checklist only) |

Still open: Revit's own definitions (U) if the owner wants Revit parity checked term by term; BimCraft's
ifc-vis.js runEdges body; BimCraft's canvas drawing of door tags in plan (searched, not found); measured cost of a
mesh plan cut on a large model here (an experiment for the phase's research).
