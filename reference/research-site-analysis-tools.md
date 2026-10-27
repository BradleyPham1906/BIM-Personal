# V172: site analysis tools and synthesis, ArcGIS's way

The phase PIPELINE names: one pane for every analysis tool (typed parameters checked as filled, Run, messages,
History to rerun from, results as layers); buffer, distance, slope classes, exclusions, weighted suitability in
Esri's four steps (criteria, transform, weight, locate); the constraints and opportunities map; the buildable
area; sun hours on the GPU; each tool a guide page in one template. The owner's brief from V156 is in
`reference/research-arcgis-site-analysis.md` (1). This note is the research before building, under
`reference/research-protocol.md`, read on 2026-10-27.

## 1. Sources

| Source | What was read | Level |
|---|---|---|
| Esri, "How Weighted Overlay works" (doc.esri.com, ArcGIS Pro latest) | the whole page | P |
| Esri, "Weighted Overlay" tool reference | the whole page | P |
| Esri, "Suitability modeling framework"; "Implement the suitability modeling workflow"; "Suitability tab"; "Locate tab"; "Exclude restricted locations" | the whole pages | P |
| Esri, "How Rescale by Function works"; "The transformation functions available for Rescale by Function" | the whole pages; their formulas are images, so the formulas come from QGIS (next row) | P for the behaviour; formulas S |
| QGIS 3.40, `src/analysis/processing/qgsalgorithmfuzzifyraster.cpp` (GPL-2.0+, read as text, the method only) | the linear, power, large, small, gaussian and near functions | P |
| Esri, "Use a geoprocessing tool"; "Geoprocessing history"; "Understanding validation in script tools" | the whole pages | P |
| Esri, "Buffer" tool reference; "Euclidean Distance" tool reference; "How Slope works"; "Reclassify"; "How Locate Regions works" | usage and parameters | P |
| Penrith Development Control Plan 2014, C1 Site Planning and Design Principles, 1.1.1 Site Analysis | the section | P (practice) |
| North Sydney Development Control Plan 2013, Part A Section 5 Site Analysis | 5.1 to 5.4.1 | P (practice) |
| Chalfont Borough (Bucks County, PA) Zoning, § 440-17 Site capacity calculations, as published by Zoneomics | the section, its table | S (a reproduction of the code, not the borough's own copy); the same method found in Limerick Township's code by search, not read |
| USFWS National Wetlands Inventory map service (`fwspublicservices.wim.usgs.gov/.../Wetlands/MapServer/0`) | a query near Philadelphia International Airport: 91 features, five types; CORS answered for the Pages origin, preflight allowed | P (tested). Licence: a US federal work (S); its disclaimer pages not read (U, said on any use) |
| The app's own code | `analysis/simulation.js` (sun hours, solar, rain), `analysis/results-layers.js`, `site-analysis/land-water.js` (the 5 m ground, Horn's slope, the registry's slope classes, FEMA's zones), `site-analysis/zoning-envelope.js` (the lot, its setbacks, the plate), `site-analysis/land-use.js`, `site/property.js`, the analysis workspace | P |

Refused or not reached: the Auckland Design Manual's "Opportunities and constraints" page (HTTP 406 to a script
and to the fetch tool); Lake Macquarie's site analysis guideline (403). Esri's "geoprocessing pane" and
"parameter validation" pages have moved and answered 404; the "Use a geoprocessing tool" page covers the same.

## 2. What ArcGIS does, read at the source

**The geoprocessing pane.** A tool's parameters are required (a red asterisk) or optional with a default;
inputs are layers, numbers, choices; Run at the bottom; a status banner with progress, then succeeded,
succeeded with warnings, or failed, its messages behind it; outputs added to the map as layers. Every run is a
history entry kept with the project: its parameters, when it ran and for how long, whether it succeeded, its
messages; an entry reopens the tool with the same settings, or is removed. Validation is internal (types,
required values) and the tool's own (custom warnings and errors, parameters enabled or disabled by others).

**Suitability, the four steps** ("Implement the suitability modeling workflow"):
1. Determine and prepare the criteria (slope from elevation by the Slope tool, distance by Euclidean Distance).
2. Transform each criterion to a common suitability scale (1 to 10 by default): **Unique Categories** (one
   value to one suitability, for land use), **Range of Classes** (ranges to values), **Continuous Functions**
   (linear and nonlinear functions). Defaults: fewer than 27 integer values, categories; 27 or more, classes;
   floating point, functions.
