# Research: assets for scale and the simulations (V169)

The owner (V166): "do we have asset designed yet ... trees, building shape, human, bike, car for later
simulations?" The plan (`plan-v167-v170.md`, V169) and the owner's decision of 2026-10-17: made in-house
now, low-detail and adjustable, sized to cited standards; valdrada's credited models (its MIT pedestrians,
its CC BY trees and vehicles) converted later, once glTF can be imported.

Researched 2026-10-19 to `research-protocol.md`. Every source below was read here, as text, from its own
host; the files were kept in the session's scratch folder, never committed (the Green Book and the
National Academies' report are copyrighted; the others are public domain or under the Open Government
Licence, and are cited, not copied).

## 1. People

**Practice.** Entourage in architecture is sized to a population's measured body: stature from a national
health survey, the other dimensions in proportion. Views and sight lines are taken at eye height (the app's
isovists, V164, use 1.6 m). Accessibility codes size the wheelchair's space, not the person in it.

| Fact | Source | Read | Level |
|---|---|---|---|
| Adult stature, 20 and over, 2015-2018: men mean 175.3 cm (5th 162.8, 95th 187.4), women 161.3 cm (149.8, 172.5) | Fryar et al., Anthropometric Reference Data for Children and Adults: United States, 2015-2018, NCHS Vital Health Stat 3(46), January 2021, Tables 9 and 11 (public domain), https://www.cdc.gov/nchs/data/series/sr_03/sr03-046-508.pdf | the tables | P |
| A child of 8: boys mean 132.1 cm | the same, Table 7 | the table | P |
| The body's other dimensions, as linear in stature between the smallest and the largest crew member: stature 148.6 to 194.6 cm, sitting height 77.7 to 101.3, eye height sitting 66.5 to 88.9, bideltoid (shoulder) breadth 37.8 to 56.1 | NASA, Human Integration Design Handbook, NASA/SP-2010-3407/REV1 (2014), Appendix B Tables 1a and 1b; 4.2.2: the data are linear regressions on stature (and mass) from the 1988 ANSUR survey, projected to 2015 | the tables and the method | P (for that population) |
| ANSUR II (2012), the newer survey: its own page says it is not an approximation of the US civilian population; its data files have moved behind an app | https://www.openlab.psu.edu/ansur2/ | the page | P (the caution) |

**The derivation, said in the app.** The top of the head to the eye is sitting height less eye height
sitting (11.2 cm for the smallest, 12.4 cm for the largest), a head dimension, the same standing. Eye height
standing is stature less that distance; shoulder width is the bideltoid breadth; each taken linearly in
stature between NASA's two ends, as NASA's own tables are built. For NHANES's means: a man of 175.3 cm has
his eyes at 163.4 cm and shoulders 48.4 cm across; a woman of 161.3 cm, 149.8 cm and 42.9 cm. A child is
outside the adult data: the same line, extrapolated, and said to be an estimate (S: derived from P, the
population a military one, the gap stated on the model).

**The wheelchair user.**

| Fact | Source | Read | Level |
|---|---|---|---|
| Clear floor space 30 x 48 in (760 x 1220 mm), 305.3; turning space a 60 in (1525 mm) circle, 304.3.1 | U.S. Department of Justice, 2010 ADA Standards for Accessible Design (2010-09-15), https://www.ada.gov/assets/pdfs/2010-design-standards.pdf | 304 and 305 | P |
| Manual chair users: occupied height mean 1249 mm; occupied seat height mean 495 mm (5th-95th 430-566); 95% accommodated (bivariate) by 820 x 1420 mm; eye height, all device users, mean 1152 mm (SD 77); the manual chair row of Table 2 did not come through in the text | Steinfeld, Paquet, D'Souza, Joseph, Maisel, Anthropometry of Wheeled Mobility Project, Final Report for the U.S. Access Board, IDeA Center, University at Buffalo, 2010-12-31, Appendix Two Tables 1 and 2, and pp. 86-87 | the tables and text | P |

**Walking speed.**

| Fact | Source | Read | Level |
|---|---|---|---|
| The app's walking speed, 80 m/min (4.8 km/h) | the registry's `walk.speed` (V167), TfL 2015, 2.5 | the record | P |
| Pedestrian clearance at 3.5 ft/s (1.07 m/s), 4I.06 para. 07; walk plus clearance at 3 ft/s (0.91 m/s), para. 14; slower where people who walk slowly or use wheelchairs cross routinely, para. 10 | FHWA, MUTCD 11th Edition (December 2023), Part 4, and the 11th Edition with Revision 1 (December 2025), the same paragraphs unchanged, https://mutcd.fhwa.dot.gov/kno_11th_Editionr1.htm | 4I.06 in both | P |

