# That Open gap study: engine_components, packages/core

Research, 2026-11-28. Pinned source: `ThatOpen/engine_components` at commit `6bedaa4a593d37092d5eb4e04992d09d3e98320d`
(2026-11-23), package `@thatopen/components` 3.6.0 (`packages/core/package.json`). Types it calls into were read in
`ThatOpen/engine_fragment` at `643d24e`. Paths below are relative to `packages/core/src/` unless they start with `src/js/`
(this app). Levels as in `../research-protocol.md`: P read in the primary source (cited file:line), S a dependable
secondary source with the gap said, U a pointer only. No U fact is used in a recommendation; where a recommendation
needs one, the U fact is listed as open work. The clone was read as text; no code from it was run.

## 1. Summary

- That Open's core is a viewer-and-coordination toolkit built on its own fragments model: nearly every component
  (Classifier, Hider, ItemsFinder, BoundingBoxer, EdgeProjector, IDSSpecifications, Views by storey, Viewpoints'
  selection and visibility) reads or writes a `FragmentsModel` through the fragments worker (P: e.g.
  `fragments/Hider/index.ts:31-55`, `fragments/ItemsFinder/index.ts:59-105`). So "reuse" (R) means the on-demand Review
  view of V206 (WO-08, not built yet: `docs/work-orders/v206/TASKS.md:91`), and anything the editable model needs is a
  port (P) onto `A3D.objs`.
- The app is already at least as good in drafting and drawing output (dimensions, sheets, layouts, DXF/DWG, Make2D,
  OpenCASCADE hidden lines), in clipping with caps, snapping, shadows, grids, point clouds (LAS/PLY) and splats.
- The real gaps are openBIM exchange and model query: **BCF** (no BCF at all in `src/`), **IDS** (no checker), a
  **query/finder** over properties, **dynamic classification groups**, **per-element hide/isolate**, **viewpoints
  with element state**, **multiple clipping planes**, a **view range (far plane)**, **orthographic 3D**, and **E57**.
- That Open's own IDS is incomplete at this commit: the Classification and PartOf facets are stubs (P:
  `openbim/IDSSpecifications/src/facets/Classification.ts:38-125`, `PartOf.ts`), several XML writers emit malformed
  XML, applicability facets are united rather than combined, and the length restriction lets max overwrite min. Its
  BCF imports clipping planes but never writes them to a `.bcfv`. So for IDS and BCF, reuse alone does not close the
  gap; the recommendation is a port of the parts that work plus our own facets.
