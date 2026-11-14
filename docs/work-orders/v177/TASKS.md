# V177 work orders: Save as IFC

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

**WO-01 to WO-08** add one function each to `src/py/bim_ifcos.py`, below the functions already there, and change
nothing else: not the header, no `import` line (every module is imported already; the gate refuses an added import),
not another file. Python 3.13 (Pyodide). Every `ifcopenshell.api` call is `ifcopenshell.api.<module>.<function>(f,
...)` with keyword arguments as the spec writes them. A function answers a plain dict; on a failure
`{"error": "..."}`, never an exception. Their tests run in the app's own Pyodide (the first run downloads the pinned
wheels into `.cache/ifcos/`, as V176's did):

    node --test --test-name-pattern="WO-01" docs/work-orders/v177/v177.test.mjs
    npm test

**WO-09 to WO-17** add one function each to `src/js/engine/io/ifc-export.js`, below its header comment, and change
nothing else: not another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`, `function`;
no `let`, `const`, arrow functions, classes or template strings. Use only the names listed; never a name from
another file. Their tests read the file as text:

    node --test --test-name-pattern="WO-09" docs/work-orders/v177/v177-js.test.mjs
    node --check src/js/engine/io/ifc-export.js
    npm test

Implement the whole function; never a placeholder. Nothing calls these functions until WO-18. Scores are from
`../ROUTING.md` (files, logic, understanding, judgment, trickiness, check).

---

## [ ] WO-01 [Cline] `bim_ifcos_add_storey(name, elevation)`

- **It must:** An `IfcBuildingStorey` named `name` with `Elevation = elevation`, aggregated to the first `IfcBuilding`; answers `{"guid": storey.GlobalId}`.
- **May use:** `ifcopenshell.api.root.create_entity`, `ifcopenshell.api.aggregate.assign_object`, `_bim_ifcos_file`.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v177/v177.test.mjs`. **Score:** 0+0+1+0+1+0 = 2.

---

## [ ] WO-02 [Cline] `bim_ifcos_add_wall_on(storey_guid, name, x0, y0, x1, y1, z, height, thickness, offset)`

- **It must:** SPEC 4.1 WO-02: as `bim_ifcos_add_wall`, on the storey whose GlobalId is `storey_guid`, at height `z`, with `offset=offset` in `add_wall_representation`. Errors in order: `no storey`, `zero length`, `bad size`; nothing added on an error. You may add the small helpers `_bim_ifcos_body(f)` (the Body sub-context), `_bim_ifcos_by_guid(f, guid, ifc_class)` and `_bim_ifcos_matrix(x, y, z, a)` above it; WO-03 to WO-07 use them.
- **May use:** `ifcopenshell.api.root.create_entity`, `ifcopenshell.api.geometry.add_wall_representation`, `ifcopenshell.api.geometry.assign_representation`, `ifcopenshell.api.geometry.edit_object_placement`, `ifcopenshell.api.spatial.assign_container`, `math`, `numpy`, `_bim_ifcos_file`.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 45
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v177/v177.test.mjs`. **Score:** 0+0+1+0+2+0 = 3, tier B.

---

## [ ] WO-03 [Cline] `bim_ifcos_add_slab(storey_guid, name, points, z, depth)`

- **It must:** SPEC 4.1 WO-03. Fewer than 3 points or not a list: `too few points`; `depth <= 0`: `bad size`; the outline closed by repeating its first point when the last differs.
- **May use:** `ifcopenshell.api.geometry.add_slab_representation`, the WO-02 helpers and API names.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 35
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v177/v177.test.mjs`. **Score:** 0+0+1+0+1+0 = 2.

---

## [ ] WO-04 [Cline] `bim_ifcos_add_column(storey_guid, name, x, y, z, width, depth, height, rotation)`

