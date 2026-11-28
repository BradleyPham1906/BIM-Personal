# Authoring and standards: the element model against openBIM practice

Date: 2026-11-28. Area: authoring and standards (one part of the That Open gap study).

Pinned sources read (read-only clones, no code run from them):

| Source | Commit | Date of commit | Licence | Read |
|---|---|---|---|---|
| engine_clay (`packages/clay/src`) | 6f14cbe14c8720ddb0678d312c8628b847238fe3 | 2024-10-09 | MIT | every file under core/, elements/, geometries/, general/, utils/ifc-utils.ts, utils/math-utils.ts; primitives/ skimmed (drawing helpers, no IFC) |
| engine_templates | 1b305244d5b2c42dc34639823fd87d734b2aab6b | 2026-09-29 | MIT | README, templates/vanilla (main.ts, package.json, ui-templates, bim-components) |
| engine_web-ifc (schema only, as a reference for enum values) | 9ab7d5c | 2026-11-26 | MPL-2.0 | src/ts/ifc-schema.ts, IFC4 namespace |
| This repository | 0abf980 | 2026-11-27 | Apache-2.0 | src/js/engine/bim, io/ifc-save.js, io/ifcos-worker.js, io/ifcos-py.js, src/py/bim_ifcos.py, properties/palette.js, bim/classification.js, assets/family-library.js (ranges only) |
| IfcOpenShell 0.8.5 wheel, as committed in `runtime/ifcos/0.8.5/` | pinned by MANIFEST.json | | LGPL-3.0 (file as a whole GPL-3.0, CGAL) | api/ module signatures and docstrings, guid.py, util/schema/Pset_IFC4X3.ifc, read as text from the wheel (zip), not imported or run |

Levels: P = read in the primary source at the cited lines; S = dependable secondary, gap said; U = pointer only, never used in a recommendation. Every fact below is P unless marked.

## 1. Summary

Clay is a small, unfinished authoring layer over web-ifc: it writes IFC4X3 entities straight into a web-ifc model as they are drawn. It gets three things right that this app does not yet do: every element has an IFC class and a GlobalId from the moment it is created, each element is made from a type object, and openings are real voids (`IfcRelVoidsElement`) that the host's geometry subtracts. It also has a useful hosting idea (openings remember their distance along the wall). But it stops there: it never writes `IfcRelDefinesByType`, `IfcRelFillsElement`, materials, property or quantity sets, classification, a building or storeys, or georeferencing, and several of its entities are wrong (section 4). Its GlobalIds are 36-character UUID strings, not IFC's 22-character form. It is pinned to web-ifc 0.0.59 and fragments 2.2 and has not changed since 2024-10-09. It is a source of methods, not a dependency.

engine_templates is a viewer starter (load IFC, highlight, clip, measure, viewpoints, an element data table). It shows no authoring workflow at all.

This app already writes better IFC than Clay at save time: IfcOpenShell in the worker builds Project, Site, Building and storeys, walls, slabs, columns, doors and windows with true voids and fills, and imported property sets (bim_ifcos.py:54-86, 195-285, 319-337). The gap is that the app's element model is not IFC-native: the IFC class is chosen at save time from `bim.type`, nothing authored has a GlobalId that survives a second save, types are not written, materials and standard property sets are not written, wall joins exist only as moved endpoints, rooms are not spaces, classification has no system, and the site's location is not written.

