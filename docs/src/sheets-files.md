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
