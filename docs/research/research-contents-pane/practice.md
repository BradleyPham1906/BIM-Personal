# V173 research: practice in the professional tools (Contents pane, symbology, labels, filters, layer cake)

Part of the V173 research ("Site analysis SA6: the Contents pane"). This note covers how the professional
tools do it, read from their own documentation. No code was written and no downloaded code was run. Open-source
code (QGIS, kepler.gl) was read as text only.

Levels: **P** read in the primary source itself; **S** dependable secondary source, gap stated; **U** search
summary only, to confirm. U facts must not reach the code.
Dates: pages fetched 2026-11-07 unless marked (08) for 2026-11-08.
Esri pages were read in the ArcGIS Pro 3.5 help (`pro.arcgis.com/en/pro-app/3.5/...`), because the
`latest` addresses now redirect to `doc.esri.com`, and some of those redirects return 404. The Contents pane page
was also checked in the latest (3.7) help on doc.esri.com: it lists the same tabs.

## 1. Search log

| # | Where | Query / address | What came back | Kept / set aside |
|---|---|---|---|---|
| 1 | WebFetch | pro.arcgis.com latest contents-pane | 301 to doc.esri.com, then 404 | Set aside; used versioned 3.3/3.5 pages |
| 2 | WebSearch | "Contents pane" "List By Drawing Order" ... | Pro 2.6 to 3.6 Contents pane pages | Pointer only; the page was then read (P) |
| 3 | curl | Pro 3.5 contents-pane.htm | Six tabs, the filter list | Kept (P) |
| 4 | curl | Pro 3.3 unique-value.htm | Up to 3 fields; all other values; Add all values | Kept (P) |
| 5 | curl | Pro 3.5 graduated-colors.htm, data-classification-methods.htm | Methods, normalization, 7-colour guideline; no default stated | Kept (P) |
| 6 | WebSearch | default Natural Breaks 5 classes | Pointers to the Pro SDK and to training blogs | SDK page read (P); the blogs are not used |
| 7 | curl | Pro SDK GraduatedColorsRendererDefinition (topic11645) | Defaults NaturalBreaks and 5 | Kept (P, SDK, gap: the SDK, not the GUI) |
| 8 | curl | arcpy GraduatedColorsRenderer | Method keywords; std-dev intervals 1, 0.5, 0.333, 0.25; normalization keywords | Kept (P) |
| 9 | curl | Pro 3.5 symbology-pane.htm (imagery) | Raster symbology types, stretch types, Classify, the 2,048 limit | Kept (P) |
| 10 | curl | stretch-function.htm; arcpy image-analyst stretch; set-raster-and-imagery-default-options | No default percent clip or n stated | Kept as negative evidence |
| 11 | WebSearch / WebFetch | percent clip default 0.5 | Two university tutorials ("default is Percent Clip"); one teaching site (0.5 %, Pro 2.9.1) | S, with the gap stated |
| 12 | curl | ArcMap stretch-function | No default n | Negative evidence |
| 13 | curl | definition-query.htm, write-a-query..., construct-and-modify-queries | Definition query behaviour; designer and editor modes | Kept (P) |
| 14 | WebSearch | query builder operators "is equal to" "includes the value(s)" | WWU guide (503 when fetched); Pro SDK enums | Operator labels stay U; SDK SQLPredicate read (P) |
| 15 | curl | GP query-builder (3.0); SDK SQLPredicate (topic14513) | Clause mode steps; predicate list incl. BETWEEN, IN, LIKE, IS NULL | Kept (P) |
| 16 | curl | labeling-basics, label-classes, specify-text-for-labels, standard engine | Label class, default field rule, scale range, Maplex default | Kept (P) |
| 17 | curl | repair-broken-data-links, work-with-group-layers, symbolize-feature-layers | Red exclamation point; group types; legend patch | Kept (P) |
| 18 | raw.githubusercontent | QGIS-Documentation master: general_tools.rst, vector_properties.rst, raster_properties.rst, qgis_configuration.rst | Layers panel, Layer Order, renderers, Query Builder, min/max | Kept (P). The commit hash could not be read (the GitHub API is closed to this session): the files are the master branch on 2026-11-07 |
| 19 | raw.githubusercontent | QGIS master source: qgsgraduatedsymbolrendererwidget.ui/.cpp, qgsrasterminmaxorigin.h | Default class count 5, Jenks warning, 2 %/98 %, std-dev factor 2.0 | Kept (P, source read as text) |
| 20 | WebSearch | McHarg overlay method darker tone | PSU GEOG 160, Interreg page, CSISS PDF, spam PDFs | PSU and CSISS read; the spam sites set aside |
| 21 | curl / pdftotext | PSU GEOG 160 node 1975; CSISS Classics (Corbett 2001); Penn Architectural Archives finding aid | The quotation (p. 34); method; "layer cake method" | Kept (S) |
| 22 | WebSearch | Spirn "layer cake" "the litany" | Pointer to Spirn's essay (the uop.edu.jo PDF returned 503) | U |
| 23 | curl | Esri 10.1 "GIS is based on layers" | McHarg, Tomlinson, layers as the GIS principle | Kept (P for Esri's own statement) |
| 24 | curl | Qgis2threejs docs 3.3 Exporter | Altitude mode, expression, Add Flat Plane | Kept (P) |
| 25 | curl | doc.esri.com arcpy LayerElevation | cartographicOffset, elevationMode | Kept (P) |
| 26 | raw.githubusercontent (08) | kepler.gl docs and src/constants default-settings.ts | Layers panel, filters, scale types | Kept (P) |
| 27 | WebFetch (08) | help.felt.com style-vector-layers.md | Style types, methods, default Continuous | Kept (P) |
| 28 | WebSearch / WebFetch (08) | Mapbox Studio layers panel; choropleth page | Pages moved; only the blog and search summaries | U |
| 29 | WebFetch (08) | Giraffe Intercom "Custom layer styling" | Data Table Style and Filter; Style JSON | Kept (P, thin) |
| 30 | WebFetch (08) | Esri "ArcGIS for Autodesk Forma user interface" | Layers tab: show/hide, chips, Remove | Kept (P, for the ArcGIS add-in in Forma only) |
| 31 | WebSearch (08) | archiMap; UrbanEyes | Nothing about either product | Not found |
| 32 | WebSearch / WebFetch (08) | Brewer and Pickle 2002 | Penn State Pure abstract | Kept (P for the abstract) |

## 2. Findings by topic

### 2.1 ArcGIS Pro Contents pane

- **Tabs (list-by views).** The Pro 3.5 help lists six tabs: Drawing Order, Data Source, Selection, Editing,
  Snapping and Labeling. "The active tab is indicated with a blue underline." The latest (3.7) page lists the
  same six. **No "Perspective" tab and no "Charts" tab is documented for maps.** (P, high)
- **Drawing Order.** "Layers at the top of the list draw above those below them." You drag a layer to reorder
  it, and a check box beside each layer controls whether it is visible. A layer outside its visible scale range
  shows "a grayed check box and a line underneath the box". The order is saved with the project. Pro also says
  "You cannot return to a prior state of the drawing order in a session", that is, reordering cannot be undone.
  In a scene, this tab sorts layers into the 2D Layers and 3D Layers categories. (P, high)
- **Data Source.** "Group and manage layers and tables by their data sources." (P, high)
- **Selection.** "When a selection is made, the number of features selected is shown next to the layer name."
  You can clear a layer's selection from this tab. Layers that cannot be selected, such as rasters, are listed
  without a selection check box. (P, high)
- **Editing, Snapping.** These tabs list the layers that can be edited and the layers that take part in
  snapping. (P, high)
- **Labeling.** You expand a layer to see its label classes. From there you can duplicate and reorder them,
  open their properties, copy properties between classes, and edit several classes at once. (P, high)
- **Ctrl-click** on any check box checks or unchecks every layer at once. (P, high)
- **Search and Filter.** A search box finds items by name. Only one Filter can be active at a time, and a tag
  above the tabs shows it. The filters are: All layers (the default), Visible, Nonvisible, Layers with a
  visibility range set, Active definition queries, Stand-alone tables, Empty feature layers, Time-enabled,
  Range-enabled, Layers with display filters enabled. The repair page adds a Broken data link filter. (P, high)
- **Broken data source.** A layer whose source is unavailable does not draw, and the Contents pane marks it
  with a red exclamation point. Clicking the mark opens the Change data source dialog. (P, high)
- **Legend patches.** Legend patches "change the preview shape of the symbol shown in the Symbology and
  Contents panes, as well as in layout legends". They apply to single symbol, unique values, graduated colours
  and graduated symbols (lines only), on line and polygon layers. Clicking a symbol in the Contents pane opens
  Format Symbol. (P, high) Pro does not describe in prose how the classes appear expanded under a layer; it is
  shown in its figures. (gap)
- **Group layers.** Turning a group off hides all of its sublayers. Properties set on the group (visibility
  range, transparency, blending) override those of its sublayers. The sublayers are indented when the group is
  expanded. You make a group with New Group Layer, by dragging, or by right-clicking and choosing Group; Ungroup
  undoes it. The group type is **Checkbox** (many sublayers can draw at once) or **Radio** (one at a time).
  Tables always sit at the bottom of the drawing order. (P, high)
- **Raster unique values.** If a raster has 2,048 or more unique values, Pro does not load them into the
  Symbology pane. (P, high)

### 2.2 ArcGIS Pro symbology

- **Primary types for feature layers:** Single symbol, Unique values, Graduated colors, Bivariate colors,
  Unclassed colors, Graduated symbols, Proportional, Dot density, Charts, Heat map, Dictionary. (P, high)
- **Unique values.** A layer can have "up to three symbology fields", and only the first can use an
  expression. "When choosing a field for unique values for the first time, no values are added": you press
  Add all values. Values with no class of their own draw together in an "All other values" class at the bottom
  of the table, which you can turn off under More by unchecking "Show all other values". The help implies the
  class is on by default, and an Esri support article says so (S, via a search pointer). You can group values
  (select several, then Group values) and drag classes into a new order. The colour scheme list is filtered to
  the number of values, and random schemes are offered. The help states no maximum number of values for
  features. (P, high)
- **Graduated colours.** The help says "A range of seven colors is the approximate upper limit of colors that
  can be clearly distinguished on a map." Normalization takes a field, **percentage of total** or **log**, and
  is available only when the symbology is based on a field. The colour schemes offered follow the method and
  the class count (standard deviation offers diverging schemes). The More menu can add `<out of range>` and
  `<excluded>` classes and a count column. "The default sample size is 10,000 records." (P, high)
- **Default method and class count.** The GUI help never states them. The Pro SDK constructor
  `GraduatedColorsRendererDefinition` defaults to "NaturalaBreaks" (sic) and 5 breaks. (P for the SDK; S for
  the GUI, medium) Training sites say the GUI uses the same defaults (U, not used).
- **Classification methods** (help topic): Natural breaks (Jenks), Quantile, Equal interval, Defined interval,
  Manual interval, Geometrical interval, Standard deviation. (P, high)
  - Jenks: classes follow natural groupings. It is "data-specific" and "not useful for comparing multiple maps
    built from different underlying information". (P)
  - Quantile: each class holds the same number of features. The help warns the map "can often be misleading",
    because similar values can fall into neighbouring classes and very different values into the same class.
    More classes reduce this. (P)
  - Equal interval: the range is split into equal parts. It is "best applied to familiar data ranges, such as
    percentages and temperature". (P)
  - Defined interval: you set the interval size, and the class count follows from it. The interval must allow
    at least three classes. (P)
  - Geometrical interval: the class widths follow a geometric series, as a compromise between the other
    methods. It is designed for continuous data. (P)
  - Standard deviation: the classes are equal steps of 1, 1/2, 1/3 or 1/4 standard deviation from the mean.
    arcpy accepts exactly the intervals 1.0, 0.5, 0.333 and 0.25. (P, high)
  - Changing a class's upper bound switches the method to Manual interval. (P, arcpy)
- **Raster symbology types:** RGB, Unique Values, Stretch, Colormap, Classify, Discrete, Shaded Relief and
  Vector Field. Only the types valid for the data are offered. Classify and Discrete work on one band only.
  (P, high)
- **Stretch types** for the Stretched renderer: None, Minimum Maximum, Percent Clip, Standard Deviation,
  Histogram Equalization, Histogram Specification, Custom, Esri (sigmoid). Square Root and Logarithm are for
  SAR data only. The histogram can be edited for Minimum Maximum, Percent Clip and Standard Deviation. The
  statistics come from DRA (the current extent), the Dataset, or Custom values. Each percent clip value runs
  from 0 to 99. (P, high)
- **Stretch defaults.** No Esri page read here gives the default percent clip or the default n (the help,
  the raster function, arcpy, the Options page and ArcMap were all checked). Two university tutorials (Colby;
  Bard, Pro 3.3) say "The default is Percent Clip". A teaching site (Meisterlin, Pro 2.9.1) says the default
  is 0.5 % at each end. (S, medium) No source for **n = 2.5** was found. (U; leave it out)
- **Classify (raster):** Field, Normalization (field, Percent of total, Log), Method (the same classification
  methods), Classes and Color scheme, with Classes, Histogram and Mask subtabs. (P, high)

### 2.3 ArcGIS Pro labels and definition queries

- **Labels.** The label text comes from a field or an expression (Arcade, Python, VBScript or JScript).
  "This label field defaults to the first field of string type that contains the text Name in its name (not
  case sensitive)". Failing that, it is the first string field, then the first integer field, then the first
  field of any type. **Label classes** each have their own expression, an SQL query that picks which features
  they label, a symbol, a placement and a scale range. "If no scale is set, the labels have the same scale
  range as the feature layer." Classes can be made from the symbology classes. The default engine is Maplex,
  with Tahoma, Regular, 10 pt. Labels keep the same size on the page unless the map has a reference scale.
  Placement is set on the Position tab and depends on the geometry (point, line or polygon). (P, high)