- **It must:** SPEC 4.1 WO-04: an `IfcRectangleProfileDef` (`ProfileType="AREA"`, `XDim=width`, `YDim=depth`) extruded `height` by `add_profile_representation`, placed at (x, y, z) turned by `rotation`.
- **May use:** `f.create_entity`, `ifcopenshell.api.geometry.add_profile_representation`, the WO-02 helpers and API names.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 35
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v177/v177.test.mjs`. **Score:** 0+0+1+0+1+0 = 2.

---

## [ ] WO-05 [Cline] `bim_ifcos_add_opening(wall_guid, kind, name, along, sill, width, height, thickness, offset)`

- **It must:** SPEC 4.1 WO-05, step by step: the opening (a box 0.1 m thicker than the wall, from `offset - 0.05`), `feature.add_feature`, the door or window (`add_door_representation` / `add_window_representation`, `OverallHeight`, `OverallWidth`), `feature.add_filling`, contained in the wall's storey. Both placements are `numpy.dot(W, local)` with `W` the wall's placement. Answers `{"guid", "opening"}`.
- **May use:** `ifcopenshell.api.feature.add_feature`, `ifcopenshell.api.feature.add_filling`, `ifcopenshell.api.geometry.add_door_representation`, `ifcopenshell.api.geometry.add_window_representation`, `ifcopenshell.util.placement.get_local_placement`, `ifcopenshell.util.element.get_container`, `numpy.dot`, the WO-02 helpers and API names.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 55
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v177/v177.test.mjs`. **Score:** 0+1+1+0+2+0 = 4, tier B.

---

## [ ] WO-06 [Cline] `bim_ifcos_add_mesh(storey_guid, name, ifc_class, vertices, faces)`

- **It must:** SPEC 4.1 WO-06, with the list `BIM_IFCOS_CLASSES` added just above the function. `empty mesh`, then `bad face` (short, or an index not an int in range) before anything is added.
- **May use:** `ifcopenshell.api.geometry.add_mesh_representation`, the WO-02 helpers and API names.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v177/v177.test.mjs`. **Score:** 0+0+1+0+1+0 = 2.

---

## [ ] WO-07 [Cline] `bim_ifcos_add_pset(guid, name, props)`

- **It must:** SPEC 4.1 WO-07: keep `str`, `int`, `float` (not NaN), `bool` values only; answers `{"count": <kept>}`.
- **May use:** `ifcopenshell.api.pset.add_pset`, `ifcopenshell.api.pset.edit_pset`, the WO-02 helpers.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v177/v177.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-08 [Cline] `bim_ifcos_save_model(model, path)`

- **It must:** SPEC 4.1 WO-08 in its order: levels (or the one default), the project, the first storey renamed, the other storeys; walls, slabs, columns, openings (only on a wall that was added, with that wall's thickness and offset), meshes, psets; then `bim_ifcos_write_read(path)` plus `guids` and `skipped`.
- **May use:** `bim_ifcos_new_project`, `bim_ifcos_write_read`, the functions of WO-01 to WO-07, `_bim_ifcos_file`.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 75
- **Test:** the cases named `WO-08 ...` in `docs/work-orders/v177/v177.test.mjs`. **Score:** 0+1+1+1+1+0 = 4, tier B.

---

## [ ] WO-09 [Cline] `bimIfcxPlan(p)`

- **It must:** `[p[0], 0 - p[1]]`.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-export.js`, `docs/work-orders/v177/v177-js.test.mjs`
- **Budget:** 5
- **Test:** the cases named `WO-09 ...` in `docs/work-orders/v177/v177-js.test.mjs`. **Score:** 0.

---

## [ ] WO-10 [Cline] `bimIfcxLevels(levels)`

- **It must:** SPEC 4.2 WO-10.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-export.js`, `docs/work-orders/v177/v177-js.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-10 ...` in `docs/work-orders/v177/v177-js.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-11 [Cline] `bimIfcxLevelOf(levels, levelId, y)`

- **It must:** SPEC 4.2 WO-11.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-export.js`, `docs/work-orders/v177/v177-js.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-11 ...` in `docs/work-orders/v177/v177-js.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-12 [Cline] `bimIfcxWalls(o, levels)`

