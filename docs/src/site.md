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

**Site analysis** is in the **Analyze** tab (`SITEANALYSIS` opens it). It starts with one button.

### Analyze site

**Analyze site** (`ANALYZESITE`) needs only where the site is: its latitude and longitude, or an
address typed in the box beside the button. It does the rest from free open data, and lists each
step as it goes:
1. **The site:** the address found on OpenStreetMap (Nominatim), if the site is not placed yet.
2. **Context:** the buildings, roads, water, green, trees, railways, land use and terrain, at least
   300 m around. A smaller context radius is raised to 300 m, which the noise and the views need.
3. **Ground and water:** the ground every 5 m for 150 m around the site, from the same free AWS
   Terrain Tiles, kept with the project in metres above sea level; and for a US site, FEMA's flood
   zones (the National Flood Hazard Layer). FEMA maps the US and its territories only.
4. **Climate and time zone:** ten years of daily climate, a year of hourly wind and heat, air
   quality and earthquakes. The site's UTC offset comes with them, so the sun needs no typing. An
   offset you gave is kept.
5. **Access and people:** walk times to daily needs and transit, and the census tract (US sites).
6. **Zoning:** read from a council layer, where one is loaded in Data Layers and the property line
   is drawn.
7. **The analyses, drawn in the model** (below).

Each step reads Done, Partly (some of its sources down, each named), Failed (with the reason) or
Skipped (with why). What fails leaves the rest standing. The whole run is **one undo step**.
**Analyze site again** fetches everything again, and keeps what you changed in the diagrams.

### The analyses in the model

Each analysis draws its diagram as elements of the model, on its own layer under **Layers > Site
analysis**:

| Analysis | What it draws | Worked out from |
|---|---|---|
| Compass and distance | the compass ring on true north, its sixteen points, and a ring every 100 m out to the context's edge | the site's true north |
| Sun paths | the sun's path on 21 June, on 20 March and 22 September, and on 21 December, on a dome over the site; a dot an hour; the sun now | NOAA's solar position equations |
| Shadows | the model's own shadows at 9, 12 and 15 on those dates. 20 March is shown; the solstices are on layers of their own, off | the sun and the model, drawn again whenever the model changes |
| Winds | an arrow for each season's prevailing wind, as wide as its share of hours (seasons from the same quarter share one); the strongest winds; the year's wind rose | a year of hourly ERA5 wind, via Open-Meteo |
| Views | what can be seen at eye height and from the top floor (isovists); each view named by what it reaches: water, a park or woods, a landmark, open land | the context's buildings and trees, at their heights |
| Noise | each road's noise in 5 dB classes from 55 dB, following the street and screened behind buildings; the loudest roads and the railways marked; the level at the site | an estimate from each road's class (below) |
| Contours | a line every 0.25 to 50 m, at round heights above sea level (at most 24 lines), coloured green low to brown high; every fifth an index contour, thicker and labelled with its height | the ground every 5 m (below) |
| Slope | the ground in five classes: 0 to 5%, 5 to 10%, 10 to 15%, 15 to 25%, over 25%; the site's mean and steepest. Off at first | Horn's method on the same ground |
| Aspect | the way the ground faces, in eight directions and flat, coloured for warmth: facing the equator warm, facing the pole cool. Off at first | Horn's method |
| Water flow | the flow lines, wider by their Strahler order; the divides between the large catchments; the land draining onto the site, shaded; an arrow where the site's water leaves it | Priority-Flood and D8 on the same ground |
| Ponds | where water would stand 10 cm or more over 50 m2 or more: its depth, area and volume, its deepest point marked | the same, filled |
| Flood zones | FEMA's floodway, 1% annual chance (A, AE, AH, AO; V and VE on the coast), 0.2% (shaded X) and undetermined (D) zones, cut to 150 m around, each with its base flood elevation; the zone the site is in | FEMA's National Flood Hazard Layer (US sites) |

**Live and editable.**
- Select an element to move, turn, mirror, scale or delete it, or to change its colour, line,
  opacity or labels in Properties. An area (a slope class, a pond, a flood zone) is selected by
  clicking inside it, where nothing else is: the model and the lines and words over it come first.
  A selected area's edge is lit.
- Slope and Aspect cover the whole ground, so they start with their layers off: **Show** on their
  row turns one on.
- **Run the analysis again** (in Properties, or on its row) lays it down again from what the
  project holds now. What you have not touched is refreshed. What you changed is kept, and marked
  when the analysis would now draw it differently. What you deleted stays deleted.
- **Reset to the analysis** gives one element back. An analysis's **Reset** gives back its whole
  layer: what you deleted comes back, and what you changed or copied goes.
- Properties says what each element shows, how it was worked out, and its source and date.
- Diagram elements are not building elements. Schedules, quantities, the LOD checks and the
  exports pass them by.
- A legend at the top right keys each analysis shown, with its source. **Hide the legend** turns it
  off. When the view is too small for every key, the sources go first, then the last analyses' keys,
  with a line saying how many more. On a phone there is none over the drawing: each analysis's row
  in Analyze carries its key.
