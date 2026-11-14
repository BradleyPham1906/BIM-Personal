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

## [ ] WO-06 [Cline] `bim_ifcos_put_mesh(m)` and `bim_ifcos_put_psets(guid, psets)`

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

## [ ] WO-07 [Cline] `bim_ifcos_export(model, path)`

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

## [ ] WO-08 [Claude] Audit step 1, then step 2's spec

Claude's: audit WO-01 to WO-07; then step 2 (SPEC part 2): the wheels and their licence texts in `runtime/` and its
manifest, the worker, `io/ifc-save.js` (the model as SPEC part 3's data, Cline's with unit tests), File, Export, IFC,
Make editable for imported walls and floors, and the phase's one browser check.