3. Weight and combine: by **multiplier** (transformed values times the weight, added; "common weights are
   between 1 and 2"), or by **percent** (must sum to 100; the added result is linearly rescaled to the scale).
4. Locate: from the suitability map, the regions that meet the spatial requirements (total area, number of
   regions, minimum and maximum size, distances between them).

**Restricted and NoData** (Weighted Overlay; "Exclude restricted locations"). Restricted is a decision: a cell
excluded because of what is known to be there (a stream buffer, a building, a park, a zone where the use is not
permitted). NoData is ignorance: nothing is known there. They are kept apart and drawn apart: restricted grey,
NoData transparent. Weighted Overlay gives Restricted the scale's minimum minus 1; the Suitability Modeler
gives it NoData on the outputs with the Restricted map drawn under them. The app takes the second: restricted
cells are not scored, and are drawn as their own layer.

**The transformation functions** (Esri's behaviour; QGIS's formulas, where f1 is the spread and f2 the
midpoint): linear `(x - a)/(b - a)` clamped, decreasing when the scale is reversed; large
`1/(1 + (x/f2)^-f1)`; small `1/(1 + (x/f2)^f1)`; near `1/(1 + f1 (x - f2)^2)`; gaussian
`exp(-f1 (x - f2)^2)`. Each function's values between the lower and upper thresholds are rescaled to the
scale's minimum and maximum; values outside take a set value or Restricted.

**Buffer.** Planar (Euclidean) in a projected system, which the app's model metres are; dissolve none, all, or
by field. **Euclidean Distance**: each cell's straight-line distance from its centre to the nearest source,
with an optional maximum. **Slope**: the app already has Horn's method on the 5 m ground (V165) with the
registry's classes (V167).

## 3. What practitioners draw (two councils' requirements, read)

A site analysis plan shows, at the scale of the site plan: the site's dimensions and area, north and
orientation, topography (contours), access points, services and easements, rights of way, views to and from,
overland flow and drainage, existing buildings, significant vegetation, noise sources, the neighbours' form and
open spaces, heritage (Penrith C1 1.1.1; North Sydney 5.4.1). Its purpose: "identify the opportunities and
constraints of a development site" and use them to inform the design (North Sydney 5.2), within 50 to 100 m of
the site (Penrith).

The app has most of these as layers already (V164 to V171). The constraints and opportunities map is their
summary on one plan, not new data: constraints (flood, steep slope, setbacks, noise, overshadowing, easements)
and opportunities (the sunny side, views, frontage and access, quiet edges, green), each drawn from the layer
it came from and named.

## 4. The buildable area: a site capacity calculation (S, Chalfont § 440-17)

Pennsylvania municipalities ask for a site capacity calculation with a subdivision or land development:
- **Base site area:** the total site area less future road and existing utility rights-of-way, land not
  contiguous or cut off by a road, railroad or major stream, and land already reserved as open space.
- **Resource protection land:** each resource's area times its open space ratio. Where resources overlap, only
  the highest ratio counts. Chalfont's ratios: floodplains 1.00; steep slopes 15% to 25% 0.70, 25% or more
  0.85; forest 0.50 alone, 0.80 with another resource; ponds 1.00; pond shores 0.80; waters of the
  Commonwealth 1.00; wetlands 1.00; wetland margins 0.80.
- **Net buildable site area** = base site area less resource protection land; then dwelling units = net area
  times the district's density (not rounded up), impervious cover = net area times its ratio.

Each municipality sets its own ratios; they belong in the standards registry (V167) as a record with its place,
"applied outside its place" said elsewhere, overridable with a reason. The app has floodplains (FEMA, V165),
slopes (V165), trees and woods (V157, V168), ponds (V165); wetlands would come from the NWI service (section 1).
The zoning envelope's setbacks (V160) give the buildable plate inside the lot; the two together answer "where,
and how much".

## 5. The proposed design (to confirm with the owner)

- **Tools in the analysis workspace.** A Tools group on its left (V171c's one list), each tool opening on the
  right where an analysis opens: its parameters typed and checked as they are filled (a required one marked, a
  wrong one said beside it), Run, the status and messages, its output added as a result layer (V148), its run in
  History (reopen with the same settings, rerun, remove), kept with the project. Each tool also a command.
- **The tools:** Buffer (any layer's features, by a distance, dissolved or not; exact polygons); Distance (a
  grid of straight-line distance from a layer's features, on the site's grid); Slope classes (the V165 ground
  reclassed by the registry's classes); Exclusions (restricted areas from chosen layers and buffers, drawn
  grey); Suitability (criteria, transform by categories, classes or a function, weights by multiplier or
  percent, a 1 to 10 scale, restricted cells left out); Locate (the best connected region of a given area within
  the suitability, simplified from Locate Regions); the Constraints and opportunities map; the Buildable area
  (the site capacity calculation, with the plate inside the setbacks).
- **The grid:** the site's 5 m ground (V165) for the context; a finer grid (1 m) inside the lot for the
  buildable area and Locate, so a small lot is not three cells.
- **Guide pages:** one template for every tool -- summary, usage, parameters (name, explanation, type), how it
  works -- in `docs/src/`, as Esri's reference pages are.

## 6. Edges for the tests

- Overlapping resources: only the highest ratio counts (a floodplain on a steep slope is 1.00, not 1.70).
- A slope of exactly 15% or 25%: Chalfont's classes are "15% to 25%" and "25% or more"; 25% is the upper class.
- Percent weights that do not sum to 100: refused with a message, as Esri does.
- A criterion with one value everywhere (the function's thresholds equal): no division by zero; the cell takes
  the scale's middle and the message says the criterion does not discriminate.
- Restricted beside NoData: a cell outside the ground grid is NoData, not restricted, and is said so.
- A buffer of 0, a negative buffer (inward, from a polygon), and dissolve with overlapping buffers.

## 7. Questions for the owner (asked together, 2026-10-27)

1. Where the tools live: in the analysis workspace as a Tools group (proposed), or a separate geoprocessing pane.
2. The buildable area: Pennsylvania's site capacity calculation with Chalfont's ratios as the first record
   (proposed), or every constraint removed in full.
3. Sun hours on the GPU: in V172, or left to V172c (Ladybug's sun-hours and radiation) so the app has one sun
   tool.
4. Locate: the simplified best region (proposed), or left out.

## 8. Still open

- The Auckland Design Manual's page (refused) and a third practitioner source on the constraints map.
- Chalfont's code read from the borough's own publisher, to raise section 4 from S to P.
- NWI's disclaimer and use limitations.
