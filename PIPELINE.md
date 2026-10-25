# canvas_v10 — the pipeline

## OpenBridge UI enrichment (cross-cutting intake, 2026-10-22)

Research and task annotations were recorded in Notion before repository changes.
See `reference/research-openbridge.md` and `vendor/openbridge/README.md`: 17 curated
SVG icons, 124 scoped token values, exact Apache-2.0 snapshot, source copies,
checksums, offline workbench and intake tests. Production HTML and phase
completion remain unchanged. Open `wip/openbridge-ui-preview.html` from the repo tree.

This is supplemental UI work, not a numbered phase or a substitute for V169
3D assets. The research records the existing Notion/main-pipeline numbering
discrepancy for animation/traffic/Contents; no adjacent rows are renumbered,
rescheduled or marked complete by this intake. Further production integration
requires command mapping, full app regressions and owner review.


**Read this first in a new session.** One page. The detail lives in the docs listed at the bottom.

    canvas_v10.html   3538478 bytes
    sha256            c77eb5aa6d0bca806ff31b4a7b8bb68b8f1dd5b4846ecbd35968e186a3ba92ab
    markers           __acad3dV60 ... __acad3dV171, plus __acad3dV105b, __acad3dV113b, __acad3dV113c,
                      __acad3dV121b, __acad3dV166b, __acad3dV166c, __acad3dV166d
    tests             130 suites, 6537 checks, 0 failures (the 129 older suites' 6428 and V171's 109; with cjval
                      built, V139 and V140 run their three more)

    The user guide (V142): every phase updates docs/src/, its log entry and BIM_APP_VERSION, then
    runs tools/dump_catalog.py and tools/build_docs.py. The V142 suite and the Pages workflow
    refuse a guide that does not match the build.

    Run the regression in parallel: tests/run_all.py [build] [filter] [-jN], default -j6,
    about 4 minutes; give it the build's absolute path. tests/falsify_all.py
    <falsify_phaseNN.py> <suite.py> [-jN] proves every broken variant is caught: a minute for a
    small suite, seventeen for V123's (56 variants of a 108-check suite); a suite that hangs on a
    variant is reported TIMEOUT. Every current suite is in tests/, the folder the runner reads;
    commit new and amended suites there. Patch and falsify scripts, and each phase's pre-phase
    backup, are in Phase/. The suites need Playwright's Python package and Pillow (V116's reads
    pixels) -- in a fresh container, pip install playwright pillow before the baseline run. Pin
    Playwright to the version of the Chromium in /opt/pw-browsers (1.56 for chromium-1194, V166c;
    1.63.0 for chromium-1243, 2026-10-25),
    and build cjval (cargo install cjval --features build-binary): without it V139 and V140 skip
    three checks.

    The source is src/, by feature (2026-10-25, CLAUDE.md "The source"): the page, 11 CSS files and
    the engine's 172 files in feature folders. tools/build_app.py joins it into canvas_v10.html, the
    build above, byte for byte; --check fails when they differ. Pages serves the same app as
    separate files (tools/check_site.py proves they run alike).

Start every session by verifying that hash (tools/build_app.py --check) and taking a backup. Never
read or output canvas_v10.html whole and never edit it by hand: patch the files under src/ with
anchored Python scripts that assert exact match counts, then run tools/build_app.py.

---

## NOW - Buildings from LOD1 to LOD3 (V139 to V145), then the hub's history and branches, the envelope and MEP

The owner looked at Giraffe (giraffe.build), a map-first feasibility app, and chose four of its
ideas, ahead of the MEP runs, then asked for the map "just like how giraffe do". The research, with an
inventory of everything Giraffe does against this app, is in `reference/research-giraffe.md`.
In V135 the owner pointed at GeoLibre (an open-source GIS) and chose its portal search (V135), then
colour by attribute with legends (V136) and the map on 3D terrain (V137), ahead of the envelope.
What was and was not taken from it is in `reference/research-open-data-portals.md`.

After V138 the owner set the next track: "a progression from LOD1 to LOD2, and then ultimately LOD3
... imagery reconstruction based on the facade ... do it carefully". The research, the sources and the
reasons for the order are in `reference/research-lod-reconstruction.md`. In short: automatic where the
research is proven (LOD1.3, LOD2 from OSM roofs and from LiDAR, 3DBAG's method), guided by the owner
where it is not yet (LOD3 openings from rectified facade photos), each level verified as V138 verifies a
survey. The GPL tools (roofer, City3D, val3dity) are methods to follow, not code to copy.

V128 to V130 settled how commands are found (see Recently finished):
- **V128:** one command search over every command and tool.
- **V129:** a centred shortcuts panel, and real tooltips.
- **V130:** that panel holds every tool too. The dock is one row of the tools pinned for the
  discipline.

**Rules for new commands and keys:**
- A new command goes into the search (`CADCMDS` or the ribbon registry, with synonyms in
  `BIM_CMD_TERMS`).
- A new key goes in `A3D_KEYS`, with the command it runs (`cmd`).
- A new ribbon tool appears in the Tools and shortcuts panel by itself. Only add it to
  `A3D_DOCK_PIN_DEFAULTS` if it is one of a discipline's few most-used tools.
- Check any chrome change against the drawing space and the suites' fitted views:
  - V129's taller dock broke four suites' geometry.
  - V130's shorter one put a sketch's midpoint grip under the gizmo's X box in V110 (a grip wins
    a press, V97).

**Design rule (owner, V147): every redesign works on a phone, a tablet and a computer.** Each UI
phase's suite checks three sizes, measured in the browser:
- a phone, 390 x 844, touch;
- a tablet, 820 x 1180, touch (and 1180 x 820 where it differs);
- a computer, 1500 x 950, mouse.

On touch, targets are at least 36 px and nothing depends on hover. On a phone, panels are bottom
sheets; on a tablet, drawers; on a computer, docked and resizable. The breakpoints are the app's
three tiers: compact up to 720 px wide or 500 px high, medium up to 1024 px, desktop above.

**Design rule (owner, V125):** keep the interface clean and consistent, following Rhino's model
(see `reference/research-structural-ui.md`).
- Settings are Properties pages that follow the selection.
- An analysis is a display turned on and off by its command.
- A feature adds a window, rail tab or toolbar strip only when no existing one can hold it.

