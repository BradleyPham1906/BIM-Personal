---
title: Sheets and files
order: 8
---
# Sheets and files

## Sheets

- **Layouts:** `LAYOUT` adds a sheet layout with viewports. `TITLEBLOCK` edits the title block.
- **Model and paper space:** `MSPACE` and `PSPACE` switch between them.
- **Presenting:** the **Presentation** tab on the left rail lists the pages. From there you can
  present them full screen or print the set.
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
