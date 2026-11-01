---
title: Sheets and files
order: 8
---
# Sheets and files

## Sheets

- **Layouts:** `LAYOUT` adds a sheet layout with viewports. `TITLEBLOCK` edits the title block.
- **Model and paper space:** `MSPACE` and `PSPACE` switch between them.
- **Presenting:** the **Presentation** tab on the left rail lists the pages of the set, with their
  thumbnails. From there you can present them full screen or print the set.
- **Boards in the set:** **+ Board** adds a board of the site analysis as a page: Climate and risk,
  Zoning and yield, or Access and people. Analyze's **Show in Presentation** does the same.
  - A board's page opens in the main view, with the panels beside it, and lays out by the room it
    has. **Esc** gives the drawing back.
  - Drag a board to move it among the sheets; the sheets keep their own order, as the layout tabs
    show it. Right-click it to present from it, print it alone, move it or remove it from the set.
    Its data stays in Analyze.
  - **Present** shows it as on screen; the wheel scrolls it to its end, then goes on to the next
    page. **Print set** prints it on A3 landscape pages of its own, in its place in the set.
- **Printing one sheet:** `PLOT`.

## Arranging a board

A board's **Edit**, on its bar, arranges its figures, as a sheet's viewports are arranged:
- Drag a figure by its handle or its body; size it by its corner. **Snap**, **Grid** and **Ortho**
  are the drawing's own (F3, F9, F8) and govern it: Snap catches an edge on another figure's or the
  board's, Grid puts the edges on the board's 12 columns and on rows of the same step, Ortho keeps a
  drag straight across or straight down.
- The arrow keys move the figure in focus; Shift and the arrow keys size it; Delete removes it.
- A figure's menu (its button, or a right-click): **Options** (its title; the chart, its numbers as a
  table, or both; UTCI's condition), **Fit the height to its content**, **Duplicate**, earlier or
  later in reading order, **Remove**.
- **Add a figure** lists every analysis the project has, from any board, each with its preview; it
  goes below the others at its own width.
- **Reset** gives one of the three boards its own figures in their own places again.

Each change is one undo step and is kept with the project. A board not yet arranged keeps its own
layout. Once it is arranged, figures of its own that come later, with new data, wait below the others
until placed. Present, Print set and the thumbnail show a board as arranged. On a phone its figures
are in reading order, and each one's menu moves it earlier or later.

**+ Board**, then **New board**, makes a board of your own: name it in Edit, then add any analysis to
it. A board's menu in Presentation duplicates it as a new board, and deletes a board of your own
(Ctrl+Z brings it back).

## Exporting

| Format | Command |
|---|---|
| PDF | `EXPORTPDF` |
| PNG image | `EXPORTPNG` |
| DXF (for AutoCAD and others) | `EXPORTDXF` |
| SVG | `EXPORTSVG` |
| GeoJSON | `GEOEXPORT` |
| CityJSON 2.0 | `CITYJSONOUT` |
| the project file (.json) | `SAVE` |

## Importing

| Format | Command |
|---|---|
| DXF, IFC, OBJ, STL | `IMPORTCAD` |
| IFC as a linked model | `LINKIFC` |
| GeoJSON, KML | `GEOIMPORT` |
| CityJSON | `CITYJSONIN` (or `IMPORTCAD` with a `.city.json` file) |
| SketchUp (.skp) | `SKPIN` (or `IMPORTCAD` with a `.skp` file) |
| survey points | `SURVEY` |
| a project file | `OPEN` |

DWG, STEP and IGES are not read: export DXF or IFC from the other program instead.

### SketchUp files

`SKPIN` (also `IMPORTSKP` or `SKETCHUP`) opens a `.skp` file from any SketchUp, including SketchUp
2021 and later. The file is read by openskp's reader (MIT), which is built into the page, so nothing
is uploaded. The model comes in where it was drawn, in metres:

- **Faces.** Each group or component, in each of its materials, is one locked solid. Faces drawn
  loose in the model are one solid per material, for example "Concrete faces". A face is brought
  in once, even when its back is painted a colour of its own.
- **Tags.** The file has a layer of its own, named after the file. Each tag is a sub-layer of it,
  for example "site_kit - Walls", in the tag's colour. A tag that was off in SketchUp is off here.
  Untagged faces go on the file's layer. Opening the same file again uses the same layers.
- **Materials.** Each solid takes its material's colour. A textured material takes the colour
  SketchUp keeps with the texture (the image's average, which SketchUp's Shaded style shows). The
  texture's file is named in Properties. An unpainted face is SketchUp's white.
