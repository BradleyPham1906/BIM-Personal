# Research: how professionals present a zoning analysis, the envelope and the yield

For V160 (Site analysis SA3, regulation). The owner wants the site analysis "really really really
professional" (V159). This note records, in our own words, how practice presents the legal side
of a site, and the design it sets.

## 1. The zoning analysis table

Councils ask for it with a permit application, and architects put it on the cover sheet. Its form:
- one row per control: lot area, lot width and depth, floor area ratio (FAR), gross floor area,
  height and storeys, street-wall height, setbacks (front, side, rear), stepbacks, lot coverage,
  parking and loading, and permitted uses;
- what is **permitted** (or required), what is **proposed**, and whether it **complies**.

([Sechelt zoning analysis table](https://www.sechelt.ca/en/business-and-development/resources/Documents/Zoning-Analysis-Table.pdf),
[3D City Planner: zoning analysis](https://3dcityplanner.com/en/articles/data-driven-urban-planning/what-is-zoning-analysis-a-guide-for-developers/),
[Buildability](https://buildability.us/features/zoning-analysis),
[from parcel to buildable](https://mmcganalytics.com/articles/buildable-area-analysis-parcel/))

## 2. The envelope, drawn

**New York's ZD1 zoning diagram** (Department of Buildings) is the strictest standard we found. It
asks for:
- a site plan with dimensioned building and street-wall heights, setbacks and the sky exposure
  plane;
- an axonometric of the building;
- front, side and rear sections, with the maximum building envelope where it governs.

([ZD1 guide](https://www.nyc.gov/assets/buildings/pdf/zd1_guide.pdf),
[ZD1 sample](https://www.nyc.gov/assets/buildings/pdf/zd1_sample.pdf))

**The sky exposure plane** is a sloping plane. It starts at a set height above the street line and
rises into the lot at a set ratio of vertical to horizontal, and a building may not pierce it. It is
why Manhattan's towers step back. Typical values:
- the setback starts at 60 ft in R6–R7 districts and 85 ft in R8–R10;
- the initial setback is 20 ft on a narrow street and 15 ft on a wide one.

([NYC ZR 23-736](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-736),
[sky exposure planes](https://preliminaryzoninganalysis.com/blog/sky-exposure-planes/),
[Setback (architecture)](https://en.wikipedia.org/wiki/Setback_(architecture)))

**ArcGIS Urban's envelope** is the maximum volume a building may fill, bounded by:
- height limits;
- setbacks, which can differ per edge by orientation and street adjacency, and come in tiers with
  start heights;
- sky planes, given by a start offset and an angle.

FAR and coverage then limit how much of that volume a building can actually use.
([ArcGIS Urban: envelopes](https://doc.arcgis.com/en/urban/latest/help/help-zoning-envelopes.htm),
[zoning regulations](https://doc.arcgis.com/en/urban/help/help-zoning-regulations.htm))

TestFit, Archistar and Giraffe all put the envelope and the yield together, so that a massing
change updates the numbers.
([Hektar: feasibility tools compared](https://www.hektar.ai/post/comparing-early-stage-feasibility-tools-2026-forma-giraffe-finch-testfit-hektar))

## 3. The yield

- **Gross floor area** permitted by FAR = FAR × lot area.
- **What the envelope can hold:** the floor plates that fit under it, storey by storey, with
  coverage limiting each plate.
- **The achievable area** is the lesser of the two. Saying which one governs is what makes a yield
  study useful.
- **Net area** = gross × efficiency. Residential efficiency is typically 75–85%.
- **Units** = net residential area ÷ the average unit size.
- **Parking** = units × the ratio, plus the non-residential area × its rate. Typical ratios are
  1–2 spaces a unit, set by the code.

([FAR vs GFA](https://www.feasibility.pro/far-vs-gfa-vs-bua/),
[FAR / density calculator](https://datadrivenaec.com/tools/far-density-calculator),
[floor area](https://en.wikipedia.org/wiki/Floor_area),
[residential feasibility studies](https://www.ginardstudio.com/journal/feasibility-studies-for-residential-development-why-smart-developers-and-investors-start-with-architecture-led-analysis))

## 4. Against Giraffe

The owner asked, partway through V160, whether we do what Giraffe does for zoning. Giraffe's site and
its Notion help pages could not be opened from the build environment (the names do not resolve), so
this comes from search summaries of those pages. It is Giraffe's own account of its product, not a
test of it.

**Giraffe's Envelope transform** works from a selected polygon:
- it takes a maximum height;
- each side of the site gets its own setbacks and heights, with as many sides as needed;
- a **setback and levels editor** plots height (up) against inset from the polygon edge (across);
  you drag or type the points, so any combination of steps and slopes can be drawn;
- a toggle outputs only the ground-floor setback polygon.

([Envelope](https://giraffetechnology.notion.site/Envelope-df9601a267e145ed8d9a25c22f3aceef),
[Solving for envelope and setback requirements](https://giraffetechnology.notion.site/Solving-for-Envelope-and-Set-Back-Requirements-10a689ac43744c1cac4edac0976c375e))

**Around it:**
- a **Zoneomics app** reads a parcel's zoning (US and Canada, a paid data source) and generates the
  envelope, linking to the zoning report;
  ([Zoneomics app](https://giraffetechnology.notion.site/Zoneomics-e1bbf811d51249b2a2ca87300c6194d3))
- automated constraint checks and red flags in site screening;
- generative solvers that fill the envelope with apartment layouts, the levels set by the
  envelope's height;
- a live financial model (cost, revenue, return) linked to the geometry.

([feasibility](https://www.giraffe.build/real-estate-feasibility-software/),
[plugins](https://www.giraffe.build/plugins/),
[generative design](https://www.giraffe.build/generative-design/),
[site analysis](https://www.giraffe.build/site-analysis/))

**What V160 takes from this:**
- **A rule for each kind of side, as Giraffe's profile is.** Each rule is a setback at the ground,
  steps ("above 15 m, set back 6 m") and an angular plane from the lot line. That form covers:
  - the street wall and stepback, and New York's sky exposure plane;
  - side setbacks that grow with height, as in setbacks by storey;
  - rear angular and daylight planes, such as a 45° plane from the rear lot line.
- Any side can be set as front, side or rear by hand, so a corner lot has two fronts.
- **The controls from free council layers.** We do not use the paid Zoneomics data. We read the
  district, and the FAR and height where the layer has them: MapPLUTO's ResidFAR, CommFAR and
  ZoneDist1, an FSR, and a building height, with feet turned into metres.

**What it leaves for later phases:** massing generated inside the envelope, and the financial model.

**Where V160 goes further than Giraffe's pages say they do:**
- the permit-style zoning analysis table (permitted, proposed, complies);
- sections at true scale, dimensioned after ZD1;
- the plates by storey and which limit governs;
- volumes and plates worked out exactly, not sampled.

## 5. The design this sets for V160

**A zoning record for the site**, entered by hand or read from council layers (V134) at the lot. It
holds:
- the district, the permitted uses and the source;
- FAR, maximum height and storeys, and maximum coverage;
- a rule for each kind of side (front, side, rear): a setback at the ground, steps, and an angular
  plane (for the front, the sky exposure plane), with the street wall and stepback as the front's
  first step;
- which side is the front, and any side's role set by hand;
- the yield assumptions: floor-to-floor height, efficiency, average unit size, residential share,
  and parking rates.

**The envelope in 3D:** at every height, the lot with each side moved in by its rule's setback there,
up to the height limit. Between the heights where a rule changes, every corner moves in a straight
line. So:
- the plate's area is a quadratic in the height, and Simpson's rule gives the volume exactly;
- the solid is built from whole flat faces: one per side per piece, terraces where the plate steps
  in, and convex roofs.

A lot that is not convex is moved in side by side, joined where the sides meet, as the setback line
is. Where the setbacks would split a lot in two, the envelope stops just short and says so. The
envelope is a translucent solid on a Zoning envelope layer, and massing that leaves it is flagged.

**The yield:** GFA by FAR, the envelope's capacity storey by storey, which of the two governs, the
net area, the units and the parking.

**The Zoning and yield board**, in the Climate and risk board's form:
- indicators;
- the zoning analysis table (permitted, proposed, complies, with an icon and a word);
- two dimensioned envelope sections at true scale, after ZD1: front to rear, and side to side;
- the rules by side, as setback against height, after Giraffe's profile editor;
- the lot plan with its sides, setbacks, street, and the plate above each step;
- the floor plates by storey;
- the yield compared (by FAR, the envelope's capacity, the proposed);
- notes on every assumption and the source of every value.

Each result is a finding in Legal and regulatory.