- **Definition queries.** A definition query limits which features "are retrieved from the dataset by the
  layer". It changes not only what draws but also what appears in the attribute table and what can be
  selected, labelled, identified and processed. Display filters, by contrast, limit only what is drawn. A query
  is one or more SQL clauses plus, optionally, one spatial clause. "A layer can have multiple definition
  queries associated with it, but no more than one definition query can be active at a time". All of them can
  also be off. The queries are named. Selecting several layers lets you activate the queries that share a name
  on all of them at once. The query builder has a Designer mode (clauses, the default) and an SQL Editor mode
  ("The WHERE clause is assumed"). (P, high)
- **Clause mode.** You add a clause, pick a field, pick an operator, then pick or type a value. "Valid options
  are displayed depending on the field type". Clauses are joined with And or Or and can be grouped. (P, high)
- **Operator labels.** The help gives only examples ("Is Equal To", "Is Greater Than"). The SDK's SQLPredicate
  list is Between, Equal, Exists, GreaterThan(Equal), In, IsNull, IsNotNull, LessThan(Equal), Like, NotBetween,
  NotEqual, NotExists, NotIn, NotLike, SimilarTo, NotSimilarTo. (P for the SDK list) The designer labels "does
  not equal", "includes the value(s)", "contains the text", "begins with", "ends with", "is null", "is above/below
  average" come from a university guide and a forum thread (U). The forum thread also says "does not include the
  values" matches whole values and "does not contain the text" matches part of a value (U). "Is between" was not
  confirmed as a designer label (open).

