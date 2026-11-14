# V177 research: IfcOpenShell in the app (load, licence, Save as IFC, editable IFC elements)

Claude, 2026-11-13. Follows V176 (`docs/work-orders/v176/`), which proved IfcOpenShell 0.8.5 runs in the app's Pyodide
and built the adapter `src/py/bim_ifcos.py`. Levels: P read in the primary source or measured here, S dependable
secondary, U unverified. The owner's decisions are asked in part 11; V177's spec waits for them.

## 1. Abstract

Can IfcOpenShell ship in the app and carry Save as IFC and editing of imported IFC elements? Technically yes: in a
browser's worker the whole start (Pyodide, the wheels, the import) takes 4.4 to 5.5 s in Edge 157, not the 25 s
measured in Node, and its API has ready functions for walls, slabs, doors, windows, openings, meshes and property
sets. The blocker is the licence: the WebAssembly wheel's one binary contains CGAL packages that are GPL, so the file
we would ship is GPL in effect, and the app's library rule says never GPL. Recommendation: the owner decides D1
first; if the answer allows it, V177 ships the wheel as its own file run only in the Python worker, and Save as IFC
for walls, floors, doors, windows and columns.

## 2. The question and the hypotheses

- H1 The 25 s import is compiling the 53.6 MB module. **False**: compiling takes 0.08 s, instantiating 0.18 s (e01).
- H2 The import is slow in a browser too. **False** in Edge 157: 2.2 to 2.6 s for the wrapper, 4.4 to 5.5 s in all
  (e04). Node's default tiering is the cost: with `--liftoff-only` Node takes 2.8 s (e03).
- H3 The wheel is LGPL as its metadata says, so it fits the library rule as a separate file. **False as shipped**:
  the binary contains GPL CGAL packages (part 4.2).
- H4 `ifcopenshell.api` 0.8.5 has what Save as IFC needs without our own geometry code. **True** for walls, slabs,
  doors, windows, openings, meshes, property sets (part 4.3).

## 3. Method

