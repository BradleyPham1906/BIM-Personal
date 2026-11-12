# V194: the rendered view, and what the reference apps can give us

Research and build, 2026-11-11 to 11-12. Levels: P = read at the primary source, S = dependable secondary,
U = a search summary (a pointer only; no U fact is in the code).

## 1. The question

The owner (2026-11-11): the app "is not really professional"; others do "BIM + simulations + rendering with
three.js"; "improve the UI and missing BIM/CAD features and rendering by write the code into the app ... like
Bonsai, FreeCAD, BIMCraft / Beamcraft, and CreaBIM. just clone or read their codes on github and plug them
into our app and make it work." The video shared is Open Infra Studio on Open CAD Studio.

Two questions: what of those projects can go into this app, and what closes the largest gap first.

## 2. Hypotheses

- H1: the largest visible gap is the 3D view's look, not the BIM or the simulations. **Held** (3).
- H2: most of the named projects cannot be plugged in as code. **Held** (4): five are Rust, one is Python on
  Blender, one is C++; four are GPL.
- H3: three.js can draw the app's own scene description beside the two engines, without touching the modelling
  code. **Held** (experiment e01; 175 unit tests; the app's own browser check is still to run).
- H4: a picture built from many passes gives soft shadows and corner shading with three.js's core alone, fast
  enough for a live view. **Held** on this PC (e01: about 3 ms a pass at 1500 x 900).

## 3. The app's code, read (P)

- The renderer is five files, 1,299 lines (`src/js/engine/render/`). Faces are shaded by one formula, a fixed
  light and a flat colour: `0.45+0.55*abs(dot(n,light))` (`webgl.js`, `gpu-batches.js`, `webgpu.js`). No
  materials, no textures on the model, no cast shadows in the view, no sky.
- `bimSceneSync` (V152) describes the scene once for both engines: chunks of merged triangles and a table of
  each object's place, transparency, colour and selection. A third reader needs nothing else.
- The camera is `camVecs` and `bimGlProjMatrix`; right, up and back are a right-handed basis, so three.js
  takes the two matrices as they are.
- Simulation and BIM are not the gap: traffic and walkers, Ladybug's radiation and sun hours, comfort, noise,
  drainage, the frame solver; walls, floors, roofs, stairs, columns, openings, footings, rooms, types, history.
- Behind: IFC reads only walls, slabs and storeys as extrusions (`io/import-ifc.js`); no glTF; no MEP.

## 4. The reference projects (P: GitHub's API and each repository's files, 2026-11-11)

| Project | Repository | Language | Licence | What it can give this app |
|---|---|---|---|---|
| BimCraft | getcadcraft/bimcraft @ cfbd948 | JavaScript | Apache-2.0 | Code, with credit. Its fast render is this phase's method. Also to read: IFC, clash, MEP, families |
| BIMCraft | IPedrax/BIMCraft | Rust | Apache-2.0 / MIT | Methods and code to port, with credit |
| BeamCraft | Apibim-com/BeamCraft | Rust | MPL-2.0 | Methods; a ported file stays MPL |
| CreaBIM | chopinregis/CreaBIM | Rust | GPL-3.0 | Behaviour and interface ideas only |
| Open CAD Studio | HakanSeven12/OpenCADStudio | Rust | GPL-3.0 | Behaviour and interface ideas only |
| Open Infra Studio | OpenAEC-Foundation/Open-Infra-Studio | Rust | GPL-3.0 | Behaviour and interface ideas only |
| Bonsai | IfcOpenShell/IfcOpenShell | Python on Blender | GPL-3.0 (IfcOpenShell LGPL-3.0) | Ideas only; IfcOpenShell itself could run in Pyodide as a library |
| FreeCAD | FreeCAD/FreeCAD | C++, Python, Qt | LGPL-2.1+ | Not pluggable; its kernel has a WebAssembly build (heavy) |
| three.js | mrdoob/three.js 0.186.1 | JavaScript | MIT | The renderer, unchanged, as a runtime |

- A Rust, C++ or Blender program cannot be pasted into an ES5 browser engine; their browser builds are whole
  apps with their own interface, not libraries.
- GPL code copied or translated into the app would put the whole app under the GPL. The repository has no
  licence file, and the owner declined Transitous for terms that "would open the code and rule out selling the
  app" (V166). So GPL projects stay what PIPELINE already says of GPL tools: methods to follow, not code to copy.
  BimCraft keeps the same rule for itself (its PROVENANCE.md).
- The video's look (flat colours by surface, soft light, trees, water) is not three.js; the app has most of its
  content already (LOD2 buildings, CityJSON, map layers, terrain, alignments). What it lacked is the light.

## 5. Alternatives

| | A. three.js as a second view (built) | B. replace the engine with three.js | C. write the effects by hand |
|---|---|---|---|
| Modelling code touched | no | all of it | the two engines, each effect twice |
| First picture | this phase | after months | several phases |
| Contract | a second written exception | the contract gone | kept |
| Risk | two views to keep in step | 140 suites | never reaches the ecosystem |

## 6. Experiment e01 (`experiments/v194-rendered/`)

The engine's own `rendered-core.js` and the pinned bundle on a made-up site, in headless Edge on this PC
(AMD Radeon 780M, Direct3D 11), 1500 x 900, nine cases. Numbers and what the pictures showed: `results.txt`.
No error in any case; the first pass 70 to 100 ms once the shaders are compiled; 3 to 9 ms a pass after it.
Found and changed: a face whose normal disagrees with its winding shades dark (now flat shading, no normals);
one sky direction stripes the walls it grazes on the first pass (the first pass has no sky shadows); BimCraft's
night is black without lamps (a dim blue night).

## 7. As built

- `runtime/three/0.186.1/bim-three.min.js`: three.js's core, unchanged, as one classic script (a module is
  refused from `file://`), built by `tools/three/build_three.mjs`, pinned in `runtime/MANIFEST.json`, checked
  by subresource integrity where the browser can. 0.186.1 is the version BimCraft ships.
