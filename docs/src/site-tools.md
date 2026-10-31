---
title: Site analysis tools
order: 7
---
# Site analysis tools

Eight tools for working the site analysis out on a grid. They follow ArcGIS's way of building
analysis tools: every tool opens in the same shape, checks its parameters as you fill them in,
runs, says how it went, and keeps its output as a layer and its run in History.

They are in **Analyze**, in the **Tools** group under the ten categories:
- Buffer
- Distance
- Slope classes
- Exclusions
- Suitability
- Locate
- Constraints and opportunities
- Buildable area
- History

`SITETOOLS` opens History. Each tool also has its own command, given in its section below.

## How a tool works

- **Open it.** Click its row. It opens on the right, where an analysis opens.
- **Its parameters.** Each has a type: a layer, a number with its unit, a choice, a tick, or a
  run from History. A red asterisk marks a required one.
- **Checked as you go.** A value is checked as soon as you leave its field. A wrong one has its
  message beside it, in red, and **Run** waits until it is right; hold the pointer on Run to read
  why. A warning (orange) does not stop the tool. For example, a layer you have not fetched yet
  is a warning in Exclusions, and that reason is left out.
- **Run.** The status comes first: Succeeded, Succeeded with warnings, or Failed. With it come
  the time it took, the messages and the results. The output is added as a layer, shown on the
  plan, with **Hide** and **Show**, and its key.
- **Reset parameters** puts a tool's defaults back.
- **Its runs.** Under each tool are its last runs, each with **Open** and **Run again**.

**The grid.** Every tool works on one grid over the lot: cells of 1 m over the lot and 100 m
around it. With no property line, it covers 100 m around the site's centre. A larger lot gets
cells of 2 m, 4 m and so on, so there are never more than 250,000 cells.
- This is the tools' **processing extent**, as in ArcGIS: anything beyond it is not counted, and
  the messages say so.
- An area counts the cells whose centres are inside it. A line or a point counts the cells within
  half a cell of it.
- Areas are therefore good to about a cell's width along their edges.

**Outputs are layers.** Every run's output is a layer in **Layers**, under Analysis, with its
key.
- A run with the same parameters as an earlier one replaces that layer, as ArcGIS overwrites a
  tool's output.
- When the property line changes, the layer is marked **Out of date**. **Update** runs it again on
  the lot as it is now, with the same parameters.
- A run is one step of **Undo**: undo takes back both the run and its layer.

**History** lists every run, newest first. Each run keeps:
- its parameters;
- when it ran and how long it took;
- its status, messages and results;
- its layer.

Each run has three buttons:
- **Open** shows the tool with that run's parameters;
- **Run again** runs it again with them;
- **Remove** takes it off the list and leaves its layer.

History is kept with the project, up to the last 40 runs.

## Buffer

`BUFFER`

**Summary.** The area within a distance of a layer's features: around the streets, the lot line,
the trees or the flood zones.

**Usage.**
- Planar distance, in metres, from cell centre to cell centre.
- Overlapping buffers are one area.
- For an area layer (the lot, the flood zones, the buildings), **Outside** keeps only the ring
  around the area, and **Inside** only the band within its edge.

**Parameters.**

| Parameter | Explanation | Type |
|---|---|---|
| Input layer (required) | The features to buffer: the lot, the lot line, streets and paths, arterial roads, buildings around, trees, woods and tree crowns, ponds and water, flood zones (1% annual chance), wetlands | Layer |
| Distance (required) | More than 0 m, at most 100 m (the extent's margin) | Number, m |
| Side | The features and around them; outside an area only; inside an area only | Choice |

**How it works.** Every cell within the distance of a feature's cell, by the exact distance
transform below.

## Distance

`DISTANCEFROM`

**Summary.** The straight-line distance from every cell to the nearest of a layer's features,
as ArcGIS's Euclidean Distance gives it.

**Usage.**
- Cells beyond the maximum distance, if you give one, have no value.
- The results give the lot's nearest, mean and farthest distance.

**Parameters.**

| Parameter | Explanation | Type |
|---|---|---|
| Input layer (required) | The features to measure from | Layer |
| Maximum distance | Optional; more than 0 m | Number, m |

**How it works.** Felzenszwalb and Huttenlocher's exact distance transform ("Distance Transforms
of Sampled Functions", 2012): the lower envelope of parabolas along each row, then each column.
It is exact, not an approximation. The layer keeps each value to one of 91 levels between 0 and
the greatest.

## Slope classes

`SLOPECLASSES`

**Summary.** The ground's slope in the classes the standards registry gives for development (0 to
5, 5 to 10, 10 to 15, 15 to 25 and over 25%), with the lot's area in each.

