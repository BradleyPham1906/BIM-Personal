# Research: site analysis run from one button, drawn in the model (V164 to V167)

The owner, after V163: "the purpose of site analysis was to understand whats surrounding using
existing data, then make it understandable using diagrams. The current tool we built only provide
the report in the board, and i have to input information, which is not the right way ... remove
[the checklist] entirely ... all i want is button then the analysis run, then it leverage
appropriate relevant data from target api to analyze the site, then put that under analysis
layers, built straight in the model that i can interact with." Then: "it should make site
analysis quicker with complex logic to run each type of analysis. research how architects, GIS
scientist, landscape architect, transportation planner, analysist do this and how they present
each analysis in a professional way".

The owner's references are SketchUp site-analysis diagrams. Around the building they show:
- a compass ring and dashed distance rings (100 to 500 m);
- the sun's paths for June, March and September, and December, with hour dots (6h to 20h) and
  the sun now as a red dot;
- winds by season as wide arrows;
- views as dashed arrows, noise as arcs, storms as a spiral;
- parking entry and exit as chevrons;
- contours over a satellite image.

A sheet of circular diagrams covers transport, topography, zone and area, winter and summer sun,
shade and wind, and connection. Asked how the diagrams should live, the owner chose "a live
analysis that is editable". Asked what goes, they chose everything typed by hand. The boards stay
as they are.

`research-site-analysis-process.md` (V158) covers the process: the stages, McHarg's layers and
Esri's suitability steps. This note covers each analysis: how each profession works it out, and
how it is drawn.

## 1. Architects: the climate and the context around the building

