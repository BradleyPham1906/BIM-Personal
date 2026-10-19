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
  Nominatim asks. The place found is also the site's place for its standards (see
  [Standards](#standards)), in the same undo step.

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
| Trees | A trunk and a crown, as tall as the `height` tag, else 8 m. The crown is `diameter_crown` across, else a share of the height by the `leaf_type` and `leaf_cycle` tags (the Urban Tree Database's medium tree of that kind; 0.6 where the leaf type is not mapped). A needle-leaved tree is a cone. A tree row puts a tree about every 8 m, from end to end. |
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
5. **Access and people:** walk times to daily needs and transit; the streets within 800 m with what
   movement reads (speed, lanes, bike lanes, parking), the crossings' signals and stops, the doors
   on the lot, the car parks and garage entrances within 400 m, and each line's headway where it is
   mapped; and the census tract (US sites).
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
| Flood zones | FEMA's floodway, 1% annual chance (A, AE, AH, AO; V and VE on the coast), 0.2% (shaded X) and undetermined (D) zones, cut to 150 m around, each labelled inside it with its base flood elevation, apart from the others' labels; the zone the site is in | FEMA's National Flood Hazard Layer (US sites) |
| Street hierarchy | every street and path within 800 m by its class (motorway and trunk, arterial, collector, local, service, path), the heavier the line the higher the class; the main streets named with their speed limits; the lot's frontage named and heavier | OpenStreetMap's street classes |
| Cycling stress | each street's level of traffic stress, LTS 1 (carefree) to LTS 4 (white knuckles); the stressful crossings of main streets marked; the streets the lot reaches at low stress, as a wide pale band. Off at first | the 2012 criteria and the 2016 crossing table (below) |
| Transit | the stops within 8 minutes' walk (a bus) and 12 (rail, metro, light rail, tram), each with its walk and lines; the streets within 8 and 12 minutes; the bus and tram routes along their streets; the way to the nearest stop and station; PTAL at the site | OpenStreetMap's stops and routes; TfL's PTAL (below) |
| Walk times | the streets and paths reached on foot in 5, 10 and 15 minutes from the lot. Off at first | the walk times (Access and people) |
| Daily needs | the way along the streets to the nearest of each kind of daily need, the place marked with its walk | the same walks, traced back |
| Vehicle access | the driveways and service roads at the lot, with an arrow where each enters it, or a provisional entry from the lot's lowest street; the doors on the lot; the car parks (kind, spaces, walk) and garage entrances within 400 m; parking along the streets, each side drawn on its own | OpenStreetMap |
| Land use | every land use area and the grounds of schools, car parks, pitches and the like, and the buildings with a use of their own, in their LBCS family's colour, outlined, with a texture where two colours sit close (industrial hatched one way, assembly the other, natural resources dotted) and the family's name on large areas; the 400 m square around the site, labelled with its land use mix. Off at first | OpenStreetMap's tags, by LBCS's activities (below) |
| Figure-ground | the buildings filled dark, the open ground pale, in the 400 m square; its 100 m cells, each with its FSI; the square's GSI, FSI and storeys. Off at first | the context's buildings, by Spacematrix's measures (below) |
| Green and trees | the trees' crowns, the woods dotted, the public green spaces (one under 0.5 ha dashed); the neighbourhood's circle with its canopy; a line to each tree seen from the site; the nearest public green space of 0.5 ha or more, with its walk; 3-30-300 at the site | the context's trees, woods and parks, the sight lines and the walks (below) |
| Zoning around | a council layer's zoning districts in the layer's own colours, the site's district heavier and named, each district named on it; or, where no layer is loaded, that it is not. Off at first | a council's layer in Data Layers, its drawing info read once by Analyze site |

**Live and editable.**
- Select an element to move, turn, mirror, scale or delete it, or to change its colour, line,
  opacity or labels in Properties. An area (a slope class, a pond, a flood zone) is selected by
  clicking inside it, where nothing else is: the model and the lines and words over it come first.
  A selected area's edge is lit.
- Slope and Aspect cover the whole ground, so they start with their layers off: **Show** on their
  row turns one on. Cycling stress and Walk times colour the same streets as the Street hierarchy,
  so they start off too. Land use, Figure-ground and Zoning around cover the ground as well, and
  start off.
- **Run the analysis again** (in Properties, or on its row) lays it down again from what the
  project holds now. What you have not touched is refreshed. What you changed is kept, and marked
  when the analysis would now draw it differently. What you deleted stays deleted.
- **Reset to the analysis** gives one element back. An analysis's **Reset** gives back its whole
  layer: what you deleted comes back, and what you changed or copied goes.
- Properties says what each element shows, how it was worked out, and its source and date.
- Diagram elements are not building elements. Schedules, quantities, the LOD checks and the
  exports pass them by.
- A legend at the top right keys each analysis shown, with its source. **Hide the legend** turns it
  off. When the view is too small for every key, the sources go first, then the keys of the analyses
  you turned on longest ago, with a line saying how many more. On a phone there is none over the
  drawing: each analysis's row in Analyze carries its key.
- The diagrams' words keep clear of the north arrow, the view cube and the legend, which are drawn
  over them: a word that would fall under one moves, or gives way.
- Each analysis is also a row in its category, with Show or Hide, Run again, Select, Reset and its
  key: Compass in Location; Contours, Slope and Aspect in Landform; Water flow, Ponds and Flood
  zones in Water; Sun paths, Shadows and Winds in Climate; Noise in Environmental risk; Street
  hierarchy, Cycling stress, Transit, Walk times and Vehicle access in Access and circulation;
  Views and Daily needs in People and place; Land use and Figure-ground in Location and context;
  Green and trees in Ecology; Zoning around in Legal and regulatory.

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

**How movement is worked out.**
- **The streets** are kept within 800 m of the lot with the tags movement reads; past 6,000 points
  the farthest go first, and the layer says how far it reaches. A street's class follows the usual
  crosswalk from OpenStreetMap's to the FHWA's functional classes. On a light map the higher classes
  are darker; on the dark plan, brighter. After changing the map, **Run again** on the row draws
  the other set.
- **Cycling stress** follows Mekuria, Furth and Nixon's criteria (MTI report 11-19, 2012): a cycle
  track or path is LTS 1; a bike lane is rated by the lanes each way and the speed, beside parking or
  not, and with no parking beside it by its width where that is mapped; mixed traffic by the speed and the lanes, a residential
  street of under 3 lanes a level lower. A street is as stressful as its worst feature. Where a
  street maps no speed or lanes, its class's are assumed, as the noise analysis assumes them, and
  Properties says so. The speeds are read in rows: up to 25 mph (40 km/h), 30 mph (50 km/h), 35 mph
  (60 km/h), and over.
- **Crossings.** Where a calm street (LTS 2 or less) meets a main street of another name, with no
  signal or all-way stop within 20 m, the crossing takes Furth, Mekuria and Nixon's 2016 table by
  the main street's speed and lanes. A median refuge is not counted, which errs stressful.
- **The low-stress reach** is the streets the lot reaches at LTS 2 or less, a stressful crossing
  breaking the way, at most 25% further than the shortest ride. One-way streets are ridden both ways:
  a simplification.
- **PTAL** is TfL's method: each line at its nearest stop within reach (8 minutes for a bus, 12 for
  rail, metro, light rail and tram), its walk, half its headway and a reliability allowance (2
  minutes for a bus, 0.75 for rail) make its access time, and 30 over that its frequency at the door;
  per mode the best line counts in full and the others at half. The headways are OpenStreetMap's
  route intervals, so PTAL is given where every line within reach has one, as a floor where some do,
  and otherwise the layer says why there is none.
- **Daily needs and the nearest stop** are reached by the walks (Access and people), traced back
  along the streets to the lot. The design guides' 400 m (to green space) and 800 m (to shops and a
  primary school) are said in Properties.
