# That Open gap: components-front and ui-components against the app

Research, 2026-11-28. Part of the That Open gap study (the owner: close every gap between this app and That Open
Engine). Levels as in `docs/research/research-protocol.md`: P primary (read in the source, file:line), S secondary,
U a pointer only. U facts are kept out of the recommendations.

Pinned clones read (read-only, no code run from them):

| Repository | Commit | Package version (package.json) |
|---|---|---|
| ThatOpen/engine_components | 6bedaa4 | `@thatopen/components-front` 3.6.1 (packages/front/package.json:4) |
| ThatOpen/engine_ui-components | cd91b3f | `@thatopen/ui` 3.4.33 (packages/core/package.json:4), `@thatopen/ui-obc` 3.4.5 (packages/obc/package.json:4) |

The app was read at the working copy of 2026-11-28 (`src/`). Paths below are relative to
`engine_components/packages/front/src/` (written `front/`), `engine_ui-components/packages/` (written `ui/`) and
`src/js/engine/` (written `engine/`), unless given in full.

## 1. Summary

- That Open's front package is a **viewer toolkit around fragments models**: named highlight styles with
  priorities, a GPU-picked hover, per-group outlines, 3D measuring (length, area, angle, volume) with snapping to
  vertices, edges and faces, styled section cuts, clustered 3D markers, a post-processing renderer (pen and colour
  styles, AO, outlines, gloss), streamed point clouds (Potree 2.0, through potree-core) and Gaussian splats (its own
  WebGL2 renderer), civil alignment navigators, and a drawing-annotation editor. (P, the files in the table.)
- The app already matches or exceeds it on **2D drafting** (linear, aligned, angular, radius, diameter, leader,
  baseline and continued dimensions; inquiry and MASSPROP), **sections with capped cuts**, **alignments authored with
  stations and profiles**, **local LAS/PLY point clouds**, **sheets and layouts**, a **view cube**, a **project
  browser**, **IFC property sets in Properties**, and **schedules**. (P, `engine/` files in the table.)
- The **biggest gaps**: (1) no hover pre-highlight and no named highlight styles beyond two selection tints; (2) no
  outline of selected or grouped items; (3) no measuring in 3D on model surfaces (the app's DIST, AREA and
  dimensions work on the active level's plane), and no face-area or element-volume pick tool; (4) no clustered 3D
  markers; (5) no live screen-space AO or pen-with-shadows style in the shaded view; (6) no spatial tree
  (Site > Building > Storey > class > element) for imported IFC; (7) no BCF topics, viewpoints or comments, and no
  IDS result chart; (8) no octree or streamed point clouds (LAZ, COPC, Potree), and **no drawing of Gaussian splats
  at all**: V205's WO-06 is ticked in `docs/work-orders/v205/TASKS.md:71`, but `grep -rni splat src/` finds only the
  pure functions in `engine/render/splats.js`, a comment in `engine/site/drone-plan.js:4` and the include line in
  `src/index.html:208` (P); (9) no cross-section navigator along an alignment, and no IfcAlignment import.
- That Open's UI-OBC panels are **Lit web components** (`ui/obc/package.json:41-44`: `@thatopen/ui` ~3.4.0 and
  `lit` 3.3.1) that read That Open's own objects (`OBC.Components`, `FragmentsModel`, `OBF.Highlighter`). They are
  custom elements registered with `customElements.define` (`ui/core/src/core/Manager/index.ts:106-133`), so they can
  be placed in any DOM, which makes them usable **inside the Review view only**; for the app's editable model they
  must be **re-made in ES5 DOM** because they call fragments-model methods the app's objects do not have (for
  example `model.getSpatialStructure()`, `ui/obc/src/components/tables/SpatialTree/src/template.ts:167`). (P)
