# That Open gap: fragments 3.x and web-ifc, against this app

Research, 2026-11-28. Levels as in `research-protocol.md`: P primary (source read, file:line, or measured here), S
secondary (with the gap said), U a pointer only (never used in a recommendation).

Pinned sources (read as text, never run from the clones):

| Source | Revision | Note |
|---|---|---|
| ThatOpen/engine_fragment | 643d24e (2026-11-23) | `packages/fragments/package.json` says 3.6.1; its CHANGELOG has an "Unreleased" block, so the clone is ahead of npm 3.6.1 (published 2026-11-08). `research-thatopen.md` read bc3f688. |
| ThatOpen/engine_web-ifc | 9ab7d5c (2026-11-26) | `package.json` says 0.0.82 (unreleased). npm latest is 0.0.81 (2026-11-23). |
| npm web-ifc 0.0.81 | tarball, unpacked in the scratchpad | for what the published build contains |
| The app's pinned packages | `tools/thatopen/node_modules`: @thatopen/fragments 3.6.1, web-ifc 0.0.79, three 0.186.1 | what `runtime/thatopen/3.6.0/` was built from (MANIFEST.json 378-402) |

Paths below: `F/` is `engine_fragment/packages/fragments/src/`, `W/` is `engine_web-ifc/src/`, the app's are from
the repository root. This note extends `research-thatopen.md` (2026-11-13) and `research-ifc-engine.md` (V196). It
does not repeat their bundle sizes, file:// workarounds or the 13-file comparison.

## 1. Summary

- Fragments 3.x stores a model as one flatbuffers table: items by `localId` (the IFC express id), GlobalIds, IFC class
  names as strings, every kept attribute as a typed `[name, value, type]` string, relations as named lists of ids, a
  spatial tree, and geometry as shells (faces with holes) placed by samples (instances) with one RGBA material each
  (`F/../flatbuffers/index.fbs` 111-148, 219-245). P.
- The data and geometry can be read without a worker, a scene or a renderer: `SingleThreadedFragmentsModel` answers
  `getItemsGeometry`, `getItemsData`, `getSpatialStructure` and the rest synchronously (`F/FragmentsModels/src/
  single-threading/index.ts` 17-20, 59, 110-330). Measured here (e2) on the app's pinned 3.6.1 and web-ifc 0.0.79. P.
- **The geometry fragments and web-ifc give is already +Y up, in metres, and shifted to the origin.** web-ifc
  multiplies every placement by a fixed Z-up to Y-up matrix and the unit scale (`W/cpp/web-ifc/geometry/
  representation/geometry.h` 341-345; `IfcGeometryProcessor.cpp` 2259-2274), and fragments stores that transform
  (`F/Importers/IfcImporter/src/geometry/ifc-file-reader.ts` 228-231, 248-249, 914-933; `F/FragmentsModels/src/
  utils/geometry/transform-helper.ts` 27-31). e1 and e2 confirm: a 3 m wall is 3 m along Y. So V206's WO-01
  `bimTorMesh` (x, z, -y) must **not** be applied to fragments output: it would lay every element on its side. P.
- WO-09 can reuse V196's mesh, layer, level and property code almost unchanged; the recipe is in section 5, with
  every call's return shape as measured.
- web-ifc's writer (`CreateModel`, `WriteLine`, `SaveModel`) works and is small, but it is a line writer: no
  high-level helpers and no schema checks (e1 wrote an IfcWall with no GlobalId without complaint). Keep IfcOpenShell
  for Save as IFC; use web-ifc's writer only to patch an imported file in place (section 6).
