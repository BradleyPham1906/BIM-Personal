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
- **From OpenStreetMap (through Overpass):** buildings, roads, water, green areas, trees,
  railways, airports, power lines and land use.
- **From AWS Terrain Tiles:** the ground.

Buildings come in at their height and stand on the ground. Where OpenStreetMap has roof tags or
building parts, they get them: see [Buildings and LOD](buildings-lod.html).

The rest comes in 3D too. Each keeps its line or outline, which you can select and snap to, and
carries a surface:

| Kind | In 3D |
|---|---|
| Roads | A strip as wide as the `width` tag, or its lanes at 3.3 m each, or a width for its class. Coloured by use: car road, pedestrian zone, footway, cycleway or path. |
| Bridges | A deck 0.8 m thick, 6 m up for each `layer` (at least one), on piers every 30 m. |
| Tunnels | The centre line only, named "Tunnel: ...". Nothing is drawn on the ground. |
| Railways | Rail, light rail, subway and narrow gauge 3.2 m wide; tram 2.6 m. A platform stands 1 m high. |
| Airports | Runways 45 m wide and taxiways 18 m, or as tagged. Aprons and helipads are paved. The aerodrome is its boundary. |
| Trees | A trunk and a crown, as tall as the `height` tag, else 8 m. A tree row puts a tree about every 8 m, from end to end. |
| Power | Pylons 25 m tall, or as tagged. The line is drawn 20 m up. |
| Land use | Residential, commercial, retail, industrial, railway and construction land, as a tint on the ground. |

With **On the ground** ticked, every surface follows the terrain point by point. A change to that
setting takes effect at the next `CONTEXT`. Select any of these to see its use, width, deck or
height in Properties.

**Properties > Site > Site Context** sets:
- the radius;
- the kinds to get;
- the Overpass server.

`CONTEXTREMOVE` takes it all away.

## Site analysis

**Site analysis** is the second view of the **Analyze** tab: the switch at its top reads
*Analyses | Site analysis* (`SITEANALYSIS` opens it). It runs a site analysis the same way every time. It
follows the order professionals use: the RIBA Plan of Work's Stage 1 and a developer's due
diligence. The stages are:

0. **Define:** the boundary (the property line), the project type, and the questions the analysis
   must answer.
1. **Desktop study:** each category filled from open data and the model.
2. **Site visit:** each category's checklist, with notes and photographs pinned on the plan.
3. **Surveys:** where the visit leaves doubt.
4. **Analysis:** each finding classed and weighed.
5. **Synthesis:** the buildable area, the envelope and the yield.
6. **Report:** the standard boards.

Press a stage to mark where the project is.

**Ten categories, always in this order:**
1. Location and context
2. Legal and regulatory
3. Landform
4. Water
5. Climate
6. Ecology
7. Environmental risk
8. Access and circulation
9. Utilities
10. People and place

Each category lists what to find at the desk and what to check on site, as boxes to tick.

**A finding** has:
- a title and what was found;
- a class: fact, opportunity, constraint or red flag;
- a severity: low, medium or high;
- a confidence: desktop, seen on site, or surveyed;
- a source and a date;
- a note and a photograph (kept at most 960 px across).

*Place on the plan* pins a finding where you click. The pins carry the finding's number, such as
7.1, the first finding under Environmental risk, coloured by class. Red flags are listed first.

**Fill from the model** (`SAFILL`) adds what the app already knows, with the source and date of
each:
- the location;
- the built context (count, mean and tallest heights);
- the property line's area;
- the data layers and flood zones;
- the terrain's height, relief and slope;
- water and rain flow;
- the day lengths at the solstices;
- trees and green areas;
- streets by use, bridges and tunnels;
- railways, airports, overhead power and land use around.

Filling again updates these in place. A class or note you set is kept. A finding the model no
longer supports is removed, unless you have written on it.

Everything is saved with the project, and every change is one undo step.

## Climate and risk

In Site analysis, **Get climate and risk** (`CLIMATEGET`) fetches, for the site's latitude and longitude:
- **ten full years of daily weather and the last full year hour by hour** from ERA5 reanalysis, via
  Open-Meteo;
- **92 days of PM2.5** from CAMS, via Open-Meteo;
- **the earthquakes of magnitude 4.5 and above within 100 km since 1976** from the USGS.

All three sources are free and need no account. What is worked out is kept with the project, so
the board opens offline. Each result also becomes a finding under Climate or Environmental risk.

**Open the board** (`CLIMATE`) shows the result as a professional site-analysis board.

The **header** gives the place, the Köppen–Geiger climate zone, the period and the date.

The **indicators** are:
- climate zone;
- mean temperature;
- rainfall;
- prevailing wind;
- heating and cooling degree days;
- solar energy;
- outdoor comfort;
- PM2.5, with a state against the WHO guideline;
- earthquakes, with a state.

**Nine figures**, each titled with what it shows, with its source and a table:
1. temperature (the mean daily high and low, and the band of 80% of real days), with rainfall below
   it on the same months;
2. the wind rose for the year, with winter and summer beside it;
3. every hour of the year as a heat map in named temperature bands;
4. the sun path;
5. heating and cooling degree days (base 18 °C);
6. solar energy by month;
7. the psychrometric chart with the comfort zone and the share of hours in it;
8. the earthquakes by distance and direction, with the largest listed;
9. daily PM2.5 against the WHO guideline and interim targets.

Notes on method and the sources close the board.

Hover any mark for its values, and press **Tables** for every number. The board follows the app's
theme, prints on A3 landscape on white, and redraws its charts for a phone's width.

The climate is modelled at about 25 km, so a city's heat island or a valley's frost may differ.
Confirm with a local station where it matters. Earthquakes are history, not a hazard model: for
design, use the national seismic hazard map and code.

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
