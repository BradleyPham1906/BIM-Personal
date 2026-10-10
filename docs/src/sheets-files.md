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
| survey points | `SURVEY` |
| a project file | `OPEN` |

DWG, STEP and IGES are not read: export DXF or IFC from the other program instead.

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
