# canvas_v10 — the pipeline

**Read this first in a new session.** One page. The detail lives in the docs listed at the bottom.

    canvas_v10.html   1,787,923 bytes
    sha256            8d5857417d52274ebe35817b5eedc47866b3f07df62aed64cfaffcdb572459b8
    markers           __acad3dV60 ... __acad3dV130, plus __acad3dV105b, __acad3dV113b, __acad3dV113c,
                      __acad3dV121b
    tests             86 suites, 3008 checks, 0 failures

    Run the regression in parallel: tests/run_all.py [build] [filter] [-jN], default -j6,
    about 4 minutes; give it the build's absolute path. tests/falsify_all.py
    <falsify_phaseNN.py> <suite.py> [-jN] proves every broken variant is caught: a minute for a
    small suite, seventeen for V123's (56 variants of a 108-check suite); a suite that hangs on a
    variant is reported TIMEOUT. Every current suite is in tests/, the folder the runner reads;
    commit new and amended suites there. Patch and falsify scripts, and each phase's pre-phase
    backup, are in Phase/. The suites need Playwright's Python package and Pillow (V116's reads
    pixels) -- in a fresh container, pip install playwright pillow before the baseline run.

Start every session by verifying that hash and taking a backup. Never output the whole file; patch
with anchored Python scripts that assert exact match counts.

---

## NOW - Giraffe's ideas and the map, then the MEP runs (V131 to V138)

The owner looked at Giraffe (giraffe.build), a map-first feasibility app, and chose four of its
ideas, ahead of the MEP runs, then asked for the map "just like how giraffe do". The research, with an
inventory of everything Giraffe does against this app, is in `reference/research-giraffe.md`.

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

**Design rule (owner, V125):** keep the interface clean and consistent, following Rhino's model
(see `reference/research-structural-ui.md`).
- Settings are Properties pages that follow the selection.
- An analysis is a display turned on and off by its command.
- A feature adds a window, rail tab or toolbar strip only when no existing one can hold it.

| # | Phase | Scope | Notes |
|---|---|---|---|
| 131 | Usages and live areas | A usage (Residential, Retail, Office...) on rooms and masses: a colour, GBA→GFA→NSA efficiencies, and simple formula properties (`GFA * rate`) with our own evaluator (not HyperFormula, which is GPLv3). Defined once and edited in Properties. A live area table for the selection, by usage and level | **Start here.** Giraffe's Usages (`reference/research-giraffe.md`). Research first: area definitions (GBA, GFA, NSA, and IPMS / BOMA / local equivalents) and Revit's Area Schemes. Builds on rooms, Areas by Level and the schedules. |
| 132 | The map | Street and satellite basemaps under the plan and the 3D ground, placed by the project's latitude, longitude and true north and drawn by our own renderer; address search (Nominatim); a cached tile store and an attribution footer; GeoJSON/KML import of parcels and GeoJSON export | The owner: "just like how giraffe do", free only, "as much open public data as possible". Sources, licences and rules: `reference/research-open-data.md`. No API keys; offline-first. |
| 133 | Site context in one click | From the site's extent: OSM buildings (at their height, or levels × 3 m), roads, water and trees via Overpass, as locked context; terrain from AWS Terrain Tiles into V108's TIN | Microsoft and Overture footprints as file imports where OSM is thin. |
| 134 | Data layers | A Data section: catalogue presets (council parcels and zoning, FEMA flood...) plus any ArcGIS REST, WMS, WFS or GeoJSON URL; click to read a feature; a parcel becomes a property line | Giraffe's data layers. A server without CORS is reported by name. |
| 135 | Zoning envelope | Setbacks, stepbacks and a height limit on a property become a 3D envelope; massing outside it is flagged | Builds on V103's setbacks; Giraffe's Basic Envelope. |
| 136 | Colour-by-property lens | Colour by usage, level, type or any property, with a legend, under Appearance | Giraffe's lenses; Revit's colour schemes. |
| 137 | Design scenarios | Options within one project, switched between and compared by their numbers | Giraffe's scenarios; Revit's Design Options. |
| 138 | MEP runs | Duct and pipe runs at connectors, systems, flow, velocity and friction | MEP is its own discipline (the owner's choice). The research is drafted in `reference/research-mep-runs.md`. |
| later | Generators | Parking layout to a ratio, subdivision into lots, and envelope-filling massing | Giraffe's generative editors; after the map and the envelope. |
| later | Costs and pro forma | Cost, rent, yield and sale price per usage, and a feasibility summary | Builds on V131's formulas. |
| later | Flows and an app SDK | Per-object node graphs (Giraffe's Flows, a light Grasshopper); a documented plugin API of read-only state snapshots with listeners and named commands over postMessage | The engine's `__a3dRegisterCommand`, `__a3dRegisterDiscipline` and `__a3dRegisterTab` are the start of it. Giraffe's model: one set of functions reached two ways, the browser console and a postMessage bridge for an iframe app in the right panel, over GeoJSON-like data (`reference/research-giraffe.md`). |

### LATER - Track A, drafting (moved behind Track B in V100)

The numbers in this table are its order, not phase numbers: a phase takes the next free V number
when it starts (V111 to V130 went to other work; V131 to V138 are in NOW).

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

**Recently finished:** Phase 130 (V130), **every tool in one panel, and a dock of the few used
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
