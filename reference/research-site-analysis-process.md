# Research: how professionals do site analysis, and one standard process for the app

The owner (V156): "do some research on how professionals do site analysis. i want to standardize the
whole process. looks like it is more advance than what we currently have now."

## 1. What the profession does

The sources agree on the shape. They differ mainly in which lens comes first.

- **Three parts: documentation, analysis, inferences.** Gather everything about the site, study
  it, then draw design conclusions. Architectural guides call the first part the desktop study:
  maps, previous studies, property records, the planning authority's rules. A site visit follows,
  then surveys where the desktop leaves doubt (slope, setbacks, lot dimensions, soils).
  ([archisoup](https://www.archisoup.com/architecture-site-analysis-introduction),
  [ProjectManager](https://www.projectmanager.com/blog/site-analysis-in-architecture),
  [Mastt](https://www.mastt.com/guide/site-analysis))
- **RIBA Plan of Work, Stage 1 (Preparation and Briefing):**
  - site appraisals, and site information collated from surveys of many kinds: topographical,
    ground investigation, ecology, trees, heritage, flood risk;
  - an initial visit with photographs, notes and sketches;
  - a check of the site's history for contamination and geology;
  - feasibility studies.
  - The stage ends with an approved brief, and site information sufficient to begin concept
    design. ([RIBA Plan of Work 2020 overview](https://www.riba.org/media/syneeeto/2020ribaplanofworkoverviewpdf.pdf),
    [RIBA Stage 1 checklist](https://www.riba.org/media/w3epmqnb/1-preparation-and-brief-checklist-pdf.pdf))
- **Kevin Lynch, Site Planning:**
  - Natural factors: geology and landform, soils, drainage, topography and slope, erosion,
    surface and ground water, vegetation, wildlife, and climate (sun, wind, humidity).
  - Cultural factors: existing land use, ownership and regulation, socio-economic conditions,
    utilities, circulation and history.
  - Each is read for its constraints, opportunities and potential.
  ([summary](https://urbandesignlab.in/book-review-site-planning-kevin-lynch/))
- **Edward T. White, Site Analysis: Diagramming Information for Architectural Design.** He calls
  it contextual analysis: an inventory of every pressure, force and situation on and around the
  site, existing, imminent and potential. Each is turned from words and numbers into a diagram,
  in a consistent graphic vocabulary.
  ([book](https://www.goodreads.com/book/show/6851887-site-analysis))
- **Ian McHarg, Design with Nature: the layer cake.**
  - The landscape is read through fixed lenses, always in the same order: climate, geology,
    hydrology, soils, vegetation, wildlife, then land use.
  - Each lens is a map.
  - Overlaid, the maps show where each use is suitable.
  - This is where GIS overlay began.
  ([CSISS Classics](https://escholarship.org/content/qt5x78n2gn/qt5x78n2gn.pdf),
  [Design Workshop](https://www.designworkshop.com/docs/news/blending-project-goals-performance.pdf))
- **Esri's suitability workflow**, the modern McHarg, in four steps:
  1. determine and prepare the criteria;
  2. transform each to a common suitability scale (unique categories, ranges of classes, or
     continuous functions);
  3. weight them and add them up;
  4. locate the areas that meet the total area, the number of regions, their sizes and the
     distances between them.
  ([ArcGIS Pro](https://pro.arcgis.com/en/pro-app/latest/help/analysis/spatial-analyst/suitability-modeler/the-general-suitability-modeling-workflow.htm),
  [Weighted Overlay](https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/how-weighted-overlay-works.htm))
- **Due diligence, the developer's and the lender's side (US):**
  - an ALTA/NSPS land title survey (boundaries, improvements, utilities, recorded and observed
    easements, zoning and setbacks, adjoining parcels);
  - a Phase I environmental site assessment (historic uses, recognised environmental conditions);
  - a zoning analysis: permitted uses, FAR, height and setbacks, lot coverage, parking.
  - The feasibility study turns these into a buildable envelope and a yield, and checks the yield
    against what the market will carry.
  ([ALTA guide](https://www.partneresi.com/resources/references/other-tools/2026-guide-to-alta-nsps-land-title-surveys/),
  [Phase I ESA](https://en.wikipedia.org/wiki/Phase_I_environmental_site_assessment),
  [zoning analysis](https://3dcityplanner.com/en/articles/data-driven-urban-planning/what-is-zoning-analysis-a-guide-for-developers/),
  [feasibility](https://www.accessengineeringlibrary.com/content/book/9780071494373/back-matter/appendix2))

What separates professional work from a pile of maps:
- **every finding names its source, its date and how sure it is** (desktop, seen on site, surveyed);
- **every finding is classed** as a constraint, an opportunity, or neither, and red flags come
  first;
- **the categories are fixed**, so nothing is forgotten and two sites can be compared;
- **the analysis ends in a synthesis:** a buildable area, an envelope and a yield, not just
  diagrams.

## 2. The standard: Site Analysis in six stages and ten categories

**Stages** (RIBA Stage 1 and the due-diligence order, in the app's words):
0. **Define:** the site boundary (from a parcel, V134, or drawn), the project type, and the
   questions the analysis must answer.
1. **Desktop study:** each category filled from open data, automatically where it can be, every
   value with its source and date.
2. **Site visit:** a checklist per category of what to verify on site, with photographs and notes
   placed on the plan; a finding's confidence rises from "desktop" to "seen on site".
3. **Surveys:** where the visit leaves doubt, a survey is requested (topographic, ALTA, ground,
   trees, Phase I). When it comes in (V108, V138), it raises the confidence to "surveyed".
4. **Analysis:** each category drawn as a diagram in one graphic vocabulary (White's), and each
   finding classed as a constraint or an opportunity, with a severity.
5. **Synthesis:** constraints and opportunities overlaid (McHarg's cake, Esri's four steps). From
   that, the buildable area, the zoning envelope and the yield (GFA by FAR, units, parking).
6. **Report:** a standard set of boards, below, every number credited.

**Categories** (Lynch's natural and cultural factors, McHarg's order, the due-diligence items):

| # | Category | What it answers | Open data, free | In the app now |
|---|---|---|---|---|
| 1 | Location and context | Where, what surrounds it, figure-ground, land use | OSM (V133), basemaps (V132) | Mostly: context massing, map |
| 2 | Legal and regulatory | Zoning, permitted uses, FAR, height, setbacks, coverage, parking, easements, ownership, heritage | Council GIS (V134 presets), entered by hand where none | Parcels as layers; **no zoning summary, no FAR/envelope/yield** |
| 3 | Landform | Topography, slope, aspect, relief, geology, soils | Terrain tiles (V133), USGS 3DEP, SSURGO soils (US) | Terrain, slope, aspect, cut and fill (V144, V145); **no soils** |
| 4 | Water | Drainage, flood zones, water bodies, runoff | FEMA NFHL (V134), OSM water, the V143 rain flow | Flood layer, rain flow; **no flood summary** |
| 5 | Climate | Temperature, rain, Köppen zone, sun path, shadows, wind, solar, degree days | Open-Meteo (ERA5), NASA POWER, the V107 sun | Sun, shadows, sun hours, solar (V143); **no climate chart, wind rose, degree days** |
| 6 | Ecology | Vegetation, trees, habitat, protected areas | OSM trees and landuse, protected areas (WDPA) | Trees in context; **no protected areas** |
| 7 | Environmental risk | Seismic, contamination, air quality, noise, wildfire | USGS quakes, EPA Envirofacts (US), Open-Meteo air quality | **None** |
| 8 | Access and circulation | Street hierarchy, street use, transit, walking and cycling, parking, entries | OSM highways, transit stops (GTFS, OSM) | Roads in context; **no hierarchy, no walk times** |
| 9 | Utilities | Water, sewer, power, stormwater | Rarely open; OSM where mapped; else "survey needed" | **None** |
| 10 | People and place | Demographics, amenities within a walk, history, views, landmarks, noise sources (Lynch's paths, edges, districts, nodes, landmarks) | US Census ACS, OSM amenities | **None** |

**The report**, eight boards in a fixed order:
1. location and context;
2. zoning summary (a table);
3. landform and water;
4. climate (the climate chart, wind rose and sun path);
5. access and circulation;
6. risks;
7. constraints and opportunities (one map);
8. buildable area, envelope and yield, with the summary cards and the sources and dates.

## 3. What it means for the plan

Site analysis becomes a workspace with this structure. Finding-level records carry the source, the
date, the confidence and a constraint or opportunity class. The categories' data, diagrams,
synthesis and report fill it in phase by phase. The tool pane, the Contents pane and the
presentation work from the ArcGIS note (`research-arcgis-site-analysis.md`) serve it. See
`PIPELINE.md`, V157 to V164.
