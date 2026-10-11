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
    draining to one outlet; the large ones are outlined, dashed, as the divides between them. For
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

- **PTAL** (Transport for London):
  - Rates a place from 1a to 6b from the walk to the nearest stops (up to 8 minutes for a bus,
    12 for rail) and how often each line runs.
  - Without timetables, the stops and the lines that call at them are what can be shown
    ([PTAL](https://en.wikipedia.org/wiki/Public_transport_accessibility_level),
    [the method](https://blog.podaris.com/ptal-accessibility-analysis/)).
- **Walk Score.**
  - Full points for a place within a 5-minute walk (0.25 mile), decaying to none at 30 minutes
    (about 1.5 miles), in about nine weighted categories, groceries highest.
  - Less for long blocks (over 120 m) and few intersections (under 200 a square mile)
    ([Walk Score methodology](https://walkscore.com/methodology),
    [Census workshop](https://lehd.ces.census.gov/doc/workshop/2012/Palma.pdf)).
- **Level of traffic stress** for cycling:
  - LTS 1 (children) to LTS 4 (strong and fearless), from lanes, speed and the kind of bike
    facility.
  - A route is as stressful as its worst link (Mekuria, Furth and Nixon 2012; Furth's tables
    v2.2, 2022) ([LTS](https://peterfurth.sites.northeastern.edu/level-of-traffic-stress),
    [Boston's guide](https://www.boston.gov/sites/default/files/file/2020/12/Bicycle%20Level%20of%20Traffic%20Stress%20Report%20%26%20Guide%20for%20Large%20Developments.pdf)).
- **Street hierarchy and traffic.** Streets are classed by function. FHWA's typical daily traffic
  by class, when a street has no count
  ([FHWA functional classification](https://www.fhwa.dot.gov/planning/processes/statewide/related/highway_functional_classifications/section03.cfm)):

  | Class | Rural | Urban |
  |---|---|---|
  | Interstate | 12,000 to 34,000 | 35,000 to 129,000 |
  | Other freeway or expressway | 4,000 to 18,500 | 13,000 to 55,000 |
  | Other principal arterial | 2,000 to 8,500 | 7,000 to 27,000 |
  | Minor arterial | 1,500 to 6,000 | 3,000 to 14,000 |

  Collectors and local streets still need their source.

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
