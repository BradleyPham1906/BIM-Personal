---
title: Buildings and LOD
order: 6
---
# Buildings and LOD

Neighbouring buildings come from OpenStreetMap with `CONTEXT`, or from a CityJSON file with
`CITYJSONIN`. Each one says its **level of detail** (LOD) and how it was made, in its LOD group in
Properties.

## The levels

| LOD | What it is | Made here from |
|---|---|---|
| 1.2 | the whole footprint, extruded to one height | an OSM building's footprint and height (or levels x 3 m) |
| 1.3 | a building split into parts, each at its own height | OSM's building parts (`building:part`, `min_height`, `height`) |
| 2.0 | the roof's shape on walls straight up from the footprint | OSM's roof tags |

## Roofs from OpenStreetMap

When a building has `roof:shape`, it gets that roof. Every roof is made of flat planes, never a
smoothed surface:
- **hipped:** a straight skeleton over any footprint;
- **gabled, half-hipped, gambrel, mansard, skillion:** planes rising from the eaves, on a convex
  footprint;
- **pyramidal:** a triangle from each edge to one apex;
- **flat.**

**Roof height:** `roof:height`, else `roof:levels`, else `roof:angle`, else an assumed 30 degrees.
`height` is the whole building and `building:levels` counts the walls.

**Ridge direction:** along the longest side, unless `roof:orientation=across` or `roof:direction`
says otherwise.

**Roofs not built.** Curved roofs, and ridged roofs on a non-convex footprint, keep the LOD1 block
and say why.

## Checking the solids

`LODCHECK` checks every building, following val3dity's rules. Each building must be:
- closed;
- turned outward;
- made of faces flat to 1 cm;
- in one piece.

It selects the first building with a problem.

## CityJSON

- `CITYJSONOUT` writes the buildings as CityJSON 2.0:
  - in the site's UTM zone, heights above sea level;
  - building parts as BuildingParts under their Building;
  - surfaces typed roof, wall and ground;
  - OSM's credit in the attributes.
- `CITYJSONIN` reads a CityJSON file (`.city.json`), taking each object's highest LOD:
  - UTM files land on the site;
  - files in other grids are placed by their centre, and the grid is named.
