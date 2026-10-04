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
