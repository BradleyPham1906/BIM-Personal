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

## Zoning and yield

In Site analysis, **Enter zoning** (`ZONING`) opens the district's controls:
- the district, its permitted uses and the source (code, section, date);
- the floor area ratio, the height limit, a storeys limit and the coverage limit;
- a rule for each kind of side: the **front** (the street), the **sides** and the **rear**.

Each rule has a setback at the ground and, as the code gives them:
- **steps**: "above 15 m, set back 6 m";
- an **angular plane** rising from the lot line at a ratio: the front's sky exposure plane, or a
  side or rear daylight plane.

The front also takes the familiar street wall height and stepback above it. Pick the lot's front.
The rear is the side facing it and the rest are sides; any side can be set by hand, for example a
corner lot's second front.

**From the layers** reads a council zoning layer under the lot (see Data layers): the district and,
where the layer has them, the FAR and the height. That covers NYC's MapPLUTO (its residential or
commercial FAR, by the scheme's use) and an FSR and building-height layer, and a height given in
feet is turned into metres. Each value is credited to its layer and field.

**Build envelope** (`ENVELOPE`) builds the zoning envelope as a translucent, locked solid on its own
**Zoning envelope** layer. At every height, the envelope is the lot with each side moved in by its
rule there, up to the height limit. Every change to the record rebuilds it.

From the envelope the app works out:
- the floor plate at each storey's ceiling, capped by coverage;
- the envelope's capacity;
- the FAR's gross floor area;
- the **achievable** area, the lesser of the two, and which one **governs**;
- the net area, the units and the parking.

It also checks the design: GFA from the usages, the height, the ground coverage, and every element
outside the envelope in plan or in height. Below the ground the envelope does not apply.

**Open the board** (`ZONINGBOARD`) shows it all as a professional zoning and yield board:
- **indicators**: lot, FAR, height, coverage, capacity, achievable GFA, units, parking, and the
  design, with a state;
- **the zoning analysis table**: each control, what is permitted, what is proposed, and whether it
  complies, with an icon and a word;
- **two sections at true scale**, front to rear and side to side, with every setback, step and
  plane dimensioned, after New York's ZD1 zoning diagram;
- **the rules by side**: each kind of side's setback against height;
- **the lot plan**, turned so the street is at the bottom;
- **the floor plates by storey**;
- **the yield**, from gross area to units and parking.

Hover, **Tables**, the theme, print and the phone work as on the Climate board. Each result is also
a finding under Legal and regulatory, and every change is one undo step.

Check every control against the current code, and any overlay, variance or bonus, before relying on
it. A lot whose setbacks would split it in two is worked out up to that height, and the board says
so.

## Access and people

In Site analysis, **Get access and people** (`ACCESSGET`) asks two free sources at once, with no
account:
- **OpenStreetMap, through Overpass:** every street and path around the site, the transit stops and
  the routes that serve them, and the places of daily needs;
- **the US Census Bureau:** TIGERweb names the census tract, county and state at the site, and the
  American Community Survey's 5-year estimates give their people, with margins of error.

From the streets the app works out **walk times from the lot**, along the network at 80 m a minute
(4.8 km/h), with steps at half that. The walk leaves the lot anywhere within 30 m of its line, so a
lot with two frontages starts from both. Motorways, private roads and ways closed to people on foot
are left out, unless a private way is tagged for walking. Sidewalks are walked but not drawn. A
footbridge over the lot is walked, but it is not where the lot opens onto. With no property line,
the walk starts at the site's point.

It works out:
- **the rings:** the streets and paths reached within 5, 10 and 15 minutes, drawn as lines along
  the streets, as ArcGIS Network Analyst draws service areas;
- **daily needs:** the walk to the nearest food shop, health care, school or library, park or
  playground, café, bank or post office, and community centre or place of worship, and how many of
  each lie within 5, 10, 15 and 20 minutes. A park is reached at the nearest point of its edge. The
  kinds follow the 15-minute city; this is not a Walk Score;
- **transit:** the stops by walk time, with the lines that serve them. A stop's two sides, and a
  station with its entrances, count as one. OpenStreetMap holds no timetables, so how often a line
  runs needs the operator's GTFS feed;
- **the frontage:** each street the lot faces within 30 m, with the length of lot line it fronts,
  its class (arterial, collector, local, service), speed limit, lanes, sidewalks and cycleway;
- **connectivity:** the intersections within 400 m of the lot, counted as LEED ND counts them. A
  junction leading only to dead ends is left out, and a divided road's crossing counts once. The
  density is set against LEED ND's thresholds (90 per square mile to qualify, 300 and 400 for
  points). It also works out how much longer the walks are than the straight line.

The walk times appear on the plan as a **Walk times** layer, under Analysis in Layers (`WALKTIMES`
adds it again). It follows the access data, so a refresh updates it.

The people's figures are for the tract, its county and its state: population and density, age,
households, income, renting, homes empty, households without a car, and how people get to work.
Each comes with its 90% margin of error. A share's margin is worked out by the Census Bureau's
formula for a derived proportion, and the tract differs from its county only where the difference
is larger than the two margins together.

**Open the board** (`ACCESS`) shows it all as a professional access and people board:
- **indicators** in two rows, with a state where a reference exists: daily needs, the nearest bus
  and rail, lines within 10 minutes, intersections; population, age, income, renting, no car;
- **the walk-time map**, north up, with 400 and 800 m as the crow flies for comparison;
- **daily needs** on one scale of minutes, with the nearest of each kind;
- **the street hierarchy** within 400 m, line weight by class, with the frontage table;
- **transit** by walk time, with each stop's lines;
- **connectivity** against LEED ND, and route directness;
- **the tract against its county and state**, each measure with its margin, and the key facts;
- **how people get to work**, as 100% bars;
- **the age pyramid**, men and women in five-year bands, with the county's outline.

Each result is also a finding under Access and circulation or People and place, and all of it is
one undo step. Hover, **Tables**, the theme, print and the phone work as on the Climate board.

The census part covers US sites. Elsewhere the walk times still work, and the board says where the
national statistics office publishes the equivalent. If a server refuses the request, or does not
allow browser access, it is named; the app never routes around it.

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
