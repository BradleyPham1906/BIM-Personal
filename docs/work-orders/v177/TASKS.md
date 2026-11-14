# V177 work orders, step 1: the adapter that writes a model as an IFC file

Spec: `SPEC.md` in this folder (part 3 is the data, part 4 has every function in full). Implementation target: local
`main`. One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every task: add its function(s) to the end of `src/py/bim_ifcos.py` and change nothing else: not another file, not
the header, no `import` line (every module the tasks need is imported already: `math`, `os`, `numpy`, `ifcopenshell`
and its `api.aggregate`, `api.context`, `api.feature`, `api.geometry`, `api.project`, `api.pset`, `api.root`,
`api.spatial`, `api.unit`, `guid`, `util.element`, `util.placement`, `util.unit`; the gate refuses an added import),
not V176's functions, not `canvas_v10.html`. Python 3.13 (Pyodide). Use only the names listed in the task and in SPEC
part 4; every `ifcopenshell.api` call is `ifcopenshell.api.<module>.<function>(_bim_ifcos_file, ...)` with keyword
arguments as the spec writes them. Each function that the spec says answers a dict wraps its body in `try` and
answers `{"error": "failed"}` on any exception it does not name; it answers `{"error": "no project"}` when
`_bim_ifcos_file` is `None`. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v177/v177.test.mjs`, outside `npm test` (the first run downloads the pinned
wheels, about 16 MB, into `.cache/ifcos/`; each run takes about 30 s). After each task run its own cases, then the
unit tests:

    node --test --test-name-pattern="WO-01" docs/work-orders/v177/v177.test.mjs
    npm test

Scores are from `../ROUTING.md` (files, logic, understanding, judgment, trickiness, check).

---

## [x] WO-01 [Cline] `bim_ifcos_matrix`, `bim_ifcos_storey`, `bim_ifcos_body`, `bim_ifcos_keep_guid`

- **It must:** add the four functions exactly as SPEC part 4 "WO-01" writes them. These four answer values, not
  dicts, and have no `try` of their own except `bim_ifcos_keep_guid`'s around `by_guid` (it raises when no entity has
  the GlobalId: that is the case where the GlobalId is free and is set).
- **Example:** `bim_ifcos_matrix(1, 2, 3, 0)` is `[[1, 0, 0, 1], [0, 1, 0, 2], [0, 0, 1, 3], [0, 0, 0, 1]]`;
  `bim_ifcos_keep_guid(p, "short")` leaves `p.GlobalId` as it was and answers it.
- **May use:** `numpy.array` (with `dtype=float`), `math.cos`, `math.sin`, `_bim_ifcos_file.by_type`,
  `_bim_ifcos_file.by_guid`, `isinstance`, `len`, `all`.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-01 ...`. **Score:** 0+0+1+0+1+0 = 2.

---

## [x] WO-02 [Cline] `bim_ifcos_begin(name, levels)`

- **It must:** follow SPEC part 4 "WO-02" in its order: the empty-levels default, `bim_ifcos_new_project`, rename the
  first storey, add the others under the building, then place every storey at its `Elevation`.
- **Example:** `bim_ifcos_begin("House", [{"name": "Ground", "elev": 0}, {"name": "First", "elev": 3.2}])` answers a
  summary whose `storeys` are `[{"name": "Ground", "elevation": 0}, {"name": "First", "elevation": 3.2}]`.
- **May use:** `bim_ifcos_new_project`, `bim_ifcos_summary` (V176), `bim_ifcos_matrix` (WO-01),
  `ifcopenshell.api.root.create_entity`, `ifcopenshell.api.aggregate.assign_object`,
  `ifcopenshell.api.geometry.edit_object_placement`, `_bim_ifcos_file.by_type`.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 35
- **Test:** the cases named `WO-02 ...`. **Score:** 0+0+1+0+1+0 = 2.

---

## [x] WO-03 [Cline] `bim_ifcos_put_wall(w)`

- **It must:** follow SPEC part 4 "WO-03". The zero-length check comes before anything is created.
- **Example:** after `bim_ifcos_begin`, a wall from (1, 2) to (5, 2), base 3.2, height 2.7, thickness 0.2, offset
  -0.1 fills the box from (1, 1.9, 3.2) to (5, 2.1, 5.9).
- **May use:** `math.hypot`, `math.atan2`, `ifcopenshell.api.root.create_entity`,
  `ifcopenshell.api.geometry.add_wall_representation`, `ifcopenshell.api.geometry.assign_representation`,
  `ifcopenshell.api.geometry.edit_object_placement`, `ifcopenshell.api.spatial.assign_container`, and WO-01's four.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 35
