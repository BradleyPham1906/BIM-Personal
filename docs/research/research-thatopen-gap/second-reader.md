# V206 That Open: the second reader's check

Date: 2026-11-28. Reader: an independent second reader (Claude, a separate agent), per
`docs/research/research-protocol.md`. Scope: every fact the V206 code relies on, re-checked against the installed,
pinned packages (`tools/thatopen/node_modules`: @thatopen/components 3.6.0, components-front 3.6.1, fragments 3.6.1,
web-ifc 0.0.79, three 0.186.1) and by re-running the measurements. Nothing in the repository was edited except this file.

## What was read

- `src/js/engine/io/thatopen-runtime.js` (all 185 lines), `src/js/engine/io/thatopen-review.js` (all 311 lines), the
  That Open helpers in `src/js/engine/io/ifc-review.js` (lines 1-185), `src/js/engine/io/ifc-full.js` 115-215,
  `src/js/engine/testing/hooks-drawing.js` 446-465, `tools/thatopen/build_thatopen.mjs` (all),
  `runtime/thatopen/3.6.0/LICENSES.txt` (headings and the entries named below).
- Installed dist and type files (file:line below): `@thatopen/fragments/dist/index.d.ts`,
  `.../Importers/IfcImporter/index.mjs`, `.../IfcImporter/src/properties/property-processor.mjs`,
  `.../IfcImporter/src/geometry/ifc-file-reader.mjs`, `.../IfcImporter/src/classes.mjs`, `.../Utils/ifc-utils.mjs`,
  `.../Utils/worker-utils.mjs`, `.../FragmentsModels/index.mjs`, `.../FragmentsModels/src/model/coordinates-manager.mjs`,
  `.../src/model/edit-manager.mjs`, `.../src/virtual-model/virtual-fragments-model.mjs`,
  `.../virtual-model/virtual-controllers/virtual-properties-controller.mjs`,
  `.../virtual-model/virtual-helpers/{coordinates-helper,geometry-helper}.mjs`;
  `@thatopen/components/dist/index.{d.ts,mjs}`; `@thatopen/components-front/dist/index.{d.ts,js}`;
  `three/src/renderers/WebGLRenderer.js`, `three/src/renderers/shaders/ShaderChunk/clipping_planes_fragment.glsl.js`.
- Upstream clone, read as text only: `toe/engine_web-ifc` @ 9ab7d5c (package 0.0.82, three versions after the pinned
  0.0.79, so S for 0.0.79), `src/cpp/web-ifc/geometry/IfcGeometryProcessor.cpp` 2318-2383.
- IfcOpenShell 0.8.5 `ifcopenshell/guid.py`, read as text from `runtime/ifcos/0.8.5/ifcopenshell-0.8.5-...whl` (unzip -p),
  not imported; its `compress`/`expand` transcribed into a scratch script.

## What was run (scripts in the session scratchpad, not committed)

- `node docs/research/experiments/thatopen/e02/probe.mjs` on 2x3-arch.ifc and 43-bridge.ifc (Chromium 1243, SwiftShader).
- `ENGINE_ORDER=cc-first node docs/research/experiments/thatopen/e03/run.mjs <dir> http`, dir = symlinks to 2x3-arch,
  fzk-haus, schependomlaan (SHA-256 prefixes c4db65ba847f6b36, 70cc8ff245fc0894, 2c3565ca1904f2aa).
- `f4.mjs`: the built `canvas_v10.html` (`build_app.py --check` passed: e0d48799...) over http, `window.__a3dToe.read`
  on schependomlaan, fzk-haus, 2x3-arch, advanced_model; storeys, coord, first part; every request the page made logged.
- `f3.mjs`: the same reader, property and quantity sets of fzk-haus and 2x3-arch.
- `align.mjs`: the reader's own load settings, then whether `getItemsGeometry(part)[g]` belongs to `part[g]`, on 9 files
  (4-wallopen, 2x3-arch, 43-road, 43-bridge, fzk-haus, dental_clinic, FM_ARC_DigitalHub, schependomlaan, advanced_model).