## 2. Bikes

| Fact | Source | Read | Level |
|---|---|---|---|
| A solo upright cycle 1.8 m long, 0.65 m wide, turning circle outer radius 1.65 m, inner 0.85 m; the cycle design vehicle 2.8 x 1.2 m | Department for Transport, Cycle Infrastructure Design, LTN 1/20 (July 2020), Table 5-1 (Open Government Licence v3), https://assets.publishing.service.gov.uk/media/5ffa1f96d3bf7f65d9e35825/cycle-infrastructure-design-ltn-1-20.pdf | the table, 5.4.1 | P |
| Sheffield stands: spacing 1.2 m recommended, 1.0 m minimum; bay length 2 m; access aisle 3 m (1.8 minimum) | the same, Table 11-2 | the table | P |

## 3. Vehicles

| Fact | Source | Read | Level |
|---|---|---|---|
| The design vehicles' dimensions in metres (height, width, length, front and rear overhang, wheelbase): P 1.30, 2.13, 5.79, 0.91, 1.52, 3.35; SU-9 (SU-30) 3.35 to 4.11, 2.44, 9.14, 1.22, 1.83, 6.10; CITY-BUS 3.20, 2.59, 12.19, 2.13, 2.44, 7.62; the same in feet in Table 2-4a | AASHTO, A Policy on Geometric Design of Highways and Streets, 7th Edition (2018), Table 2-4b and 2-4a; the owner's copy, from the owner's Notion (Documentation DB), kept in the session's scratch folder | the tables, and the page image of 2-5b | P |
| Minimum design turning radius, centreline turning radius (CTR), minimum inside radius, in metres: P 7.26, 6.40, 4.39; SU-9 12.73, 11.58, 8.64; CITY-BUS 12.80, 11.52, 7.45 | the same, Table 2-5b | the table | P |
| **The book's two tables differ for the city bus:** Table 2-5a gives its minimum design turning radius as 41.6 ft (12.68 m), Table 2-5b as 12.80 m; every other value of the three agrees within rounding. The app uses 2-5b, as it works in metres, and says so | Tables 2-5a and 2-5b, compared here | | P (both read) |
| The turning path: the speed below 10 mph, the outer front wheel on the arc the steering allows; the path bounded by the outer trace of the front overhang and the path of the inner rear wheel; the CTR roughly the minimum design turning radius less half the front width | the same, 2.8.2 and Table 2-5's note | the text | P |
| The same turning radii in feet, as Table 2-5a | Texas DOT, Roadway Design Manual, 4.3.3 Table 4-1, https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-3-traffic-characteristics/4-3-3-control-vehicles.html | the table | S (agrees) |
| The same body dimensions, from an earlier edition (P 4.25 ft high) | Indiana DOT, 2013 Design Manual, Chapter 40, Figure 40-4A, https://www.in.gov/dot/div/contracts/design/Part%203/Chapter%2040%20-%20Basic%20Design%20Controls.pdf | the figure | S (agrees) |
| 23 CFR 625.4(d)(1)(i) incorporates AASHTO GDHS-7, the 7th Edition (2018), for the National Highway System; 625.4 last amended at 87 FR 41 (3 January 2022) | eCFR, Title 23 Part 625, current to 2026-10-15, https://www.ecfr.gov/current/title-23/chapter-I/subchapter-G/part-625 | the section | P |
| The free update of the design vehicles needs a login to download; its online pages are images | National Academies, Highway and Street Design Vehicles: An Update (2023), doi:10.17226/27236 | the pages | refused |
| Off-street parking bay at least 4.8 m long by 2.4 m wide, 8.3.58; aisle for a 2.4 m bay 6.0 m at 90 degrees, 4.2 m at 60, 3.6 m at 45, 8.3.51 | Department for Transport, Manual for Streets (2007), https://assets.publishing.service.gov.uk/media/5a7e0035ed915d74e6223743/pdfmanforstreets.pdf | 8.3 | P |
| The largest refuse vehicle about 11.6 m long, turning circle 20.3 m (after BS 5906:2005) | the same, 6.8.7 | the paragraph | S |
| Philadelphia's zoning code (parking) | codelibrary.amlegal.com and phila.gov | refused a script (403) | refused |

## 4. Trees

