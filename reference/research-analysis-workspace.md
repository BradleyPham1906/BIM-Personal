# Research: the analysis workspace (V171b)

The owner, 2026-10-25, with a 32-second video of MassLabs' archiMap and a picture of Autodesk Forma's
microclimate analysis: "i think we can improve this better. please see the videos of other app doing site
analysis and simulation ... their layout looks clean and professional thats what i want. ours current right
now is a mess when doing simulation and site analysis".

Researched to `reference/research-protocol.md`. The products' own screens were read as pictures; their
words are our own here, and none of their frames or pictures are kept in the repository (it is public).

## What was read

| Source | What was read | Date | Level |
|---|---|---|---|
| archiMap (MassLabs), the owner's video, 1280 x 720, 31.8 s | A frame every 2 s, and two at full size: the screen while a site's diagrams are styled | 2026-10-25 | P (the product's screen) |
| `masslabs-archi.com` | The home page: four tools under one account; archiMap's limits by plan (area, uses a month, a site report on Pro and Max); exports PNG, SVG, DXF, PDF and 3DM, SKP, RVT, STL. Nothing on the screen's layout. | 2026-10-25 | P |
| Autodesk Forma, the owner's picture of its microclimate analysis | The whole screen | 2026-10-25 | P (the product's screen) |
| Autodesk, "Start your pre-design site analysis with Forma Site Design's sun hours analysis", `blogs.autodesk.com/forma/?p=743` | Read through the fetch tool's digest: Sun hours is opened from Analyze in the right panel; the area and the dates are set at the panel's top; an inspect tool at the 3D scene's top right gives a point's exact value | 2026-10-25 | S (a digest) |
| Autodesk, `blogs.autodesk.com/forma/?p=1701` | Read through the digest: "Open analysis" takes Run's place once there are results; the right panel's Highlights and Area breakdown; dates toggled; a time-interval slider; the legend filters the results to a range; a camera angle saved; an image exported with or without the date and the ranges | 2026-10-25 | S (a digest) |
| Autodesk Learn's Forma tutorials (microclimate, compare analyses) | Refused (403) from here | 2026-10-25 | - |
| ArcGIS Pro's Contents and geoprocessing panes | As `reference/research-arcgis-site-analysis.md` (1) read them for V157: one stack of layers, a legend patch under each, a tool's pane of parameters, Run, messages and History | 2026-10-16 | P, as recorded there |
| The app: Analyze (`bimAnalyzeHtml`, `bimAnzCards`, `bimDgCards`), the site run (`bimAnalyzeSite`), the legend (`bimDgLegendLayout`), the labels (`drawDiagrams`), the colour lens (`bimLensCol`, read by the GPU batches every frame), the basemap shaders (`map-tiles.js`, `webgpu.js`), the paint (`terrain-3d.js`), Properties (`refreshProps`), the shell and its tiers | Read as text | 2026-10-25 | P |
| The app as it is, screenshots of the fixture's neighbourhood analysed and its traffic simulated, at 1440 x 900 and 390 x 844, dark and light | Taken here (kept out of the repository) | 2026-10-25 | P |

Nothing at level U reached the code. Forma's own help pages were not found; what the digests say agrees with
the owner's picture.

## What the two products do

**archiMap.** A light screen: a top bar of menus (Style, Source, Plan, Settings, Help, Review) with 2D and 3D
and Export at its right. On the left, the area (a circle or a rectangle, its diameter) and then one tree of
layers by theme (base, text, boundary, environment, building information, facilities, building, traffic,
cadastre, contour, water, green), each with a tick box and a small swatch; picking a swatch opens a small
style card (pattern, fill, line, shadow) beside the tree. The map takes the middle: only the site's circle in
colour, everything outside it faded. A small key sits in the map's bottom right corner. On the right, three
tabs (Diagram, Ratios, Environment) over a single-choice list of diagram types (basic, building, building use,
height, floors, floor area, green, traffic, contour, facility, wind, sun path, shadow, view, sunlight, solar
radiation, thermal comfort, sky view, traffic noise, congestion, walkability, ground heat, vegetation,
population, slope), the chosen one in a black bar. One diagram at a time; the layers under it are ticked.

