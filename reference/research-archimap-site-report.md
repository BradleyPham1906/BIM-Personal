# archiMap's one-click site report: what it does, and where the app stands

The owner, 2026-11-01, with a video of archiMap (MassLabs) titled "One click on Site Analysis": "watch this video and see
how this app archimap do the site analysis. our current is not to this point yet and i want this." This note records
what was seen, at what level, against what the app has, as the input to the plan's decision. No code has changed.

## 1. Sources

| Source | What was read | Date | Level |
|---|---|---|---|
| The owner's video, 27.0 s, 720 x 1280 (a phone recording), AV1 with an audio track | 27 frames, one a second, at full size; the scene changes at 1.8, 2.5, 5.6, 6.5 and 18.7 s. The sound has no silences and no words were transcribed (no speech engine here); what follows is the screen's. | 2026-11-01 | P (the product's screen) |
| archimap.masslabs-archi.com | "Site analysis in one minute. 195 countries · 100+ layers · 350+ datasets · building data 8+ · parcel data 5+ · true-width roads · 3D terrain"; "+2.5B buildings worldwide"; the source of every building dataset credited | 2026-11-01 | P |
| masslabs-archi.com | plans: the site report on Pro (4 km2, 20 uses a month) and Max (9 km2, 30), not on Plus or the trial; exports PNG, SVG, DXF, PDF; 3DM, SKP, RVT, STL; Colorgram | 2026-11-01 | P |
| `reference/research-analysis-workspace.md` | archiMap's earlier video (2026-10-25): its light workspace, its style card and Ratios | 2026-10-25 | P |

## 2. The flow (the video's own captions, 7 to 20 s)

1. **"Go to archiMap":** search a place; Area as a circle, a rectangle or a polygon (a diameter of 948 m, then 1,000 m:
   0.79 km2); Date and time (annual, monthly, daily; a season; the solar time; day or night).
2. **"Click 'load info' button":** the area's map loads inside the circle: buildings, roads at their true width,
   parcels, trees, water; Unlock area, Recenter.
3. **"Click 'site' icon & calculate":** among the tools (Diagram, Explode, Ratios, Analysis, Laser cutting, Section,
   Site report), Site report: "Click [Get started] -> in Site, click [Draw site] or [Parcels] -> [Done] -> choose a
   business type -> [Calculate]". Planned business: restaurants, cafes and bars, retail, personal services, health,
   education, finance and real estate, offices and professional, hotels, culture and leisure, automotive. Then
   "Calculating... 22 / 25".
4. **"Customize color":** the report in a viewer (a page strip, "Site location 2 / 20"), Colorgram's palette of four
   colours (each locked, shuffled, copied, edited) from 120 palettes (Concrete, Brick, Wood, Mono, Soft, Light, Dark,
   Cold, Pastel, Vintage, Autumn, Winter, Earth, Sea, Sunset, Night), Generate, Apply: every page takes the palette.
   Format: PDF, PowerPoint.

## 3. The report's pages seen (20 in all; New York, Hudson Yards)

| Page | Title | What it shows |
|---|---|---|
| 2 | Site location | Rings of 1, 2 and 3 km with the people living in each (42,549; 165,858; 469,543); the country and the city with the site; address, borough, district, parcels, coordinates |
| 4 | Climate 2/2 | Air quality by month (PM2.5, PM10, NO2) against WHO's guideline, days over it (123 of 365); outdoor comfort by month (cold, cool, comfortable 9 to 26 C, hot, extreme heat), the share comfortable (33%), the best and worst months; solar radiation by month (direct and diffuse), annual GHI and DNI; a radiation rose (the radiation on vertical surfaces by direction, its peak) |
| 5 | Site views (3D) | The site in the 3D model from the SW and the NE, land use coloured, shadows |
| 7 | Site status | The site in 3D, land use coloured (residential, mixed use, commercial, industrial, public, infrastructure, parking, woods, grass, shadow), six numbered viewpoints with arrows, and their six views (from the S, SW, NW, N, NE, SE) |
| 7 (another report) | Site section | Two sections 6 km long through the site at x3 vertical: terrain (DEM), buildings (Overture's heights), roads and water (OpenStreetMap), subway stations, a land-use band under it; an isometric block of the city around the site |
| 9 | Street context | The walk to the nearest station (34th Street-Hudson Yards, 7 min) and the bus stops (4 min), landmarks, each road's measured width; the station catchment grade, the roads adjacent |
| 11 | Site overview | The site's parcels and their numbers, its area (5,951 m2), land category, zoning (C2-8) and the zoning shares within 300 m; the site's elevation: 1 m contours, the corners' levels, the edges' lengths, lowest, highest, mean slope |
| 12 | Surrounding lots and footprints | Within 200 m: parcels by area, footprints by area; treemaps of the shares; each by distance from the site; the median and the largest, the site against them |
| 14 | Surrounding height and floors | Within 200 m: heights and storeys by class, their shares, by distance; median and maximum |
| 15 | Surrounding BCR and FAR | Within 200 m: building coverage and floor area ratio by parcel, their shares, by distance |
| 18 | Vehicle in/out flows (estimate) | The share of traffic in and out on each road around a 160 m ring (bigger and longer roads carry more, the formula printed); congestion (speed as a share of free flow); traffic noise per cell against 55 dB (WHO) |
| 20 | Business mix | Businesses within a 5 and a 10 minute walk by category (3,314 and 364), by distance and walking distance; the planned business type's neighbours: the nearest, how many within 480 m and 800 m |

Each page: a map or figure, a few numbers in a side panel, one sentence that says what it means, the method in small
print. Every number is the site's.

## 4. Where the app stands (P, its code and records)

**Already there, in its own form:** Analyze site in one click (V164) and the analysis workspace (V171b, V171c); the
location and context (V157, V168: land use, figure-ground, green and trees); zoning and yield (V160); access and people
(V161, V166: streets, cycling, transit, walking, daily needs); climate and risk (V159: temperature, rain, wind, sun
path, degree days, solar, a psychrometric chart, PM2.5, earthquakes); landform and water (V165: terrain, contours,
slope, aspect, flow, ponds, FEMA's flood); noise from roads (V164); traffic and people (V171); the sun path (V171d);
the analysis tools and buildable area (V172); three boards as pages of the set, printed (V159 to V162).

**Coming:** in V172b, outdoor comfort by UTCI in four conditions (archiMap's comfort by month is the same kind of
figure), the psychrometric chart with comfort and strategies, design days, and the boards made editable (any
analysis on any board, boards of one's own); in V172c, radiation on surfaces (archiMap's radiation rose is Ladybug's
`RadiationRose`); V173 to V176, the Contents pane, designed boards, live elements, styles and export, ending in a
Site Analysis report of eight boards (PIPELINE).

**Not there:** the report itself: one action that makes every page, in order, from one site and one area; people
within 1, 2 and 3 km; air quality by month for PM10 and NO2; the radiation rose; 3D views from numbered viewpoints;
site sections; the walk to the nearest station with its time; parcels with their numbers, zoning shares within 300 m,
corner levels; the statistics of the lots, footprints, heights, storeys, coverage and FAR within 200 m against the
site; vehicle flows and congestion; businesses within a walk and the planned business's neighbours; a palette applied
to every page; PowerPoint.

## 5. Data each missing page would need (to research and test, U until then)

People within rings (WorldPop or GHSL population grids, or a national census); businesses (OpenStreetMap through
Overpass, or Overture's places); building heights and storeys (OpenStreetMap's tags, Overture's buildings, as
archiMap credits for its sections); parcels and zoning (city open data where it exists, as V160 reads); PM10 and NO2
(Open-Meteo's air quality API, as V159 reads PM2.5); congestion (no free keyless source known: to research);
stations and walking times (V161's and V166's sources). Each to be tested from here, its licence read, as the
protocol asks.

## 6. The decision for the owner

Where this sits in the plan: after V172b (whose editable boards are the report's pages and whose comfort is its
climate figure), as the next phase; or now, pausing V172b; or where the plan has it, in V176 after V173 to V175.
