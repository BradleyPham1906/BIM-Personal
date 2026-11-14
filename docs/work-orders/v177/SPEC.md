# V177 spec: Save as IFC through IfcOpenShell, and imported IFC walls and floors made editable

Research: `docs/research/research-ifcopenshell-app.md` (the owner's D1 to D4, 2026-11-13: IfcOpenShell's wheel as a
separate file run only in the Python worker; walls, floors, doors, windows and columns as real IFC elements and
everything else as shapes; editing imported walls and slabs in this phase; File, Export, IFC). Implementation target:
local `main`. Written by Claude, 2026-11-13. Cline reads this with TASKS.md.

## 1. What it does for the user

File, Export, IFC writes the model as an IFC4 file other BIM programs open: the levels as storeys, straight walls,
floors, doors and windows (each cutting its wall) and columns as IFC's own elements, everything else with its shape
and its IFC class. An element that came from an IFC file keeps its GlobalId. An imported wall or floor can be made
editable: it becomes one of the app's own walls or floors, and is saved back under the same GlobalId.

## 2. The steps

| Step | What | Who | State |
|---|---|---|---|
| 1 | The adapter: a model, as plain data, written as an IFC file (part 4) | Cline, WO-01 to WO-07 | ready |
| 2 | The app's side: the model as that data (`io/ifc-save.js`), the wheels in `runtime/` with their licence texts, the worker, the command, Make editable | Claude writes its spec after step 1 ships; the runtime, the worker and the command are Claude's | next |

Step 1 changes one file, `src/py/bim_ifcos.py`; nothing in the app calls it yet, so `canvas_v10.html` does not change.

## 3. Data: the model the app hands the adapter

Metres. IFC's axes: X east, Y north, Z up (the app's x, minus its z, its y; step 2 converts). Angles in radians,
anticlockwise from +X. Every item may carry `id` (the app's id, any string), `guid` (an IFC GlobalId to keep, else a
new one is made), `name`, `level` (the index of its level in `levels`; missing or out of range: the first) and
`psets` (`[{"name": "BIM_Personal", "props": {"Layer": "Walls"}}]`).

    {"name": "House",
     "levels":   [{"name": "Ground", "elev": 0}, {"name": "First", "elev": 3.2}],
     "walls":    [{"id", "guid", "name", "level", "x0", "y0", "x1", "y1", "base", "height", "thickness", "offset"}],
     "prisms":   [{"id", "guid", "name", "level", "cls", "pts": [[x, y], ...], "base", "depth"}],
     "openings": [{"id", "guid", "name", "cls", "host", "x", "y", "a", "base", "width", "height", "depth"}],
     "meshes":   [{"id", "guid", "name", "level", "cls", "verts": [[x, y, z], ...], "faces": [[i, j, k], ...]}]}

- A wall runs from (x0, y0) to (x1, y1); `base` is the height of its foot above the project's zero (not above its
  storey); `offset` is where its body starts across the line: 0 puts the body on the line's left, `-thickness/2`
  centres it.