- `render/rendered-core.js`: the picture (BimCraft's method, ES5). `render/rendered-scene.js`: the model as
  numbers. `render/rendered-view.js`: loading, the frame, the settings, Properties.
- `RENDER`, and Properties > View > Display: Shaded or Rendered; Sky, Quality, Ground, Edges. Off at start.
- The sun is the site's (V171d) and follows the clock; without a place, the shaded view's light.
- Any failure is said once and the shaded view draws the same frame.

## 8. The owner's decisions

- Open-source code may be brought in ("just clone or read their codes ... and plug them"): taken as the second
  written exception to "no dependencies", for three.js as a runtime.
- Recorded, not asked: GPL code is not copied (4). Say so if that should change.

## 9. Not yet

The basemap and the map draped on a terrain in the rendered view; a rendered view on a sheet or in Present;
materials by element type (glass, metal, concrete) beyond colour and transparency; textures; lamps; glTF in and
out; full IFC; a path-traced still. The app's own browser check of this phase has not been run.

## 10. Next, in order (each its own phase)

1. glTF and GLB in and out (three.js's loader and exporter, the same runtime).
2. Full IFC in (web-ifc, MPL-2.0, already on the roadmap as H3; BimCraft's own IFC engine is the other source).
3. Surfaces by kind in both views: roofs, walls, ground, water, trees in their own colours (the video's look).
4. The map and terrain in the rendered view.
5. The interface: needs the app seen in a browser first.
6. BIM gaps against BimCraft, read from its code: clash checks, doors and windows as families, MEP.

## 11. Sources

- P: this repository's code at 8e4209f. P: GitHub API, the seven repositories' licence, languages and files,
  2026-11-11. P: getcadcraft/bimcraft at cfbd948: NOTICE, PROVENANCE.md, THIRD_PARTY.md,
  `app/render/render-core.js`, `looks.js`, `sun.js`. P: npm `three` 0.186.1 (published 2026-09-24), its
  LICENSE and build files, loaded and run here. P: the owner's video, 20 frames read.
- U (pointers only): web searches for the projects' names.
