# V174 research: what the app already has (sheets, boards, figures, map surround)

Part of the V174 research ("Presentation P1: boards"). Written by the main session, 2026-11-08, from the code
at commit 6699a9e (main, after V173d merged). Every line below was read in `src/`, so every fact here is **P**.
Paths are under `src/js/engine/` unless given in full.

## 1. Two kinds of page, drawn two ways

The presentation set today holds two different kinds of page, and they are drawn by two different machines.

| | Sheets (V44, V116, V121, V122) | Boards (V162, V172b) |
|---|---|---|
| Record | `A3D.sheets[]`: `{id, number, name, sizeKey, w, h, viewports[]}` in millimetres (`sheets/sheets.js:63-68`) | `A3D.pres = {boards[], order[]}`; a board `{id, kind, figs?, off?, name?}` (`sheets/boards.js:27-38`, `sheets/board-figures.js:63-101`) |
| Drawn on | A canvas 2D context, at `pxPerMM` (3 on screen, 6 for export: `sheets.js:60`) | HTML: cards of SVG and tables built as strings (`bimBoardHtmlFor`, `bimClbCard`), on a 12-column grid 1408 px wide (`board-figures.js:19`) |
| Elements | Viewports only (plan, elevation, section, schedule), each a rectangle with a scale; one fixed title block | Figures from a catalogue of 33 (`board-figures.js:25-46`), each `{k, f, x, y, w, h, o}` in grid columns and rows (`board-figures.js:72-90`); one free kind, `text` (a heading) |
| Order on the page | The array's order | Reading order, by bands (`bimBrdBands`, `bimBrdOrder`, `board-edit.js:38`) |
| Editing | Drag and size a viewport (`sheets/viewports.js:205-262`); wheel changes the scale (`viewports.js:121`); a properties dialog | Edit mode: move by handle or body, size by corner, arrows nudge, Shift sizes (`board-edit.js:147-224`); Snap, Grid, Ortho shared with the drawing (`board-edit.js:104-133`) |
| Export | PNG (`viewports.js:489`), SVG with vector plans and raster for the rest (`viewports.js:765-824`), print and Print set (`viewports.js:826-910`) | Printed and presented as HTML (`present.js:154`, `bimPrintSetHtml`, `viewports.js:848`) |
| On a phone | The page fitted and zoomed (`pages-display.js:83-128`) | The figures flow in one column in reading order; each figure's menu moves it earlier or later (`board-edit.js:20-27`) |

**Consequence for V174.** "A board is a sheet you design on" has to choose which machine a designed board runs on.
A sheet's canvas has `globalCompositeOperation`, `globalAlpha` and `clip()`, which is where the 16 blend modes and
masks live; a board's HTML has CSS `mix-blend-mode`, `opacity`, `clip-path` and `mask`, which the browser composites
and the print path already prints. Today neither has a layer tree, groups, lock, hide, shapes or images. This is the
largest design choice in the phase and goes to the owner (the main note, part 11).

## 2. Page sizes today

`sheets/sheets.js:34-48`, `SHEET_SIZES`, in millimetres: ANSI A (215.9 x 279.4), ANSI B (279.4 x 431.8), ANSI B
landscape, ANSI D landscape (914.4 x 609.6), A3 landscape, A1 landscape, ANSI D, A4, A3, A1, Custom (420 x 297).
`SHEET_NEW_SIZE = 'ANSI-B-L'` (`sheets.js:50`, V116: drawing sheets are landscape). Missing: ANSI C and E, A0, A2,
every ARCH size, and a portrait or landscape switch independent of the size (each orientation is its own key). The
New Sheet dialog is a select list of these labels (`viewports.js:274-306`); there is no gallery. A sheet keeps its
`w` and `h` as numbers, so a new size list need not break old sheets: `sizeKey` is only a label once the sheet
exists.

