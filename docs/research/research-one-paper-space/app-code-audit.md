# One paper space: what the app has today (the main session, 2026-11-12)

Read from `src/` at main 961fc20, by file and line. Level P throughout (the app's own code). The question this
note answers: what is a Page (a sheet) and what is a Board today, where do they overlap, and where do they differ?

## 1. The two records

| | Page (a sheet) | Board |
|---|---|---|
| Kept in | `A3D.sheets[]` (`sheets/sheets.js:64-70`, `bimNewSheet`) | `A3D.pres.boards[]` (`sheets/boards.js:33-43`, `bimPresValid`) |
| Since | V44 (sheets), V116 (layout tabs, sizes, numbering) | V159 to V162 (site boards), V172b (editable), V174 (objects, pages), V175 (live) |
| Its fields | `id, number ('A101'), name, sizeKey, w, h (mm), viewports[]` | `id, kind ('climate', 'zoning', 'access', 'custom'), name, figs[], objs[], lay{}, page{key,o}, off[]` |
| What goes on it | Viewports: a plan, elevation or section at a scale (`scaleDenom`, `scaleMode`), or a schedule as a table | Figures (the site analysis's charts and cards), objects (rectangle, ellipse, line, polygon, star, text, image), title block, sheet frame, map frame (a plan or view at a scale, `board-map.js`), legend, north arrow, scale bar, live text and numbers (V175a), schedules, indicators, result charts (V175b) |
| Title block | One, drawn by the sheet renderer from `A3D.titleBlock` (`sheets.js:376`) | An object (`tblock`, ISO 7200 or a US strip), from the same `A3D.titleBlock` (`board-design.js`) |
| Page size | `SHEET_SIZES` (`sheets.js:31-44`) | V174c's registry of sizes (`page-sizes.js`); a sheet's size is ensured from the same gallery (`bimPgEnsureSheetSize`) |
| Drawn by | Canvas: each viewport through the model's `paint()` into an offscreen canvas (`sheets.js` header, `bimRenderSheet`); SVG for print (`bimBuildSheetSVG`) | HTML and SVG (`board-design.js`, `bimBdsHtml`); a map frame's picture through the same viewport machinery, cached on `A3D_REV` (`board-map.js:62-78`) |
| Edited by | The sheet bar: + Viewport, Sheet Setup, Title Block, Export PNG, Export SVG, Print, Present, Close (`ui/build-ui.js:221`); drag and resize viewports (`viewports.js:216-260`); work in a viewport (model space through paper, `bimSetModelSpace`) | The board bar: Edit, Add a figure, Draw, Page, Reset, Done (`board-figures.js:261-284`); objects on the one layer table, Properties panel, align, distribute, stacks (V174) |
| Layers | The model's layers decide what a viewport shows | Every object is on a layer of the same one table (V174a, R1 to R4) |
| Tabs | A layout tab each, beside Model (`layout-tabs.js:21-30`) | No layout tab; opened from the Presentation panel |
| In the set | Yes: `bimPresSeq` interleaves sheets and boards in one order (`boards.js:51-64`) | Yes, the same order |
| Present | One slideshow over the set (`present.js`, `bimSlideshowStart`), from the panel, the sheet bar, or a page's menu (`layout-tabs.js:178`, `boards.js:161`) | The same slideshow |
| Print set | One print of the set (`viewports.js:854-899`): a sheet as SVG at its size, a board as HTML at its page size or A3 strips | The same print |

## 2. Where they overlap

Since V174c and V174d a board with a page is a sheet in all but name: a page size from the same gallery, a title
block from the same project fields, a frame, and map frames that are viewports (a plan or view at a scale, panned,
drawn by the same viewport renderer). A sheet cannot hold text, shapes, images, legends, live values, schedules as
objects, or figures; a board cannot hold a section, is not numbered as a drawing (A101), and has no layout tab.

So the app has two paper spaces with two editors, two toolbars, two ways to place a view at a scale, and two ways
to draw a title block, joined by one set, one Present and one Print.

## 3. Drafting aids on paper

- One setting, `A3D_SNAP` (`drawing/plan-mode-sketch.js:42`: point, grid, gridSize, ortho), toggled by the status
  bar, F3, F8, F9 (`ui/touch-input.js:236-238`, `ui/build-ui.js:1051-1052`).
- A board obeys it (`board-design-edit.js:289-298`) and its Edit bar shows the same toggles again
  (`board-edit.js:105`, `data-brdsnap`).
- A sheet ignores it: dragging a viewport moves it freely (`viewports.js:249-260`, no `A3D_SNAP`), and on a sheet the
  status bar hides the aids altogether (`css/sheets/layouts-pages-present.css:56`: `.a3d-onsheet #a3d-snapgrp
  {display:none}`; `layout-tabs.js:38`, "the model's aids step aside on paper"). This is what the owner saw.
- "Pres" in the status bar is the Presentation appearance (`plan-mode-sketch.js:137`, Tech or Pres), not Present.

## 4. Size of each side

| | Files | Lines |
|---|---|---|
| Pages: `sheets.js`, `viewports.js`, `pages-display.js`, `layout-tabs.js`, `page-sizes.js` | 5 | 2,015 |
| Boards: `boards.js`, `board-*.js`, `live-*.js`, `presentation-panel.js`, `present.js` | 17 | 4,976 |
| Browser suites naming sheets, layouts or viewports (V110 to V122) | 16 | |
| Browser suites naming boards (V162 to V175) | 21 | |
| Callers of `bimSheetOnScreen()` | 23 | |

The board side is the larger and the newer, and already has the object model (layers, Properties, align, stacks,
live values). The page side has what a drawing set needs that boards lack: numbering, layout tabs, sections and
schedules as viewports, model space through a viewport, vector (SVG) export.