- **Sun path.**
  - Drawn for the summer and winter solstices and the equinox, with the hours marked. It decides
    which faces take the heat, where the shade falls and how the plan is oriented
    ([Ladybug sun path](https://bsl.hku.hk/tutorials/energy-building-simulation/ladybug/sunpath-and-sunlight-hour-analysis/),
    [Ladybug Tools](https://www.food4rhino.com/en/app/ladybug-tools)).
  - Computational designers draw it as a dome over the building. Each sun position sits on a
    sphere at its azimuth and altitude, so in plan an hour's dot is r cos(altitude) from the
    centre. The owner's references are that dome, seen from above and from an angle.
- **Shadows.**
  - Planning shadow studies plot the shadows at several times of day, on the winter solstice
    and the equinoxes (a condition such as Northumberland's names the winter solstice and both
    equinoxes).
  - The BRE test for an open space asks that at least half of it gets two hours of sun on 21
    March, and counts a loss as noticeable below that and below 0.8 of its former value
    ([summary of BRE 209](https://www.london.gov.uk/sites/default/files/mgla071020-6458_ir_response.pdf)).
  - Very low sun, under about 10 degrees, is left out as unrealistic.
- **Wind.**
  - A wind rose is built from a year of hourly records. The prevailing direction by season
    decides where openings and windbreaks go
    ([ClimateStudio site analysis](https://climatestudiodocs.com/docs/siteAnalysis.html),
    [Ladybug wind](https://www.linkedin.com/learning/grasshopper-essential-training/analyzing-wind-data-with-ladybug)).
  - On a site plan it is drawn as arrows from the prevailing direction, one per season, labelled
    with the season.
- **Views, noise, the compass and distance.**
  - Views are drawn as arrows to what is worth seeing, and to what should be screened.
  - Noise is drawn as arcs at its source.
  - A north arrow and a scale go on every diagram.
  - Guides agree that each diagram should carry one idea: sun, wind and traffic on one sheet
    clutter it ([site strategy diagram](https://openlab.citytech.cuny.edu/arch3612f23/files/2022/02/Site-Strategy-Diagram.pdf)).

## 2. Landscape architects: the land and its water

- **Inventory, analysis, synthesis** (LaGro, *Site Analysis: A Contextual Approach*):
  - Physical: topography, geology, hydrology, soils, climate and hazards.
  - Biological: vegetation and habitat.
  - Cultural: land use, circulation, perceptual quality.
  - Each is read as opportunities and constraints for the programme. McHarg's overlays
    (*Design with Nature*) are where the layers came from
    ([LaGro outline](https://www.researchgate.net/figure/Site-inventory-James-A-LaGro-Site-Analysis-A-Contextual-Approach-to-Sustainable-Land_fig7_329001724)).
- **Slope classes.** The bands vary by place. A working set, with 15% and 25% as the decision
  points ([Antrim NH](https://www.antrimnh.org/conservation-commission/pages/slope),
  [Southern Tier planning](https://www.stcplanning.org/wp-content/uploads/2021/07/DeterminingSlope.pdf)):

  | Slope | Reading |
  |---|---|
  | 0 to 5% | flat to gentle, the easiest to build on |
  | 5 to 10% | moderate |
  | 10 to 15% | moderately steep |
  | 15 to 25% | steep: engineered walls and drainage |
  | over 25% | not developable without great cost |

  The map states its units (percent or degrees) and the terrain's resolution.
- **Elevation, aspect, water.**
  - Contours are coloured by height, a hypsometric ramp from low to high.
  - Aspect is read for warmth: north-facing slopes are cold in the north.
  - Water is followed downhill cell by cell to flow lines, catchments and ponds (the D8 method,
    which the app's rain flow uses since V143). Flood zones come from the agency's map (FEMA's
    NFHL in the US).
- **What V165 does (and why).**
  - **The ground at site scale.** The context's terrain is a 25 by 25 grid over 600 m, a point
    every 25 m: one point for a whole building. Analyze site fetches the same free tiles (AWS
    Terrain Tiles, about 3.7 m a pixel at 40 degrees north at zoom 15) for 150 m around the site and
    samples them every 5 m, kept with the project in metres above sea level so every analysis runs
    again offline. A surface of the project's own (a survey, LandXML) is used instead where it
    covers the site; with neither, the context's terrain, its 25 m said. The source's own
    resolution is named on every element: the tiles carry 3DEP's 10 m or finer in the US and SRTM's
    30 m elsewhere, so 5 m is a sampling, not a measurement.
  - **Slope and aspect by Horn's method** (Horn, 1981, "Hill shading and the reflectance map"):
    the fall across each cell from its eight neighbours, the centre ones counted twice; GDAL's
    default ([xdem, terrain attributes](https://xdem.readthedocs.io/en/latest/terrain.html)). The
    edge cells take their own value for a missing neighbour. Aspect is measured clockwise from true
    north; under 2% a cell is flat.
  - **Slope in the five classes above**, the steeper the darker and more saturated, as Esri's
    Mapping Center maps slope ([aspect-slope map](https://www.esri.com/arcgis-blog/products/product/mapping/aspect-slope-map));
    yellow to dark red, a sequential scheme that reads without red-green vision. 15% and 25% are
    the breaks many ordinances use ([steep slopes, InRoads](https://communities.bentley.com/products/road___site_design/b/road_and_site_design_blog/posts/creating-a-steep-slopes-analysis-with-inroads-view-color-coded-slopes-tool),
    [slope for site planning](https://atlas.co/blog/how-to-map-slope-for-site-planning/)).
  - **Aspect read for warmth**: the slopes facing the equator warm (orange to red), those facing
    the pole cool (blues), east and west between; a diverging scheme with a neutral middle, turned
    for a site south of the equator. GIS's own default is a rainbow round the compass, which says
    which way, not what it means for a building.
  - **Contours** every 0.25 to 50 m, the step giving at most 24 lines over the area, every fifth an
    index contour, thicker and labelled with its height above sea level; coloured on a hypsometric
    ramp, green low to brown high.
  - **Water.** The ground is filled by Priority-Flood (Barnes, Lehman and Mulla, 2014), each cell
    raised to the lowest level water could leave it by, a little more every step so even a flat
    drains; then each cell drains to its steepest neighbour (D8, O'Callaghan and Mark, 1984). Flow
    lines are the cells draining 0.25 ha or more, ordered by Strahler's rule (two streams of one
    order make the next), drawn wider by order, each with an arrowhead where it runs out. Catchments are the cells
    draining to one outlet; the large ones (4% of the ground or more) are named at their middles,
    and the divide between two of them is drawn once, dashed, along the edges between their cells,
    its steps eased to within a cell.
    Outlining each catchment on its own drew every divide twice, the two dash patterns out of step. For
    the site: the land whose water reaches it, and where it leaves. Ponds are where the filled
    ground stands 10 cm or more above the real one: their depth, area and volume, the deepest point
    marked.
  - **Flood zones from FEMA's National Flood Hazard Layer** (layer 28, the preset V134 added),
    US sites only. The Special Flood Hazard Area, the 1% annual chance flood (zones A, AE, AH, AO,
    AR, A99, V, VE), in blue; the regulatory floodway, the channel kept free of building, in crimson
    over it; shaded zone X, the 0.2% annual chance flood, in orange; zone D, not determined, in
    grey; unshaded X, minimal hazard, not drawn. The base flood elevation, where given, in its
    feet and in metres. The colours follow the FIRM's convention of blue for the base flood; FEMA's
    own renderer could not be read from the build environment, whose proxy refuses FEMA's host
    ([NFHL zones](https://emilms.fema.gov/is_0273/groups/36.html)).

## 3. GIS scientists: what can be seen, and how a map is made

- **Viewshed.**
  - Computed on a surface from an observer's eye height (Esri's default is 1.75 m) to a target
    height.
  - The bare-earth version ignores buildings and trees, so a surface with the buildings on it
    (a DSM) is the one that tells views in a town
    ([Esri, Using viewshed](https://pro.arcgis.com/en/pro-app/latest/tool-reference/3d-analyst/using-viewshed-and-observer-points-for-visibility.htm),
    [Viewshed, ready to use](https://pro.arcgis.com/en/pro-app/latest/tool-reference/ready-to-use/viewshed.htm)).
- **Isovist.**
  - The area visible from a point (Tandy 1967, Benedikt 1979): its area, perimeter and how much
    of its edge is hidden behind something. Visibility graphs (Turner 2001) extend it to a grid
    ([Isovist](https://en.wikipedia.org/wiki/Isovist)).
  - For a site, an isovist at eye height and from the upper floors, against the context's
    buildings, finds the open directions. What lies in each open direction (water, a park, a
    landmark, open land, high ground) makes it a view worth drawing.
- **The map's parts.**
  - A title naming the subject, place and time, a legend, a scale bar with round numbers, a
    small north arrow, the data's source and its date.
  - In that order of weight after the theme itself: the theme dominates and the base recedes
    (Monmonier) ([map elements](https://atlas.co/courses/gis-basics/map-elements-and-layout/),
    [basic cartographic design](https://gsp.humboldt.edu/OLM_2019/Courses/GSP_270_Online/Additional_Resources/BasicCartographicDesign.pdf),
    [layout hierarchy](https://michaelminn.net/tutorials/arcgis-pro-layout)).

## 4. Transportation planners: getting to and from the site

- **How practice draws movement.**
  - A UK parameter plan for access and movement keys the primary vehicle routes, the pedestrian
    routes, the routes closed to through traffic and the vehicle access points, with arrowheads
    for the direction of movement. The access points are marked provisional until the detailed
    design ([Sutton, parameter plan 3](https://www.sutton.gov.uk/documents/d/guest/cde-6-parameter-plan-3-access-and-movement)).
  - Masterplans draw a route hierarchy by line weight and kind: a main access road, secondary
    roads, pedestrian-priority streets, primary, secondary and green walking routes, the bus stops
    marked ([Dublin, landscape rationale](https://www.pleanala.ie/publicaccess/EIAR-NIS/310350/3.%20%20%20Reports/8.%20%20%20Landscape%20Rationale.pdf)).
    Design codes class streets from principal streets down to lanes
    ([Cheshire West and Chester](https://www.cheshirewestandchester.gov.uk/documents/planning-and-building-consultancy/total-environment/PRDG/3.3-Street-Hierarchy-1.0.pdf),
    [Nottinghamshire](https://www.nottinghamshire.gov.uk/media/sb4b0xzx/21-hierarchy-and-well-connected-streets.pdf)).
  - Design guides put pedestrians first, then cyclists and public transport, motor vehicles last.
    They check walks of 400 m (5 minutes) to a bus stop and local green space, and 800 m (10
    minutes) to shops and a primary school
    ([North Norfolk design guide](https://designguide.north-norfolk.gov.uk/sections/residential-development/movement-connectivity)).
  - So a movement diagram is one plan: the streets by their role, the walking routes dashed, the
    cycle routes by their stress, the stops and their lines, the walk times as bands along the
    streets, the vehicle entries and parking as arrows and hatched areas, each in the key.
- **PTAL** (Transport for London's method, first used in Hammersmith and Fulham in 1992):
  - From the point, the walk to each stop within reach: 8 minutes to a bus stop, 12 to a rail
    station, at 4.8 km/h (640 and 960 m).
  - Each line's scheduled waiting time is half its headway, plus a reliability allowance: 2
    minutes for a bus, 0.75 for rail. The walk and the wait make the total access time, turned into
    an equivalent doorstep frequency: 30 / total minutes.
  - Per mode, the best line counts in full and the others at half. Their sum is the accessibility
    index, banded 0, 1a (0.01 to 2.5), 1b (to 5), 2 (to 10), 3 (to 15), 4 (to 20), 5 (to 25), 6a
    (to 40) and 6b (over 40)
    ([Camden's TfL report](https://camdocs.camden.gov.uk/CMWebDrawer/Record/4813966/file/document),
    [UNECE, the bands](https://unece.org/sites/default/files/2025-05/ECE-TRANS-WP.6-2025-04E_0.pdf),
    [TfL's glossary](https://tfl.gov.uk/info-for/urban-planning-and-construction/planning-with-webcat/glossary),
    [PTAL](https://en.wikipedia.org/wiki/Public_transport_accessibility_level),
    [the method](https://blog.podaris.com/ptal-accessibility-analysis/)).
  - **The headways, free and keyless.** OpenStreetMap's route relations may carry `interval`, the
    headway as an estimate, with `interval:conditional` for times of day
    ([Key:interval](https://wiki.openstreetmap.org/wiki/Key:interval)); it is rarely mapped.
    Timetables proper are GTFS feeds. The Mobility Database catalogues them, but its API wants a
    token, and a feed's host may not let a page read it
    ([Mobility Database](https://mobilitydatabase.org/about)).
  - **Transitous**, a volunteer-run router over the world's open GTFS feeds on the MOTIS engine
    (MIT), needs no key. MOTIS answers every request with `Access-Control-Allow-Origin: *` (its
    `net` library's `enable_cors`, read from its source), so a page may call it. Its
    `/api/v6/stoptimes` takes a centre, a radius, a time and a window. One request (the site, 960 m,
    a weekday at 8:00, an hour, scheduled times only) gives every departure from every stop within
    reach, with its route and direction: every line's headway, and PTAL in full. Its terms
    ([API policy](https://transitous.org/api/), [sources](https://transitous.org/sources/)): no
    commercial use; the app's source code under an open-source licence (this repository has none
    of its own yet, only `THIRD_PARTY_NOTICES.md`); a visible link to its sources page and
    OpenStreetMap's attribution; a contact on the site that serves the app, the Referer standing in
    for the User-Agent a page cannot set; light use, contact first for heavy use. One request a run
    is light.
  - **A GTFS file dropped in** is read locally, with no key. The build already holds a zip reader
    (fflate 0.8.3's `unzipSync`, inside V163's SketchUp reader). A big city's `stop_times.txt`
    runs to hundreds of MB, so it is scanned for the stops within reach, not read whole.
  - **Drawn as:** each stop within reach with its lines and its walk in minutes; the catchment
    along the streets out to 8 and 12 minutes; the index and its band where it can be worked out.
    TfL's map runs from blues at 0 to dark red at 6b; its exact colours could not be read from
    here, and a rainbow reads badly without red-green vision. The bands go on a sequential scale
    of the app's own, checked with the dataviz validator, and the key says the method is TfL's.
- **Walk Score.**
  - Full points for a place within a 5-minute walk (0.25 mile), decaying to none at 30 minutes
    (about 1.5 miles), in about nine weighted categories, groceries highest.
  - Less for long blocks (over 120 m) and few intersections (under 200 a square mile)
    ([Walk Score methodology](https://walkscore.com/methodology),
    [Census workshop](https://lehd.ces.census.gov/doc/workshop/2012/Palma.pdf)).
- **Level of traffic stress** for cycling:
  - LTS 1 (most children would ride it) to LTS 4 (the strong and fearless only), from lanes,
    speed and the kind of bike facility. A street is as stressful as its worst feature, and a route
    as its worst link (Mekuria, Furth and Nixon, MTI report 11-19, 2012). Furth's later tables
    (v2.0, 2017; v2.2, 2022) add daily traffic, which open data does not carry
    ([LTS](https://peterfurth.sites.northeastern.edu/level-of-traffic-stress),
    [JTLU, revision 2.0](https://www.jtlu.org/index.php/jtlu/article/download/1159/1134),
    [Boston's guide](https://www.boston.gov/sites/default/files/file/2020/12/Bicycle%20Level%20of%20Traffic%20Stress%20Report%20%26%20Guide%20for%20Large%20Developments.pdf)).
  - **The 2012 criteria need only what OpenStreetMap maps:** speed (`maxspeed`), lanes, class
    (`highway`), the bike facility (`cycleway`, `cycleway:left` and `:right`) and parking by side
    (`parking:left`, `:right`, `:both`). The mixed-traffic table, for 2 to 3, 4 to 5 and 6 or more
    lanes: up to 25 mph, LTS 1 or 2, 3, 4; at 30 mph, 2 or 3, 4, 4; at 35 mph and over, 4. The lower
    value is for a residential street, or one without a marked centreline
    ([Princeton's reproduction](https://www.princetonnj.gov/DocumentCenter/View/1697/Appendix-A---Level-of-Traffic-Stress-PDF)).
    Bike Ottawa's model (below) is the same table in km/h. The bike-lane tables (a bike lane and
    parking lane together 15 ft or wider LTS 1, 14 to 14.5 ft LTS 2, narrower LTS 3; a bike lane
    without parking 6 ft or wider LTS 1) are only partly confirmed by what could be read here
    ([MTI 11-19](https://transweb.sjsu.edu/sites/default/files/1005-low-stress-bicycling-network-connectivity.pdf),
    [MC Atlas, modified LTS](https://mcatlas.org/bikestress/documentation/ModifiedLevelOfTrafficStressMethodology.pdf)).
  - **Crossings.** An unsignalized crossing without a median refuge, by the crossed street's speed
    and lanes (up to 3, 4 to 5, 6 or more): up to 25 mph LTS 1, 2, 4; 30 mph 1, 2, 4; 35 mph 2, 3,
    4; 40 mph and over 3, 4, 4. A refuge lowers some cells, not all readable here
    ([Furth, Mekuria and Nixon, 2016](http://www1.coe.neu.edu/~pfurth/Furth%20papers/2016%20Network%20Connectivity%20for%20Low-Stress%20Bicycling.pdf)).
    OpenStreetMap marks the controls: `highway=traffic_signals`, `highway=stop`,
    `crossing=traffic_signals`, `crossing:island=yes`.
  - **Two open implementations from OpenStreetMap, read as text from their code:**
    - PeopleForBikes' Bicycle Network Analysis (`azavea/pfb-network-connectivity`, Apache 2.0)
      rates a street only low or high stress. Where a tag is missing it assumes: primary and
      secondary 40 mph and 2 lanes a direction; tertiary 30 mph and 1 lane; unclassified 25 mph and
      1 lane; residential the city's or state's default speed; parking on both sides, 8 ft parking
      lanes, 5 ft bike lanes, a 27 ft residential roadway. Motorways and trunks are high stress,
      paths low, living streets low unless `bicycle=no`. A lesser street crossing a main one with
      no signal or stop sign is high stress by the main street's lanes and speed, eased by a rapid
      flashing beacon or an island.
    - Bike Ottawa's stress model (`BikeOttawa/stressmodel`, MIT, 2018) rates LTS 1 to 4: separated
      paths and `cycleway=track` LTS 1; mixed traffic at up to 40 km/h LTS 2 on a residential street
      of up to 3 lanes, 3 otherwise and with 4 to 5 lanes, 4 above; at up to 50 km/h LTS 2 on a
      residential street of under 3 lanes, 3 up to 3 lanes, 4 above; over 50 km/h LTS 4. It assumes
      2 lanes, and 100 km/h on a motorway, 80 on a primary or secondary road, 50 elsewhere. It does
      not model bike-lane widths or direction, and adds a rule of its own: a bike lane on a street
      that is not residential is LTS 3 at least.
    - Both say every assumption with each street
      ([OSM Cycling Quality Index](https://github.com/SupaplexOSM/OSM-Cycling-Quality-Index),
      [Boston Cyclists Union's map](https://labs.bostoncyclistsunion.org/map/lts/),
      [OSM's accuracy for LTS](https://journals.sagepub.com/doi/ref/10.1177/0361198119836772)).
  - **Low-stress connectivity**, the method's main point: mapped alone, the low-stress streets fall
    into islands. Two points are connected when a path at LTS 2 or less is at most 25% longer than
    the shortest; San Jose's study counted the home-to-work trips so connected
    ([MTI 11-19](https://scholarworks.sjsu.edu/mti_publications/74)). For a site: the streets it
    reaches at LTS 2 or less within that detour, its low-stress reach.
  - **Drawn as:** each street in its level, named in plain words (Boston's labels: carefree,
    easygoing, tense, white knuckles). The common green-yellow-orange-red fails red-green vision, so
    a blue to red scale (blue LTS 1, light blue, orange, red), checked with the validator.
- **Street hierarchy and traffic.** Streets are classed by function. FHWA's typical daily traffic
  by class, when a street has no count
  ([FHWA functional classification](https://www.fhwa.dot.gov/planning/processes/statewide/related/highway_functional_classifications/section03.cfm)):

  | Class | Rural | Urban |
  |---|---|---|
  | Interstate | 12,000 to 34,000 | 35,000 to 129,000 |
  | Other freeway or expressway | 4,000 to 18,500 | 13,000 to 55,000 |
  | Other principal arterial | 2,000 to 8,500 | 7,000 to 27,000 |
  | Minor arterial | 1,500 to 6,000 | 3,000 to 14,000 |

  Collectors and local streets still need their source. FHWA's HPMS carries counted traffic for
  the federal-aid roads, state by state on geo.dot.gov, which the build environment could not
  reach.
- **Vehicles: entries and parking.**
  - Entries: `highway=service` with `service=driveway` (one property's, with no default access, so
    its `access` is read), service roads meeting the lot's frontage, and `entrance=*` on the
    buildings; drawn as arrows across the frontage, provisional, as a parameter plan marks them
    ([service=driveway](https://wiki.openstreetmap.org/wiki/Tag:service%3Ddriveway)).
  - Parking: car parks, `amenity=parking` with `parking=surface`, `multi-storey`, `underground` or
    `street_side`; on-street parking by side on the street line, `parking:left`, `:right` and
    `:both`, the current scheme
    ([parking:both](https://wiki.openstreetmap.org/wiki/Key:parking:both),
    [street parking](https://wiki.openstreetmap.org/wiki/Wiki:Street_parking)).
- **What V166 will do (and why).** V161 already fetches the network, the places, the stops and
  their lines, and works out walk times from the lot (`research-access-people.md`). V166 draws
  them, and what follows from them, as six live, editable layers of the same button:
  1. **Street hierarchy:** every street by its role, the weight by class, names and speeds on the
     main ones, the frontage streets outlined.
  2. **Cycling stress:** each street in its LTS by the 2012 criteria, its assumptions said; the
     unsignalized crossings of main streets by the 2016 table; the site's low-stress reach. Off at
     first.
  3. **Transit:** the stops within 8 and 12 minutes with their lines; the catchment; PTAL from
     Transitous's departures if its terms are accepted, else where OpenStreetMap maps the
     headways, a floor where some are not.
  4. **Walk times:** the network in 5, 10 and 15-minute bands from the lot, as lines along the
     streets.
  5. **Daily needs:** the way to the nearest of each kind, in minutes; the 400 m and 800 m checks
     of the design guides; the crossings (`highway=crossing` with `crossing=*`) where the ways
     cross a main street.
  6. **Vehicle access and parking:** driveways and entries at the frontage, car parks by kind,
     on-street parking by side.

  Findings: the streets the lot fronts and their stress; transit (PTAL, or the stops within
  reach); the daily needs within 10 minutes; where vehicles can enter.

  Open before coding:
  - the 2012 bike-lane cells and the crossing table's refuge cells, against the report;
  - for the owner: Transitous's terms (an open-source licence for the app, no commercial use, a
    contact on the site);
  - whether a GTFS drop is in V166 or later.

  The build environment refuses most web hosts (Furth's pages, the MTI report and its mirror,
  Wikipedia, TfL, geo.dot.gov): the facts above come from search results, their sources linked,
  and from code read from raw.githubusercontent.com as text, never run.

## 5. Acoustic analysts: noise

- **The UK method (CRTN, 1988).**
  - The basic level is L10(18h) = 29.1 + 10 log10 Q dB(A), 10 m from the nearside kerb, where Q
    is the 18-hour flow, at 75 km/h with no heavy vehicles and a level road.
  - Speed, heavy vehicles, gradient, surface and distance are corrections to it. It holds to
    about 300 m
    ([CadnaA, CRTN](https://doku.datakustik.com/CadnaA/en/Str_CRTN.html),
    [Noisemap](https://www.noisemap.ltd.uk/wpress/features/calculation-methods/)).
  - The distance term, the ground term and the conversion to LAeq and Lden are still to be
    checked against the 1988 document itself. TRL's linear conversions exist, and are argued
    over ([TRL conversion](https://programmeofficers.co.uk/Aylesbury/CD/CD%209.11.pdf),
    [is CoRTN an Leq procedure](https://acoustics.asn.au/conference_proceedings/AAS2008/papers/p25.pdf)).
- **The EU method (CNOSSOS-EU).** It needs flow, speed and vehicle mix per road. Europe-wide
  studies simplify it to the noisiest façade, the one nearest the busiest road
  ([CNOSSOS-EU in Ireland](https://www.sciencedirect.com/science/article/pii/S0003682X22000664)).
- **How it is drawn.**
  - 5 dB bands, in the colours of DIN 18005-2 and UNI 9884: light green under 35 dB, through
    yellow and orange to red, violet and blue at 80 and over.
  - A known weakness: 40 to 45 can be mistaken for 60 to 70. Diverging schemes are proposed
    instead ([NoiseModelling colour scheme](https://noisemodelling.readthedocs.io/en/latest/Noise_Map_Color_Scheme.html),
    [a colour scheme for sound](https://www.conforg.fr/euronoise2015/proceedings/data/articles/000069.pdf),
    [colours in END maps](http://www.carreteros.org/explotacion/2012/6.pdf)).
- **What the app can honestly do.** Open data carries a road's class, lanes and speed limit, and
  almost never its traffic. So the level is a screening estimate: the class's typical flow (§4)
  through the basic formula, at the site's nearest façade. It is labelled as an estimate, with
  the assumptions named, and a survey is recommended where it matters.
- **What V164 does (and why), found by drawing it.**
  - The distance term as built: −10 log10(d′/13.5), d′ the slant distance from a line 3.5 m in from
    the kerb and 0.5 m up, to a point 4 m up. It is 0 dB at 10 m from the kerb, as the basic level
    requires; the speed and heavy-vehicle correction is 0 dB at 75 km/h with none heavy. No class
    reaches past 300 m.
  - **Unscreened, the map says nothing.** Drawn as plain bands, a motorway's 65 dB class reached the
    300 m limit on both sides and every class covered every street around the site. Real noise
    maps are canyons: loud along the street, quiet behind the first row of buildings. So each class
    is now found every 15 m along the road, on each side, out to the first building, and behind it
    the level is less the building's screening.
  - **The screening is ISO 9613-2's barrier term** at 500 Hz: Dz = 10 log10(3 + 20 z / λ), z the
    path over the building's roof less the straight path, λ = 0.686 m; nothing where the roof is
    under the line of sight; at most 20 dB, the standard's limit for one edge. Mixing it with CRTN is
    a screening estimate's licence, and it is said so. Only the first building on a line counts, and
    the ground is taken as hard, so the estimate still errs loud.
  - **Colours.** DIN 18005's named classes from 55 dB: orange, red, crimson, violet, blue. The
    standard's exact RGB values are not free, so the colours are the app's own, after the names.
  - **Traffic.** FHWA's typical daily ranges by functional class, the urban figure where 40 or more
    buildings stand in the context, the rural otherwise; a slip road a quarter of its road. The urban
    collector and local figures are the app's assumption, said so in Properties.

## 6. Analysts and planners: land use and form

- **Land use colours** (APA's Land Based Classification Standards, activity, first digit):

  | Activity | Colour |
  |---|---|
  | 1000 residential | yellow |
  | 2000 shopping, business or trade | red |
  | 3000 industrial | purple |
  | 4000 institutional and infrastructure | blue |
  | 5000 travel and movement | grey |
  | 6000 mass assembly | dark slate grey |
  | 7000 leisure | light green |
  | 8000 natural resources | forest green |

  Real maps vary. Copies of the table disagree on hex codes, so the RGB values are the ones to
  use ([LBCS colour codes](https://www3.uwsp.edu/cnr-ap/clue/Documents/Comprehensive_Planning/Land_Use_Resource_Guide_Appendix_C.pdf),
  [LBCS tables](https://planning-org-uploaded-media.s3.amazonaws.com/legacy_resources/lbcs/standards/pdf/InOneFile.pdf)).
- **Figure-ground.** The buildings solid, the open space empty (after Nolli's plan of Rome, 1748).
  It shows grain, enclosure and the gaps between buildings.

## 7. What this means for the app

### The button

**Analyze site** needs only where the site is: an address found on the map, or the latitude and
longitude already set. It does the rest:
- It fetches everything at once: the context (buildings, roads, land use, water, green, terrain),
  the climate, access and people, and the zoning where a council layer has it.
- It runs every analysis on what came back.
- Each source is listed as it arrives, or by name when it fails.
- The time zone comes with the climate, so the sun needs no typing.
- One undo step.

### Live and editable

- Each analysis is a group of diagram layers under Layers > Site analysis. Each element is an
  object: select it, move or rotate it, change its colour, line or label, or delete it.
- Run again refreshes what you have not touched. What you changed is kept and marked as yours;
  **Reset** gives it back to the analysis. What you deleted stays deleted until the layer is
  reset.
- Properties says what an element is, its numbers, how they were worked out, and the source with
  its date.
- Diagram elements are not building elements: they stay out of schedules, quantities, the LOD
  checks and the IFC and CityJSON exports.

### Drawn professionally

- One idea per layer, in the standard colours above: noise in DIN 18005's bands, land use in
  LBCS, slope in its five classes, elevation on a hypsometric ramp.
- A legend for each layer, the compass ring as the north arrow, the distance rings as the scale,
  and the source credited on the element and in the legend.
- Plan and 3D draw the same elements: the sun's paths as arcs in the sky over the site, the rest
  on the ground.

### What goes from Analyze

- The stages, the questions and the brief, the typed findings, the photographs and the
  checklists. What a project stored stays in its file.
- Findings the analyses write from the data stay, as sentences on their layers.

### In four phases, each adding layers to the same button

1. **V164, the button and the climate around the building:**
   - the engine (live, editable, kept through a re-run);
   - the compass and distance rings;
   - the sun's three paths with their hours, and the sun now;
   - the shadows at 9, 12 and 15 on both solstices and the equinox;
   - the winds by season, and the strongest;
   - the views (an isovist at eye height and from the top floor, against the context);
   - the noise (the screening estimate above).
2. **V165, land and water:** contours by height, slope classes, aspect, flow lines and catchments,
   ponds, flood zones.
3. **V166, movement:** the street hierarchy, cycling stress, stops and lines with their 8- and
   12-minute catchments, walk times, the way to each daily need, and vehicle entries and parking.
4. **V167, land:** land use in LBCS colours, figure-ground, green and trees, zoning.

The tools-and-synthesis phase (the old SA5) and the contents pane follow, on these layers.