| # | Phase | Scope | Notes |
|---|---|---|---|
| 139 | LOD-A: LOD1.3, labelled LODs, CityJSON | **Done** (see Recently finished) | `reference/research-lod-reconstruction.md` (1, 4, 6). |
| 140 | LOD-B: LOD2 from OSM roofs | **Done** (see Recently finished) | `reference/research-lod-reconstruction.md` (7). |
| 141 | Panels and Analyze | **Done** (see Recently finished) | The owner's order: panels and Analyze, Simulation, terrain, then the LOD track again. |
| 142 | User guide and versions | **Done** (see Recently finished) | `docs/`, `tools/build_docs.py`, `tools/build_site.py`; the site keeps every older build at v/<version>/. |
| 143 | Simulation | **Done** (see Recently finished) | Next: weather years (EPW, NASA POWER) for expected yield; sun on facades; wind and energy later. |
| 144 | Terrain | **Done** (see Recently finished) | Breaklines, boundaries, own faces, slope/elevation/aspect bands, LandXML 1.2 in and out. |
| 145 | Grading | **Done** (see Recently finished) | Daylight slopes (fans, valleys), the proposed surface, exact TIN-to-TIN cut and fill, the cut and fill map, spot elevations, slope arrows. Next: sloped pads, retaining walls, sections along an alignment. |
| 146 | Hub H1: element history | **Done** (see Recently finished): commits, per-element diffs, restore, an element's history, saved with the project | The first piece of the owner's "GitHub for BIM" (`reference/research-bim-hub.md`). Every object already has a stable ID and the project is JSON. |
| 147 | The right panel, redesigned | **Done** (see Recently finished): a bottom sheet on a phone, a 340 px drawer on a tablet, 36 px touch targets; tokens for dark and light, sentence-case headers, one row grid, one input and button style, Show all, resizable and minimisable. Next: More for rarely used fields, type by type | The owner's note: "clean up more... aesthetic and minimal, easy to use". `reference/research-presentation-panels.md` (3). Every Properties suite is amended where the markup changes, never the behaviour. |
| 148 | Analyze, redesigned; results as layers | **Done** (see Recently finished): a list in four groups with a search; Add as layer for sun hours, rain, slope, elevation, aspect and cut and fill; Layers' Analysis and Data sections. Next: result layers on sheets, locking, blend modes with the boards | QGIS writes a processing run's outputs as layers into a named group. `reference/research-presentation-panels.md` (2). |
| 149 | The shell on phone and tablet | **Done** (see Recently finished): a tab bar and a drawer on a phone upright, the rail and a drawer on a tablet upright or a phone on its side, unchanged on a computer; safe areas. Next: a context menu on a long press when the drawing has one | The owner (V147): "consider the adaptation for phone, iPad/tablet, and computer". |
| 150 | A tool palette for a phone and a tablet | **Done** (see Recently finished): the essentials in a frosted capsule, dragged anywhere, docked upright at an edge, folded to one button; the dock gives way to it on a phone and an upright tablet | The owner: "make it clean like how Apple did it ... only the essential ones". |
| 151 | Hub H2: branches and merge | **Done** (see Recently finished): branches switched between and compared by their numbers; a three-way merge per element and per field, conflicts side by side, Keep or Take; a merge version with two parents. Next: a graph of the branches; solar and usages in Compare | Replaces "Design scenarios" (Giraffe's scenarios, Revit's Design Options). |
| 152 | Render R1: GPU-friendly batches | **Done** (see Recently finished): merged chunks, one object table on the GPU sending only the rows that change, the camera alone sending nothing; 5,000 elements in 1 draw call instead of 5,000, the same pixels; the per-object path kept as the fallback. Next: the table's upkeep only for objects that changed; culling; instances | The owner (V151): WebGPU for efficiency and scale. |
| 153 | Render R2: the WebGPU engine, WebGL kept | **Done** (see Recently finished): WebGPU where the browser has it, from V152's description; WGSL shaders, the table as a storage buffer, 4x multisampling, every draw in a render bundle replayed with only the camera sent; WebGL while it starts, without it, after a lost device or a failed frame, by choice (GRAPHICS), and for the map and terrain in 3D | WebGL stays for devices without WebGPU (iOS before 26, some Android phones and browsers). |
| 154 | Render R3: the map and terrain in WebGPU | **Done** (see Recently finished): the basemap and the draped terrain drawn with WebGPU (tile textures with mipmaps made on the GPU, given back with their tiles); outlines pulled toward the eye in both engines, ending their depth tie with the face | V153 handed those frames to WebGL. |
| 155 | Render R4: culling and BENCHMARK | **Done** (see Recently finished): chunks by 64 m cells, a chunk out of view not drawn in either engine; WebGPU bundles per chunk and pass, kept; BENCHMARK times 5,000 and 20,000 elements with both engines on the owner's own devices | The owner's "easier to scale later". |
| 156 | Render R5: the frame's upkeep and picking | **Done** (see Recently finished): the owner's BENCHMARK read in (5,000: WebGPU 3.1 ms, WebGL 4.1; 20,000: 9.3 and 10.5, all well within 60 fps); the frame's upkeep cut down (no search for removed objects unless the count says one is gone; a type's colour once a frame); a click on a model over 20,000 faces picked by a WebGL id pass, even while WebGPU draws (here 56 ms against 198) | The next cut: upkeep only for what changed, once every edit path marks what it changed. |
| 157 | Site context C2: the whole surroundings | **Done** (see Recently finished): from the same free Overpass API, four new kinds (railways, airports, power, land use) and every line kind with a 3D surface: roads as strips of their width (the width tag, lanes at 3.3 m, else by class), coloured by use (car road, pedestrian zone, footway, cycleway, path); bridges as decks 6 m up a layer, on piers every 30 m; tunnels as their line only; rail 3.2 m, tram 2.6 m, platforms 1 m high; runways 45 m, taxiways 18 m, aprons and helipads paved, the aerodrome its boundary; trees as trunk and crown at their height, tree rows a tree about every 8 m; pylons and the line hung 20 m up; land use as a ground tint; all following the terrain. Not done yet: fetching a large area in tiles; woods filled with trees; tunnels dashed in plan; man_made=bridge outlines, stations and terminals; OpenRailwayMap; the US NBI, NTAD and FAA layers as V134 presets | `reference/research-site-context.md`; the owner's notes on free infrastructure sources (Overpass, OpenRailwayMap, NTAD). |
| 158 | Site analysis SA1: the workspace and the standard | **Done** (see Recently finished): a Site tab on the rail; the stages as buttons; Define (boundary, project type, questions); the ten categories in their fixed order, each with its findings, a desk checklist and a site checklist; findings with class, severity, confidence, source, date, note, photograph and a numbered pin on the plan, red flags first; Fill from the model (location, built context, property, data layers, terrain relief and slope, water, day lengths, trees, streets by use, rail, airport, power, land use), refilled in place keeping what the owner said. Analysis and Data made group rows in the Layers tree, as Context is. Not yet: pins on sheets and opening a finding from its pin; findings drawn as diagrams | `reference/research-site-analysis-process.md`. The owner: "i want to standardize the whole process". |
| 159 | Site analysis SA2: climate and risk | **Done** (see Recently finished): research on how professionals present climate and risk (`reference/research-climate-risk-presentation.md`); Site analysis moved inside Analyze (the owner: "they should be together"); CLIMATEGET from ERA5, CAMS and USGS (free, no key); the Climate and risk board: header, nine indicators with states, nine figures (temperature with rain, wind roses, hourly heat map, sun path, degree days, solar, psychrometric comfort, earthquakes, PM2.5) each titled with its finding, sourced and tabled; hover, print A3, phone. Not yet: wind and sun on the plan, ventilation potential and UTCI, EPW input, the flood summary (SA3) | `reference/research-arcgis-site-analysis.md` (2, 3); `reference/research-climate-risk-presentation.md`. |
| 160 | Site analysis SA3: regulation | **Done** (see Recently finished): the zoning record (district, uses, FAR, height, storeys, coverage, parking, the source), by hand or from council layers under the lot (the district, and the FAR and height where the layer has them: MapPLUTO, an FSR and building-height layer, feet to metres); a rule for each kind of side, as Giraffe's envelope tool has (a setback at the ground, steps, an angular plane; the street wall and stepback and the sky exposure plane at the front); any side's role by hand (a corner lot's two fronts); the envelope in 3D, exact, of whole flat faces, on its own layer, rebuilt with each change; the yield (plates by storey, capacity, FAR, what governs, net, units, parking); the design checked (GFA, height, coverage, elements outside); the Zoning and yield board (indicators, the zoning analysis table, two sections at true scale after ZD1, the rules by side, the plan, the plates, the yield). Not yet: massing generated inside the envelope and costs (the Generators and Costs rows below); overlays and bonuses; parking and loading layout; the flood summary | `reference/research-zoning-envelope-yield.md`, with what was taken from Giraffe and what was not. |
| 161 | Site analysis SA4: access and people | **Done** (see Recently finished): ACCESSGET from OpenStreetMap (one Overpass request: the network, places, parks, stops and routes) and the US Census (TIGERweb, the ACS 5-year), free; walk times from the lot along the network (Dijkstra, 80 m a minute, steps slower, leaving the lot anywhere along its frontage), the rings of 5, 10 and 15 minutes as service-area lines; daily needs in seven kinds (a park to its edge); stops grouped with their lines; the frontage streets with class, speed, lanes, sidewalks; LEED ND's intersection density and route directness; the tract, county and state with margins of error (the Census Bureau's formulas, differences tested at 90%); eight findings; a Walk times layer on the plan; the Access and people board (ten indicators, eight figures). Not yet: GTFS frequency, cycling and slope-aware walks, census figures for the whole walk shed | `reference/research-access-people.md`. |
| 162 | One Analyze; the boards are pages of the set | **Done** (see Recently finished): Analyze is one list by the ten categories, each with its data, analyses and findings, Model at the end, one search; the boards are pages in Presentation beside the sheets (thumbnail, the main view, Present, Print set, + Board), and Analyze links to them | The owner: "they should be just one ... it should be on the presentation layer". `reference/research-one-analyze-boards.md`. |
| 163 | Open SketchUp files | **Done** (see Recently finished): openskp's TypeScript reader (MIT, with fflate and earcut) bundled and compiled to ES5 syntax by `tools/openskp/build_reader.mjs`, inlined by its hash as a script of its own, the licences in it; a `.skp` from any SketchUp (the 2021 ZIP too) opens as locked solids per placement and material, each face once, the tags as sub-layers of the file's layer (colour, on and off), see-through materials on a sub-layer at their opacity, textures by the colour SketchUp keeps with them, named components as Assets blocks; Properties says where each came from; Import CAD, SKPIN, the library's Import. Not yet: textures drawn as images, a face's own tag, hidden instances, SketchUp's scenes as views | `reference/research-sketchup-import.md`. | The owner chose this from openskp (github.com/iamahsanmehmood/openskp): a file toolkit in five languages, not a modelling app, so only the browser reader is taken. After V162, as the owner asked. |
| 164 | Site analysis in the model I: the button, and the climate around the building | **Done** (see Recently finished): **Analyze site** (`ANALYZESITE`) from the site's place or an address -- the context (300 m at least), then the access, the climate with the site's time zone beside them, the zoning where a council layer covers the property, each step listed (Done, Partly, Failed, Skipped), one undo step; six analyses drawn as live, editable `diag` elements on Layers > Site analysis (compass and distance rings, sun paths on a dome, the model's shadows on three dates, winds by season and the strongest, isovists and named views, road noise by CRTN screened behind buildings by ISO 9613-2); kept through a re-run when changed, deleted stays deleted, Reset; a key on the view; each a row in its category. Removed: the stages, Define, typed findings, photographs, pins, checklists | `reference/research-site-analysis-in-model.md` (sections 1, 3, 5, 7). |
| 165 | Site analysis in the model II: land and water | **Done** (see Recently finished): a Ground and water step in Analyze site (the ground every 5 m for 150 m around from AWS Terrain Tiles, kept in metres above sea level; FEMA's flood zones for US sites); six layers -- contours at round heights coloured by height, slope in five classes and aspect read for warmth (Horn's method, off at first), flow lines by Strahler order with the divides between the large catchments and the land draining onto the site (Priority-Flood and D8), ponds, FEMA's zones with their base flood elevations; three findings; an area picked by its inside. Not yet: the ground finer than the tiles, culverts and pipes, flood depth, the site's own drainage design | `reference/research-site-analysis-in-model.md` (2). |
| 166 | Site analysis in the model III: movement | **Done** (see Recently finished): the access step's one Overpass request also asks for the crossings' controls, the doors, the garage entrances and the car parks, and keeps every street within 800 m with the tags movement reads (a budget of 6,000 nodes, the window kept said); six layers -- the street hierarchy by class, cycling level of traffic stress by the 2012 criteria with the 2016 crossing table and the site's low-stress reach (off at first), transit with its 8- and 12-minute catchments and PTAL where OpenStreetMap maps the headways, walk times (off at first), the way to each daily need, vehicle access (driveways, an arrow at the lot line or a provisional entry from the lowest street, doors, car parks, on-street parking by side); colours for the dark plan and a light map; two findings new and Transit's with PTAL. The owner: no timetable files, only free online data; Transitous not used (its terms would open the code and rule out selling the app). Not yet: headways where OpenStreetMap has none, daily traffic, refuges and bike-lane widths beside parking, one-way streets ridden one way | `reference/research-site-analysis-in-model.md` (4). |
| 166b | The panels | **Done** (see Recently finished): Properties' Analysis tab gone (Project, Site, View); Frame analysis's settings, results and floor loads, and the areas by usage, in their Analyze rows; the usages on Project; the left panel's edge dragged by mouse, pen or finger (242 to 560 px, the drawing keeping 320 px beside Properties, kept in this browser, a double click to reset, the keys of W3C's window splitter) and a button that widens it a step at a time (WCAG 2.2's 2.5.7); a computer's layout, a tablet on its side included | The owner: "make sure to fix the right panel also since i still see the analysis tab on it ... left panel needs to be dragable like the right panel also". `reference/research-panels.md`. |
| 166c | The analytical member, cleaned | **Done** (see Recently finished): the four fields `bimAnalyticalModel` gave each member and nothing read -- `hy` and `hz` (dead since V126 took the section from the profile), `p2` and `material` -- no longer written; the member is derived on every solve and never stored, so no project carried them | V166b's follow-up: `falsify_phase125.py`'s retired `column_axes_swapped`. |
| 166d | Properties' width by one press | **Done** (see Recently finished): a button in Properties' header beside the minimise (30 px, 36 on a touch screen) widening it 240, 320, 400, 480, 560 within what the screen allows, then back to 240, its label saying where the next press goes (WCAG 2.2's 2.5.7 and 2.5.8); the drawing keeps 320 px beside the left panel at its narrowest; the edge a W3C window splitter (Left widens, Home, End, Enter minimises) dragged by any pointer; docked by the stylesheet's own query; the shell's audit reaches Properties' header | V166b's "Not done". `reference/research-panels.md` (V166d). |
| 167 | Standards registry | **Done** (see Recently finished): every standard, guideline and assumption an analysis applies is a record (32 topics: 18 applied, 14 in the US catalogue), each edition with where and when it is in force, its source to the section and the level it was read at; one reader, the edition in force for the site's place (from the address search) and the project's date, the most specific winning, a method applied outside its place saying so; overrides with a reason; stamps on every run and on the data fetched once, Out of date with why; packs with their SHA-256 and every difference shown first; Properties > Site > Standards (`STANDARDS`); no standard's number left in code, which a suite scans for. Not yet: IDS-shaped checks (I2), a pack's export, the roofs, survey tolerances and usages' defaults as records | The owner: "building a system based on the industry standards (but flexible enough when the standards changed)". `reference/research-standards-registry.md` (As built). |
| 168 | Site analysis in the model IV: land | **Done** (see Recently finished): land use by LBCS's activities through a crosswalk checked against LBCS's descriptions, in LBCS's hues stepped to pass the colour-blindness checks for every pair on the light map and the dark plan, every area outlined, three families textured, named on large areas; the mix on a 5 m grid with Cervero's entropy over the eight families; the figure-ground with Spacematrix's GSI, FSI, OSR and L for the 400 m square and its 100 m cells, and the grain; green and trees with 3-30-300 (the trees seen by the sight lines, the canopy on a 2 m grid cut to the context and said, the walk to a public green space of 0.5 ha or more); the zoning around in a council layer's own colours, read once from its drawing info; four findings; LBCS, Spacematrix, 3-30-300 and the app's land settings as records (the owner: 500 m, 0.5 ha, 8 families). Not yet: Spacematrix's types (the book not read), a land cover map for the canopy, the canopy beyond the context's square | `reference/research-site-analysis-in-model.md` (6, As built). |
| 169 | Assets: people, cycles, vehicles, parking and trees | **Done** (see Recently finished): thirteen models in Assets for scale and the simulations, each built from its parameters and the standards registry (a new area, Assets, eleven topics): a man, a woman, a child of 8 and a seated person at NCHS's mean heights with NASA's proportions (eyes, shoulders), a wheelchair user at the Access Board's measured sizes within ADA's clear floor space, its turning space on the plan; LTN 1/20's cycle and Sheffield stand; Manual for Streets' bay; AASHTO's P, SU-30 and CITY-BUS from the Green Book's 7th Edition (the owner's copy), each with its turning path on the plan, left or right; broadleaf and conifer trees by the Urban Tree Database's types; a deciduous tree bare out of the site's growing season (ETCCDI's GSL from the climate), its trunk alone casting a shadow; the context's mapped trees by their leaf tags, needle-leaved ones cones; a standards change rebuilding every placed asset. Not yet: turning templates through an angle, glTF models | The owner (V166): "do we have asset designed yet ... trees, building shape, human, bike, car for later simulations?" `reference/research-assets.md`. |
| 170 | Animated site analysis | **Done** (see Recently finished): one clock for every analysis, still until Play; Pause keeps the moment, Stop gives the still drawing back; the app opens still, and pauses where the device asks for reduced motion while it plays; the clock waits while the page is hidden. Marching dashes along the water's flows, the views, the vehicle entries and the routes (as drawn) and along the walks, the ways to daily needs and the stops (away from the site); the winds drawn on, tail to tip; the 100 m rings growing outward as one ripple; the layers coming in one after another at each Play; the sun along its path from sunrise to sunset of the study's day, with one shadow at its moment, the sun study in plan on the same clock, the project's time unchanged. Motion a style of each element (Properties, Motion), kept when the analysis runs again. Play, Pause and Stop in the status bar, first and as icons on a phone or tablet; PLAY. Save image with the 3D model (it had the overlay only). No video and no batch stills (the owner) | `reference/research-animation.md` (9, as built). V171's traffic and pedestrians draw with the same clock. |
| 171 | Simulation S1: traffic and pedestrians around the site | **Done** (see Recently finished): Traffic and people in Analyze's Access, on V170's clock (`TRAFFIC`): V166's streets within 300 m, lanes capped by a mapped width; cars by the IDM (the authors' standard car at the street's speed) and MOBIL, entering where there is room, seeing the next line, taking an amber only when they reach their line in it, keeping a signal clear, turning left after the oncoming inside the junction, claiming the lane they go into; each mapped signal's own assumed plan (Webster's cycle held between 60 and 120 s, Kell and Fullerton's yellow and red clearance, every green at least WALK and the crossing at 3.5 ft/s), all-way stops, stops on one approach, right of way as SUMO gives it; each street's typical traffic by class at Florida's 9%, half each way, turns by NCHRP 255 with no exit drawing more than its junction's busiest way in, a ramp its quieter end's; the design's trips by San Diego's rates from its usages; walkers at Helbing and Molnar's speeds over the junctions' corners, crossing only where a crossing is, on green at a signal, cars giving way on their half; typed-array pools by quality (Light, Normal, Detailed, from the device); drawn in plan and 3D; Run lays the plans, the entry's queue, the doors' people and the junctions' delays. Not a calibrated model, and said. Not yet: protected lefts and turn lanes, crossings between junctions, left-hand traffic, offsets between signals | The owner chose to build on valdrada's methods inside the app (`reference/research-valdrada.md`), credited; none of its code is in the build. `reference/research-traffic.md` (8, 9). |
| 172 | Site analysis SA5: tools and synthesis, ArcGIS's way | **Start here.** One pane for every analysis tool (typed parameters checked as filled, Run, messages, History to rerun from, results as layers); buffer, distance, slope classes, exclusions, weighted suitability in Esri's four steps (criteria, transform, weight, locate); the constraints and opportunities map; the buildable area; sun hours on the GPU; each tool a guide page in one template (summary, usage, parameters, how it works) | `reference/research-arcgis-site-analysis.md` (1). |
| 173 | Site analysis SA6: the Contents pane | The layer stack by drawing order, by source and by selection, a legend patch under each layer; symbology (by category, graduated, stretch), labels and a filter (definition query); the stack exploded in 3D as McHarg's layer cake | ArcGIS Pro's Contents pane. |
| 174 | Presentation P1: boards | V162 made the site analysis's boards pages of the set; this phase is boards you design. New Layout's page gallery (ANSI, Architectural, ISO, portrait and landscape); map frames with a live legend, north arrow and scale bar. A board is a sheet you design on: one layer tree (frames, groups, lock, hide, reorder), opacity and blend modes on every element (canvas compositing, the same 16 modes as Figma), masks, shapes, text, images; align, distribute, smart spacing; rows and columns that space their children (a light auto layout) | Figma's layer model. `reference/research-presentation-panels.md` (1). |
| 175 | Presentation P2: live elements | Elements linked to their source and redrawn when the model changes: model views, schedules, legends, the V157 dashboard's charts and cards, any result layer's chart, analysis results (sun hours, cut and fill, solar), numbers (GBA, cut volume, site area), text bound to project data (autotext). An edit on the board is an override, marked, with Reset | Archicad's linked drawings and autotext; SketchUp LayOut's overrides and Reset. The data stays connected (the owner's rule). |
| 176 | Presentation P3: styles, templates, export | The Site Analysis report: eight boards in a fixed order (location and context, zoning summary, landform and water, climate, access, risks, constraints and opportunities, buildable area and yield), filled from SA1 to SA5 in one click, every number credited. Reusable components with variants (title blocks, legend cards, callouts); shared colour and text styles (a brand kit); master boards; templates; a presenting mode, one board per slide; PDF, PNG and SVG export with blend modes, opacity and masks kept | Canva's templates and brand kits; Figma's components; Archicad's master layouts. |
| 177-180 | Interiors (I1-I4) | I1 programme and adjacency: the rooms, their areas and counts, an adjacency matrix (next to, near, apart) and its bubble diagram, checked against the model's rooms (shared walls and doors, the walk between them). I2 ergonomics and accessibility: each furniture and fixture model with its clearance zone, and a check where a wall or another piece blocks it (the ADA Standards' 30 by 48 in clear floor space, 60 in turning circle, reach ranges and door clearances; Part M; Neufert, and Panero and Zelnik). I3 circulation and escape: the travel distance to the exits, corridor and door widths. I4 inside the rooms: daylight, the view out, sightlines (V164's isovists indoors) | The owner (V166): "what about interior? the relationship and human ergonomics?" After the site analysis tools and their presentation, as the owner chose. Each phase researches first. The owner (2026-10-18), sharing Scale (github.com/ThomasZhang223/Scale, MIT): "this is my vision for interior design. i want to scan objects or have AI do it for me" -- the way in (glTF import, Poly Haven's CC0 furniture, RoomPlan scans, a mesh bound to a measured size, a mesh from a photo by TRELLIS.2's free Space, Scale's fit checks, a small solver, WebXR at 1:1) is researched in `reference/research-scale.md`, kept with the interiors (the owner's choice: keep the plan); imports first, a native Apple shell with RoomPlan and Object Capture when the app comes to the owner's Apple devices ("eventually this app might be on apple products (macbook and iphone and ipad)"); TRELLIS.2's Space with no key; the 1:1 view last (no headset to hand). |
| 181-187 | Freeform (F1-F7) | NURBS curves; surfaces from curves (extrude, revolve, loft, planar, edge); sweeps, pipe, cap; surface analysis (zebra, curvature, draft) in Analyze; point editing and blends; picture planes, text objects, flow along a surface; Make2D and rendering; Parametric Design Foundation: editable sketch -> Pad -> Pocket, persistent feature inputs/history, deterministic dependency rebuilds and failure recovery (planned; discovery and owner approval before implementation) | `reference/research-rhino-guide-gap.md`: what the owner's Rhino guide teaches that the app lacks. Placed here pending the owner's word; the LOD track follows. Owner places parametric work within this F1-F7 group (Notion parent: V181-V187), not as a separate later phase. [Task #44](https://github.com/BradleyPham1906/BIM-Personal/issues/44); `reference/plan-parametric-design.md`. Internal sequence, dates and effort TBD after audit/reuse research. The repository numbers the group V181-V187 too: reconciled 2026-10-24, when the rows from before V170 was inserted, left twice by the merges, were removed. |
| 188 | LOD-C: point clouds | LAS, LAZ (laz-perf, Apache-2.0) and PLY; USGS 3DEP fetched around the site (EPT or COPC); by class or height; ground to a V108 surface through V138's check | Philadelphia has city LiDAR (2015, 2018) and PA statewide QL2. |
| 189 | LOD-D: LOD2.2 from LiDAR | Region-growing roof planes, roof partition, optimised and extruded; LOD1.3 from the same partition; per-building RMSE to the points | 3DBAG's published method (roofer is GPL-3 C++: the method, not the code). |
| 190 | LOD-E: facade images | The owner's photos or Panoramax panoramas placed on an LOD2 wall and rectified straight-on, in metres | Texture2LoD3's rectification; Panoramax is CC BY-SA, no key. |
| 191 | LOD-F: LOD3 openings | Windows and doors drawn on the rectified facade, regularised into rows and columns, optionally detected (SAM in the browser, on request), cut into the wall | Checked against measured openings. |
| 192 | LOD-G: Gaussian splats | A `.splat` capture placed on the site as a photoreal backdrop to trace against | antimatter15/splat, MIT. |
| 193 | MEP runs | Duct and pipe runs at connectors, systems, flow, velocity and friction | MEP is its own discipline (the owner's choice). The research is drafted in `reference/research-mep-runs.md`. |
| later | Model import: glTF, and valdrada's credited models | glTF and GLB in as Assets models (meshes, materials as colours, sizes kept); valdrada's vehicles (CARLA's and its author's, CC BY 4.0) converted to V169's kinds, their dimensions kept, credited in THIRD_PARTY_NOTICES.md | The owner (V166): in-house models first, valdrada's later. Read 2026-10-24: its pedestrians (`client/src/sim/pedmesh.js`) and street trees (`client/src/city/treeGen.js`) are generator code (MIT), not model files, so they need no glTF: the walk cycle about joint pivots is for V171, on V169's bodies; the crown envelopes by species form, optional, for nearer views. |
| later | Hub H3: full IFC | web-ifc (WebAssembly, MPL-2.0) to read and write full IFC 4 and 4.3; IFC GUIDs kept on the elements so H1's diffs are IFC diffs | Our IFC writer and reader cover a subset today. |
| later | Hub H4: share and sync | Push and pull a project's history to a repository, one file per element so git diffs and merges per element; GitHub as the first hub; only when asked | The first network piece of the hub. |
| later | Hub H5: the server | Accounts, permissions per element, private models checked on the server (clashes, codes) returning only the result, paid access | Needs a backend: beyond a static site. "Zero-knowledge" checks in the viewer's browser are not possible: what runs there can be read there. |
| later | Streaming | OGC 3D Tiles out and in, so a district or a city streams by what is in view | After the LOD track. |
| later | Rendering on WebGPU | One rendering layer, WebGPU where the browser has it and WebGL where not (Figma's route); compute shaders for the simulations | When performance asks for it; the renderer is our own WebGL today. |
| later | Water and presentation rendering | Evan Wallace's WebGL Water techniques: a heightfield water surface for V143's ponds and for flooding, raytraced reflections and refractions, soft shadows, caustics; with F7's rendering | Techniques from his write-up, written ourselves. |
| later | Structural and wind analysis | A frame solver (stiffness method) for V125's columns and beams: reactions, moments, deflections; wind around buildings by lattice Boltzmann on the GPU | Feeds the Analyze tab's Simulation section. |
| later | Survey control | Horizontal control and raw total-station files | Breaklines, boundaries and LandXML landed in V144; V138's checks cover them. |
| later | Generators | Massing generated inside V160's zoning envelope to the achievable area (storeys from the envelope's height, plates from its floors, usage-tagged so the yield and the checks follow); parking layout to a ratio; subdivision into lots | Giraffe's generative solvers; the owner may pull this forward (V160 reply). |
| later | Costs and pro forma | Cost, rent, yield and sale price per usage, and a feasibility summary on V160's yield (GFA, net, units, parking) | Builds on V131's formulas; Giraffe's live financial model. The owner may pull this forward (V160 reply). |
| later | Flows and an app SDK | Per-object node graphs (Giraffe's Flows, a light Grasshopper); a documented plugin API of read-only state snapshots with listeners and named commands over postMessage | The engine's `__a3dRegisterCommand`, `__a3dRegisterDiscipline` and `__a3dRegisterTab` are the start of it. Giraffe's model: one set of functions reached two ways, the browser console and a postMessage bridge for an iframe app in the right panel, over GeoJSON-like data (`reference/research-giraffe.md`). |

### LATER - Track D, the owner's drone bridge project (Skydio, PennDOT/NYSDOT)

The owner's live project: Skydio photos go through photogrammetry to a digital model of NSTM
bridges that exist only as CAD. Photogrammetry stays outside the app, in Pix4D, iTwin Capture or
free WebODM/OpenSplat. The app does everything before and after that step. Parked by the owner
until after the LOD track ("Gaussian splats should be later on"). Detail
is in `reference/research-bridge-splatting.md` (7).

| # | Phase | Scope |
|---|---|---|
| D1 | Flight read-in and coverage | Skydio JPEG EXIF/XMP (or the geolocation CSV) to cameras on the map and in 3D; GSD, overlap and blind spots, checked on site |
| D2 | Hand-off to processing | Image list, control and check points, CRS, written for ODM/COLMAP and Pix4D |
| D3 | Bring the capture back | Point cloud, mesh, splat and solved camera positions, in site coordinates (shared with LOD-C, LOD-G) |
| D4 | Bridge model from the CAD | DXF to IFC 4.3 `IfcBridge` members with NSTM flags and member IDs |
| D5 | Register and compare | Control points then ICP; per-member deviation by colour; check-point RMSE |
| D6 | Photo-linked findings | A point on a member lists the raw photos that saw it; findings with condition state, tied to the member and the photos; report |

Project photos, models and drawings are never committed: the repo and its site are public.

### LATER - Track E, field work and autonomy

The owner (2026-10-18) shared DeepScenario's visual localisation without GPS, and BILT, SimLab and
Synode, "for the phase where field and autonomous work" happens. Read at the source in
`reference/research-field-autonomy.md`: the three companies make 3D work instructions, training and
VR from CAD, not site simulation; DeepScenario's published method (OrthoLoC) places a drone photo on
an orthophoto and a surface model, but its code and data are non-commercial, so the method only.
Candidates, their order the owner's (five questions in the note):

| # | Phase | Scope |
|---|---|---|
| E1 | glTF and GLB export | Meshes named by element ID and layer, metres, +Y up; opens in Synode, SimLab, Blender and headsets |
| E2 | Steps | A sequence over the model: a view, elements shown, ghosted, highlighted or moved, text read aloud, tools and safety, a check; by element ID, so the steps follow the model; offline on phone, tablet and computer |
| E3 | Field record | Checks done on site with time, who and a photo; a report; xAPI if wanted |
| E4 | Place a photo | Guided camera solve from points matched on the photo and the map or model, each point's error; shares Track D's control-point solve (D5) |
| E5 | A track and its video | GPX or CSV tracks and Track D's flights on the map beside a video in step; real speeds as a check on V171 |
| E6 | Automatic matches | Optional: a light matcher (XFeat, Apache-2.0) proposing E4's points against USGS NAIP orthophotos (0.6 m, keyless, CORS open) |
| E7 | 1:1 on site | E2's steps in WebXR (`reference/research-scale.md`, step H) |
| E8 | Simulation out | V166's streets as ASAM OpenDRIVE 1.9.0, a V171 run as OpenSCENARIO XML 1.4.0 |

### LATER - Track A, drafting (moved behind Track B in V100)

The numbers in this table are its order, not phase numbers: a phase takes the next free V number
when it starts (V111 to V138 went to other work; V139 to V193 are in NOW).

| # | Phase | Scope | Notes |
|---|---|---|---|
| 111 | Associativity, part 3 | Walls take added vertices; openings re-hosted after Break | What V99 did not cover. Openings are indices along a centreline, so a vertex insert or a Break has to move them with the geometry.  |
| 112 | WIPEOUT and 3DPOLY | A masking region, and a polyline with per-vertex elevation | WIPEOUT is a draw-order question rather than a geometry one, and V96's `explicit` appearance flag is the mechanism it needs. 3DPOLY needs per-vertex Y. |
| 113 | ELLIPSE and SPLINE | The two shapes bulges cannot express | Needs its own storage decision the way arcs did in V88. DONUT waits here too: it is a filled ring, which needs either polyline width or a hole in a sketch profile, and this build has neither. |
| 114 | Fillet and Chamfer between curves | Tangent-arc constructions, replacing the line-line intersections those two use now | Largest remaining piece of the curve series. |
| 115 | Join and Merge on curves | Colinearity replaced by concentricity | Smaller than 101 and independent of it. Finishes the eight modify tools. |
| 116 | Modify toolbox, rest | STRETCH EXPLODE ARRAYPATH PEDIT MATCHPROP PROPERTIES OOPS OVERKILL | What V87 did not cover. |
| 117 | Dimension set | DIMORDINATE DIMBASELINE DIMCONTINUE DIMALIGNED DIMARC DIMSTYLE QDIM DIMEDIT DIMTEDIT | DIMORDINATE is station-and-offset — civil and bridge drawings can't be issued without it. |
| 118 | Blocks and data | ATTDEF ATTEDIT BEDIT WBLOCK DATAEXTRACTION TABLESTYLE TABLEDIT TABLEEXPORT | First phase that's about the disciplines, not drafting. BLOCK and INSERT landed in V124, as the Assets library's blocks: saved records inserted as independent copies. A block reference that follows its definition (what BEDIT edits) is not built. |
| 119 | Sheets and plotting, rest | MVIEW (draw a viewport on the paper) PAGESETUP (plot settings beyond Sheet Setup) PUBLISH (V122's Print set prints every sheet in one job; a chosen subset and page setups remain) EXPORTPDF (vector PDF of a sheet) VPLAYER (per-viewport layer visibility) viewport lock | LAYOUT, MSPACE and PSPACE landed in V116, with layout tabs and model space through a viewport. |

**Recently finished:** Phase 171 (V171), **traffic and people around the site**.
- The owner's choices (2026-10-25), each as the research proposed: each junction's own signal plan; the authors'
  standard car at the street's speed; Florida's 9% on the typical traffic by class, turns by NCHRP 255; the lot's
  trips by San Diego's rates from its usages. Then: go on without stopping for questions. The first phase built in
  `src/` after the split; the simulation is its own folder, `src/js/engine/simulation/` (seven files).
- **Cars** by the IDM and MOBIL on V166's streets within 300 m, entering where there is room, seeing the next line,
  taking an amber only when they reach their line in it, keeping a signal clear, turning left inside the junction
  after the oncoming, claiming the lane they go into; **signals** where mapped, each junction's assumed plan (Webster,
  Kell and Fullerton, the least greens, WALK and the crossing), all-way stops, stops on one approach, right of way as
  SUMO gives it; **demand** by class at Florida's K, turns by NCHRP 255 (no exit above its junction's busiest way in;
  a ramp its quieter end's), the design's trips by San Diego's rates.
- **Walkers** over the junctions' corners, crossing only where a crossing is, on green at a signal; cars give way on
  their half.
- **Light:** typed-array pools allocated once (Light 200 cars and 300 walkers, Normal 600 and 1,000, Detailed 1,500
  and 3,000), the quality from the device; 0.14 ms a step at Light here.
- **Traffic and people** in Analyze's Access (its row: Simulate, the peak hour, the quality, the speed), on V170's
  clock; drawn in plan and 3D; Run lays the signals' plans, the entry's queue, the doors' people, the junctions' delays.
  `TRAFFIC`, `TRAFFICOFF`. Ten standards topics in a new area, Traffic.
- **Checked** in 109 checks against a Python reference worked from the sources; broken 62 ways, all 62 caught on the final suite (the first run missed
  two, a dead filter and a tolerance the fixture never reached, each fixed). Found while building:
  red runs at short links, an amber taken then lost, walkers across four lanes at a driveway, a motorway drawing 76%
  of a junction, two cars in one place, a merging ramp with the way; each fixed (`research-traffic.md`, 9). The full
  regression: 130 suites, 6537 checks, all passed (V166d's tap after a run alone);
  V62, V141, V142, V148, V162, V165 and V167 amended.

Phase 170 (V170), **the site analysis in motion**.
- The owner's choices (2026-10-24): still until Play, with Pause; all four motions; no video and no
  batch of stills ("just image at the moment it captured"). Built while V169's checks ran, from a
  frozen copy (the owner: never idle on long checks).
- **One clock**, run by the browser's frames while playing, at most 30 a second; Pause keeps the
  moment, Stop gives the still drawing back pixel for pixel; nothing saved or undone.
- **The motions:** marching dashes along flows, views, vehicle entries and routes (as drawn) and along
  walks, the ways to daily needs and the stops (away from the site); winds drawn on; the 100 m rings
  growing as one ripple; the layers coming in in Analyze's order; the sun on its dome through the
  study's day with one shadow, the sun study in plan following. Each element's Motion in Properties.
- **Play, Pause and Stop** in the status bar; on a phone or tablet first, as icons. `PLAY`.
- **Save image** has the model now: the 3D canvas copied in the task it is drawn in, the overlay over it.
- **Checked** in 104 checks against a Python reference of the design and the canvas's own pixels;
  broken 83 ways, all 83 caught on the final suite (four
  earlier runs found ten checks the fixture never reached or compared wrongly, each fixed). Found: Save image lost the model; the status bar already ran past a tablet's screen.
  The full regression: 129 suites, 6431 checks, all passed, no older suite amended.

Phase 169 (V169), **assets: people, cycles, vehicles, parking and trees**.
- The owner's choices (2026-10-19): vehicles sized to AASHTO's design vehicles, the owner sharing the
  Green Book (its 7th Edition, from their Notion, kept out of the repository; only its numbers used,
  cited); the van as the SU-30; the context's trees by their leaf tags; Manual for Streets' bay where
  no rule is recorded.
- **Thirteen models** in Assets' new group, each built from its parameters and the standards registry
  (a new area, Assets, eleven topics): people at NCHS's mean heights with NASA's proportions (eyes,
  shoulders; a child extrapolated and said; seated); a wheelchair user at the Access Board's sizes
  within ADA's clear floor space, its turning space on the plan; LTN 1/20's cycle and Sheffield stand;
  Manual for Streets' bay; AASHTO's car (P), delivery truck (SU-30) and city bus (CITY-BUS), each with
  its turning path, from the inner rear wheel out to the front overhang's corner, left or right; a
  broadleaf and a conifer by the Urban Tree Database's types.
- **Trees in leaf** over the site's growing season (ETCCDI's GSL from the climate fetched): out of it,
  a deciduous tree is bare and casts its trunk's shadow only. The context's mapped trees take their
  crown from their leaf tags; needle-leaved ones are cones.
- **A standards change rebuilds** every placed asset, a size set by hand kept.
- **Checked** in 183 checks against a Python reference of every source and method; broken 100 ways, all 100
  caught on the final suite (the first run missed one, and the suite was fixed). Found while building: a
  cycle 1.782 m long (its wheels' sides), V157's crowns 0.85 of their size, the Green Book's two tables
  differing for the city bus (12.80 m, 41.6 ft), an override not resizing what was placed, labels cut off.
  The full regression: 128 suites, 6327 checks, the failures of three older suites explained in the log
  (V142 until the log and the guide caught up; V82 by design, amended; V132 under load), each passing after.

Phase 168 (V168), **site analysis in the model IV: land**.
- The owner's choices (2026-10-18): a 500 m neighbourhood for the canopy, 0.5 ha as the smallest
  public green space, the mix over LBCS's eight families; each a standards record, overridable.
- **Land use** by the American Planning Association's LBCS activities, through a crosswalk from
  OpenStreetMap's tags checked against LBCS's descriptions (a hotel residential, a port movement, a
  place of worship assembly); LBCS's hues stepped so any two pass the colour-blindness checks on the
  light map and the dark plan, every area outlined, industrial, assembly and natural resources
  textured, names on large areas, the key of nine; the mix by Cervero's entropy index.
- **Figure-ground** with Spacematrix's GSI, FSI, OSR and storeys for the 400 m square and its 100 m
  cells, and the grain; **green and trees** with 3-30-300 (the trees seen by the sight lines, the
  canopy on a 2 m grid cut to the context and said, the walk to a public green space of 0.5 ha or
  more); **zoning around** in a council layer's own colours, read once from its drawing info.
- Four findings; LBCS, Spacematrix, 3-30-300 and the app's land settings as records in a new area,
  Land and green; the context asks for 24 more land use values and the grounds of amenities.
- **Checked** in 92 checks against a Python reference of every method; 84 variants, all caught (three
  told apart by the fixture first). Found while building: a crown missing every 5 m cell (the canopy
  is counted on 2 m), 0.49 x 10000 a hair over 4900, the key keeping eight of nine families. V62,
  V133, V141, V148, V157, V158, V162, V164, V165 and V167 amended; 18 falsify anchors moved by V167,
  V168 and earlier re-anchored. V153 (a lost device under load) and V167 (its date written in) made
  robust. 127 suites, 6144 checks, 0 failures.

V166d, **Properties' width by one press** (inside Phase 166, built on V167; the version stays V166).
- V166b's "Not done": Properties' edge had only the drag and the minimise. A button in its header,
  beside the minimise, widens it a step at a time -- 240, 320, 400, 480, 560 within what the screen
  allows, then back to 240 -- and says where the next press goes: WCAG 2.2's single-pointer way. It
  is hidden where Properties is a drawer or a sheet, and while it is minimised.
- **The drawing keeps 320 px** beside the left panel at its narrowest, whatever the left panel does
  (it gives way to Properties, never below 242). The drag, End and a width kept from a wider screen
  stop there too.
- **The edge** follows W3C's window splitter: a focusable separator named Properties; Left widens it
  (the splitter moves the way the arrow points), Home, End, Enter to minimise. A finger drags it now:
  it took the mouse alone.
- **Found:** the code docked Properties wherever the window was wider than 900 px and the stylesheet
  only over 1024 by 500, so between them its arrow shrank a drawer or a phone's sheet to a 42 px strip;
  the code now reads the stylesheet's own query. Properties could leave the drawing under 320 px on a
  window narrower than 1176 px. The shell's audit had never reached Properties; it now reaches its
  header and edge.
- **Checked** in 50 checks on a computer, a tablet either way and a phone either way, and at eleven
  sizes either side of 1024 and 500 px. 51 falsify variants, all caught. V147's and V166b's falsify
  scripts re-anchored; V166b's suite now waits for the left panel's easing to settle.

Phase 167 (V167), **the standards registry**.
- The owner: "building a system based on the industry standards (but flexible enough when the
  standards changed)", any country, with fallbacks, overrides with a reason, new editions with app
  versions and as files. The owner's answers (2026-10-18): a method outside its place still runs and
  says so; only the analyses' assumptions overridable now; the US catalogue listed; packs shown by
  their SHA-256 and publisher first, unsigned.
- **Every standard is a record:** 32 topics (PTAL, the walking speed and distances, LEED ND, FHWA's
  classes, CRTN, WHO's air and road noise guidelines, the stress methods, FEMA's zones, IBC's occupant
  loads, ASCE 7's combinations, and the app's own assumptions; 14 US codes in a catalogue), each
  edition dated, placed, cited to its section with its level (21 read at the source, 7 secondary, 4
  the app's, 3 not read and never applied). V105 to V166's constants are gone; every sentence that
  states a value builds it from the record.
- **In force here:** the address search gives the site's country, region, district and city; the
  most specific edition adopted there on the project's date applies; elsewhere a method says
  "applied outside its place". An edition can be chosen; a value overridden with a reason.
- **What a result keeps:** each run and the data fetched once keep the standards and values they
  were worked out with; a row or finding says Out of date and why; the findings are worked out again
  at once from the data kept.
- **Packs** add editions as files, their differences, SHA-256 and publisher shown before Apply.
- **Properties > Site > Standards** (`STANDARDS`, `CODES`), on a phone in its sheet.
- **Checked** in 195 checks against a Python reference of every record and rule; 123 falsify
  variants, all caught. Found while building: the compass rings stamped under the wrong name; numbers
  worked out at fetch said at today's values; findings fixed until Analyze ran again; typed fields
  lost on a redraw; seven standards' numbers left in sentences (among them WHO's 53 dB, now a record);
  a level overstated; two older suites' rules (V114's dead CSS, V141's tab heights) met by the app.
  V62, V73, V132, V141, V161 and V166b amended. Full regression 125 suites, 5999 checks, 0 failures.

V166c, **the analytical member keeps only what is read** (inside Phase 166; the version stays V166).
- V166b's follow-up. `falsify_phase125.py`'s `column_axes_swapped` swapped a member's `hy` and `hz`
  and was not caught: nothing reads them.
- **The audit first.** They were never on the element: `bimAnalyticalModel` derives a member from
  each column and beam on every solve, and that member is never stored (not in `bimCarryBim`, the
  project's JSON, the history, IFC or Properties). Of its seventeen fields, thirteen are read; `hy`,
  `hz`, `p2` and `material` are not, and were not in V125's own build either. In V125 the locals
  `hy` and `hz` fed the section; since V126 the section is the profile's.
- **Patch 166g** writes the thirteen and drops the two locals. Nothing a user sees changes; the
  guide, the release notes and BIM_APP_VERSION stay as they are.
- **Checked:** V125 50 of 50 and V126 61 of 61, their falsify scripts 35 of 35 each; every literal
  anchor of the 84 falsify scripts unmoved; a frame saved by V166b's Save opens in V166c with the
  same members, model and solve, and a file whose members carry `hy` and `hz` opens and analyses as
  the plain one. No new suite: a removal of what nothing reads cannot be seen in behaviour.
- **Full regression** 124 suites, 5801 checks, 0 failures. V166b recorded 5804; its own build gives
  5801 here too, every suite the same count, so the three are not this phase's.

V166b, **the panels** (inside Phase 166; the version stays V166).
- The owner: "make sure to fix the right panel also since i still see the analysis tab on it (looks
  like form the old design). left panel needs to be dragable like the right panel also."
- **Properties has three tabs** with nothing selected: Project, Site, View. The Analysis tab was
  Analyze's settings left behind when Analyze moved to the left. Frame analysis's row in Analyze
  now holds its combination, self-weight, display and deflected shape, its results, and the
  level's floor loads. Areas by usage's row lists the areas usage by usage. The usages are on
  Project.
- **The left panel's edge** is dragged by a mouse, a pen or a finger, from 242 to 560 px. The drawing
  keeps 320 px beside Properties. The width is kept in this browser, and a double click puts it
  back. It follows W3C's window splitter: a focusable separator, the arrows, Home, End, and Enter
  to shut the panel.
- **A button beside the collapse** widens the panel a step at a time and from the widest back to
  242. That is the single-pointer way WCAG 2.2's 2.5.7 asks for. The light theme's collapse, white
  on white since the shell was built, is grey now.
- **Checked** in 68 checks (the edge by mouse, by touch on a tablet on its side, and by pointer
  events; its clamps; 1280 px beside a wide Properties; the keys; the drawers on an upright tablet
  and a phone). 54 falsify variants, all caught. Five older suites amended. Falsification found two
  pieces of dead code, now removed, and one empty check in V141's suite, now made to test.

Phase 166 (V166), **site analysis in the model III: movement**.
- The third of the four phases the owner's one button grows by. The owner's answers to the research:
  Transitous not used ("do what is best": its terms would open the code and rule out selling the
  app), no timetable files ("use what's available online free"), no class set by hand.
- **Analyze site**'s access step asks the same free Overpass request for the crossings' controls,
  the doors, the garage entrances and the car parks, and keeps every street within 800 m with the
  tags movement reads, so the layers run again offline.
- Six more layers, each live and editable: the street hierarchy by class; cycling stress (each
  street's level of traffic stress by the 2012 criteria and why, the uncontrolled crossings of main
  streets by the 2016 table, the site's low-stress reach; off at first); transit (the 8- and
  12-minute catchments, the routes, the stops with their lines, PTAL by TfL's method where
  OpenStreetMap maps the headways); walk times (off at first); the way to each daily need; vehicle
  access (an arrow where a driveway enters the lot, or a provisional entry from its lowest street;
  doors, car parks, garage entrances, parking by side). Colours for the dark plan and a light map.
- Transit's finding gives PTAL; Cycling and Vehicle access and parking are new findings.
- **Checked** in 98 checks against the methods worked out again in Python (the 2012 stress criteria
  case by case, the 2016 table at every junction, the low-stress reach by two Dijkstras, PTAL by TfL's
  method), on V161's street grid with a case of each rule added; 117 falsify variants, all caught; six
  older suites amended, and two more made to measure what they claim (V155's table growing past a
  chunk that is not rebuilt; V159's second press, a race under load).

Phase 165 (V165), **site analysis in the model II: land and water**.
- The second of the four phases the owner's one button grows by ("button then the analysis run ...
  then put that under analysis layers, built straight in the model").
- **Analyze site** now fetches the ground every 5 m for 150 m around the site (the free AWS
  Terrain Tiles, kept with the project in metres above sea level) and, for a US site, FEMA's flood
  zones, beside the context and the climate. The project's own surface is read instead where it
  covers the site.
- Six more layers, each live and editable as V164's: contours coloured by height, slope in five
  classes (15% and 25% the decision points), aspect read for warmth, water flow (flow lines by
  Strahler order, the divides between the large catchments, the land draining onto the site and
  where its water leaves), ponds, and FEMA's zones with their base flood elevations. Three findings
  follow: the site's slope, its drainage, its flood zone (a red flag in the floodway).
- An area -- a slope class, a pond, a flood zone -- is selected by clicking inside it, after the
  model and the lines and words over it.
- Cleaned up on the owner's word: flood zones labelled apart, not stacked by the site; a short
  view's key keeps the analyses turned on last; the diagrams' words keep clear of the north arrow,
  the view cube and the key.
- **Checked** in 111 checks against every method worked out again in Python (Horn, marching
  squares, Priority-Flood with D8, Strahler, the catchments, the divides, the ponds, FEMA's
  classes), on a made-up ground served as Terrarium tiles and a FEMA answer, with FEMA down, a site
  outside the US, the context's terrain and a survey of the project's own; 82 falsify variants,
  all caught; four older suites amended. V148's falsify script was re-anchored, and its suite
  closes a gap left since V158: a layer dragged onto the Analysis heading is refused.

Phase 164 (V164), **site analysis in the model, from one button**.
- The owner: "all i want is button then the analysis run ... then put that under analysis layers,
  built straight in the model that i can interact with", "a live analysis that is editable", and
  the checklist removed entirely.
- **Analyze site** needs only the site's place (or an address): it fetches the context, the
  access, the climate with the time zone and the zoning, lists each step as it arrives or fails,
  and draws six analyses on Layers > Site analysis -- compass and distance, sun paths, shadows,
  winds, views, noise. One undo step.
- Each element is the analysis's and yours: moved, turned, restyled or relabelled it is kept
  through a re-run; deleted it stays deleted; Reset gives it back. Properties says what it shows,
  how, and from where. The stages, Define, typed findings, photographs, pins and checklists are gone.
- **Checked** in 171 checks against the standards and geometry worked out again in Python (CRTN,
  ISO 9613-2, the sight lines, the wind binned again, the sun's declination), with every service
  answered by a fixture and each one broken in turn, and a project from before V164 opened; 69
  falsify variants, all caught; six older suites amended.

Phase 163 (V163), **SketchUp files open as the app's own objects**.
- The owner asked for openskp's code ("they opensource sketchup like app ... make it work in our
  app") and chose Open .skp files. Its reader goes in as written, compiled to ES5 syntax by a
  pinned, reproducible build, its licence and its two packages' in the page.
- A SketchUp file opens where it was drawn: a locked solid for each placement and material, every
  face once; the tags as sub-layers in their colours, off where SketchUp had them off; glass on a
  see-through sub-layer; named components as blocks in Assets. One undo step.
- **Checked** in 115 checks against a file written by openskp's own writer from geometry the
  test knows (bounds, areas, a nested and a mirrored placement), and 54 falsify variants, all
  caught; by hand on openskp's samples, SketchUp 2017 to 2025, a Portuguese file among them.

Phase 162 (V162), **one Analyze, and the boards as pages of the set**.
- The owner: the analyses and the site analysis "should be just one", and the boards belong "on
  the presentation layer not its own thing". They chose Analyze by the ten categories, and boards
  as pages in the set.
- Analyze is one list: the stages and Define, the ten categories each holding its data, analyses
  and findings, then Model. One search: a category your words name shows whole, otherwise only
  its matching analyses.
- Climate and risk, Zoning and yield, and Access and people are pages in Presentation beside the
  sheets: a thumbnail, the main view with the panels beside it, Present, Print set on A3
  landscape, + Board, dragged among the sheets. Analyze fetches the data and links to them.
- **Checked** in 109 checks, with 60 falsify variants, all caught; eight older suites amended.

Phase 161 (V161), **access and people: walk times, transit, the frontage, connectivity, the census, and the board**.
- From free sources, no key: OpenStreetMap through Overpass (the walking network, the places of
  daily need, parks, stops and their routes) and the US Census (TIGERweb, the ACS 5-year).
- Walk times from the lot along the streets, drawn as Network Analyst draws service areas; daily
  needs in seven kinds; the stops with their lines; the streets the lot fronts; connectivity as
  LEED ND counts it; the tract against its county and state, with every margin of error.
- The Access and people board (ten indicators, eight figures), eight findings, and a Walk times
  layer on the plan.
- **Checked** in 152 checks against an independent working (a half-metre net, heapq,
  numpy, the Census formulas written out again), with a reference that breaks each walking rule
  to show it matters, and 64 falsify variants, all caught.

Phase 160 (V160), **zoning, the envelope by side, the yield, and the board**.
- The owner asked, mid-phase, whether this matches Giraffe's zoning analysis. On the core it does;
  the one gap in the envelope (a profile for every side, not the front only) was closed before
  shipping. Generated massing and costs are their own later phases.
- The zoning record, by hand or from council layers (MapPLUTO, FSR and height layers). Each kind of
  side has a rule (a setback, steps, an angular plane). The envelope is worked out exactly and
  built as a closed solid of whole faces. Then the yield, and the design checked against it.
- The Zoning and yield board: the permit-style zoning analysis table, true-scale sections after
  ZD1, the rules by side, the plan, plates and yield.
- **Checked** in 132 checks against independent working (rectangles by formula, an L-shaped and a
  U-shaped lot by hand, the mesh as a closed surface), and 42 falsify variants, all caught.

Phase 159 (V159), **climate and risk, and the board**.
- The owner asked for research on how professionals present it, and for a really professional
  result. The board follows CBE Clima, Ladybug, Weather Spark, ArcGIS Dashboards and data-journalism
  practice: indicators with references, figures titled with their findings, every number sourced
  and tabled.
- Ten years of ERA5 climate, a year of hours, CAMS PM2.5 and USGS earthquakes, free, worked out in
  the app and kept with the project; nine findings join the Site analysis.
- Site analysis now lives inside Analyze, as the owner asked.
- **Checked** in 89 checks against an independent recomputation, and 29 falsify variants.

Phase 158 (V158), **the site analysis workspace and its standard**.
- The owner: "i want to standardize the whole process." A Site tab runs every site analysis the
  same way: the stages, the ten categories, checklists for the desk and the site.
- Every finding names its source, date and confidence, and is classed (fact, opportunity,
  constraint, red flag) and weighed; red flags come first; findings are pinned on the plan, with
  photographs.
- Fill from the model turns what the app already knows into findings with their sources.
- Analysis and Data are group rows in the Layers tree, as Context is, each with one eye for all
  it holds.
- **Checked** in 92 checks and 34 falsify variants.

Phase 157 (V157), **the whole surroundings, in 3D**.
- The owner: "the trees and roads and tunnels, bridges railway and airports. currently we only
  have buildings." From the same free Overpass API, the context now brings railways, airports,
  power lines and land use too, each on its own layer under Context.
- Every road, railway, runway and taxiway has a surface of its width; a road is coloured by its
  use. Bridges stand on piers at their deck; tunnels are their line only. Trees have trunks and
  crowns; tree rows are planted. On the terrain, everything follows the ground.
- **Checked** in 121 checks and 25 falsify variants.

Phase 156 (V156), **the frame's upkeep and picking**.
- The owner's BENCHMARK (their computer): 5,000 elements 3.1 ms a frame with WebGPU, 4.1 with WebGL;
  20,000, 9.3 and 10.5. Both far inside the 16.7 ms of 60 fps; WebGPU 25% and 11% quicker.
- At 20,000 the shared JavaScript upkeep is most of the frame: cut down (the search for removed
  objects only when one is gone; colours by type once a frame).
- A click on a large model picked by a GPU id pass: what is drawn there, frontmost by depth.
- **Checked** in 17 checks and 10 falsify variants.

Phase 155 (V155), **culling and BENCHMARK**.
- Chunks by 64 m cells of the ground; a chunk wholly out of view is not drawn, in either engine,
  with the same picture. Up close on 20,000 elements, 15 of 16 chunks are left out.
- WebGPU records a bundle per chunk and pass, kept: the view sweeping the model records nothing.
- BENCHMARK times 5,000 and 20,000 elements with WebGPU and WebGL on the device it runs on, and
  puts the model back.
- **Checked** in 24 checks and 15 falsify variants.

Phase 154 (V154), **the map and terrain in WebGPU; outlines that hold**.
- The basemap and a terrain surface with the map draped on it drawn with WebGPU, each tile a
  texture with mipmaps made on the GPU; a site project now stays on WebGPU.
- Outlines pulled toward the eye by 0.02% of their distance in all three shaders: no more depth
  tie with their face, no flicker, and the two engines agree.
- **Checked** in 24 checks and 18 falsify variants.

Phase 153 (V153), **the WebGPU engine, WebGL kept**.
- WebGPU draws the model where the browser has it, from V152's description; every draw recorded
  once in a render bundle and replayed with only the camera sent.
- WebGL draws while it starts, without it, after a lost device or a failed frame, by choice
  (GRAPHICS), and for the map and terrain in 3D; Statistics names the engine.
- Checked against WebGL pixel by pixel, offscreen (a headless browser cannot present WebGPU).
- **Checked** in 38 checks and 23 falsify variants.

Phase 152 (V152), **the 3D scene in GPU-friendly batches**.
- Objects merged into chunks; each object's offset, transparency, colour and selection in one
  table on the GPU, only changed rows sent; the camera alone rebuilds and sends nothing.
- 5,000 elements: 1 draw call instead of 5,000, a frame about twice as fast in software; 20,000:
  4 instead of 20,000, about three times. The same pixels as before in every case checked.
- **Checked** in 39 checks and 19 falsify variants.

Phase 151 (V151), **branches and merge (the Hub's H2)**.
- Design options as branches: New Branch, switch (refused over changes not committed), each
  branch's own line of versions, Compare's numbers side by side, Delete asked once.
- Merge In, three ways against the version both share: one side's change taken, both sides'
  fields put together, the same field both ways or a change against a delete a conflict, shown
  side by side, kept or taken; Finish Merge makes a version with two parents.
- On a phone and a tablet the History commands open the Properties sheet; the tab strip is no
  longer see-through as the panel scrolls.
- **Checked** in 56 checks and 37 falsify variants.

Phase 150 (V150), **a tool palette for a phone and a tablet**.
- Select, Pan, Line, Rectangle, Circle, Wall, Door, Window, Dimension, Delete and All tools in a
  frosted capsule; the tool in use in blue; dragged by its grip, docked upright at an edge or flat,
  folded to one round button, kept where it was left. The dock gives way to it on touch layouts.
- **Checked** in 36 checks and 23 falsify variants.

Phase 149 (V149), **the shell on a phone and a tablet**.
- A phone upright: a labelled tab bar along the bottom with More for the rail's tools; the left
  panel a drawer over a full-width drawing, shut at the start, shut by its tab, a tap beside it
  or Esc. A tablet upright or a phone on its side: the rail and the same drawer. A computer and a
  tablet on its side: unchanged. The layout follows the screen as it turns.
- Safe areas (notch, home bar) kept clear; messages above the bar; pinch and pan checked again.
- Typing on a phone: every field 16 px on a touch screen, so iOS does not zoom in; the keyboard
  lifts Properties and the drawer, the field tapped in view; Find keeps the address typed.
- **Checked** in 74 checks on five screens, and 39 falsify variants.

Phase 148 (V148), **Analyze, redesigned; results as layers**.
- Analyze is a list in four groups (Model, Site and terrain, Structure, Environment): one line a
  row, opened in place to the rest; a search that matches the starts of words.
- **Add as layer**: sun hours and rain kept as run (saved, comparable, out of date when the model
  moves, Update on their own date); slope, elevation, aspect and cut and fill following their
  surface. Layers has Analysis and Data sections: eye, opacity, legend, rename, reorder, remove.
- Sized for a finger on a phone and a tablet; the Project Browser's tree no longer covers the
  other tabs on a phone.
- **Checked** in 114 checks measured in the browser, and 57 falsify variants.

Phase 147 (V147), **the right panel, redesigned**.
- One set of tokens for dark and light; sentence-case headers on a hairline; one row grid that
  stays inside the padding; one input and one button style; the element's name at 13 px.
- Resizable from its left edge (240-560 px, remembered, double click resets) and minimisable to a
  strip; long lists end in Show all.
- On a phone a bottom sheet (62%, a grab bar to 92%); on a tablet a 340 px drawer; 36 px targets
  on any touch screen.
- **Checked** in 24 checks measured in the browser, and 19 falsify variants.

Phase 146 (V146), **history by element** (the Hub's H1).
- **COMMIT** keeps the model as a version; each element (every object, and each project part)
  stored once by a 128-bit hash of its canonical JSON, so a version adds only what changed.
- **HISTORY**: changes since the latest version, field by field ("moved by 1, 0, 2", "Level 1
  added"); each version's changes; Restore (undoable, the history never rewritten); an element's
  own history. Saved with the project.
- **Checked** in 42 checks (the hash recomputed in Python) and 28 falsify variants.

Phase 145 (V145), **grading**.
- **GRADE** runs each pad's cut and fill slopes out to the ground -- square to its edges, fanning
  round outside corners, meeting in valleys at inside ones -- into a proposed surface, updated in
  place and out of date when a pad or the ground changes.
- **CUTFILL** is exact between any two surfaces (overlapping triangles clipped, plane differences
  integrated); **CUTFILLMAP**, **SPOTELEV**, **SLOPEARROWS**; a Grading card in Analyze.
- **Checked** in 62 checks against closed forms and a 5 cm integral of the defining surface, and
  38 falsify variants.

Phase 144 (V144), **terrain: breaklines, boundaries, analysis, LandXML**.
- **Breaklines** from polylines (BREAKLINE) or the survey's BL/BRK codes, forced into the
  triangles; crossing lines meet at a shared vertex. **A boundary** trims the surface
  (TERRAINBOUNDARY); points outside are left out and counted, not failed.
- **Slope, elevation and aspect** bands in plan, with a legend and the area of each (SLOPEMAP,
  ELEVATIONMAP, ASPECTMAP; Properties and the Analyze tab).
- **LandXML 1.2** out in the survey's own coordinates and units, with breaklines and boundary;
  in with the file's own triangles (LANDXMLOUT, LANDXMLIN, IMPORTCAD).
- **Checked** in 83 checks against independent calculations, and 36 falsify variants.

Phase 143 (V143), **Simulation**.
- **Sun hours** on the ground through a day (SUNHOURS), **clear-sky solar** on every face through a
  year with shading (SOLAR, shown by Colour By), **rain on terrain**: ponds, their volume, and flow
  lines (RAINFLOW). In the Analyze tab's Simulation section.
- **Checked** in 43 checks, each against an independent Python calculation, and 24 falsify variants.

Phase 142 (V142), **the user guide, and versions**.
- **A guide on the site** (`/docs/`): nine pages written for this app, a command reference built
  from the app's own catalogue, release notes for V87 to V142, and a versions page.
- **Every older build kept** at `/v/<version>/` (55 of them), from the builds kept in `Phase/`.
- **In the app:** the version in Properties > Project > Statistics; DOCS, RELEASENOTES; F1 in the
  command search opens the command's entry.
- **Checked** in 31 checks (the guide is held to the build) and 12 falsify variants.

Phase 141 (V141), **a shorter right panel, and an Analyze tab**.
- **Properties' tabs** with nothing selected: Project | Site | View | Analysis; the site's place and
  sun in a Location group; commands turn to their group's tab; the tab is remembered.
- **Analyze**, on the rail below Assets: seven cards, each saying what it shows, to run it or open
  its settings. ANALYSES.
- **Checked** in 49 checks and 21 falsify variants; ten older suites amended for the tabs.

Phase 140 (V140), **LOD-B: LOD2 roofs from OSM's tags**.
- **Roofs made of planes, never smoothed:** hipped by the straight skeleton; gabled, half-hipped,
  gambrel, mansard and skillion as the lower envelope of planes; pyramidal to an apex; flat. Walls
  rise to the roof's edge: one closed solid, LOD2.0.
- **From the tags:** roof:height, roof:levels, roof:angle (else 30 degrees), roof:direction,
  roof:orientation; curved and unknown shapes kept as blocks, with the reason.
- **Checked** against hand-worked volumes in 55 checks, and 32 falsify variants.

Phase 139 (V139), **LOD-A: building parts, labelled LODs, CityJSON**.
- **LOD1.3 from OSM's building parts:** an outline with parts is drawn as its parts, each from its
  base to its top, standing on its building's ground; whole buildings stay LOD1.2.
- **Every building says its LOD** and how it was made, with a **solid check** by val3dity's rules
  (LODCHECK).
- **CityJSON 2.0 out and in:** in the site's UTM zone, Building and BuildingPart, typed surfaces,
  OSM's credit; read back to the millimetre; other grids placed by their centre and named.
  CITYJSONOUT, CITYJSONIN.
- **Checked** in 116 checks (cjval validates the export) and 62 falsify variants.

Phase 138 (V138), **verify the survey**.
- **A Survey Check on every surface:** lines skipped, duplicates, the surface through every point,
  bust shots, check shots' RMSE, control points, and the public terrain (offset, feet read as
  metres), with a verdict and a report to export. SURVEYCHECK.
- **Verified every time:** surveys in `tests/data/surveys/` with a sidecar are held to it on every
  build; `tools/verify_survey.py` checks any file headless. See `tests/data/surveys/README.md`.
- **Checked** in 57 checks and 33 falsify variants.

Phase 137 (V137), **the map on 3D terrain**.
- **Terrain in 3D:** a surface (the one CONTEXT brings, or a survey) drawn shaded in 3D views, the
  basemap draped over it tile by tile, lined up with the flat map around it.
- **Buildings on the ground:** context buildings stand on the lowest ground under their footprint
  (Site Context: Buildings on the terrain, on by default).
- **Checked** in 28 checks and 23 falsify variants.

Phase 136 (V136), **colour by property**.
- **The model coloured by** usage, level, type, layer, material, height or any property (OSM tags,
  imported attributes), in 3D and 2D, with a legend of each colour and its count. Kept with the
  project; one undo step. COLOURBY.
- **A data layer coloured by** one of its attributes, at an opacity.
- **Checked** in 56 checks and 38 falsify variants.

Phase 135 (V135), **find open data**.
- **238 US open-data portals** (federal, state, city and county) from GeoLibre (MIT), searched from
  the Data Layers group: ArcGIS Hub through ArcGIS Online's search, Socrata through its Discovery
  API. The portal is guessed from the site's address.
- **A result becomes a data layer:** a layer, a service's layers picked one by one, a GeoJSON item,
  or a Socrata dataset asked for the site's box only.
- **FINDDATA** opens it. Checked in 77 checks and 51 falsify variants.

Phase 134 (V134), **data layers**, and V134d.
- **Data layers.** Parcels, zoning and flood zones from any ArcGIS REST layer, WFS or GeoJSON file,
  with presets for FEMA's flood zones and Philadelphia's parcels and zoning. They are read for the
  site's area and drawn on the plan.
- **Click to read.** A click reads a feature's attributes, and a parcel becomes a property line in
  one step.
- **Kept with the project.** Features are saved with the project, outside the undo snapshots.
- **V134d (the owner's "i cant get any context").** CONTEXT asks Overpass with a plain GET and
  tries its public mirrors when overpass-api.de refuses.
- **Checked** in 72 checks and 32 falsify variants.

V133d and V133e, from the owner's first real use.
- **The street map** is Esri's World Street Map (V133f). OSM's own servers answer a page opened as
  a file with "Access blocked" tiles, and CARTO's with "API KEY REQUIRED".
- **The satellite's zoom** counts screen density, and every tile is mipmapped.
- **Zoom** goes from 0.5 m to 200 km, about the cursor, as in AutoCAD and Revit. The far plane
  follows the view.
- **Checked** in 21 checks at device scale 2, and 11 falsify variants.

Phase 133 (V133), **site context in one click**.
- **One press** (CONTEXT, or Get Context in Properties) brings the buildings, roads, water, green
  and trees around the site from OpenStreetMap (Overpass), and the ground from AWS Terrain Tiles.
  The area is 150 m by default, around the property lines or model 0,0.
- **Buildings** are extruded to their height tag, levels × 3 m, or an assumed 6 m (said).
  Multipolygons are joined; a courtyard is filled and counted.
- **The terrain** becomes a V108 surface sampled from the Terrarium tiles. Its datum is kept on the
  site, or is the survey base's, and its credit names the tiles' own sources.
- **The objects** are pinned, on Context sub-layers, each with its source, credit, OSM id and tags.
  A fresh fetch replaces only what it brings, in one undo step. Each source's failure is named.
- **Checked** in 102 checks and 49 falsify variants. A screenshot found the new surface left
  selected; falsification found a dead current-layer restore.

Phase 132 (V132), **the map**, "just like how giraffe do", free sources only.
- **Placed on the earth:** the site's latitude and longitude are model 0,0 and true north turns
  the model; metres become degrees on the WGS84 ellipsoid (checked against a Vincenty geodesic).
- **The basemap:** OpenStreetMap's street map, Esri's imagery, or any `{z}/{x}/{y}` tile URL with
  its own credit, under the plan and the 3D ground, in WebGL and on the 2D canvas. Off until
  turned on, so nothing is asked of the network until then; never on paper.
- **Tiles:** zoom from metres per pixel, at most 80 a view, 12 in flight, nearest first, a parent
  while one loads, about 400 kept. A server that fails, or does not allow browser access, is named
  in the credit line.
- **The address:** Find (Nominatim, one request a press, a second a second) puts the site there.
- **Site data:** GeoJSON and KML in, as sketches and points with their properties on a Site data
  layer (a projected file refused with the reason); the plan out as GeoJSON in longitude and
  latitude, a mass as its footprint.
- **Commands:** MAP, FINDADDRESS, GEOIMPORT, GEOEXPORT, on the ribbon and in the search.
- **Checked** in 157 checks and 49 falsify variants. A routed response cannot fail CORS (the
  harness answers it), so the suite starts a real local server that sends no CORS header.

Phase 131 (V131), **usages and live areas**, the first of Giraffe's ideas.
- **The library:** a usage (Residential, Office, Retail, Hotel, Parking, or your own) carries a
  colour, GBA→GFA and GFA→NSA ratios, a floor-to-floor height, parameters and formulas. It is kept
  with the project's types.
- **Measuring:**
  - a mass is stacked into floors and each floor sliced at mid-height;
  - a floor slab is one floor of gross;
  - a room is net, measured.
- **Formulas:** `units = floor(NSA / unitSize)`, read by our own evaluator, with every mistake said
  in words.
- **In Properties:** the Usage page (for a whole selection at once), the project's Areas by Usage,
  and the usage editor. An Areas by Usage schedule, and USAGE and USAGES.
- **Checked** in 56 checks and 32 falsify variants. Falsification found two undo checks that passed
  without their undo step.

Phase 130 (V130), **every tool in one panel, and a dock of the few used
most**, the owner's request ("this tool bar is very crowded ... only show the keys one").
- **The panel:** Tools and shortcuts lists every ribbon tool, grouped by tab, then every key. It has:
  - one search;
  - All / Tools / Keys filters;
  - sorting by group, by name, or by most used;
  - an On the dock list, and a pin on each tool.

  A row runs its tool.
- **The dock:** one row, about 50 px tall against V129's 143. It holds the discipline, the tools
  pinned for it (the most used by default, twelve at most), All tools (`?`) and the search.
- **Checked** in 59 checks and 21 falsify variants. Sixteen older suites were amended, because their
  tools moved from the dock's More menus into the panel. V129's falsify retired three variants and
  re-anchored three.

Phase 129 (V129), **the shortcuts panel and a labelled dock**, the owner's request, built to a
mockup the owner approved.
- **The panel:** `?` or SHORTCUTS opens it centred over the drawing, with a search, categories
  with counts, and the keys in a right-hand column beside the command to type. Typing points (x,y,
  d<a) is its own page.
- **The dock:**
  - every tool and every group is named, and the overflow says More;
  - search is a labelled pill;
  - tooltips show after a short pause, or at once on keyboard focus, with the name, keys, what to
    type, what it does and where it lives;
  - Appearance can switch to icons only.
- **Checked** in 62 checks and 34 falsify variants. The first labelled dock was 53 px taller and
  broke four suites' geometry. It was made compact (143 px against 119), and falsification caught
  a panel whose every click counted as a category click.

Phase 128 (V128), **one command search**, the owner's request.
- **One search.** Ctrl+K, the dock's magnifier, and typing a letter on the drawing (AutoCAD's
  type-anywhere) all open the same search, which covers every command and every ribbon tool.
- **Rows** show what each command does, where it sits on the ribbon, its alias and its keys, with
  the matched letters marked.
- **Matching:** synonyms (ROUND → FILLET), abbreviations (PLNE), keyboard chords (Ctrl+Z → UNDO),
  and a typo when nothing else matches. Results are ordered by match, then by use, and an empty
  search starts with the recently used.
- **Shortcuts:** `?` searches the keyboard shortcuts, and so does the shortcut sheet's new search
  box.
- **Teaching:** every ribbon tooltip names the command to type.
- **Checked** in 50 checks and 38 falsify variants. Falsification found two fixtures that matched
  by more than the rule under test.

Phase 127 (V127), **alignments and profiles**, Track B item 3.
- **ALIGNMENT** turns an open polyline into a route, in its place. Each PI gets a circular curve,
  and curves that would overlap are refused.
- **Stations** are ticked every 20 m and labelled every 100 m, and every PC and PT is marked.
  STATION reads the station and offset of any clicked point, exactly on the arcs.
- **The profile** has PVIs and AASHTO parabolic vertical curves, with K and the high or low point.
  It is set in Properties next to the Alignment page. PROFILEVIEW draws it in model space over the
  ground sampled from a V108 surface.
- **Schedules and export:** Alignment and Profile schedules, and the route in DXF, SVG and on
  sheets.
- **Checked** against the textbook on a route turned off the axes. A fixture with room to spare
  hid the fitted radius until falsification caught it.

Phase 126 (V126), **the section-profile library**, Track B item 2. A column or
beam type may carry a profile -- rectangle, round, HSS, pipe, I (W and IPE) or channel -- and the
member is that section: its solid is the profile swept along it (a beam hung by its top with its web
upright, a column's section turned with it), its analysis takes the section's A, I and J (computed
exactly from its nominal dimensions, fillets stated as not modelled), and Properties' Structural page
shows them with the mass per metre. 28 sections ship: AISC W, C, HSS and pipe, EN IPE, and concrete
rounds, all Steel except the rounds. A stored project gains them once and keeps its own types. The
section is chosen in the Type list (now grouped by material), or dropped from a folded Sections group
in Assets; a profiled member's width is refused, and Edit Type locks it. Checked against the textbook
to 1e-12, the AISC manual within the fillets' share, A x L for every solid, and PL^3/3EI. Found: a
square section and a bounding box each hid a wrong rule from the checks; the falsify runner skipped
six variants with capitals in their names.

Phase 125 (V125), **the structural object model**, Track B item 1. The
analytical model is derived from the live columns and beams (lines at column centres and beam tops,
ends merged within 50 mm, a member split where another lands on it); supports at column bases
(Automatic, Fixed, Pinned, Free) and beam end connections (Rigid, Pinned); D and L loads -- self-
weight, line and point loads on beams, lateral loads at column tops -- and the ASCE 7 combinations;
a 3D direct stiffness solve (RCM-ordered band, Cholesky) that refuses an unstable frame by node and
direction. ANALYZE shows the analytical lines, a moment, axial or shear diagram labelled with each
member's peak and the deflected shape over the model; ANALYZEOFF hides it; a changed model shows no
result, only that it is out of date. Set in Properties -- the member's Structural page, the model's
Analysis page -- with SUPPORT and LOAD opening them, and one Analyze button: the owner asked mid-phase
for a clean, consistent interface after Rhino's, and nothing new was opened. Checked against closed
forms, a plane-frame solve written in the suite, and equilibrium. Found: a sampled peak missed the
real one between samples; a typed load value was lost when the panel re-rendered; four checks that
could not tell right from wrong (an axis-aligned member's turn is its own transpose).

Phase 124 (V124), **Assets**, the third panel of the owner's stack: "blocks
templates premade for easy drag and drop into the project", a library that "can be built upon ... when
I go online and collect items, obj, or import models". The Assets tab is the library: a search, Import,
Block, Model and Template; models (a starter set of nine at real sizes, and the user's), blocks and
templates as tiles with thumbnails; annotation, materials, wall types and patterns after them. Drag a
tile onto the drawing and it lands at that point on the active level, snapped as a click is; a
material, wall type or pattern goes on the object it is dropped on; a click places at the centre of
the view. An imported OBJ or STL asks its unit and up axis and shows the size it would come in at. A
block is the selection's own records -- a wall stays a wall with its type -- inserted on the active
level at its elevation, its members' links pointing at each other's copies; a template opens a new
project tab. BLOCK, INSERT and ASSETS on the command line. Found: a block's room did not follow its
wall; a copy made by Ctrl+D, the gizmo or an array kept the ORIGINAL's links, so a copied hatch
re-traced onto the original when the original's sketch was edited (since V99) -- one relink rule for
every copy path now; a real click was eaten after a drop; Escape did not end a drag once anything was
selected (V83's lesson again).

Phase 123 (V123), **direct manipulation**, taken ahead of Assets on the
owner's word: "geometry manipulation for objects, shapes and assetts ... quite limited for my push,
pull, rotate ... Look into Autodesk but also Rhinoceros by McNeel on how they do it." Researched
against Rhino's gumball, AutoCAD's PRESSPULL, Revit's drag controls and temporary dimensions,
SketchUp's Push/Pull and Fusion's Press Pull (`claude/research-direct-manipulation.md`). A face is
taken by a double-click, Ctrl+Shift+click or PRESSPULL, stepped with Tab, and pushed or pulled along
its normal by hand -- stopping on other geometry, a level, the grid -- or by a number; what it means is
the object's rule: a box's Height, a cylinder's Radius, a wall's top and ends (the type kept, the
openings following), a column's top, a solid's flat faces, a closed sketch pulled into a solid. A
click on any gizmo handle asks for its value, in the project's unit. Dragging an object by its body is
the gizmo's move. Found: a typed length was metres in every project (500 in a millimetre project
moved half a kilometre); a wall lost its type through eleven rebuild and copy paths; a copy of a moved
object was made where the original had been; a turned floor kept its old outline; the body drag was
not an undo step (Ctrl+Z deleted the box); a click on a handle added an empty undo step, Ctrl+click an
invisible copy; a box's size was shown nowhere, and its Base Offset read its middle.

Phase 122 (V122), **Presentation**, the second panel of the owner's stack:
"Need a presentation for doing presentation with clients. using layout spaces, with multi pages view
like a pdf viewer." A Presentation panel second on the rail -- the sheets as a PDF reader's thumbnail
column, in order, with Present, + Page and Print set; click to read, double-click to edit, drag or
Move up / down to reorder (one order: the tabs, pages, Present and the set follow it). The sheet
view's Pages display, every sheet in one scroll with page n of N, zoom and page keys. Present: full
screen, one page at a time, keys from one table, click, wheel and a bar; Esc back to where it
started. Print set: every page in one print job on its own paper size, for the client's PDF. Found:
the model's selection (and a half-drawn sketch) was drawn on every sheet; a schedule on a sheet never
drew (its decimals were called as a function); every sheet raster at 6 px/mm -- the PNG export, the
raster print -- drew its text at half size; and a sheet's raster ignored the Presentation appearance
its print used. A page is now the same page at any size, in the appearance it prints in.

Phase 121b (V121b), **the old canvas's saved data, cleared**: the owner's
answer to V120's question, "No i want to clear them up". Seven browser-storage entries the whiteboard
wrote (`obsidian-canvas-enhanced-v6`/`-v5`, `acadDrawingsV1`, `acadLayoutsV1`, `acadBlocksV1`,
`acadDockV1`, `canvas-grid`) are removed at start by exact name, never by pattern -- a page opened
from disk shares storage with every other page opened from disk -- and the app's own keys are
untouched. Found: the light interface went dark on every reload since V114, because the Appearance
menu still saved it under the whiteboard's `canvas-theme` and nothing read that back; the theme is
`acad3dTheme` now, restored at every start, with the old value carried over once.

Phase 121 (V121), **Layers**: the owner's "layers (this should combine with
model) ... manipulate a table like how autocad do like linetype, color, hide/show, layer, sub layer,
transparency". A Layers panel first on the rail -- the layer tree with the model inside it -- and
AutoCAD's Layer Properties Manager from LAYER / LA (listed since V86, it ran nothing), with the
meanings researched from AutoCAD's help: off is still taken by SELECT ALL, frozen by nothing, locked
is drawn faded and plotted, no-plot is drawn and not plotted, and a sub-layer is what its parents
leave it. Linework is drawn By Layer in acadiso linetypes and AutoCAD lineweights; everything takes
its layer's transparency. Every way of selecting asks the layers; the plan SVG, sheet SVG, sheet
paper and plan PDF/PNG are plots; the DXF writes and reads every layer's state and linetype. Found:
locking a layer hid its room tags everywhere; hidden layers stayed snap targets; turning a layer off
left its linework drawn; nine makers gave no layer, so walls followed whichever layer was current;
SELECT ALL took frozen and locked objects; exports drew every layer and the DXF wrote them all white
and on.

Phase 120 (V120), the canvas-era cleanup: the whiteboard's stylesheet, names and scaffolding out,
the CSS one stylesheet, the shell's ids its own; the dock's User Interface menu works again.

Phase 119 (V119), the owner's "quick clean up of this drop down" and Rayon's
clean rail. The view dropdown is gone, and the HUD names the active view in its place: "Level 0 - Floor
Plan", "3D View", "Section", a saved view's own name, a sheet's number and name. The left rail is icons
only, and the "File" tab is named for what it opens, the Project Browser.

The dropdown was the one readout that named the view. Moving the name into the HUD showed that the
engine's record of the active view was right only for views opened from the Project Browser. The status
bar's 3D / 2D, the > key, every drawing tool started in 3D, the ViewCube, the dock's view buttons,
sections, saving or deleting a view, and the status bar's level all changed the view without it, and
the Project Browser's mark and Properties had been wrong the same way since V84. Every one of them
records the view now, and the name follows what it names.

Also fixed in V119:
- "flat means plan" in six more places, one predicate now: LINE started in an elevation stayed there and
  refused both clicks; the north arrow, terrain, shadows and sun path were drawn in elevations;
- an invisible ViewCube: in the plan, 51 of 121 clicks in the empty top-right corner switched the view;
- Zoom extents on an empty plan swung the camera into 3D (from the Small list);
- a saved section view's Exit goes back to the view before it.

Lesson: a rule nothing checks is a convention. V84 wrote "every view opens through bimActivateView",
and it held for the one caller V84 fixed.

Phase 118 (V118), Properties keeps the focus through its own rebuild.
Every panel edit used to re-render the panel by replacing its elements. That dropped the focus to
the page, where the next key belongs to the model, so the second ArrowDown on the wall's Type
dropdown, or the second ArrowUp on its Height, moved the wall a metre.

Panels now render through one helper that brings the live panel into line with the new markup and
keeps every element that is still there. That covers Properties, the dock's Discipline dropdown, the
views list and the level rows.

Also fixed in V118:
- after any field edit, Properties re-renders from the model: a refused Type change on a pinned wall
  used to go on showing the refused type;
- an open dialog owns the keyboard, through one gate: the nudge keys moved the object behind a dialog,
  and Ctrl+Z undid the object a dialog was about to act on;
- V105's room-field workaround is gone, and a click from one field into another now lands.

Lesson: a falsification variant that cannot fail named the missing scenario, and it held a real
bug.

Phase 117 (V117), the rest of the 2D wire shell. Deleted:
- the whiteboard's click-to-select;
- its hidden Properties / Layers / Blocks dock and rail buttons;
- its wire marquee and its Delete listener;
- seven hooks and 76 CSS rules.

The prune is proven by a same-length control, because the byte shift alone moved two anti-aliased
pixels.

**The BIM engine's Delete key had been riding on the deleted listener.** It is the engine's own now,
behind the engine's key gates. That closed two leaks:
- Delete erased the selection of the project behind the Start page;
- Backspace erased the object behind an open dialog.

**A dropdown counts as a field now:** ArrowDown on the wall's Type dropdown used to move the wall a
metre. Lesson: before deleting a hook, grep for what assigns or wraps it, not only what calls it.

Phases 115 and 116 (V115, V116), the owner's "startup tab, and project side
by side ... model and paperspace (copying the autocad and revit layout)". **Projects side by side:**
AutoCAD's file tabs -- Start, one tab per open project with its own close button, and + -- each tab
its own model with its own undo history, stored one project per key with `acad3dV1` still the one on
screen; Open opens a file in a new tab instead of replacing the model; close is not delete. The Start
page had never been seen (z-index under the drawing area; V114's suite read a class), and the
quick-access bar's Save, Open, Undo, Redo and Plot had done nothing since V113c. **Model and layout
tabs:** Model, one tab per sheet and + at the left of the status bar, drawn from the sheets; every way
onto and off a sheet is a view now (seven paths were not); and model space through a viewport --
double-click in, drag to pan, wheel through standard scales 1:1 to 1:5000, Escape out -- with the pan
in the camera every output solves. Keys and tools no longer act on the model hidden behind a sheet.
An edit made in the autosave's 300 ms wait no longer dies with a reload. Harness lesson: a Playwright
init script that touches localStorage on `file://` cuts the page's storage off about half the time.

Phase 114 (V114), **the whiteboard's stylesheet, and what was left of its
document model.** 1,583 CSS rules, 16 selector lists, 22 keyframes and 5 style elements that could
never match anything, deleted by a patch that DERIVES the dead set from the file and asserts its
output re-analyses to nothing dead -- then proved invisible: every element's computed style, with
::before and ::after, and the screenshot, identical in twelve driven states. 204 KB. On the way the
state walk found what no suite had: the Start tab and + threw after V113c, because the "drawings"
were whiteboard wire sets -- a surface that had already been misleading before, since the BIM model
was never part of them. They are one honest project tab and a Start screen that offers only what
works. And nine shell toasts had been silently doing nothing since V113c; they go through the BIM
engine's one toast now. The V114 suite keeps an independent copy of the dead-CSS analysis as a
permanent guard.

Phase 105b (V105b), **area plans**. Gross floor area per level, measured to
the inside face of the exterior walls the way IBC 202 defines it, derived from the same wall
arrangement the room tool traces; net area from the rooms; efficiency; and occupant load taken per
IBC factor rather than per room. An Areas by Level schedule, and AREAPLAN drawing the gross ring on
the plan. What it found: **a room was measured to the wall CENTRELINES**, so the same plan drawn as
one closed wall and as four separate walls reported two different areas, and a level's net area
came out larger than its gross -- impossible, and the reason the bug finally surfaced. A room now
stops at the faces of the walls that bound it, from the same inset the gross ring uses; a floor or
a foundation slab still runs to the centrelines, because a slab does run under its walls.

Phase 112 (V112), the second half of "upgrade the thing and logic": **what a
gizmo drag understands.** Object snapping (the selection's own points land on other objects'
points, through the handle's own freedom, nearest first, marked and named SNAP); a typed distance,
angle or factor that finishes the gesture exactly while the gesture keeps deciding the direction;
Escape restoring everything mid-drag; Ctrl-drag leaving a copy behind; Shift as precision; and a
pivot the user can place with Alt so rotations and scales happen about a chosen point. Found on the
way: Backspace and Delete never reached the drafting workspace at all - two workspace-era key gates
claim them before the BIM engine's handler runs, the same class V94 fixed for letters.

Phase 111 (V111), on the owner's "still lacking, I want the full detail":
**the gizmo completed against the references** (Unity, 3ds Max, Blender, three.js, Revit).
Hover highlighting with the handle named in the read-out; rotation as four full rings - one per
axis plus the screen ring about the camera - with the near half drawn solid and picked first and
the far half faded, measured by depth; the swept angle filled as a sector with witness lines; and
3ds Max's even-scale triangle between the scale boxes. The vertical ring is still V78's, so a wall
turns exactly as before.

Phase 110 (V110), on the owner's references: **the transform gizmo,
reworked.** Plane squares between the arrows, a free-move centre square (plan plane in 2D, screen
plane in 3D), tilt arcs about X and Y, scale boxes on every axis (Shift for an even scale), all in
Revit's colours - X red east, Y green north, Z blue up, origin lines included. World / Local / View
alignment and Hide from a right-click menu on any handle, or the GIZMO command. Tilt and scale are
drawn only when the WHOLE selection can follow: generic solids in 3D, sketches in plan, building
elements never. Found on the way, and fixed as a class: the transform dispatcher applied world
transforms to local geometry, so anything that had been moved turned about the wrong point in
ROTATE, MIRROR, SCALE, polar ARRAY and the ring alike; a parametric Box could not be turned at all
(it now becomes a plain solid and says so); a mirrored mesh was inside out; MIRROR and ARRAY
straightened a sketch's arcs.

Phase 109 (V109), taken out of order on the owner's request: **the view
controls moved into the status bar.** Pan, orbit, the 2D/3D switch and Tech/Pres now sit beside
SNAP, ORTHO and GRID instead of in a pill floating over the drawing -- the same buttons, so every
handler, shortcut and selector still works; the pill, its CSS and every reference to it are gone.

Phase 108 (V108), site 3: **terrain.** SURVEY takes pasted survey points
(PNEZD, PENZD, NEZ or ENZ; metres, feet or US survey feet; a base point kept on the site; turned to
True North) and makes a TIN surface (Delaunay, derived from the points, never stored). Contours in
plan, every fifth an index contour, labelled; interval from the relief or set in Properties. A
closed outline given a Pad Elevation in Properties is measured against every surface under it by
the TIN prism method -- cut, fill, and the area off the surface -- shown there and in an Earthwork
schedule. Found on the way: patches written through a tool call had been putting literal non-ASCII
into the file since V105 (JSON turns a typed \u00b2 into the character).

Phase 107 (V107), site 2: **sun position, shadows, sun path.** The NOAA
solar equations, checked against NREL SPA (pvlib) at six places and dates: elevation and azimuth
within 0.01 deg, sunrise and sunset within half a minute, the midnight sun handled. Latitude,
longitude, UTC offset, date and time on the site, set in Properties with nothing selected, with
altitude, azimuth, sunrise and sunset shown beside them. SUNSTUDY draws the model's shadows on
the ground in plan (projected along the sun, the building's own footprint cut out, ground slabs
neither casting nor hiding) and a polar sun path turned to true north. Found on the way: zoom to
extents on an empty drawing leaves plan for the 3D home view.

Phase 106 (V106), structural 2: **tributary areas and the column load
takedown.** Each column carries the slab of the level its top reaches; its tributary area is the
perpendicular-bisector cell of that slab (the half-bay rule on a grid, true bisectors off it);
dead and live kPa per level, set for the active level in Properties; loads taken down column on
column from the top; a Column Loads schedule with grid marks (B-2), D, L, D+L and 1.2D+1.6L, blank
where a level has no load; TRIBAREA draws the cells. No live load reduction, no self-weight,
columns only -- all labelled. Found on the way: level elevation, height and name are editable only
in a container that is never shown.

Phase 105 (V105), rooms 2: **occupant load and room colour fill.** Occupant
load per room from IBC Table 1004.5 (2018/2021), kept in published square feet with gross or net and
the m2 value derived; a room Load Factor the owner sets overrides it; occupants = area / factor
rounded up, blank when there is no factor, never 0. The room schedule and Properties show factor,
basis, source and load. ROOMCOLOR fills rooms by Department or Occupancy with a legend drawn from
what was painted; off by default, undoable, saved, and carried by plan SVG and sheet viewports.
Found on the way: room copy had dropped Comments since V101, and a Tab between room fields lost
the cursor. A first attempt at this phase divided by a persons-per-square-foot rate (100 m2 of
office = 14,286 people) and was discarded unshipped. Area plans moved to 105b.

Phase 104 (V104): **exports are where objects are, north up.** DXF, plan
SVG and sheet viewports apply position offsets; DXF and plan SVG are no longer mirror images
(DXF Y = -Z, bulges flipped; SVG y = +Z); DXF import is the exact inverse; sheet viewports frame
sketch-only plans.

Phase 103 (V103), site 1: **property lines from a survey, setbacks, true
north.** Parcels entered by bearing and distance with closure shown before OK, or made from a drawn
shape; per-side setbacks with the buildable area and live violation marks; True North setting and
a north arrow. Found on the way: exporters ignore moved objects' positions and DXF is mirrored --
now Phase 104.

Phase 102 (V102), structural 1: **foundations and a type catalogue.**
Isolated footings under columns and wall foundations under walls, each following its host through
move, resize, re-type, turn and reshape, deleted with it, detached and told when moved alone;
foundation slabs; beam and footing types; footing schedules with concrete volume; the three greyed
foundation buttons now work. Found on the way: every exporter drew turned columns axis-aligned.

Phase 101 (V101), first of Track B: **room data and room tags.** Rooms
carry a number (per level: 101.., 201..), department, occupancy and finishes; tags show them live
and can never disagree with their room; Tag Room (un-greyed on the ribbon) and Tag All Rooms work
from ribbon and command line; tags move with their room and go when it is deleted; the room label
steps aside when tagged, on canvas and in every export, and sits inside L-shaped rooms now.

Phase 100 (V100): **ending a drawing command keeps what was drawn.**
Escape, a plan/3D switch or starting another command used to throw away a LINE, PLINE or wall
chain in progress; now they keep it through the same finisher Enter uses. PLINE Enter ends the
polyline open, as AutoCAD. Found on the way: no drawing command was ever undoable. Fixed; a LINE
run is one undo step.

Phase 99 (V99): **a region follows every shape that bounds it.** A room,
hatch, floor, ceiling or roof traced from several shapes - walls, sketches, construction lines -
is linked in the relation graph to each of them and re-traces when any one changes; a shape
drawn across it, deleted from it or dragged into it is caught at `saveSoon()` by a plane
signature. An open boundary keeps the last shape and says so. Older multi-wall rooms are adopted.
Found on the way: a body drag teleported sketches and lines by their distance from the origin,
and consequence toasts were overwritten by the action's own summary. Both fixed.

Phase 98 (V98), taken out of order on the owner's report: **annotations
and grid lines could not be touched or edited.** A dimension or text label inside a room could
not be clicked, because the model was picked before the annotations drawn on top of it; angular,
radius, diameter and leader annotations could not be clicked anywhere; no annotation had grips;
and a grid could not be selected at all. Annotations are now picked first, every kind, where they
are drawn; each kind has grips that re-derive it; and a grid can be clicked, dragged by its ends
or its line, renamed, retyped, deleted, and selected from its Levels-panel row.

Phase 97 (V97) made **everything built on a boundary follow it**,
prompted by the owner testing the app: a room on a rectangle did not adapt as the rectangle's
vertices were edited. The graph already linked a room to its sketch; what broke was HOW it
re-measured - a curved sketch failed outright, a sketch moved before the room was made could not
be picked, and a room moved together with its sketch landed twice as far away. Floors, ceilings,
roofs and hatches did not follow at all: the source edge was room-only, and a roof that stored
its source was never linked to it. All five now follow through one reader of the source's
boundary, a detach is announced by name, and a sketch takes an ADDED vertex from a midpoint grip.
"Everything derived follows its source" is now standing law 7.

Driving the owner's scenario with the mouse found three more: the move gizmo swallowed the
midpoint grip on any symmetric shape, and both the grips and the gizmo were hit-tested from the
last paint, so a drag on a deselected sketch could still edit or rotate it.

Phase 96 (V96) shipped **HATCH and HATCHEDIT** and a real hatch object.
The Phase 53 pattern library turned out to be alive and wired into three sinks - the gap was
that it had no object to draw, no reachable command, and no ANGLE: direction was baked into
the tile names, so a hatch could not be set to 30 degrees. Pattern angle is now a real parameter
applied by one rotation function in every sink, with the sign that y-down drawing requires.

Found along the way: the SVG export of a Technical drawing dropped every hatch, because all
four sinks gated patterns on presentation mode and the new hatch branches inherited that gate
while the canvas - the one being looked at - did not. A material's own hatch angle was being
thrown away after choosing a tile name. And a duplicate test export silently shadowed the new
signature and dropped its angle argument.

Still not done, and stated: DXF writes a hatch's BOUNDARY only (R12 has no HATCH entity;
exploding the pattern into clipped LINE entities is its own phase). No GRADIENT - there is no
gradient renderer, and a command that opens a dialog and draws nothing is a decorative control.
A hatch has no hole, so a region with an island is covered and the toast says so.

Phase 95 (V95) shipped **BOUNDARY**, and with it the planar arrangement
the app has never had: every edge split at every crossing before the face walk runs, arcs
included, with the walk's angular key taken from the tangent rather than the chord. The face
walk itself was already there and correct since V22 - what was missing was the arrangement in
front of it, which is why room tracing had only ever worked on walls meeting end to end.

The V22 wall tracer is DELETED, not parked beside the new one, so Room, Floor and Ceiling
inherit three fixes: walls that cross now enclose a region, a curved wall no longer traces as
its chord, and a moved wall no longer bounds rooms from where it used to be.

It also found that the **entire BIM toolset was unreachable from the command line** - ROOM,
FLOOR, CEILING, ROOF, STAIR, COLUMN, BEAM, DOOR, WINDOW, SECTION and the gridline tool were all
ribbon-only. Third time this class has surfaced (V87, V90), and the third time a test wanting to
drive a tool is what found it.

Phase 94 (V94) shipped **XLINE and RAY** as real construction geometry:
stored as a root and a direction, clipped by one Liang-Barsky clipper for all four renderers,
snappable at their roots and at every crossing with a wall, a sketch or each other, and picked
where they are drawn. The extent they are drawn across is derived from the drawing, so the same
command works on a 3 m room and a 400 m bridge.

It also found that the letters **V, H and N have never reached the drafting workspace at all**.
Two separate Canvas-era guards, both registered on window in the CAPTURE phase at load and both
ahead of the BIM key handler, swallow plain letters - and in a CAD workspace H and V mean
Horizontal and Vertical. Both gates now ask the drawing whether it wants the key instead of
keeping a list of their own, and the letters a point-taking tool claims became one table that
the handler dispatches through and the gates query.

Phase 93 (V93) shipped **POLYGON, POINT, DIVIDE and MEASURE**, and made
CIRCLE a real circle — two vertices with bulge 1 instead of a 24-sided polygon that was out by
0.14 m2 on a 2 m circle. DIVIDE and MEASURE walk ARC LENGTH, so a mark on a quarter circle
lands at the sweep midpoint and not 0.414 m away at the chord midpoint. Two real bugs fell out
of making the circle exact: the viewport had been drawing every committed arc as its CHORD
since V88 (drawSketchPath was handed `o.pts` unflattened while the rubber band that produced it
flattened), and five consumers read `o.pts` as the outline, which a two-vertex circle turns from
a quiet approximation into a hard refusal. Both fixed as classes.

Phase 92 (V92) taught **Extend and Lengthen** curves through one shared
"grow the end" operation — on an arc the sweep changes while the centre and radius stay put.
Five of the eight modify tools now handle curves.

Phase 91 (V91) taught **Trim and Break** curves, on one implementation
that replaced the straight-only versions rather than sitting beside them — and deleting those
turned up a real bug within one run, because a piece cut exactly at an endpoint has two identical
points and a vertex-count guard accepts it.

Phase 90 (V90) made curves DRAWABLE — `A` switches WALL and PLINE into
arc segments and `L` back, each arc leaving the run tangent to the segment before it — and taught
**Offset** to produce concentric arcs. Also found and fixed that WALL was not reachable from the
command line at all.

Phase 89 (V89) made wall centerlines curve and gave **FILLET a radius**; wall length became arc
length in the same phase, because a schedule reporting the chord is quietly wrong.

Phase 88 (V88) settled the arc-storage question — **bulge factor per vertex**, DXF group code
42, an optional `bulges` array parallel to `pts` where absent means straight. Detail in
`claude/canvas_v10_STATUS.md`.

Phase 87 (V87) shipped EXTEND, BREAK, BREAKATPOINT, LENGTHEN, CHAMFER, SCALE and FILLET-at-0,
made ROTATE / ARRAYRECT / ARRAYPOLAR / ALIGN / JOIN reachable from the command line for the
first time, and fixed the typed-coordinate class bug.

**Small, unscheduled, do when convenient:**

- Make F8 ortho constrain the *rubber band*, not just the snap. Roughly an hour, and it finishes
  the V86 command line.
- Thirteen legacy suites (`bim_phase28`–`bim_phase40*`) hardcode
  `file:///home/claude/canvas_v10.html` and take no argument, so they cannot run against a named
  build. One line each.
- Openings are not re-hosted onto the second piece after a Break.
- Level elevation, height and name can only be edited in #a3d-lvlrows, which is display:none, so
  in the visible UI a level cannot be renamed or moved. Found in V106, which put floor loads in
  Properties for that reason. Needs a visible level editor (Properties with nothing selected is
  the natural place, beside the level picker).
- Terrain, not yet: breaklines and a boundary (the TIN covers the convex hull of the points);
  terrain in 3D views; contours in DXF and SVG exports.
- V105-V107 put literal non-ASCII (the squared and cubed signs, an em dash) into labels and
  toasts; convert them to \u escapes. V108's patch scripts escape inserted text by code.
- The gizmo's pivot drag and plane handles use the ground plane in every flat view
  (`bimGizmoBeginPivot`, the plane pick), so in an elevation they act on an edge-on plane. The fix
  is the view plane, not `bimCameraIsPlan`. Found in V119.
- Fit to Model does not count grids, so a model of grids alone fits to nothing. Found in V119.
- The project title at the top of the left panel is clipped by the panel's first row in every tab
  (the Assets tab's search box, the Project Browser's first group). Seen in V124; V123 is the same.
- ROTATE's dialog is labelled "Angle (degrees, CCW)" and a positive angle turns the plan
  CLOCKWISE; the V110 gizmo reads angles the Revit way (positive is counter-clockwise seen from
  above), so the two disagree. The sign belongs to ROTATE, the polar array's fill angle and the
  column rotation property together, with tests, not to one dialog.

---

## NEXT — Track B, the object model

Items 1 to 3 were built in V125 to V127; item 4 is in NOW.

The command audit's central finding: implementing all 902 AutoCAD commands would still leave MEP,
HVAC and civil alignment work **entirely unbuilt**. The object model is where the discipline value
actually is.

1. **Structural object model** — loads, supports, load combinations, results. `TYPE_CATS` still
   covers wall/floor/ceiling/column only.
2. **Section-profile library** — steel sections, reinforcement, bolt patterns.
3. **Alignment / profile objects** — horizontal alignment, vertical profile, station-offset.
4. **Connector-based MEP objects** — ducts and pipe as connected runs with size and flow.

**Items 1 and 2 are the common prerequisite for three separate things**: the ARCH5 port, the
PennDOT input writer, and any real structural work. Build them once, three things unblock.

A linear-elastic 3D frame solver (the STAAD-equivalent) IS item 1 — direct stiffness method,
textbook math, bounded scope, validates against closed-form solutions. Most tractable major piece
on this whole list.

---

## ALSO READY — DXF, no dependencies

**DXF export then import.** R12 ASCII. Published format; both AutoCAD and MicroStation read it.
Days, not weeks, and it stops work being trapped inside the app. Can slot in anywhere.

---

## PARKED — PennDOT bridge engineering (Track C)

**Deliberately later.** Scoped and documented so it can start cold whenever wanted.

- **Blocked on nothing technical.** The input formats are published: PennDOT's official manuals are
  free and public at `penndot.engrprograms.com`, and Chapters 5/6 document the command records
  field by field. 44 commands for PSLRFD, 57 for STLRFD, **23 shared between them**.
- **What's needed to start:** run `reference/penndot/fetch_manuals.sh` to pull the PDFs, then
  extract the field definitions. Also worth grabbing one real `.dat` input file plus its output
  from a past job — that's the validation fixture and settles the format question from the artifact
  rather than the manual.
- **Recorded trap:** `DPL` means "Drape Point Location" in PSLRFD and "Design Plate Location" in
  STLRFD. A code table keyed only on the three letters emits a valid-looking, wrong file.
- **Build order when it starts:** output parser first (needs only a sample output file, no format
  docs, delivers automated rating reports immediately) → generic command emitter → shared core →
  per-program member modules.
- **Depends on Track B items 1 and 2** for the loads and sections it has to write.

**Also parked:** the ARCH5 port. `ENGPROG/in-house/arch5.for`, 1,424 lines of FORTRAN, the firm's
own RC arch rib load-rating program, rights confirmed. `ARCH527.OUT` is a worked example with
published answers (inventory RF 2.52, operating RF 4.20, 207.4 / 346.3 tons) — the port isn't done
until the JS reproduces them. Same Track B dependency.

**Out of scope permanently:** reimplementing or reverse-engineering the licensed programs — PennDOT
suite, STAAD, MicroStation, CSiBridge, AASHTOWare. Confirmed there's no source to copy in any case;
they ship as compiled binaries.

---

## Where the detail lives

| Doc | What's in it |
|---|---|
| `claude/canvas_v10_STATUS.md` | Full phase history from V60 on, every bug and its lesson, per-phase scope. Large — search it, don't read it start to finish. |
| `claude/roadmap-autocad-command-coverage.md` | All 902 AutoCAD commands scored against the five disciplines, with coverage counts. |
| `claude/penndot-official-documentation.md` | PennDOT program inventory, licensing, verified manual URLs. |
| `claude/penndot-input-spec.md` | The input command inventory for PSLRFD and STLRFD, shared-core analysis, model-data mapping. |
| `reference/penndot/fetch_manuals.sh` | Pulls the public manuals down. Run on any machine with normal internet. |

## Standing rules

- **Research to the protocol** (the owner, 2026-10-17: "the more careful research the better"):
  `reference/research-protocol.md`. Every fact the code uses is read in its primary source, or a
  dependable secondary one with the gap said; search summaries are pointers, never sources.
- Every phase ships with a browser test suite, **falsified against a deliberately broken build**
  carrying the phase marker before it's trusted.
- Assert on the **model**, not on appearance. The V86 lesson: a palette that looked perfect and did
  nothing passed every appearance check for as long as it existed.
- **Claim a control only after driving it** (the V85 lesson — a whitelist entry taken on faith is
  worse than no whitelist).
- Never hand-list what can be derived (V74; applied again in V86 to prompt strings).
- Full regression before shipping; commit to the Mac and verify by hash.
- An overlay is "shown" when it is what the pointer hits: assert `elementFromPoint`, not a class (V115 --
  the Start page was under the drawing area for a whole phase while its suite passed).
- Never touch localStorage from a Playwright init script on a `file://` page: about half the time it cuts
  the page's storage off from the browser and a reload finds nothing (V115, measured 4 of 8). Seed stored
  state from a blank page on the same origin, with the app closed.
- A flaky failure needs a rate, not a run: measure each side several times before naming a cause (V115).
- "Used" means something could reach it: a CSS name is live where an element can be given it, not where
  the word appears (V120 -- a toast saying "the viewport" kept the whiteboard's `#viewport` for seven
  phases). The V120 suite derives dead rules, unread custom properties and unused functions this way.
- When a control goes, grep every selector that named it: an opener's contract includes its closer
  (V120 -- the dock's User Interface entry did nothing from V70 on because the close handler named only
  the removed button). The V120 suite checks that every `[data-x="v"]` in the code names a live control.
- A look the painter decided is not a line on the canvas: where drawing is the claim, measure the pixels
  (V121 -- a painter that ignored the lineweight passed every check that read the decision).
- When two mechanisms cover a case, test the case only one of them covers, or removing either passes
  (V121 -- a locked layer leaves the selection twice over; a layer turned off only once).
- A render that borrows the live paint clears everything the live paint draws for the person at the
  screen, listed from what the draw functions read, not from memory (V122 -- sheets drew the model's
  selection from `A3D.selSet` for as long as they had viewports).
- A second resolution is a backing scale on one layout, never a second layout (V122 -- a sheet at
  6 px/mm drew every pixel-sized text at half its size on the paper).
- A catch that keeps a page drawing keeps its fault quiet: test the pixels behind it (V122 -- every
  schedule on a sheet had been a grey box and a console line).
- A rebuild owns only the geometry it writes. Every other field of an element's record is carried by
  `bimCarryBim`, never listed by the caller (V123 -- eleven rebuild and copy paths had eleven lists, and
  a wall's type fell out of most of them).
- A press is not a gesture until it moves: the undo step, and any copies, are made by the first
  movement past the click distance (V123 -- a click on a handle added an empty undo step, and
  Ctrl+click an invisible copy).
- What a face means is the object's decision, never the mesh's (V123): a box's top is its Height, a
  wall's side its type's thickness.
- The browser delivers pointer positions in whole pixels: aim a drag at whole pixels and compute the
  expectation from what was sent. Undo depth stops at `UNDO_MAX`: a suite that counts undo steps starts
  each scene from an empty history (V123).
- A suite never waits without a bound, and never ends without a RESULT line: every page step has
  STALL seconds, and a stall or an exception is a FAIL naming where it stopped. The falsify runner
  reports a hung variant as TIMEOUT instead of cancelling every variant still queued (V123 -- its
  first falsify run reported nothing).
- A fallback masks the fault it backs up wherever it happens to be right: test the case it gets wrong
  (V123 -- a copy that lost its type had it re-guessed from its size, right for every type of a
  unique size).
- A fixture is what its computed property says, not what it is called (V123 -- the "inside-out" test
  cube ran outward, and the outward-normal code went untested). Press where only the gesture under
  test answers: at an object's centre a press is the gizmo's.
- Time is measured in the page, where it happens: a slow suite reads late, never early (V123).
- A copy is a new object: every link it holds is decided when it is made -- pointed at what was copied
  with it, or dropped and said -- read from the ORIGINAL record, never inherited by copying the record
  (V124 -- a copied hatch re-traced onto the original's sketch since V99; `bimRelinkCopies` is the one
  rule for every copy path).
- Suppress the one event you mean by when it is dispatched, never by a window of time: a time window
  eats whatever the user does next (V124 -- a click after a drop was lost for 400 ms).
- A new state that Escape ends is a line at the head of `onKey`'s chain, not a listener of its own:
  `onKey` is registered at load and stops Escape for anything selected (V83, and again in V124).
- A fixture that is symmetric agrees with a wrong rule by accident: a member along the model's axes
  has a rotation matrix equal to its transpose, so a transposed turn passed every check (V125). Test a
  member turned off the axes.
- Where an extreme can be found exactly, find it: a sampled maximum is a lower bound that reads as the
  answer (V125 -- a moment's peak is where its shear passes zero).
- A form in a panel that can re-render under it keeps its state outside the DOM, read before any
  handler can re-render (V125 -- a typed load value was lost).
- New features fit the existing interface first: Properties pages that follow the selection, a
  command and its Off form for a display, one toolbar button (owner, V125; Rhino's model).
- A square section is a symmetric fixture, and so is a bounding box: check a turn on a section that
  is not square, and check that a rebuild kept its shape by the solid's volume, not by its extent
  (V126).
- Count the variants the falsify runner ran against the number written: it reads lower-case names
  only, and a skipped variant reads as caught (V126 -- six were skipped).
- One reader for a derived quantity: the solid, the analysis, Properties and Assets all read a
  section through `bimProfileProps` and `bimMemberSection`, so they cannot disagree (V126).
- A fixture must need the rule it tests: an alignment whose legs left room for a 142 m curve could
  not tell whether the 100 m default respected its legs (V127). Pick the fixture the rule binds on.
- An edit is made to a copy and checked before it is kept: a number that would break the model is
  refused by name and never reaches it (V127, `bimAlignEdit`).
- Every command is found in one place: a new typed command goes in `CADCMDS`, a new tool in the
  ribbon registry, and the command search (`bimCmdCatalog`) picks up both. Give it search words in
  `BIM_CMD_TERMS`, and a chord in `A3D_KEYS` (with `cmd`) if it has one (V128).
- Nothing listens for a plain letter on the drawing except type-anywhere, which asks
  `__a3dTypeAnywhere` first. A new state that takes letters must make that test refuse (V128).
- When a phase changes how a value is read, remove what still writes the old one: V126 took a
  member's section from its profile and left its `hy` and `hz` written for nothing until V166c, found
  only because a falsify variant that swapped them stopped being caught.