- **A vehicle entry** is drawn where a driveway or service road crosses the lot line. With none, a
  provisional entry is marked on the lot's lowest street (an alley before a local street, an
  arterial last), as a parameter plan marks an entry until the design decides.

**How the land is worked out.** Each setting below is a record in **Properties > Site > Standards**
(Land and green), and can be overridden there with a reason.
- **Land use** reads each feature's tags by a crosswalk to the American Planning Association's
  Land-Based Classification Standards (LBCS), activity dimension, checked against LBCS's own
  descriptions: a hotel is residential (transient living), a port is movement, construction and
  waste are industrial, a cemetery or military land is institutional, a place of worship, a theatre
  or a station is assembly, a park is leisure, farmland or a managed forest natural resources, a
  wood or brownfield no activity. A building's own amenity, shop or office is read before its
  building value; an area's port before its industrial land use.
- **The mix** is counted on a 5 m grid over the 400 m square: each cell takes a building's own use,
  else the smallest area over it, else grass's or a flowerbed's, which take the class of what they
  lie in. Each family's share is of the cells that say one, 1000 to 8000; the mix is Shannon's
  entropy over them divided by the log of the families counted (eight, the owner's choice): 1 an
  even balance, 0 one use. What says no activity, or nothing, is left out and said.
- **The colours** are LBCS's hues, each stepped so that any two pass the colour-blindness checks
  (as on a map, where any two may touch), on the light map and on the dark plan; the textures, the
  outlines, the names and the key carry what colour alone cannot.
- **Density** follows Spacematrix (Berghauser Pont and Haupt): GSI is the ground floors over the
  land, FSI the floor area over it, OSR (1 - GSI) / FSI, and L, FSI over GSI, the storeys on
  average. The land is the whole square, streets and all; each footprint is cut to it, less its
  courtyards. A building's storeys are its building:levels (less building:min_level for a part
  standing on another), else its height over 3 m, at least one. Spacematrix's types are not named:
  their bounds are in the book, which was not read.
