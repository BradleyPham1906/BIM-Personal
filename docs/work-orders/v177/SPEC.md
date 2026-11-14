# V177 spec: Save as IFC, through IfcOpenShell

Research: `docs/research/research-ifcopenshell-app.md`. The owner's decisions, 2026-11-14: **D1 (a)**, GPL and AGPL
libraries are allowed as separate files run only in the Python worker (this also settles Ladybug; CLAUDE.md's
library rule is reworded in WO-19); **D2 as recommended**, V177 saves levels, walls, floors, doors and windows with
their openings, and columns, and every other solid as a mesh, so nothing is missing from the file; **D3 as
recommended**, editing imported IFC elements waits until the import engine is settled (That Open); **D4 as
recommended**, File, Export, "IFC (.ifc)", beside DXF and glTF. Implementation target: local `main`. Written by
Claude, 2026-11-14. Cline reads this with TASKS.md.

## 1. What it does for the user

File, Export, IFC (.ifc) writes the model as an IFC4 file that Revit, Archicad, Bonsai and any IFC viewer open:
one storey per level, walls as `IfcWall` with their real thickness and side, floors as `IfcSlab`, rectangular columns
as `IfcColumn`, each door and window as an `IfcDoor` or `IfcWindow` filling an opening cut in its wall, and every
other solid (roofs, stairs, beams, imported meshes) as a mesh of its own class or `IfcBuildingElementProxy`. Each
element carries a property set `BIM_Personal` with the app's id and name. The first export in a session takes 4 to 5
seconds while the worker loads IfcOpenShell; the status line says so. Phone, tablet and desktop alike: the command is
in the File menu and the command palette (`IFCOUT`).

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/py/bim_ifcos.py` | changed | eight new adapter functions (part 4.1); its header imports `feature` and `pset` (done) | Cline, WO-01 to WO-08 |
| `src/js/engine/io/ifc-export.js` | new, in the build after `gltf.js` (header done) | the app's model as the plain model (part 4.2) | Cline, WO-09 to WO-17 |
| `docs/work-orders/v177/v177.test.mjs` | new | the Python cases, in the app's Pyodide (V176's setup) | Claude (done) |
| `docs/work-orders/v177/v177-js.test.mjs` | new | the JavaScript cases | Claude (done) |
| `runtime/wheels/`, `runtime/MANIFEST.json`, `THIRD_PARTY_NOTICES.md` | changed | the seven wheels pinned, the LGPL-3.0 and GPL-3.0 texts beside them | Claude, WO-18 |
| `src/js/engine/ladybug/runtime.js` or a sibling | changed | the worker loads the IFC wheels on the first IFC call and runs `bim_ifcos.py` | Claude, WO-18 |
| `src/js/engine/io/ifc-export.js`, `ui/`, `commands/` | changed | `bimIfcExport()`: model to worker to a download; the menu item and `IFCOUT` | Claude, WO-18 |

## 3. Data

**The plain model** (JSON; what `bimIfcxModel` returns and `bim_ifcos_save_model` takes). Metres; IFC's axes:
X east, Y north, Z up. The app's plan point `[x, z]` is IFC `[x, -z]`; the app's height `y` is IFC `Z`.

```
{ name: 'House',
  levels:   [{id:'L0', name:'Ground', elevation:0}, ...],                    // by elevation, low first
  walls:    [{id, host, name, level, x0, y0, x1, y1, z, height, thickness, offset}],   // one per straight segment
  slabs:    [{id, name, level, points:[[x,y],...], z, depth}],                // z is the slab's bottom
  columns:  [{id, name, level, x, y, z, width, depth, height, rotation}],     // rotation in radians about Z
  openings: [{id, name, kind:'door'|'window', wall, along, sill, width, height}],  // wall: a walls[].id
  meshes:   [{id, name, level, ifcClass, vertices:[[x,y,z],...], faces:[[i,j,k,...],...]}],
  psets:    [{id, name:'BIM_Personal', props:{AppId, Name}}] }