- Each analysis is also a row in its category, with Show or Hide, Run again, Select, Reset and its
  key: Compass in Location; Contours, Slope and Aspect in Landform; Water flow, Ponds and Flood
  zones in Water; Sun paths, Shadows and Winds in Climate; Noise in Environmental risk; Views in
  People and place.

**How the noise is estimated.** Open data gives a road's class and seldom its traffic, so:
- the traffic is the class's typical daily flow, from FHWA's functional classes (urban where the
  area is built up), with 94% of it in the 18 hours;
- the level 10 m from the kerb, and how it falls with distance, follow CRTN (1988), at a point 4 m
  up and no further than 300 m, where the method stops;
- a building in between screens what is behind it, by ISO 9613-2's barrier term at 500 Hz, at most
  20 dB;
- the ground is taken as hard, and only the first building on each line counts.

So it errs loud. It is a screening estimate: measure where it matters.

**How the ground and its water are worked out.**
- **The ground.** The project's own surface where it covers the site; else the ground Analyze site
  kept, when the site is still where it was fetched for; else the context's terrain, which is a
  point every 25 m, and says so. The ground under the site's origin is the model's 0.
- **Slope and aspect** follow Horn (1981): each 5 m cell's fall across its eight neighbours, the
  nearest two counted twice. Slope is rise over run, as a percentage. 15% and 25% are the decision
  points: up to 15% building and roads are routine, 15 to 25% needs walls and engineered drainage,
  over 25% is seldom built on. Aspect is the way the ground falls, clockwise from true north; under
  2% it is flat.
- **Contours** are traced by marching squares between the grid's points, so each line passes where
  the ground is at its height. A saddle is read by the middle of its cell.
- **Water.** Priority-Flood (Barnes, Lehman and Mulla, 2014) fills each hollow to the level its
  water could leave by, then D8 (O'Callaghan and Mark, 1984) sends each cell's water to its steepest
  neighbour. A flow line starts where 2,500 m2 or more drains through a cell, and its order is
  Strahler's: two of the same order make the next. A catchment of 4% or more of the ground is
  named, and the divide between two of them follows the edges between their cells, its steps eased
  to within a cell. A pond is where
  the filled ground stands 10 cm or more over the real one.
- **FEMA's zones** are read as FEMA classes them: the floodway by its zone subtype, the 1% annual
  chance zones by their special flood hazard flag, shaded X (or B) as the 0.2%. Unshaded X, minimal
  hazard, is not drawn. A base flood elevation of -9999 means none was set; feet are also given in
  metres, on FEMA's vertical datum.

The ground is every 5 m, from elevation tiles: kerbs, swales, culverts and pipes are not in it. It
is a screening of the land and its water, made before a survey and a drainage design decide.

### The ten categories and the findings

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

Each category holds its data, its analyses and its **findings**. The data writes the findings:
Analyze site, and each fetch on its own. Each finding has a class (fact, opportunity, constraint or
red flag), a severity, a source and a date. It is numbered by category: 7.1 is the first under
Environmental risk. Red flags are listed first. Findings are to read; there is nothing to type.

They cover:
- the location;
- the built context (count, mean and tallest heights);
- the property line's area;
- the data layers and flood zones;
- the terrain's height, relief and slope;
- the site's slope from the ground around it: its mean, its steepest, how much is under 5% and how
  much 15% or more;
- water and rain flow;
- the site's drainage: which way it drains, how much land drains onto it, the ponds near it;
- its FEMA flood zone, and the zones within 150 m: a red flag in the floodway, a constraint in a
  flood zone;
- the day lengths at the solstices;
- trees and green areas;
- streets by use, bridges and tunnels;
- railways, airports, overhead power and land use around;
- and the climate, risk, zoning, access and people data, below.

A finding the data no longer supports goes. Everything is saved with the project.

## Climate and risk

In Analyze, under 5. Climate, **Get climate and risk** (`CLIMATEGET`) fetches, for the site's latitude and longitude:
- **ten full years of daily weather and the last full year hour by hour** from ERA5 reanalysis, via
  Open-Meteo;
- **92 days of PM2.5** from CAMS, via Open-Meteo;
- **the earthquakes of magnitude 4.5 and above within 100 km since 1976** from the USGS.

All three sources are free and need no account. What is worked out is kept with the project, so
the board opens offline. Each result also becomes a finding under Climate or Environmental risk.

**Show in Presentation** (`CLIMATE`) puts the Climate and risk board in the set and opens it. It shows the result as a professional site-analysis board.

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

In Analyze, under 2. Legal, **Enter zoning** (`ZONING`) opens the district's controls:
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

**Show in Presentation** (`ZONINGBOARD`) puts the Zoning and yield board in the set and opens it. It shows it all as a professional zoning and yield board:
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

In Analyze, under 8. Access, **Get access and people** (`ACCESSGET`) asks two free sources at once, with no
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

**Show in Presentation** (`ACCESS`) puts the Access and people board in the set and opens it. It shows it all as a professional access and people board:
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