**Usage.** It needs the ground from Analyze site. It has no parameters: the classes are the
registry's (Properties > Site > Standards, Slope classes for development), and an override there
changes them.

**How it works.** The slope of the 5 m ground grid (Horn's method), between its four nearest
points. A slope exactly at a bound is in the class above it.

## Exclusions

`EXCLUSIONS`

**Summary.** Where building is restricted by what is known to be there:
- outside the lot;
- inside the zoning setbacks;
- the flood zones (1% annual chance);
- wetlands;
- steep slopes;
- buildings standing now;
- a buffer from History.

**Usage.**
- Each cell takes the first reason, in that order, that applies to it.
- Restricted is a decision about what is there. A cell where nothing is known has no value
  instead: ArcGIS keeps the two apart, and so do these tools.
- A reason whose layer the project does not have yet is a warning, and is left out.
- Tick at least one reason, or pick a buffer.

**Parameters.**

| Parameter | Explanation | Type |
|---|---|---|
| Outside the lot | Needs a property line | Tick |
| Inside the zoning setbacks | From the zoning record (Legal): its front, side and rear setbacks at the ground | Tick |
| Flood zones (1% annual chance) | FEMA's floodway, A, AE, AH, AO and V zones | Tick |
| Wetlands | The National Wetlands Inventory, after **Get wetlands** in Buildable area | Tick |
| Steep slopes | With **Steep from**: by default the registry's upper slope bound (25%) | Tick |
| Steep from | More than 0%, at most 100% | Number, % |
| Buildings standing now | The context's buildings | Tick |
| A buffer from History | A Buffer run, its area restricted | Run |

**How it works.** The reasons are drawn in their own colours. Suitability leaves these cells out
and draws them grey.

## Suitability

`SUITABILITY`

**Summary.** Where on the site is best to build. Each criterion is turned to a common scale, then
they are weighted and added, and the restricted cells are left out. This is ArcGIS's weighted
overlay, as its Suitability Modeler does it.

**Usage.** The criteria are:
- slope;
- distance to the streets;
- distance from arterial roads;
- sun hours, from the last Sun hours run;
- distance to trees;
- slope class.

Tick the ones that matter. A criterion whose layer is missing is off by default.

Each criterion is turned to the scale in one of three ways:
- **Continuous functions** between a lower and an upper threshold, by default the data's least
  and greatest:
  - **Linear**, lower or higher better;
  - **Small**, lower better;
  - **Large**, higher better;
  - **Near a value**, best at its midpoint.
- **Range of classes:** breaks in rising order, and one value more than the breaks. A value at a
  break takes the class above.
- **Unique categories:** for slope class, a value for each class. Leave them blank to spread them
  over the scale, the flattest best.

There are two ways to weight:
- **Multiplier:** each transformed value times its weight, added.
- **Percent:** each added at its share. The shares must add to 100%, and the result is rescaled
  to the scale.

**Parameters.**

| Parameter | Explanation | Type |
|---|---|---|
| Suitability scale | 1 to 10 (the default), 1 to 9, or 1 to 5 | Choice |
| Weight by | Multiplier or Percent | Choice |
| Restricted cells from | An Exclusions run; by default the latest | Run |
| Criteria | For each one ticked: its transform, its weight, and the transform's values | Criteria |

**How it works.**
- The continuous functions are QGIS's fuzzy membership formulas, where f1 is the spread and f2
  the midpoint:
  - Small, 1/(1+(x/f2)^f1);
  - Large, 1/(1+(x/f2)^-f1);
  - Near, 1/(1+f1(x-f2)^2).
- Each is rescaled so that its least and greatest values between the thresholds are the scale's
  ends.
- A criterion that has the same value everywhere adds the scale's middle, with a warning.
- A cell where any criterion has no value has none in the result. Restricted cells are grey.

## Locate

`LOCATE`

**Summary.** The best place of a given area in a suitability map: one connected region with the
highest mean suitability.

**Usage.** Pick a Suitability run and give the area, for example a 600 m² footprint. Within the
lot keeps the region on the lot. An area larger than can be used there is refused, with how much
can be.

**Parameters.**

| Parameter | Explanation | Type |
|---|---|---|
| Suitability from (required) | A Suitability run; by default the latest | Run |
| Area (required) | More than 0 m² | Number, m² |
| Within | The lot, or the whole extent | Choice |

**How it works.** A simplified Locate Regions:
- the 24 best cells, each at least half the region's side from the others, are seeds;
- from each seed, the region grows by its best neighbouring cell (sharing a side) until it has
  the area;
- the region with the highest mean suitability is kept, the earlier seed among equals.

ArcGIS's own algorithm also weighs the region's shape and the spacing between regions. This one
does not.

## Constraints and opportunities

`CONSTRAINTSMAP`

**Summary.** What limits the site and what it offers, on one plan, as councils ask a site
analysis plan to show.

**Usage.**
- The constraints:
  - flood zones;
  - wetlands;
  - steep slopes;
  - buildings standing now;
  - the zoning setbacks;
  - near an arterial road;
  - overshadowed.
- The opportunities:
  - street frontage;
  - sunny;
  - near trees and woods;
  - flat to gentle ground.
- Each cell takes its first constraint, in that order. With none, it takes its first
  opportunity.
- Sunny and overshadowed need a Sun hours run. Without one they are not shown, and the messages
  say so.

**Parameters.**

| Parameter | Explanation | Type |
|---|---|---|
| Where | On the lot (the default), or the whole extent | Choice |

**How it works.** Each item comes from a layer the project has. The distances and hours are the
app's working set in the standards registry (Constraints and opportunities: the distances and
hours), not a standard, and you can override them there:
- near an arterial within 30 m;
- frontage within 10 m of a street;
- sunny from 6 h;
- overshadowed under 2 h;
- near trees within 15 m.