- **3-30-300** is measured as Browning et al. (2024) measure it, with what the app has:
  - **3 trees seen**: the site's sight lines at eye height (as Views draws them), a tree counted
    where a line meets its crown first, within 100 m; a window view's stand-in;
  - **30% canopy**: the mapped trees' crowns (diameter_crown, else 0.6 of the height) and the woods,
    on a 2 m grid, over a 500 m neighbourhood (the owner's choice: the rule fixes none), cut to the
    context's square and said so; ESA's land cover map, which the experts rate best, cannot be read
    from a page;
  - **300 m**: the walk along the streets (Access and people) to a public green space of at least
    0.5 ha, a park, garden, recreation ground or village green not mapped private: to a point of the
    network inside it, or to its edge from the nearest street within 60 m.
- **A council layer's colours** are read as Esri's own code reads a layer's drawing info: its unique
  values (one field, or two or three joined), each value's solid fill and outline, the default for
  the rest, the layer's transparency. A hatched fill is not drawn; a layer with no colours, or one
  whose description cannot be read, is outlined and named in the app's.

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
- transit's PTAL, its floor, or why there is none;
- cycling: the frontage streets' levels of stress and the low-stress reach;
- vehicle access and parking: the driveways into the lot or a provisional entry, the car parks
  within 400 m and their spaces, and the parking along the frontage;
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
  station with its entrances, count as one. How often a line runs is read from its route's interval
  where OpenStreetMap maps one, for PTAL (Site analysis, Transit);
- **the frontage:** each street the lot faces within 30 m, with the length of lot line it fronts,
  its class (arterial, collector, local, service), speed limit, lanes, sidewalks and cycleway;
- **connectivity:** the intersections within 400 m of the lot, counted as LEED ND counts them. A
  junction leading only to dead ends is left out, and a divided road's crossing counts once. The
  density is set against LEED ND's thresholds (90 per square mile to qualify, 300 and 400 for
  points). It also works out how much longer the walks are than the straight line.

