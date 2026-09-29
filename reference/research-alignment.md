# Research: alignments, profiles and stations (V127)

PIPELINE, Track B item 3: "Alignment / profile objects -- horizontal alignment, vertical profile,
station-offset." Vendor documentation (Autodesk, Bentley) came through search summaries; the
sources are listed below. The owner's V125 rule, after Rhino, sets how the feature fits in:
- its settings are pages of Properties that follow the selection;
- its commands act on the selection;
- it adds no window, rail tab or discipline, and at most one toolbar button.

## What the civil programs do

1. **An alignment is made from a polyline.** Civil 3D's "Create Alignment from Objects" takes a
   polyline, and its vertices become the PIs. The "Add curves between tangents" option puts a free
   circular curve of a set radius at each PI, and the curve stays tangent to both legs when either
   leg moves. (Civil 3D Help: Alignment Design Strategies; tutorials on alignment from objects.)
2. **Stations are labelled with major and minor ticks.** Civil 3D's label sets ("Major Minor and
   Geometry Points") tick every minor station, label every major one, and label the geometry
   points: the beginning and end, and every PC and PT. (NRCS North Dakota Civil 3D styles, 500
   Alignments.)
3. **A profile view is drawn in model space.** It is a grid of station against elevation, with a
   vertical exaggeration. The existing ground is sampled from a surface along the alignment, and
   the design profile is drawn over it. (Civil 3D Help: profile view vertical exaggeration; NRCS
   600 Profiles.)
4. **A vertical curve is a symmetric parabola** (AASHTO, and every US DOT design manual):
   - y = y_PVC + g1 x + (g2 - g1) x^2 / 2L, with the PVI at L/2.
   - A = g2 - g1, in percent: negative is a crest, positive a sag.
   - The high or low point is at x = -g1 L / A (in consistent units).
   - K = L / |A|. (WYDOT Road Design Manual 3-03; Civil 3D Help: About Vertical Curve Design.)

## What V127 takes from it

- **The alignment.** ALIGNMENT turns the selected open polyline into an alignment, in its place,
  following (1). Each interior PI gets a circular curve, of the largest radius up to 100 m that
  the legs leave room for. Curves that would overlap are refused, never trimmed.
- **Stations and labels.** Minor ticks fall every 20 m and labelled major ticks every 100 m, and
  the beginning, end, PCs and PTs are marked with their stations, following (2). Stations are
  written k+mmm.mm, because the project's units are metric.
- **The profile view.** It is drawn in model space where PROFILEVIEW is clicked, at 10x vertical
  exaggeration by default, following (3). The ground is sampled from the first V108 surface under
  the route.
- **The profile.** It is AASHTO's parabola, following (4). Each vertical curve shows its A, K and
  high or low point.
- **Where it is set.** The Alignment and Profile pages in Properties, with STATION as a command
  that reports station and offset. The one button is Alignment, in the existing Site panel.

## Not taken, yet

- Spirals (clothoids), superelevation, corridors and cross-sections.
- PI grips.
- US-customary 100-ft stations: the project has no feet unit.
- The profile view in DXF and SVG export.

## Sources

- [Autodesk Civil 3D Help: Alignment Design Strategies](https://help.autodesk.com/view/CIV3D/2025/ENU/?guid=GUID-63ED9FBE-85E2-44F3-97CD-CBEA4D0E390E)
- [Autodesk Civil 3D Help: About Vertical Curve Design](https://help.autodesk.com/view/CIV3D/2025/ENU/?guid=GUID-FFE978DE-6282-4D40-8C16-7A1D6288D7A1)
- [NRCS North Dakota, Civil 3D styles: Alignment lines](https://www.nrcs.usda.gov/sites/default/files/2023-03/500_Alignments.pdf)
- [NRCS North Dakota, Civil 3D styles: Profile lines](https://www.nrcs.usda.gov/sites/default/files/2023-03/600_Profiles.pdf)
- [Infratech Civil: Civil 3D alignment from objects](https://www.infratechcivil.com/pages/civil-3d-alignment-from-objects)
- [Autodesk: vertical exaggeration of a profile view](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-modify-the-Vertical-exaggeration-and-scale-of-profile-view-in-Civil-3D.html)
- [WYDOT Road Design Manual 3-03, Vertical Alignment](https://www.dot.state.wy.us/files/live/sites/wydot/files/shared/Project%20Development/Road%20Design%20Manual_1/3-03_2019_MAY.pdf)
- [MATHalino: Parabolic curve](https://mathalino.com/reviewer/surveying-and-transportation-engineering/parabolic-curve)
