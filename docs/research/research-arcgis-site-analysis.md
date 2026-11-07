# Research: how ArcGIS builds its analysis tools, and a site-analysis dashboard

The owner (V156): "ArcGIS has really good documentation and their app is really good at this. Take a
good look on how they develop their tools. Presentation should include analysis and charts and stuff
for quick and easy presentation about site analysis." The owner also showed four things: a GIS layer
stack diagram, ArcMap's suitability analysis, ArcGIS Pro's Contents pane and New Layout gallery, and
UrbanEyes' site dashboard.

This note records patterns, in our own words. Esri's and UrbanEyes' text, images and code are theirs.
We rebuild the ideas, not the products, and the owner's screenshots are not committed.

## 1. What ArcGIS gets right

**Everything is a layer, in one stack.** A map is a stack of thematic layers in one coordinate
system: imagery at the bottom, then parcel framework, parcels, addresses and uses, rights, and
administrative areas. Each layer is a table of features with a geometry. Analysis reads layers and
writes new layers. The owner's first picture is this idea.

**The Contents pane** is the map's table of contents. It lists the same layers in several ways:
- **Drawing order:** top draws over bottom. You drag to reorder, and the eye box shows or hides.
- **By source:** which file or service each layer comes from, and whether it is broken.
- **By selection:** which layers can be selected, and how many features each has selected.
- **By editing**, by snapping and by labeling: per-layer switches for those modes.

Each layer has a legend patch under its name, so the pane is also the legend. Its Properties hold:
- symbology, by category, graduated colours, or a stretch for rasters such as the DEM;
- labels and a definition query (show only the features that match an expression);
- elevation, time, and the display range by scale.

**The geoprocessing pane.** Every tool, about 1,800 of them, opens in the same pane, in the same
shape:
- parameters, each with a type (a layer, a field, a distance with units, a value list), checked as
  you fill them in, with a warning or an error beside the field;
- environments (extent, cell size, the coordinate system of the output);
- Run; then messages, with the duration, warnings and the output;
- every run kept in History, so you can open it again with the same parameters, or rerun it.

Outputs are added to the map as new layers. **ModelBuilder** chains tools into a graph, and a graph
is itself a tool.

**The documentation follows the same template for every tool:**
- a one-sentence Summary, an illustration, and Usage notes (what to know before running);
- the Parameters as a table: name, explanation, data type;
- a Python example, Environments, and Licensing.

The consistency is the point: once you have read one tool's page, you know how to read all of them.
Concept pages ("How Weighted Overlay works", "Understanding distance analysis") sit beside the
reference pages.

**Suitability analysis.** The classic workflow is "where should the town go?":
1. Buffer the rivers and the roads.
2. Exclude the protected areas and the floodplain.
3. Reclassify slope from the DEM.
4. Overlay, weighted or Boolean.
5. Keep the cells or polygons that pass.

The result is one more layer: the suitability area. ArcGIS Pro has a Suitability Modeler that walks
through these steps with a live preview.

**Layouts.** A layout is a page holding:
- **map frames**: live views of maps, at a scale;
- **dynamic elements** tied to a map frame: legend, north arrow, scale bar, grid, and text that
  reads the map's properties;
- **charts and tables.**

New Layout offers a gallery of page sizes, grouped by family: ANSI (Letter to E), Architectural
(A 9x12 to E 36x48), ISO (A5 to A0), in portrait and landscape. Layout templates (.pagx) carry a
whole page design.

**Charts belong to layers.** A bar, line, histogram, scatter or box chart is made from a layer's
fields, saved with that layer, and linked both ways: selecting bars selects the features. A chart
can be put on a layout.

## 2. UrbanEyes: site analysis at a glance

The owner's last two pictures show a site page for Philadelphia: a 3D city on satellite imagery with
lens tabs, then a dashboard.
- **3D lens tabs:** Base, Type, Height, Floors, Area, Age, Population, Street use, Figure ground.
  Street use colours the network as pedestrian zone, footway, cycleway, mixed path and car road.
- **Climate chart:** monthly mean temperature as a line, the daily range as a band, and rainfall as
  bars, with the Köppen zone in words: "Dsa, hot-summer continental, dry summer. 993 mm rain a
  year".
- **Wind rose:** 16 directions. Petal length is the share of days and shade is the strength.
  Caption: "Mostly from the WNW, 17 km/h daily peak".
- **Sun path:** the sun's track on 21 June, the equinox and 21 December on a polar plot, with the
  day lengths.
- **Cards:**
  - climate zone;
  - heating and cooling degree days (base 18 °C);
  - solar energy per year (kWh/m²);
  - terrain relief and steepest grade;
  - air quality (PM2.5 against the WHO guideline);
  - seismic history (M4.5+ within 100 km);
  - built context (buildings and ground coverage within 700 m);
  - mean building height.

Every card is a number, one line saying what it means, and a coloured dot where it calls for
attention. The data credit is at the foot.

## 3. Free sources for the same (no keys, CORS-open, credited)

| Card or chart | Source | Notes |
|---|---|---|
| Monthly temperature and rainfall, Köppen zone, degree days | Open-Meteo historical weather (ERA5) | A year of daily values; Köppen computed in the app from monthly means and totals |
| Wind rose | Open-Meteo hourly wind speed and direction | 16 sectors; share of hours, mean speed per sector |
| Solar energy per year | NASA POWER (already planned for V143) or Open-Meteo shortwave radiation | kWh/m²/year on the horizontal |
| Sun path | The app's own V107 sun position | No network |
| Terrain relief and grade | V108/V137 terrain, or AWS Terrarium (V133) | No new source |
| Air quality | Open-Meteo air quality (CAMS) | PM2.5, last 92 days; against the WHO 15 µg/m³ 24-hour guideline |
| Seismic history | USGS FDSN event service | M4.5+ within 100 km since 1976 |
| Built context, mean height | V133 OSM context (Overpass) | Counts and coverage within a radius |

All of these are fetched only when asked, cached with the project, and credited on the dashboard
and on any sheet it is placed on (the V132 ground rules).

## 4. What it means for this app (the plan, V157 to V163)

- **V157 Site analysis A1, the dashboard:** the cards and three charts above for the project's site,
  from the free sources, saved with the project, light and dark, phone to desktop. Every value says
  what it is and where it came from.
- **V158 Analysis A2, the tool pane:** one pane for every analysis tool, ArcGIS's shape:
  - typed parameters checked as you fill them, a Run button, and messages;
  - a History you can rerun from, with results as layers (V148's Analysis section).
  - The first tools are buffer, distance, slope class, a flood or protected exclusion, and a
    weighted suitability overlay (the town-location workflow).
  - Sun hours runs on the GPU when there is one.
  - Each tool gets a guide page in one template: summary, usage, parameters, how it works.
- **V159 Analysis A3, the Contents pane:**
  - the layer stack shown by drawing order, by source and by selection, each layer with its legend
    patch;
  - layer properties for symbology (by category, graduated, stretch), labels and a filter (the
    definition query);
  - the stack drawn as the owner's diagram in an exploded 3D view.
- **Presentation P1 to P3 (V160 to V162):**
  - New Layout's page gallery (ANSI, Architectural, ISO, both orientations);
  - map frames with a live legend, north arrow and scale bar;
  - the V157 cards and charts, and any result layer's chart, as live board elements;
  - a "Site analysis" template that lays out the whole dashboard on a sheet in one click.