The scales (`sheets.js:54-59`): 1:1 to 1:5000 metric, 16 steps; no imperial architectural or engineering scales
(1/8" = 1'-0", 1" = 20'). That matters for a scale bar in feet (map-elements note).

## 3. The title block

`bimDrawTitleBlock` (`sheets.js:367-394`) and its SVG twin `bimBuildTitleBlockSVG` (`viewports.js:738-764`): one
fixed block at the page's bottom right, 90 mm or 42 % of the width by 28 mm or 22 % of the height, four rows:
project, drawn and checked by, client and date, sheet name and number. Fields come from `A3D.titleBlock` and
`bimProjectLabel()`. It is drawn after the viewports, always. Not an element: it cannot be moved, hidden or
replaced. V176 plans title blocks as components; V174 at least has to let a board have none or have it as an
element.

## 4. Viewports: how the model gets onto paper

`bimRenderSourceToCanvas` (`sheets.js:250-297`) redirects the whole `paint()` pipeline at a scratch canvas with the
viewport's camera, sets `A3D.sheetCapture = true` and `A3D_PLOT.pxmm`, paints, and restores every piece of state
in `finally`. `bimCompositeViewport` (`sheets.js:327-366`) clips to the rectangle and draws the image. A viewport
that cannot be resolved draws a labelled grey box and warns, as the build contract asks.

**What a map frame would show today.** Several site layers return early when `A3D.sheetCapture` or `A3D_PLOT.on`
is set, so they never reach paper:

| Layer | Where it stops | Line |
|---|---|---|
| Data layers (V134, V173) | `drawDataLayers`: "on the plan, under the model's linework: never on paper" | `map/find-open-data.js:321-323` |
| The colour lens and its legend | `if(A3D.sheetCapture||A3D_PLOT.on)return;` | `map/colour-lens.js:201` |
| The layer cake | the same | `map/layer-cake.js:77` |
| Map tiles | `if(A3D_PLOT.on)return;` (drawn in a sheet on screen, not in a plot) | `map/map-tiles.js:265, 304` |
| Site analysis legend | `bimDgLegendLayout` returns null | `site-analysis/model-analyses.js:32` |
| The north arrow | `drawNorthArrow` draws only in plan, at the view's corner, as screen chrome | `site/property.js:130-150` |

So a map frame "with a live legend" needs, at the least, data layers and analysis layers drawn under
`sheetCapture`, which V173 deliberately kept off paper. Map tiles in a plot raise their licence's attribution (the
owner's rule: free data, credited); a printed tile needs its credit on the page. Both go to the owner.

## 5. North, scale and legend: pieces that exist

- **True north.** `A3D.site.trueNorth`, degrees from project north, clockwise, normalised to (-180, 180]
  (`site/alignment-profile.js:650-658`); read by `bimTrueNorthDeg()` (`survey/survey-arithmetic.js:5-8`). The plan's
  north arrow turns the vector (sin tn, -cos tn) through the camera (`site/property.js:133-137`), so it is right in
  any rotated plan. There is no grid north or convergence: the model is a local plane in metres.
- **Scale bars.** Two, both SVG strings on boards, each picking a round length from a fixed list:
  `bimZnScaleBar` (`site-analysis/zoning-envelope.js:606-612`: 1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000 m, the
  largest that fits maxW) and `bimAccScaleBar` (`site-analysis/access-board.js:65-71`: 25 to 5000 m, the largest
  under a fifth of the width, km from 1000). One division each, half filled. No feet. A map frame's scale bar can
  generalise these into one function with a units switch.
- **A north arrow on a board.** `bimAccNorth` (`access-board.js:73`): a fixed glyph, not turned by true north.
- **Legends.** The data layer's legend rows (`map/data-symbology.js:105-133`: `bimDataSwatch`, `bimDataLegendHtml`,
  from `bimDataLensScale` and `bimLensRows`), the result layers' (`layers/analysis-data-rows.js:39-60`: `bimResSwatch`,
  `bimResLegendHtml`), the site analyses' key (`site-analysis/model-analyses.js:31-` `bimDgLegendLayout`), the terrain
  bands (`terrain/breaklines.js:508`). They are HTML or canvas, each its own; a live legend element would read the
  same row builders (`bimLensRows`, the results' keys) and draw them on the board, so it agrees with the Layers tab
  by construction.

## 6. Snap, Grid, Ortho, undo, images

- **Snaps.** `A3D_SNAP = {point, grid, gridSize: 0.5, ortho, pxThreshold: 12}` (`drawing/plan-mode-sketch.js:41`).
  The board's `bimBrdSnap` (`board-edit.js:104-133`) catches a moving edge on another figure's or the board's edge
  within 12 screen px, else rounds to the grid, and Ortho locks the larger axis. It snaps edges only: no centres, no
  equal gaps, no distances shown. Smart spacing (the layout note) extends this function's job.
- **Undo.** `pushUndo` pushes `bimSnapshotState()`, a `JSON.stringify` of the whole project state including
  `sheets` and `pres` (`plan-mode-sketch.js:289-300`), up to 50 steps (`UNDO_MAX`). Anything inline in a board
  record is copied into every snapshot.
- **Images.** The plan's image note reads a file as a data URL, refusing over 4 MB (`annotation/annotation-overlay.js:225-241`).
  A 4 MB image inline in a board would be copied into each of 50 undo snapshots (up to about 270 MB of strings,
  since base64 grows by a third) and into every autosave. Images on boards need to be kept once, by reference (an
  id into IndexedDB, which V172f already runs: `core/` store), not inline. This is a design constraint, not a choice.
- **Compositing used today.** `globalAlpha` for layer transparency (`annotation/dimensions.js:141`), and
  `destination-out` to cut holes in analysis fills (`site-analysis/model-layers.js:246-254`). No blend modes anywhere
  (`grep globalCompositeOperation`, `mix-blend-mode`: those two files only).

## 7. File sizes, against the 400-line guide

`sheets/viewports.js` 928, `sheets/presentation-panel.js` 819, `sheets/board-edit.js` 491, `sheets/sheets.js` 470,
`sheets/board-figures.js` 389. V174's code belongs in new files (a board model, its renderer, its layer tree, its
layout and snapping, its map surround), not grown into these.

## 8. What this means for the plan

1. The element model is new: a tree of typed nodes with geometry in millimetres, opacity, blend mode, lock, hide,
   mask flag, and children for frames and groups. The 12-column figure list (V172b) stays readable: a figure can be
   one node kind, placed in millimetres converted from columns, so old boards open unchanged.
2. Map frames reuse the viewport machinery (`bimRenderSourceToCanvas`), with the site layers allowed on paper.
3. The north arrow, scale bar and legend read the existing sources (`bimTrueNorthDeg`, the scale bars' rule, the
   legend row builders), so they cannot disagree with the plan.
4. Snaps extend `bimBrdSnap`'s rule with centres and equal gaps, keeping the same 12 px threshold and the same F3,
   F9, F8 switches.
5. Images by reference, kept out of the undo snapshot's copy.
