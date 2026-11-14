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
| 2a | The model as that data: `src/js/engine/io/ifc-save.js` (part 7) | Cline, WO-09 to WO-15 | ready |
| 2b | The wheels and their licence texts in `runtime/`, the worker, File > Export > IFC, Make editable, the browser check | Claude (protected paths and the worker), spec to follow | next |

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

## 7. Step 2a: the model as data (all in `src/js/engine/io/ifc-save.js`, ES5)

The file's header (Claude's) has `BIM_IFC_SAVE` (the file's functions by name, for the tests), `BIM_IFC_SAVE_CLASS`
(the IFC class by `bim.type`), `bimIfcSaveNum(v)` (a number to 4 decimals, never minus zero), `bimIfcSavePt([x, z])`
(IFC's `[X, Y]` = `[x, -z]`) and `bimIfcSavePt3([x, y, z])` (`[x, -z, y]`). Every number put in an item goes through
`bimIfcSaveNum`. Each function below is followed by its line in the list, as written. No function reads `A3D` or
the page: each is given what it works on. `base` is what `bimIfcSaveBase` answered for the element; "a copy of
`base`" is a new object with each of `base`'s own keys.

An element is "moved" when any of `o.pos`'s three numbers is over 1e-9 in size (a missing `pos` is not moved).

### WO-09: `bimIfcSaveLevels(levels)` and `bimIfcSaveLevel(o, lv, y)`
- `bimIfcSaveLevels`: `{list: [{name, elev}], at: {<level id>: <its index in list>}}`, in the order given; `name`
  is `String(l.name || ('Level ' + i))`; `null` or `[]` gives `{list: [], at: {}}`.
- `bimIfcSaveLevel`: `lv.at[o.bim.levelId]` when `o.bim` has a `levelId` that `lv.at` has (`hasOwnProperty`); else
  the index of the level with the greatest `elev` that is not above `y + 1e-6`; none: 0.
- List: `BIM_IFC_SAVE.levels=bimIfcSaveLevels;BIM_IFC_SAVE.level=bimIfcSaveLevel;`

### WO-10: `bimIfcSaveBase(o, layerName)`
- `{id: o.id, name: String(o.name || o.id), psets: [...]}`, and `guid: o.bim.guid` only when it is a string of 22
  characters. `psets` starts with `{name: 'BIM_Personal', props: {Type: String(bim.type || o.t || ''), Layer:
  String(layerName || '')}}`; then, for each of `o.bim.psets` (an imported element's: `{name, rows: [[key, value],
  ...]}`), `{name: String(name), props: {...}}` with each row that has a key as `String(key): String(value)` (a
  `null` value is `''`); a set with no such row, with no name, or named `BIM_Personal`, is left out.
- List: `BIM_IFC_SAVE.base=bimIfcSaveBase;`

### WO-11: `bimIfcSaveWalls(o, lv, base)`
- `null` unless `o.bim.type` is `'wall'`, its `centerline` has 2 or more points, `bimHasBulge(o.bim.bulges)` is
  false, the element is not moved, and its `thickness` and `height` are above 0.
- The sides: `off = bimAlignOffsets(bim.thickness, bim.align)` (`{dLeft, dRight}`). The segments: from point `i` to
  point `i + 1`, and, when `bim.closed` and there are more than 2 points, from the last back to the first. A segment
  shorter than 1e-6 is passed over. For a segment from `a` to `q` (plan points), with `dx = q[0] - a[0]`,
  `dz = q[1] - a[1]`, `len` its length and `nr = bimSegNormal(a, q)`: `s = (nr[0] * dz - nr[1] * dx) / len` (1 or
  -1: which side of IFC's line the app's left is on).
- Each segment's item: a copy of `base`, and `level: bimIfcSaveLevel(o, lv, bim.baseY)`, `x0, y0` from
  `bimIfcSavePt(a)`, `x1, y1` from `bimIfcSavePt(q)`, `base: bim.baseY`, `height`, `thickness: off.dLeft +
  off.dRight`, `offset: Math.min(s * off.dLeft, -s * off.dRight)`. Every item after the first written has
  `id: o.id + '#' + i` (`i` the segment's index, counting passed-over ones) and no `guid`. When more than one item
  is written each `name` is `base.name + ' ' + (its place in the answer, from 1)`.
- Returns the items, or `null` when none was written.
- List: `BIM_IFC_SAVE.walls=bimIfcSaveWalls;`

### WO-12: `bimIfcSavePrism(o, lv, base)`
- `null` when the element is moved. A floor (`bim.type` `'floor'`, a `profile` of 3 or more points, `thickness`
  above 0): `cls: 'IfcSlab'`, the outline `bim.profile`, `base: bim.baseY - bim.thickness` (a floor hangs under its
  `baseY`), `depth: bim.thickness`. A column (`bim.type` `'column'`, no `bim.section`, a `center`, `width`, `depth`
  and `height` above 0): `cls: 'IfcColumn'`, the outline `bimRectFootprint(bim.center, bim.width, bim.depth,
  bim.rotation || 0)`, `base: bim.baseY`, `depth: bim.height`. Anything else: `null`.
- The item: `{cls}` and a copy of `base`, `level: bimIfcSaveLevel(o, lv, bim.baseY)`, `pts` (each outline point
  through `bimIfcSavePt`), `base`, `depth`.
- List: `BIM_IFC_SAVE.prism=bimIfcSavePrism;`

### WO-13: `bimIfcSaveOpening(o, walls, base)`
- `walls` are wall items already made (WO-11). `null` unless `o.t` is `'opening'`, `o.bim.type` is `'door'` or
  `'window'`, it has a `center`, and its `width` and `height` are above 0.
- Its segment: among the items whose `id` is `bim.hostWallId` or starts with `bim.hostWallId + '#'`, the one nearest
  the centre `c = bimIfcSavePt(bim.center)`: for each, `t` = the centre's place along the segment, held between 0
  and 1 (`((c[0] - x0) * dx + (c[1] - y0) * dy) / (dx * dx + dy * dy)`), and the distance from `c` to that point.
  None: `null`.
- The item: a copy of `base`, `cls` (`'IfcWindow'` for a window, else `'IfcDoor'`), `host` (the segment's `id`),
  `x, y` (the point on the segment at `t`), `a: Math.atan2(y1 - y0, x1 - x0)` (not rounded), `base: segment.base +
  (bim.sillHeight || 0)`, `width`, `height`, `depth: segment.thickness + 0.2`.
- List: `BIM_IFC_SAVE.opening=bimIfcSaveOpening;`

### WO-14: `bimIfcSaveMesh(o, m, lv, base)`
- `m` is the element's mesh (`{v: [[x, y, z]], f: [[i, j, k, ...]]}`). `null` when there is no `m`, `m.v` or `m.f`.
- The item: a copy of `base`, `verts` (each corner plus `o.pos`, through `bimIfcSavePt3`), `faces` (each face of 3
  or more corners as a fan of triangles from its first corner: `[f[0], f[j - 1], f[j]]` for `j` from 2), `cls`,
  `level: bimIfcSaveLevel(o, lv, <the lowest y of its corners, with pos>)`. No triangle: `null`.
- `cls`: for an imported element (`bim.imported`) whose `bim.ifcType` matches `/^Ifc[A-Za-z0-9]+$/`, that name
  without a trailing `StandardCase` or `ElementedCase`; else `BIM_IFC_SAVE_CLASS[bim.type]`; else
  `'IfcBuildingElementProxy'`.
- List: `BIM_IFC_SAVE.mesh=bimIfcSaveMesh;`

### WO-15: `bimIfcSaveModel(name, levels, entries)`
- `entries` is `[{o, mesh, layer}]`: an element, its mesh (or `null`), its layer's name.
- `lv = bimIfcSaveLevels(levels)`; the model `{name: String(name || 'Project'), levels: lv.list, walls: [],
  prisms: [], openings: [], meshes: []}`. For each entry, `base = bimIfcSaveBase(o, layer)`; an `o.t` of
  `'opening'` is kept for later; else the first of these that does not answer `null`: `bimIfcSaveWalls` (its items
  added to `walls`), `bimIfcSavePrism` (to `prisms`), `bimIfcSaveMesh(o, mesh, lv, base)` (to `meshes`); all `null`:
  `{id: o.id, why: 'no shape'}` to `left`. Then each kept opening: `bimIfcSaveOpening(o, model.walls, base)` to
  `openings`, or `{id: o.id, why: 'its wall is not written as a straight wall'}` to `left`.
- Returns `{model, left}`.
- List: `BIM_IFC_SAVE.model=bimIfcSaveModel;`
