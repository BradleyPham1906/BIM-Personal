# Research: the Rhino user's guide against this app, and a documentation site

The owner shared 20 chapters of McNeel's *Rhino User's Guide* (2026-10-03) and asked whether the
app has what they teach, to build what it lacks, and for documentation and versioning "like
AutoCAD and Rhino on their websites".

**Copyright.** The guide's text and pictures belong to Robert McNeel & Associates. They are not
copied into this repository or its documentation. What is reused is what no one owns:
- the *features* (a loft, a sweep, a zebra analysis);
- the published *mathematics* behind them (NURBS, de Boor's algorithm, Coons patches).

Our own guide is written in our own words, about our app. The owner's PDFs stay on the owner's
machine.

## 1. The guides, one by one

The commands each chapter uses were read out of the PDFs and matched against the app's command
catalogue (164 commands) and its ribbon.

**Status key:**
- **Have:** the app does it.
- **Partial:** some of it, or for BIM objects only.
- **Missing:** not yet.

| Chapter | What it teaches | Here |
|---|---|---|
| Introduction | the window, command line, help per command, templates | **Have:** command line, command search (V128), shortcuts panel (V129/V130), templates (V124 Assets). **Missing:** help per command (CommandHelp). |
| Navigating Viewports | zoom, pan, orbit, standard and named views, four viewports | **Have:** zoom/pan/orbit, ViewCube, top/front/right/home views, SAVEVIEW. **Partial:** one viewport at a time; no split into four. |
| Rhino Objects | points, curves, surfaces, polysurfaces, solids, meshes, Properties | **Partial:** points, lines, arcs, polylines, BIM solids and meshes. **Missing:** NURBS curves and surfaces, polysurfaces, Untrim, SolidPtOn. |
| Selecting Objects | click, window and crossing, SelAll, SelNone, selection by type | **Have:** click, window/crossing, SELECTALL. **Missing:** selection by type (SelCrv, SelSrf, SelPolysrf), SelNone as a command. |
| Accurate Modeling | typed coordinates, distance and angle, snaps, grid, ortho | **Have:** OSNAP, ORTHO, GRID, typed values, distance and angle constraints (DC*, GC*). |
| Transforms | Move, Copy, Rotate, Scale, Scale2D, Mirror, Orient | **Have:** MOVE, COPY, ROTATE, SCALE, MIRROR, arrays, the gizmo (Rhino's Gumball). **Missing:** Orient (two reference points to two targets), non-uniform Scale2D. |
| Edit Curves and Surfaces | Join, Explode, Trim, Split, Extend, Fillet, Untrim | **Have** for lines, arcs, polylines and walls: JOIN, EXPLODE, TRIM, BREAK, EXTEND, FILLET, CHAMFER. **Missing** for surfaces: Split, Untrim. |
| Create Surfaces from Curves | ExtrudeCrv, Loft, Revolve, RailRevolve, Sweep1, Sweep2, EdgeSrf, PlanarSrf | **Partial:** PAD and PRESSPULL extrude a closed planar profile. **Missing:** all the rest. |
| Curve and Surface Analysis | Dir, CurvatureGraph, Zebra, EMap, CurvatureAnalysis, DraftAngleAnalysis, ShowEdges, Audit | **Partial:** the solid check (V139) finds open (naked) and non-manifold edges and faces turned wrong. CHECKMODEL. **Missing:** the visual surface analyses. |
| Organization and Annotation | layers, dimensions, text, leaders, hatches, dots, notes | **Have:** layers (V121), linear/angular/radius/diameter dimensions, text, leaders, hatches. **Missing:** Dot (a small always-facing label), document Notes. |
| Mechanical Part (and Layouts) | a solid part from primitives and Booleans; Make2D; layouts | **Have:** primitives, UNION, SUBTRACT, INTERSECT, PAD, POCKET; sheets with viewports and title blocks. **Partial:** elevations and sections stand in for Make2D. **Missing:** hidden-line 2D from any view. |
| Pull Toy: Solids and Transforms | primitives, Booleans, Pipe, Cap, transforms | **Have:** primitives, Booleans, transforms. **Missing:** Pipe, Cap, edge fillets on solids. |
| Flashlight: Revolve Curves | a profile curve revolved | **Missing** (Revolve). |
| Headphone: Sweep, Loft and Extrude | rails and profiles into a smooth product | **Missing** (Sweep1/2, Loft). |
| Boat Hull: Loft and Sweep | fair curves, Rebuild, CurvatureGraph, a lofted hull | **Missing.** |
| Penguin: Point Editing and Blending | control-point editing, InsertKnot, BlendSrf | **Missing.** |
| Dragonfly: Trace Images | a picture on a plane, traced with curves; NetworkSrf, BlendSrf | **Partial:** image notes in the drawing (annotation). **Missing:** a scaled picture plane in 3D to trace; NetworkSrf. |
| Wrap Text: Flow along Surface | text as curves, flowed onto a surface | **Missing** (TextObject, FlowAlongSrf). |
| Render | lights, materials, a rendered view | **Partial:** Presentation mode, materials on BIM types, sun and shadows. **Missing:** lights, a rendered image. |

**In short:**
- The app already covers Rhino's drafting, precision, transform, solid and layout chapters, for
  the objects a building is made of.
- What it lacks is Rhino's core: **freeform NURBS curves and surfaces**, with the analysis and
  editing that come with them.
- Separately, **help per command** and a **user guide with versions** are missing.

## 2. A freeform track (F1 to F7), if the owner wants it

Each phase is built on published mathematics, written in ES5 in the app, and checked as every
phase is (a suite, falsified variants, the regression).

| # | Phase | Builds | Verified by |
|---|---|---|---|
| F1 | NURBS curves | Curve (by control points), InterpCrv (through points), degree 1-5; control-point editing; Dir; Rebuild; InsertKnot; the curvature graph | points on a curve against de Boor by hand; an interpolated curve through every point; knot insertion leaving the curve unchanged |
| F2 | Surfaces from curves | ExtrudeCrv (any curve, open or closed), Revolve (exact circles, rational), RailRevolve, Loft (skinning, made compatible), PlanarSrf, EdgeSrf (Coons) | a revolved circle's radius exact; a loft through its sections; areas and volumes against formulas |
| F3 | Sweeps and solids | Sweep1, Sweep2, Pipe, Cap; joining surfaces into closed polysurfaces | V139's solid check (closed, outward); volumes of known shapes |
| F4 | Surface analysis | Zebra, EMap, Gaussian and mean curvature in false colour, draft angle, ShowEdges (naked and non-manifold edges) -- in the Analyze tab | a cylinder's curvature 1/r, a plane's 0; a draft angle known by construction |
| F5 | Point editing and blends | control points on surfaces, BlendCrv and BlendSrf (position, tangency, curvature), MatchSrf | G0, G1, G2 measured across each seam |
| F6 | Images, text, flow | a picture on a plane in 3D, scaled to a known length, to trace; TextObject (text as curves and solids); FlowAlongSrf | the picture's scale; the text's outline area |
| F7 | 2D from 3D and rendering | Make2D (visible and hidden lines from any view, to a sheet); lights (point, rectangular, sun) and a rendered image | a box's Make2D against its edges by hand; a lit sphere's shading |

**Quick wins outside the track:**
- selection by type (SelCrv, SelSrf, SelPolysrf, SelNone);
- Orient; non-uniform scale;
- Dot;
- hide, show and lock single objects;
- help per command, which comes with the guide below.

## 3. A user guide, and versions

What AutoCAD and Rhino publish: a guide by topic, a command reference with a page per command,
release notes per version, and older versions kept.

For this app, on the same GitHub Pages site that serves it:

- **`/docs/`:** a guide in our own words.
  - **Getting started:** the window, the rail, Properties' tabs, the command line and search.
  - **Topics:** drawing, BIM, site and context, survey and terrain, buildings and LOD,
    analysis, sheets, files.
  - Each page is written as its phase is built, and checked like the code: every command and
    field it names must exist in the build.
- **A command reference, generated from the app itself:** every command's name, aliases,
  description, where it sits on the ribbon and its keys, from the same catalogue the command
  search uses. It cannot fall behind the app.
- **Release notes:** one entry per version (V1 onward), drawn from `canvas_v10_STATUS.md`.
- **Versions:**
  - The app says its version (V141) and links to that version's notes.
  - Each version merged to main is tagged (`v141`), and the site keeps the builds at `/v/141/`,
    so an older version stays reachable.
- **Help per command:** F1 (or `?` after a command name) opens that command's page.

## Sources

- The owner's PDFs: *Rhino User's Guide* chapters, Robert McNeel & Associates (read here, not
  redistributed).
- NURBS: Piegl and Tiller, *The NURBS Book* (2nd ed., 1997) -- the standard algorithms (de Boor,
  knot insertion, global interpolation, skinning, swept and revolved surfaces).
- Coons patches: S. A. Coons, *Surfaces for Computer-Aided Design of Space Forms* (MIT, 1967).