- A prism is an outline raised by `depth` from `base`: a floor (`cls` `"IfcSlab"`), a column (`"IfcColumn"`).
- An opening is a door or a window (`cls` `"IfcDoor"` or `"IfcWindow"`): `host` is its wall (the wall's `id` in the
  model for `bim_ifcos_export`; the wall's GlobalId for `bim_ifcos_put_opening`), (x, y) the middle of its width on
  the wall's line, `a` the wall's direction, `base` its foot above zero, `depth` how far the cut goes through the wall
  (the wall's thickness and a margin).
- A mesh is any other element: its corners and its faces (indices into `verts`), and its IFC class.

Every function answers a plain dict and never raises: a failure is `{"error": "<reason>"}`. The reasons: `"no
project"` (nothing begun), the function's own (below), and `"failed"` for any other exception.

## 4. Functions (all in `src/py/bim_ifcos.py`, below V176's)

`f` is `_bim_ifcos_file`. Every `ifcopenshell.api` call is `ifcopenshell.api.<module>.<function>(f, ...)` with the
keyword arguments written here.

### WO-01: four small parts
- `bim_ifcos_matrix(x, y, z, a)`: the 4 x 4 numpy matrix (floats) that turns by `a` about Z and moves to (x, y, z):
  `[[cos a, -sin a, 0, x], [sin a, cos a, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]`.
- `bim_ifcos_storey(level)`: `f.by_type("IfcBuildingStorey")[level]` when `level` is an int inside the list, else
  the first storey.
- `bim_ifcos_body()`: the `IfcGeometricRepresentationSubContext` whose `ContextIdentifier` is `"Body"`.
- `bim_ifcos_keep_guid(product, guid)`: when `guid` is a str of 22 characters, all from
  `0-9 A-Z a-z _ $`, and no entity in `f` has it (`f.by_guid(guid)` raises), set `product.GlobalId = guid`.
  Always answers `product.GlobalId`.

### WO-02: `bim_ifcos_begin(name, levels)`
- **Does:** an empty `levels` is `[{"name": "Level 0", "elev": 0}]`. `bim_ifcos_new_project(name, levels[0]["elev"])`
  (V176; its error is answered as it is); the first storey's `Name` becomes `levels[0]["name"]`; for each further
  level an `IfcBuildingStorey` (`root.create_entity`) with its `Name` and `Elevation`,
  `aggregate.assign_object(f, products=[storey], relating_object=<the IfcBuilding>)`; then every storey is placed:
  `geometry.edit_object_placement(f, product=storey, matrix=bim_ifcos_matrix(0, 0, storey.Elevation, 0))`.
- **Returns:** `bim_ifcos_summary('')`.

### WO-03: `bim_ifcos_put_wall(w)`
- **Does:** length `L = math.hypot(x1 - x0, y1 - y0)`; under 1e-9: `{"error": "zero length"}`, nothing added. An
  `IfcWall` named `w["name"]`; `geometry.add_wall_representation(f, context=bim_ifcos_body(), length=L,
  height=w["height"], thickness=w["thickness"], offset=w.get("offset", 0))`, `geometry.assign_representation(f,
  product=wall, representation=rep)`; `geometry.edit_object_placement(f, product=wall, matrix=bim_ifcos_matrix(x0, y0,
  w["base"], atan2(y1 - y0, x1 - x0)))`; `spatial.assign_container(f, products=[wall],
  relating_structure=bim_ifcos_storey(w.get("level")))`.
- **Returns:** `{"guid": bim_ifcos_keep_guid(wall, w.get("guid"))}`.

### WO-04: `bim_ifcos_put_prism(p)`
- **Does:** fewer than 3 points, or a depth missing or not above 0: `{"error": "bad outline"}`, nothing added. An
  element of class `p.get("cls") or "IfcSlab"`; `geometry.add_slab_representation(f, context=bim_ifcos_body(),
  depth=p["depth"], polyline=[(float(x), float(y)), ...])` (the outline as it is, in the world), assigned; placed with
  `bim_ifcos_matrix(0, 0, p["base"], 0)`; contained in its storey.
- **Returns:** `{"guid": bim_ifcos_keep_guid(element, p.get("guid"))}`.

### WO-05: `bim_ifcos_put_opening(o)`
- **Does:** the host `f.by_guid(o["host"])`; not there, or not an `IfcWall` (`host.is_a("IfcWall")`):
  `{"error": "no host"}`. A width, height or depth not above 0: `{"error": "bad size"}`. The matrix
  `M = bim_ifcos_matrix(x - cos(a) * width / 2, y - sin(a) * width / 2, base, a)`. The cut: an `IfcOpeningElement`,
  its body `geometry.add_wall_representation(f, context=body, length=width, height=height, thickness=depth,
  offset=-depth / 2)`, assigned, placed with `M`, `feature.add_feature(f, feature=opening, element=host)`. The door or
  window: an `IfcWindow` when `o["cls"]` is `"IfcWindow"`, else an `IfcDoor`; its body
  `geometry.add_window_representation(f, context=body, overall_height=height, overall_width=width)` or
  `geometry.add_door_representation(...)` with the same arguments, assigned, placed with `M`;
  `feature.add_filling(f, opening=opening, element=element)`; contained where its host is
  (`ifcopenshell.util.element.get_container(host)`).
- **Returns:** `{"guid": bim_ifcos_keep_guid(element, o.get("guid")), "opening": opening.GlobalId}`.

### WO-06: `bim_ifcos_put_mesh(m)` and `bim_ifcos_put_psets(guid, psets)`
- `bim_ifcos_put_mesh`: no `verts` or no `faces`: `{"error": "empty mesh"}`. An element of class `m.get("cls") or
  "IfcBuildingElementProxy"`; `geometry.add_mesh_representation(f, context=bim_ifcos_body(), vertices=[[(x, y, z),
  ...]], faces=[[(i, j, k), ...]])` (one list of corners inside a list, one list of faces inside a list; tuples of
  floats and of ints), assigned; placed with `bim_ifcos_matrix(0, 0, 0, 0)`; contained in its storey. Returns
  `{"guid": bim_ifcos_keep_guid(element, m.get("guid"))}`. A class IFC4 does not have raises inside
  `root.create_entity`: `{"error": "failed"}`.
- `bim_ifcos_put_psets`: the element `f.by_guid(guid)`; not there: `{"error": "not found"}`. For each set with a
  non-empty `props`: `pset.add_pset(f, product=element, name=set["name"])`, then `pset.edit_pset(f, pset=pset,
  properties=set["props"])`. Returns `{"psets": <how many were written>}`.

### WO-07: `bim_ifcos_export(model, path)`
- **Does:** `bim_ifcos_begin(model.get("name") or "Project", model.get("levels") or [])` (its error answered as it
  is). Then, in this order, every item of `walls` (`bim_ifcos_put_wall`), `prisms` (`bim_ifcos_put_prism`),
  `openings` (`bim_ifcos_put_opening`, on a copy of the item whose `host` is the GlobalId written for the wall with
  that `id`, or `''` when there is none) and `meshes` (`bim_ifcos_put_mesh`). An item that answers an error is added
  to `skipped` as `{"id": item.get("id"), "why": <the error>}`; one that is written is counted, its GlobalId kept
  under its `id`, and its `psets`, when it has any, written with `bim_ifcos_put_psets`. Last,
  `bim_ifcos_write_read(path)` (V176).
- **Returns:** what `bim_ifcos_write_read` answered, with `"skipped"` (the list, in the order met) and `"written"`
  (the count): `{"bytes", "summary", "skipped", "written"}`.

## 5. Order of the work

WO-01 to WO-07, in order: each uses the ones before it. After each:
`node --test --test-name-pattern="WO-0N" docs/work-orders/v177/v177.test.mjs` (about 30 s: IfcOpenShell's start in
Node), then `npm test`.

## 6. Not in step 1

Nothing in the app (no `.js`, no menu, no worker, no wheels in `runtime/`): step 2. No curved walls as IFC walls
(step 2 sends them as meshes), no materials, colours or types, no IFC2x3.