- **It must:** SPEC 4.2 WO-12, with the offsets of SPEC part 3 (`thickness = dLeft + dRight`, `offset = 0 - dLeft`).
- **May use:** `bimIfcxPlan`, `bimIfcxLevelOf` (this file).
- **Files:** `src/js/engine/io/ifc-export.js`, `docs/work-orders/v177/v177-js.test.mjs`
- **Budget:** 35
- **Test:** the cases named `WO-12 ...` in `docs/work-orders/v177/v177-js.test.mjs`. **Score:** 0+0+1+0+1+0 = 2.

---

## [ ] WO-13 [Cline] `bimIfcxSlab(o, levels)`

- **It must:** SPEC 4.2 WO-13 (a floor's top is `baseY`: the slab's `z` is `baseY - thickness`).
- **May use:** `bimIfcxPlan`, `bimIfcxLevelOf` (this file).
- **Files:** `src/js/engine/io/ifc-export.js`, `docs/work-orders/v177/v177-js.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-13 ...` in `docs/work-orders/v177/v177-js.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-14 [Cline] `bimIfcxColumn(o, levels)`

- **It must:** SPEC 4.2 WO-14 (`rotation: 0 - (bim.rotation || 0)`).
- **May use:** `bimIfcxPlan`, `bimIfcxLevelOf` (this file).
- **Files:** `src/js/engine/io/ifc-export.js`, `docs/work-orders/v177/v177-js.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-14 ...` in `docs/work-orders/v177/v177-js.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-15 [Cline] `bimIfcxOpening(m, walls)`

- **It must:** SPEC 4.2 WO-15: the nearest segment of its host wall that the centre projects onto.
- **May use:** `bimIfcxPlan` (this file).
- **Files:** `src/js/engine/io/ifc-export.js`, `docs/work-orders/v177/v177-js.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-15 ...` in `docs/work-orders/v177/v177-js.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-16 [Cline] `bimIfcxMesh(o, levels)`

- **It must:** SPEC 4.2 WO-16, with the table `BIM_IFCX_CLASS` added as a `var` just above the function.
- **May use:** `bimIfcxLevelOf` (this file).
- **Files:** `src/js/engine/io/ifc-export.js`, `docs/work-orders/v177/v177-js.test.mjs`
- **Budget:** 35
- **Test:** the cases named `WO-16 ...` in `docs/work-orders/v177/v177-js.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-17 [Cline] `bimIfcxModel(objs, levels, name)`

- **It must:** SPEC 4.2 WO-17: each solid into the first list that takes it, one pset per entry, the openings last.
- **May use:** the functions of WO-10 to WO-16 (this file).
- **Files:** `src/js/engine/io/ifc-export.js`, `docs/work-orders/v177/v177-js.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-17 ...` in `docs/work-orders/v177/v177-js.test.mjs`. **Score:** 0+0+1+0+1+0 = 2.

---

## [ ] WO-18 [Claude] The wheels, the worker, File > Export > IFC

Claude's: crosses `runtime/`, the worker, the UI and the command map (score 2+2+2+1+2+1 = 10). Pin the seven wheels
in `runtime/wheels/` and `runtime/MANIFEST.json` with the LGPL-3.0 and GPL-3.0 texts and their credit in
`THIRD_PARTY_NOTICES.md`; load them in the Python worker on the first IFC call only; embed `bim_ifcos.py` as
`bim_ladybug.py` is; `bimIfcExport()` (SPEC 4.3), the menu item and `IFCOUT`; move both test files into
`tests/unit/` (the Python one stays outside `npm test` if it needs the network). One browser check of File, Export,
IFC on phone, tablet and desktop (Rule #1: a phase's new interface), its script in `tests/e2e/`.

---

## [ ] WO-19 [Claude] The records

CLAUDE.md's library rule reworded for D1 (a): GPL and AGPL libraries allowed as separate files run only in the
Python worker, never bundled into the app's own files. PIPELINE row 177, the log, Notion's task and the research
note's page.