- **Test:** the cases named `WO-03 ...`. **Score:** 0+0+1+0+1+0 = 2.

---

## [x] WO-04 [Cline] `bim_ifcos_put_prism(p)`

- **It must:** follow SPEC part 4 "WO-04". The outline check comes before anything is created.
- **Example:** `{"cls": "IfcColumn", "pts": [[1.8, 1.8], [2.2, 1.8], [2.2, 2.2], [1.8, 2.2]], "base": 0, "depth": 3}`
  is a column 0.4 m square and 3 m high.
- **May use:** `ifcopenshell.api.root.create_entity`, `ifcopenshell.api.geometry.add_slab_representation`,
  `ifcopenshell.api.geometry.assign_representation`, `ifcopenshell.api.geometry.edit_object_placement`,
  `ifcopenshell.api.spatial.assign_container`, and WO-01's four.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-04 ...`. **Score:** 0+0+1+0+1+0 = 2.

---

## [x] WO-05 [Cline] `bim_ifcos_put_opening(o)`

- **It must:** follow SPEC part 4 "WO-05": the host and size checks first (in that order), then the cut
  (`IfcOpeningElement`, `feature.add_feature`), then the door or window with the same matrix (`feature.add_filling`),
  contained where its host is. The lookup of the host has its own `try`: `by_guid` raises when the GlobalId is not in
  the file, and that answers `{"error": "no host"}`.
- **Example:** a door 0.9 wide and 2.1 high at (2, 0) on a wall along +X, depth 0.4: its opening fills the box from
  (1.55, -0.2, 0) to (2.45, 0.2, 2.1).
- **May use:** `math.cos`, `math.sin`, `ifcopenshell.api.root.create_entity`,
  `ifcopenshell.api.geometry.add_wall_representation`, `ifcopenshell.api.geometry.add_door_representation`,
  `ifcopenshell.api.geometry.add_window_representation`, `ifcopenshell.api.geometry.assign_representation`,
  `ifcopenshell.api.geometry.edit_object_placement`, `ifcopenshell.api.feature.add_feature`,
  `ifcopenshell.api.feature.add_filling`, `ifcopenshell.api.spatial.assign_container`,
  `ifcopenshell.util.element.get_container`, and WO-01's four.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-05 ...`. **Score:** 0+1+1+0+1+0 = 3, tier B.

---

## [x] WO-06 [Cline] `bim_ifcos_put_mesh(m)` and `bim_ifcos_put_psets(guid, psets)`

- **It must:** follow SPEC part 4 "WO-06". In `bim_ifcos_put_mesh` the corners go in as one list inside a list and
  the faces as one list inside a list (`vertices=[[...]]`, `faces=[[...]]`), each corner a tuple of three floats, each
  face a tuple of ints. In `bim_ifcos_put_psets` the lookup of the element has its own `try` (`{"error": "not
  found"}`), and a set whose `props` is empty or missing is passed over and not counted.
- **May use:** `ifcopenshell.api.root.create_entity`, `ifcopenshell.api.geometry.add_mesh_representation`,
  `ifcopenshell.api.geometry.assign_representation`, `ifcopenshell.api.geometry.edit_object_placement`,
  `ifcopenshell.api.spatial.assign_container`, `ifcopenshell.api.pset.add_pset`, `ifcopenshell.api.pset.edit_pset`,
  `_bim_ifcos_file.by_guid`, and WO-01's four.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-06 ...`. **Score:** 0+0+1+0+1+0 = 2.

---

## [x] WO-07 [Cline] `bim_ifcos_export(model, path)`

- **It must:** follow SPEC part 4 "WO-07": begin, then walls, prisms, openings, meshes in that order; an opening is
  put from a copy of its item (`dict(item)`) whose `host` is the GlobalId written for the wall with that `id`, or
  `''`; each error goes to `skipped` with the item's `id`, each success is counted and its `psets` written; then
  `bim_ifcos_write_read(path)` with `skipped` and `written` added to its answer.
- **Example:** a model with a wall of no length and a window hosted by it answers `skipped` of
  `[{"id": "w3", "why": "zero length"}, {"id": "d2", "why": "no host"}]`.