**Forma.** A light screen: a slim bar over the scene with the analysis's name in capitals and a close cross.
On the left, the proposals and, under the chosen one, the history of analyses by date, each a row with its
name, time and an icon to compare. The scene in the middle shows only that analysis, a heat map on the ground
around white massing. One colour bar at the bottom centre is the legend. On the right, the analysis's panel:
its settings at the top (the month, the hour on a slider), then its charts (air temperature as a histogram,
the wind as a rose, the wind speed's distribution), the weather data with its source, and the area metrics.

**What they share, and what the app lacks today:**
1. The analysis is a place you go into and leave (a title and a cross), not a list beside the drawing tools.
2. One analysis drawn at a time, with others added on purpose. The app draws 14 of its 23 at once after a run
   (202 elements in the fixture), and their words cover each other in 3D.
3. One legend, for what is drawn, small, at the edge. The app's covers a quarter of the view with fourteen keys.
4. The left lists, the right explains: settings, charts, numbers and the source for the one analysis.
   The app's left panel holds the run's steps, the ten categories, the findings and the cards, and its right
   panel shows the project's identity data and usages while analysing.
5. The scene is quiet: the ground and the context in greys, colour only for the data. The app's view stays
   dark with the satellite map under the analyses, in light mode as in dark.
6. The drawing tools are not on screen while analysing; the app's dock stays, and its messages cover it.
7. On a phone the scene stays in view. The app's Analyze covers the whole screen.

## The owner's decisions (2026-10-25)

1. **The look follows the app's mode** ("depend on our mode. we have light and dark mode"): in light mode the
   workspace is light, panels and view, as archiMap and Forma are; in dark mode it is dark. The view follows
   too: the ground, the context and the map go quiet in the mode's greys, and only the data keeps its colour.
2. **One analysis at a time**, others ticked to be drawn under it. After Analyze site the view shows the site
   and its context, and the list offers the analyses.

## The design

- **The workspace.** Entered when Analyze site finishes, by Open on an analysis's row in Analyze, by the
  command `SITEANALYSIS`, and by `TRAFFIC`; left by the cross in its bar or by the list's back button. What it
  showed stays shown when it is left. Its focus and ticks are the project's, kept with it.
- **Its bar**, over the view's top left: SITE ANALYSIS, the analysis in focus, and the cross.
- **The left: the analyses**, in their groups (Site; Sun and wind; Views and noise; Land and water;
  Movement; Land), each a row with a tick box, its colour and its name. A row's name puts it in focus: drawn
  alone, the ticked ones under it. The focus and the ticks are the layers' visibility, so Layers agrees and a
  sheet shows the same; a change is one undo step.
- **The right: the analysis's panel**, where Properties is while nothing is selected: what it shows, its
  settings (the traffic's peak hour, quality and speed, with Play), its chart where the app has one (the wind
  rose, the sun's paths), its key in full, what the run said, the source and its date, the standards it used,
  and Run again, Select and Reset. With nothing in focus: the site, the last run and its sources.
- **The view**: the mode's ground colour; the map greyed and faded; the context's buildings, roads, water and
  green in the mode's quiet tones; the legend in the mode's colours at the view's bottom left; the drawing
  dock hidden; messages at the top, under the bar.
- **A phone**: the panel drawer closes so the view shows; the analyses are a row of chips under the bar, and
  the analysis's panel is Properties' sheet.

## Still open

- archiMap's style card (pattern, fill, line, shadow per layer) and its Ratios tab; Forma's compare and its
  history of runs by date. V172's tool pane (History) and V173's Contents pane are where they belong.
- A legend that filters the view to a range (Forma's), and an inspect tool for a point's value.

## As built (2026-10-25)

The workspace is `src/js/engine/site-analysis/analysis-workspace.js` with its stylesheet
`src/css/site-analysis/workspace.css` and the suite's hooks `testing/hooks-workspace.js`; patches `Phase/patch_v171b_a.py`
to `_e.py` reach into the files it touches. As designed, with these found while building:

- **The context's roads, rail and water are sketches,** drawn in their layer's colour, not through the colour lens the
  solids take; they take the mode's tone in `drawSketches` (patch b).
- **The context's terrain has renderers of its own** (WebGL, WebGPU and the canvas), each reading its colour; the
  first light view kept a brown ground (patch c). It also drapes the map with shaders that neither grey nor fade it,
  so in the workspace it is drawn plain and the map lies around it (patch e).
- **The streets' analyses and the cars chose light or dark colours by the map's style**, so dark cars sat on the dark
  ground; in the workspace they follow the mode (patch d).
- **An undo did not give the focus back:** the step was taken after the focus changed. It is taken first now, and the
  bar and Properties' title follow every refresh of Properties, an undo's included.
- **A second Analyze site** keeps the focus and the ticks; only the first starts on the overview. The list has
  **Analyze again** beside the site's name.
- **A sub-phase keeps its phase's number:** the app says V171, as V166b said V166, since every suite reads the number.

The older suites that read each analysis as a run drew it (V164, V165, V166, V167, V168, V170, V171) leave the
workspace when a run ends and show each analysis as a run did before (`__a3dAwClassic`); V171's also leaves it before
reading Traffic's row in Analyze and before Analyze site again.