Steep and flat are the registry's slope classes.

## Buildable area

`BUILDABLE`

**Summary.** Pennsylvania's site capacity calculation. The base site area less the resource
protection land gives the net buildable site area. Then it shows where to build: inside the
setbacks and clear of the resources.

**Usage.**
- **Get wetlands** asks the National Wetlands Inventory for the extent. It covers US sites only.
- Give what the property line does not show: rights-of-way and land set aside. From the
  district's regulations you can also give its density and its impervious surface ratio.
- The results follow the ordinance's form:
  1. the total site area;
  2. the base site area;
  3. each resource's land and the land it protects;
  4. the land with resource restrictions;
  5. the resource protection land;
  6. the net buildable site area, in m² and acres;
  7. the dwelling units allowed, not rounded up;
  8. the impervious surface allowed;
  9. what is buildable within the setbacks and clear of every resource.

**Parameters.**

| Parameter | Explanation | Type |
|---|---|---|
| Rights-of-way and land set aside | Future road and utility rights-of-way, land cut off, land reserved as open space; at most the lot | Number, m² |
| Density allowed | Optional; dwelling units an acre | Number, du/acre |
| Impervious surface ratio | Optional; 0 to 100% | Number, % |

**How it works.** Each resource's land on the lot is counted at its open space ratio, from the
standards registry (Site capacity: the open space ratios of resource protection land). The first
edition is Chalfont Borough's (Bucks County, Pennsylvania) Zoning, section 440-17, read in a
secondary copy and said so:

| Resource | Ratio |
|---|---|
| Floodplains | 1.00 |
| Wetlands | 1.00 |
| Ponds, and waters of the Commonwealth | 1.00 |
| Steep slopes, 25% or more | 0.85 |
| Forest with another resource | 0.80 |
| Steep slopes, 15% to 25% | 0.70 |
| Forest with no other resource | 0.50 |

- Where resources overlap, only the highest ratio counts.
- Pond shores and wetland margins are not counted: the ordinance defines their extent elsewhere,
  and that part was not read.
- Each municipality sets its own ratios. Outside Chalfont the tool says it is applied outside its
  place.
- An override in Standards changes the calculation, and the run says it was overridden.