### 2.4 QGIS (user manual, master branch, read on 2026-11-07)

- **Layers panel** ("also called the map legend"). A checked layer is drawn. Dragging a layer changes its
  Z-order, and higher layers draw on top. The toolbar has: Layer Styling, Add group, Map Themes, a filter menu
  (Filter Legend by Map Content, Show Private Layers, **Show Broken Layers Only**), Filter Legend by Expression,
  Expand All, Collapse All and Remove. **Show Feature Count** is in the context menu. Classified renderers list
  their classes under the layer, each with its own check box, and right-clicking a class offers Toggle Items,
  Show All Items, Hide All Items, Rename Item, Select features, Show in attribute table, a colour wheel and Edit
  Symbol. Layers added together are stacked points, then lines, polygons, point clouds, meshes, rasters. (P, high)
- **Layer Order panel** (Ctrl+9). "Control rendering order" sets a drawing order separate from the legend's
  order. A group set to "Render layers as a group" appears in it as one entry. (P, high)
- **Categorized renderer.** The value is a field or an expression. You pick a colour ramp (optionally random)
  and press Classify. "By default, QGIS appends an all other values class". Each class has a check box that
  hides it, and classes can be added, deleted ("Delete Unused" too) or dragged into a new order. (P, high)
- **Graduated renderer modes:** Equal Count (Quantile), Equal Interval, Fixed Interval, Logarithmic scale,
  Natural Breaks (Jenks), Pretty Breaks (R's `pretty`: steps of 1, 2 or 5 times a power of 10), Standard
  Deviation. There is an interactive histogram, and each class can be turned off. (P, high)
- **QGIS defaults, from the source.** The class count widget starts at **5** (range 1 to 999, in
  `qgsgraduatedsymbolrendererwidget.ui`). The mode list is filled from a name-sorted map, so the first entry
  in English is "Equal Count (Quantile)". This is an inference about the default mode. (P for the source,
  medium for the default mode) Jenks above 50,000 features asks for confirmation ("O(n2) complexity"). (P, high)
- **Raster Min/Max** (Singleband gray and pseudocolor): User defined, **Cumulative count cut (2 % to 98 %)**,
  Min/max, Mean +/- standard deviation x. The statistics extent is Whole raster, Current canvas or Updated
  canvas, with Estimate or Actual accuracy. The source constants are `CUMULATIVE_CUT_LOWER = 0.02`,
  `CUMULATIVE_CUT_UPPER = 0.98` and `DEFAULT_STDDEV_FACTOR = 2.0`. (P, high) The pseudocolor colour ramp
  shader has Discrete, Linear and Exact interpolation and the modes Equal interval, Continuous and Quantile.
  Its legend is by default "a continuous color ramp with min and max values". (P, high)
- **Labels:** No labels (the default), Single labels (a field or an expression), Rule-based, or Blocking, with
  scale-dependent visibility. (P, high)
- **Filter (Query Builder).** It is "a SQL-like WHERE clause" applied by the data provider, so the syntax
  depends on the provider. The dialog has Fields, Values (All, or a Sample of 25) and Operators buttons, plus
  Test, which reports the number of matching features, Clear, and Save/Load (.QQF). Only the subset exists for
  the project while the filter is on. A filtered layer shows a filter icon in the Layers panel, and
  double-clicking the icon opens the builder. (P, high)

### 2.5 McHarg's layer cake and stacked 3D views

- **The method.** McHarg (Design with Nature) mapped each factor on a transparency: physiographic factors "so
  that the darker the tone, the greater the cost", and social values so that darker meant higher value. "When
  these are superimposed, the least-social-cost areas are revealed by the lightest tone." The quotation is from
  p. 34, as quoted in PSU GEOG 160, which cites the 1971 printing. (S, high; gap: the book itself was not read)
- Corbett (CSISS Classics, 2001): there was one transparency per factor, darkest for the greatest value, and
  all were "superimposed upon one another over the original map". (S, high)
- **The name.** The Penn Architectural Archives finding aid (2008) calls McHarg's approach the "layer cake
  method" of mapping and says GIS uses "the same 'layer cake method'". (S, high) Spirn's account says students
  called the ecological inventory "the layer cake" or "the litany", always in the same order (climate,
  geology, hydrology, soils, vegetation, wildlife). (U: the PDF did not load)
- Esri's own help (10.1, "GIS is based on layers") credits McHarg's overlays and Tomlinson's thematic layers
  as the origin of GIS layers. (P, high)
- **3D stacking in the tools.**
  - ArcGIS Pro: each 3D layer has an `elevationMode` and a `cartographicOffset` that "adjust where features
    are drawn vertically relative to the base height" (arcpy LayerElevation). A layer cake can therefore be
    built by giving each layer an absolute height plus an offset. (P, high) Esri has no "layer cake" command.
  - Qgis2threejs: a vector layer's Altitude Mode is Absolute or Relative to a DEM, and its altitude is a
    numeric expression. The Scene menu has "Add Flat Plane" with a set altitude. Stacking is possible this way,
    but no stacking command is documented. (P, high)
  - No tool read here has a one-click "explode the layer stack". (medium; a search for one found nothing)
- **What the stack diagram shows.** The illustrations themselves could not be inspected, so the usual drawing
  stays **U**: oblique view, equal gaps between the sheets, the name of each layer beside its sheet, and the
  base map (or the composite) at the bottom or at the top. The only text-backed points are the fixed order of
  the factors (Spirn, U) and the superimposition over the base map (Corbett, S).

### 2.6 Prior art in other apps

See the table in section 4.

## 3. Defaults table

| Item | Tool | Default | Level / source |
|---|---|---|---|
| Graduated colours method | ArcGIS Pro | Natural Breaks (Jenks) | P (SDK); GUI not stated |
| Graduated colours classes | ArcGIS Pro | 5 | P (SDK); GUI not stated |
| Readable class limit | ArcGIS Pro help | about 7 colours | P |
| Std-dev intervals | ArcGIS Pro | 1, 1/2, 1/3, 1/4 sd | P |
| Defined interval minimum | ArcGIS Pro | 3 classes | P |
| Classification sample size | ArcGIS Pro | 10,000 records | P |
| Unique values "all other values" | ArcGIS Pro | shown (on) | P (implied), S (support article) |
| Unique values on first field pick | ArcGIS Pro | no values added until Add all values | P |
| Raster unique values not loaded | ArcGIS Pro | 2,048 or more values | P |
| Raster stretch type | ArcGIS Pro | Percent Clip | S (two tutorials) |
| Percent clip min / max | ArcGIS Pro | 0.5 % / 0.5 % | S (one tutorial, Pro 2.9.1) |
| Std-dev stretch n | ArcGIS Pro | not found (2.5 unconfirmed) | U |
| Label field | ArcGIS Pro | first string field whose name contains "Name", then rules | P |
| Label engine / font | ArcGIS Pro | Maplex; Tahoma Regular 10 pt | P |
| Label scale range | ArcGIS Pro | the layer's own range | P |
| Active definition queries | ArcGIS Pro | at most one per layer | P |
| Query builder mode | ArcGIS Pro | SQL Designer (clauses) | P |
| Contents filter | ArcGIS Pro | All layers | P |
| Graduated classes | QGIS | 5 (1 to 999) | P (source .ui) |
| Graduated mode | QGIS | Equal Count (Quantile), first in the sorted list | P source, medium inference |
| Jenks warning | QGIS | above 50,000 features | P (source) |
| Categorized "all other values" | QGIS | appended | P |
| Cumulative count cut | QGIS | 2 % to 98 % | P (manual and source) |
| Mean +/- sd factor | QGIS | 2.0 | P (source) |
| Labels | QGIS | No labels | P |
| Query Builder sample | QGIS | 25 values | P |
| Colour range method | Felt | Continuous (no classes) | P |
| New layer style | Felt | Simple | P |

## 4. Prior art table

| App | Layer list | Legend | Filter | Styling | Level |
|---|---|---|---|---|---|
| ArcGIS Pro | Contents pane, 6 tabs, drag order, check box, selected count, red "!" when broken | Classes and patches under each layer | Definition queries (many, one active), display filters | Single, unique (3 fields), graduated (7 methods), stretch, classify | P |
| QGIS | Layers panel plus Layer Order panel, feature count, broken-only filter | Class entries with check boxes, Toggle/Show/Hide All | Provider Query Builder, filter icon in the panel | Categorized, Graduated (7 modes), pseudocolor min/max | P |
| kepler.gl | Layers panel: drag to reorder ("top ... foreground"), eye to show/hide, a coloured bar per dataset; blending Normal/Additive/Subtractive | Not described in the docs read | Filters panel: dataset, field, value by type; polygon/rectangle filter; applies to every layer of the dataset | Colour by field; scale types ordinal, quantile, quantize, (linear, sqrt, log), custom breaks, custom ordinal | P (docs and source constants) |
| Felt | (not read) | You can drag a category to change its place in the legend | A separate "Filter layers" page (not read) | Simple, Categories, Color range, Size range, Heatmap, H3; methods Continuous (default), Equal intervals, Quantiles, Standard deviations, Geometric intervals, Jenks, Manual | P |
| Mapbox Studio | Layers panel (left), the style holds the layer order | n/a | "data conditions" | "Style across data range", "Style with data conditions", nested with zoom | U (manual pages moved) |
| Giraffe | Layer palette by kind: Drawing, Geospatial, Portfolio, Raster, Temporary | Not documented | Data Table "Style and Filter" | Data Table Style, or Mapbox style JSON | P (thin) for styling; U for the rest |
| Forma (ArcGIS add-in) | Layers tab: show/hide, View-only/Images chips, type icons, Refresh, Remove | Not on the page | n/a | n/a | P (Esri's add-in page only) |
| archiMap | not found | | | | none |
| UrbanEyes | not found | | | | none |

## 5. Counter-evidence and limits

- **Jenks.** Esri says the breaks are data-specific and not comparable between maps (P). QGIS warns that the
  algorithm is O(n^2) and asks before running it on more than 50,000 features (P, source). In the abstract of
  Brewer and Pickle (2002, Annals of the AAG 92(4)), natural breaks and a hybrid equal interval were "less
  than 70 percent as accurate as for quantiles" on map-reading tasks across a map series (P, abstract). With
  few distinct values, Jenks cannot make more classes than there are values: this is logical, but no source
  read here states it (open; to test in an experiment).
- **Quantile.** Esri warns quantile maps "can often be misleading" (P). The counter-evidence is Brewer and
  Pickle (2002): quantiles and minimum boundary error were "best suited" for general map reading, and the
  optimised methods "seem to offer no benefit over the simpler quantile method" (P, abstract). Using the same
  legend across a series raised map-comparison accuracy by about 28 % (P, abstract). The two positions are
  compatible: the method matters less than legend consistency for comparing maps, and quantile can still mislead
  on skewed data with ties.
- **Equal interval** suits familiar ranges such as percentages and temperature (Esri, P). It leaves classes
  empty on skewed data (a known property, not from a source read here; U).
- **Colour count.** Esri's guideline is about seven distinguishable colours (P).
- **Percent clip and std-dev stretch** are display stretches: they push outliers to the ends of the ramp, so
  the legend's min and max are not the data's min and max (Esri stretch function, P). This matters for a legend
  patch under a raster.
- **Definition query versus display filter.** In Pro a definition query also removes features from analysis,
  labels and selection (P), and QGIS treats the filtered subset as the whole layer (P). A "filter" in the
  Contents pane is therefore a data change, not only a display change. The two products agree on this.
- **Layer cake.** The overlay method assumes the factors are independent and of equal weight. That is a known
  criticism in planning, not checked against a source here (U). The tools read here have no layer-cake view;
  ArcGIS Pro (offsets) and Qgis2threejs (altitudes) make one possible by hand.

## 6. References

| What | URL | Read | Date | Level |
|---|---|---|---|---|
| Pro 3.5 Contents pane | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/map-authoring/contents-pane.htm | whole page | 2026-11-07 | P |
| Pro latest Contents pane | https://doc.esri.com/en/arcgis-pro/latest/help/mapping/map-authoring/contents-pane.html | tabs table | 2026-11-07 | P |
| Pro 3.3 Unique values | https://pro.arcgis.com/en/pro-app/3.3/help/mapping/layer-properties/unique-value.htm | setup, modify, More menu | 2026-11-07 | P |
| Pro 3.5 Graduated colors | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/layer-properties/graduated-colors.htm | draw, normalization, color scheme, More | 2026-11-07 | P |
| Pro 3.5 Data classification methods | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/layer-properties/data-classification-methods.htm | whole page | 2026-11-07 | P |
| Pro SDK GraduatedColorsRendererDefinition ctor | https://pro.arcgis.com/en/pro-app/3.6/sdk/api-reference/topic11645.html | parameters | 2026-11-07 | P |
| arcpy GraduatedColorsRenderer | https://pro.arcgis.com/en/pro-app/3.5/arcpy/mapping/graduatedcolorsrenderer-class.htm | properties | 2026-11-07 | P |
| Pro 3.5 Change the symbology of imagery | https://pro.arcgis.com/en/pro-app/3.5/help/data/imagery/symbology-pane.htm | RGB, Unique Values, Stretch, Classify | 2026-11-07 | P |
| Pro 3.5 Raster histogram stretching | https://pro.arcgis.com/en/pro-app/3.5/help/data/imagery/histogram-stretching.htm | intro, table | 2026-11-07 | P |
| Pro 3.5 Stretch function | https://pro.arcgis.com/en/pro-app/3.5/help/analysis/raster-functions/stretch-function.htm | parameters, stretch types | 2026-11-07 | P |
| arcpy Image Analyst Stretch | https://pro.arcgis.com/en/pro-app/3.5/arcpy/image-analyst/stretch.htm | syntax, defaults (None) | 2026-11-07 | P |
| Pro 3.5 Raster and imagery default options | https://pro.arcgis.com/en/pro-app/3.5/help/data/imagery/set-raster-and-imagery-default-options.htm | whole page | 2026-11-07 | P |
| Colby tutorial (M. Gimond) | https://sites.google.com/colby.edu/mgimond-arcgis-pro/symbolizing-raster-features | default stretch | 2026-11-07 | S |
| Bard tutorial (Ayala), Pro 3.3 | https://sites.google.com/bard.edu/arcgis-pro-tutorials-ayala/symbolizing-raster-features | default stretch | 2026-11-07 | S |
| Meisterlin, "mapping 101", Pro 2.9.1 | https://tan-caterpillar-s99x.squarespace.com/skills/arcgispro-stretchedrasters | percent clip default | 2026-11-07 | S |
| Pro 3.5 Definition queries | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/layer-properties/definition-query.htm | whole page | 2026-11-07 | P |
| Pro 3.5 Introduction to query expressions | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/navigation/write-a-query-in-the-query-builder.htm | whole page | 2026-11-07 | P |
| Pro 3.5 Construct and modify queries | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/navigation/construct-and-modify-queries.htm | whole page | 2026-11-07 | P |
| Pro 3.0 GP Query builder | https://pro.arcgis.com/en/pro-app/3.0/help/analysis/geoprocessing/basics/query-builder.htm | clause mode | 2026-11-07 | P |
| Pro SDK SQLPredicate | https://pro.arcgis.com/en/pro-app/3.4/sdk/api-reference/topic14513.html | members | 2026-11-07 | P |
| Pro 3.5 Labeling basics | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/text/labeling-basics.htm | whole page | 2026-11-07 | P |
| Pro 3.5 Use label classes | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/text/label-classes.htm | whole page | 2026-11-07 | P |
| Pro 3.5 Specify text for labels | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/text/specify-text-for-labels.htm | intro, note on the default field | 2026-11-07 | P |
| Pro 3.5 Standard Label Engine | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/text/label-with-the-standard-label-engine.htm | position | 2026-11-07 | P |
| Pro 3.5 Repair broken data | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/layer-properties/repair-broken-data-links.htm | indicator, filter | 2026-11-07 | P |
| Pro 3.5 Work with group layers | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/layer-properties/work-with-group-layers.htm | whole page | 2026-11-07 | P |
| Pro 3.5 Symbolize feature layers | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/layer-properties/symbolize-feature-layers.htm | types, legend patch | 2026-11-07 | P |
| arcpy LayerElevation | https://doc.esri.com/en/arcgis-pro/latest/arcpy/mapping/layerelevation-class.html | discussion, properties | 2026-11-07 | P |
| Esri 10.1 GIS is based on layers | https://resources.arcgis.com/en/help/main/10.1/00v2/00v200000003000000.htm | whole page | 2026-11-07 | P |
| QGIS manual general_tools.rst | https://raw.githubusercontent.com/qgis/QGIS-Documentation/master/docs/user_manual/introduction/general_tools.rst | Layers panel, Layer Order | 2026-11-07 | P |
| QGIS manual vector_properties.rst | https://raw.githubusercontent.com/qgis/QGIS-Documentation/master/docs/user_manual/working_with_vector/vector_properties.rst | Query Builder, Categorized, Graduated, Labels | 2026-11-07 | P |
| QGIS manual raster_properties.rst | https://raw.githubusercontent.com/qgis/QGIS-Documentation/master/docs/user_manual/working_with_raster/raster_properties.rst | render types, Min/Max, color ramp shader, legend | 2026-11-07 | P |
| QGIS manual qgis_configuration.rst | https://raw.githubusercontent.com/qgis/QGIS-Documentation/master/docs/user_manual/introduction/qgis_configuration.rst | contrast enhancement options | 2026-11-07 | P |
| QGIS source graduated widget (.ui, .cpp) | https://raw.githubusercontent.com/qgis/QGIS/master/src/ui/qgsgraduatedsymbolrendererwidget.ui ; .../src/gui/symbology/qgsgraduatedsymbolrendererwidget.cpp | class spin box; mode list; Jenks warning | 2026-11-07 | P (read as text) |
| QGIS source min/max origin | https://raw.githubusercontent.com/qgis/QGIS/master/src/core/raster/qgsrasterminmaxorigin.h | constants | 2026-11-07 | P (read as text) |
| PSU GEOG 160, map overlay | https://www.e-education.psu.edu/geog160/node/1975 | McHarg quotation | 2026-11-07 | S |
| Corbett 2001, CSISS Classics | https://escholarship.org/uc/item/5x78n2gn | method paragraph | 2026-11-08 | S |
| Penn Architectural Archives, McHarg finding aid | https://www.design.upenn.edu/sites/default/files/McHarg109.pdf | biographical note | 2026-11-08 | S |
| Spirn (via uop.edu.jo PDF) | https://uop.edu.jo/PDF File/uop uop env4-19434_Part6.pdf | not loaded (503) | 2026-11-08 | U |
| Qgis2threejs 3.3 Exporter | https://minorua.github.io/Qgis2threejs/docs/3.3/Exporter.html | Z coordinate, Scene menu | 2026-11-07 | P |
| kepler.gl user guides | https://raw.githubusercontent.com/keplergl/kepler.gl/master/docs/user-guides/ (README, e-filters, hide-edit-delete, blend-and-rearrange, l-color-attributes) | those pages | 2026-11-08 | P |
| kepler.gl default-settings.ts | https://raw.githubusercontent.com/keplergl/kepler.gl/master/src/constants/src/default-settings.ts | SCALE_TYPES | 2026-11-08 | P (read as text) |
| Felt, Style vector layers | https://help.felt.com/styling/style-vector-layers.md | types, methods | 2026-11-08 | P |
| Giraffe, Custom layer styling | https://intercom.help/giraffe-knowledgebase/en/articles/11815089-custom-layer-styling | whole article | 2026-11-08 | P |
| Esri, ArcGIS for Autodesk Forma UI | https://doc.esri.com/en/arcgis-autodesk-forma/latest/workflows/arcgis-for-autodesk-forma-user-interface.html | Layers tab | 2026-11-08 | P |
| Brewer and Pickle 2002 (abstract) | https://pure.psu.edu/en/publications/evaluation-of-methods-for-classifying-epidemiological-data-on-cho/ | abstract | 2026-11-08 | P (abstract only) |

## 7. What stayed U, and why

- ArcGIS Pro's GUI defaults for graduated colours (Jenks, 5): the help does not state them, so they rest on the
  SDK (P) and are confirmed for the GUI only by blogs (U).
- Percent clip 0.5/0.5 is S (one tutorial). **Std-dev n = 2.5 was not found** in any source; do not use it.
- Pro's designer operator labels ("includes the value(s)", "contains the text", "begins with", "ends with",
  "is between"): the help gives only two examples, and the WWU guide returned 503. The SDK predicate list is P.
- Mapbox Studio's layer panel and data-driven controls: the manual pages moved (404), so only the blog and
  search summaries were seen.
- Spirn's "layer cake / litany" and the fixed order of the factors: the PDF did not load.
- How layer-cake diagrams are drawn (gaps, labels, base map position, oblique view): the images could not be
  inspected. Treat these as design choices for the owner, not as documented practice.
- archiMap and UrbanEyes: no documentation was found under those names. Ask the owner for their addresses.
- Esri's support article saying "Show all other values" is on by default was seen only as a search summary.
- Design with Nature itself was not read; the quotation comes through PSU GEOG 160 and Corbett.