```

A wall entry's body spans `offset` to `offset + thickness` across its line, measured to the left of the direction
x0,y0 to x1,y1 (IfcOpenShell's `add_wall_representation`). The app keeps a wall's sides as `dLeft` and `dRight`
about its centreline, its "left" being the app's normal `(-dz, dx)`, which in IFC's plan is the line's right: so
`thickness = dLeft + dRight` and `offset = -dLeft`. `align`: `'left'` is `{dLeft:0, dRight:t}`, `'right'` is
`{dLeft:t, dRight:0}`, an object `{dLeft, dRight}` is used as it is, anything else `{dLeft:t/2, dRight:t/2}`
(the same rule as `bimAlignOffsets` in `bim/footings.js`, written out again because the work orders use no other
file's names).

**The adapter's answers** are plain dicts: `{"guid": ...}` for an element, `{"error": "<reason>"}` for a failure,
never an exception. Reasons: `no project`, `no storey`, `no wall`, `no element`, `zero length`, `bad size`,
`too few points`, `bad kind`, `empty mesh`, `bad face`, `bad pset`, `bad model`, `unreadable`.

## 4. Functions

### 4.1 Python, `src/py/bim_ifcos.py` (Cline, WO-01 to WO-08)

The project is `_bim_ifcos_file`. "The body context" is the `IfcGeometricRepresentationSubContext` whose
`ContextIdentifier` is `"Body"`. "Place at (x, y, z, a)" is `ifcopenshell.api.geometry.edit_object_placement(f,
product=e, matrix=M)` with `M = numpy.array([[cos a, -sin a, 0, x], [sin a, cos a, 0, y], [0, 0, 1, z], [0, 0, 0, 1]],
dtype=float)`, as `bim_ifcos_add_wall` does. "Contain in" is `ifcopenshell.api.spatial.assign_container(f,
products=[e], relating_structure=storey)`. "A storey by guid" is `f.by_guid(guid)` inside `try`, `None` when it
raises or `not e.is_a("IfcBuildingStorey")` (likewise `IfcWall`, `IfcProduct`). Every function: no project, `{"error":
"no project"}`; any exception, `{"error": "unreadable"}`.

- **WO-01 `bim_ifcos_add_storey(name, elevation)`**: an `IfcBuildingStorey` named `name`, `Elevation = elevation`,
  aggregated (`aggregate.assign_object`) to the first `IfcBuilding`. Answers `{"guid"}`.
- **WO-02 `bim_ifcos_add_wall_on(storey_guid, name, x0, y0, x1, y1, z, height, thickness, offset)`**: as
  `bim_ifcos_add_wall`, but on the given storey, at height `z` (not the storey's elevation), with
  `add_wall_representation(..., offset=offset)`. Errors in this order: `no storey`; length under 1e-9 `zero length`;
  `height <= 0` or `thickness <= 0` `bad size`. Nothing is added on an error.
- **WO-03 `bim_ifcos_add_slab(storey_guid, name, points, z, depth)`**: `points` a list of `[x, y]`, at least 3
  (`too few points`); `depth <= 0` `bad size`. The polyline is the points as float tuples, closed by repeating the
  first when the last differs. `IfcSlab`; `geometry.add_slab_representation(f, context=body, depth=depth,
  polyline=poly)`; assign; place at (0, 0, z, 0); contain.
- **WO-04 `bim_ifcos_add_column(storey_guid, name, x, y, z, width, depth, height, rotation)`**: any size `<= 0` `bad
  size`. `IfcColumn`; profile `f.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=width,
  YDim=depth)`; `geometry.add_profile_representation(f, context=body, profile=prof, depth=height)`; assign; place at
  (x, y, z, rotation); contain.
- **WO-05 `bim_ifcos_add_opening(wall_guid, kind, name, along, sill, width, height, thickness, offset)`**: errors in
  order `no wall`, `bad kind` (not `"door"`/`"window"`), `bad size` (width, height or thickness `<= 0`). `W` is the
  wall's placement, `ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)`. The opening: an
  `IfcOpeningElement` named `name + " opening"`, body `add_wall_representation(f, context=body, length=width,
  height=height, thickness=thickness + 0.1)`, placed by `numpy.dot(W, M(along - width/2, offset - 0.05, sill, 0))`,
  `feature.add_feature(f, feature=opening, element=wall)`. The filling: `IfcDoor` or `IfcWindow` named `name`, body
  `geometry.add_door_representation(f, context=body, overall_height=height, overall_width=width)` or
  `add_window_representation` with the same keywords, `OverallHeight` and `OverallWidth` set, placed by
  `numpy.dot(W, M(along - width/2, offset, sill, 0))`, `feature.add_filling(f, opening=opening, element=fill)`,
  contained in the wall's storey (`ifcopenshell.util.element.get_container(wall)`). Answers `{"guid": fill,
  "opening": opening}` (their GlobalIds).
- **WO-06 `bim_ifcos_add_mesh(storey_guid, name, ifc_class, vertices, faces)`**: `vertices` `[[x, y, z], ...]`,
  `faces` lists of indices. Empty either: `empty mesh`. A face shorter than 3, or an index not an `int` in
  `0 .. len(vertices) - 1`: `bad face`. `ifc_class` not in `BIM_IFCOS_CLASSES` (a list the task adds above the
  function: `IfcBuildingElementProxy, IfcWall, IfcSlab, IfcRoof, IfcStair, IfcBeam, IfcColumn, IfcRailing,
  IfcCovering, IfcFooting, IfcMember, IfcPlate, IfcFurniture, IfcSpace`) becomes `IfcBuildingElementProxy`.
  `geometry.add_mesh_representation(f, context=body, vertices=[[tuple of floats per vertex]], faces=[[list per
  face]])`; assign; place at (0, 0, 0, 0); contain.
- **WO-07 `bim_ifcos_add_pset(guid, name, props)`**: element by guid as an `IfcProduct` (`no element`); empty `name`
  or `props` not a dict: `bad pset`. Keeps the values that are `str`, `int`, `float` (not NaN) or `bool`, keys as
  `str`. `pset.add_pset(f, product=el, name=name)` then `pset.edit_pset(f, pset=pset, properties=clean)`. Answers
  `{"count": len(clean)}`.
- **WO-08 `bim_ifcos_save_model(model, path)`**: `model` not a dict: `bad model`. Levels, or
  `[{"id": "", "name": "Level 0", "elevation": 0}]` when none; `bim_ifcos_new_project(model name or "Project",
  first level's elevation)`; the new project's one storey renamed to the first level's name; one
  `bim_ifcos_add_storey` per other level; a map level id to storey guid. An element's storey: its `level`'s, else the
  first. Then, in this order: walls (`add_wall_on`), slabs, columns, openings (only when its `wall` was added; its
  thickness and offset are that wall entry's), meshes, then psets for elements that were added. `guids` maps each
  added entry's `id` to its GlobalId; `skipped` lists the ids that answered an error or had no wall. Then
  `bim_ifcos_write_read(path)`; answers its dict plus `"guids"` and `"skipped"`.

### 4.2 JavaScript, `src/js/engine/io/ifc-export.js` (Cline, WO-09 to WO-17)

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-09 `bimIfcxPlan(p)`**: `[p[0], 0 - p[1]]` (written so, `0 - 0` is `0`, never `-0`).
- **WO-10 `bimIfcxLevels(levels)`**: `[]` unless an array-like; leave out entries that are not objects or whose
  `elev` is not a finite number; each `{id: String(id), name: name ? String(name) : 'Level ' + <count so far>,
  elevation: elev}`; sorted by elevation.
- **WO-11 `bimIfcxLevelOf(levels, levelId, y)`** (levels as WO-10 makes them): `''` when none; the level whose `id`
  is `levelId` when `levelId` is given and found; else the last level with `elevation <= y + 1e-6`; else the first.
- **WO-12 `bimIfcxWalls(o, levels)`**: `[]` unless `o.bim.type === 'wall'` with a centreline of 2 or more points
  and no `bulges`. Segments: each pair of points, and last to first when `closed` and more than 2 points. Offsets by
  `align` (part 3). Each entry: `id` `o.id` (one segment) or `o.id + '#' + i`; `host` `o.id`; `name` `o.name` or
  `o.name + ' ' + (i + 1)`; `level` `bimIfcxLevelOf(levels, bim.levelId, bim.baseY)`; ends by `bimIfcxPlan`;
  `z` `bim.baseY`; `height`; `thickness` `dLeft + dRight`; `offset` `0 - dLeft`.
- **WO-13 `bimIfcxSlab(o, levels)`**: `null` unless `bim.type === 'floor'` with a profile of 3 or more points.
  `{id, name, level: levelOf(bim.levelId, baseY - thickness), points: each by bimIfcxPlan, z: baseY - thickness,
  depth: thickness}` (a floor's top is `baseY`; `bimBuildFloorGeometry`).
- **WO-14 `bimIfcxColumn(o, levels)`**: `null` unless `bim.type === 'column'` with a `center` and no `section`.
  `{id, name, level: levelOf(levelId, baseY), x, y (bimIfcxPlan of center), z: baseY, width, depth, height,
  rotation: 0 - (bim.rotation || 0)}` (the app turns a column in its plan, whose Y is IFC's -Y).
- **WO-15 `bimIfcxOpening(m, walls)`**: `null` unless `bim.type` is `'door'` or `'window'` with a `center` and
  `walls` given. `p = bimIfcxPlan(center)`. Among `walls` whose `host === bim.hostWallId` and length is 1e-9 or
  more: `t` the projection of `p` on the segment from its start, kept when `-1e-6 <= t <= L + 1e-6`; the one whose
  distance from `p` to its line is least. `{id, name, kind: bim.type, wall: <that entry's id>, along: t, sill:
  bim.sillHeight || 0, width, height}`, or `null` when none.
- **WO-16 `bimIfcxMesh(o, levels)`** and the table `BIM_IFCX_CLASS` above it: `{wall: 'IfcWall', floor: 'IfcSlab',
  slab: 'IfcSlab', roof: 'IfcRoof', stair: 'IfcStair', beam: 'IfcBeam', column: 'IfcColumn', railing:
  'IfcRailing', ceiling: 'IfcCovering', footing: 'IfcFooting'}`. `null` without `o.mesh.v` and `o.mesh.f`, both
  non-empty. Each vertex `v + pos` (pos `o.pos` or `[0, 0, 0]`) as `[x, 0 - z, y]`; faces of 3 or more indices,
  copied; `null` when no face is left. `level` by the lowest `y + pos[1]`. `ifcClass`: `bim.ifcType` when it is a
  string matching `/^Ifc[A-Za-z]+$/`, else the table's class for `bim.type`, else `'IfcBuildingElementProxy'`.
- **WO-17 `bimIfcxModel(objs, levels, name)`**: `{name: name || 'Project', levels: bimIfcxLevels(levels), walls,
  slabs, columns, openings, meshes, psets}`, all lists empty when `objs` is not a non-empty array. For each object
  in order (skip falsy): `t === 'opening'` kept for later; `t !== 'solid'` skipped; else the first of walls (WO-12,
  every entry), slab, column, mesh that answers; one pset per entry made, `{id: <entry id>, name: 'BIM_Personal',
  props: {AppId: o.id, Name: o.name || ''}}`. Then each kept opening by WO-15 against all walls; those not `null`
  in `openings`.

### 4.3 Claude's (WO-18, WO-19)

`bimIfcExport()` in `ifc-export.js`: `bimIfcxModel(A3D.objs, A3D.levels, <the project's name>)`, to the worker,
`bim_ifcos_save_model(model, '/tmp/out.ifc')`, the file read back from Pyodide's file system and offered with the
app's save (`io/file-save.js`); a toast with the counts and the skipped ids. The worker: the seven wheels pinned in
`runtime/wheels/` and `MANIFEST.json`, loaded on the first IFC call only; `bim_ifcos.py` embedded as
`bim_ladybug.py` is (`tools/embed_py.py`). Offline from `file://`, the command says IFC export needs the Pages
address, as Ladybug does.

## 5. Order of the work

WO-01 to WO-08 in order (WO-08 uses all of them), then WO-09 to WO-17 in order (WO-15 uses WO-12's entries, WO-17
all of them); the two groups do not depend on each other. Then Claude's WO-18 (the wheels, the worker, the command,
the one browser check of File, Export, IFC) and WO-19 (the records, the library rule's wording). The owner can try it
in the app after WO-18.

## 6. Not in this phase

Editing imported IFC elements (D3: after That Open). Curved walls as walls (they go as meshes). Materials, layers
and types (`IfcMaterialLayerSet`, `IfcWallType`). Several buildings (every level goes in one `IfcBuilding`). Site
georeferencing (`IfcMapConversion`). IFC 4.3 or IFC2x3 output. Reading back into the app.