| Fact | Source | Read | Level |
|---|---|---|---|
| 14,487 measured urban trees in 17 US cities, with tree type (broadleaf, conifer, palm; deciduous, evergreen; small, medium, large), height and average crown diameter | McPherson, van Doorn and Peper, Urban Tree Database, Forest Service Research Data Archive RDS-2016-0005 (public domain), TS3_Raw_tree_data.csv; the archive's SHA-256 c0c888e2... matched its page | the raw data | P |
| Medians of the trees at or above their type's median dbh: broadleaf deciduous medium 14.0 m high, crown 11.9 m (crown/height 0.85); large 20.0 m, 15.9 m (0.81); conifer evergreen medium 12.5 m, 8.5 m (0.74); large 20.0 m, 10.7 m (0.57) | worked out here from that file, the script in the session's scratch folder | | S (our median of P data, the method said) |
| GSL, growing season length: from the first span of at least 6 days with daily mean temperature above 5 C to the first span after 1 July (1 January in the Southern Hemisphere) of 6 days below 5 C | ETCCDI, the 27 core climate indices, http://etccdi.pacificclimate.org/list_27_indices.shtml | the definition | P |
| The site's daily mean temperatures, ten years | the app's climate step (V159: Open-Meteo's ERA5 archive) | the code | P |

**The vehicles, worked out.** At the sharpest turn the turn's centre lies on the rear axle's line, and the
front axle's middle on the CTR, so the rear axle's middle is the square root of CTR squared less the wheelbase
squared from the centre (P 5.45 m, SU-30 9.84 m, CITY-BUS 8.64 m); the front overhang's outer corner is then
sqrt((that + half the width)^2 + (wheelbase + front overhang)^2) from it (7.79, 13.27 and 13.92 m). Checked against
the book: that distance less half the width gives the minimum inside radius within 0.02 m for P and SU-30
(4.39 and 8.62 against 4.39 and 8.64); the bus's wheels sit inside its body (7.35 against 7.45). The plan shows
the ring from the minimum inside radius out to the overhang's corner, with the minimum design turning radius
between. The wheels' sizes (0.65 m for the car, 1.0 m for the truck and bus) and the bodies' shapes are the
app's (`app.assets`).

**Leaf.** A deciduous tree is in leaf over the site's thermal growing season, worked out with ETCCDI's
rule from the climate the app already fetches, year by year, the median start and end kept. A tree's
leaves come out some weeks after the season starts; that is said. Without the climate, a deciduous tree
is treated as in leaf all year, and that is said too (no rule by latitude is invented).

## 5. What the app has (read 2026-10-19)

- The Assets library (V124): built-ins of boxes and cylinders (`A3D_ASSET_STARTER`, `bimAsmMesh`), placed as
  solids (`bimPlaceFamilyInstance`) with their own mesh.
- Shadows come from solids (`bimShadowCasters`), in the plan's shadows, sun hours (V143) and the shadows
  analysis (V164); the context's trees are points with a mesh and cast none.
- The context's trees (V157): `bimTreeMesh`, a hexagonal trunk and a 20-face crown; height from the tag or
  the registry's `app.context` tree height, crown `diameter_crown` or 0.6 of the height.
- The renderer (V152 to V156) merges solids into batches; it has no GPU instancing. Undo keeps a JSON
  snapshot, so a thousand trees are measured in memory and in the project's size.
- The registry (V167) already holds catalogue records for the 2010 ADA Standards, the MUTCD (11th with
  Revision 1) and the Green Book (7th); V169 adds the values it uses to them.

## 6. The owner's decisions (2026-10-19)

1. **Vehicles:** sized to AASHTO's design vehicles; the owner shared the Green Book (their Notion, 2026-10-19),
   read here for Tables 2-4 and 2-5 and 2.8.2; the book stays out of the repository, only its numbers are used, cited.
2. **The van:** AASHTO's SU-30 single-unit (delivery) truck, named as such.
3. **The context's trees:** the same tree model, by OpenStreetMap's `leaf_type` and `leaf_cycle`; the crown
   ratio from the Urban Tree Database by leaf type (broadleaf 0.85, conifer 0.74), 0.6 kept where untagged.
4. **Parking bay where no rule is recorded:** Manual for Streets' 2.4 x 4.8 m, applied outside its place and
   said so, overridable per project.

## 7. Still open

- The city bus's minimum design turning radius: 12.80 m (2-5b) against 41.6 ft (2-5a); kept as 2-5b, overridable.
- The Green Book's turning templates (Figures 2-10 to 2-18) are not drawn: the app shows the ring of the sharpest
  turn, not a path through a given angle (the traffic simulation, V171).
- The manual chair users' eye height row (Table 2 of the IDeA report) did not come through in the text;
  the all-users mean is used and said.
- A child's proportions: extrapolated from adults, an estimate.