- **Glass.** A see-through material goes on a sub-layer of its tag at the material's transparency,
  for example "site_kit - Windows - 65% see-through". This app keeps transparency on layers.
- **Components.** Each component that has a name is kept in **Assets** → **Blocks** as a block
  from SketchUp, with what is inside it. It is kept in its own frame, and its insertion point is
  the block's base point. Groups, and components left with SketchUp's own name (Component#1), stay
  in the model only. Opening the same file again replaces its blocks.
- **Properties** → **SketchUp** shows where a selected object came from: the file and the SketchUp
  that saved it, its component or group (and what it is inside), its tag, and its material.
- **Undo.** The whole file is one undo step. The blocks stay in the library, which is kept apart
  from any project.

The library's **Import** in **Assets** also takes a `.skp` file. It keeps the file's components as
blocks and places nothing.

Limits: 250,000 triangles a file; a block of up to 6,000 triangles, and as many blocks as fit in
the library's storage. Each limit says when it is reached. A file the reader cannot read is
refused, with the reader's reason. Some very old files (SketchUp 3) are among these.

## Versions and history

The project keeps its own history, element by element. It works like git, at the grain of a
building element.

**Commit.** Properties → **Project** → **History** (or `HISTORY`) lists what has changed since the
last version. Each element that was added, removed or changed is listed. A changed element is
listed field by field, for example "moved by 1, 0, 2", "name: "Site" → "North Lot"", or "Level 1
added". Type a message and press **Enter** or **Commit** to keep the model as a version. `COMMIT`
puts the cursor in the message.

**What a version stores.** Every object is an element, by its id. So are the project's other
parts: levels, grids, layers, types, sheets, the title block, buildings, the site,
classifications and saved views. Each element is stored once, by a hash of its content. A version
therefore adds only the elements that changed, and identical content is kept once.

**Looking back.**
- **Changes**, on a version, opens what that version changed.
- **Restore** brings the model back as it was at that version. It is an edit like any other: Undo
  takes it back. The history itself is never rewritten. Commit afterwards to keep the restored
  model as the latest version.
- **Discard Changes** goes back to the latest version.

An element's own Properties show its **History**: the versions that added, changed or removed it,
and what changed each time.

The history is saved with the project, in the browser and in the `.acad3d.json` project file.

### Design options: branches

A **branch** is a name at a version: one design option. Every project starts on **main**.

- **New branch.** In History, type a name in *New branch* and press **Enter** or **New Branch**
  (or `BRANCH`). The branch starts at the latest version and you are put on it. Changes not yet
  committed come along. A name is letters, numbers, spaces, dots and dashes, up to 40.
- **Switch.** Pick a branch in the **Branch** list. The model becomes that branch's latest version,
  and Undo takes the switch back. Commit or discard your changes first, so nothing is lost.
- **Commit** moves only the branch you are on. The version list shows that branch's line: its own
  versions and the ones it shares, with each branch's name on its latest version.
- **Compare** (or `COMPAREBRANCHES`) puts each branch's numbers side by side: objects, walls and
  their length, doors and windows, rooms and their area, gross area, levels, cut and fill. Rows
  that differ are in bold. The branch you are on is counted as the model is now, committed or not.
- **Delete** removes the branch picked in the list beside Merge In. It asks once first; the branch
  you are on cannot be deleted.

### Merging

**Merge In** (or `MERGE`) brings the picked branch's work into the one you are on. The app finds
the version both branches share and compares each element three ways: as it was there, as it is
here, and as it is on the other branch.

- If this branch has nothing new, it simply moves up to the other branch.
- If this branch already has everything, nothing happens.
- Otherwise each element that only one side changed is taken from that side. Where both sides
  changed the same element in different fields (one moved a column, the other renamed it), the
  fields are put together.
- A **conflict** is the same field changed both ways, or an element deleted on one side and
  changed on the other. Conflicts are listed in History with the two sides next to each other.
  Choose **Keep** (this branch's) or **Take** (the other's) for each, then **Finish Merge**.
  **Cancel** leaves the model as it was.

A finished merge is a version with two parents, so the next merge between the same branches starts
from it. Branches are saved with the project; a project from before V151 opens with its history
on main. On a phone or a tablet, `HISTORY`, `BRANCH`, `MERGE` and `COMPAREBRANCHES` open the
Properties sheet at History.