- `guid_ref.py` (IfcOpenShell's algorithm) on 207 vectors, `guid_app.mjs` the app's codec through
  `tests/unit/helpers/engine.mjs loadEngine()`; the same script ran `bimToeUnit` on 6 synthetic headers and the 13 files.
- `node tools/thatopen/build_thatopen.mjs --check` (passed), `python3 tools/check_runtime.py` (passed, 57 files),
  `openssl dgst -sha256 -binary | base64` of the three runtime files against `BIM_TOE.files[].sri` (all three equal).

## Verdicts

| Fact | Verdict | Evidence |
|---|---|---|
| F1 getItemsGeometry: per item a list of {positions, indices, transform Matrix4}; transform x positions is metres, +Y up, moved by getCoordinates()'s base; base has the meaning of web-ifc's COORDINATE_TO_ORIGIN shift | CONFIRMED | Type: fragments `index.d.ts` 1747 (`Promise<MeshData[][]>`), 4364-4380 (MeshData: transform THREE.Matrix4, indices?, positions?, localId?); built from `geometry-helper.mjs` 6-26 (`sample.transform.clone()`). three's Matrix4.elements is column-major; e02's first transform has its translation at 12-14 (`[0,0,1,0,1,0,0,0,0,1,0,0,-0.15,-0.45,0.075,1]`), as bimToeMesh reads it. Re-run of e02/probe.mjs: 2x3-arch (a MILLI file) box 38.5 x 7 x 24.3: metres, height on Y. geoBox - webifcBox: min and max both (-2.400, -1.150, 3.375); coord - webifcCoord translation (-8+5.6, -0.9-0.25, 6.375-3) = (-2.400, -1.150, 3.375). 43-bridge: geoBox - webifcBox (7.004, -3.610, -0.552) at min and at max; coord - webifcCoord (7.004, -3.610, -0.552). web-ifc's sign (upstream @9ab7d5c, S for 0.0.79): `IfcGeometryProcessor.cpp` 2329/2339 `_coordinationMatrix = glm::translate(-firstPoint)`, 2360 `transformation = _coordinationMatrix * newMatrix`, so P_webifc = P_ifc + t and therefore P_thatopen = P_ifc + base, which is what `coord` (translation = base) states. |
| F2 spatial tree alternates category nodes {category, localId null} and item nodes {localId, category null}; a storey's localId is on the child of the IFCBUILDINGSTOREY category node | CONFIRMED | `index.d.ts` 5934-5941 (SpatialTreeItem {category: string\|null, localId: number\|null, children?}); e02 re-run, 2x3-arch: `{"category":"IFCBUILDINGSTOREY","localId":null,"children":[{"category":null,"localId":36,...` and getItemsData(36) is the IFCBUILDINGSTOREY "00 groundfloor". f4: schependomlaan's 6 storeys, fzk-haus's 2, advanced_model's 4 found by bimToeTree with their names. |
| F3 getItemsData values are {value, type}; IsDefinedBy gives property sets with HasProperties (NominalValue...) and quantity sets with Quantities | CONFIRMED | `index.d.ts` 3628-3635 (ItemAttribute {value, type?}), 3731-3732, 3879-3902 (ItemsDataConfig), 1811-1826 (the IsDefinedBy example). e02 re-run: `"Name":{"value":"kitchen","type":"IFCLABEL"}`, `_localId`, `_guid`, `_category` as {value}. f3: fzk-haus Pset_StairCommon rows HandicapAccessible No, FireExit Yes (NominalValue); quantity sets BaseQuantities (Height 2.01, Width 0.885, Area 1.77885...), 2x3-arch Qto_WallBaseQuantities (Length 1800, NetVolume 1.26926) read through Quantities and *Value. Note: IsDefinedBy also returns type objects and, in 43-bridge, a node with `_category {value:null}`; bimToeSets skips both (no rows), which is right. Property and quantity values are in the file's units (Length 1800 is mm): That Open does not convert them. |
| F4 Storey Elevation is in the file's length unit, so bimToeUnit is needed | WRONG | That Open replaces it. `IfcImporter/index.mjs` 123 `replaceStoreyElevation = true` (default), documented `fragments/dist/index.d.ts` 3080-3085: "Whether to replace the IfcBuildingStorey.Elevation with the absolute storey elevation ... it is always given in meters". `property-processor.mjs` 98-100 sets the factor, 309-315 writes `Elevation = absoluteZ * _lengthUnitsFactor`. Measured (f4, the built app): schependomlaan (MILLI; file elevations -1000, 0, 3000, 6000, 9000, 12000) gives elev -0.01101, -0.01001, -0.00701, -0.00401, -0.00101, 0.00199 with base[1] -0.01001, i.e. That Open's value is -1, 0, 3, 6, 9, 12 (metres) and `e*unit` scales it a second time. advanced_model (MILLI, 3800 mm): -0.09037 = 3.8 x 0.001 - 0.09417. fzk-haus (METRE, 2.7) and 2x3-arch (elevation 0) are right only because the unit is 1 or the value 0. Every millimetre file's levels collapse to within 12 mm of each other. e03's committed table never showed `levels`; my re-run shows `levels TO 0` only because cc-ifc ran first and made the levels (ifc-full.js 228 skips a level of the same name), so e03 cannot catch this. The research note already states it (`research-thatopen-gap/fragments-webifc.md` 105). Fix: in thatopen-runtime.js 141, `elev: e + (+base[1]\|\|0)`, without `*unit`; or set `imp.replaceStoreyElevation = false` in the instanceCallback and keep `*unit` (then it is the attribute, relative to the building, as cc-ifc's `bimIfcStoreys`). The first keeps That Open's own factor, which (`Utils/ifc-utils.mjs` 35-65) knows only METRE, FOOT and the MILLI/CENTI/DECI prefixes and takes the last LENGTHUNIT of every assignment, so an inch file would come out in inches; the second keeps bimToeUnit's fuller table. Also note the meaning differs between the engines: That Open's is the absolute placement Z (sum of the placement chain's Z, rotations ignored, `property-processor.mjs` 271-294), cc-ifc's the attribute. |
| F5 IfcLoader.load(data, coordinate, name, {instanceCallback}) passes the IfcImporter, whose classes.elements is a set of web-ifc type codes; adding IFCSPATIALZONE and IFCROADPART makes them meshed | CONFIRMED | components `index.mjs` 11289-11316: `new FRAGS.IfcImporter()`, `config?.instanceCallback(serializer)` before `serializer.process`; `index.d.ts` 4064-4110. fragments `IfcImporter/index.mjs` 101 `elements: new DataSet([...ifcClasses.elements])` (per instance; DataSet extends Set, `index.d.ts` 630); `classes.mjs` lists WEBIFC.* codes; `ifc-file-reader.mjs` 208-211 meshes only `modelClasses.filter(type => classes.elements.has(type))`. In classes.mjs' elements: IFCSPATIALZONE, IFCROADPART, IFCRAILWAYPART, IFCMARINEPART, IFCFACILITYPARTCOMMON absent; IFCBRIDGEPART present (adding it is harmless); IFCSPACE and IFCOPENINGELEMENT present (hence BIM_TOE.skip). web-ifc 0.0.79 has all six as numbers (IFCSPATIALZONE 463610769, IFCROADPART 550521510, ...). e03 43-road AGREE 65/65 (committed). |
| F6 autoSetWasm false never fetches from unpkg; getWorker() with fragments/inline imported needs no network; toClassicWorker exists | CONFIRMED | components `index.mjs` 11235-11239 (setup) and 11294-11296 (load) call autoSetWasm only when `settings.autoSetWasm`; the unpkg fetch is inside autoSetWasm. fragments `FragmentsModels/index.mjs` 155-163: with `_inlineWorkerB64` set the worker is a blob, the unpkg branch (164-) is not reached; `inline.mjs` calls `registerInlineWorker(...)`, and the build imports `@thatopen/fragments/inline` (build_thatopen.mjs, stdin); the built bim-thatopen.min.js contains `registerInlineWorker("dmFy...")`. `Utils/worker-utils.mjs` 1-8: toClassicWorker fetches the blob, strips the `export {}` and makes a new blob. Measured: f4's four reads made no request other than 127.0.0.1 (none to unpkg, jsdelivr or the .invalid wasm address, which the shim answers). Not measured: the Review view's own run. The bundle also holds a jsdelivr URL (opentype.js, three's TTFLoader) reached only from components-front's FontManager.load (`index.js` 13857-13883, DrawingEditor fonts), which the app never calls. |
| F7 SimplePlane's plane is setFromNormalAndCoplanarPoint(normal, origin); three clips negative signed distance; the cut-away side is (p - origin)·normal < 0; the code passes the negated normal to bimTorClip | CONFIRMED (with a caveat) | components `index.mjs` 20264 (constructor) and 20288-20297; Clipper.create -> createPlaneFromIntersection 20854 `newPlane(world, intersect.point, worldNormal.negate())`. three `WebGLRenderer.js` 254-255: "Points in space whose dot product with the plane is negative are cut away." bimTorClip(p, {n:-normal, p:origin}) is (p-o)·(-n) > 1e-9, i.e. (p-o)·n < 0: right. Caveat: after the user drags a plane, SimplePlane.update (20300-20306) rebuilds `three` from `_helper.position`; `origin` is not updated (only 20294, 20349 copy it), so the report on a later plane uses stale origins. `pl.three.distanceToPoint(p) < 0` would always match what is drawn. |
| F8 the ES5 GUID codec matches IfcOpenShell's guid.compress/expand | CONFIRMED | 207 vectors (all zeros, all ones, 0123...cdef with dashes, 8000...0001, c0ffee..., 3a7f..., ff..00, 200 seeded random): bimTorGuidFromHex = compress and bimTorGuidToHex = expand on all 207, every result bimTorGuidValid. 0x0 -> `0000000000000000000000`, all ones -> `3$$$$$$$$$$$$$$$$$$$$$`. Bad inputs (3 chars, a first character '4', 31 hex digits) give null. |
| F9 bimToeUnit's SI prefixes and foot/inch factors | CONFIRMED | The 16 prefix names equal web-ifc 0.0.79's `IFC4.IfcSIPrefix` members exactly (EXA ... ATTO) (P); the powers of ten are the SI prefixes (S: the SI Brochure, from knowledge, not fetched today). Foot 0.3048, inch 0.0254, yard 0.9144, mile 1609.344 are the 1959 international definitions (S). Runs: MILLI 0.001, CENTI 0.01, no prefix 1, 'FOOT' 0.3048, 'inch' 0.0254, the project's assignment chosen over others; the 13 files: MILLI where the file says so, 1 for fzk-haus, dental_clinic, FM_ARC_DigitalHub (its DECI unit is not in the project's assignment). Limits: the factor comes from the unit's name, not its ConversionFactor; 'US SURVEY FOOT' gives 0.3048 (the survey foot is 1200/3937 = 0.3048006). |
| F10 e03 on 2x3-arch, fzk-haus, schependomlaan: AGREE, same counts | CONFIRMED | Re-run (http, cc-first): `agree on 3 of 3; page errors: none`. 2x3-arch 12/12 elements, 12 GlobalIds, 1130/1130 tris, box 38.543 x 7 x 24.286; fzk-haus 83/83, 83 GlobalIds, 21636/21684, box 18 x 7.318 x 16; schependomlaan 3504/3504, 3504 valid GlobalIds, 260942/261457, box 23.95 x 15.056 x 24.465: identical to e03/results.txt. |
| F11 every package in LICENSES.txt is under a licence the rule allows | CONFIRMED, two gaps in the credits | 31 packages: MIT (most), ISC (earcut, inherits, lru-cache 11.1.0: its package.json and LICENSE say ISC), Apache-2.0 (flatbuffers 25.2.10), MPL-2.0 (web-ifc 0.0.79, its own file bim-webifc.min.js), (MIT AND Zlib) (pako 2.1.0), (MIT OR GPL-3.0-or-later) (jszip 3.10.1, used under MIT). Zlib is not named in CLAUDE.md's list but is a permissive licence compatible with Apache-2.0 distribution; worth one line from the owner. Gaps: (1) jszip ships `LICENSE.markdown`, which build_thatopen.mjs's file list (LICENSE, LICENSE.md, LICENSE.txt, license, LICENCE, license.md) misses, so LICENSES.txt has only "No licence file in the package" for it, though the MIT text exists: add `LICENSE.markdown`. (2) isarray and @nodable/entities ship no licence file at all; their declaration is recorded. The build's allowed pattern also admits BlueOak-1.0.0 and 0BSD, which the rule does not name; no current package uses them. |

## Other things found in the two new files

1. getItemsGeometry is read by position (`G[g]` for `part[g]`, thatopen-runtime.js 149-151). In the source a localId can
   map to several geometry items (`virtual-properties-controller.mjs` 150-167, 985-996: `_localIdsToGeometryIds` holds
   arrays, unknown ids are skipped), so the result can be longer or shorter than the ids. Measured on 9 files (up to
   6401 ids): every entry's MeshData.localId equals its id, none longer or shorter. Safe today; grouping by
   `MeshData.localId` would not depend on it.
2. bimRvwSectionText (thatopen-review.js 185-197) says "have their centre cut away", but `model.getPositions()` returns
   each item's global transform position (`coordinates-helper.mjs` 2-16, `coordinates-manager.mjs` 43-56), the
   placement origin, not the centre of its geometry. With the stale `origin` of F7, the count can differ from what the
   view shows. Either say "placement point" or use the items' boxes; and use `pl.three`.
3. The Review view loads models without the instanceCallback (thatopen-review.js 158), so the IFC4.3 facility parts and
   spatial zones the import draws (F5) are not drawn in Review.
4. bimRvwProps labels `ContainedInStructure[0]` "Storey" (thatopen-review.js 80-84); the container can be an IfcSpace
   (e02: the kitchen is contained in the IFCSPACE "living room"), so the label can be wrong.
5. bimToeMesh (ifc-review.js) pushes every index, including a trailing one or two when `indices.length` is not a
   multiple of 3; harmless for That Open's triangle buffers, but the two loops are the same as one.
6. Measuring (pointAt, thatopen-review.js 240-250) reads `tool.lastPick.point`; `lastPick` is protected in the types
   (`components-front/dist/index.d.ts` 2947) and set from the vertex picker (`index.js` 12585); its shape was not
   checked here, and on a miss the code waits 800 ms and goes on. Not a WRONG, unverified.
7. Checked and right: SRI strings equal the files' SHA-256; `build_thatopen.mjs --check` and `check_runtime.py` pass;
   Hider.set/isolate, Highlighter.highlightByID and config.selectEnabled, OrthoPerspectiveCamera.fitToItems,
   Clipper.create/delete/deleteAll, Measurement create/endCreation/cancelCreation, Area.points (DataSet) and .value,
   Line.value exist with the signatures the code uses (`components/dist/index.d.ts` 3636, 3643, 5289;
   `components-front/dist/index.d.ts` 2074, 2122, 2553-2554, 3054-3055, 167-196, 2564-2600).

## Open

- The Review view was not run in a browser by this reader (its network requests, picking, measuring, touch).
- F9's SI and foot/inch values are S (definitions known, not fetched today).
- web-ifc's coordination sign was read in 0.0.82's source, not 0.0.79's; the measurement (F1) covers the pinned build.

## Taken in (Claude, 2026-11-28)

- F4: confirmed in the source (`IfcImporter/index.mjs:123`, `property-processor.mjs:309-315`). The import now sets
  `replaceStoreyElevation = false` (`bimToeImporterSetup` in `io/thatopen-runtime.js`), so Elevation is the file's
  attribute and the import's unit factor applies once, as cc-ifc's reader does. e03 now compares the levels too, each
  measured from its engine's own shift: on the six files tried first (millimetre and metre), every storey agrees to
  the millimetre (schependomlaan -1, 0, 3, 6, 9, 12 m on both engines).
- F11: `LICENSE.markdown` added to the names looked for, so jszip's text is in `LICENSES.txt`; BlueOak-1.0.0 and 0BSD
  removed from the allowed list; pako's zlib licence put to the owner (research-thatopen-gap.md part 11).
- F7: the section report reads each plane from its three.js plane (current after a drag) and says "placement point".
- Geometry: parts are grouped by their own `localId`, the list's order only where a part has none.
- Review: models load with the same importer setup (facility parts); the data's row says "Contained in" with the
  class, so a space is named as one.
- Not changed: the jsdelivr address inside components-front's font loader (never called by the app; noted as a risk).