Analyze site draws the walk times in the model, on Layers, Site analysis (Walk times). The plan
overlay of earlier versions is still there on request: `WALKTIMES` adds it as a **Walk times** layer
under Analysis in Layers, and it follows the access data.

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

## Standards

Every standard, guideline and assumption an analysis applies is a record in the app's standards
registry, never a number in its code. **Properties > Site > Standards** (`STANDARDS`, or `CODES`)
shows them, area by area: transit and walking, roads and noise, cycling, air, flood and ground,
buildings, structure, site context, land and green, climate.

### The place and the date

Which edition is in force depends on where the site is, and when:
- **Find** (or `FINDADDRESS`, or the address Analyze site looks up) sets the site's place from
  Nominatim's answer: the country, the region (a state, England), the district (a London borough)
  and the city, as ISO 3166-2 gives them. **Set** gives them by hand, as codes (US, US-PA, GB-WSM);
  **Clear** takes them away. If the site moves far from where its place was found, the group says so.
- **In force on** is today, unless you give a date: a project held to the codes of an earlier date.

The edition in force is the one adopted most specifically for the place, on that date: the city's,
then the district's, the region's, the country's, then an international one. Where two are adopted
for the same place, the one adopted latest; an adoption's end date is the first day it no longer
applies.

Where no edition is adopted for the place, a method the analyses need is still applied, and says
**applied outside its place**, with where it is in force: TfL's PTAL is London's, the walking
distances in Manual for Streets are England's and Wales's, and WHO's road noise guideline, which the
noise layer gives for scale, is guidance for its European Region. The app's own assumptions (a storey's
height where OpenStreetMap maps none, the slope classes) say they are the app's.

### A topic, its values and its source

Each topic row shows its edition, how it applies here, what uses it, and the level its source was
read at:

| Level | Means |
|---|---|
| **P** | Read at its source. |
| **S** | From a dependable secondary source; the gap is said. |
| **U** | Not yet verified. Never applied. |
| **A** | The app's own assumption. |

**Values** lists each value in words with its unit, and the source to its section, with a link.
A topic of more than one edition can be **chosen** for the project in the list under it; **By place
and date** goes back.

### Overrides

**Override** sets a number for this project. It needs a reason, which every result that uses it
shows. The value must be a number, more than zero (a percentage may be zero, a temperature
anything), and in order where values are ordered: a walk to a bus stop shorter than to a station, a
slope class below the next. A table changes only with a pack. **Reset** gives the standard's value
back. Each change is one undo step.

### What a result keeps

- Each analysis drawn in the model keeps the standards it used. When one changes (an edition, a
  value, an override), its row in Analyze reads **Out of date**, says which and why, and **Run
  again** redraws it. Every row names the standards it uses.
- The data Analyze site fetches keeps what it was worked out with: the walking speed of the walk
  times, the sizes given to what OpenStreetMap leaves unsized, the climate's degree-day base, calm
  and comfort band, WHO's levels. A finding drawn from that data states those values, and says when
  **Analyze site again** is needed to work it out with the values as they are now.
- A change works the findings out again at once from the data kept, with no fetch: a threshold such
  as LEED's prerequisite, or a slope class's edge, is in the finding straight away.
- A finding names the standards behind it, and an edition applied outside its place or a value
  overridden, with its reason.

### In force here, not applied by the app yet

