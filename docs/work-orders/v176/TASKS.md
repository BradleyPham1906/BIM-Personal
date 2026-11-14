# V176 work orders: IfcOpenShell in the app's own Python

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every task: add one function to `src/py/bim_ifcos.py`, below the file's header and imports, and change nothing else:
not another file, not the header, no `import` line (every module the tasks need is imported already: `math`, `os`,
`numpy`, `ifcopenshell` and its `api` and `util` modules; the gate refuses an added import), not `canvas_v10.html`. Python 3.13 (Pyodide). Use only the names listed in the
task and in SPEC part 4; every `ifcopenshell.api` call is `ifcopenshell.api.<module>.<function>(file, ...)` with
keyword arguments as the spec writes them. A function answers a plain dict; on a failure it answers
`{"error": "..."}` and never raises. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v176/v176.test.mjs`, outside `npm test` (the first run downloads the pinned wheels,
about 7 MB, into `.cache/ifcos/`; later runs use the cache). After each task run its own cases, then the unit tests:

    node --test --test-name-pattern="WO-01" docs/work-orders/v176/v176.test.mjs
    npm test

Scores are from `../ROUTING.md` (files, logic, understanding, judgment, trickiness, check).

---

## [x] WO-01 [Cline] `bim_ifcos_summary(path)`

- **It must:** answer the summary of SPEC part 3 for `ifcopenshell.open(path)`, or for `_bim_ifcos_file` when `path`
  is `''`. `products`: every `file.by_type("IfcProduct")` counted by `element.is_a()`, leaving out
  `"IfcOpeningElement"`. `storeys`: each `IfcBuildingStorey` in `by_type` order as `{"name": s.Name,
  "elevation": round((s.Elevation or 0) * scale, 6)}` with `scale = ifcopenshell.util.unit.calculate_unit_scale(file)`.
  `schema`: `file.schema`. A missing path: `{"error": "not found"}`; `''` with no project: `{"error": "no project"}`;
  any exception while reading: `{"error": "unreadable"}`.
- **Example:** the test's IFC gives `{"schema": "IFC4", "products": {"IfcBuilding": 1, "IfcBuildingStorey": 1,
  "IfcSite": 1, "IfcWall": 1}, "storeys": [{"name": "Level 1", "elevation": 3.5}]}`.
- **May use:** `os.path.exists`, `ifcopenshell.open`,
  `ifcopenshell.util.unit.calculate_unit_scale`, `_bim_ifcos_file`.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v176/v176.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-01 ...`. **Score:** 0+0+1+0+1+0 = 2.

---

## [x] WO-02 [Cline] `bim_ifcos_new_project(name, elevation)`

- **It must:** do exactly what SPEC part 4 lists, in that order, keep the new file in `_bim_ifcos_file`
  (`global _bim_ifcos_file`), and answer `bim_ifcos_summary('')`. Units in metres: three `unit.add_si_unit` calls
  (`"LENGTHUNIT"`, `"AREAUNIT"`, `"VOLUMEUNIT"`, no prefix) passed together to `unit.assign_unit(f, units=[...])`.
- **Example:** `bim_ifcos_new_project("Test project", 0)` answers `{"schema": "IFC4", "products": {"IfcBuilding": 1,
  "IfcBuildingStorey": 1, "IfcSite": 1}, "storeys": [{"name": "Level 0", "elevation": 0}]}`.
- **May use:** `ifcopenshell.api.project.create_file`, `ifcopenshell.api.root.create_entity`,
  `ifcopenshell.api.unit.add_si_unit`, `ifcopenshell.api.unit.assign_unit`, `ifcopenshell.api.context.add_context`,
  `ifcopenshell.api.aggregate.assign_object`, `bim_ifcos_summary` (WO-01).
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v176/v176.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-02 ...`. **Score:** 0+0+1+0+1+0 = 2.

---

## [ ] WO-03 [Cline] `bim_ifcos_add_wall(name, x0, y0, x1, y1, height, thickness)`

- **It must:** follow SPEC part 4: the first `IfcBuildingStorey` of `_bim_ifcos_file`; the Body sub-context (the
  `IfcGeometricRepresentationSubContext` whose `ContextIdentifier` is `"Body"`); length `math.hypot(x1 - x0, y1 - y0)`;
  the placement matrix as written there (`numpy.array`, floats); answer `{"guid": wall.GlobalId}`. No project:
  `{"error": "no project"}`. Length under 1e-9: `{"error": "zero length"}`, nothing added.
- **Example:** after `bim_ifcos_new_project("Walls", 0)`, `bim_ifcos_add_wall("Wall B", 0, 0, 0, 4, 3, 0.2)` places
  the wall at (0, 0) turned a quarter turn (its X axis along +Y).
- **May use:** `ifcopenshell.api.root.create_entity`, `ifcopenshell.api.geometry.add_wall_representation`,
  `ifcopenshell.api.geometry.assign_representation`, `ifcopenshell.api.geometry.edit_object_placement`,
  `ifcopenshell.api.spatial.assign_container`, `math`, `numpy`, `_bim_ifcos_file`.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v176/v176.test.mjs`
- **Budget:** 45
- **Test:** the cases named `WO-03 ...`. **Score:** 0+0+1+0+2+0 = 3, tier B.

---

## [ ] WO-04 [Cline] `bim_ifcos_write_read(path)`

- **It must:** no project: `{"error": "no project"}`; else `_bim_ifcos_file.write(path)` and answer
  `{"bytes": os.path.getsize(path), "summary": bim_ifcos_summary(path)}`.
- **May use:** `os.path.getsize`, `bim_ifcos_summary` (WO-01), `_bim_ifcos_file`.
- **Files:** `src/py/bim_ifcos.py`, `docs/work-orders/v176/v176.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-04 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-05 [Claude] Review, then V177's spec

Claude's: review WO-01 to WO-04 against SPEC part 4 and the research; record the times in the research note; write
V177's research and spec (the wheels pinned in `runtime/` with the LGPL and GPL texts, loaded in the Python worker;
Save as IFC; editable imported walls and slabs).
