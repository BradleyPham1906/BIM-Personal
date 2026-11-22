# Research: the FreeCAD gaps after the CADCraft list (V266 to V273)

Asked by the owner, 2026-11-22: "Ok now what about freecad. What is the current gap?", then "Ok do it all in one run
pls". The gaps are the eight of the FreeCAD workbench survey (`docs/dev/canvas_v10_STATUS.md`, 2026-09-06), less what
V255 (a measure that leaves nothing) and V264 (OpenCASCADE: extrude, fillet, chamfer, shell, revolve, loft, booleans,
STEP) had already closed.

## 1. The question and the hypotheses

What does FreeCAD's Part, PartDesign, Sketcher, Material, Spreadsheet, Import, Points, Mesh, TechDraw and Assembly do
that this app still cannot, and how much of it can be built on what the app already ships?

- H1: the rest of PartDesign (a picked edge, draft, sweep, patterns, thickness) needs no new library: replicad 1.2.1
  and its OpenCASCADE build, pinned since V264, expose them.
- H2: a solid turned or scaled by the app's mesh tools can stay a B-rep, because those tools keep the mesh's vertices
  and their order, so the map between the two meshes is one affine transform.
- H3: TechDraw's exact hidden lines are in the same OpenCASCADE build (HLRBRep).
- H4: IGES is not in that build, and needs a second library.

## 2. What was read and measured (2026-11-22)

| # | Source | What | Level |
|---|---|---|---|
| 1 | `tools/occt/node_modules/replicad/dist/replicad.d.ts` (1.2.1) | fillet and chamfer by a function per edge; `draft`; `Sketch.sweepSketch`; `genericSweep`; `makeProjectedEdges`; `ProjectionCamera`; `makeSolid`, `makePolygon`, `importSTL` | P |
| 2 | `replicad.js` 1.2.1, `makeProjectedEdges` and `PROJECTION_PLANES` | HLRBRep_Algo, HLRAlgo_Projector, the visible and hidden compounds | P |
| 3 | `runtime/occt/1.2.1/replicad_single.wasm`, its exports listed in Node | gp_Trsf (with SetValues), BRepBuilderAPI_Transform, HLRBRep_*, BRepBuilderAPI_Sewing present; IGESControl absent; BRepBuilderAPI_GTransform absent (no non-uniform scale on a B-rep) | P (measured) |
| 4 | FreeCAD `src/Mod/Material/Resources` at 170926f (sparse clone) | the 1.0 .FCMat format: YAML, `General`, `Models` and `AppearanceModels` keyed by model UUID (LinearElastic 7b561d1d..., Thermal 9959d007..., MaterialStandard 1e2c0088..., BasicRendering f006c7e4...); units written in the values; generic cards' values | P |
| 5 | npm `occt-import-js` 0.0.23, its tarball read as text | LGPL-2.1; OpenCASCADE's STEP, IGES and BREP readers as a 7.6 MB wasm; output as meshes | P (read, not run) |
| 6 | `docs/work-orders/v190/SPEC.md`, `v189/SPEC.md` | the point-cloud slice's remaining Claude tasks; Make2D on meshes, Cline's | P |

Experiments run here (Node, the pinned runtime): a one-edge fillet by midpoint matches 6 - r^2 (1 - pi/4) h; a 5 degree
draft matches the prismatoid formula; a sweep along a straight path is the section times its length; a mirror-scale
gp_Trsf through SetValues gives the expected bounds and volume; the projection camera's direction points at the viewer
(direction +Z with x east gives a plan with north up); meshing a deserialized shape repeats its vertices exactly, which
H2 relies on. Each is now a unit test (`tests/unit/occt-features.test.mjs`, `occt-views.test.mjs`, `mesh-repair.test.mjs`).

## 3. Findings

- H1 holds. H2 holds for turns, mirrors and even scales; a plan-only SCALE (x and z, not y) is a stretch, which a B-rep
  cannot follow here (no GTransform): the solid is then left a mesh and says so. H3 holds. H4 holds: IGES needs
  occt-import-js (or a larger OpenCASCADE build).
- A semicircle is the least radius on its chord, so a radius constraint starting there has a zero slope; and an arc's
  bulge as a raw unknown can cross zero and flip the arc to the other side. The solver takes log|b| as the unknown
  (the side kept) and starts a semicircle slightly flat. It also damped a diagonal of numerical noise by itself, which
  turned 1e-22 into steps of millions; such a diagonal is now damped as a zero one.
- The material library already matched FreeCAD's generic cards (V120). What was missing was a library the user edits,
  the thermal and strength properties, and the .FCMat file.

## 4. Built

| Phase | What | Where |
|---|---|---|
| V266 | FILLETEDGE and CHAMFEREDGE on edges clicked in any view; DRAFTANGLE (TAPER); SWEEP; SOLIDPATTERN (linear, polar, mirrored, joined); THICKNESS (top, bottom, both open); solids that follow ROTATE, MIRROR, COPY and an even SCALE | `solids/occt-features.js`, `occt-adapter.js` |
| V267 | GCTANGENT, GCPOINTONARC, DCRADIUS, DCDIAMETER: constraints on arcs, the bulge solved | `drawing/sketch-arc-constraints.js`, `sketch-constraints.js` |
| V268 | MATERIALS: the project's own cards, an editor, FreeCAD .FCMat import and export, assign | `assets/material-cards.js`, `material-browser.js` |
| V269 | SPREADSHEET: formulas, aliases, ranges, obj() reads; cells bound to position, wall height and thickness, text, sketch constraints | `views/spreadsheet-eval.js`, `spreadsheet.js` |
| V190 WO-12, WO-13 | LAS and PLY clouds imported, drawn as GL points, coloured by RGB, class or height, classes hidden, ground to surface | `map/pointcloud-view.js` |
| V271 | MESHREPAIR (weld, clean, orient, holes reported); MESHTOSOLID | `editing/mesh-repair.js` |
| V272 | VIEWBASE (TECHDRAW): front, top, right, isometric, exact hidden lines | `solids/occt-views.js` |
| V273 | JOINT (fixed, hinge, slider) driving parts; BOM as CSV | `assembly/joints.js` |

Checks: `npm test` 495 of 495; the browser check `tests/e2e/bim_phase266_273_check.mjs` 32 of 32.

## 5. What is open

- **IGES (V270): needs the owner's approval of occt-import-js 0.0.23** (LGPL-2.1, its own file under `runtime/`, as
  OpenCASCADE's build is). It was not run here. `docs/research/experiments/v270-iges/` holds a generator of our own IGES
  box for its test. Until then Import says to use STEP.
- Joints: a hinge's axis is vertical; a ball, a cylindrical joint, or a hinge on a tilted axis is not built; closed loops
  are refused rather than solved.
- Make2D on meshes (v189) stays Cline's; VIEWBASE covers OpenCASCADE solids exactly.
- A point cloud over 500,000 points is not saved inside the project; it asks for its file again after a reload.
- Not attempted: FreeCAD's FEM, CAM, Robot, OpenSCAD (out of scope since the September survey).
