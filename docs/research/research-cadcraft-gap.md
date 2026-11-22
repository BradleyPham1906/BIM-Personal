# Research: CADCraft against this app, the 2D drafting gap

Asked by the owner, 2026-11-22: "evaluate and fill in the missing features of our current app based on
this app open source on github https://cadcraft.org/online. i think the current app still lacking quite
a lot of features."

This is a gap survey, the first step of the research protocol, not a phase's full research. It says what
CADCraft is, what it does that this app does not, and proposes a drafting track for the owner to choose
from. Each phase it proposes still needs its own research note (sources, experiments, a second reader)
before its SPEC and TASKS are written.

## 1. What CADCraft is

- **A 2D, AutoCAD-style drafting program.** Pure Rust, egui interface, wgpu rendering, a WebAssembly
  build at cadcraft.org/online (upstream v0.18.0, "early development"). Repository
  `github.com/storytold/cadcraft`, MIT OR Apache-2.0. cadcraft.org is an independent guide to it, not
  the upstream project. (S: the site and the repository's README and `docs/gaps.md`, read 2026-11-22.)
- **No 3D solids.** The repository's description says "2D and 3D", but its own gap list says "No 3D" and
  its blog found only `3DPOLY` and the 2D `SOLID`. No B-rep or mesh kernel; its `geom` crate does arcs,
  bulges, splines, intersections and offsets in f64.
- So it is not a competitor to this app's BIM, site, analysis or rendering work. It is a measure of how
  complete a **drafting** tool is, and on that measure this app is well behind.

## 2. The comparison, by area

Our side was read in `src/js/engine/` on 2026-11-22 (P: the code). "Have" means a command exists;
"partial" means a narrower version exists; "missing" means no code was found for it.

| Area | CADCraft | This app | Gap |
|---|---|---|---|
| Object snaps | endpoint, midpoint, center, geometric center, node, quadrant, intersection, insertion, perpendicular, tangent, nearest | vertices of sketches and wall centrelines, grid nodes, construction-line crossings (`bimSnapCandidates`, `drawing/plan-mode-sketch.js:169`) | **missing:** midpoint, center, quadrant, intersection of any two objects, perpendicular, tangent, nearest, insertion; per-mode toggles |
| Tracking | polar tracking, ortho, direct distance entry | ortho, grid snap, typed length along the live direction | **missing:** polar tracking at set angles, object snap tracking |
| Draw | LINE, PLINE with widths, CIRCLE (2P, 3P, TTR), ARC, RECTANG with fillet/chamfer, POLYGON, ELLIPSE and elliptical arcs, SPLINE, POINT, XLINE, RAY, DONUT, MLINE, REGION, HELIX, TEXT, MTEXT, HATCH with gradients | line, polyline with arcs, rectangle, circle (centre and radius), arc, polygon, point, xline, ray, boundary, hatch | **missing:** ellipse and elliptical arc, circle 2P/3P/TTR, donut, polyline widths, revision cloud, wipeout. Spline is already queued (V183, NURBS curves) |
| Modify | MOVE, COPY, ROTATE, SCALE, MIRROR, STRETCH, OFFSET, TRIM, EXTEND, FILLET, CHAMFER, BREAK, JOIN, EXPLODE, ARRAY (associative), draw order, OVERKILL, grips that cycle Stretch/Move/Rotate/Scale/Mirror | rotate, scale, mirror, offset, trim, extend, fillet, chamfer, break, lengthen, align, rectangular and polar arrays (not associative), duplicate, the gizmo | **partial:** move and copy by base point and second point (the gizmo and duplicate do part of it). **Missing:** stretch by crossing window, explode, join for polylines (JOIN here merges walls), overkill, draw order, match properties, associative arrays |
| Constraints | geometric and dimensional, AUTOCONSTRAIN, parameters with expressions | the GC/DC set in sketches (`drawing/sketch-constraints.js`) | **partial:** no auto-constrain, no parameter expressions |
| Dimensions | every DIM type, DIMSTYLE, associative | linear, angular, radius, diameter, leader (`annotation/dimensions.js`) | **missing:** baseline, continue, ordinate, arc length; dimension styles (text height, arrows, units, precision, scale) |
| Text | TEXT, MTEXT with formatting codes, TrueType fonts, text styles | one text tool | **missing:** multiline text, text styles, fonts |
| Leaders, tables | MLEADER, TABLE | leader; schedules | **partial:** no multileader styles; no drawn table object outside schedules |
| Linetypes and colour | linetypes, lineweights, colour index and true colour per layer and per object | AutoCAD's acadiso linetypes and lineweights per layer (`layers/select-change.js`), plot by layer | **partial:** no per-object linetype, colour or lineweight overrides (corrected 2026-11-22: linetypes per layer were already there) |
| Layers | isolate, freeze, off, lock, match, previous, layer states | show, lock, pin, rules, list by | **partial:** no isolate, freeze per viewport, previous, layer states |
| Blocks | BLOCK, INSERT, attributes, nested blocks, external references, image attach | block make and insert, families, the library | **missing:** attributes, a block editor, explode, external references (DXF), images in model space (V188 adds picture planes) |
| Inquiry | DIST, AREA, ID, LIST, MASSPROP, COUNT, QuickCalc | measure, tributary area, area plans | **partial:** no LIST, ID, MASSPROP, COUNT or calculator as commands |
| DXF in | R12 to 2018, ASCII and binary, every common entity | LINE, ARC, CIRCLE, LWPOLYLINE, POLYLINE, POINT, 3DFACE (`io/import-dxf.js`) | **missing:** TEXT, MTEXT, INSERT and blocks, HATCH, DIMENSION, ELLIPSE, SPLINE, linetypes, binary DXF |
| DXF out | R2000 to 2018 | walls, columns and dimensions written as lines and TEXT (`io/dxf-export.js`, 110 lines) | **partial:** no layers' linetypes, blocks, hatches, true dimensions |
| DWG | read R13 to 2018, write R2000, through the open-source acadrust library | none | **missing.** Needs a library (third-party rule, below) |
| Output | PDF plot, SVG, PNG, PUBLISH | PDF, SVG, PNG, sheets, present | close |
| Command line | prompts with clickable keywords, history, autocomplete, aliases, repeat last | command palette, typed commands, prompts with keys | close; repeat-last and clickable keywords not checked |
| Automation | script files, an AutoLISP subset, an MCP server, a JSON control socket | `window.__a3d*` hooks; flows and an app SDK queued (V215) | partial, already planned |

Where this app is far ahead, for balance: everything 3D, BIM elements, IFC, the site, terrain, analysis,
structure, simulation, the rendered view, sheets and presentation boards, history and branches.

## 3. A drafting track, if the owner wants it

Ordered by how much each makes every other tool better. Each would get its own research note and
work orders under the existing workflow (Claude specifies, Cline builds).

| Proposed | What | Why first or later |
|---|---|---|
| D1 | Object snaps (midpoint, center, quadrant, intersection, perpendicular, tangent, nearest, node) with an OSNAP settings dialog, polar tracking (F10) | **Built as V249, 2026-11-22.** Object snap tracking not yet |
| D2 | Modify: move and copy by base point, stretch, explode, join polylines, overkill, draw order, match properties | **Built as V250, 2026-11-22** (MOVE and EXPLODE were typed commands with no handler before) |
| D3 | Draw: ellipse and elliptical arc, circle 2P/3P/TTR, donut, polyline widths, revision cloud, wipeout | Small, independent |
| D4 | Annotation styles: text styles and multiline text, dimension styles, baseline/continue/ordinate/arc-length dimensions, multileaders | Drawings that read like professional sheets |
| D5 | Linetypes and per-object colour and lineweight | Needed for D7's round trip, and for plotting |
| D6 | Blocks: attributes, a block editor, explode, external references | Title blocks and tags carry data |
| D7 | DXF fidelity: read and write text, multiline text, blocks, hatches, dimensions, ellipses, splines, linetypes; binary DXF in | **Import built as V251, 2026-11-22:** blocks (nested, arrays, mirrored), dimensions, TEXT, MTEXT, ATTRIB, ELLIPSE, SPLINE, SOLID, true-arc circles. Still open: HATCH, binary DXF, and the export side |
| D8 | Inquiry: LIST, ID, DIST, AREA, MASSPROP for regions, COUNT, a calculator | Small |
| D9 | DWG | **Built as V252, 2026-11-22** (the owner approved cc-dwg): opens R13 to R2018 through the Import picker, saves the plan as AutoCAD 2013 DWG (EXPORTDWG, DWGOUT, the ribbon's DWG). docs/research/research-dwg-library.md |

## 4. The owner's decisions

1. Add this drafting track to the queue, and where: ahead of the queued phases, or after V202.
2. Which of D1 to D9, and in what order (the table's order is the recommendation).
3. DWG: research a library now (D9), or leave DWG out.
4. Command names: keep matching AutoCAD's names and aliases, as the constraint commands already do
   (recommended: drafters arrive knowing them).

## 5. What is still open

- The CADCraft facts are from its README, `docs/gaps.md` (updated 2026-11-20) and cadcraft.org (S). Its
  ROADMAP, `docs/file-format-parity.md` and the running web build were not checked.
- On our side, associative dimensions, repeat-last-command and the command line's clickable keywords
  were not checked.
- acadrust's license and WebAssembly build were not checked.

## Sources

- cadcraft.org/online, cadcraft.org, cadcraft.org/vs-autocad, cadcraft.org/download,
  cadcraft.org/blog/cadcraft-3d: read 2026-11-22 (S, an independent guide).
- github.com/storytold/cadcraft README and `docs/gaps.md`: read 2026-11-22 (S, upstream's own claims,
  not tested here).
- This repository's `src/js/engine/` at the branch's head, 2026-11-22 (P).