- **May use:** `bim_ifcos_begin`, `bim_ifcos_put_wall`, `bim_ifcos_put_prism`, `bim_ifcos_put_opening`,
  `bim_ifcos_put_mesh`, `bim_ifcos_put_psets`, `bim_ifcos_write_read` (V176), `dict`.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v177/v177.test.mjs`
- **Budget:** 45
- **Test:** the cases named `WO-07 ...`. **Score:** 0+1+1+0+1+0 = 3, tier B.

---

## [x] WO-08 [Claude] Audit step 1, then step 2's spec

Done 2026-11-14: WO-01 to WO-07 audited (`GATE-LOG.md`; two small fixes, the tests grown). Step 2a's spec is SPEC
part 7 and its work orders are below.

---

# Step 2a: the model as data, `src/js/engine/io/ifc-save.js`

Spec: SPEC part 7 (every function in full) and part 3 (the data). Every task: add its function(s) to
`src/js/engine/io/ifc-save.js` **above the file's last line (`export { ... };`)** and below what is already there,
followed by its "List" line exactly as SPEC part 7 writes it (the tests find the function through that line; without
it the task's cases are skipped and the gate refuses the task). Change nothing else: not another file, not the
header, not the `import` or `export` lines, not `canvas_v10.html` by hand (`python tools/build_app.py` rebuilds it).
ES5 only: `var`, `function`, no arrow functions, no `let` or `const`, no template strings, no `Object.assign`, no
`for...of`. Do not read `A3D`, `window` or `document`: each function works only on its arguments. Use only the names
listed in the task. Implement the whole function; never a placeholder.

After each task: `node --check src/js/engine/io/ifc-save.js`, its own cases, the build, the unit tests:

    node --test --test-name-pattern="WO-09" tests/unit/ifc-save.test.mjs
    python tools/build_app.py
    npm test

---

## [ ] WO-09 [Cline] `bimIfcSaveLevels(levels)` and `bimIfcSaveLevel(o, lv, y)`

- **It must:** follow SPEC part 7 "WO-09", then the List line `BIM_IFC_SAVE.levels=bimIfcSaveLevels;BIM_IFC_SAVE.level=bimIfcSaveLevel;`.
- **Example:** `bimIfcSaveLevels([{id: "lvl-0", name: "Ground", elev: 0}])` is `{list: [{name: "Ground", elev: 0}], at: {"lvl-0": 0}}`; with levels at 0 and 3.2, an element at height 3.1 with no level of its own is on level 0.
- **May use:** `bimIfcSaveNum`, `hasOwnProperty`, `String`.
- **Files:** `src/js/engine/io/ifc-save.js`, `tests/unit/ifc-save.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-09 ...` in `tests/unit/ifc-save.test.mjs`. **Score:** 0+0+1+0+0+0 = 1.

---

## [ ] WO-10 [Cline] `bimIfcSaveBase(o, layerName)`

- **It must:** follow SPEC part 7 "WO-10", then `BIM_IFC_SAVE.base=bimIfcSaveBase;`. `o.bim` may be missing.
- **Example:** `bimIfcSaveBase({id: "a1", t: "solid", name: "Wall_1", bim: {type: "wall"}}, "Walls")` is `{id: "a1", name: "Wall_1", psets: [{name: "BIM_Personal", props: {Type: "wall", Layer: "Walls"}}]}`.
- **May use:** `String`.
- **Files:** `src/js/engine/io/ifc-save.js`, `tests/unit/ifc-save.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-10 ...` in `tests/unit/ifc-save.test.mjs`. **Score:** 0+0+1+0+0+0 = 1.

---

## [ ] WO-11 [Cline] `bimIfcSaveWalls(o, lv, base)`

- **It must:** follow SPEC part 7 "WO-11", then `BIM_IFC_SAVE.walls=bimIfcSaveWalls;`. Add, above it, the small helper `bimIfcSaveMoved(o)` (true when the element is moved, as part 7 defines it); WO-12 uses it too. The copy of `base` is made with `for (k in base) if (base.hasOwnProperty(k))`.
- **Example:** a wall with centerline `[[0, 0], [6, 0]]`, thickness 0.2, height 3, align `"center"`, baseY 0 gives one item with `x0: 0, y0: 0, x1: 6, y1: 0, base: 0, height: 3, thickness: 0.2, offset: -0.1`.
- **May use:** `bimHasBulge`, `bimAlignOffsets`, `bimSegNormal`, `bimIfcSaveLevel` (WO-09), `bimIfcSavePt`, `bimIfcSaveNum`, `Math.sqrt`, `Math.min`, `Math.abs`.
- **Files:** `src/js/engine/io/ifc-save.js`, `tests/unit/ifc-save.test.mjs`
- **Budget:** 45
- **Test:** the cases named `WO-11 ...` in `tests/unit/ifc-save.test.mjs`. **Score:** 0+1+1+0+2+0 = 4, tier B.

---

## [ ] WO-12 [Cline] `bimIfcSavePrism(o, lv, base)`

- **It must:** follow SPEC part 7 "WO-12", then `BIM_IFC_SAVE.prism=bimIfcSavePrism;`.
- **Example:** a floor with baseY 3.2 and thickness 0.25 has `base: 2.95, depth: 0.25, cls: "IfcSlab"`; its profile `[[0, 0], [6, 0], [6, 4], [0, 4]]` becomes `pts: [[0, 0], [6, 0], [6, -4], [0, -4]]`.
- **May use:** `bimIfcSaveMoved` (WO-11), `bimRectFootprint`, `bimIfcSaveLevel`, `bimIfcSavePt`, `bimIfcSaveNum`.
- **Files:** `src/js/engine/io/ifc-save.js`, `tests/unit/ifc-save.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-12 ...` in `tests/unit/ifc-save.test.mjs`. **Score:** 0+0+1+0+1+0 = 2.

---

## [ ] WO-13 [Cline] `bimIfcSaveOpening(o, walls, base)`

- **It must:** follow SPEC part 7 "WO-13", then `BIM_IFC_SAVE.opening=bimIfcSaveOpening;`. A host id of `"w"` must not match the wall `"w1"`: compare the whole id, or the id up to `#`.
- **Example:** a door with center `[2, 0.05]`, width 0.9, height 2.1 on the wall item `{id: "w1", x0: 0, y0: 0, x1: 6, y1: 0, base: 0, thickness: 0.2}` gives `host: "w1", x: 2, y: 0, a: 0, base: 0, depth: 0.4, cls: "IfcDoor"`.
- **May use:** `bimIfcSavePt`, `bimIfcSaveNum`, `Math.atan2`, `Math.max`, `Math.min`, `String`, `indexOf`.
- **Files:** `src/js/engine/io/ifc-save.js`, `tests/unit/ifc-save.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-13 ...` in `tests/unit/ifc-save.test.mjs`. **Score:** 0+1+1+0+1+0 = 3, tier B.