For the place, the codes in force that the app does not apply yet, each with its source and how it
is had (free, free to read, or sold). For a Pennsylvania site: the Uniform Construction Code and the
2021 International Building Code it adopts, the 2010 ADA Standards, the MUTCD, PennDOT's Design
Manual 4 and the AASHTO bridge specifications it adopts, and the FAA's airport design circular. The
registry also lists editions not adopted for a place it knows (the 2024 IBC, ASHRAE 90.1-2025,
ASCE/SEI 7-22, the Green Book), and, at level U with nothing claimed, those whose current edition
could not be read (ACI 318, AISC 360, PennDOT's Design Manual 2).

### Standards packs

A pack is a JSON file of up to 1 MB that adds editions and topics: a newer edition, or a place's own.
**Load a pack** reads it and, before anything changes, shows its name, publisher, date and SHA-256,
and for each topic the edition in force before and after and the values that change. Packs are
unsigned: their origin is the file you chose. **Apply** or **Cancel**. **Remove** takes a pack away.
Packs are kept with the project.

A pack never changes an edition already in the registry: a revision is a new edition. An edition
of a topic the app applies must carry every value the app reads, of the same kind (a number, or a
table).

```
{"format": "bim-standards-pack", "version": 1,
 "publisher": "Example Planning Office", "name": "Example walking standard", "date": "2026-09-01",
 "topics": [{"id": "walk.speed", "eds": [{
   "id": "walk.speed.example", "name": "A slower walk (an example)", "pub": "2026-01-01",
   "adopt": [{"at": "us-pa", "from": "2026-01-01"}],
   "src": {"t": "Example Planning Office", "w": "section 1", "u": "https://example.org/walk", "lv": "P"},
   "v": [{"n": "m_min", "v": 70, "u": "m/min", "say": "the walking speed"}]}]}]}
```

A place key is `*` (international), a country (`us`), a region or district (`us-pa`, `gb-wsm`), or a
city after its region (`us-pa:philadelphia`).

## People, vehicles and trees

**Assets** has a group of models for scale and for the simulations: people (a man, a woman, a
child of 8, a seated person, a wheelchair user), a cycle and a cycle stand, a parking bay, three
vehicles (a car, a delivery truck, a city bus) and two trees (a broadleaf and a conifer). Click one
to place it in the middle of the view, or drag it where you want it. Each is sized to a source the
standards registry names (**Properties > Site > Standards**, area **Assets**):

| Model | Sized to |
|---|---|
| People | the mean height of US adults and of a boy of 8 (NCHS, 2015 to 2018); eyes and shoulders scaled from the height as NASA's Human Integration Design Handbook does |
| Wheelchair user | the Access Board's measured manual chair users (IDeA Center, 2010), within the 2010 ADA Standards' clear floor space; its turning space, 1525 mm across, shown on the plan if ticked |
| Cycle, stand | the UK's LTN 1/20: a solo cycle 1.8 m by 0.65 m, Sheffield stands 1.2 m apart |
| Parking bay | Manual for Streets: 2.4 m by 4.8 m, used where no other rule is recorded |
| Car, delivery truck, city bus | AASHTO's design vehicles P, SU-30 and CITY-BUS (the Green Book, 7th Edition, 2018); each can show its turning path on the plan, from the inner rear wheel out to the front corner, to the left or the right |
| Trees | the Urban Tree Database: broadleaf or conifer, deciduous or evergreen, small, medium or large |

**Properties** shows a model's sizes and where they come from. A person's height can be their
own; a tree's height and crown too. Choosing someone or something else (a child, a large tree)
takes that one's sizes. When a standard is overridden, every placed model is rebuilt to it, except
a size set by hand.

**Trees in leaf.** A deciduous tree is in leaf over the site's growing season: from the first six
days in a row above 5 C to the first six days below 5 C after midsummer (ETCCDI's GSL), the median
of the years of the site's climate (**Analyze site**, or **Properties > Site > Climate**). Out of its
season the tree is bare, and only its trunk casts a shadow. Until the climate is fetched, a tree is
in leaf all year, and its page says so.

## GeoJSON and KML

- `GEOIMPORT` brings in GeoJSON or KML as site data, placed by longitude and latitude.
- `GEOEXPORT` writes the plan as GeoJSON.

## Sun and shadows

`SUNSTUDY` shows the shadows and the sun path for the site's date and time. They are set in
**Properties > Site > Location**. The sun's position follows NOAA's equations. A deciduous tree from
**Assets** casts its trunk's shadow only on a date outside its growing season.

## Alignments

- `ALIGNMENT` makes a selected polyline a road alignment.
- `STATION` reads station and offset along it.
- `PROFILEVIEW` places its vertical profile.
