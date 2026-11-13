# V176 spec: IfcOpenShell in the app's own Python

Research: this spec's part 0 (the owner's decisions, 2026-11-13: reuse Bonsai's own engine, `ifcopenshell.api`,
instead of writing our own; the app is Apache-2.0, IfcOpenShell LGPL-3.0 loaded unchanged as a separate file;
IfcOpenShell is V176 and V177; Cline builds the adapter). Implementation target: local `main`. Written by Claude,
2026-11-13. Cline reads this with TASKS.md.

## 0. What was checked before this spec (Claude, 2026-11-13)

- **Pinned: 0.8.5** (`ifcopenshell-0.8.5-cp313-cp313-pyodide_2025_0_wasm32.whl`, 14,654,346 bytes, SHA-256
  `fbebb7a7...929c`, tag `v0.8.5`). Found after the first spec (Claude, 2026-11-13, WO-01's test): 0.9.0.post1's wheel
  imports, but crashes on `ifcopenshell.open` ("memory access out of bounds") and cannot make an empty file ("Unable to
  resolve module path"): it keeps its schemas in separate modules (the repository's `modular` folder). 0.8.5 is one
  module and runs every step of this spec. In 0.8.5 each `ifcopenshell.api.<module>` is imported explicitly (the
  header does it). pyparsing is not a dependency of 0.8.5.
- IfcOpenShell publishes WebAssembly wheels: `ifcopenshell-0.9.0.post1-cp313-cp313-pyodide_2025_0_wasm32.whl`,
  4,617,450 bytes, SHA-256 `5b3b46dc...c209`, in github.com/IfcOpenShell/wasm-wheels (tag `v0.9.0post1`), built by
  IfcOpenShell's own workflow `publish-ifcopenshell-wasm-wheel.yml`. Licence LGPL-3.0-or-later (`pyodide/meta.yaml`).
  The wheel carries no licence file: V177 ships the LGPL and GPL texts beside it.
- It is CPython 3.13 on the `2025_0` Pyodide ABI: the app's Pyodide 0.29.5 is the same (`pyodide-lock.json`:
  `abi_version 2025_0`, Python 3.13.2).
- Its dependencies (the wheel's METADATA): shapely, numpy, isodate, python-dateutil, lark, pyparsing,
  typing-extensions. numpy is the app's own; shapely, python-dateutil (and six), pyparsing and typing-extensions are
  Pyodide 0.29.5's builds; isodate (BSD-3) and lark (MIT) come from PyPI. All pinned by SHA-256 in `v176.test.mjs`.
- Measured in Node with the app's runtime (Windows, 2026-11-13), 0.8.5: Pyodide starts in 1.0 s, the wheels install
  in 0.5 s from the cache, `import ifcopenshell` takes **25 to 26 s** on every run (compiling its one 14 MB module;
  0.9's split build imported in 0.7 s but cannot open a file). V177's first question: the time in a browser (streaming
  compilation, and whether the compiled module can be cached), loading it in the Python worker in the background.
- Found: in this build `ifcopenshell.version` is `'0.0.0'`; the version is read from the package metadata.
- The `ifcopenshell.api` functions this spec names were read in the wheel's own source (0.9.0.post1), with their
  arguments. `unit.assign_unit(file)` with no units makes millimetres; this spec asks for metres.

## 1. What it does for the user

Nothing visible yet: V176 proves that IfcOpenShell, Bonsai's engine, runs inside the app's own Python, and builds
the small adapter the app will call. V177 uses it to save the model as IFC and to make imported IFC elements editable.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/py/bim_ifcos.py` | new (header by Claude) | the adapter: four functions | Cline (WO-01 to WO-04) |
| `docs/work-orders/v176/v176.test.mjs` | new | the tests, outside `npm test` (the first run fetches the pinned wheels into `.cache/ifcos/`) | Claude |

## 3. Data

Every function answers a plain dict that `json.dumps` can write. A summary is
`{"schema": "IFC4", "products": {"IfcWall": 1, ...}, "storeys": [{"name": "Level 1", "elevation": 3.5}]}`:
`products` counts every `IfcProduct` by its class name (`element.is_a()`), leaving out `IfcOpeningElement`; `storeys`
is every `IfcBuildingStorey`, in the file's order, its `Name` and its `Elevation` in metres (the file's length unit
scale times the value, `ifcopenshell.util.unit.calculate_unit_scale(file)`, rounded to 6 places; `0` when not set).
A failure is `{"error": "<short reason>"}`, never an exception.

The project being built lives in the module's `_bim_ifcos_file` (an `ifcopenshell.file`, or `None`).

## 4. Functions (all in `src/py/bim_ifcos.py`)

### `bim_ifcos_summary(path)` - WO-01
- **Takes:** `path`, a path in Pyodide's file system, or `''` for the project in `_bim_ifcos_file`.
- **Returns:** the summary (part 3) of `ifcopenshell.open(path)`, or of `_bim_ifcos_file` when `path` is `''`.
- **Edge cases:** a path that does not exist: `{"error": "not found"}`; `''` with no project: `{"error": "no project"}`;
  any other failure while reading: `{"error": "unreadable"}`.
- **Example:** the test's IFC (a wall with an opening on a storey at 3500 mm) gives
  `{"schema": "IFC4", "products": {"IfcBuilding": 1, "IfcBuildingStorey": 1, "IfcSite": 1, "IfcWall": 1}, "storeys": [{"name": "Level 1", "elevation": 3.5}]}`.
- **Uses:** `os.path.exists`, `ifcopenshell.open`, `file.schema`, `file.by_type`, `ifcopenshell.util.unit.calculate_unit_scale`.

### `bim_ifcos_new_project(name, elevation)` - WO-02
- **Takes:** the project's name; the first storey's elevation in metres.
- **Does:** `_bim_ifcos_file = ifcopenshell.api.project.create_file(version="IFC4")`; an `IfcProject` named `name`
  (`root.create_entity`); units in metres: `unit.add_si_unit(f, unit_type="LENGTHUNIT")`, `"AREAUNIT"`, `"VOLUMEUNIT"`,
  then `unit.assign_unit(f, units=[...])`; contexts: `context.add_context(f, context_type="Model")`, then a body
  sub-context `context.add_context(f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model)`;
  an `IfcSite` named `"Site"`, an `IfcBuilding` named `"Building"`, an `IfcBuildingStorey` named `"Level 0"` with
  `Elevation = elevation`; `aggregate.assign_object` site to project, building to site, storey to building.
- **Returns:** `bim_ifcos_summary('')`.
- **Example:** `bim_ifcos_new_project("Test project", 0)` returns
  `{"schema": "IFC4", "products": {"IfcBuilding": 1, "IfcBuildingStorey": 1, "IfcSite": 1}, "storeys": [{"name": "Level 0", "elevation": 0}]}`.
- **Uses:** `ifcopenshell.api.project.create_file`, `root.create_entity`, `unit.add_si_unit`, `unit.assign_unit`,
  `context.add_context`, `aggregate.assign_object` (all `ifcopenshell.api.<module>.<function>(file, ...)`).

### `bim_ifcos_add_wall(name, x0, y0, x1, y1, height, thickness)` - WO-03
- **Takes:** the wall's name; its start and end in metres in the plan (IFC's X and Y); its height and thickness in metres.
- **Does:** on the project's first storey: an `IfcWall` named `name`; its body
  `geometry.add_wall_representation(f, context=<the Body sub-context>, length=L, height=height, thickness=thickness)`,
  `geometry.assign_representation`; its placement `geometry.edit_object_placement(f, product=wall, matrix=M)` where
  `L` is the distance from start to end and `M` is a 4 x 4 numpy matrix turning by `a = atan2(y1 - y0, x1 - x0)` about Z
  (`[[cos a, -sin a, 0, x0], [sin a, cos a, 0, y0], [0, 0, 1, storey elevation], [0, 0, 0, 1]]`);
  `spatial.assign_container(f, products=[wall], relating_structure=storey)`.
- **Returns:** `{"guid": wall.GlobalId}`.
- **Edge cases:** no project: `{"error": "no project"}`; `L` under 1e-9: `{"error": "zero length"}` and nothing added.
- **Example:** after `bim_ifcos_new_project("Walls", 0)`, `bim_ifcos_add_wall("Wall A", 1, 2, 5, 2, 3, 0.2)` adds a
  4 m wall whose placement starts at (1, 2) and runs along +X.
- **Uses:** the names above, `math.atan2`, `math.cos`, `math.sin`, `math.hypot`, `numpy.array`.

### `bim_ifcos_write_read(path)` - WO-04
- **Takes:** a path in Pyodide's file system.
- **Does:** writes `_bim_ifcos_file` there (`file.write(path)`), then reads it back.
- **Returns:** `{"bytes": <the file's size>, "summary": bim_ifcos_summary(path)}`.
- **Edge cases:** no project: `{"error": "no project"}`.
- **Uses:** `file.write`, `os.path.getsize`, `bim_ifcos_summary`.

## 5. Order of the work

WO-01 first (WO-02 and WO-04 answer with it), then WO-02, WO-03, WO-04. After each:
`node --test --test-name-pattern="WO-0N" docs/work-orders/v176/v176.test.mjs`. Nothing in the app calls the adapter
until V177, so `canvas_v10.html` does not change.

## 6. Not in this phase

The app does not load IfcOpenShell yet (V177 pins the wheels in `runtime/` and loads them in the Python worker);
no Save as IFC, no editing of imported elements, no openings, slabs or property sets. No change to any `.js` file.