---

## [ ] WO-14 [Cline] `bimIfcSaveMesh(o, m, lv, base)`

- **It must:** follow SPEC part 7 "WO-14", then `BIM_IFC_SAVE.mesh=bimIfcSaveMesh;`.
- **Example:** a corner `[1, 2, 1]` of an element with pos `[10, 3.2, 0]` becomes `[11, -1, 5.2]`; the face `[0, 1, 2, 3]` becomes `[0, 1, 2]` and `[0, 2, 3]`.
- **May use:** `BIM_IFC_SAVE_CLASS`, `bimIfcSaveLevel`, `bimIfcSavePt3`, `Math.min`, `String`, a regular expression.
- **Files:** `src/js/engine/io/ifc-save.js`, `tests/unit/ifc-save.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-14 ...` in `tests/unit/ifc-save.test.mjs`. **Score:** 0+0+1+0+1+0 = 2.

---

## [ ] WO-15 [Cline] `bimIfcSaveModel(name, levels, entries)`

- **It must:** follow SPEC part 7 "WO-15", then `BIM_IFC_SAVE.model=bimIfcSaveModel;`. Openings are handled after every other entry, so their walls are already in `model.walls`.
- **Example:** `bimIfcSaveModel("", [], [])` is `{model: {name: "Project", levels: [], walls: [], prisms: [], openings: [], meshes: []}, left: []}`.
- **May use:** `bimIfcSaveLevels`, `bimIfcSaveBase`, `bimIfcSaveWalls`, `bimIfcSavePrism`, `bimIfcSaveMesh`, `bimIfcSaveOpening`, `concat`, `String`.
- **Files:** `src/js/engine/io/ifc-save.js`, `tests/unit/ifc-save.test.mjs`
- **Budget:** 35
- **Test:** the cases named `WO-15 ...` in `tests/unit/ifc-save.test.mjs`. **Score:** 0+1+1+0+1+0 = 3, tier B.

---

## [ ] WO-16 [Claude] Step 2b

Claude's: audit WO-09 to WO-15; the wheels and the LGPL, GPL and CGAL notices in `runtime/ifcos/` and
`runtime/MANIFEST.json`; `tools/embed_py.py` for `bim_ifcos.py`; the IFC worker; File > Export > IFC; Make editable
for imported walls and floors (the walls-and-slabs reader's parameters kept at import); the browser check.