- web-ifc since 0.0.79 (the app's pin): 0.0.80 bundles geokernel (MPL-2.0) and turns it on as the reserve for open
  boolean results, adds `SectionMesh`/`GetSection`, wireframe output for curve-only products (`EXPORT_POLYLINES`) and
  STEP binary literals over 65,535 characters; 0.0.81 adds `GetSweptDiskAxes` and brep fixes (openings on aggregated
  parts, arcs faceted by size). The brep engine (`StreamAllBrepMeshes`) is a build option not in the npm wasm.

## 2. Question and hypotheses

What do fragments 3.x and web-ifc give that the app lacks, how exactly does WO-09 turn their output into the app's
meshes, and can web-ifc's writer replace or complement IfcOpenShell?

- H1: fragments output needs the Z-up to Y-up swap of `bimTorMesh`. **False** (P, e1, e2): it is Y-up already.
- H2: WO-09 needs fragments' worker. **False** (P, e2): `SingleThreadedFragmentsModel` reads everything on the
  calling thread; the worker is only needed for the Review view's rendering.
- H3: fragments keeps the property sets and GlobalIds V196 shows. **Held** (P, e2): GlobalId per item, psets and
  quantity sets through `IsDefinedBy`, type objects too; it keeps more (typed values, materials, CRS).
- H4: fragments keeps opening elements as items. **False** (P): `IFCOPENINGELEMENT` is commented out of the element
  classes (`F/Importers/IfcImporter/src/classes.ts` 350); `IfcRelVoidsElement` and `IfcRelFillsElement` are not in the
  default relations (`F/Importers/IfcImporter/index.ts` 70-103; they are only in `addAllRelations`, `F/Utils/
  ifc-relations-map.ts` 92, 176). Openings come through as holes cut by web-ifc.
- H5: web-ifc's writer checks what it writes. **False** (P, e1).
- H6: the npm web-ifc build includes the brep engine. **False** (P): `StreamAllBrepMeshes` is not among the 0.0.81
  wasm's names (strings search), and the API throws "this build has no brep engine" (`W/ts/web-ifc-api.ts` 1547).

## 3. Method

Search log:

| Where | What was read or run | Level |
|---|---|---|
| `F/../flatbuffers/index.fbs` | whole schema, 248 lines | P |
| `F/FragmentsModels/src/model/fragments-model.ts`, `model-types.ts`, `edit-manager.ts`, `coordinates-manager.ts` | public methods and their types | P |
| `F/FragmentsModels/src/single-threading/index.ts`, `virtual-model/virtual-fragments-model.ts`, `virtual-helpers/geometry-helper.ts`, `virtual-controllers/virtual-properties-controller.ts` 630-760, `virtual-tiles-controller.ts` 189-195, 934-951 | how geometry and item data are produced | P |
| `F/Importers/IfcImporter/index.ts`, `src/classes.ts`, `src/geometry/ifc-file-reader.ts`, `src/properties/property-processor.ts` | what the importer keeps | P |
| `F/FragmentsModels/src/edit/editor.ts`, `F/Utils/edit/edit-types.ts`, `fetch-functions.ts` | the Editor | P |
| `F/Utils/ifc-splitter/index.ts` 1-60, 984-1300 | IfcSplitter | P |
| `W/ts/web-ifc-api.ts`, `W/ts/ifc-schema.ts` (SchemaNames), `W/ts/helpers/properties.ts`, `W/../docs/boolean-fallback.md` | API, schemas, helpers | P |
| `W/cpp/web-ifc/geometry/IfcGeometryProcessor.cpp`, `IfcGeometryLoader.cpp`, `representation/geometry.h`, `W/cpp/CMakeLists.txt` 178-183 | geometry kernel coverage, axes, coordination | P |
| `git log` of a separate blobless clone of engine_web-ifc | commits between 0.0.79 and 9ab7d5c | P |
| `npm view` web-ifc, @thatopen/fragments; `npm pack web-ifc@0.0.81` | versions, dates, dependencies, the build's contents | P |
| e1, e2 (section 7) | measured | P |
| The app: `src/js/engine/io/ifc-full.js`, `ifc-review.js`, `ifc-save.js`, `import-ifc.js`, `src/py/bim_ifcos.py`, `runtime/MANIFEST.json`, `tools/thatopen/build_thatopen.mjs`, `docs/work-orders/v206/` | what the app does now | P |

No web search was used. A second, independent reader has not yet re-checked this note (section 9).

## 4. The gap table

Gap: NONE, PARTIAL, MISSING. Close by: R reuse through an adapter (library approved 2026-11-13), P port into our
ES5 engine, X not worth it. Effort: S (under a day), M (days), L (a phase or more).

### 4.1 Fragments 3.x

| Capability | What (our words) | Source | Ours | Gap | Close by | Effort | Level |
|---|---|---|---|---|---|---|---|
| Model format | One flatbuffers `Model`: local ids, GlobalIds, class names, typed attributes, named relations, spatial tree, meshes, user indexes; deflated unless `raw` | `index.fbs` 206-245; `IfcImporter/index.ts` 294-322 | Project JSON with each element's welded mesh (`ifc-full.js` 227-229) | PARTIAL | X as stored data (format changes with each major, `research-thatopen.md` F11); keep a `.frag` only as a cache for Review | S | P |
| Geometry model | Shells (faces, holes, big variants over 65,535 points) and circle extrusions (rebars), placed by samples = item x representation x material x local transform | `index.fbs` 79-148 | One welded triangle mesh per element | PARTIAL | X: the app needs one mesh per element to select and edit; instancing stays a Review benefit | - | P |
| Read without a worker | `SingleThreadedFragmentsModel(id, bytes, raw)`, `ready`, then synchronous reads | `single-threading/index.ts` 20, 59-95 | cc-ifc on the main thread | NONE | R (the WO-09 route) | S | P, e2 |
| Geometry per element | `getItemsGeometry(localIds)` returns `MeshData[][]`: per item, per sample `{transform: Matrix4, positions: Float32Array, indices: Uint16/32Array, normals: Int16Array, localId, sampleId, representationId}`; transform = global x local | `fragments-model.ts` 506; `model-types.ts` 281-296; `geometry-helper.ts` 15-57; `transform-helper.ts` 27-31 | `bimIfcMeshParts` from `StreamAllMeshes` (`ifc-full.js` 86-119) | NONE once WO-09 is built | R | M | P, e2 |
| Axes and units | Y up, metres, shifted to the origin by the coordination matrix (web-ifc's, kept by the importer) | `ifc-file-reader.ts` 228-231, 590, 715, 914-933 | Same, from cc-ifc (`ifc-full.js` 84, 166) | NONE | R | - | P, e1, e2 |
| Colour per sample | `getSamples([sampleId])` gives `{item, material, representation, localTransform}`; `getMaterials([id])` gives `{r, g, b, a (0-255), renderedFaces, stroke}`. web-ifc's `hasColor` is not kept: an unstyled element is white | `fetch-functions.ts` 233-250, 431-451; `ifc-file-reader.ts` 650-664 | Majority colour, `#b8b8b0` when none (`ifc-full.js` 71-74, 112) | PARTIAL | R, with a rule: treat pure white at 255 alpha as "no colour" only if the file has no styled items (open) | S | P, e2 |
| Spatial tree | `getSpatialStructure()`: alternating nodes, a class node `{category, localId: null, children}` and item nodes `{category: null, localId, children}` | `model-types.ts` 398-405; `property-processor.ts` 903-938 | `bimIfcContainers` over web-ifc's tree (`ifc-full.js` 131-140) | NONE once walked as in 5.4, step 6 | R | S | P, e2 |
| Classes | `getCategories()` (strings, upper case, e.g. `IFCWALL`); `getItemsOfCategories([RegExp])` gives `{CLASS: [ids]}` | `fragments-model.ts` 324, 461 | Layer per class (`ifc-full.js` 187, 210-219) | NONE | R | S | P, e2 |
| GlobalId | `getGuidsByLocalIds(ids)`, `getLocalIdsByGuids(guids)`; `_guid` in item data | `fragments-model.ts` 307, 436; `virtual-properties-controller.ts` 688-692 | `o.bim.guid` (`ifc-full.js` 220) | NONE | R | S | P, e2 |
| Attributes | Every direct attribute but `Representation`, `ObjectPlacement`, `CompositionType`, `OwnerHistory` and GlobalId, as `{value, type}` with the IFC type name | `IfcImporter/index.ts` 41-46; `property-processor.ts` 403-545 | Name and GlobalId only | PARTIAL | R: keep Description, ObjectType, Tag, PredefinedType in `o.bim.attrs` | S | P, e2 |
| Property and quantity sets | Through `IsDefinedBy` (IfcRelDefinesByProperties), each set's `HasProperties` or `Quantities` | `IfcImporter/index.ts` 70-74; `classes.ts` 55-74 | `bimIfcPsets`, 40 sets of 80 values, as text (`ifc-full.js` 142-161) | NONE | R | S | P, e2 |
| Type objects and their sets | The type comes in `IsDefinedBy` too (IfcRelDefinesByType's related name), its sets in `HasPropertySets` | `IfcImporter/index.ts` 75-78; `classes.ts` 75-230 | Not read: V196 calls `getPropertySets(mid, id, true)` without type properties (`ifc-full.js` 156) | MISSING | R (one more relation in the config) | S | P |
| Materials | IfcMaterial, layer sets and usages, profile sets, through `HasAssociations` | `classes.ts` 27-38; `IfcImporter/index.ts` 79-82 | None from IFC | MISSING | R: a Materials group in Properties | S | P |
| Storey elevation | `replaceStoreyElevation` (default true) writes each storey's absolute elevation in metres into `Elevation` | `IfcImporter/index.ts` 136; `property-processor.ts` 424-436 | `Elevation x unit + C[13]` (`ifc-full.js` 121-129) | NONE | R | S | P, e2 |
| Queries | `getItemsByQuery({categories, attributes: {queries: [{name: RegExp, value}]}, relation})` | `fragments-model.ts` 485; `model-types.ts` 738-766 | None over IFC attributes | MISSING | R inside Review first; P a small filter over `o.bim` later | M | P |
| Coordinates | `getCoordinates()` gives `[x, y, z, xx, xy, xz, yx, yy, yz]` (the shift and the axes); `getCoordinationMatrix()` builds a Matrix4 from it | `coordinates-manager.ts` 7-46; `coordinates-helper.ts` 21-41 | `D.coord` and `bim.edit.shift` (`ifc-full.js` 179, 225) | NONE | R | S | P, e2 |
| Georeferencing | `getCRS()`: IfcProjectedCRS (or IfcCoordinateReferenceSystem) and IfcMapConversion (eastings, northings, height, x axis, scale), `null` without one | `fragments-model.ts` 428; `model-types.ts` 549-579; `property-processor.ts` 760-800 | Read by nobody: V196 left it open (`research-ifc-engine.md` 8) | MISSING | R to read; P to place on the map (`site/`, `map/`) | M | P, e2 (null case only) |
| Alignments, grids | IFC4.3 alignments as curves (lines, clothoids, arcs, parabolas); IfcGrid axes as polylines, other curve types listed as unsupported | `fragments-model.ts` 671-713; `model-types.ts` 496-546 | Own grids (`bim/structural-grids.js`); no IFC alignment or grid import | MISSING | R | M | P |
| Spaces | IfcSpace kept, drawn half transparent by default | `classes.ts` 231+; `ifc-file-reader.ts` 652-658 | Imported as solids on an IfcSpace layer | NONE | R | - | P |
| Space boundaries, MEP ports | Opt-in: second-level space boundaries; ports and their connections | `ifc-file-reader.ts` 365-375; `IfcImporter/index.ts` 166-183 | Rooms and MEP flow are the app's own | MISSING | X for now | - | P |
| LOD, tiles, culling | Tiles per material and size, LOD as boxes or wires, three modes | `model-types.ts` 787-799; `virtual-tiles-controller.ts` | The app's own batches; import cap 1.5 million triangles (`ifc-full.js` 29) | MISSING over the cap | R in Review (WO-08) | L | P |
| Editor | Requests to create, update and delete materials, representations, samples, transforms, items, relations, indexes; `edit`, `save` (a new `.frag`), undo, redo; `createElements` from three.js geometry | `editor.ts` 40-326; `edit-types.ts` 181-231; `single-threading/index.ts` 480-534 | The app's own parametric engine edits; imported IFC is locked, walls and slabs can be made editable (`ifc-editable.js`) | NONE that matters | X: it edits fragments, not BIM elements with rules (`research-thatopen.md` H5) | - | P |
| IfcSplitter | Streams STEP text (no wasm) to split a file in N valid files or `extract` chosen elements with all they depend on, keeping wall, opening and door together | `F/Utils/ifc-splitter/index.ts` 984-996, 1259-1271 | None | MISSING | R for "export these imported elements as IFC" from the source file (needs the original bytes kept) | M | P |
| Worker | Fetches its worker from unpkg unless `inline` is imported; `classicWorker` option | `F/FragmentsModels/index.ts` 22-30, 74-90 | e01's workarounds (`research-thatopen.md` F2, F3) | NONE | R | - | P |

### 4.2 web-ifc

| Capability | What (our words) | Source | Ours | Gap | Close by | Effort | Level |
|---|---|---|---|---|---|---|---|
| Schemas | IFC2X3 (also IFC2X_FINAL), IFC4, IFC4X3 (IFC4.3 ADD2; IFC4X1, 4X2, RCs and ADD1 parsed as 4X3 with a warning, refusable with `ALLOW_INCOMPATIBLE_SCHEMA_ALIASES: false`) | `W/ts/ifc-schema.ts` 1196-1201, 9268, 18951; `web-ifc-api.ts` 99-104, 607-630 | cc-ifc: the same three (`research-ifc-engine.md` 5) | NONE | - | - | P |
| Reading | `OpenModel(bytes, settings)`, `OpenModelFromCallback`, `StreamMeshes(ids)`, `StreamAllMeshes`, `StreamAllMeshesWithTypes`, `GetFlatMesh`, `GetLine(id, recursive, inverse)` | `web-ifc-api.ts` 638-710, 904-930, 1512-1640 | cc-ifc copies these calls (`ifc-full.js` 89-128) | NONE | - | - | P |
| Placed geometry | `FlatMesh {expressID, geometries}`, each `{color, hasColor, geomType, geometryExpressID, flatTransformation}`; vertices 6 floats (x y z, normal) | `web-ifc-api.ts` 145-164, 229-236, 1475-1481 | Read so by `ifc-full.js` 92-101 | NONE | - | - | P |
| Kernel coverage | Extrusions (and tapered), revolutions, swept disks, fixed-reference and surface-curve sweeps, sectioned solids (and horizontal, IFC4.3), CSG primitives, boolean results and clipping, half spaces, faceted and advanced breps (B-spline surfaces with knots, rational), polygonal and triangulated face sets, TINs, mapped items, text literals; profiles arbitrary, rectangle, circle, ellipse, I-shape; curves polyline, indexed polycurve, circle, ellipse, B-spline, trimmed, composite, clothoid, gradient and segmented reference curves. No case found for IfcOffsetCurve, IfcSectionedSpine, IfcRevolvedAreaSolidTapered, IfcDirectrixCurveSweptAreaSolid, IfcSweptDiskSolidPolygonal | `IfcGeometryProcessor.cpp` (the `case schema::` list; e.g. 522, 542, 553, 1078, 1158, 1414, 1440, 1467); `IfcGeometryLoader.cpp` | cc-ifc matched web-ifc on 13 files (`research-ifc-engine.md` 4) | NONE | - | - | P (coverage by case labels; behaviour per case not tested) |
| Openings | Voids cut per element; more than `BOOLEAN_UNION_THRESHOLD` (150) voids are fused first | `IfcGeometryProcessor.cpp` 459-475; `web-ifc-api.ts` 600 | cc-ifc with Manifold | NONE | - | - | P |
| Boolean reserve | 0.0.80: `SetBooleanFallback(fn)`; `Init()` registers the bundled geokernel 0.10.0 (MPL-2.0, 235 KB JS) unless told not to; the result with fewer naked edges is kept | `web-ifc-api.ts` 46-47, 472-477, 1736-1754; `W/../docs/boolean-fallback.md` | None needed at 0.0.79 | NONE | Decide on upgrade: keep it (better solids) or `SetBooleanFallback(null)` (0.0.79 behaviour) | S | P |
| Brep engine | `StreamAllBrepMeshes`, `SetBrepBooleansOnly`: only in builds made with `BREP_ENGINE` | `web-ifc-api.ts` 1536-1584; `W/cpp/CMakeLists.txt` 178-183 | - | - | X (not in the npm wasm, H6) | - | P |
| Tessellation | `CIRCLE_SEGMENTS` 12 by default; plane, back-deviation and scalar tolerances 1e-4; 0.0.81 facets arcs by size | `web-ifc-api.ts` 586-604; git 43189a7d | cc-ifc's own (finer on NURBS) | PARTIAL | R: expose `CIRCLE_SEGMENTS` if curved walls look coarse | S | P |
| Curves and points | 0.0.80: `EXPORT_POLYLINES` gives line strips and points for products with no solid (annotations, grids, curve sets), `geomType` 1 or 2 | `web-ifc-api.ts` 70-82, 118-124, 145-158; git 91cf367d | Not imported | MISSING | R: import as the app's lines on the class layer | S | P |
| Sections | 0.0.80: `SectionMesh(positions, indices, plane)` and `GetSection(modelID, plane)`: cut lines and a capped area | `web-ifc-api.ts` 1756-1820; git 8f927525 | `views/` sections of the app's own model | NONE for the app's model | R in Review for imported IFC | M | P |
| Property helpers | `properties.getItemProperties`, `getPropertySets(id, recursive, includeTypeProperties)`, `getTypeProperties`, `getMaterialsProperties(id, recursive, includeTypeMaterials)`, `getSpatialStructure(includeProperties)`, setters for psets and materials | `W/ts/helpers/properties.ts` 75-164 | Two of them (`ifc-full.js` 156, 170) | PARTIAL | R (types and materials: as in 4.1) | S | P |
| Coordination | `COORDINATE_TO_ORIGIN` shifts by minus the first vertex of the first solid streamed; `GetCoordinationMatrix` returns that shift (column-major) | `IfcGeometryProcessor.cpp` 2321-2345; `web-ifc-api.ts` 1463 | Kept as `D.coord` | NONE | - | - | P, e1 |
| Georeferencing | Geometry never applies IfcMapConversion (only the schema code names it) | grep of `W/cpp`: only `schema/` | As 4.1 | MISSING | As 4.1 (read through fragments' `getCRS`) | M | P |
| Alignments | `GetAllAlignments`, `GetAllCrossSections2D/3D` | `web-ifc-api.ts` 1292-1368 | None | MISSING | R through fragments' alignments | M | P |
| Rebars | 0.0.81: `GetSweptDiskAxes(model, product)`: a swept disk's directrix and radii without meshing | `web-ifc-api.ts` 192-204, 1567; git 43189a7d | None | MISSING | X (no rebar authoring in the app) | - | P |
| Memory | `MEMORY_LIMIT` 2 GiB and `TAPE_SIZE` 64 MiB by default; heap pointers read unsigned past 2 GB | `web-ifc-api.ts` 589-591; `boolean-fallback.md` | cc-ifc in the JS heap | NONE | - | - | P (limits read, not reached) |
| Writer | `CreateModel({schema, name, description, authors, organizations, authorization})`, `CreateIfcEntity`, `CreateIfcType`, `CreateIFCGloballyUniqueId`, `WriteLine(s)`, `DeleteLine`, `WriteRawLineData`, `SaveModel`, `SaveModelToCallback` | `web-ifc-api.ts` 421-428, 724-810, 1032-1065, 1106-1190, 1232-1240 | IfcOpenShell in Pyodide (`src/py/bim_ifcos.py`, `io/ifc-save.js`, `io/ifcos-*.js`) | NONE (different engine) | See section 6 | - | P, e1 |

## 5. WO-09 recipe

What WO-09 must do: an IFC file becomes, per element with geometry, one locked solid in metres, +Y up, on a layer
for its IFC class under a layer named after the file, with its GlobalId, storey and property sets, and the storeys
become levels, exactly as V196 does, but read through fragments. The app's own code stays ES5; the calls below go
through one adapter file (say `io/ifc-toe.js`). Each shape is the one e2 printed (section 7) unless noted.

### 5.1 Runtime

`runtime/thatopen/3.6.0/` already holds `bim-webifc.min.js` (global `BIMWEBIFC`), `bim-webifc-wasm.js`
(`BIMWEBIFC_WASM`, base64) and `bim-thatopen.min.js` (global `BIMTOE`, with `BIMTOE.FRAGS` = @thatopen/fragments,
three mapped to `BIMTHREE`) (`tools/thatopen/build_thatopen.mjs` 6-11, 40-59). Both `IfcImporter` and
`SingleThreadedFragmentsModel` are in the bundle (grep of `bim-thatopen.min.js`). Load order: `BIMTHREE`,
`BIMWEBIFC` (+ wasm), `BIMTOE`, by the same "beside the page, then the site with SRI" loader as `bimIfcLoad`
(`ifc-full.js` 32-70), and the e01 fetch wrapper that serves the wasm from `BIMWEBIFC_WASM` (WO-08 builds it once).
No worker is needed for import.

### 5.2 Convert

```
var FR = BIMTOE.FRAGS;
var imp = new FR.IfcImporter();
imp.wasm = {path: wasmBase, absolute: true};       // F/Importers/IfcImporter/index.ts 30-33; SetWasmPath, ifc-file-reader.ts 188
imp.webIfcSettings = {COORDINATE_TO_ORIGIN: true}; // the default (index.ts 35-37); as V196 (ifc-full.js 166)
imp.parseOnce = true;                              // one web-ifc parse for geometry and properties (index.ts 195-203)
imp.distanceThreshold = null;                      // see the edge in 5.6
imp.process({bytes: u8, raw: true, progressCallback: function (p, d) {...}})   // index.ts 220-323
  -> Promise<Uint8Array>   (the .frag buffer; raw = not deflated)
```

`progressCallback(progress 0..1, {process: 'geometries'|'attributes'|'relations'|'conversion', state, class,
entitiesProcessed})` (`F/Importers/IfcImporter/src/types.ts` 3-8) feeds the toast. The conversion runs on the
calling thread, one web-ifc stream per IFC class (`ifc-file-reader.ts` 318-350).

### 5.3 Open and read

```
var M = new FR.SingleThreadedFragmentsModel(stem, frag, true);   // single-threading/index.ts 59
M.ready.then(...)                                                // resolves when set up (index.ts 41-51)
```

Every read below is synchronous on this class; wrap each in `Promise.resolve()` so the same adapter also works
with the worker's `FragmentsModel`, whose reads return promises (`fragments-model.ts` 299-660).

| Call | Returns (measured, e2) | Use |
|---|---|---|
| `M.getItemsIdsWithGeometry()` | `number[]` of local ids (= IFC express ids), e.g. `[29]` | the elements to draw |
| `M.getItemsOfCategories([/IFCBUILDINGSTOREY/])` | `{IFCBUILDINGSTOREY: [14, 18]}` | the storeys |
| `M.getItemsData(storeyIds, {attributesDefault: true})` | `[{_category: {value: 'IFCBUILDINGSTOREY'}, _localId: {value: 14}, _guid: {value: '08_q4...'}, Name: {value: 'Level 0', type: 'IFCLABEL'}, Elevation: {value: 0, type: 'IFCLENGTHMEASURE'}}, ...]` | level name and absolute elevation, metres |
| `M.getCoordinates()` | `[0, -3, -0.15, 1, 0, 0, 0, 1, 0]`: the shift x, y, z, then the x and y axes | `coord`; the storey's app elevation is `Elevation + coords[1]` |
| `M.getSpatialStructure()` | `{category: 'IFCPROJECT', localId: null, children: [{category: null, localId: 1, children: [{category: 'IFCSITE', localId: null, children: [...]}]}]}` | element to storey map |
| `M.getItemsData(ids, CFG)` | per id: `{_category, _localId, _guid, Name, ..., ContainedInStructure: [storey data], IsDefinedBy: [{_category: {value: 'IFCPROPERTYSET'}, Name: {value: 'BIM_Personal'}, HasProperties: [{Name: {value: 'Type'}, NominalValue: {value: 'wall', type: 'IFCLABEL'}}, ...]}]}` | class, GlobalId, name, psets |
| `M.getItemsGeometry(ids)` | `MeshData[][]`; e2: `positions` Float32Array(72), `indices` Uint16Array(36), `normals` Int16Array, `transform.elements` `[1,0,0,0, 0,0,-1,0, 0,1,0,0, 3,-1.5,-0.15,1]`, `localId` 29, `sampleId` 59 | the mesh |
| `M.getSamples([sampleId])` then `M.getMaterials([material])` | `Map`: `59 -> {item: 56, localTransform: 60, material: 58, representation: 57}`; `58 -> {r: 255, g: 255, b: 255, a: 255, renderedFaces: 0, stroke: 0}` | colour and opacity |
| `M.getCRS()`, `M.getMetadata()` | `null` here; metadata `{schema: 'IFC4', names: [...], descriptions: [...], crs, generator, version}` | the toast's schema; georeferencing later |

`CFG` for the item data must switch off the relations that point back, or the result is circular (e2 failed with
"Converting circular structure to JSON" until `DefinesOccurrence` was off): a nested item inherits its parent
relation's setting unless its own relation is named (`virtual-properties-controller.ts` 630-663).

```
var CFG = {attributesDefault: true,
  relations: {IsDefinedBy: {attributes: true, relations: true},
              HasPropertySets: {attributes: true, relations: true},     // a type object's own sets
              HasAssociations: {attributes: true, relations: false},    // materials (optional)
              ContainedInStructure: {attributes: true, relations: false},
              DefinesOccurrence: {attributes: false, relations: false},
              ObjectTypeOf: {attributes: false, relations: false},
              AssociatedTo: {attributes: false, relations: false},
              ContainsElements: {attributes: false, relations: false},
              IsDecomposedBy: {attributes: false, relations: false},
              Decomposes: {attributes: false, relations: false}},
  relationsDefault: {attributes: false, relations: false}};
```

Read in chunks (say 500 ids) to bound memory on large files.

### 5.4 Turn it into the app's objects

1. **Mesh per element.** For each `arr` of `getItemsGeometry(chunk)` and each `m` of `arr` (skip empty arrays; key
   by `m.localId`, not by position): world point = `m.transform` (column-major `elements`) times each
   `m.positions` triple, exactly as `ifc-full.js` 98-101 does with `flatTransformation`; indices offset by the
   vertices so far. **No axis swap and no unit scale**: the result is already metres, +Y up, shifted as V196's.
   Normals are not needed (`bimGltfWeld` and `bimGltfFeatureEdges` rebuild what the app uses). Then
   `bimGltfWeld(pos, idx)`, `mm.fe = bimGltfFeatureEdges(mm)`, the same triangle cap (`BIM_IFC.maxTris`).
2. **Colour.** Per sample: `getSamples` then `getMaterials`; hex from `r, g, b` (0-255, not 0-1 as web-ifc's);
   opacity `a / 255`; the colour covering most triangles at full opacity, as `ifc-full.js` 103-112.
3. **Class.** `_category.value` is upper case (`IFCWALLSTANDARDCASE`). The layer names V196 made are web-ifc's type
   names (`IfcWallStandardCase` then `bimIfcClass` strips the suffix). Map the upper-case name back with
   `BIMWEBIFC.IfcAPI` `GetNameFromTypeCode(GetTypeCodeFromName(cat))`, or a table from the schema, so the layers
   keep V196's names and `bimTorCompare` compares like with like.
4. **GlobalId, name.** `_guid.value`, `Name.value` (through `bimIfcText`).
5. **Storeys as levels.** Storey ids from `getItemsOfCategories`; name and `Elevation.value` from their item data;
   app elevation `Elevation.value + coords[1]` (fragments has already made `Elevation` absolute and metric,
   `property-processor.ts` 424-436; V196 got the same with `e * u + C[13]`, `ifc-full.js` 126). Then the same level
   rule as `ifc-full.js` 204-209.
6. **Element to storey.** Walk the spatial tree: `walk(n, holder)`: if `n.localId != null` and it is a storey, it
   becomes the holder for its subtree; else if `n.localId != null` and there is a holder, `map[n.localId] = holder`;
   recurse into `n.children`. The class nodes (`localId: null`) only group. This also covers parts of aggregates
   (stair flights), which `ContainedInStructure` alone misses.
7. **Property sets.** `bimIfcSet` (`ifc-full.js` 142-154) works on fragments' item data as it is: it reads
   `L.HasProperties || L.Quantities`, `q.Name`, the first key ending in `Value`, `EnumerationValues`, `ListValues`,
   and `bimIfcVal` takes `.value`. Sets: every `IsDefinedBy` entry whose `_category` is `IFCPROPERTYSET` or
   `IFCELEMENTQUANTITY`; for an entry whose `_category` ends in `TYPE`, its `HasPropertySets` (new: V196 had none).
   Same caps (40 sets, 80 values).
8. **Shift.** `D.coord` for `bim.edit.shift` (`ifc-full.js` 224-225): `[coords[0], coords[1], coords[2]]`, the same
   numbers V196 took from `C[12..14]`.
9. **Compare with V196.** Counts by class from both readers into `bimTorCompare` on the 13 files of
   `research-ifc-engine.md` 4. Expect differences where fragments drops geometry with no vertices or indices (`ifc-file-reader.ts`
   580-584, 705-709) and where its face rebuild changes triangle counts; compare elements, boxes and areas, not triangles.

### 5.5 What changes in V206's pure functions

- `bimTorMesh` (WO-01, `io/ifc-review.js` 6) swaps axes: right only for raw IFC coordinates (Z up), wrong for
  fragments' and web-ifc's placed output (e1, e2). WO-09 should not call it on `getItemsGeometry` output; keep it for
  Z-up data only (for instance a point the user picks in IFC coordinates), or change SPEC 5 WO-01 to say so.
- `bimTorGuidValid`, `bimTorGuidFromHex`, `bimTorGuidToHex` fit as they are: fragments' GUIDs are the file's 22
  characters (e2).

### 5.6 Edges

- `distanceThreshold` (100,000 by default) skips an element whose placement is farther along +x, +y or +z, but not
  along a negative axis (`ifc-file-reader.ts` 250-262): one-sided. With `COORDINATE_TO_ORIGIN` it rarely matters; set
  it to `null` so nothing is dropped silently, and count elements against the file.
- The origin shift depends on which solid web-ifc streams first (`IfcGeometryProcessor.cpp` 2321-2345); fragments
  streams class by class with IfcAnnotation last (`ifc-file-reader.ts` 318-350), V196 streamed all at once. The two
  readers can shift the same file differently: compare boxes after undoing each shift.
- Unstyled elements are white in fragments (e2), grey in V196.
- Opening elements are not items (H4): no opening can be selected, as in V196.
- The importer runs web-ifc on the calling thread; a large file blocks the page as V196 does (`research-ifc-
  engine.md` 8). The fragments worker does not help here: it loads `.frag`, it does not convert.

## 6. web-ifc writer vs IfcOpenShell

| | web-ifc writer | IfcOpenShell 0.8.5 in Pyodide (V177) |
|---|---|---|
| Already shipped | Yes, the same web-ifc as the reader (`runtime/thatopen/3.6.0/`) | Yes (`runtime/ifcos/0.8.5/`, Pyodide 0.29.5) |
| Download | Nothing more once the reader is loaded (about 0.6 MB compressed wasm) | Pyodide (8.6 MB wasm, 2.4 MB stdlib, 2.8 MB numpy) plus the 14.7 MB IfcOpenShell wheel and its helpers, raw sizes (MANIFEST.json) |
| Licence | MPL-2.0, its own file | LGPL-3.0, its own file, in the Python worker |
| Level of the API | One STEP line at a time: the app would build IfcProject, units, contexts, placements, profiles, extrusions, aggregation, containment, voids, fills and psets itself | `ifcopenshell.api` does each in one call (`bim_ifcos.py` 54-116, 195-335) |
| Checks | None: e1 wrote `IFCWALL($,$,...)`, a wall with no GlobalId, and saved it | S, not run here: IfcOpenShell checks attribute types when an entity is made, and ships a validator (`ifcopenshell.validate`) |
| Header | Defaults to `ViewDefinition [CoordinationView]` and `'2;1'` for every schema (`web-ifc-api.ts` 738-760; e1); the caller can pass `description` | Set by IfcOpenShell |
| GlobalId | `CreateIFCGloballyUniqueId` gives a valid 22-character id (e1) | `root.create_entity`; V177 keeps imported ids (`bim_ifcos.py` 156) |
| Round trip of a foreign file | Strong: open the original, change or add lines, `SaveModel`: everything the app does not understand is kept | Possible (`ifcopenshell.open`), heavier |
| Schemas | IFC2X3, IFC4, IFC4X3 | IFC2X3, IFC4, IFC4X3 |

**Recommendation.** Do not replace IfcOpenShell for Save as IFC: the app would rewrite in JavaScript what
`ifcopenshell.api` already does, with no check behind it, and V177's writer is built and tested. Use web-ifc's writer
as a complement for one job IfcOpenShell does less well here: **saving an imported IFC back with the user's
property edits**, by reopening the original bytes, writing `IfcPropertySet` and `IfcRelDefinesByProperties` lines for
the changed elements (found by GlobalId, `GetExpressIdFromGuid`, `web-ifc-api.ts` 1669) and `SaveModel`. Pass an
IFC4 view name in `description`. Any such file should pass IfcOpenShell's validator (in the same Pyodide worker)
before it is offered as valid; that check is the owner's decision (section 8). Effort M; not WO-09.

## 7. Experiments (run here, 2026-11-28)

Scripts: `docs/research/experiments/thatopen-gap/webifc-e1.cjs` (e1) and `fragments-e2.mjs` (e2). Input: `tests/fixtures/ifc/v177_wall_ifcos.ifc`
(one 6 m x 3 m x 0.3 m IfcWall, two storeys, one pset).

- **e1**, npm web-ifc 0.0.81 unchanged, Node 22: without `COORDINATE_TO_ORIGIN` the wall's box is x 0..6, y 0..3,
  z -0.15..0.15 (height on Y, IFC's y becomes minus z); with it, x 0..6, y -3..0, z -0.3..0, and the coordination
  matrix's translation is (0, -3, -0.15), minus the wall's first vertex. Writer: `CreateModel` IFC4, an IfcProject
  and an IfcWall with new GUIDs, and an IfcWall with every attribute null: all written; `SaveModel` gave 728 bytes,
  reopened as 3 lines; header as in section 6.
- **e2**, the app's pinned @thatopen/fragments 3.6.1 and web-ifc 0.0.79 (`tools/thatopen/node_modules`): `IfcImporter`
  converted the file in about 100 ms to a 3,632-byte raw `.frag`; `SingleThreadedFragmentsModel` gave the shapes in
  section 5.3; the wall's world box from `getItemsGeometry` was x 0..6, y -3..0, z -0.3..0, the same as e1's.

One small file only: enough for axes, units, shift and return shapes; not for speed, coverage or large models.

## 8. The owner's decisions to ask (together, at the end of the gap research)

1. WO-09 route: fragments (`IfcImporter` then `SingleThreadedFragmentsModel`, as the 2026-11-13 decision reads), or
   web-ifc directly through V196's existing code (cc-ifc copies web-ifc's API, so `ifc-full.js` needs only its three
   cc-ifc-only calls replaced: `api.geometry(mid).g.lengthUnit`, `api.notes`, `api.booleans`). Fragments gives types,
   materials, CRS and one buffer shared with Review; direct web-ifc is smaller work and one parse.
2. On moving to web-ifc 0.0.81: keep geokernel as the boolean reserve (default) or switch it off for 0.0.79's output.
3. `bimTorMesh`: restrict it to Z-up input (recommended) or remove it from WO-09's path.
4. Unstyled elements: white (fragments) or V196's grey.
5. web-ifc's writer for saving an imported IFC back with edited properties, checked by IfcOpenShell's validator:
   yes or later.

## 9. Open, risks, threats to validity

- The clone at 643d24e is ahead of npm 3.6.1; the recipe's calls were measured on npm 3.6.1 (e2), so they hold for
  the pinned build. The "Unreleased" changes (IfcSplitter's async API) are not in the pin (S: from the CHANGELOG).
- One fixture file; the 13-file comparison is WO-09's own test.
- Coverage of web-ifc's kernel is read from case labels; a missing case means "not drawn" by inference, not by test.
- geokernel's default registration (0.0.80) changes boolean output and sets globals (`globalThis.__morphBool`,
  `__morphBoolStats`); not measured here.
- No second reader yet: every P fact in sections 4 and 5 is to be re-checked by an independent agent before WO-09.

## 10. References

- ThatOpen/engine_fragment @ 643d24e, https://github.com/ThatOpen/engine_fragment: files listed in section 3. P.
- ThatOpen/engine_web-ifc @ 9ab7d5c, https://github.com/ThatOpen/engine_web-ifc: files listed in section 3; commits
  2619f4c9 (0.0.79), 5ba24671 (0.0.80), c4a65a31 (0.0.81), b6cf0ce2 (after 0.0.81). P.
- npm: web-ifc 0.0.81 (MPL-2.0, published 2026-11-23), @thatopen/fragments 3.6.1 (MIT, 2026-11-08; peers three
  >=0.182.0, web-ifc >=0.0.77). Read 2026-11-28. P.
- This repository at the session's HEAD: the files listed in section 3. P.
