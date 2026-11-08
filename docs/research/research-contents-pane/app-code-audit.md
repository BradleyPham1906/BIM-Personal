# V173 Contents pane: what the app already has (audit, 2026-11-07)

Read from `src/` at main f2b410c (build 3996141 bytes, sha256 6fe27273...). Level P throughout: the app's own code.
Line numbers are as of that commit.

## 1. Four kinds of "layer", four stores

The app has no single layer stack. What a GIS user would call layers are four different things:

| Kind | Store | Drawn by | Draw position | Listed in |
|---|---|---|---|---|
| Model layers (AutoCAD-style, a tree, V121) | `A3D.layers` (`{id,name,parent,color,visible,frozen,locked,plot,linetype,lineweight,transparency,description}`) | every object's own drawer, filtered by `bimLayerShown` | with its objects | Layers panel tree (`layers/layers-panel.js:99`), Layer Properties Manager (`layers/layer-manager.js`) |
| Site analysis layers (V164 to V171) | model layers named `Site analysis - <name>` under `Site analysis` (`site-analysis/model-layers.js:31-54`); the elements are `diag` objects (`o.dg`) | `drawDiagrams` (`model-layers.js:428`), two passes, under and over the solids | `terrain-3d.js` paint lines 396 (under) and 490 (over) | Layers panel tree; the Analyze workspace's left list (V171b/c) |
| Result layers (V148, V158, V161, V172) | `A3D.site.results`-style list read by `bimResLayers()` (`analysis/results-layers.js`) | `drawResultLayers` (`results-layers.js:225`), **plan view only** (returns when the camera is not plan) | paint line 395, under the diagrams | Layers panel, section Analysis (`layers/analysis-data-rows.js:99`) |
| Data layers (V134 to V136) | `A3D.site.dataLayers` (`{id,name,kind,url,color,visible,credit,by,opacity,status,geom}`), features in `A3D.dataFeatures[id]` as `{g: GeoJSON geometry, p: properties}` | `drawDataLayers` (`map/find-open-data.js:315`) at the lowest level's elevation (`bimShadowGround`) | paint line 476, over the solids, under property lines | Layers panel, section Data; Properties, Site, Data layers (`properties/context-lod-data.js:133`) |

Consequences for V173:

- **Drawing order across kinds is fixed by the paint function** (`map/terrain-3d.js` around lines 391 to 495):
  terrain, shadows, simulation overlays, result layers, diagrams (under), solids, Ladybug study, grids, data layers,
  property lines, alignments, hatches, sketches, rooms, dimensions, text, diagrams (over), legends. A Contents pane
  that lets any layer be dragged above any other would mean rewriting paint into one ordered list of drawers: a
  large change touching every drawer. Within a kind, order is already a list.
- **The two existing lists disagree on direction.** Result layers: index 0 is drawn last, so the top of the list is
  on top (`results-layers.js:229` walks from the end) and `bimResultLayerMove` (line 155) reorders it. Data layers:
  drawn in list order, so the LAST is on top, but the panel lists them first to last, so the top row in the panel is
  drawn underneath. ArcGIS's convention is the first (top of the list draws over). Found by this audit; no reorder
  exists for data layers, so the panel's order has never been claimed to be drawing order.

## 2. Symbology today

- **The lens (V136, `map/colour-lens.js`)** colours the model's objects by usage, level, type, layer, material, height
  or a named property. Numbers get six **equal-interval** bins over the min-max range on ColorBrewer's YlOrRd
  (`BIM_LENS_RAMP`, line 20); text gets categories in name order on `BIM_SCHEME_COLS`. One lens for the whole model,
  saved in `A3D.site.lens`, one undo step.
- **Data layers by attribute (V136)**: `L.by` names an attribute; `bimDataLensScale` (line 141) reuses the same scale:
  equal interval in six bins, or categories. No method, no class count, no ramp choice, no manual breaks, no
  "all other values" bucket limit (categories are unlimited; the legend caps rows at 14, `BIM_LENS_MAX_ROWS`).
