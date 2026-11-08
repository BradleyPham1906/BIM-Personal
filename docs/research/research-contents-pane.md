# V173 Site analysis SA6: the Contents pane (research, 2026-11-07 to 11-08)

Under `docs/research/research-protocol.md` ("Research as a scientist does it"). Levels: **P** read in the primary
source (the standard, the vendor's own document, the code read as text, the app's code, or measured here), **S** a
dependable secondary source with the gap said, **U** a search summary or an unchecked single copy, kept out of the code.
This note is written from five working notes in `docs/research/research-contents-pane/`, each with its own search log,
findings, levels and references:

| Working note | Side | Written by |
|---|---|---|
| `practice.md` | ArcGIS Pro's Contents pane, symbology, labels and definition queries; QGIS; McHarg; prior art | research agent 1 |
| `classification.md` | The classification methods, stretches and colour ramps; open implementations; experiments | research agent 2 |
| `filter-and-labels.md` | The filter language (CQL2, ArcGIS SQL, QGIS, MapLibre), label placement, security; experiments | research agent 3 |
| `app-code-audit.md` | What the app already has, by file and line | the main session |
| `independent-check.md` | The second reader's re-check of every fact the code uses | research agent 4 (part 3 says where it stands) |

## 1. Abstract

The question: how should the app give its site-analysis layers a Contents pane in the way ArcGIS Pro does (the stack
listed by drawing order, by source and by selection, a legend patch under each layer, symbology by category,
graduated and stretched, labels and a definition query, and the stack exploded in 3D as McHarg's layer cake),
within an ES5, zero-dependency app that keeps four different kinds of layer in four stores? The answer: the pane is
the rail's Layers tab with a "List by" switch, over the stores that exist, not a new store. Drawing order is
reorderable within each kind and shown as fixed groups across kinds, since the paint function fixes the order of the
kinds. Symbology uses an engine module already built in this phase (`src/js/engine/map/classify.js`): exact
Fisher-Jenks, quantile type 7, equal interval, standard deviation, R's pretty breaks, log interval and manual breaks,
with the goodness of variance fit on each, and four stretches. It was checked against mapclassify's published
examples and a brute-force optimum. The filter is a small subset of OGC CQL2's text form, kept as text in the project,
read by the app's own parser, never by `eval`, with a clause builder for touch screens. Labels come from a field,
placed at the pole of inaccessibility (polylabel's method), dropped greedily where they collide. The layer cake lifts
each analysis and data layer to a height of its own in an oblique view, over the map. Fourteen decisions for the owner
close the note (part 11).

## 2. The question and the hypotheses

**The question.** What must the pane list and do, how should each symbology method and the filter be defined so the
app agrees with the professional tools, and where in the app's code does each part belong? A good answer decides the
pane's place, the drawing-order model, each method's definition and default, the filter grammar and its semantics,
the label method, and the layer cake's scope.

| # | Hypothesis (falsifiable) | Outcome | Evidence | Level |
|---|---|---|---|---|
| H1 | ArcGIS Pro's Contents pane has drawing order, source and selection views, each layer with its legend patch | Held: six tabs (Drawing Order, Data Source, Selection, Editing, Snapping, Labeling), the same in the 3.5 and 3.7 help | practice 2.1 | P |
| H2 | ArcGIS and QGIS both default graduated colours to natural breaks with 5 classes | Failed in part: both use 5 classes; ArcGIS's SDK defaults to Natural Breaks, QGIS's list puts Equal Count (Quantile) first | practice 3 | P (method in the GUI: not stated) |
| H3 | The exact Jenks optimum can be computed in an ES5 browser for 100,000 values in under half a second | Held: 84 to 197 ms with plain arrays, Node 22 (part 6) | experiments | P (measured) |
| H4 | Open Jenks implementations agree with the exact optimum | Failed: geostats' traceback starts one value short (GVF 0.662 against 0.998 on calemp); mapclassify's `NaturalBreaks` is k-means, only `FisherJenks` exact; QGIS samples above 3,000 values | classification | P (code read) |
| H5 | A standard filter language exists that is small enough to parse in ES5 and close to ArcGIS's definition query | Held: CQL2 (OGC 21-065r2, 1.0.0, 2024), Basic plus advanced comparison, about 14 KB of ES5 in the experiment, 73 of 73 edge cases | filter 3.1, 7 | P |
| H6 | LIKE can be matched safely by turning the pattern into a regular expression | Failed: `%a%a%a%a%a%a%a%b` took 75 s on an 80-character value as a RegExp; a matcher of our own took 3 ms on 20,000 characters | filter 7 | P (measured) |
| H7 | Some GIS offers an "explode the stack" command for a layer cake | Failed: none found; ArcGIS Pro's per-layer offsets and Qgis2threejs's per-layer heights let one build it by hand | practice 2.5 | P |
| H8 | The app can draw a layer cake with its existing 3D projection, without a new renderer | Held for analyses and data layers (one choke point each, `bimDgW` and `drawDataLayers`'s height); failed for result layers, which draw only in plan | audit 6 | P |
| H9 | The app's current colour lens fails when every value is equal | Failed (the agent's first claim, corrected): `colour-lens.js:95` returns before the division | classification, audit | P |

## 3. Method

- **Search logs:** practice (32 entries), classification and filter-and-labels each keep their own, with every
  query, where, what came back and what was kept.
- **Sources by kind:** Esri's ArcGIS Pro 3.5 and 3.7 help and Pro SDK; QGIS's user manual and source (qgis/QGIS,
  read as text); OGC 21-065r2 itself; Esri's SQL reference; the MapLibre style specification; mapclassify,
  simple-statistics, geostats, QGIS, pygeofilter, cql2-rs, jsep and polylabel read as text, licence first; R's
  `pretty.c`; ColorBrewer's and d3's scheme data; Brewer and Pickle (2002); McHarg (1969) through Penn's archive and
  quotation (S); kepler.gl and Felt documents. Full lists in each working note's references.
- **Experiments:** `docs/research/experiments/v173-classify/` (the methods written from their definitions, timed and
  checked against mapclassify's examples; `time-engine.mjs` times the engine's own module) and
  `docs/research/experiments/v173-filter/` (a CQL2 subset parser, its edge cases, the LIKE timing). Our own code;
  no downloaded code was run.
- **Independent check (2026-11-08):** a fourth agent re-fetched every source and re-read it as text, and checked the
  calemp numbers with its own Python, apart from the notes' code (`independent-check.md`). Of 55 facts: 51 confirmed,
  2 not confirmed, 2 not checkable (Corbett 2001 and Penn's finding aid answered 403; no code depends on them). The
  percent clip default and McHarg's quotation are confirmed but stay S. It also traced QGIS's default graduated mode
  further: a new renderer starts on "Custom", outside the method list, so the list shows its first entry, Equal
  Count (Quantile) (code read, not run). The two not confirmed are in part 10.

## 4. Findings, by topic

### 4.1 The pane (practice 2.1, 2.4; audit 1, 7)

- ArcGIS Pro: Drawing Order (drag, a visibility box, a greyed box when out of scale range; a reorder is not an undo
  step), Data Source (a red exclamation mark on a broken source, which opens Change data source), Selection (the
  selected count beside the layer; rasters have no box), and Editing, Snapping, Labeling. One Contents filter at a
  time (visible layers, layers with a definition query, broken links). Group layers are check box or radio. P, high.
- QGIS keeps a Layer Order panel apart from the Layers panel; each class under a layer has its own box. P, high.
- The app's four stores (audit 1): model layers, site-analysis layers (model layers holding `diag` elements), result
  layers and data layers. The rail's Layers tab already lists the first two as a tree and the other two as the
  sections Analysis and Data, with a swatch, an eye and opacity. P, high.
- **Found by the audit:** the result layers' list puts the top of the list on top; the data layers' list puts the
  top row underneath (drawn in list order, listed in the same order). P, high.

### 4.2 Symbology (practice 2.2, 2.4; classification)

- ArcGIS Pro: unique values on up to three fields, "All other values" on, no values added until Add all values;
  graduated colours with seven methods, normalisation by a field, the percentage of the total or a log; about seven
  colours readable; classification reads a sample of 10,000 records; standard deviation in 1, 1/2, 1/3 or 1/4. P.
  The stretch default (Percent Clip, 0.5 and 0.5 per cent) is S, from tutorials; no source gives the standard
  deviation stretch's n. QGIS: 5 classes; cumulative count cut 2 to 98 per cent; mean plus or minus 2.0 standard
  deviations; a prompt before Jenks on more than 50,000 features. P (source).
- Natural breaks: Fisher's (1958) exact optimum, filled by divide and conquer over the monotone best start
  (Ckmeans.1d.dp's method, Wang and Song 2011). Same breaks as the plain dynamic programme wherever both ran. P.
- Quantile: type 7 (linear at (n - 1) p), R's default and what QGIS, mapclassify and simple-statistics use; geostats
  uses nearest rank and differs. Repeated breaks are merged. P.
- Standard deviation: two conventions exist (a class centred on the mean, or the mean on a break), and the standard
  deviation of the sample (n - 1) or of the population (n). Implementations disagree. P that they disagree; which
  ArcGIS uses is U.
- Geometric interval (Esri) cannot be rebuilt from its documentation; equal steps on a log scale, named so, replace
  it. P (that the documentation does not define it).
- Colour: the app's `BIM_LENS_RAMP` is ColorBrewer's YlOrRd 6 exactly; ColorBrewer is Apache-2.0. P.
- Counter-evidence: Esri warns that quantile maps mislead and Jenks breaks are specific to the data; Brewer and Pickle
  (2002) found quantile the most accurate for reading choropleth maps and natural breaks under 70 per cent of it, and
  one legend across maps added about 28 per cent in comparison accuracy. S (the paper through its abstract and
  citations; see practice 5).

### 4.3 Labels and filters (practice 2.3; filter-and-labels)

- ArcGIS: a label field defaulting to the first text field whose name contains "Name"; label classes each with a
  query and a scale range. At most one active definition query per layer; it limits what is drawn, selected,
  labelled and processed. P.
- CQL2 (OGC 21-065r2, 1.0.0, approved 2024-05-23): Basic CQL2 (comparison, AND, OR, NOT, IS NULL), Advanced
  Comparison (LIKE, BETWEEN, IN), Case-insensitive Comparison (CASEI); NOT binds before AND before OR; strings in
  single quotes with `''` inside; a comparison with a null is unknown and a feature is kept only when the whole
  filter is true. P.
- ArcGIS's file SQL shares that core (`<>` and NOT IN leave nulls out). QGIS: LIKE case-sensitive, ILIKE not.
  MapLibre's JSON filters are strictly typed (`"10"` is not `10`) and have no LIKE. P.
- No open evaluator fits ES5 without dependencies; pygeofilter's builds Python source and runs it, the pattern to
  avoid. P.
- polylabel 2.1.0 (ISC): the inside point furthest from every edge, by a grid of cells and a priority queue, about 80
  lines. QGIS's "never overlap" drops colliding labels by priority; a greedy box test does the same, as the app's
  `bimDgPlaceLabels` already does for the diagrams. P.
- The app's `bimGeoCleanProps` writes keys onto a plain object, so a feature property named `__proto__` would not be
  an own property: a filter must read properties with own-property checks. P (code read).

### 4.4 The layer cake (practice 2.5; audit 6)

- McHarg's rule (Design with Nature, 1969, p. 34 as quoted): each factor mapped darker for greater cost, the maps made
  transparent and stacked, the lightest areas the best. Penn's archive calls it the layer cake method. S.
- No GIS has an explode command; what the drawing usually shows (gaps, names beside, the base map at the bottom, an
  oblique view) is U, from images only.
- In the app, a per-layer height is one change in `bimDgW` for analyses and one in `drawDataLayers` (and
  `bimDataPick`) for data layers; result layers would need a 3D path of their own. P.

## 5. The alternatives compared

Criteria, stated first: works with the four stores without a second state store (the OpenBridge intake's rule);
matches ArcGIS where the owner's reference is ArcGIS; ES5 with no dependency; usable on a phone; the size of the change.

**Where the pane lives**

| Option | Stores | ArcGIS-like | Phone | Change |
|---|---|---|---|---|
| A. The Layers tab gains "List by: Drawing order, Source, Selection" (recommended) | the existing ones | yes (tabs as a switch) | the rail's drawer, as today | moderate |
| B. A new Contents tab beside Layers | the existing ones | yes | another tab in a crowded rail | moderate, and two lists of one thing |
| C. Inside the Analyze workspace's left list | analyses only | partly | as V171c | small, but misses model and data layers |

**Drawing order across kinds**

| Option | ArcGIS-like | Change | Risk |
|---|---|---|---|
| A. Reorder within each kind; the kinds as fixed groups in paint's order (recommended) | within a group | small | none to paint |
| B. One free order for every layer | fully | rewrite paint into one ordered list of drawers | every drawer, every suite that counts draws |

**The filter's stored form** (filter-and-labels 8)

| Option | Safe without eval | Typable | Standard | ES5 size | Phone |
|---|---|---|---|---|---|
| A. CQL2 text subset, with a clause builder that writes it (recommended) | yes | yes | OGC | about 14 KB | the builder |
| B. An ArcGIS-like SQL WHERE subset | yes | yes | a dialect | about the same | needs a builder too |
| C. MapLibre JSON | yes | no | de facto | about 4 KB | no |
| D. Structured clauses only | yes | no | none | about 3 KB | best |

**Natural breaks** (classification)

| Option | Exact | 1e5 values | Code |
|---|---|---|---|
| A. Fisher-Jenks by divide and conquer, plain arrays (built) | yes | 84 to 197 ms | 40 lines |
| B. The plain dynamic programme | yes | 57 s | 25 lines |
| C. Sampling to 3,000 (QGIS) or 10,000 (ArcGIS) then exact | on the sample | fast | A plus a sample |

What would change the recommendations: an owner's wish for one free drawing order (B), or for typed filters only (D).

## 6. The experiments

- `v173-classify/run.js` (the agent's): calemp k=5 natural breaks [75.29, 192.05, 370.5, 722.85, 4111.45], counts
  [49, 3, 4, 1, 1], GVF 0.998435, matching mapclassify's test; quantile [1.464, 5.798, 13.278, 54.616]; equal interval
  [822.394, ...]; R's pretty; simple-statistics' cases; timings of the two forms (in `classification.md`).
- `v173-classify/time-engine.mjs` (the engine's module, plain arrays, Node v22.23.4, three runs each), in ms:

  | n | k = 5 | k = 9 |
  |---|---|---|
  | 1,000 | 9.2, 4.3, 5.7 | 9.4, 5.0, 3.2 |
  | 10,000 | 26.6, 9.9, 8.0 | 12.3, 13.4, 15.4 |
  | 30,000 | 42.3, 39.2, 21.6 | 38.4, 34.1, 38.3 |
  | 100,000 | 83.5, 99.9, 84.3 | 138.2, 196.7, 128.7 |
  | 300,000 (sampled to 100,000) | 186.6, 179.7, 216.4 | 224.6, 230.7, 234.6 |

  Raw output in `time-engine.txt`. Typed arrays (the agent's run) gave 108 and 127 ms at 100,000: no reason to change
  the ES5 contract for them.
- `v173-filter/run.js`: 73 of 73 edge cases after one fix (the LIKE escape); 10,000 features filtered in 16 to 18 ms;
  the RegExp LIKE timing of H6.
- Not measured here: a phone's speed (assumed 3 to 5 times slower than this machine; the classification would still
  be under a second at 100,000 values), Safari, Firefox.

## 7. Edges

- Fewer distinct values than classes: natural breaks lowers k and says so; quantile and equal interval may leave empty
  classes; one value gives one class for every method. (Unit tests.)
- Text and blanks among numbers: numbers and numeric strings are read, everything else dropped and counted out.
- Above 100,000 values natural breaks reads an even sample, the lowest and highest kept, the same every time.
- Standard deviation breaks outside the data range are dropped (the class centred on the mean can leave the lowest
  class narrower than a step). Log interval refuses zero or negative values.
- Filters: a null or missing field is unknown; `<>` and NOT IN do not keep nulls; `'10'` against `10`; a quote inside a
  string; a backslash in LIKE (the standard does not say whether it escapes the wildcard: open, D11); nesting and
  length capped (64, 4,000 characters).
- Layer order: an empty group; a data layer that failed to load (the Source view's mark).

## 8. What the app already has

`research-contents-pane/app-code-audit.md`, by file and line: the four stores and paint's order
(`map/terrain-3d.js` 391 to 495), the lens and data-layer scales (`map/colour-lens.js`), the Layers panel's sections
(`layers/analysis-data-rows.js`), data layer fields set through `bimDataSet` (`map/find-open-data.js:272`), the
diagrams' label placement (`site-analysis/model-layers.js:370`) and the layer cake's choke points.

**Built in this phase so far (2026-11-08):** `src/js/engine/map/classify.js`, `__acad3dV173`: `bimClsBreaks`,
`bimClsStretch`, `bimClsStretchAt`, with `window.__a3dClsBreaks` and `__a3dClsStretch` for the suites, and
`tests/unit/classify.test.mjs` (9 tests: the calemp examples, simple-statistics' cases, a brute-force optimum on 30
random cases, the edges, sampling, the stretches). Nothing draws with it yet.

## 9. Risks and threats to validity

- Esri's GUI defaults are from the SDK and tutorials; Esri's help moved to doc.esri.com and some pages answer 404.
- Fisher (1958) and Jenks (1977) were not read in the original; their method is P through implementations and
  Wang and Song's paper.
- Brewer and Pickle (2002) through its abstract and citations (S).
- One machine, one engine (Node 22) for timings; no phone measured.
- The independent check re-read every source, but by one more agent, with the same network.
- Agents wrote three of the five working notes; one claim of theirs (H9) was wrong and corrected by the main session.

## 10. What is still open (U)

- ArcGIS's standard deviation centring and the n of its standard deviation stretch; its on-screen operator names.
- How layer cake drawings are usually drawn (gaps, labels, viewing angle): images only.
- The CQL2 backslash in LIKE.
- **Back to U after the independent check:** (1) that CQL2's LIKE is case-sensitive: the standard never says so; it
  follows from what CASEI is for, so it is the app's choice, not CQL2's rule (D10 covers it). (2) `NOT IN ('a',
  NULL)` giving unknown "under CQL2": CQL2 Text has no NULL literal, so the list does not parse, and the standard does
  not define IN with a null item; the app's rule is a decision (D9 extended), not CQL2's.
- Mapbox Studio's, archiMap's, UrbanEyes' and Forma's layer lists: moved pages or nothing found; the owner may have
  their addresses.

## 11. The owner's decisions

Each with the recommendation first. Asked together on 2026-11-08. **The owner's answers (2026-11-07, this
session's date): all fourteen as recommended, option A each** (D1 the Layers tab with List by; D2 reorder within
each kind; D3 the top row on top; D4 natural breaks, 5 classes; D5 a class centred on the mean, the sample's
standard deviation; D6 percent clip 2 to 98; D7 plain arrays; D8 the CQL2 text subset with a clause builder; D9
numeric text compared as numbers; D10 aliases accepted, written back as CQL2; D11 a backslash escapes; D12 a field
or a template, polylabel, greedy collisions; D13 analyses and data layers in the cake; D14 V173a to V173d).

| # | Question | Options (recommended first) | Evidence |
|---|---|---|---|
| D1 | Where does the Contents pane live? | A. The Layers tab with List by: Drawing order, Source, Selection; B. a new tab; C. the Analyze workspace | 4.1, 5 |
| D2 | Drawing order across kinds | A. reorder within each kind, the kinds as fixed groups; B. one free order (paint rewritten) | audit 1, 5 |
| D3 | The data layers' list direction | A. the top row draws on top, as ArcGIS and the result layers (the list shown reversed, the stored order kept); B. leave it | 4.1 |
| D4 | The default graduated method and classes | A. Natural breaks, 5 classes (ArcGIS's SDK), the GVF shown; B. Quantile, 5 (QGIS; Brewer and Pickle); C. keep equal interval, 6 (today's lens) | 4.2 |
| D5 | Standard deviation: the convention | A. a class centred on the mean, sample standard deviation, the other offered; B. the mean on a break | 4.2, 7 |
| D6 | The stretch default for surfaces (sun hours, slope, elevation, cut and fill) | A. percent clip 2 to 98 per cent (QGIS, P); B. 0.5 and 0.5 (ArcGIS, S); C. min-max | 4.2 |
| D7 | Typed arrays | A. not needed: plain arrays are fast enough (part 6), the contract unchanged; B. allow them | 6 |
| D8 | The filter's stored form | A. CQL2 text subset, with a clause builder; B. SQL WHERE subset; C. MapLibre JSON; D. clauses only | 5 |
| D9 | Numbers stored as text | A. compared as numbers when both sides read as numbers, else as text; B. strict types | 4.3, 7 |
| D10 | Aliases on input (`!=`, ILIKE, UPPER and LOWER) | A. accepted and written back as CQL2 (`<>`, CASEI); B. CQL2 only | 4.3 |
| D11 | A backslash in a LIKE pattern | A. escapes the next character, so `\%` and `\_` match themselves; B. a plain character | 7 |
| D12 | Labels | A. one field or a template such as `{name} ({height} m)`, polylabel ported (ISC, credited), collisions dropped greedily; B. one field, at the centroid | 4.3 |
| D13 | The layer cake's scope | A. analyses and data layers lifted over the map, in an oblique view, names beside; result layers later; B. result layers too (a 3D path for their images) | 4.4 |
| D14 | Order of building | A. V173a symbology for data and analysis layers, V173b filter and labels, V173c the List by views, V173d the layer cake; B. all in one | the size of each part |

## 12. References

Each working note lists its own references with URLs, what was read, the date and the level: `practice.md` part 6,
`classification.md` (references), `filter-and-labels.md` part 12, and `independent-check.md` for what was re-read.
The app's code was read at commit f2b410c (`app-code-audit.md`).
