---
title: Site and context
order: 4
---
# Site and context

## Putting the project on the earth

The project's model 0,0 sits at the site's **latitude and longitude** (**Properties > Site >
Location**). To set it:
- type the latitude and longitude there; or
- run `FINDADDRESS` and search OpenStreetMap's Nominatim. It runs one search per press, as
  Nominatim asks.

`TRUENORTH` turns the model to true north.

## The map

`MAP` steps through the basemaps:
- off;
- street map (Esri World Street Map);
- satellite (Esri World Imagery);
- your own tiles.

Each map's credit is shown on the drawing. Tiles are cached in the browser.

## Property lines

- `PROPERTYLINE` draws a property by its bearings and distances.
- `PROPERTYFROMSHAPE` makes one from a drawn shape.

Setbacks follow the property.

## Site context in one click

`CONTEXT` fetches what is around the site, in one undo step:
- **From OpenStreetMap (through Overpass):** buildings, roads, water, green areas and trees.
- **From AWS Terrain Tiles:** the ground.

Buildings come in at their height and stand on the ground. Where OpenStreetMap has roof tags or
building parts, they get them: see [Buildings and LOD](buildings-lod.html).

**Properties > Site > Site Context** sets:
- the radius;
- the kinds to get;
- the Overpass server.

`CONTEXTREMOVE` takes it all away.

## Data layers

`DATALAYERS` adds public GIS data around the site: parcels, zoning, flood zones. A layer can be:
- an ArcGIS REST layer;
- a WFS;
- a GeoJSON file.

Click a feature on the plan to read it. `FINDDATA` searches US city, county, state and federal
open-data portals for layers to add. A server that does not allow browser access is named; the
app never routes around it.

## GeoJSON and KML

- `GEOIMPORT` brings in GeoJSON or KML as site data, placed by longitude and latitude.
- `GEOEXPORT` writes the plan as GeoJSON.

## Sun and shadows

`SUNSTUDY` shows the shadows and the sun path for the site's date and time. They are set in
**Properties > Site > Location**. The sun's position follows NOAA's equations.

## Alignments

- `ALIGNMENT` makes a selected polyline a road alignment.
- `STATION` reads station and offset along it.
- `PROFILEVIEW` places its vertical profile.