- Several items the brief named do **not exist** at these commits: no `Plans` and no `ShadowDropper` in front (no
  such folder or class under `front/`; P, by `find` and `grep`); the storey plans are now `Views.createFromIfcStoreys`
  in the **core** package (`engine_components/packages/core/src/core/Views/index.ts:129`, another agent's area); no
  classifications tree, element-relations tree or views list in ui-obc (relations are rows inside ItemsData,
  `ui/obc/src/components/tables/ItemsData/src/template.ts:139-156`); and **WorldsConfiguration is entirely commented
  out** (`ui/obc/src/components/tables/WorldsConfiguration/index.ts:1-44`, template 1065 lines with 24 not commented;
  its export is commented at `ui/obc/src/components/tables/index.ts:1`). (P)
- Version notes for the Review view: ui-obc 3.4.5 asks for `three` 0.185.0 as a peer (`ui/obc/package.json:68-74`)
  and components-front 3.6.1 for `three` >=0.182.0 (`front/../package.json:35-40`); the app ships 0.186.1. Front's
  WebGPU paths import `three/tsl` dynamically (`front/core/PointCloudLoader/webgpu-points.ts:129`,
  `front/core/SplatLoader/gsplat/webgpu-splats.ts:43`) but the WebGPU composition files import it statically
  (`front/core/PostproductionRenderer/webgpu/composition/composition.mjs:41`), which the lean build of e01 must keep
  stubbed (research-thatopen.md F8). (P)

## 2. The table

Gap: NONE (the app has it), PARTIAL (what is missing is said in section 3), MISSING. Close by: R reuse That Open's
code in the on-demand Review view (V206 WO-08, not yet built) through an adapter; P port the method into the ES5
engine for the editable model; X not worth it. Effort S (a day or two), M (a week), L (more).

| Component | What it does (our words) | Source (file:lines) | Our equivalent (file) | Gap | Close by | Effort | Level |
|---|---|---|---|---|---|---|---|
| Highlighter | Named highlight styles (colour, opacity, keep the element's own material) over sets of items, with a priority so the strongest style shows when two claim an item; click to select (single, or add with Ctrl or Shift), zoom to the selection, events before and after | `front/fragments/Highlighter/index.ts:11-667` (config 60-79, styles and priority 81-92, highlight 214-261, highlightByID 285-378, getStylesByPriority 419-435, zoomSelection 542-587); `src/types.ts:1-57` | Selection tint in `engine/render/gpu-batches.js:114,145` (`sel` and `sel2` only), `selSet` in `engine/render/webgpu.js:173` and `engine/render/rendered-scene.js:24,106`; colour lens `engine/map/colour-lens.js:126`; Zoom to Selection `engine/ui/chrome-framing.js:168-175` | PARTIAL | P (styles with priority) | M | P |
| Hoverer | Pre-highlight of the item under the cursor, picked by the GPU, drawn as proxy meshes sharing the tile's geometry, faded in and out; skipped while the camera is dragged or wheeled; two modes (every frame, or when the cursor stops) | `front/fragments/Hoverer/index.ts:27-30` (modes), `45-647` (hover 292-355, beginUnhover 356, buildProxy 460-498, events 514-620, animate 622-647) | GPU pick of a click `engine/render/gpu-pick.js:33` (`bimPickGpu`); no hover on model elements (only the gizmo's handles, `engine/gizmo/gizmo-handles.js:100`) | MISSING | P | S | P |
| Outliner | Coloured outlines with thickness and an optional fill, in named groups, each bound to a Highlighter style so a selection is outlined automatically | `front/fragments/Outliner/index.ts:63-765` (create 267, configure 280, bindStyle 324, addItems 339, removeItems 348, update 367); pass `front/core/PostproductionRenderer/src/simple-outline-pass.ts:84-1025` | Model edges drawn by the engine (`engine/render/webgl.js:21`, edge pull); selection is a tint, never an outline | MISSING | P (screen-space outline of the selection) | M | P |
| Mesher | Turns fragments items into three.js meshes (per item, optional material, transform applied), cached per model | `front/fragments/Mesher/index.ts:8-174` (get 29-91, remove 107, getMeshesFromResult 128, createMesh 152) | `engine/io/ifc-review.js` `bimTorMesh` (V206 WO-01, Z-up to Y-up) | PARTIAL (the adapter half exists as pure code; the fragments side is in Review) | R (Mesher feeds V206 WO-09) | S | P |
| Measurement (base) | Shared machinery: snapping to point, line and face, preview marker on move or on stop, units and rounding, basic or fat lines, fills, volumes, labels, clipping-plane visibility | `front/measurement/Measurement/index.ts:54-812` (snappings 61-65, pickMode 86, units 431-479, rounding 480-497, lineType 523-560, applyPlanesVisibility 713); units `Measurement/src/types.ts:1-36`, `default-units.ts:1-11`; picker `front/utils/graphic-vertex-picker.ts:132-150` | Running object snaps on the level plane `engine/drawing/plan-mode-sketch.js` (`bimSnapCandidates(y0,...)`, `bimSnapPoint`); unit display `bimFmtLen`, `bimFmtArea` (`engine/annotation/inquiry.js:93`) | PARTIAL (no snap to 3D vertices, edges and faces of meshes) | P | M | P |
| LengthMeasurement | 3D distance between two picked points (free) or the length of a picked mesh edge (edge mode) | `front/measurement/LengthMeasurement/index.ts:1-288` (modes 35, edge key 280-288); `src/types.ts:1-18` | DIST `engine/annotation/inquiry.js:21-25`; linear dimensions `engine/annotation/dimensions.js`, `engine/annotation/dim-tools.js` (V258) | PARTIAL (plan only: no 3D point to point, no edge mode) | P | M | P |
| AreaMeasurement | Area of a picked polygon (free), of a rectangle from two points and a face normal (square), or of a whole picked face (face) | `front/measurement/AreaMeasurement/index.ts:1-325` (modes 36, face 210-223, square 240); `front/utils/area.ts:1-245` | AREA `engine/annotation/inquiry.js:27-30`; MASSPROP `engine/annotation/inquiry-more.js:9-30`; `bimTorArea` `engine/io/ifc-review.js` (V206 WO-06, 3D polygon) | PARTIAL (no face pick, no area on a sloped plane) | P (face mode) | S | P |
| AngleMeasurement | Angle between two rays from a vertex, with an arc and a label, in 3D | `front/measurement/AngleMeasurement/index.ts:1-531` (create 131, arc 474-506); `front/utils/angle.ts:1-81` | Angular dimension `engine/annotation/dimensions.js:16-61` (on the plan) | PARTIAL (plan only) | P | S | P |
| VolumeMeasurement | Volume of picked elements, summed, with a proxy-mesh highlight and the label at their centre | `front/measurement/VolumeMeasurement/index.ts:1-165`; `front/utils/volume.ts:40-55` (calls core `MeasurementUtils.getItemsVolume`, `engine_components/packages/core/src/measurement/MeasurementUtils/index.ts:307-315`); `front/utils/measure-volume.ts:1-239` | `bimObjVolume` `engine/bim/type-instance-params.js:435-440` (closed meshes only), `bimMeshSignedVolume` `engine/bim/section-profiles.js:108`; shown in Properties | PARTIAL (no pick-and-sum tool) | P (a tool over `bimObjVolume`) | S | P |
| ClipStyler | Edges and fills on a clipping plane's cut, with named styles per classifier group (for example concrete walls hatched one way), linked to a view or clipper plane | `front/core/ClipStyler/index.ts:1-168` (create, createFromView, createFromClipping); `src/clip-edges.ts:1-415`; `src/types.ts:1-51` | Section tool with capped loops `engine/views/section-tool.js:15-30,96` (`bimCapLoop`); wall poche in plots `engine/layers/plot-by-layers.js:117-128` | PARTIAL (no cut style per category or material on 3D caps) | P | M | P |
| Marker | Screen-sized HTML labels anchored at 3D points, clustered when closer than a pixel threshold, click a cluster to fly to it | `front/core/Marker/index.ts:1-550` (TODOs 5-8: n-squared clustering; threshold 83, create 172, cluster 312-365, navigateToCluster 503); `src/mark.ts:1-95` | Notes and markers anchored at a level and drawn at pixel size `engine/annotation/annotation-overlay.js:16-30` (V82); no clustering | PARTIAL (no clustering, no free 3D anchor) | P (clustering) | S | P |
| PostproductionRenderer | Renderer with styles colour, pen, pen with shadows and their mixes; AO, edge detection, outlines, gloss, excluded objects, SMAA or MSAA; a deferred pipeline (screen-space and world-space AO, sun shadows, FXAA); a WebGPU composition | `front/core/PostproductionRenderer/index.ts:94-1173`; aspects `src/modes.ts:12-29`; passes `src/index.ts:30-440`, `src/edge-detection-pass.ts:1-391`, `src/gloss-pass.ts:1-245`, `src/ao-pass.ts:1-49`; `deferred/pipeline-v2.ts:1-1117`, `deferred/screen-space-ao-pass.ts:1-277`, `deferred/sun-shadow-pass.ts:1-392` | Shaded view with edges (`engine/render/webgl.js`, `engine/render/webgpu.js`); rendered view, accumulated soft shadows and sky occlusion `engine/render/rendered-core.js:4-18,109-112`; exact hidden lines `engine/solids/occt-views.js:69-71`; 2D plan drawing | PARTIAL (no live AO or pen style in the shaded view; no gloss) | P (pen style and a cheap AO in the shaded view) | L | P |
| PointCloudLoader | Potree 2.0 octree streamed by a point budget with LOD, eye-dome lighting, circle or square points, float64 anchor rebase, pluggable fetch; potree-core as an optional peer | `front/core/PointCloudLoader/index.ts:1-1053` (settings 36-75, load 454-559, rebase 479-510); peer `front/../package.json:35-45`; `webgpu-points.ts:1-333` | LAS 1.2-1.4 and PLY read, sampled to a budget, rebased, drawn as GL points `engine/map/pointcloud.js:3-9`, `engine/map/pointcloud-view.js:23-45` (V190) | PARTIAL (no LAZ, COPC or Potree octree streaming; no EDL) | R for streamed clouds in Review; P for EDL | M | P (potree-core's licence: U, to read before use) |
| SplatLoader | Gaussian splats from PLY, compressed PLY, SOG (WebP textures) and a streamed LOD manifest; its own WebGL2 renderer with a worker sort, cell LOD and culling, depth-tested against the BIM model; placement transform; collision proxy | `front/core/SplatLoader/index.ts:1-698` (load 244, setTransform 359, setCollisionProxy 389); `gsplat/renderer.ts:1-377`, `gsplat/ply.ts:1-227`, `gsplat/sog.ts:1-212`, `gsplat/stream.ts:1-825`, `gsplat/sort-worker-src.ts:1-116` | `.splat` read, bounds, two-pair fit, back-to-front order `engine/render/splats.js:7-115` (pure only); no drawing anywhere in `src/` | MISSING (drawing); PARTIAL (formats) | R (draw in Review); P (PLY reader into `splats.js`) | M | P |
| CivilNavigators | Alignment curves from fragments shown in plan, elevation and 3D; hover and select markers, station labels every N metres, highlight of the picked alignment | `front/civil/CivilNavigators/index.ts:1-154`; `src/index.ts:11-673` (setMarkerAtPoint 212, highlight 223, createStations 246, updateStations 266-455) | Alignment and profile authored, stations, ticks, profile view, tables `engine/site/alignment-profile.js:23-648` (V127) | PARTIAL (no IfcAlignment import to navigate) | R (for imported IFC alignments in Review) | M | P |
| CivilCrossSectionNavigator | A section plane perpendicular to the alignment at the picked station, with cut edges drawn | `front/civil/CivilCrossSectionNavigator/index.ts:1-202`; `front/civil/CivilRaycaster/index.ts:1-102`; `front/civil/Utils/civil-utils.ts:1-205` | Station query `bimStationAt` `engine/site/alignment-profile.js:586`; section tool `engine/views/section-tool.js` | MISSING (cross-section at a station) | P (section tool placed normal to the alignment at a station) | S | P |
| DrawingEditor | Interaction for core's TechnicalDrawing: snapping, tool routing, labels from a font, multi-select and drag; tools linear (single, sequential, by line), angle, block, callout, leader, slope | `front/drawings/DrawingEditor/index.ts:1-592`; tools `src/LinearAnnotationsTool/index.ts:1-486` (modes `src/modes.ts:1-34`), `src/AngleAnnotationsTool/index.ts:1-500`, `src/BlockAnnotationsTool/index.ts:1-500`, `src/CalloutAnnotationsTool/index.ts:1-520`, `src/LeaderAnnotationsTool/index.ts:1-436`, `src/SlopeAnnotationsTool/index.ts:1-520` | Dimensions, baseline and continue `engine/annotation/dim-tools.js:15-63`; angular, radius, diameter, leader `engine/annotation/dimensions.js:16-99`; notes and callouts `engine/annotation/annotation-overlay.js`; blocks in `engine/assets/` | PARTIAL (no slope annotation) | P (slope arrow) | S | P |
| Plans, ShadowDropper | Not present in front at 6bedaa4; storey plans are core's `Views.createFromIfcStoreys` | none in `front/`; `engine_components/packages/core/src/core/Views/index.ts:129` | Floor plans per level, saved views `engine/views/saved-views.js`; shadows `engine/site/shadows.js` | NONE (front); core is another note | X here | - | P |
| ui-obc SpatialTree | A table of each model's spatial structure (project, site, building, storey, then classes, then elements), names fetched in one batch, optional collapse of one-child classes, click a row to select through the Highlighter | `ui/obc/src/components/tables/SpatialTree/index.ts:1-43`; `src/template.ts:1-304` (getSpatialStructure 167, getItemsData 177, row click 241-271); `src/types.ts:1-41` | Site and buildings `engine/bim/building-site-hierarchy.js:10-25`; levels; Project Browser groups `engine/sheets/presentation-panel.js:314-417`; Layers panel by order, source or selection `engine/layers/list-by.js:16-25`; imported elements carry `bim.storey` `engine/io/ifc-full.js:221` | PARTIAL (no tree Site > Building > Storey > class > element) | R in Review; P (ES5 tree over `A3D.buildings`, levels, `bim.ifcType`) for the model | S (R) / M (P) | P |
| ui-obc ItemsData | Property table of selected items: attributes, then chosen relations (property sets by IsDefinedBy, the containing storey) as nested rows | `ui/obc/src/components/tables/ItemsData/src/template.ts:1-206` (relations config 139-156); `src/types.ts:1-39` | IFC group and property sets in Properties `engine/io/ifc-full.js:261-272` (`bimIfcPropsHtml`); palette `engine/properties/palette.js` | PARTIAL (no relation rows, no multi-item table) | R in Review; P (relations) | S | P |
| ui-obc ModelsList | Loaded models with show or hide, download and dispose buttons | `ui/obc/src/components/tables/ModelsList/src/set-defaults.ts:1-106` (dispose 49-52, visibility 59, download 73-84) | External references `engine/io/xref.js:13` (V265); imported IFC as layers | PARTIAL (no one list of federated models) | R in Review | S | P |
| ui-obc WorldsConfiguration | Camera, grid and post-processing settings table | commented out: `ui/obc/src/components/tables/WorldsConfiguration/index.ts:1-44`, `tables/index.ts:1` | View settings in the app's own dialogs | NONE (nothing to take) | X | - | P |
| ui-obc ViewpointsList, TopicsList, CommentsList, Topic sections, TopicForm | BCF: topics with status, priority, assignee, dates; viewpoints (select, colour, camera); comments; links between topics | `ui/obc/src/components/tables/ViewpointsList/src/set-defaults.ts:1-141`; `tables/TopicsList/src/types.ts:1-23`; `tables/CommentsList/src/types.ts:1-20`; `sections/TopicRelations/src/types.ts:1-12`; `ui/obc/src/utils/topics/form-template.ts:1-232` | none (`grep -rli bcf src/` finds only `engine/standards/registry.js`) | MISSING | R in Review (with core's BCFTopics) | M | P |
| ui-obc charts: Categories, Attributes, Topics, Labels | Charts of item counts by class or by an attribute's value, or topics by status; click a slice to select | `ui/obc/src/components/charts/Categories/src/template.ts:1-115` (getItemsOfCategories 74, select 100); `charts/Attributes/src/template.ts:1-133`; `charts/Topics/src/template.ts:1-95` | Schedules `engine/views/schedules.js`; Analyze charts `engine/site-analysis/analysis-workspace.js:408` | PARTIAL (no chart of model contents by class) | P (a counts-by-class chart) | S | P |
| ui-obc chart IDS | Pass and fail chart of an IDS check, by specification | `ui/obc/src/components/charts/IDS/src/template.ts:1-167`; `src/types.ts:1-12` | none (no IDS in `src/`) | MISSING | R in Review (with core's IDSSpecifications) | M | P |
| ui-obc ViewCube, World, World2D, SheetBoard | Lit elements for a view cube, a 3D world viewport, a 2D world with an infinite grid, and a board to arrange drawing sheets with DXF export events | `ui/obc/src/core/ViewCube/index.ts:1-245`; `core/World/index.ts:1-97`; `core/World2D/index.ts:1-162`, `src/Infinite2DGrid.ts:1-256`; `core/SheetBoard/index.ts:1-1082` | View cube `engine/render/viewcube.js` (V37); sheets and layouts `engine/sheets/`; DXF export `engine/io/dxf-export.js` | NONE (ViewCube, 2D, sheets); World is Review's own canvas | R (World element as Review's viewport) | S | P |
| ui-obc buttons load-ifc, load-frag | Buttons that open a file and load it | `ui/obc/src/components/buttons/load-ifc/src/template.ts:1-55`; `load-frag/src/template.ts:1-42` | `bimIfcPick` `engine/io/ifc-full.js:273-279`; import entry `engine/io/import-entry.js` | NONE | X | - | P |

## 3. Notes per gap

### 3.1 Highlighter: named styles with priority (P, M)

What to port: a style table (name, colour, opacity, keep own material) and a selection map per style, resolved by
priority. The rule is in `front/fragments/Highlighter/index.ts:81-92` (the highest priority wins an item; the others
keep it and repaint it when the winner releases it; ties go to the style registered last; the select style is
highest), with the resolution in `getStylesByPriority` and `getPriority` (419-435) and `updateStyleMap` (436-465).
`clear(name)` (466) and `highlightByID(name, map, removePrevious, zoom, exclude)` (285-378) are the API to copy.
In the app, the per-slot selection value is one number (`engine/render/gpu-batches.js:145`, `v[7]` is 0, 1 or 2);
a style index in that texel, with a palette uniform, carries N styles to both engines. The zoom already exists as
`bimZoomToSelection` (`engine/ui/chrome-framing.js:168`), which uses the same bounding-sphere idea as
`zoomSelection` (542-587, sphere radius times `zoomFactor` 1.5, line 46).

### 3.2 Hoverer (P, S)

Port the behaviour, not the code: on pointer move, at most one pick a frame (`HovererMode.MOUSE_MOVE`, 27-30), skip
while dragging or wheeling (`hover` 292-311), tolerate two null picks before clearing (`NULL_PICK_TOLERANCE`, 97),
fade over `fadeDuration` 200 ms (67). The app's `bimPickGpu(x,y)` (`engine/render/gpu-pick.js:33`) already returns
the element under a pixel; the hover is a third value in the same selection texel. That Open draws proxy meshes
sharing tile buffers (460-498) because fragments' tiles are shared; the app's batches are per object slot, so a
uniform tint is simpler.

### 3.3 Outliner (P, M)

That Open writes each group's id colour into a mask target, then dilates it in a screen pass to the group's
thickness and blends a fill (`front/core/PostproductionRenderer/src/simple-outline-pass.ts:60-84` for the id
uniform, 153-340 for the mask, dilation and combine shaders). Groups are bound to Highlighter styles
(`front/fragments/Outliner/index.ts:324-337`, `wireStyle` 464-484). For the app: draw the selected slots into a
mask in `engine/render/webgl.js` and `engine/render/webgpu.js`, then one dilation pass. The shaders are GLSL; they
must be re-written in the app's GLSL and WGSL, in our words.

### 3.4 3D measuring: snapping and the four tools (P, M in total)

The app's measuring is planar on purpose (`engine/annotation/inquiry.js:15-20`: X and Y on the plan, Z the level's
elevation). The gap is a **3D measure** for review of imported and solid models. What That Open does:
- Snapping classes point, line, face (`front/measurement/Measurement/index.ts:61-65`), resolved by core's raycaster
  with `snappingClasses` (`front/utils/graphic-vertex-picker.ts:132-150`). The app needs a pick that returns the
  3D point and the triangle: a depth read beside `bimPickGpu`, then the nearest vertex or edge of that triangle
  within a pixel radius (`snapDistance`, Measurement 653-659).
- Length edge mode keys an edge by its rounded ends so the same edge is not re-picked (`LengthMeasurement/index.ts:
  280-288`, Q = 1000, millimetres).
- Area face mode takes the whole picked face's points (`AreaMeasurement/index.ts:210-223`); square mode builds a
  rectangle from two points and the face normal (240-262). `bimTorArea` (V206 WO-06) already gives a 3D polygon's
  area by Newell's sums.
- Angle: two rays from a vertex, arc points sampled between them (`AngleMeasurement/index.ts:474-506`).
- Volume: sum of item volumes (`front/utils/volume.ts:40-55`); the app's `bimObjVolume` refuses open meshes
  (`engine/bim/type-instance-params.js:431-440`), which is stricter and should stay so.
- Units: length mm, cm, m, km; area and volume squared and cubed; angle deg or rad; rounding 2
  (`Measurement/src/types.ts:1-6`, `default-units.ts`).

### 3.5 ClipStyler: cut styles per category (P, M)

`ClipEdgesItemStyle` names a style and an optional classifier intersection (`front/core/ClipStyler/src/types.ts:
10-21`): items of a class or material get their own line and fill materials on the cut. The app's section tool
caps every loop (`engine/views/section-tool.js:96`, `bimCapLoop`) in one way. Port: a cut-style table keyed by the
app's own classification or material, read when a cap is drawn. Hatch patterns already exist for plans (V96).

### 3.6 Marker clustering (P, S)

`cluster(world)` (`front/core/Marker/index.ts:312-365`) merges labels whose screen distance is below `threshold`
50 px (83), places a cluster label at the mean position (`getAveragePositionFromLabels`, 421-436) and flies to the
cluster on click (503). Its own TODOs (5-8) say the method is O(n squared); the app should use a screen grid of
`threshold`-sized cells instead. The anchor and pixel-sized drawing already exist (`engine/annotation/
annotation-overlay.js:16-30`).

### 3.7 Post-production: pen style and live AO (P, L)

`PostproductionAspect` (`front/core/PostproductionRenderer/src/modes.ts:12-19`) has six looks: colour, pen, pen with
shadows, colour with pen, colour with shadows, all three. "Pen" is edges only on white; "shadows" is AO. The app
has edges in the shaded view, exact hidden lines from OCCT, and AO only in the accumulating rendered view
(`engine/render/rendered-core.js:4-18`). A pen look (white faces, edges, optional AO) in the shaded view is the
gap. That Open's screen-space AO is `deferred/screen-space-ao-pass.ts:1-277` with a denoise in `deferred/
ao-denoise-pass.ts:1-174`; the composer path uses three's GTAOPass (`src/ao-pass.ts` and `src/index.ts` import it). Reuse inside
Review is possible for the WebGL composer path only (three's examples are in the app's three build per e01, S: the
build's addon list was not re-read here). For the editable model, port the method (P), not the code.

### 3.8 Point clouds: streamed octrees (R in Review, M)

`PointCloudLoader.load` (`front/core/PointCloudLoader/index.ts:454-559`) imports `potree-core` lazily (469) and
streams a Potree 2.0 `metadata.json` octree with a point budget (default 1,500,000; settings 36-75) and EDL. It
reads no LAS or LAZ itself. The app reads local LAS and PLY in full (V190) and names LAZ, COPC and EPT as waiting
for the library rule (`engine/map/pointcloud.js:3-9`). Two separate gaps: (a) **LAZ, COPC** reading, which That Open
does not cover, so it is not closed by reuse; (b) **Potree octree streaming**, closable in Review with potree-core,
whose licence must be read first (U now). EDL is a small port (P, S): shade each point by its depth difference to
its neighbours (`edlStrength` 0.4, `edlRadius` 1.4 px; defaults at lines 60-70).

### 3.9 Gaussian splats: drawing is missing (R or P, M)

V205 shipped only the pure part (`engine/render/splats.js:7-115`: `.splat` parse, bounds, two-pair fit, apply,
back-to-front sort on the main thread). Its WO-06 ("Splats in the rendered view") is ticked but no drawing code is
in `src/` (section 1). That Open's renderer (`front/core/SplatLoader/gsplat/renderer.ts:1-377`) draws instanced
quads from data textures with EWA covariance projection, sorts in a worker (`gsplat/sort-worker-src.ts:1-116`),
picks LOD per cell of a 10-cubed grid, and depth-tests against the BIM depth so the model occludes splats
(`SplatLoader/index.ts:56-73`). It also reads INRIA PLY (`gsplat/ply.ts:1-227`) and SOG (`gsplat/sog.ts:1-212`),
which the app does not. Recommendation: draw splats in Review with SplatLoader (R) if the owner wants splats
beside imported IFC; otherwise port the worker sort and the instanced covariance quad into the rendered view (P).
Either way, the V205 record should be corrected (an audit item, not this note's to fix).

### 3.10 Civil: IfcAlignment and the cross-section navigator (R and P)

That Open's navigators work on alignment curves that fragments extracts from IFC (`front/civil/CivilNavigators/
src/index.ts:15`, `alignments: THREE.Group[]`). The app authors alignments natively with stations, PC and PT labels
and a profile view (`engine/site/alignment-profile.js:23-648`) but does not import IfcAlignment
(`grep -rn IfcAlignment src/` finds nothing). In Review, the navigators can be reused for imported alignments (R,
M). The cross-section navigator is a small port for the app's own alignments (P, S): place the section plane at
`bimStationAt` (586) with the plane normal along the alignment's tangent, as `CivilCrossSectionNavigator` does
(`front/civil/CivilCrossSectionNavigator/index.ts:1-202`; its plane at line 29, its offset 0.1 at line 37).

### 3.11 Drawing annotations: slope (P, S)

All of That Open's drawing tools have app equivalents except the slope annotation
(`front/drawings/DrawingEditor/src/SlopeAnnotationsTool/index.ts:1-520`: a position, a direction and a slope value
from the face under the cursor). The app has roof pitch as a property (`engine/site-analysis/panel.js:552`) but no
drawn slope arrow. Port as a `t:'dim'` kind, as V25 did for angular dimensions. Linear modes single, sequential
and by line (`LinearAnnotationsTool/src/modes.ts:1-34`) match DIMLINEAR, DIMCONTINUE and selecting a line.

### 3.12 Spatial tree, item data and model list (R in Review, P for the model)

In Review, `spatialTree`, `itemsData` and `modelsList` (`ui/obc/src/components/tables/*/index.ts`) can be mounted as
they are, through an adapter that calls `BUI.Manager.init()` and the ui-obc `Manager.init()`
(`ui/obc/src/core/Manager/index.ts:1-21`) once, on first open. Costs to record in Review's spec: Lit and
`@thatopen/ui` join the Review bundle; their look follows `--bim-ui_*` CSS variables, not the app's tokens; phone
layout is not shown anywhere in these templates (P, by reading `SpatialTree/src/template.ts`). For the editable model,
an ES5 tree is needed: Site (`A3D.site`), buildings (`A3D.buildings`), levels, then `bim.ifcType` or the app's type,
then elements; the collapse rules (`SpatialTree/src/types.ts:7-34`: merge a class row that has one child; skip
listed classes) are worth copying as behaviour.

### 3.13 BCF and IDS panels (R in Review, M)

The BCF tables and sections and the IDS chart depend on core's BCFTopics and IDSSpecifications (another agent's
area). They are the clearest case for R: the app has neither, they are coordination features that belong to
Review, and re-making them in ES5 would duplicate core logic the app does not have.

## 4. Can the Lit panels be used?

Yes inside Review, no for the editable model (P for the facts, the judgement is ours):
- They are custom elements defined at run time (`ui/core/src/core/Manager/index.ts:106-133`), so the app's ES5 code
  can create and append them as DOM nodes once the Review bundle has loaded. The library's code is not held to ES5
  under the third-party rule; the adapter in `engine/io/` stays ES5.
- Their data comes from That Open objects only (`SpatialTreeState.components`, `models: Iterable<FRAGS.
  FragmentsModel>`, `ui/obc/src/components/tables/SpatialTree/src/types.ts:3-6`), so they cannot show the app's
  `A3D.objs` without a fake fragments model, which is not worth it.
- `ui-obc` 3.4.5 pins `three` 0.185.0 as a peer (`ui/obc/package.json:72`); the app's 0.186.1 is a minor step
  above. Whether anything in ui-obc's own code breaks on 0.186.1 is not tested here (open).

## 5. What is still open

- potree-core's licence and size (U).
- Whether ui-obc's World, ViewCube and SheetBoard run on three 0.186.1 (not run here; e02 should cover it).
- That Open's AO and outline passes on the app's three build: which three addons the lean build of e01 kept
  (research-thatopen.md F8 and section 10 say the WebGPU stub is unexercised).
- The V205 WO-06 discrepancy (splats ticked as drawn, no drawing code) needs the owner or an audit.

## 6. Search log

2026-11-28: `find` and `wc -l` over `front/` and `ui/obc/src`; `grep` for public members, TODOs, imports of `three/
webgpu` and `three/tsl`, `potree-core`, `@thatopen/ui`; read the headers and the methods cited above. In the app:
`grep -rn` for measure, area, angle, volume, snap, hover, selection colour, isolate, outline, AO, cluster, splat,
point cloud, bcf, IDS, IfcAlignment, station, classifications and the project browser's groups; read the cited
ranges. No code from the clones was run. No second reader yet: the facts the recommendations use are all P and
are listed with their lines for one.
