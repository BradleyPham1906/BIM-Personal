---
title: Survey and terrain
order: 5
---
# Survey and terrain

## A surface from survey points

`SURVEY` reads survey points and builds a terrain surface (a TIN) with contours.

**What it reads:**
- point files in PNEZD, PENZD or XYZ order, from a file or pasted in;
- metres or US survey feet;
- an elevation at model 0.

**Check shots.** Points whose description starts with the check code (CHK by default) are kept
out of the surface and measured against it.

**Earthwork.** The surface gives cut and fill against building pads.

## Verify every survey

`SURVEYCHECK` checks a surface, and its Survey Check group in Properties shows each check with a
pass, warning or failure:

| Check | What it looks at |
|---|---|
| read | lines that could not be read, by number |
| duplicates | points with the same name |
| through every point | the surface passes through every point, to 1 mm |
| triangles | no triangle without area |
| bust shots | points far from the plane through their neighbours |
| check shots | RMSE of the check shots against the surface |
| control | points whose elevation you know, typed as name=elevation, to 2 cm |
| public terrain | the offset from the public terrain, and feet read as metres |

**Export Report** writes the result as a page to keep with the survey.

## The terrain in 3D

In 3D views, the surface is drawn shaded with the basemap draped over it. Context buildings stand
on it.

## Breaklines

A breakline is a line the surface must follow: a ridge, a ditch, the top or toe of a bank, a kerb.
Without one, the triangles join whatever points are nearest and can cut across the line.

**From the drawing.** Draw a polyline over the surface, select it (and the surface, if there are
several), then run `BREAKLINE`. Each segment is forced into the triangles. Where the line meets
ground between survey points, a vertex is added at the height the surface already has there.

**From the survey.** Points whose description starts with BL or BRK and a name (BL1,
BRK-ridge) are joined, in file order, into one breakline per name. They keep their own
elevations.

Lines that cross each other get a shared vertex where they cross, so both are held. A segment that
cannot be held is named in the message and in Properties.

## The boundary

`TERRAINBOUNDARY` trims the surface to the selected closed polyline. The boundary is held like a
breakline, and the triangles outside it are dropped. The survey points outside stay in the survey
but are left out of the surface. The survey check counts them and does not treat them as errors.

## Slope, elevation and aspect

Properties of a surface → **Terrain Analysis → Colour By** colours it in plan, with a legend and
the area in each band.

| Colour By | Bands |
|---|---|
| Slope | 0–2%, 2–5%, 5–8.33% (1:12), 8.33–15%, 15–25%, 25–50%, 50% and over |
| Elevation | seven equal steps from the lowest point to the highest |
| Aspect | flat (under 2%), then north, north-east ... north-west: the way the ground falls, measured from True North |

Each triangle is measured on its own plane, and its plan area goes to its band. The same commands
are `SLOPEMAP`, `ELEVATIONMAP`, `ASPECTMAP` and `TERRAINANALYSISOFF`. Each works on the selected
surfaces, or on every surface when nothing is selected. The Terrain card in the **Analyze** tab
does the same.

## LandXML

LandXML 1.2 is the open exchange format of civil design and survey software.

**Out.** `LANDXMLOUT` writes every surface (or the selected ones) with:
- its points, back in the survey's own northings, eastings and elevations and in its own units;
- its triangles;
- its breaklines and boundary, as source data.

**In.** `LANDXMLIN`, or `IMPORTCAD` with a `.xml` file, reads each TIN surface.
- The file's own triangles are kept. Faces marked invisible are left out, and every face is turned
  to the same winding.
- The surface is placed by the site's survey base. With no base, the first point becomes the base.
- Feet and US survey feet are converted. Millimetre files are not read yet.

**Re-triangulate** in Properties drops the file's triangles and triangulates the points again.