Experiments, scripts in `docs/research/experiments/v177/` (Windows 11, Node 26.13, Edge 157 headless, the app's
`runtime/pyodide/0.29.5`, V176's pinned wheels in `.cache/ifcos/`): e01 times each WebAssembly compile and each
import; e02 Python's cProfile of the import; e03 the same steps under V8 flags; e04 the same in a classic Web Worker
in Edge, two workers in one page load, with a kept profile and a fresh one. Sources: the wheel itself (its METADATA,
its Python source unpacked, the strings of its binary); CGAL's manual and licence page; IfcOpenShell's README and
`pyodide/meta.yaml` at tag v0.8.0; V8's documentation of its compile pipeline. Web searches (3, 2026-11-13) only
pointed to these pages. Not done: an independent second reader; Firefox and Safari (not installed here).

## 4. Findings

### 4.1 Start-up time (P, measured; confidence high for Chromium, none for others)

| Where | Wrapper import | Everything (boot to a written IFC) |
|---|---|---|
| Node 26.13, default | 14.7 to 15.7 s, then 8 to 9 s for the api modules | 27 s |
| Node 26.13, `--liftoff-only` | 2.8 s, api 0.35 s | about 5 s |
| Node 26.13, `--no-wasm-tier-up` | 19 s, api 3.8 s, first `create_file` 11 s | 36 s |
| Edge 157, Web Worker, first | 2.2 to 2.4 s, api 0.24 s | 4.4 to 4.8 s |
| Edge 157, Web Worker, second in the same page | 2.1 to 2.6 s | 4.9 to 5.5 s |

Edge, by step (ms, first worker): Pyodide 1070, fetch seven wheels from localhost 230 to 280, unpack 280 to 340,
numpy 260, shapely 80, wrapper 2160 to 2410, api and util 230 to 260, `create_file` 4, a wall 10, write 2, open 4.
A kept browser profile made no difference: nothing of the compiled module is reused, each worker pays the 4 to 5 s.
In Node the time is inside one native call, `schema_names()` (14.3 s, e02): V8's handling of the module's very
large functions, not work the program does. V176's test keeps its 60 s allowance; nothing to fix in the adapter.

### 4.2 Licence of the file we would ship (P for the facts, the conclusion is a legal judgment)

- The wheel's METADATA and IfcOpenShell's `pyodide/meta.yaml` say LGPL-3.0-or-later (P). The README's table marks
  ifcopenshell-python and the C++ libraries "LGPL-3.0-or-later*"; the asterisk is not explained in the text read.
- The wheel's binary (`_ifcopenshell_wrapper...so`, 53,612,307 bytes) contains CGAL and Open CASCADE code: its
  strings name `CGAL/Nef_3` (13 times), `CGAL/Convex_decomposition_3`, `CGAL/Nef_S2`, `CGAL/Arrangement_2`,
  `CGAL/Polygon_offset_builder_2`, `Polygon_mesh_processing` (232), `Nef_polyhedron_3` (516), and Open CASCADE
  symbols (`opencascade` 4,656, `BRepAlgoAPI` 158); also gmp and mpfr (P, read from the pinned file).
- CGAL's manual (6.2.1) gives the licence of each: 3D Boolean Operations on Nef Polyhedra GPL, Convex Decomposition
  of Polyhedra GPL, 2D Arrangements GPL, Polygon Mesh Processing GPL, 2D Straight Skeleton and Polygon Offsetting
  GPL; the kernel and number types LGPL (P). CGAL's licence page: GPL v3+; "If you distribute your software based
  on GPLed CGAL data structures ... you are furthermore obliged to distribute the source code of your own software
  under the GPL" (P).
- So the binary is a combined work that includes GPL-3 code: whoever distributes it does so under GPL-3 terms,
  whatever IfcOpenShell's own source says. Committing it to `runtime/` and serving it on Pages is distributing it.
- What that means for the app (judgment, confidence medium): the adapter `bim_ifcos.py` imports the library, so the
  adapter with the wheel is one GPL-3 work; Apache-2.0 code may be part of a GPL-3 work, so the adapter can stay
  Apache-2.0. The app itself talks to the worker only by JSON messages and works without it; that is the usual
  "separate programs" arrangement, as a program that runs a GPL command-line tool. It is an arrangement people
  rely on, not a certainty, and it contradicts the present wording of the app's rule ("never GPL or AGPL").
- The same question was already open for Ladybug (AGPL-3.0, in `runtime/wheels/` since V172b, loaded the same way).
- Open CASCADE's own licence page could not be fetched (U); LGPL-2.1 with an exception is what is generally stated.

### 4.3 What the API gives Save as IFC (P, the wheel's source, `ifcopenshell/api/`)

`geometry.add_wall_representation(file, context, length, height, thickness, ...)`, `geometry.create_2pt_wall(file,
element, context, p1, p2, elevation, height, thickness, is_si)`, `geometry.add_slab_representation(file, context,
depth, polyline, ...)`, `geometry.add_door_representation(file, context=, overall_height=, overall_width=, ...)`,
`geometry.add_window_representation(...)`, `geometry.add_profile_representation(file, context, profile, depth)`,
`geometry.add_mesh_representation(file, context, vertices, faces=)`, `feature.add_feature(file, feature, element)`
(an opening in a wall), `feature.add_filling(file, opening, element)` (a door or window in it),
`pset.add_pset(file, product, name)` and `pset.edit_pset(file, pset, properties=)`,
`geometry.edit_object_placement(file, product, matrix, is_si=True)`. The modules present: aggregate, attribute,
classification, context, feature, geometry, georeference, grid, material, owner, profile, project, pset, root,
spatial, style, type, unit and others.

### 4.4 Size (P)

The seven wheels are 15,907,875 bytes together (IfcOpenShell 14,654,346; shapely 832,503; python-dateutil 229,892;
lark 113,151; typing-extensions 44,613; isodate 22,320; six 11,050). numpy is in `runtime/` already. Fetched only
when IFC is saved or an IFC element is edited.

## 5. The alternatives compared

| | Licence of what ships | Save as IFC | Edit imported IFC | Our own code | Cost |
|---|---|---|---|---|---|
| A. IfcOpenShell wheel, own file, worker only | GPL-3 in effect (CGAL inside) | its API | its API | adapter only | 15.9 MB on demand, 4 to 5 s |
| B. A wheel built without CGAL (Open CASCADE only) | LGPL | its API | its API | adapter, and our own wasm build to keep up | days of build work, unproven for wasm |
| C. That Open / web-ifc (MPL-2.0 engine, MIT components) | permissive | writes IFC entities, no authoring API: we write the wall, slab, opening logic | property edits; geometry edits ours | much more | already chosen for import and Review |
| D. Our own IFC writer | ours | all ours | all ours | all of it | what the owner asked to stop doing |

Recommendation: A if the owner accepts D1; otherwise C for writing, with B noted as research for later.

## 6. The experiments

Raw numbers are in part 4.1. e01: sync compile 53,612,307 bytes 80 ms, instantiate 178 ms, wrapper import 14,745 ms,
api and util 9,177 ms, first `create_file` 2,147 ms. e02: 27.9 s, of which `schema_names` 14.3 s. e03 and e04: the
table. Each script's first lines say how to run it.

## 7. Edges

- A browser that treats the module as Node does would take 25 s or more; Firefox and Safari are untested (U). The
  load is in the worker, so the app stays usable, and the interface must say it is loading.
- 0.9.0.post1's wheel is smaller (4.6 MB) but cannot open or create a file when unpacked alone (V176); stay on 0.8.5.
- `file://`: the worker fetches the runtime from the Pages address, as Ladybug does; offline from a file, IFC save
  is not available and says so.
- The adapter's `bim_ifcos_add_wall` uses the storey's elevation as metres: right for its own projects, wrong for an
  imported file in millimetres; the spec converts with `calculate_unit_scale`.

## 8. What the app already has

- The Python worker: `src/js/engine/ladybug/runtime.js` (a classic worker from a Blob, wheels checked by SHA-256,
  `bimLbCall(fn, args, files)`), `tools/embed_py.py` (embeds `src/py/bim_ladybug.py`), `runtime/MANIFEST.json` and
  `tools/check_runtime.py`.
- The model: walls `{type:'wall', centerline, thickness, height, align, baseY, closed}`
  (`bim/import-compliance.js:151`), floors `{type:'floor', profile, thickness, baseY, levelId}`
  (`bim/ceiling-floor-profile.js:85`), doors and windows `{hostWallId, center, dir, width, height, sillHeight}`
  (`bim/columns-openings.js:413`), columns, beams, roofs and stairs (meshes with parameters), `A3D.levels`.
- IFC import: `io/ifc-full.js` (cc-ifc): each element a locked solid with `bim.guid`, `ifcType`, `storey`, `psets`.
  No IFC export exists.

## 9. Risks

Licence (part 4.2), the largest. An untested browser being slow (part 7). The wheel is a third party's build:
pinned by SHA-256, but we cannot rebuild it today. Editing imported elements depends on which import is kept
(cc-ifc now, That Open planned): if both IfcOpenShell and That Open ship, the app carries two IFC engines.

## 10. Still open

Firefox and Safari timings; Open CASCADE's licence text; what the README's asterisk means; whether IfcOpenShell
publishes a statement on its binaries' licence; whether a CGAL-free wasm build works.

## 11. The owner's decisions

- D1 The wheel contains GPL code. (a) Accept GPL and AGPL libraries when they are separate files run only in the
  Python worker, and change the rule's wording to say so (this also settles Ladybug); (b) no GPL: Save as IFC goes
  through That Open's engine with our own authoring code; (c) pause IFC save and try a CGAL-free build first.
- D2 If D1 is (a): what V177 saves first. Recommended: levels, walls, floors, doors and windows with their openings,
  columns; everything else as plain meshes (`IfcBuildingElementProxy`) so nothing is missing from the file.
- D3 Editing imported IFC elements: in V177, or after the import engine is settled (That Open). Recommended: after;
  V177 is Save as IFC only.
- D4 Where the command lives: File, Export, "IFC (.ifc)", beside DXF and glTF. Recommended: yes.

**Answered (the owner, 2026-11-13):** D1 (a): GPL and AGPL libraries are allowed as separate files run only in the
Python worker; the rule in `CLAUDE.md` now says so, and Ladybug is settled by it. D2: the core elements as real IFC
elements, everything else as shapes. D3: editing imported walls and slabs is in V177 too. D4: File, Export, IFC.

Checked after the answers (e05, 2026-11-13): every call V177 names runs in the wasm build: a second storey, a slab
from a polyline, an opening (`feature.add_feature`) with a door filling it (`feature.add_filling`), a window, a mesh,
a property set, a kept GlobalId, write and read, and the geometry kernel on the written wall and slab.

## 12. References

- The pinned wheel `ifcopenshell-0.8.5-cp313-cp313-pyodide_2025_0_wasm32.whl` (SHA-256 `fbebb7a7...929c`): METADATA,
  `ifcopenshell/api/**` signatures, the binary's strings. Read 2026-11-13. P.
- CGAL 6.2.1 manual, package overview, https://doc.cgal.org/latest/Manual/packages.html: the License line of seven
  packages. 2026-11-13. P.
- CGAL licence, https://www.cgal.org/license.html: the GPL and LGPL sections. 2026-11-13. P.
- IfcOpenShell README and `pyodide/meta.yaml` at v0.8.0 (raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.8.0/).
  2026-11-13. P.
- V8, WebAssembly compilation pipeline, https://v8.dev/docs/wasm-compilation-pipeline: the tiers. Search summary
  only. U (not used by the code).
- Experiments e01 to e04, `docs/research/experiments/v177/`. P.
