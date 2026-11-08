# V175 working note: what the app already has (the main session, 2026-11-08)

Read from `src/` at main e1e3a31, by file and line. Level P throughout (the app's own code). The question this note
answers for each item of V175's row: is it already live on a board, a snapshot, or not on boards at all?

## 1. The one place a model change passes through

- `saveSoon()` (`src/js/engine/bim/region-regenerate.js:95-110`) is called after every model mutation (269 call
  sites, `grep -rn "saveSoon()" src/js/engine`). It runs the sweeps, then `setA3D_REV(A3D_REV+1)` (line 104,
  `__acad3dV122`), `bimFileTouch()` and `bimPagesStale()` (`sheets/pages-display.js:256-262`, which queues the pages
  and the thumbnails 250 ms later).
- `A3D_REV` is declared at `core/objects-save.js:48`, with its comment: "the model's revision, moved by every change
  (saveSoon). What draws a page ... keeps the revision it drew at and draws again only when this has moved."
- Who keys on it already: `sheets/board-edit.js:35` (a built-in board's measured layout), `sheets/board-map.js:66`
  (a map frame's picture), `sheets/pages-display.js:95` (a sheet page's signature, with the title block and project
  label), `sheets/present.js:165` (the slideshow), `sheets/presentation-panel.js:152` (the board's drawn key).
- What moves without `saveSoon` (to be confirmed by the invalidation note): the sun's time while the V170 clock plays,
  the view's camera, map tiles arriving (`board-map.js:65` counts loaded tiles into its key for that reason), images
  arriving from IndexedDB (`board-design.js:217`, `A3D_BIMG.redraw`).

So strategy (b) of the invalidation note, a revision counter, is already the app's design since V122. V175 does not
need a new mechanism to know *that* the model changed; it needs live objects to be drawn from the source at draw time,
and caches keyed on `A3D_REV`.

## 2. Each item of the row

| Item | Today | Where |
|---|---|---|
| Model views | **Live.** V174d's map frame shows a plan, elevation or flat saved view, drawn by the sheets' viewport machinery, its picture cached under `A3D_REV`. A deleted level or view gives the error text in the frame. | `board-map.js:37-78`, `sheets.js:149-155` (`Level no longer exists`) |
| Schedules | **Live on sheets, not on boards.** `bimSheetSourceOptions` lists every registered schedule (`sheets.js:142-146`); the board's map frame filters them out (`board-map.js:36`). | `views/schedules.js` (rooms, `bimBuildRoomSchedule` 219; areas by level, `bimLevelAreas` 177) |
| Legends | **Live.** V174d's legend follows the shown data and result layers, in the Layers order, hidden when empty (D17). Not editable: no override. | `board-map.js:102-114` |
| The boards' charts and KPI cards ("the V157 dashboard") | **Live at the figure level.** A V172b figure (`fig` object) is read from its board each time the board draws (`board-figures.js:20-110`, `bimFigCat`): climate, zoning, access and people figures and the four `*.kpis` card rows. A KPI card cannot be placed alone, and nothing on a figure can be overridden. The name "V157 dashboard" matches no phase in the repository: V157 is Site context C2. The nearest are V159's climate board (ArcGIS Dashboards' indicator practice, PIPELINE) and V162's boards as pages. Open: asked as a decision. | `board-figures.js:32-50`; PIPELINE V159, V162 |
| A result layer's chart | **Not on boards.** Result layers (`A3D.resultLayers`) draw on the model (`analysis/results-layers.js:208-235`) and in the legend; their numbers are in Analyze's panel only. | `results-layers.js:33-66` |
| Analysis results: sun hours, solar | **Kept, with "out of date and why"; not rerun on change.** V143 Solar and V148 Sun hours as result layers, stale when `bimResKey` moves (`results-layers.js:46-56`); V172c's Ladybug studies give the reasons (`ladybug/studies.js:61-71`, `bimLbsStale`). `bimSimStamp` (`analysis/simulation.js:24-32`) hashes the model's meshes, north and sun settings. | as cited |
| Cut and fill | **Kept on the proposed surface** (`o.grading.volume`, `terrain/grading.js:312-336`) by CUTFILL, a command run by hand; the two-surface case is kept in `A3D_ANZ.cutfill` (not saved). Regrading does not rerun it. | `grading.js`, `terrain-tin.js:124` |
| GBA | **Computed on demand.** Gross area by level, `bimLevelAreas(levelId).gross` (`schedules.js:177-218`), from the closed runs of walls; the zoning yield's achievable floor area, `bimZnCalc()` (`site-analysis/zoning-envelope.js:251-322`, `C.achievable`, `C.farGFA`, `C.lot`). | as cited |
| Site area | **Computed on demand.** The property's lot area is `bimZnCalc().lot` (`zoning-envelope.js:315`); the site tools' grid has its own (`site-tools/basic.js`, `grid.js`). | as cited |
| Text bound to project data | **The title block only.** `bimBdsTblock` (`sheets/board-design.js:153-162`) fills nine fields at draw time from `A3D.titleBlock` (project, client, drawnBy, checkedBy), `bimProjectLabel()`, the board's name and its place in the set (`bimPresIndex`, `bimPresSeq`); its identification number and date of issue are typed (`n.num`, `n.dt`, `board-objects.js:93-97`), the date today's until typed. A text object (`t:'text'`) is plain: `bimClbE(n.s)` (`board-design.js:107-113`). | as cited |
| Overrides and Reset | **None on boards.** The nearest pattern is ByLayer: an object's `tr` and `bm` are absent for ByLayer, present when its own (`board-objects.js:56-57`, `bimBobTr` 137). | as cited |

## 3. What constrains the build

- **The record is a whitelist.** `bimBobOne` (`board-objects.js:47-110`) copies only the fields it knows; any new field
  (a binding, overrides) is dropped on load unless it is added there. Old boards must open unchanged (D19).
- **Undo snapshots the whole state** as a JSON string, sheets and boards included, 50 deep
  (`drawing/plan-mode-sketch.js:291-300`, `bimSnapshotState`). A resolved value stored in an object is stored 50
  times and goes stale; a binding is a few dozen bytes.
- **Paper:** `A3D_PLOT.on` hides unplotted layers (`board-design.js:172-182`); map frames key on it. Present mode:
  `bimBdsPres()` (`board-design.js:34`).
- **Numbers are formatted** by `bimDispNum(v,dp)` (`properties/palette.js:67`) across the app (cut and fill toasts,
  usages). `bimBmapFmt` (`board-map.js:135`) is the scale bar's own.
- **One layer system** (the owner, 2026-11-08, research-presentation-boards.md 11a): live objects are board objects on
  `A3D.layers`; their binding, override mark and Reset go in the existing Properties panel
  (`sheets/board-design-props.js:61-127`, `bimBdePropsHtml`).
- **Files over 400 lines:** `viewports.js` 937, `presentation-panel.js` 819, `board-edit.js` 502,
  `board-design-edit.js` 416, `board-figures.js` 401. V175's code goes into new files under `sheets/`.

## 4. What this means for the scope

Of the row's items, model views, legends and the boards' figures are live already; analysis results are kept and
marked stale, never silently rerun. What V175 adds is:
1. a **live field** in text (autotext), resolved at draw time;
2. a **number** object bound to one measured quantity (GBA, cut volume, site area, sun hours ...);
3. a **schedule** and a **result layer's chart** as board objects;
4. single **KPI cards** taken out of a figure;
5. the **override**: an edit on a live object kept as its own value, marked, with Reset; and the stale mark for a
   kept analysis behind a live object.