- CHANGELOG: the root `CHANGELOG.md` stops at 3.4.0 (2026-04-09) while the package is 3.6.0, and the clone has a
  single commit, so changes from 3.4.0 to 3.6.0 cannot be read here (P: `CHANGELOG.md:3`, `packages/core/package.json:4`).
  3.3.0 added the fast model picker and face mode; 3.4.0 added IFC loader options for all attributes and relations,
  clipping-plane autoscale, angle measure and optional classic workers (P: `CHANGELOG.md:7-19, 58-75`). No "Cullers"
  component exists at this commit (P: no folder under `core/`; only EdgeProjector's visibility culler and
  ShadowedScene's distance renderer mention culling).

## 2. The table

Gap: NONE (we have it, at least as good), PARTIAL, MISSING. Close by: R (reuse in Review through an adapter), P (port
into our ES5 engine), X (not worth it). Effort S/M/L. Level is that of the row's facts about That Open.

| Component | What it does (our words) | Source (file:lines) | Our equivalent (file) | Gap | Close by | Effort | Level |
|---|---|---|---|---|---|---|---|
| Components, ConfigManager, Disposer, Types | The registry every component hangs off, settings UI data, disposal helpers, the `World`/`Event`/`DataMap` types | `core/Components/index.ts:16-203`, `core/ConfigManager/`, `core/Disposer/index.ts`, `core/Types/` | `src/js/engine/core/state.js` (A3D), our own patterns | NONE (framework) | R only as the Review view's host | S (part of WO-08) | P |
| Worlds (SimpleWorld, SimpleScene, SimpleRenderer, SimpleCamera) | A scene, camera and renderer bundle updated each frame; optional dynamic orbit anchor on pointer down; renderer draws That Open's wordmark overlay by default | `core/Worlds/index.ts:45-109`, `src/simple-world.ts:65-80, 261-300`, `src/simple-renderer.ts:85-140, 434` | `src/js/engine/render/rendered-view.js`, `render/webgl.js` | NONE | R in Review (a world on the app's three) | S | P |
| Grids | A shader-drawn infinite ground grid with two spacings and fade, also in WebGPU | `core/Grids/index.ts:14-40`, `src/simple-grid.ts:91-230` | 2D grid overlay in `src/js/engine/map/terrain-3d.js:374-376`, structural grids `bim/grid-editing.js` | NONE | X | - | P |
| Raycasters | Ray picking: GPU pick first for fragments, optional snap refinement, then a three.js ray on extra meshes | `core/Raycasters/src/simple-raycaster.ts:55-209` | `src/js/engine/render/gpu-pick.js`, CPU picks in editing/ | NONE | R in Review only | S | P |
| FastModelPicker | One render to several targets: element id, depth and normal of the pixel under the cursor, decoded synchronously | `core/FastModelPicker/src/fast-model-picker.ts:1-60` (types), whole file 1438 lines | `src/js/engine/render/gpu-pick.js:32-87` (id only) | PARTIAL: no depth/normal readback; our CPU paths give the point | X (CPU path is enough at our sizes) | - | P |
| SnapResolver | Snaps a picked point to the item's nearest vertex, edge or face, in CAD priority point > line > face, with a per-item geometry cache | `core/SnapResolver/src/snap-resolver.ts:10-15, 158-240, 351-470` | object snaps in `src/js/engine/ui/shortcuts.js:311, 395`, drawing/ | NONE | R in Review only (measuring on IFC) | S | P |
| OrthoPerspectiveCamera | Camera with perspective/orthographic switch and orbit, first-person and plan navigation modes; `fit()` to meshes | `core/OrthoPerspectiveCamera/index.ts:114-200`, `src/projections.ts:48-75`, `src/plan-mode.ts`, `src/first-person-mode.ts` | Plan and elevations are orthographic, 3D is perspective only (`src/js/engine/io/import-entry.js:103-110` uses ortho only when `A3D.flat`); walk modes in `src/js/engine/walk/` | PARTIAL: no orthographic 3D (axonometric) view | P | M | P |
| Clipper (SimplePlane) | Any number of clipping planes, made by picking a face (normal from the hit, optional snap to horizontal) or from normal and point; each has drag controls, autoscale, enable/visible; events before/after create, drag, delete | `core/Clipper/index.ts:361-447` (create, delete, deleteAll), `469-536` (from a hit), `538-561` (apply to materials); `src/simple-plane.ts:1-80` (TransformControls) | `src/js/engine/views/section-tool.js:33-227`: one plane, capped watertight, flip, exit; saved with a view | PARTIAL: one plane only, no plane placed on a picked face, no drag handle, no section box | P | M | P |
| Views (View) | A 2D view is a near plane plus a far plane (range) and its own camera; made from a plane, from every IFC storey (elevation plus offset), or as four elevations around a model box; one open per world, the previous camera restored on close | `core/Views/index.ts:91-312` (create, from plane, from storeys 129-198, elevations 200-311), `312-457` (open, close); `src/view.ts:9-214` | `src/js/engine/views/saved-views.js:120-190` (plans by level, elevation presets), `section-tool.js` | PARTIAL: no view depth (far clip), elevations are fixed presets, not fitted to the model box | P | S | P |
| Viewpoints (Viewpoint) | A BCF viewpoint: camera (perspective or orthogonal), selected, visible-exception and coloured elements by IFC GUID, clipping planes, view setup hints, a snapshot; `go()` applies camera, clipping and visibility; `serialize()` writes `.bcfv` | `core/Viewpoints/index.ts:49-116`; `src/viewpoint.ts:96-116, 241-352, 353-433, 434-535, 553-640, 686-760, 765-840`; `src/types.ts` | `src/js/engine/views/saved-views.js:24-75` (camera, flat, level filter, section) | PARTIAL: no element selection, visibility exceptions, colouring or snapshot in a saved view | P | M | P |
| ShadowedScene | A scene whose directional lights cast shadows, auto bias, one shadow cascade (several cascades a TODO) | `core/ShadowedScene/index.ts:20-24, 148-335` | `src/js/engine/render/rendered-view.js`, site shadows in `site/` | NONE | X | - | P |
| FragmentsManager | Loads, lists and disposes fragments models through a worker; ray cast, positions, boxes, highlight, item data, GUID to local id and back, base coordinate system | `fragments/FragmentsManager/index.ts:50-373` (guidsToModelIdMap 278, modelIdMapToGuids 296) | `A3D.objs`; GUID helpers in `src/js/engine/io/ifc-review.js` (V206 WO-02 to WO-04) | NONE for the editable model; it is the Review view's engine | R (WO-08) | M | P |
| IfcLoader | IFC bytes to a fragments model through fragments' `IfcImporter` (web-ifc); also opens a raw web-ifc model; by default looks up the wasm on unpkg | `fragments/IfcLoader/index.ts:82-196, 197-219, 230-251`; `src/ifc-fragment-settings.ts:6, 28` | `src/js/engine/io/ifc-full.js` (cc-ifc), `import-ifc.js` (fallback) | NONE (V206 WO-09 already plans the switch) | R with `autoSetWasm: false` | M (in V206) | P |
| Classifier | Named classifications of named groups of items: by model, by IFC class, by storey, or by any callback over item data or a relation; a group can be a stored set or a live finder query; `find()` unites groups inside a classification and intersects across classifications | `fragments/Classifier/index.ts:54-152, 154-200, 201-260, 261-328, 371-388`; `src/types.ts` | `src/js/engine/bim/classification.js` (a code registry, Phase 47), layers per IFC class at import (`io/ifc-full.js:24`), `layers/list-by.js` | PARTIAL: no dynamic grouping, no intersection across groupings, no grouping by any property | P | M | P |
| Hider | Hide or show items, isolate a set, toggle, and list what is visible or hidden, per model | `fragments/Hider/index.ts:31-114` | Layer isolate only: `src/js/engine/layers/layer-commands.js:88-95` (LAYISO/LAYUNISO) | MISSING per element | P | S | P |
| ItemsFinder (FinderQuery) | Queries by class regex, attribute name regex and value (regex, number, boolean, or presence), negate, by relation with a nested query; several queries joined or intersected; saved queries with cache, JSON import and export | `fragments/ItemsFinder/index.ts:59-175`; `src/finder-query.ts:63-218`; `src/types.ts`; query type in fragments `model-types.ts:737-766` | none (selection is by pick, marquee or layer: `src/js/engine/layers/select-change.js:19-100`) | MISSING | P | M | P |
| BoundingBoxer | The box of items or models, its centre, and a camera position for front/back/left/right/top/bottom | `fragments/BoundingBoxer/index.ts:44-156` | `src/js/engine/ui/chrome-framing.js:102-171` (Zoom to Selection), `ui/tool-palette.js:456` (fitScene) | NONE | X | - | P |
| EdgeProjector | Visible and hidden edge lines of items along a direction, with BVH acceleration, a GPU visibility pre-cull and each line tagged with its item; built on a vendored three-edge-projection | `fragments/EdgeProjector/index.ts:1-100, 102-270`; `fragments/EdgeProjector/projection/` | `src/js/engine/drawing/make2d.js` (V189, CPU), `src/js/engine/solids/occt-views.js` (OpenCASCADE exact HLR) | PARTIAL: ours is slower on large meshes and does not tag hidden lines by element (not measured here) | R in Review for IFC drawings; keep ours for the editable model | M | P (ours: S, not timed) |
| TechnicalDrawings | 2D drawings in 3D: projection lines from items, layers, viewports at a scale, and annotation systems (linear, angle, leader, slope, callout, block) with state machines and handle picking | `drawings/TechnicalDrawings/index.ts:1-125`; `src/TechnicalDrawing.ts:144-431`; `src/DrawingViewport.ts`; `src/*Annotations/` | `src/js/engine/annotation/` (dimensions, angular, leaders), `sheets/` (sheets, layouts, viewports), slope arrows on terrain `terrain/grading.js:374` | NONE (ours is richer) | X | - | P |
| DxfManager (DxfExporter) | Writes TechnicalDrawings to DXF R2000 (or 2004 with true colour): layers, lines, text, dimensions as lines, blocks, paper borders and viewports; colours mapped to 7 ACI colours | `drawings/DxfManager/src/DxfExporter.ts:31-52, 180-330` (header `318`), `239` (export) | `src/js/engine/io/dxf-export.js` (plan footprints), `io/dwg-io.js` (cc-dwg, AC1027) | PARTIAL: we do not write a sheet with its viewports and annotations to DXF/DWG paper space | P (port the paper-slot transform) | M | P |
| MeasurementUtils | Point-to-line distance, rounding, item volume through the worker, unit conversion m/cm/mm/km for length, area, volume | `measurement/MeasurementUtils/index.ts:49-70, 283-316, 394-432` | `src/js/engine/annotation/inquiry.js`, `inquiry-more.js` (MASSPROP), `bim/type-instance-params.js:435` (volume) | NONE | X | - | P |
| VertexPicker, ModelIdMapUtils, XML, UUID (utils) | Vertex preview picker; union, intersection, difference of item sets; XML parser and escaper; UUIDs | `utils/vertex-picker.ts:36-277`, `utils/model-id-map.ts:6-203` | snaps; sets as id arrays | NONE | P the set algebra with ItemsFinder (`model-id-map.ts:12-60`) | S | P |
| BCFTopics (Topic, Comment) | Issues (topics) with type, status, priority, stage, assignee, labels, comments, viewpoints, related topics and document references; extensions; import and export of `.bcfzip` in BCF 2.1 and 3.0 | `openbim/BCFTopics/index.ts:45-110, 142-287, 288-433, 494-900`; `src/Topic.ts:57-470`; `src/Comment.ts`; `src/bcf-topics-config.ts` | none (grep finds no BCF in `src/`) | MISSING | P (topics, XML and zip in ES5, the reader and writer following the TS) and R for viewpoints applied on IFC in Review | L | P |
| IDSSpecifications (Specification, facets) | Reads and writes IDS XML; specifications with applicability and requirements; Entity, Attribute, Property, Material facets test items; Classification and PartOf facets are parsed but do not test | `openbim/IDSSpecifications/index.ts:64-264`; `src/Specification.ts:56-114`; `src/facets/Facet.ts:39-105`; `src/facets/*.ts`; `src/importers/`, `src/exporters/parameter.ts` | none | MISSING | P (our own checker, ported from the working facets, with Classification and PartOf written from IDS 1.0's documents) | L | P |
| realityCapture (LAS, E57, Potree, splat octrees) | Environment-free readers and builders: LAS stream (no LAZ), E57 paged reader (XYZ and RGB of one points section), Potree 2.0 octree build and tile merge, gaussian splat PLY to an LOD tree | `realityCapture/index.ts:1-33`, `e57.ts:1-198` (openE57 `78`, e57Packets `156`), `las.ts:20, 57-153`, `potree-*.ts`, `convert-splat-fq.ts:247-262` | `src/js/engine/map/pointcloud.js` (LAS 1.2-1.4, PLY, budget sampling), `render/splats.js` (.splat) | PARTIAL: no E57, no octree streaming for clouds over the budget | P (E57 reader) | M | P |

## 3. Notes per component with a gap

### OrthoPerspectiveCamera: orthographic 3D

That Open switches projection on one camera (P: `core/OrthoPerspectiveCamera/src/projections.ts:48-75`). Ours draws
orthographic only for flat views (P: `src/js/engine/io/import-entry.js:108-110`). A BCF viewpoint may carry an
`OrthogonalCamera` with `ViewToWorldScale` (P: read at `openbim/BCFTopics/index.ts:655-700`, written at `core/Viewpoints/src/viewpoint.ts:803-809`), so BCF import needs an
orthographic 3D view. Port: let `toScreen` and the WebGL projection take an ortho flag for a 3D camera, the scale
from `ViewToWorldScale` as the view height. The TS is a three.js camera swap, so there is no line-by-line port; the
work is in our projection code. Effort M (projection touches picking and the overlay).

### Clipper: several planes, placed on a face, dragged

The TS to follow:
- placement from a hit: `core/Clipper/index.ts:469-489` (point and face normal of the hit), `491-504` (normal into
  world space, through the instance matrix when instanced), `506-519` (snap to exactly up or down when the normal's
  vertical part passes 0.7, the `orthogonalY` option);
- the list and events: `361-430`, `521-536`;
- one plane at a time is applied as a per-material clipping list (`538-561`), which our caps would replace.

Port into `src/js/engine/views/section-tool.js`: turn `A3D.section` into a list (keep the first as today's section),
run `bimClipMeshToPlane` once per plane in order, cap each, and add "Section from face" that takes the picked
triangle's normal. A section box is six planes from a box, which is the same list. Effort M. Saved views
(`saved-views.js:31`) then store the list.

### Views: view depth

The TS: a view's `range` sets a far plane parallel to the cut plane (P: `core/Views/src/view.ts:71-90, 135-146,
187-214`); storey views cut at storey elevation plus 0.25 m by default (P: `core/Views/index.ts:133, 173-178`);
elevations fit planes to the model box faces and set range to the box depth (P: `core/Views/index.ts:254-311`). Port:
a `depth` on our section and elevation views that hides triangles beyond `p + depth * dir`, using the same clip as
the near plane with the normal reversed. Effort S.

### Viewpoints: element state in a saved view

That Open's viewpoint keeps a selection set, a default visibility with exceptions, colour groups (colour to GUIDs),
clipping planes and three view setup hints (P: `core/Viewpoints/src/viewpoint.ts:32-36, 96-116, 686-760`), and
`go()` applies camera, clipping and visibility (P: `353-433`, `553-640`). Its export converts Y-up to BCF Z-up as
(x, -z, y) and derives the up vector by turning the direction 90 degrees about X (P: `765-800`), which does not give a
camera's real up vector; the code admits it (P: `viewpoint.ts:776` comment, `BCFTopics/index.ts:677` TODO). Port
into `saved-views.js:24-33`: add `sel` (ids), `vis` ({def, exc}), `col` ([{c, ids}]) and `planes` to
`bimCaptureView`, and a snapshot from the canvas as PNG bytes. Use the camera's real up vector instead of the
90-degree turn. Needs Hider (below). Effort M.

**Found in reading:** `Viewpoint.serialize()` writes no `<ClippingPlanes>` element at all (P:
`core/Viewpoints/src/viewpoint.ts:765-840`), although `toJSON()` and `set()` carry them (P: `686-760`, `311-330`). A
`.bcfzip` exported by That Open loses its section planes. Our port must write them.

### Classifier: dynamic groups

The TS to follow: groups held as `{map, query?}` and resolved lazily (P: `fragments/Classifier/index.ts:54-152`);
`aggregateItems` runs a finder query and a callback that registers items under group names (P: `154-200`);
`find()` is union inside a classification and intersection across classifications (P: `227-260`); built-ins by
model, class and storey (P: `295-328, 371-388`). There is no "by system" built-in; a system grouping would be a custom
`aggregateItemRelations` call (P: `261-293`), whose relation name for IfcRelAssignsToGroup in fragments was not read
(U, open). Export and import are commented out (P: `src/types.ts` end, `index.ts:394-435`).

Port: a new `src/js/engine/bim/groupings.js` with `bimGroupBy(key)` (key = 'type', 'level', 'layer', 'ifcType', or a
property set name and property) returning `{groupName: [ids]}`, and `bimGroupFind({grouping: [groups]})` with the same
union-then-intersect rule; a group may hold a finder query (below) instead of ids. Shown in the Project Browser.
Keep `bim/classification.js` as the code registry it is. Effort M.

### Hider: per-element hide and isolate

The TS is four small operations (P: `fragments/Hider/index.ts:31-56` set, `57-70` isolate as hide all then show the
set, `71-88` toggle, `90-113` visibility map). Port: a per-view hidden set `A3D.hideSet` (ids), honoured where layer
visibility is tested (`layers/layer-rules.js:18-40`), with commands HIDEOBJECTS, ISOLATEOBJECTS, UNISOLATEOBJECTS
(AutoCAD's names, as our LAYISO follows AutoCAD) and an undo step each. Saved views and BCF visibility exceptions read
it. Effort S.

### ItemsFinder: queries over the model

The query shape (P: engine_fragment `FragmentsModels/src/model/model-types.ts:737-766`): `categories` (regexes on the
IFC class), `attributes.queries` of `{name: RegExp, value?: RegExp | RegExp[] | number | boolean, type?, negate?}`
with `aggregation` inclusive or exclusive, and `relation {name, query?}` for a nested query on related items. Several
queries are joined or intersected (P: `fragments/ItemsFinder/index.ts:59-105`). Numeric comparisons are not supported
yet (P: `model-types.ts:741`, a comment). Saved queries serialise regexes as strings (P:
`ItemsFinder/src/finder-query.ts:144-218`, `src/types.ts`).

Port: `src/js/engine/editing/find-items.js` with `bimFindItems(queries, aggregation)` over `A3D.objs`, where class is
`o.bim.ifcType || o.bim.type || o.t`, attributes are `o.name`, `o.bim.guid`, level, layer, and `o.bim.psets` values
(property sets are kept at IFC import, P: `src/js/engine/io/ifc-full.js:155-175`); relation 'level' and 'host' first.
Add the numeric bounds That Open lacks (min/max) since IDS needs them. A QSELECT-style dialog and saved queries in the
project file. The set algebra follows `utils/model-id-map.ts:12-60`. Effort M.

### EdgeProjector: fast hidden-line drawings of large models

`EdgeProjector.get(modelIdMap, world, {onProgress, signal})` returns `{visible, hidden, groups}` line geometries in
world space with each group index mapped to `{modelId, localId}` (P: `fragments/EdgeProjector/index.ts:9-16,
102-270`); `projectionDirection` and `cullerMetersPerPixel` are its settings (P: `:49-60`). It depends on the vendored
three-edge-projection and three-mesh-bvh (P: `:1-6`, `projection/`), MIT per the package's dependency list (P:
`packages/core/package.json` dependencies; the vendored folder's licence file was not read, open). Recommendation: R
inside Review for drawings of imported IFC. For the editable model, keep Make2D and OpenCASCADE; timing ours against it
is open (no measurement here). Effort M.

### DxfManager: sheets to DXF paper space

The parts worth porting: the paper-space slot transform from a viewport's screen rectangle (Y down) to DXF paper
millimetres (Y up) (P: `drawings/DxfManager/src/DxfExporter.ts:272-295`), viewport borders and block insertions, and
the R2000 header and tables writer (P: `:56-140`, `:318`). Its colour mapping to only 7 ACI colours (P: `:31-52`) is
coarser than ours (`layers/select-change.js` keeps AutoCAD colours and lineweights), so do not take that. Port into
`src/js/engine/io/dxf-export.js` as "Export sheet to DXF", reusing our sheet and viewport model in `sheets/viewports.js`.
Effort M.

### BCFTopics: BCF 2.1 and 3.0

What it does (P unless marked):
- Versions 2.1 and 3.0 on export and import; `VersionId` written as "3.0" for 3 and read as either (P:
  `openbim/BCFTopics/index.ts:288-300, 505-520`); unsupported versions throw (P: `:518-519`).
- Archive: `bcf.version`, one folder per topic with `markup.bcf`, `.bcfv` viewpoints and snapshots, `extensions.xml`
  at the root (legacy `bcf.extensions` accepted on read), `documents.xml` and `documents/` for 3.0 (P: `:296-433,
  522-530, 539-560, 722-860`).
- Topic fields: guid, type, status, priority, stage, assignee, labels, title, description, dates, authors, due date,
  comments (text, author, date, viewpoint), related topics, document references (P: `src/Topic.ts:57-470`,
  `index.ts:434-490`).
- Extensions: allowed types, statuses, priorities, labels, stages, users, a strict mode (P:
  `src/bcf-topics-config.ts:9-24`, `index.ts:249-287`).
- Viewpoint components read: selection, visibility with exceptions, view setup hints in either version's place,
  coloring, perspective and orthogonal cameras, clipping planes (P: `index.ts:560-700`).
- Not supported: viewpoint `Lines` and `Bitmaps` (P: no match in `index.ts` or `viewpoint.ts`), the 2.1 markup
  `Header`/`Files` (the IFC files a topic refers to; no match for `Header`), clipping planes on export (above), and the
  BCF REST API (not in core). A document `Description` is written without XML escaping (P: `index.ts:319`).
- Dependencies: jszip 3.10.1 and fast-xml-parser 5.7.2 (P: `packages/core/package.json` dependencies); viewpoints need
  FragmentsManager for GUIDs and the base coordinate matrix (P: `viewpoint.ts:765-770`).

Recommendation (P): our own `src/js/engine/io/bcf.js`, ES5, following the reader at `index.ts:494-860` and the writer at
`288-433` for file layout and version differences, with topics kept in the project file and an Issues panel. It needs
a zip reader and writer. The app has none today: `src/js/engine/io/file-save.js:140-171` uses the browser's
`CompressionStream('gzip')`, not zip (P). A store-only zip writer is S; reading deflated entries can use
`DecompressionStream('deflate-raw')` where the browser has it (S: browser support not tested here), else jszip
(MIT, That Open's own dependency) under the library rule. Element references are IFC GUIDs, which our
imported objects keep (`io/ifc-full.js:116, 220`) and V177 writes. Write Lines and clipping planes, which That Open
does not. In Review (R), a BCF viewpoint applied to an IFC model is `Viewpoints.create(data)` then `viewpoint.go()`
with `world` set (P: `core/Viewpoints/index.ts:49-55`, `viewpoint.ts:353-433`). Effort L.

### IDSSpecifications: IDS 1.0

What it does (P):
- Load: parses `<ids>` XML, its info block, each specification's `ifcVersion` (IFC2X3, IFC4, IFC4X3_ADD2), name,
  identifier, and the six facet kinds in applicability and requirements (P: `openbim/IDSSpecifications/index.ts:110-237`,
  `src/types.ts` IfcVersion and IDSFacetType).
- Restrictions read: simple value, enumeration (typed by base), pattern, bounds (min/max inclusive or exclusive),
  length (length, minLength, maxLength) (P: `src/importers/parameter.ts:1-97`). Only one kind per restriction is kept;
  a restriction with both a pattern and a length keeps the last one read (P: same file, each kind overwrites
  `result.type`).
- Test: applicability facets collect items, then each requirement tests them (P: `src/Specification.ts:56-80`).
  Facets that test: Entity (class regex or value, predefined type) (P: `src/facets/Entity.ts:42-105`), Attribute,
  Property (property set, base name, value, data type, values from the type object too) (P: `src/facets/Property.ts:60,
  283-400, 578-600`), Material (P: `src/facets/Material.ts:71-130`). Classification: `getEntities` and `test` are
  commented out (P: `src/facets/Classification.ts:38-125`, 247 comment lines). PartOf: `getEntities` and `test` are
  empty and `serialize()` returns "" (P: `src/facets/PartOf.ts`).
- Results: per item, per facet, per check with the current and required value (P: `src/types.ts` IDSCheck to
  IDSCheckResult), and `getModelIdMap(result)` gives passing and failing sets (P: `index.ts:64-88`).

Faults found in reading (P), each to avoid in a port:
1. Applicability facets all add into one collector (P: `src/Specification.ts:64-68`; `Entity.ts:84, 100` use
   `ModelIdMapUtils.add`/`append`), so two applicability facets select items matching either. That IDS 1.0 requires all
   applicability facets to match is U here (not re-read); confirm it from buildingSMART's IDS documents before the port.
2. Length restriction: when both min and max are given, the max test overwrites the min result (P:
   `src/facets/Facet.ts:69-80`).
3. Pattern: tested with an unanchored JavaScript RegExp (P: `Facet.ts:64-66`). XSD patterns match the whole value (U
   here; confirm from the XSD 1.1 datatypes spec).
4. Optional cardinality passes always (P: `Facet.ts:89`); how IDS 1.0 defines "optional" for a present but wrong value
   is U, open.
5. Export writes malformed XML: bounds tags are never closed (P: `src/exporters/parameter.ts:32, 37`); `uri` and
   `dataType` attributes are unquoted and run together without spaces (P: `src/facets/Property.ts:44-50`,
   `Classification.ts:26-30`); PartOf exports nothing; specification `minOccurs` is always 1 (P:
   `Specification.ts:100`).
6. Units: property values are compared without converting to IDS units (P: `Property.ts:518`, a TODO).

Recommendation: P, a checker of our own, `src/js/engine/io/ids-check.js`, ES5, run on `A3D.objs` through the finder
above: the XML reader follows `importers/*.ts`; the test logic follows `Facet.ts:39-105` with faults 2 to 4 fixed and
`Entity.ts`, `Attribute.ts`, `Property.ts`, `Material.ts` for the facet rules; Classification and PartOf written from
IDS 1.0's own documents and its test cases (buildingSMART's IDS repository; not read here, open). Our imported objects
lack materials, classification references and predefined types (P: `src/js/engine/io/ifc-full.js:84-181` keeps
class, GUID, name, storey and property sets only), so the import must keep them first, or IDS checks run on the IFC
in Review. R (That Open's checker in Review) is acceptable only for Entity, Attribute, Property and Material, with the
faults above; it cannot check Classification or PartOf. Effort L.

Alternative noted, not recommended here: IfcOpenShell's `ifctester` runs IDS in Python, but the app's pinned wheel set
(`runtime/ifcos/0.8.5/`) does not contain it (P: listed the seven wheels; none holds `ifctester`); its licence and size
are U, open.

### realityCapture: E57

`openE57(source)` takes an injected `readBytes(offset, length)` and reads the paged container (the content bytes of
each page, its 4-byte CRC stripped), the XML section and one CompressedVector of XYZ plus optional RGB;
`e57Packets(file)` yields packets (P: `realityCapture/e57.ts:1-30, 78-198`). LAS reading there rejects LAZ like ours (P:
`las.ts:20, 147-153`). Port the E57 reader into `src/js/engine/map/pointcloud.js` beside LAS and PLY, with `File.slice`
as the byte source. The page size comes from the file (P: `e57.ts:10-13`). Potree octree streaming (`potree-*.ts`) is a larger question (L) and belongs
with the LAZ/COPC library question already open in V190. Effort M for E57.

## 4. Things the Review view adapter must do (from the reading)

- Set `IfcLoader.setup({autoSetWasm: false, wasm: {path, absolute}})`: the default is true and fetches
  `https://unpkg.com/@thatopen/components@<release>/package.json` (P: `fragments/IfcLoader/index.ts:84-86, 230-251`,
  `src/ifc-fragment-settings.ts:28`). In this source `Components.release` is "2.4.3" (P:
  `core/Components/index.ts:20`) against package 3.6.0; the publish script is said to rewrite it (S:
  `package.json` `prepublishOnly` runs `resources/updateComponentsVersion.mjs`, not read).
- FragmentsManager's documented worker path is unpkg (P: `fragments/FragmentsManager/index.ts:11`); use the inline or
  classic worker as research-thatopen.md F2 and F3 found.
- The renderer draws That Open's wordmark by default (P: `core/Worlds/src/simple-renderer.ts:85-112, 434`); it is
  inline SVG, no network (P: `core/Worlds/src/logo.ts:33-37`). Keeping it on also serves the credit the library rule
  asks for; the owner decides.

## 5. What is still open

- 3.4.0 to 3.6.0 changes: not in the CHANGELOG at this commit; read npm release notes or the tags (U until read).
- IDS 1.0 semantics for applicability (all facets), pattern anchoring, optional cardinality, units: read buildingSMART's
  IDS documentation and run its test cases.
- BCF 3.0 schema details for Lines, Bitmaps and clipping planes: read buildingSMART's BCF-XML release_3_0 schemas.
- The relation name fragments uses for IfcRelAssignsToGroup (for a system grouping).
- Whether `DecompressionStream('deflate-raw')` is available in every browser the app supports.
- Timing Make2D against EdgeProjector on the same model.
- The vendored three-edge-projection licence file inside `fragments/EdgeProjector/projection/`.

## 6. Independent check

Not yet done: a second reader should re-check every P row in section 2 and each fault listed under IDS and BCF against
the pinned files before any of it reaches a spec.
