# Research: how professionals present access and the people around a site

For V161 (Site analysis SA4, access and people). The owner's bar for the site analysis: "really really
really professional ... research online on how they present the analysis (architectural, arcgis, data
analysis)". This note records, in our own words, how practice presents walking and transit access,
the street hierarchy, connectivity, and the demographics, and the design that follows for V161.

## 1. Walking access: service areas, not circles

Architects often draw 400 m and 800 m circles around a site. Network analysis measures along the
streets instead. ArcGIS Network Analyst's **service area** is the reference tool:
- It returns either the **lines** of the network reachable before each cutoff, or **polygons**
  enclosing them, or both.
- By default each cutoff is a **ring**: with 5, 10 and 15 minutes, the 10-minute band holds what is
  reached in 5 to 10 minutes. The alternative, disks, holds everything up to the cutoff.
- On a grid of streets the polygon's detail matters little. On winding or rural roads, the lines are
  the honest picture.

([Make Service Area Analysis Layer](https://pro.arcgis.com/en/pro-app/3.3/tool-reference/network-analyst/make-service-area-analysis-layer.htm),
[Generate Service Areas](https://desktop.arcgis.com/en/arcmap/latest/extensions/network-analyst/itemdesc-generate-service-areas.htm))

**Walking speed:** 80 m a minute (4.8 km/h) is the usual planning figure. A 5-minute walk is then
400 m and a 10-minute walk 800 m, the two TOD catchments below.

## 2. Daily needs within a walk

**Walk Score's published method** is the best-known measure of amenity access:
- An amenity within a 5-minute walk (a quarter mile) counts in full.
- A decay function counts more distant ones for less.
- Nothing counts beyond a 30-minute walk.
- The distances are measured along walking routes, not straight lines.
- Pedestrian friendliness (intersection density and block length) can take a small deduction.

([Walk Score methodology](https://walkscore.com/methodology))

Walk Score is a trademark and its weights are its own, so the app does not compute a "Walk Score". It
shows what the method rests on, openly:
- the nearest of each kind of daily need, in minutes along the streets;
- how many there are within 5, 10 and 15 minutes.

**The 15-minute city** (Carlos Moreno) frames the kinds. Its six social functions are living,
working, supplying (food and shops), caring (health), learning (education) and enjoying (parks and
culture). A site is judged by how many of them are within a 15-minute walk or ride.
([AIVP on the 15-minute city](https://www.aivp.org/en/?p=26936),
[Saint-Fons case study](https://eres.architexturez.net/doc/eres-id-eres2022-163))

## 3. Transit

- **Transit-oriented development** catchments are usually 400 to 800 m (a quarter to a half mile)
  on foot.
- ITDP's People Near Transit uses 1 km to high-quality rapid transit.

So a stop within a 5-minute walk is good for buses, and a station within 10 to 12 minutes is good
for rail. ([TOD Standard](https://framework.itdp.org/?p=10662),
[People Near Transit](https://indiaenvironmentportal.org.in/reports-and-documents/people-near-transit-improving-accessibility-and-rapid-transit-coverage-in-large-cities))

OpenStreetMap holds stops, stations and route relations: which lines serve a stop, and their
numbers. It does not hold timetables, so service frequency needs the operator's GTFS feed. The board
says so.

## 4. The street hierarchy

The FHWA's functional classes describe a road's job:
- **arterials** move traffic, with access to land a lesser role;
- **collectors** connect the arterials to the local streets;
- **local streets** give access to the land beside them.

([NCDOT road functional classification](https://xfer.services.ncdot.gov/gisdot/Metadata/QuarterlyPublication/2026_Quarter2/RoadFuncClass.pdf))

OpenStreetMap's `highway` tag describes a road's character, not its federal class. The usual
approximate crosswalk:
- motorway, trunk and primary are arterials;
- secondary and tertiary are collectors (or minor arterials);
- residential, unclassified and living_street are local;
- pedestrian, footway, cycleway, path and steps are for walking and cycling only.

([talk-us mapping proposal](https://lists.openstreetmap.org/pipermail/talk-us/2010-March/002901.html))

**A site board's access diagram** draws the hierarchy by line weight: the heaviest lines for
arterials, then collectors, then local streets, with paths dashed. It names the streets the lot
fronts, with their class, speed limit, lanes and sidewalks: that is where its entries and servicing
can go.

## 5. Connectivity

**Intersection density** is the standard measure of how walkable a street network is. LEED for
Neighborhood Development sets these thresholds:
- at least **90 intersections per square mile** (about 35 per km²) within a quarter mile of the
  project, for a small site;
- **140 per square mile** (about 54 per km²) inside a project;
- points at **300 to 400** per square mile (116 to 154 per km²), and more above **400** (154 per km²).

([LEED ND v4 NPDp3](https://leeduser.buildinggreen.com/credit/ND-v4/NPDp3),
[NPDc6](https://leeduser.buildinggreen.com/credit/ND-v4/NPDc6),
[CNU on the revisions](https://www.cnu.org/node/1974))

Short blocks and **route directness** are the other two measures. Route directness is the walk
along the streets divided by the straight line; near 1 is direct.

## 6. The people: ACS, with its uncertainty

The American Community Survey's 5-year estimates are the standard US source at the census-tract
scale (about 4,000 people). They are estimates from a sample, so they carry a margin of error (90%
confidence). At the tract scale it is large:
- 99% of tracts have a margin of error of 10% or more of their population estimate;
- 15% have one of 100% or more.

([Van Riper and Spielman, NCVHS](https://ncvhs.hhs.gov/wp-content/uploads/2022/02/Presentation-Uncertainty-in-Demographic-and-Socioeconomic-Data-David-Van-Riper-and-Seth-Spielman.pdf))

Professional practice therefore:
- **shows the margin of error with each estimate**, and when comparing two places, treats
  overlapping ranges as no real difference
  ([PRB ACS community](https://acsdatacommunity.prb.org/discussion-forum/f/forum/413/error-margins-for-5-year-acs-estimates/889));
- **compares the tract with its county and state**, as Census Reporter's profiles do, because a
  number means little alone;
- **works out a share's margin of error** with the Census Bureau's formula for a derived proportion,
  (1/Y)·√(MOE_X² − P²·MOE_Y²). Where the term under the root is negative, it uses the ratio formula,
  with a plus.
  ([ACS General Handbook, ch. 8](https://www.census.gov/content/dam/Census/library/publications/2018/acs/acs_general_handbook_2018_ch08.pdf))

**Business Analyst's demographic profiles** lead with key facts: population, median age, median
household income, households, education and employment. They then show the age and sex structure
and the household composition. ([Business Analyst infographics](https://www.esri.com/arcgis-blog/products/analytics/analytics/seven-new-infographics),
[What's new, November 2022](https://www.esri.com/arcgis-blog/products/bus-analyst/announcements/whats-new-in-arcgis-business-analyst-web-app-november-2022))

**The age pyramid** is drawn by convention:
- one sex to each side;
- five-year bands, youngest at the bottom;
- as a share of the whole population, so places of any size compare;
- a larger place's outline over it shows where the site's neighbourhood differs;
- two neutral, distinct colours, never blue and pink.

**For a site**, the people figures that matter are:
- who lives there: population, density, age;
- how they live: households, household size, renters and owners, income;
- how they move: households without a car, and how people get to work.

The last two tell a designer how much parking, cycle storage and transit access the scheme needs.

## 7. The sources: free, no key

| Data | Source | Notes |
|---|---|---|
| Streets, paths, transit stops and routes, amenities | OpenStreetMap via the Overpass API, already used by CONTEXT (V133) | ODbL; credited "© OpenStreetMap contributors" |
| The site's census tract, county and state, and their land areas | The Census Bureau's TIGERweb, an ArcGIS REST server | Public domain |
| Population, households, income, tenure, vehicles, commute, age and sex | The Census Data API, ACS 5-year | Public domain; a key is optional at this volume |

These are free and need no account. The app has been checked against fixtures, not the live
servers: the build environment cannot reach them. If a server refuses browser access, the app names
it, as every other source in the app does, and never routes around it.

Outside the US the census part is not available, and the board says so. The OpenStreetMap part works
anywhere.

## 8. The design this sets for V161

**ACCESSGET** asks two free sources at once.

- **OpenStreetMap, in one Overpass request around the site:**
  - every street and path, with its nodes;
  - transit stops and stations, and the routes that serve them, with their members;
  - parks with their outlines;
  - daily-needs places in seven kinds:
    - food: supermarkets, groceries, bakeries, butchers, delis, markets, convenience stores;
    - health: clinics, doctors, dentists, pharmacies, hospitals;
    - learning: kindergartens, childcare, schools, colleges, universities, libraries;
    - parks and play: parks, playgrounds, sports and fitness centres;
    - eating out: cafes, restaurants, fast food, pubs;
    - services: banks, post offices;
    - community: community centres and places of worship.

  The app then works out:
  - **walk times** along the network (Dijkstra, 80 m a minute, steps at half that). The walk leaves
    the lot anywhere: every point of the ground network within 30 m of the lot line is a start, its
    time the straight step from the line. Motorways, ways with foot=no and private ways are left out
    (unless foot=yes). Sidewalks are walked, not drawn. A bridge or tunnel is not the lot's ground;
  - each place's and stop's time: the network's time where the place meets it, plus the step to it.
    A park's is to the nearest point of its edge;
  - **walk time bands** of 5, 10 and 15 minutes, as rings, drawn as lines along the streets, as
    Network Analyst's line output is, with 15 to 20 minutes in grey;
  - **the stops**, grouped by name. A stop's two sides and its stop position count as one, and so
    does a station with its unnamed entrances, so the walk is to the nearest entrance. Each stop
    carries its lines, once each though they run both ways;
  - **the frontage streets:** the lot line metre by metre, given to the street that faces it within
    30 m, measured outward square to the line. Each street has its class, speed, lanes, sidewalks
    (found mapped separately where the road does not say) and cycleway;
  - **connectivity:** intersections within 400 m of the lot (as LEED ND counts them), with dead
    ends taken off until none is left and corners within 12 m merged. Also route directness, the
    median of the walk over the straight line, to every place and stop 150 m or more away.
- **The Census:**
  - TIGERweb's identify at the site gives the tract, county and state, with their land areas,
    picked by their layers' names;
  - the ACS 5-year gives the key facts with margins of error for all three, and the age and sex
    structure of the tract and the county. The newest year is asked first, then the year before if
    it is not out yet.

  Shares and their margins of error are worked out by the Census Bureau's formulas; a difference
  from the county counts only where it is larger than the two margins together.

**The results:**
- **Findings** in Access and circulation (walk times, transit, the frontage, connectivity) and in
  People and place (daily needs within a walk, who lives here, households, how they move).
- **A walk times layer**, under Analysis in Layers (as V148's results are): the streets coloured by
  band and the stops marked, drawn on the plan. It follows the access data, as a terrain layer
  follows its surface.
- **The Access and people board**, in the Climate board's frame:
  - two rows of indicators, access and the people, with states where a reference exists: daily
    needs within 10 minutes, the nearest bus and rail, intersection density against LEED ND;
  - Fig. 1, the walk-time map, north up, with 400 and 800 m as the crow flies;
  - Fig. 2, daily needs as a dot plot of minutes, banded at 5, 10 and 15, with the nearest of each;
  - Fig. 3, the street hierarchy within 400 m by line weight, with the frontage and its table;
  - Fig. 4, the transit stops by walk time, with their lines;
  - Fig. 5, intersection density against LEED ND's thresholds, and route directness;
  - Fig. 6, the tract against its county and state, each measure on its own scale with the tract's
    margin of error, and the key facts;
  - Fig. 7, how people get to work, as 100% bars;
  - Fig. 8, the age pyramid with the county's outline;
  - notes on method and sources.

Every figure has its table, every mark a tooltip. The board works on a phone and prints.