The recommended path is one consistent pattern: keep the app's own JSON model as the source of truth, give each element, type and spatial record a small `ifc` identity record at creation (GlobalId, class, predefined type), keep relations as data on the records (type, joins, host, fills, classification), and serialize through the IfcOpenShell adapter the app already ships (reuse, R). Clay's methods are ported only where they are geometry the app lacks (the opening's station along the wall). Eight phases, OB1 to OB8 below, each a set of small pure functions with unit tests, then one IfcOpenShell adapter change per phase.

## 2. Question and hypotheses

Question: what must change in the app's element model so that a model authored here is, on save, what an openBIM reviewer expects from Revit-level authoring (IFC4 Reference View-like content), and which of Clay's methods are worth taking?

- H1: Clay's element model is IFC-native at creation (class, GlobalId, type) and can be ported. Result: partly true. Class and type at creation, yes; GlobalId format and most relations, no (section 4).
- H2: the app's IFC writer already covers spatial structure and voids/fills. Result: true for one building (bim_ifcos.py:74-82, 273, 282); false for several buildings and spaces.
- H3: the app loses GlobalIds between saves for authored elements. Result: true (section 5.4).
- H4: IfcOpenShell 0.8.5, as pinned, has every API needed for types, material layer sets, quantities, path connections, classification and georeferencing, so none of it has to be written by hand. Result: true at the signature level (section 6); behaviour still to be measured (section 10).

Falsifiers sought: a Clay file writing `IfcRelDefinesByType` or `IfcRelFillsElement` (none found by grep over src, section 4); an app code path that stores the GlobalId IfcOpenShell returns (none found: `bimIfcExportText` keeps only `written`, `left`, `summary`, ifcos-worker.js:152-161).

## 3. Method and search log

1. `find packages/clay/src -name '*.ts'` and `wc -l` (86 files, 7006 lines; 2 000 of them primitives with no IFC).
2. Full read of core/, general/, elements/ (walls with cornerer and nester, slab, opening, window), geometries/ Extrusion, HalfSpace; grep for `new IFC.` in curtain wall, member, plate, furniture, Brep, MappedItems, profiles.
3. Falsification grep over Clay for `IfcRel|IfcMaterial|Pset|Qto|IfcClassification|IfcUnit|IfcMapConversion|IfcBuildingStorey|IfcSpace|PredefinedType`.
4. engine_templates: README, package.json, main.ts, ui-templates, grep for `OBC.`/`CUI.`.
5. The app: `grep -rn` for element creation (`type:'wall'` and kin), `bimType|ifcClass|ifcType`, `guid`, `psets`, `Pset_|Qto_`, `LoadBearing|IsExternal|PredefinedType`, classification, georeferencing state, unit state; then ranges of the files named in the header.
6. IfcOpenShell 0.8.5: the committed wheel opened as a zip with `python3 -I`; presence of api modules, the `def` signatures, the `assign_type` body around material usages, guid.py, and the shipped buildingSMART property set templates.
7. Experiment e1 (section 8): the standard property and quantity names for the app's element classes, parsed from the templates inside the pinned wheel.

## 4. Clay: how it builds IFC (method notes)

All paths are under `engine_clay/packages/clay/src/`.

### 4.1 Core

- Model (core/Model/index.ts). Wraps one web-ifc `IfcAPI` model created with schema IFC4X3 (lines 72-83). `set` writes a line (89-91), `delete` deletes a line and optionally the handles it references (98-124), `get` resolves a handle (130-138). It keeps one plain `IfcRepresentationContext` labelled Default/Model (79-82), which is what every shape uses (utils/ifc-utils.ts:46-48), not a geometric context with a Body subcontext. `update` saves the whole model to bytes, disposes the API, re-inits and reopens it (143-156, with a "fix memory leak" note); it is called after every boolean change. This is the main reason the architecture does not scale: every void costs a full serialize and reparse.
- ClayObject (core/Object/index.ts:7-26): holds the model and an `attributes` line object; `update` rewrites it.
- ClayElement (core/Elements/Element/index.ts). Holds a type, geometry ids and a map of void relations (25-35). `addSubtraction` refuses anything that is not an `IfcFeatureElementSubtraction` (103-107), creates `IfcRelVoidsElement` with a fresh GlobalId, relating the host and related the opening (109-116), writes it and calls `Model.update` (118-123). `removeSubtraction` deletes that relation (130-136). `updateIfcElement` writes the object's position and rotation into its `IfcLocalPlacement`'s `IfcAxis2Placement3D` (198-210). Placements are never relative to a storey (PlacementRelTo is null, ifc-utils.ts:28-35).
- ClayElementType (core/Elements/ElementType/index.ts:11-51): a type is the manager of its instances (`addInstance`, `deleteInstance`), owning their geometries and fragments. This is a scene-graph idea, not an IFC relation: nothing writes `IfcRelDefinesByType` (falsification grep, step 3).
- StaticClayElementType (core/Elements/StaticElementType/index.ts:9-72): all instances share one `IfcProductDefinitionShape` held by the type (line 20). Instances point at that same shape as their own Representation (for example elements/Windows/SimpleWindow/src/index.ts:23-37 passes `type.shape`). IFC's own mechanism for shared type geometry is `RepresentationMaps` on the type and `IfcMappedItem` on the instance; Clay has a RepresentationMap class (geometries/MappedItems/index.ts:13-52) that nothing uses (grep: no reference outside its folder).
- DynamicClayElementType (core/Elements/DynamicElementType/index.ts:9-73): one geometry and fragment per instance.
- Geometry booleans (core/Geometry/index.ts:52-98): `addSubtraction` wraps the current solid in `IfcBooleanClippingResult(DIFFERENCE, current, cutter)` and keeps a linked list of clippings so one can be removed later (103 on).

### 4.2 Elements

| Clay element | Type entity (file:line) | Predefined type | Instance entity (file:line) | Geometry | Notes |
|---|---|---|---|---|---|
| SimpleWall | IfcWallType, Walls/SimpleWall/index.ts:22-35 | STANDARD (32) | IfcWall, src/simple-wall.ts:75-87 | Extrusion of a RectangleProfile, length by width by height (64-68, 90-98) | Thickness is a type attribute (`width`, index.ts:15); height and the two end points are per instance (23-27). |
| SimpleSlab | IfcSlabType, Slabs/SimpleSlab/index.ts:15-26 | FLOOR (25) | IfcSlab, src/index.ts:33-45 | Extrusion of an ArbitraryClosedProfile (23) | The type is never written to the model: no `model.set` after line 26. |
| SimpleOpening | plain IfcElementType, Openings/SimpleOpening/index.ts:40-52 | none | IfcOpeningElement, src/index.ts:21-33 | Shared static box (30-34) | IFC has no IfcOpeningElementType in use here; a generic IfcElementType is abstract-ish and not meaningful. |
| SimpleWindow | IfcWindowType, Windows/SimpleWindow/index.ts:76-90 | WINDOW, partitioning NOTDEFINED (86-87) | IfcWindow, src/index.ts:23-39 | Four frame extrusions (35-74) | Declared as IfcFurnishingElementType and IfcFurnishingElement in TypeScript (12; src 9) while constructing window entities. No filling relation to any opening. |
| SimpleCurtainWall | IfcCurtainWallType, CurtainWalls/SimpleCurtainWall/index.ts:76-90 | NOTDEFINED (86) | IfcCurtainWall, src/index.ts:23-35 | Its members and plates' bodies collected into one shape (73-74) | Makes a new member type or plate type for every single member and plate (around 105-150); members and plates are never aggregated to the curtain wall (no IfcRelAggregates). |
| SimpleMember | IfcMemberType, Members/SimpleMember/index.ts:17-28 | MULLION (15) | IfcPlate, src/index.ts:38-49 | Extrusion | Wrong class: a member instance is written as IfcPlate. The type is never written (no `model.set`). |
| SimplePlate | IfcPlateType, Plates/SimplePlate/index.ts:17-28 | CURTAIN_PANEL (15) | IfcPlate, src/index.ts:34-46 | Extrusion | Type never written. |
| SimpleFurniture | IfcFurnishingElementType, Furniture/SimpleFurniture/index.ts:29-39 | none | IfcFurnishingElement, src/index.ts:21-32 | Brep (21-24) | Type never written. |

Every Name, Description, ObjectType and OwnerHistory of these is null (for example simple-wall.ts:76-80).

### 4.3 Wall corners and nesting

- Cornerer (Walls/SimpleWall/src/simple-wall-cornerer.ts). A corner is configured per pair, with which face of wall 1 to meet (center, exterior or interior), which end of wall 2 to move, and optionally a cut (5-13, 27-41). `extend` intersects wall 2's axis with the chosen plane of wall 1 and moves the chosen end there, pushed on by wall 2's own width ("auto" offset, 98-107). With a cut, it adds an `IfcHalfSpaceSolid` (geometries/HalfSpace/index.ts:80-100) as a boolean clipping of wall 2's body, placed on wall 1's plane in wall 2's local frame (110-145). The join is kept only in this object's in-memory map; it is not an IFC relation (`IfcRelConnectsPathElements` is never written) and is not saved.
- Nester (Walls/SimpleWall/src/simple-wall-nester.ts). When an opening is added with `nest`, its position is projected onto the wall's vertical plane and stored as a signed distance from the wall's start point along its direction (14-43). On every wall update each nested opening is put back at start plus distance times direction and given the wall's rotation (49-62), so openings follow a moved or turned wall. This is the one Clay method this app lacks and can port as a pure function (OB7).

### 4.4 Spatial structure, project, units

- Project (general/Project/index.ts): writes an organization "That Open Company", an empty person, an application "CLAY" and an owner history (18-59); a geometric representation context, 3D, precision 1e-5 (61-72); units (74-92); the project (94-106); and an aggregation holder for its children (108-112). The volume unit is a defect: it is built with AREAUNIT and SQUARE_METRE (86-90), so the file has two area units and no volume unit. The project's context list holds this geometric context, while the shapes use the Model's other plain context (section 4.1).
- Site (general/Site/index.ts:19-50): an IfcSite with composition ELEMENT, no reference latitude, longitude or elevation (26-33 all null), added to the project's `IfcRelAggregates` (38), with its own aggregation holder and its own `IfcRelContainedInSpatialStructure` holder.
- SpatialChildren (general/SpatialChildren/index.ts:15-50) and ElementChildren (general/ElementChildren/index.ts:15-50): one relation each, the related list edited in place by express id.
- There is no Building, no BuildingStorey and no Space class. The wall example puts walls directly in the site (Walls/SimpleWall/example.ts:62-63).

### 4.5 Identity and placement utilities

- GlobalIds: every root entity is given `uuidv4()` directly (for example simple-wall.ts:76, Element/index.ts:110). IFC's GlobalId is a 22-character base-64 compression of the 128-bit id (IfcOpenShell guid.py:28, `compress` at 85). Clay's 36-character strings are not valid GlobalIds. Each id is made once and kept in the object's `attributes`, so it is stable while the object lives, but the format is wrong and nothing restores it after a reload.
- ifc-utils.ts: `direction` and `point` (7-21), `localPlacement` with no PlacementRelTo (23-36), `productDefinitionShape` and `shape` with no RepresentationIdentifier or RepresentationType (38-48), `setAxis2Placement` writing position and basis from a three.js object in IFC axes (50-80, through math-utils.ts:18-28, three's y up to IFC's z up).

### 4.6 engine_templates

templates/vanilla/package.json pins @thatopen/components, components-front, fragments, ui and ui-obc at ~3.4.0, three 0.182.0, web-ifc 0.0.77. main.ts builds a world, the fragments worker, the IFC loader (106-115), highlighter (117-127), clipper, length and area measurement (141-180), and a layout grid; ui-templates/sections hold a models list, viewpoints and an element data table (elements-data.ts:19, `CUI.tables.itemsData`). There is no authoring, no IFC writing and no Clay. Its only lesson for this area is that That Open's current stack treats IFC as an input to view, and authoring is left to the app.

## 5. This app's element model and IFC save (what we do)

### 5.1 Elements at creation

Elements are plain records in `A3D.objs` with a `bim` sub-record whose `type` names the kind: wall (bim/import-compliance.js:136-157 builds it, 179-193 creates the object with a type id), floor and ceiling (bim/ceiling-floor-profile.js:54, 85), column (bim/columns-openings.js:136), door and window as `t:'opening'` markers holding `hostWallId`, an absolute `center`, width, height and sill (columns-openings.js:405-433), beam (bim/section-profiles.js:130, 146), roof (bim/roofs.js:382, 392), stair (bim/stairs.js:494), footings with a `hostId` (bim/footings.js:100-118), rooms as `t:'room'` with no `bim` at all (bim/room-colour-fill.js:170-174). No record carries an IFC class, a predefined type or a GlobalId at creation (grep for `guid` assignments finds only import paths: io/ifc-full.js:116, 220; io/ifc-editable.js:83; io/sketchup-import.js:214, 279).

`bimCarryBim` copies every field of the old record that a rebuild does not set (bim/import-compliance.js:169-177), so a field added to `bim` survives rebuilds, joins and transforms without touching each tool. This is what makes an `ifc` identity sub-record cheap to add.

### 5.2 Types

`TYPE_CATS` (bim/type-instance-params.js:115-123) gives types for wall, floor, ceiling, column, beam, isolated footing and wall foundation, each with type parameters (thickness; width and depth; and so on) and one material name (for example walls, 31-34). Type edits propagate by rewriting every instance (comment at 19-29, `bimApplyTypeToInstances` 651). `bimEnsureObjType` matches or makes a type for an untyped object (575-599). Types have ids but no GlobalId, no IFC class and no predefined type, and are not written to IFC.

### 5.3 Materials, classification, units, location

- Materials: one material name per type (`params.material`) and an instance `materialName` (type-instance-params.js:389-391); no layers. Nothing is written to IFC.
- Classification: a project list of `{id, code, description}` and an object's `classId` (bim/classification.js:27-40, 67-73). No system name or edition (Uniclass 2015, OmniClass), no URI. Not written to IFC (`bimIfcSaveBase` reads no classId, io/ifc-save.js:27-41).
- Units: display units only (properties/palette.js:58-62); the model is in metres, and the IFC file states SI metre, square metre and cubic metre (bim_ifcos.py:60-65), which is correct.
- Location: the site's latitude and longitude live in `A3D.site.sun` (map/cityjson.js:255; site/sun-position.js:142), true north in `A3D.site.trueNorth` (site/alignment-profile.js:655), and a UTM forward transform and EPSG code exist (map/cityjson.js:25-53). None of it is written to IFC (no georeference call in bim_ifcos.py; grep).

### 5.4 IFC save

- The JS side turns each element into plain data (io/ifc-save.js): a base with id, name, kept GlobalId only if it is already 22 characters, and a `BIM_Personal` set plus imported sets (27-41); straight walls split into one record per segment, where every segment after the first drops the GlobalId and gets id `<id>#i` (67-86, line 80); floors and rectangular columns as prisms (88-104); doors and windows by their host wall's segment with an opening depth of wall thickness plus 0.2 m (106-125, 122); everything else as triangles with its class from `BIM_IFC_SAVE_CLASS` (15-16) or IfcBuildingElementProxy (127-145). Only elements on shown layers are exported (io/ifcos-worker.js:142).
- The Python side (src/py/bim_ifcos.py, embedded by io/ifcos-py.js) writes an IFC4 file (57), units (60-65), a Model context with a Body subcontext (66-73), one Site, one Building and storeys from the level list (74-82, 170-192), walls (195-216) with `add_wall_representation`, prisms (221-245), openings as `IfcOpeningElement` voiding the host (`feature.add_feature`, 273) and filled by an IfcDoor or IfcWindow (`feature.add_filling`, 282), meshes (289-314) and property sets (319-337). No element is given a predefined type (`create_entity` with no `predefined_type`, 204, 231, 275, 278).
- GlobalIds: `bim_ifcos_keep_guid` sets the element's GlobalId to the one sent, if valid and unused (156-167). Authored elements send none, so IfcOpenShell makes a new one; the project, site, building, storeys and openings are new every save; and the GlobalIds the export makes are not returned to the app (`bim_ifcos_export` returns only counts, 342-379; ifcos-worker.js:152-161). So two saves of the same model share no GlobalIds except imported ones. For any IFC-based workflow (BCF issues, model diff, a federated coordination model) this is the most damaging gap.

## 6. Gap table

Bar: what a Revit-authored IFC4 file normally carries for these elements. "Clay" and "Us" cite file:lines; Gap is NONE, PARTIAL or MISSING; Close is P (port Clay's method into ES5, TypeScript lines cited), R (reuse IfcOpenShell 0.8.5, already shipped, through the existing adapter), or X (not worth it); effort S, M or L.

| # | Topic | Clay | Us | Gap | Close | Effort |
|---|---|---|---|---|---|---|
| 1 | IFC class per element at creation | Yes: the instance entity is constructed with the element (simple-wall.ts:75; slab src:33; window src:23), with one wrong class (member as IfcPlate, Members/SimpleMember/src/index.ts:38) | Chosen at save from `bim.type` (ifc-save.js:15-16, 91-95, 122, 138-140); rooms and grids have none | PARTIAL | P (the idea only, a data table): `bimIfcClassOf` at creation, stored in `bim.ifc` | S |
| 2 | Predefined type | Set on types: STANDARD, FLOOR, WINDOW, MULLION, CURTAIN_PANEL (index files cited in 4.2) | None written (bim_ifcos.py:204, 231, 275, 278); footing and strip footing differ only by `bim.type` (footings.js:34) | MISSING | P (data) + R (`create_entity(predefined_type=...)`, signature read in the wheel) | S |
| 3 | Types shared by instances (IfcWallType and kin) | Type objects exist (4.2), but `IfcRelDefinesByType` is never written; three of eight types never reach the model | Seven type categories (type-instance-params.js:115-123), none written | PARTIAL | R: `type.assign_type` creates `IfcRelDefinesByType` (api/type/assign_type.py, 241-247) and maps layer-set usages (257, 268-280) | M |
| 4 | Property sets (Pset_*Common) | None | Only imported sets and `BIM_Personal` (ifc-save.js:27-41; bim_ifcos.py:319-337); no IsExternal, LoadBearing, FireRating anywhere (grep) | MISSING | R (`pset.add_pset`/`edit_pset`, already used) + data from the buildingSMART templates shipped in the wheel (experiment e1) | M |
| 5 | Quantity sets (Qto_*BaseQuantities) | None | None written; the app does compute volumes and areas (`bimObjVolume`, type-instance-params.js:435) | MISSING | R (`pset.add_qto`/`edit_qto`, signatures in the wheel) + our own pure quantity functions | M |
| 6 | Material layer sets | None (no IfcMaterial anywhere, grep) | One material name per type and per instance (type-instance-params.js:31-34, 389-391); nothing written | MISSING | R (`material.add_material_set` with IfcMaterialLayerSet, `add_layer`, `edit_layer`, `assign_material`; usages through `assign_type`) + our layer data on wall, floor and ceiling types | M |
| 7 | Spatial structure | Project, Site with aggregates and containment (general/Project 94-112; Site 19-50); no Building, Storey or Space | Project, Site, one Building, storeys (bim_ifcos.py:74-82, 170-192); several app buildings (building-site-hierarchy.js:18-30) are flattened into one; rooms are not IfcSpace | PARTIAL | R: one IfcBuilding per app building, IfcSpace per room aggregated under its storey | M |
| 8 | Wall joins as relations | Geometric extension plus half-space cut, in memory only (simple-wall-cornerer.ts:55-148); no relation | Join Walls moves both end points to the intersection and rebuilds (editing/precision-editing.js:380-414); the join is not stored | MISSING | P for the join classification (which end meets which), as a pure function; R (`geometry.connect_path`, creates IfcRelConnectsPathElements with ATSTART/ATEND/ATPATH, signature in the wheel; enum in web-ifc ifc-schema.ts IFC4 namespace, line 568 of that namespace) | M |
| 9 | Openings as voids with fills | Voids yes (Element/index.ts:102-124); fills no | Voids and fills at save (bim_ifcos.py:267-283); in the model a door is a void marker only, with no separate opening record or GlobalId | PARTIAL | R (already); add stable GlobalIds for both the opening and the filling (OB1) | S |
| 10 | Hosted elements follow the host | Nester keeps a signed station along the wall (simple-wall-nester.ts:34-42, 49-62) | Openings keep an absolute centre and are re-cut strictly where they are (columns-openings.js:208-215, 248-256); footings keep `hostId` and rebuild (footings.js:80-118) | PARTIAL | P: `bimOpeningStation` / `bimOpeningAtStation` from the nester | S |
| 11 | GlobalId stability across edits and saves | Made once per object, kept in attributes; wrong format (36 characters, simple-wall.ts:76) | Kept only for imported elements (ifc-save.js:29); per-segment walls drop it (80); project, site, building, storeys, openings new every save; results not returned (5.4) | MISSING | P (our own ES5 base-64 compression, checked against IfcOpenShell's `guid.compress` outputs as fixtures) + R (`bim_ifcos_keep_guid` already applies them) | S |
| 12 | Classification references | None | Code and description, no system (classification.js:27-40); not written | PARTIAL | R (`classification.add_classification`, `add_reference`); systems and editions as data in the standards registry | S-M |
| 13 | Units | Length, area, and a broken volume unit (Project/index.ts:74-92) | SI metre, square metre, cubic metre (bim_ifcos.py:60-65) | NONE | none | - |
| 14 | Georeferencing | Site with no latitude or longitude (Site/index.ts:26-33) | Location known (cityjson.js:255, alignment-profile.js:655) but not written | MISSING | R (`georeference.add_georeferencing` with IfcMapConversion, `edit_georeferencing`) + our existing UTM forward transform (cityjson.js:37) | S-M |
| 15 | Representation contexts and identifiers | One plain context; shapes have no identifier or type (ifc-utils.ts:38-48) | Body subcontext via IfcOpenShell (bim_ifcos.py:66-73) | NONE | none | - |
| 16 | Placement relative to storey | None (PlacementRelTo null, ifc-utils.ts:28) | Absolute matrices (bim_ifcos.py:210-212, 239-241) | PARTIAL | X for now: absolute placements are valid; relative placement matters only to exchange editing, later | - |
| 17 | Owner history, application | Written once, elements null (Project/index.ts:18-59) | IfcOpenShell's default | NONE | none | - |
| 18 | Schema | IFC4X3 (Model/index.ts:76) | IFC4 (bim_ifcos.py:57) | NONE | X: IFC4 is what most checkers and Revit read; IFC4X3 waits for an owner decision (section 11) | - |
| 19 | Curtain walls, members, plates | Present but defective (4.2) | No curtain wall element | MISSING | X in this plan: Clay's version is not a model to follow; a separate research note if the owner wants curtain walls | L |

## 7. Alternatives compared (how to make the model IFC-native)

| Option | What it means | For | Against | Verdict |
|---|---|---|---|---|
| A. In-memory IFC model as the source of truth (Clay's way) | Every edit writes IFC lines into a web-ifc model | The model is always an IFC file | Clay needs a whole save-and-reopen per boolean (Model/index.ts:143-156); pins old web-ifc; would replace the app's JSON model, undo, history, every tool | Reject |
| B. JSON model with IFC identity and relations as data, serialized by IfcOpenShell (recommended) | Add `bim.ifc` and relation fields; the worker writes IFC4 with IfcOpenShell's api | Small pure functions, unit-testable; reuses the shipped adapter; app keeps working without the worker (CLAUDE.md library rule) | Two representations to keep in step; IFC exists only when saved | Adopt |
| C. JSON model, write IFC with web-ifc's writer in the page | Port Clay's entity construction to our writer | No Python worker | Re-implements what IfcOpenShell's api already does (types, materials, usages, qto, georef); web-ifc's writer has no high-level api | Reject for authoring; keep web-ifc for reading |
| D. Port Clay wholesale | Take its classes | Some structure | TypeScript classes over a pinned old API, missing most of the relations above | Reject; port only the nester method |

## 8. Experiment e1: standard property and quantity names, from the pinned templates

Script `docs/research/experiments/thatopen-gap/psets.py`: open `runtime/ifcos/0.8.5/ifcopenshell-...whl` as a zip, read `ifcopenshell/util/schema/Pset_IFC4X3.ifc` as text, collect each `IFCPROPERTYSETTEMPLATE` and the names of its `IFCSIMPLEPROPERTYTEMPLATE` children. Run with `python3 -I`; nothing from the wheel was imported. Result (IFC4X3 templates; the IFC4 ADD2 file in the same wheel holds the same set names):

| Set | Applies to | Property names found |
|---|---|---|
| Pset_WallCommon | IfcWall, IfcWallType | Status, AcousticRating, FireRating, Combustible, SurfaceSpreadOfFlame, ThermalTransmittance, IsExternal, LoadBearing, ExtendToStructure, Compartmentation |
| Pset_SlabCommon | IfcSlab, IfcSlabType | Status, AcousticRating, FireRating, PitchAngle, Combustible, SurfaceSpreadOfFlame, Compartmentation, IsExternal, ThermalTransmittance, LoadBearing |
| Pset_ColumnCommon | IfcColumn, IfcColumnType | Status, Slope, Roll, IsExternal, ThermalTransmittance, LoadBearing, FireRating |
| Pset_BeamCommon | IfcBeam, IfcBeamType | Status, Span, Slope, Roll, IsExternal, ThermalTransmittance, LoadBearing, FireRating |
| Pset_DoorCommon | IfcDoor, IfcDoorType | Status, FireRating, AcousticRating, SecurityRating, DurabilityRating, HygrothermalRating, WaterTightnessRating, MechanicalLoadRating, WindLoadRating, Infiltration, IsExternal, ThermalTransmittance, GlazingAreaFraction, HandicapAccessible, FireExit, HasDrive, SelfClosing, SmokeStop |
| Pset_WindowCommon | IfcWindow, IfcWindowType | Status, AcousticRating, FireRating, SecurityRating, IsExternal, Infiltration, ThermalTransmittance, GlazingAreaFraction, HasSillExternal, HasSillInternal, HasDrive, SmokeStop, FireExit, WaterTightnessRating, MechanicalLoadRating, WindLoadRating |
| Pset_SpaceCommon | IfcSpatialElement, IfcSpatialElementType | IsExternal, GrossPlannedArea, NetPlannedArea, PubliclyAccessible, HandicapAccessible |
| Qto_WallBaseQuantities | IfcWall, IfcWallType | Width, Height, GrossFootPrintArea, NetFootPrintArea, GrossSideArea, NetSideArea, GrossVolume, NetVolume, GrossWeight, NetWeight (10 of the 11 children parsed; the template lists 11 references, one entry spans lines and the parser missed it: open, expected Length) |
| Qto_SlabBaseQuantities | IfcSlab, IfcSlabType | Length, Depth, Perimeter, GrossArea, NetArea, GrossVolume, NetVolume, GrossWeight, NetWeight |
| Qto_ColumnBaseQuantities | IfcColumn, IfcColumnType | CrossSectionArea, OuterSurfaceArea, GrossSurfaceArea, NetSurfaceArea, GrossVolume, NetVolume, GrossWeight, NetWeight (Length expected, same parsing caveat) |
| Qto_DoorBaseQuantities | IfcDoor, IfcDoorType | Height, Perimeter, Area |
| Qto_SpaceBaseQuantities | IfcSpace, IfcSpaceType | FinishCeilingHeight, FinishFloorHeight, GrossPerimeter, NetPerimeter, GrossFloorArea, NetFloorArea, GrossWallArea, NetWallArea, GrossCeilingArea, NetCeilingArea, GrossVolume, NetVolume |

Use: these names become data in the standards registry with the edition "IFC4 ADD2 TC1" and "IFC4X3 ADD2" (the two template files), not hand-typed lists. The parser must be fixed to read multi-line entities before the data is generated (OB5, task 1).

Predefined type values used in the plan were read in web-ifc's IFC4 namespace of `src/ts/ifc-schema.ts` (from line 12567): IfcWallTypeEnum (STANDARD, PARTITIONING, SHEAR, PARAPET, ...), IfcSlabTypeEnum (FLOOR, ROOF, LANDING, BASESLAB), IfcFootingTypeEnum (PAD_FOOTING, STRIP_FOOTING, ...), IfcCoveringTypeEnum (CEILING, ...), IfcBeamTypeEnum (BEAM, ...), IfcColumnTypeEnum (COLUMN), IfcDoorTypeEnum (DOOR, GATE, TRAPDOOR), IfcSpaceTypeEnum (SPACE, ...), IfcConnectionTypeEnum (ATPATH, ATSTART, ATEND, NOTDEFINED), IfcLayerSetDirectionEnum (AXIS1, AXIS2, AXIS3), IfcDirectionSenseEnum (POSITIVE, NEGATIVE). The registry data should be generated from that file, with its commit, rather than copied by hand.

## 9. Phase plan: an IFC-native element model

Phase names are provisional (OB1 to OB8); V numbers are given when the owner queues them. Each phase: pure functions in a new or existing file of `src/js/engine/`, their unit test in `tests/unit/`, then one `[Claude]` task for the Python adapter (bim_ifcos.py is shared code, three or more files when re-embedded) and one `[Cline]` task per pure function. Every function below takes plain data and returns plain data; none reads `A3D` unless its name says it wires state. All ES5.

### OB1: identity (GlobalIds that last)

New file `src/js/engine/bim/ifc-identity.js`; test `tests/unit/ifc-identity.test.mjs`.

- `bimIfcGuidFromBytes(bytes16) -> string22`: our own implementation of the 22-character base-64 form (alphabet 0-9, A-Z, a-z, underscore, dollar; first character carries 2 bits). Tested against fixtures made once by IfcOpenShell's `guid.compress` (fixture file in `tests/fixtures/`, made by a script, not by hand).
- `bimIfcGuidNew(rand) -> string22`: 16 bytes from an injected `rand()` (tests pass a seeded one; the app passes `crypto.getRandomValues`-backed when present, `Math.random` otherwise, warned once).
- `bimIfcGuidValid(s) -> boolean`: the same check `bim_ifcos_keep_guid` makes (bim_ifcos.py:157-161).
- `bimIfcEnsureIdentity(bim, rand) -> bim`: adds `bim.ifc = {guid}` once; never replaces a valid one.
- `bimIfcSegmentGuids(bim, n, rand) -> array`: keeps `bim.ifc.segGuids` the length of the wall's segment count, keeping existing entries in order (fixes ifc-save.js:80).
- `bimIfcForgetIdentity(bim) -> bim`: clears `bim.ifc.guid` and per-segment and opening ids, for copy, array and mirror-copy paths (a copy is a new element). The copy paths must be listed during the work order by grep, not assumed.
- `bimIfcSpatialIds(state, rand) -> {project, site, buildings: {id: guid}, levels: {id: guid}}`: ensures ids on `A3D.site`, each building and each level.
- Changes: `io/ifc-save.js` `bimIfcSaveBase` reads `bim.ifc.guid` for every element; walls use `segGuids`; openings carry `ifc.openingGuid`. `bim_ifcos.py`: `bim_ifcos_begin` and `bim_ifcos_new_project` accept project, site, building and storey guids and apply them with `bim_ifcos_keep_guid`; `bim_ifcos_put_opening` keeps the opening's guid too.
- Acceptance: export twice without edits; the two files have identical GlobalId sets (browser check, once, per Rule #1's phase row).

### OB2: class and predefined type at creation

New file `src/js/engine/bim/ifc-class.js` (data plus functions); test `tests/unit/ifc-class.test.mjs`.

- `BIM_IFC_CLASS` data: `bim.type` to `{cls, predefined, allowed: [...]}`: wall to IfcWall STANDARD; floor IfcSlab FLOOR; ceiling IfcCovering CEILING; column IfcColumn COLUMN; beam IfcBeam BEAM; footing IfcFooting PAD_FOOTING; stripfooting IfcFooting STRIP_FOOTING; roof IfcRoof (FLAT_ROOF, SHED_ROOF, GABLE_ROOF, HIP_ROOF from `bim.style`); stair IfcStair; door IfcDoor DOOR; window IfcWindow WINDOW; room IfcSpace SPACE. Allowed lists generated from web-ifc's IFC4 enums (section 8).
- `bimIfcClassOf(rec) -> {cls, predefined}`: from `bim.ifc` when set, else the table; rooms by `t`.
- `bimIfcPredefinedValid(cls, value) -> boolean`.
- `bimIfcRoofPredefined(style) -> string`.
- Wiring: each creation function (buildWallSolid, buildFloorSolid, column, door, window, footing, roof, stair, room) calls one helper `bimIfcStamp(o, rand)` that applies OB1 and OB2 (one shared call; the [Claude] task, since it touches several files).
- Changes: ifc-save.js uses `bimIfcClassOf`; `bim_ifcos.py` passes `predefined_type` to `create_entity`. Properties palette shows class and predefined type and lets the user choose among `allowed` (palette.js).

### OB3: types as IFC type objects

Changes in `bim/type-instance-params.js` (small) and a new `io/ifc-save-types.js`; test `tests/unit/ifc-types.test.mjs`.

- `bimIfcTypeClassOf(cat) -> string`: wall IfcWallType, floor IfcSlabType, ceiling IfcCoveringType, column IfcColumnType, beam IfcBeamType, footing and stripfooting IfcFootingType.
- `bimIfcEnsureTypeIdentity(typeRec, rand) -> typeRec`: `ifc.guid` and predefined on each type record (run from `bimEnsureTypes`, 546-572).
- `bimIfcSaveTypes(types, usedTypeIds) -> [{guid, cls, name, predefined, layers}]`: only types used by exported elements.
- ifc-save.js: each element item gains `typeGuid`.
- `bim_ifcos.py`: `bim_ifcos_put_type(t)` creates the type and its material set (OB4); after the elements, `type.assign_type(related_objects, relating_type)` per type. Note from the source: when the type has a predefined type other than NOTDEFINED, `assign_type` clears the instances' own PredefinedType (assign_type.py:259-265), so the predefined value should live on the type for typed elements and on the instance only for untyped ones.

### OB4: material layer sets

Data on wall, floor and ceiling types: `params.layers = [{material, thickness, fn}]` where `fn` is a label (finish, structure, insulation, membrane). New file `src/js/engine/bim/material-layers.js`; test `tests/unit/material-layers.test.mjs`.

- `bimLayersFromType(typeRec) -> layers`: migration; a type with only `material` and `thickness` becomes one layer.
- `bimLayersThickness(layers) -> number`.
- `bimLayersValidate(layers, thickness, tol) -> null | message`: sum equals the type's thickness; every thickness positive; materials named.
- `bimLayersSetThickness(layers, index, value) -> layers`: edits one layer and returns a new array (the type thickness then follows the sum, propagated by the existing `bimApplyTypeToInstances`).
- `bimLayerUsageOffset(thickness, align) -> {direction: 'AXIS2', sense: 'POSITIVE' | 'NEGATIVE', offset}`: the layer set's offset from the wall's reference line, from the app's own side distances (`bimAlignOffsets`, footings.js:219). Which sign IfcOpenShell's wall representation expects must be measured first (section 10).
- `bim_ifcos.py`: per type, `material.add_material` per distinct material, `add_material_set(set_type='IfcMaterialLayerSet')`, `add_layer` and `edit_layer` (LayerThickness), `assign_material` on the type; usages follow through `assign_type` (assign_type.py:257, 268-280). Columns and beams later as IfcMaterialProfileSet (same api, `assign_material` lists it), a separate phase.
- Interface: the type dialog (`openTypeDlg`, 721) gains a layer table; the plan's cut drawing of layers is a later phase, not here.

### OB5: standard property sets and base quantities

Data in `src/js/engine/standards/` (a new data file beside the registry, since registry.js is already over 1 000 lines): the sets of section 8 with their edition. New file `src/js/engine/properties/ifc-psets.js` and `src/js/engine/bim/ifc-quantities.js`; tests `tests/unit/ifc-psets.test.mjs`, `tests/unit/ifc-quantities.test.mjs`.

- Task 1 [Claude]: fix the template parser for multi-line entities and generate the data file, with its source path and the wheel's SHA-256 from MANIFEST.json.
- `bimPsetNamesFor(cls, edition) -> [{name, kind}]`.
- `bimPsetCommonValues(rec, typeRec) -> {set, props}`: IsExternal, LoadBearing, FireRating, AcousticRating, ThermalTransmittance from new instance and type fields; only fields that have a value are written.
- `bimQtoWall(bim, openings) -> {Length, Width, Height, GrossSideArea, NetSideArea, GrossVolume, NetVolume, GrossFootPrintArea}` per segment, net values less the openings on that segment.
- `bimQtoSlab(bim) -> {Depth, Perimeter, GrossArea, GrossVolume}`; `bimQtoColumn(bim) -> {Length, CrossSectionArea, GrossVolume}`; `bimQtoBeam(bim)`; `bimQtoOpening(bim) -> {Width, Height, Area}`; `bimQtoSpace(room, height) -> {GrossFloorArea, GrossPerimeter, GrossVolume}`.
- `bim_ifcos.py`: `bim_ifcos_put_qto(guid, name, values)` with `pset.add_qto` and `edit_qto`. Psets on types for type values, on instances for instance values.
- Interface: the Properties palette groups these fields under the set names.

### OB6: spatial structure and spaces

Changes in `io/ifc-save.js` and `bim_ifcos.py`; test `tests/unit/ifc-spatial.test.mjs`.

- `bimIfcSaveSpatial(site, buildings, levels) -> {site: {guid, name, lat, lon, elev}, buildings: [{guid, name, storeys: [{guid, name, elev, levelId}]}]}`.
- `bimIfcSaveLevelIndex(spatial) -> {levelId: [b, s]}`: replaces the flat level index (ifc-save.js:44-61) so elements land in the storey of their own building.
- `bimIfcSaveSpace(room, levelIndex) -> {guid, name, number, pts, base, height, storey}` (rooms keep `number`, room-colour-fill.js:174).
- `bim_ifcos.py`: `bim_ifcos_begin` builds one IfcBuilding per app building; `bim_ifcos_put_space` makes an IfcSpace with an extruded footprint, aggregated under its storey (spaces decompose a storey; they are not contained in it), with Pset_SpaceCommon and Qto_SpaceBaseQuantities from OB5.
- Rooms then need the OB1 identity too (they have no `bim`; add `o.ifc`).

### OB7: joins and hosting as relations

New file `src/js/engine/bim/ifc-relations.js`; test `tests/unit/ifc-relations.test.mjs`.

- `bimWallJoinKind(clA, clB, tol) -> {aAt: 'ATSTART' | 'ATEND' | 'ATPATH', bAt: ..., point}` or null: which end of each wall meets the other (an L when both are ends, a T when one is ATPATH). The app's own Join (precision-editing.js:380-401) gives the case where both are ends.
- `bimJoinRecord(a, b, kind) -> {other, aAt, bAt}`; `applyWallJoin` stores one on each wall in `bim.joins` (a [Cline] task naming precision-editing.js).
- `bimJoinsPrune(objs) -> count`: removes joins whose other wall is gone (like `bimSweepFootingHosts`, footings.js:179).
- `bimJoinsToIfc(joins, guidOf) -> [{relating, related, relatingAt, relatedAt}]`, de-duplicated (each pair once).
- Port of Clay's nester (simple-wall-nester.ts:14-43, 49-62): `bimOpeningStation(centerline, center) -> {seg, s}` (segment index and signed distance along it from its start) and `bimOpeningAtStation(centerline, seg, s) -> [x, z]`. Openings store their station when made; a wall rebuild moves them to their station before re-cutting (one call in `bimOpeningSpecsFor`, columns-openings.js:208), so a moved or stretched wall keeps its doors.
- `bim_ifcos.py`: `geometry.connect_path(relating_element, related_element, relating_connection, related_connection)` per join (creates IfcRelConnectsPathElements). Fills and voids stay as they are (bim_ifcos.py:273, 282). Footings: an `IfcRelConnectsElements` from footing to host is optional and left to the owner (section 11).

### OB8: classification and georeferencing

Data: classification systems with editions in the standards data (Uniclass 2015 with its table and release, OmniClass with its table and edition), each with source and licence noted; codes themselves are user-entered or imported, never shipped if their licence forbids it (to check per system, section 10). Files: `bim/classification.js` (system on each entry), new `io/ifc-georef.js`; tests `tests/unit/ifc-classification.test.mjs`, `tests/unit/ifc-georef.test.mjs`.

- `bimClassificationRef(entry, system) -> {system, edition, identification, name, location}`.
- `bimIfcSaveClassifications(objs, list, systems) -> [{system, refs: [{identification, name, guids}]}]`.
- `bimIfcMapConversion(lat, lon, elev, trueNorthDeg) -> {crs: 'EPSG:326nn' | 'EPSG:327nn', eastings, northings, orthogonalHeight, xAxisAbscissa, xAxisOrdinate, scale}` using the app's UTM forward transform (cityjson.js:37) and EPSG rule (53); the axis terms from true north. Tested against points computed independently (pyproj or a published UTM example, recorded in the fixture with its source).
- `bim_ifcos.py`: `classification.add_classification` and `add_reference`; `georeference.add_georeferencing(ifc_class='IfcMapConversion', name=crs)` then `edit_georeferencing` with the values; IfcSite's RefLatitude and RefLongitude as a fallback.

### Order and why

OB1 first: every later relation needs stable ids, and it is the cheapest, most visible fix. OB2 next: class and predefined type are what every checker reads first. OB3 and OB4 together make types real (OB4 depends on OB3's type entities). OB5 depends on OB2 (class decides the set) and OB4 (layer thickness for quantities). OB6 and OB7 are independent of each other and of OB4/OB5. OB8 last; it is small but depends on data decisions.

## 10. Risks and what is still open

- Measured nothing yet about IfcOpenShell's behaviour (signatures and source text only). Before OB4: one experiment writing a two-layer wall type, assigning it, and reading back the layer set usage's direction, sense and offset against `add_wall_representation`'s `offset` (bim_ifcos.py:205-209). Before OB7: the same for `connect_path` and what Revit or a viewer does with it.
- Whether `assign_type` with the default `should_map_representations` behaves correctly for types with no RepresentationMaps (source suggests usages are mapped and representations left alone, assign_type.py:249-257): measure.
- Copy paths must clear identity (OB1); the list of those paths is not yet made.
- Classification licences: whether Uniclass and OmniClass code lists may be shipped with the app is not checked (U for both). The plan ships only system names and lets users enter or import codes until checked.
- Validation: the plan has no IFC validator in the loop. The buildingSMART validation service and IfcOpenShell's `validate` are candidates; not researched here.
- The experiment's parser missed one child per some templates (section 8); the generated data must be checked against IfcOpenShell's own `util.pset` reading.
- That Open's newer packages (components 3.x) were not read in this area; another agent covers them.

## 11. The owner's decisions (to ask together)

1. Approve approach B (section 7): JSON model plus IFC identity and relations, IfcOpenShell for writing.
2. Schema of the written file: stay on IFC4 (current) or offer IFC4X3 as well.
3. Where predefined types and standard properties are edited: on the type only (Revit's habit) or also per instance.
4. Wall layers: which functions to offer (finish, structure, insulation, membrane, air gap) and whether plan cuts should draw layers in a later phase.
5. Which classification systems first (Uniclass 2015, OmniClass, other), once licences are checked.
6. Footing to host relation: write it (IfcRelConnectsElements) or not.
7. Whether elements on hidden layers should still be exported (today they are not, ifcos-worker.js:142).

## 12. References

- engine_clay 6f14cbe, packages/clay/src: core/Model/index.ts; core/Object/index.ts; core/Elements/{Element,ElementType,StaticElementType,DynamicElementType}/index.ts; core/Geometry/index.ts; elements/Walls/SimpleWall/{index.ts, src/simple-wall.ts, src/simple-wall-cornerer.ts, src/simple-wall-nester.ts, example.ts}; elements/{Slabs,Openings,Windows,CurtainWalls,Members,Plates,Furniture}/*; geometries/{Extrusion,HalfSpace,Brep,MappedItems,Profiles}/*; general/{Project,Site,SpatialChildren,ElementChildren}/index.ts; utils/{ifc-utils.ts, math-utils.ts}; packages/clay/package.json (version 2.4.0, MIT, web-ifc 0.0.59, fragments 2.2.0). Read 2026-11-28, P.
- engine_templates 1b30524: README.md, templates/vanilla/{package.json, src/main.ts, src/ui-templates/*, src/bim-components/*}. Read 2026-11-28, P.
- engine_web-ifc 9ab7d5c: src/ts/ifc-schema.ts, IFC4 namespace (from line 12567), enum classes cited in section 8. Read 2026-11-28, P (generated schema code, a dependable transcription of the EXPRESS schema; the EXPRESS itself not read, S for the schema as such).
- IfcOpenShell 0.8.5 wheel (runtime/ifcos/0.8.5): ifcopenshell/api/{root/create_entity, type/assign_type, material/add_material_set, material/add_layer, material/edit_layer, material/assign_material, pset/add_qto, pset/edit_qto, geometry/connect_path, classification/add_classification, classification/add_reference, georeference/add_georeferencing, georeference/edit_georeferencing}.py signatures; type/assign_type.py lines 61-101 and 241-280; guid.py lines 28 and 85; util/schema/Pset_IFC4X3.ifc and Pset_IFC4_ADD2.ifc (buildingSMART templates as shipped). Read 2026-11-28, P for the source text; behaviour not run (open, section 10).
- This repository at 0abf980: files and lines as cited. Read 2026-11-28, P.
- Earlier notes this one builds on: docs/research/research-thatopen.md, docs/research/research-ifcopenshell-app.md (not re-read in full here).