- **Legend patches** exist in the Layers panel for result layers (`bimResSwatch`, `bimResLegendHtml`,
  `analysis-data-rows.js:35-53`) and as a flat colour bar for data layers; the canvas legend is `drawLensLegend`
  (`colour-lens.js:190`). The diagrams have their own key (`drawDiagramLegend`).
- **No stretch.** Raster-like results (sun hours, slope, elevation, cut and fill) use fixed band tables
  (`BIM_SLOPE_COLS`, `BIM_ELEV_COLS`, `BIM_CUTFILL_COLS`, `BIM_SIM_RAMP`), not a stretch over the values.

## 3. Labels and filters today

- **Labels**: diagrams place their words with a greedy keep-clear test (`bimDgPlaceLabels`,
  `model-layers.js:370`, boxes from `bimDgKeepClear` line 353). Data layers have no labels.
- **Filter / definition query**: none anywhere. Every data feature fetched (up to `BIM_DATA_MAX` = 2000,
  `data-layers.js:22`) is drawn and picked.

## 4. Selection

- Model objects: `A3D.sel`, `A3D.selSet`. Data features: one at a time, `A3D_DATA.sel = {layer, fi}`
  (`find-open-data.js`, picked by `bimDataPick` line 353, "later layers first"). Nothing counts selected features
  per layer. A "by selection" view can list the model layers with their selected-object counts and each data layer
  with 0 or 1; a multi-feature data selection does not exist.
- Selectability: model layers have `locked` (V121b rules, `bimLayerPickable`); data layers have no selectable switch.

## 5. Source

- Data layers carry `url`, `kind` (arcgis, socrata, wfs, geojson), `credit`, `status` (with an error) and a fetched
  date: a "by source" view can group by host and show Failed.
- Result layers carry their run (`R.run`, `R.tool`, created and updated dates) and know when they are stale
  (`bimResStale`, `bimTlStale`) or their source is gone (`bimResGone`).
- Diagrams carry their analysis's source and standards stamp (V167, `bimStdStamp`).
- Model layers have no source; imported files put their objects on a layer named after the file (V163 SketchUp).

## 6. What an exploded layer cake would touch

- Diagrams: every point goes through one function, `bimDgW` (`standards/registry.js:1043`); a per-layer lift
  added there moves a whole analysis up. Labels and keys are screen-space and would follow the points.
- Data layers: one `y` per paint, `drawDataLayers` (`find-open-data.js:318`); a lift per layer is one line. Picking
  (`bimDataPick` line 354) uses the same `y` and would need the same lift.
- Result layers draw only in plan (`results-layers.js:227`), so they cannot appear in an oblique cake without a new
  3D path (an image on a plane, as the map tiles do in `map/map-tiles.js:112`).
- The map tiles and terrain are the natural base of the cake.
- The 3D camera and `toScreen` already project any `[x, y, z]`, so lifted 2D layers need no new renderer: the cake is
  the existing drawers with a height each, in a 3D view.

## 7. Where the pane can live

- The rail's Layers tab (`layers-panel.js`, `analysis-data-rows.js`) already has the model tree and two sections,
  Analysis and Data, each row with a swatch, an eye, opacity, rename, remove; result rows are draggable.
- The Analyze workspace (V171b/c) has its own left list of analyses with ticks that are the layers' visibility.
- Properties shows a data layer's settings (`bimDataModelHtml`) and the lens (`bimLensHtml`).
- File sizes (lines): `layers-panel.js` 132, `analysis-data-rows.js` 373, `colour-lens.js` 261, `find-open-data.js`
  410 (over the 400-line guide already), `context-lod-data.js` about 350. New logic belongs in new files.

## 8. Saved state and undo

- Data layer fields are set through `bimDataSet` (`find-open-data.js:272`), one undo step each, saved with the
  project. New fields (method, classes, ramp, breaks, labels, filter) fit there and in `bimDataSet`'s whitelist.
- Project files carry `A3D.site`, so a filter expression saved in a project travels with it to another machine:
  whatever evaluates it must never run it as code (no `eval`, no `new Function`).
