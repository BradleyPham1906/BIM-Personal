# Floor (gravity) loads and wind loads from the real place: ASCE/SEI 7-22, with EN 1991 for comparison

One of four parallel research notes on giving the frame solver loads from the real place
(2026-11-21). Method: `docs/research/research-protocol.md`. This side: uniform live loads and their
reduction, roof live load, default superimposed dead loads, and wind on the main wind force
resisting system (MWFRS) of enclosed rigid buildings by the directional procedure (ASCE 7-22
chapters 26 and 27, Part 1), the basic wind speed data behind it, and EN 1991-1-4 / 1-1 as a
comparison only. Experiment script: `docs/research/experiments/physical-world/wind_loads.py`
(data and checks only; it passes, run 2026-11-21 with `python3 -I`). Standard text is paraphrased;
quotes are short.

## Abstract

ASCE/SEI 7 is sold, so its 7-22 numbers here are S (two or more dependable copies agreeing, or a
code that reproduces them), except where an older edition's text is public (ASCE 7-02, incorporated
by reference in the CFR, is P for the wall pressure coefficients, the four wind load cases and the
0.613 constant) and where an adopted building code reproduces the same rule (IBC 2021 Table 1607.1
and 1607.12, read in Seattle's adopted code, P for that code). The 7-22 wind changes that matter to
code are confirmed by three independent sources and by a fit: the directionality factor Kd left the
velocity pressure and moved into the pressure equation, and the Kz profile changed (new alpha and
zg for B, C and D, coefficient 2.41 instead of 2.01); the new formula reproduces 88 of 88 tabulated
B and C values to two decimals. No documented keyless wind speed service exists: ATC's Hazards by
Location closed on 2024-12-31 and ASCE's own API needs a paid key. ASCE's ArcGIS back end
(`gis.asce.org/.../ASCE722/w2022_mri700/ImageServer/identify`) does answer keylessly from here, with
CORS for any origin, but it is undocumented and serves a commercial product; whether to use it is
the owner's decision. Recommendation: the user enters V (with Risk Category and Exposure), the app
offers the ASCE Hazard Tool link, and the solver gets storey forces from a pure function tested on
the worked examples below.

## 1. The question and the hypotheses

Question: what exact equations, coefficients and data does the app need to turn a place (a site, a
building's outline and its storeys) into (a) floor live loads with ASCE 7-22's reduction and (b)
wind storey forces for the frame solver, and can the basic wind speed come from a free, keyless web
service?

| # | Hypothesis (falsifiable) | Outcome | Evidence |
|---|---|---|---|
| H1 | A documented, free, keyless web service returns ASCE 7-22 basic wind speed by latitude and longitude, with CORS | **Failed** as stated. ATC closed; ASCE's API needs a key and pricing. An undocumented ASCE ArcGIS endpoint is keyless and CORS-open | Section 4.3 |
| H2 | ASCE 7-22 kept 7-16's Kz terrain constants (alpha, zg) | **Failed.** B 7.0/1200 ft became 7.5/3280 ft, C 9.5/900 became 9.8/2460, D 11.5/700 became 11.5/1935, and 2.01 became 2.41 | Ghosh deck; Oasis code; fit of 88 table values (check 1) |
| H3 | Kd is still inside q_z in 7-22 | **Failed.** q_z = 0.00256 Kz Kzt Ke V^2; Kd multiplies q in p (Eq. 27.3-1) | ICC deck; Smith (Professional Roofing 2023); Oasis code |
| H4 | 7-22's live load reduction (4.7) is the same formula, factors and limits as IBC 2021 1607.12.1 | **Held** (S) | Seattle 2021 and NYC 2022 codes agree; ENERCALC's 7-22 example uses the same numbers |
| H5 | The MWFRS wall Cp (0.8; -0.5/-0.3/-0.2; -0.7) and GCpi +/-0.18 are unchanged from 7-02 to 7-22 | **Held**, medium confidence (S) | 7-02 text (P); ICC 7-22 example uses +/-0.18; no source lists a change |
| H6 | The ASCE Hazard Tool shows the grid value rounded, and converts mph to m/s before rounding | **Held** (P, from the tool's own code) | `windUtil.js formatWindValue`: `Math.round(mph * 0.44704)` |
| H7 | 7-22's tabulated Exposure D Kz equal the 7-22 formula | **Failed, small.** The ICC deck's D column follows 7-16's constants; the 7-22 formula gives up to 0.015 more | Check 1 in the script |

## 2. Method

### 2.1 Search log

| # | Where | Query or request | Result | Kept / why |
|---|---|---|---|---|
| 1 | Repo | `grep` structure/, registry.js | Loads only D and L, levels carry `dl`/`ll` kPa, lateral point load at a column top; 2.3.1 combos 1, 2 | Kept: section 8 |
| 2 | curl | hazards.atcouncil.org, /api | Page: service ceased 2024-12-31, points to ASCE tool; /api 404 | Kept: H1 |
| 3 | curl | api-hazard.asce.org | 307 to /login, "ASCE API Dashboard" | Kept: keyed |
| 4 | curl | ascehazardtool.org, its app JS (config.js, standards.config.js, stores/queries/wind.js, utils/windUtil.js, Utilities.js) | 7-22 risk category to MRI layers, units, rounding, mosaic | Kept: P for how the tool reads its data |
| 5 | curl | gis.asce.org/arcgis/rest/services/ASCE722?f=json and `.../w2022_mri{300,700,1700,3000}/ImageServer/identify` at 6 cities, with `Origin:`; OPTIONS preflight | JSON pixel values; `access-control-allow-origin` echoes the origin; preflight 403 with CORS headers | Kept: H1, data |
| 6 | Web | asce.org hazard tool API page, terms page, API documentation PDF | Key required, "Get pricing"; terms "as is"; wind fields and RC to MRI table | Kept |
| 7 | curl | earthquake.usgs.gov/ws/designmaps/asce7-22.json | Keyless, `ACAO: *`, seismic only | Kept as negative for wind |
| 8 | curl | windspeed.atcouncil.org | Proxy tunnel closed | Recorded as refused |
| 9 | WebSearch | ASCE 7-22 Table 26.11-1 alpha zg changes | Pointers: ICC decks, GAF, FEMA fact sheet | Pointers only |
| 10 | curl | FEMA ASCE 7-22 wind fact sheet PDF | 403 | Refused host, recorded |
| 11 | curl | ICC "Demystifying Loads ... 2024 IBC and ASCE/SEI 7-22" Part 1 and Part 2 PDFs (iccsafe.org) | Eq. 26.10-1 and 27.3-1 as in 7-22, Kz table 7-16 vs 7-22, Kd 0.85, GCpi +/-0.18, Example 5.12 | Kept: S |
| 12 | curl | S.K. Ghosh, "Ever-changing structural provisions ... Wind" (ICC 2023) | Kz formula 2.01 to 2.41, Table 26.11-1 old/new, B and C tables, rigid/flexible, na formulas, Ke table | Kept: S |
| 13 | curl | SPRI 2023 Chamberlain deck | Ke note: 1.00 always permitted | Kept: S |
| 14 | curl | ASCE NE Texas branch ASCE 7-16 deck | Ke introduced in 7-16, Denver 0.82 | Kept: S |
| 15 | WebFetch | Smith, Professional Roofing, May 2023 | B and C Kz changed for gradient height; Kd moved | Kept: S, third source |
| 16 | curl | Florida Building Commission ASCE 7-22 wind fact sheet (2024) | ATC will not support 7-22; ASCE tool named free; FBC note allows geodatabase speeds | Kept: S |
| 17 | curl / WebFetch | codes.iccsafe.org IBC 2021 and 2024 ch. 16 | 403 to both | Refused host, recorded |
| 18 | curl | up.codes IBC 2021 ch. 16 | 404 | Set aside |
| 19 | curl | Seattle 2021 Building Code ch. 16 (seattle.gov PDF) | Table 1607.1, 1607.5, 1607.12, 1607.14 in full | Kept: P (adopted code), S for model IBC |
| 20 | curl | NYC 2022 Building Code ch. 16 | Same 4.57 equation, limits and KLL | Kept: second copy |
| 21 | curl | law.resource.org ASCE 7-02 (CFR IBR) | Table 4-1, 4.8 LLR, Table 4-2, Fig. 6-5 GCpi, Fig. 6-6 Cp, Fig. 6-9 cases, C6.5.10, Table C3-1 | Kept: P for 7-02 |
| 22 | WebSearch / curl | ENERCALC 2026 "Live Load Reduction Verification Example" | 7-22 Table 4.7-1, Eq. 4.8-1, worked numbers | Kept: S (vendor), test data |
| 23 | WebFetch | Tekla Structural Designer 2025, ASCE 7 live loads | How a vendor applies 4.7 and 4.8 | Kept: practice |
| 24 | WebFetch / curl | CSI wiki "Wind load cases", docs.csiamerica.com lateral loads manuals | Wiki is a Confluence SPA and redirects; manuals 404 | Set aside, recorded |
| 25 | WebFetch | Bentley RAM docs, eccentric load cases | Only the Eurocode UK NA page answered | Kept for EN only |
| 26 | WebFetch | SkyCiv ASCE 7-22 wind docs | Rigid G 0.85 default; detail behind paywall | Kept: practice |
| 27 | GitHub search (api) / raw | ASCE 7 wind and live load reduction code | oasiseng ASCE-7-22 calculator (MIT), ibuilder/massing loads.py (MIT), clay-good/anvilate (MIT) | Kept: read as text, section 5 |
| 28 | gh api | repo metadata for those repos | Refused: "GitHub access to this repository is not enabled for this session" | Licences read from raw LICENSE files instead |
| 29 | curl | law.resource.org EN 1991 copies; archive.org | 404; archive.org 403 | Refused, recorded |
| 30 | curl | structuraldynamics.ulb.be EN 1991-1-4:2005+A1:2010 (public.resource copy) | Table 4.1, Eqs. 4.4-4.10, Table 7.1, 6.2, 7.1.2 | Kept: P for EN 1991-1-4 |
| 31 | curl | Danish NA to EN 1991-1-1 (ds.dk) | Danish Table 6.2 values; area reduction not applied in DK | Kept: P for DK only |
| 32 | WebSearch | ASCE 7-22 errata Table 26.10-1 Exposure D | No errata found; only general change notes | Counter-evidence search, nothing found |

### 2.2 Sources by kind

- Standard text, public: ASCE 7-02 (CFR copy); EN 1991-1-4:2005+A1:2010 (public.resource copy); adopted
  IBC 2021 (Seattle) and NYC 2022 chapter 16.
- Secondary reproductions of 7-22: ICC's 2024 training decks (Part 1, Part 2); S.K. Ghosh's ICC 2023
  deck; SPRI 2023; ASCE NE Texas branch deck (7-16); Smith 2023; Florida Building Commission 2024.
- Vendors: ENERCALC (7-22 example), Tekla Structural Designer, SkyCiv, Bentley RAM; ASCE Hazard Tool (its
  code and API documentation).
- Open implementations read as text: Oasis Engineering ASCE 7-22 C&C calculator (MIT), ibuilder/massing
  `loads.py` (MIT), clay-good/anvilate `building_loads.py` (MIT).
- Experiments here: the hazard endpoints (section 4.3) and `wind_loads.py` (checks 1 to 4, examples a, b).

### 2.3 Independent check

Not yet done: the protocol's second reader must re-read the sources of every fact in section 3 marked
"code uses". Until then those stay at the level shown, and nothing P is claimed for 7-22 itself.

## 3. Findings by topic

Levels: P primary, S secondary, U unverified. Confidence: H high, M medium, L low.

### 3.1 Uniform live loads (ASCE 7-22 Table 4.3-1; IBC Table 1607.1)

IBC 2021 Table 1607.1, read in Seattle's adopted 2021 code (Seattle's amendments are shown in double
parentheses and touch only canopies and marquees). ASCE 7-22 Table 4.3-1 itself was not read; IBC's table
mirrors ASCE 7 and ICC's 2024 deck calls the 2024 changes "primarily reformatting". SI values: ASCE prints
kN/m2 beside psf (7-02 Table 4-1 shows 50 psf = 2.4, 100 psf = 4.79). The conversion is 1 psf =
0.04788 kPa.

| Occupancy or use (selection the app needs) | psf | kPa | Reduction | Source, level, confidence |
|---|---|---|---|---|
| Offices | 50 | 2.40 | yes | IBC 2021 T1607.1 item 23 (P Seattle, S 7-22), H |
| Office lobbies and first-floor corridors | 100 | 4.79 | yes | same, H |
| Corridors above first floor (offices, hospitals, libraries, schools) | 80 | 3.83 | yes | same, H |
| Residential, hotels and multifamily: private rooms and their corridors | 40 | 1.92 | yes | item 26, H |
| Hotels and multifamily: public rooms and their corridors | 100 | 4.79 | no (note a) | item 26, H |
| One- and two-family: all other areas | 40 | 1.92 | yes | item 26, H |
| One- and two-family: habitable attics and sleeping areas | 30 | 1.44 | yes | item 26, H |
| Schools: classrooms | 40 | 1.92 | yes | item 28, H |
| Hospitals: patient rooms / operating rooms, labs | 40 / 60 | 1.92 / 2.87 | yes | item 18, H |
| Libraries: reading rooms / stack rooms | 60 / 150 | 2.87 / 7.18 | yes / note b | item 20, H |
| Assembly: fixed seats / lobbies, movable seats, other | 60 / 100 | 2.87 / 4.79 | no (note a) | item 4, H |
| Dining rooms and restaurants | 100 | 4.79 | no (note a) | item 9, H |
| Stores, retail: first floor / upper floors | 100 / 75 | 4.79 / 3.59 | yes | item 34, H |
| Storage warehouses: light / heavy | 125 / 250 | 5.99 / 11.97 | note b | item 33, H |
| Manufacturing: light / heavy | 125 / 250 | 5.99 / 11.97 | note b | item 21, H |
| Garages, passenger vehicles only | 40 | 1.92 | note c | item 15, H |
| Stairs and exits (other than one- and two-family) | 100 | 4.79 | yes | item 31, H |
| Roofs, ordinary flat, pitched, curved (not occupiable) | 20 | 0.96 | by 4.8 (roof rule) | item 27, H |
| Roof areas used for assembly | 100 | 4.79 | no (note a) | item 27, H |
| Partition allowance (where partitions can move, unless Lo >= 80 psf) | 15 | 0.72 | not reducible (ICC: 7-22 4.3.2) | IBC 1607.5 (P Seattle); ICC Part 1 (S), H |

Notes of the table: (a) no reduction; (b) only by the heavy-load rule (20 % for members supporting two or
more floors); (c) only by the garage rule (the same 20 %). Concentrated loads (for example 2,000 lb =
8.9 kN on offices) are in the same table and are not needed for the frame solver's floor takedown.

### 3.2 Live load reduction (ASCE 7-22 4.7; IBC 1607.12.1)

| Fact | Value | Source, level, confidence |
|---|---|---|
| Equation (SI) | L = Lo (0.25 + 4.57 / sqrt(KLL AT)), AT in m2 (US: 15 / sqrt(KLL AT), ft2) | IBC 2021 Eq. 16-7 (P Seattle); NYC 2022 same; 7-22 Eq. 4.7-1 per ENERCALC (S); 7-02 4.8.1 (P), H |
| Applies when | KLL AT >= 400 ft2 = 37.16 m2 | same, H |
| Lower limits | L >= 0.50 Lo for members supporting one floor; >= 0.40 Lo for two or more floors | same; ENERCALC 7-22, H |
| KLL, Table 4.7-1 | interior columns 4; exterior columns without cantilever slabs 4; edge columns with cantilever slabs 3; corner columns with cantilever slabs 2; edge beams without cantilever slabs 2; interior beams 2; all others (edge beams with cantilever slabs, cantilever beams, one-way and two-way slabs, members without continuous shear transfer normal to their span) 1 | IBC T1607.12.1 (P Seattle); Tekla (S); ENERCALC (KLL 4, 7-22 Table 4.7-1), H |
| Heavy live loads | Lo > 100 psf (4.79 kPa): not reduced, except members supporting two or more floors may take up to 20 % off, never below the formula's L | IBC 1607.12.1.2 (P Seattle), H |
| Passenger vehicle garages | not reduced, except the same 20 % for two or more floors | 1607.12.1.3, H |
| Assembly (and the other note-a rows) | not reduced | Table note a, H |
| One-way slabs | AT not more than the span times 1.5 times the span | 1607.12.1.1, H |
| Roof live loads | not reduced by 4.7; by 4.8 instead (occupiable roofs by 4.7) | 1607.12, 1607.14.2.2, H |
| Alternative IBC method (1607.12.2, R = 0.08(A - 150)) | IBC-only alternative, not ASCE 7 | P Seattle; not for the app's first pass |

Practice: Tekla applies the factor to columns of any material, concrete walls and gravity-only steel beams,
finds AT by applying a unit load to the floors, and leaves KLL for cantilever slabs to the user because it
cannot detect them (Tekla 2025 page). The app's tributary takedown (V106) already finds AT by Voronoi cells
and the number of floors above a column (section 8), which is what the formula needs.

### 3.3 Roof live load (ASCE 7-22 4.8; IBC 1607.14.2)

Lr = Lo R1 R2 with 12 <= Lr <= 20 psf (0.58 to 0.96 kPa). R1 = 1 for At <= 200 ft2 (18.58 m2); 1.2 -
0.001 At between 200 and 600 ft2 (SI 1.2 - 0.011 At, 18.58 to 55.74 m2); 0.6 for At >= 600 ft2. R2 = 1 for
F <= 4; 1.2 - 0.05 F for 4 < F < 12; 0.6 for F >= 12, where F is the rise in inches per foot (SI: F = 0.12
x slope in percent). Source: IBC 2021 Eqs. 16-10 to 16-16 (P Seattle); 7-22 Eq. 4.8-1 per ENERCALC (S,
worked: At 570 ft2, 5:12 gives 11.97, so the 12 psf minimum controls). Confidence H. Note the SI R1 uses
0.011, which is 0.001 x 10.764 rounded.

### 3.4 Superimposed dead loads (defaults only)

From ASCE 7-02 Table C3-1 (P for 7-02; commentary, so a guide, not a requirement; later editions keep a
table C3.1-1a, not read here). SI column as printed: mechanical duct allowance 0.19 kPa; suspended steel
channel ceiling 0.10; acoustical fiberboard ceiling 0.05; gypsum board 0.008 per mm; ceramic or quarry tile
19 mm on 13 mm mortar 0.77; hardwood flooring 22 mm 0.19; linoleum or asphalt tile 6 mm 0.05; terrazzo 25 mm
on stone-concrete fill 1.53; single-ply roof membrane 0.03; four-ply felt and gravel 0.26. Partitions are
a live load (15 psf, 3.1). A default floor SDL built from these (finish 0.77 + ceiling 0.10 + ducts 0.19 =
1.06 kPa, rounded to 1.0 to 1.2 kPa) is our arithmetic (U as a recommendation; each part P for 7-02).
Confidence M: the values are old but such weights do not change.

### 3.5 Wind: velocity pressure (ASCE 7-22 26.6 to 26.10)

| Fact | Value | Source, level, confidence |
|---|---|---|
| Eq. 26.10-1 | q_z = 0.00256 Kz Kzt Ke V^2 (psf, V mph); SI q_z = 0.613 Kz Kzt Ke V^2 (N/m2, V m/s). **No Kd** | ICC Part 2 slides 38, 46 (S); Smith 2023 (S); Oasis code (S); H. The SI constant: 7-02 C6.5.10 (P) derives 0.613 = 1/2 x 1.225 kg/m3; check 4 |
| Change from 7-16 | 7-16 had Kd inside q_z | Ghosh slide 113 (S); NE Texas deck (S); H |
| Kd | 0.85 for buildings, MWFRS and C&C (Table 26.6-1), now applied in p | ICC Part 2 slide 38 (S); Oasis (S); 7-02 Table 6-4 0.85 (P); H |
| Kz formula (Table 26.10-1 note) | Kz = 2.41 (z/zg)^(2/alpha) for 15 ft (4.6 m) <= z <= zg; z < 15 ft uses 15 ft; Kz = 2.41 for zg <= z <= 3280 ft (1000 m) | Ghosh slide 141 (S); Oasis (S); H |
| Table 26.11-1 (7-22) | B: alpha 7.5, zg 3280 ft (1000 m); C: 9.8, 2460 ft (750 m); D: 11.5, 1935 ft (590 m) | Ghosh slide 142 (S); Oasis (S); fit check 1; H |
| Table 26.11-1 (7-16) | B 7.0 / 1200 ft; C 9.5 / 900 ft; D 11.5 / 700 ft; coefficient 2.01 | Ghosh slide 142 (S), fit check 1, H |
| What changed | B and C tabulated values changed (gradient height revised): B by up to -0.11 at 500 ft, C by 0.00 to -0.04 | Ghosh slides 143-144; Smith 2023; H |
| Exposure B, Chapter 28 only | use Kz 0.70 below 30 ft in the envelope procedure (not chapter 27) | ICC Part 2 slide 41 note (S); Oasis comment (S); H |
| Ke (26.9) | Table 26.9-1: 0 ft 1.00, 1000 ft 0.96, 2000 0.93, 3000 0.90, 4000 0.86, 5000 0.83, 6000 0.80; Ke = 1.00 always permitted; table note gives an exponential, read here as e^(-0.0000362 zg) with zg ground elevation in ft (e^(-0.000119 zg) in m) | Table: Ghosh slide 114 (S, 7-16); note 1.00: SPRI deck (S); formula: Oasis code only (S single copy), matches the table to 0.006 (check 3); M. ICC Part 2 lists 26.9 Ke in 7-22 (S) |
| Kzt (26.8) | 1.0 on flat ground; 7-22 removed the waiver for upwind features of similar height | ICC Part 2 slide 40; Ghosh slide 140 (S); H for 1.0 default |
| Units | 1 mph = 0.44704 m/s exactly; 1 ft = 0.3048 m; 1 psf = 0.04788 kPa | definitions; ASCE tool code uses 0.44704 (P); H |

### 3.6 Wind: gust, enclosure and pressures on the MWFRS (26.11 to 26.13, 27.3)

| Fact | Value | Source, level, confidence |
|---|---|---|
| Rigid vs flexible | flexible if the fundamental frequency n1 < 1 Hz; rigid if >= 1 Hz | Ghosh slide 105 (definitions, S); H |
| G, rigid | 0.85 (permitted) or calculated | 7-02 6.5.8.1 (P); SkyCiv default (S); H |
| Approximate frequency na (7-16/7-22 26.11.3, 7-10 26.9.3) | steel moment frames na = 22.2 / h^0.8; concrete moment frames 43.5 / h^0.9; other steel or concrete systems 75 / h; concrete or masonry shear walls 385 Cw^0.5 / h; h in ft. Allowed for h <= 300 ft and h < 4 Leff. SI (our conversion): 8.58 / h^0.8, 14.93 / h^0.9, 22.86 / h (h in m) | Ghosh slides 107-111 (S, printed as 7-10 numbering); 7-22 numbering U; M |
| Low-rise | buildings meeting the low-rise definition may be taken as rigid | Ghosh slide 106 (S, 7-10 wording); M |
| GCpi, enclosed | +0.18 / -0.18 (partially enclosed +/-0.55) | ICC Part 2 slides 42, 46, 113 (S 7-22); 7-02 Fig. 6-5 (P); Oasis (S); H |
| Eq. 27.3-1 | p = q Kd G Cp - qi Kd (GCpi); q = q_z on the windward wall at height z, q = q_h on leeward and side walls and roof | ICC Part 2 slides 38, 52, 54 (S); 7-02 Eq. 6-17 and Fig. 6-6 "use with" column (P); H |
| Wall Cp (Fig. 27.3-1) | windward 0.8 (with q_z); leeward -0.5 for L/B 0 to 1, -0.3 at 2, -0.2 at >= 4 (with q_h), linear interpolation permitted; side walls -0.7 (with q_h). L is the plan dimension parallel to the wind, B perpendicular | 7-02 Fig. 6-6 and note 2 (P); unchanged per H5 (S); H for 7-02, M for 7-22 |
| Load cases (Fig. 27.3-8) | Case 1: full windward plus leeward pressures, each principal axis separately. Case 2: 75 % of them with a torsional moment MT = 0.75 (PW + PL) B e, e = +/-0.15 B, each axis separately. Case 3: 75 % of Case 1 on both axes at once. Case 4: 75 % of Case 2 on both axes at once, MT = 0.563 (PWx + PLx) Bx ex + 0.563 (PWy + PLy) By ey | 7-02 Fig. 6-9 (P); ICC Part 2 example lists 27.3.5 cases 1-4 (S); Engineers Edge and RAM pointers (U); H for 7-02, M for 7-22 numbering |
| Torsion exemption | 7-22 Appendix D exempts some buildings from the torsional cases | ASCE Amplify page title only (U) |
| Minimum MWFRS load | 7-16/7-22 27.1.5: 16 psf on walls and 8 psf on the roof's vertical projection | U (memory, no source read), to confirm |

For a frame: on an enclosed building the internal pressure acts equally on the windward and leeward walls
and cancels in the net horizontal force, so a storey force is (p_windward(z) - p_leeward) x B x the
storey's tributary height. The level carries half the storey below and half above (the roof level carries
the top half storey, plus any parapet); the bottom half storey goes to the base. This is ordinary practice
(the ICC example tabulates windward p by height and a uniform leeward p), our statement (S).

### 3.7 Basic wind speed (26.5) and the data question

- 7-22 maps give V as a 3-second gust at 33 ft (10 m) in Exposure C, by Risk Category: RC I 300-year,
  II 700-year, III 1,700-year, IV 3,000-year MRI (ASCE API documentation PDF, P for the tool; 7-22 26.5.1
  map figures 26.5-1A to D, S). The tool states "linear interpolation between contours".
- 7-22 changed the maps (Florida: panhandle increased, peninsula unchanged since 2010) and allows the ASCE
  Wind Design Geodatabase in place of the maps (Florida fact sheet, S; FBC 2023 note). Special wind
  regions must be checked by the authority having jurisdiction (tool code and API PDF, P).
- See section 4.3 for the services tested.

### 3.8 Eurocode, for comparison only

EN 1991-1-4:2005+A1:2010 read in the public.resource copy (P); every value is a recommended one that a
National Annex may change. EN 1991-1-1 Table 6.2 was read only through the Danish NA (P for Denmark).

| Item | ASCE 7-22 | EN 1991-1-4 / 1-1 |
|---|---|---|
| Reference wind | V, 3-s gust, 10 m, Exposure C, MRI 300 to 3,000 years by Risk Category | vb, 10-min mean, 10 m, terrain II, 50-year (annual probability 0.02) |
| Pressure | q = 0.613 Kz Kzt Ke V^2 (no gust: G and Cp carry it) | qp(z) = [1 + 7 Iv(z)] 0.5 rho vm(z)^2, rho 1.25 kg/m3 (Eq. 4.8, 4.10) |
| Profile | power law, alpha and zg by exposure, z >= 4.6 m | log law: cr = kr ln(z/z0), kr = 0.19 (z0/0.05)^0.07 (Eqs. 4.4, 4.5), z >= zmin, zmax 200 m |
| Terrain | B, C, D | 0 (z0 0.003, zmin 1 m), I (0.01, 1), II (0.05, 2), III (0.3, 5), IV (1.0, 10) (Table 4.1) |
| Walls | Cp 0.8 / -0.5 to -0.2 / -0.7, x G 0.85 x Kd 0.85 | cpe,10: D +0.8 (h/d >= 1), +0.7 (h/d <= 0.25); E -0.5 (h/d = 1), -0.7 (>= 5), -0.3 (<= 0.25); side A -1.2, B -0.8, C -0.5 (Table 7.1) |
| Correlation | Kd and the case 3/4 factors | windward plus leeward force x 0.85 for h/d <= 1, 1.0 for h/d >= 5 (7.2.2(3) note) |
| Dynamic | G 0.85 rigid, n1 >= 1 Hz | cscd = 1 for buildings under 15 m (6.2(1)a) |
| Torsion | cases 2 and 4, e = 0.15 B | Figure 7.1: pressure removed from part of a face (7.1.2 note a) |
| Offices, live | 50 psf = 2.40 kPa | category B; Denmark 2.5 kPa (DK NA); recommended EN value U |
| Residential, live | 40 psf = 1.92 kPa | category A; Denmark 1.5 kPa |
| Area reduction | 0.25 + 4.57/sqrt(KLL AT), floor 0.5 / 0.4 | alpha_A by 6.3.1.2(10), not applied in Denmark; formula U here |

## 4. Experiments

### 4.1 `wind_loads.py` checks (run 2026-11-21, Python 3, one run, deterministic)

1. Kz formula vs tabulated: 88 B and C values (7-16 and 7-22, Ghosh) all within 0.005. Exposure D: the
   ICC deck's 7-22 D column (no change marked) matches the 7-16 constants within 0.0071; the 7-22
   formula (2.41, 1935 ft) is never lower and at most 0.0146 higher. So the 7-22 D table either was left
   at 7-16 values or the deck did not update it (H7, open).
2. ICC Example 5.12 (Exposure B, V 105 mph): Kz 1.0442 / 0.9614 / 0.7791 at 142.5 / 104.5 / 47.5 ft
   against the printed 1.04 / 0.96 / 0.78, and q 29.35 / 27.10 / 22.01 psf with the rounded Kz against the
   printed 29.4 / 27.1 / 22.0. The example rounds Kz before q.
3. Ke table vs e^(-0.0000362 zg): within 0.006 at all seven rows; the table looks rounded down at 4000 ft
   (0.8652 printed 0.86).
4. Constants: 0.5 x 1.225 = 0.6125 (0.613); 0.00256 reproduced; 15 x 0.3048 = 4.572 (4.57); 400 ft2 =
   37.16 m2; 100 psf = 4.788 kPa.

### 4.2 Worked examples (the test data)

See section 6.

### 4.3 Wind speed services, tested from here (2026-11-21)

| Service | Request | Answer | Key | CORS | Terms | Verdict |
|---|---|---|---|---|---|---|
| ATC Hazards by Location | `GET https://hazards.atcouncil.org/`, `/api/` | Notice: ceased operations 2024-12-31; `/api/` 404 | n/a | n/a | n/a | Gone |
| ASCE Hazard Tool API | `GET https://api-hazard.asce.org/` | 307 to `/login` (ASCE API Dashboard). Documented calls carry `token=`; page: "All ASCE Hazard Tool API requests need to authenticate with an API key", pricing on request; sample response shows "currentMonthlyRequestNumber": "69/1000" | yes | not tested (no key) | ASCE terms: "as is", user assumes all risk | Not keyless |
| ASCE ArcGIS back end (undocumented) | `GET https://gis.asce.org/arcgis/rest/services/ASCE722/w2022_mri700/ImageServer/identify?geometry={"x":-105.0,"y":40.0,"spatialReference":{"wkid":4326}}&geometryType=esriGeometryPoint&returnGeometry=false&returnCatalogItems=false&f=json` | `{"name":"Pixel","value":"106.977",...}` (mph, raw grid) | none | GET: `access-control-allow-origin` echoes `https://example.github.io`, with credentials; OPTIONS preflight 403 but with CORS headers (a simple GET needs no preflight) | none published for direct use; it is the back end of a product sold by subscription | Works today; use is the owner's decision (see 11) |
| USGS design maps | `GET https://earthquake.usgs.gov/ws/designmaps/asce7-22.json?...` | 301 to `/ws/building-codes/asce7-22/calculate`, JSON | none | `*` | public | Seismic only, no wind |
| NIST extreme winds | `https://www.itl.nist.gov/div898/winds/` | 200 (station data sets, not ASCE design speeds) | none | not tested | public | Not a design-speed source |
| windspeed.atcouncil.org | `GET /` | proxy: tunnel closed | | | | Refused, recorded |

How the ASCE tool reads 7-22 wind (its `standards.config.js` and `stores/queries/wind.js`, P): risk
categories I to IV map to `ASCE722/w2022_mri300`, `_mri700`, `_mri1700`, `_mri3000`; it also queries
`w2022_CONUS_Mosaic`, special wind region mosaics (`w2022_SWR_CA`, `SWR_CO_Mosaic_1007`), Puerto Rico and
island territories separately; displayed value = `Math.round(mph)` "Vmph" or `Math.round(mph x 0.44704)`
m/s. The CONUS mosaic at Denver returned 113.418, the same as `w2022_mri1700` there.

Raw values (mph) at RC I / II / III / IV: Denver 100.9 / 107.0 / 113.4 / 117.4; Chicago 100.0 / 107.1 /
114.3 / 119.2; Miami 157.0 / 169.2 / 181.4 / 189.2; San Francisco 86.5 / 91.8 / 98.6 / 102.8; New York
107.8 / 115.7 / 125.5 / 129.7; Houston 125.6 / 133.4 / 139.8 / 145.2; Philadelphia RC II 114.4. 7-16's
`ASCE/wind2016_700` at Denver gave 106.997 (7-16 and 7-22 are close there).

## 5. Practice and prior art

| Tool | What it does | Source, level |
|---|---|---|
| ASCE Hazard Tool | V by RC, special wind region flag, hurricane-prone flag; free web view, paid API | its code and pages, P |
| ETABS / SAP2000 | Auto wind "exposure from rigid diaphragm extents", windward 0.8 and leeward 0.5 inputs, case and eccentricity inputs (seen in a 2004 student report quoting ETABS output, ASCE 7-05) | U: CSI's wiki and manuals not reachable |
| Bentley RAM | Rigid diaphragms: one force at an offset; semirigid: windward and leeward pressures applied separately; Eurocode UK NA: windward eccentricity | RAM help pages, S (EN only read) |
| SkyCiv | Rigid G 0.85 default; frequency and damping for flexible; detail behind a paywall | its docs, S |
| Tekla Structural Designer | LLR as in 3.2, KLL manual for cantilever slabs, roof R2 = 1 assumed | its docs, S |
| ENERCALC | 7-22 LLR and roof examples (our test data) | its PDF, S |
| Oasis Engineering ASCE 7-22 C&C calculator (MIT) | alpha/zg 7.5/3280, 9.8/2460, 11.5/1935; Kz = 2.41 (max(z,15)/zg)^(2/alpha), capped at zg; Kd 0.85 outside qh; GCpi 0.18 / 0.55; Ke = e^(-0.0000362 z ft). Agrees with ours | raw `index.html`, read as text, P for its code |
| ibuilder/massing `loads.py` (MIT) | LLR with 15/sqrt, but always floors at 0.40 Lo (wrong for one floor), roof live unreduced, live loads by occupancy in psf | raw file, P for its code; a counter-example |
| clay-good/anvilate `building_loads.py` (MIT) | 4.57 and 37.16 constants; q = 0.613 Kz Kzt Kd Ke V^2, the 7-16 form (Kd inside q) | raw file, P for its code; shows the 7-16 form still common |

The 7-16 form (Kd in q) and the 7-22 form give the same p for MWFRS (Kd just moves), so a 7-16 tool's
pressures are not wrong for 7-22 by that alone; the Kz change is what differs.

## 6. Worked examples (test data; all arithmetic in `wind_loads.py`)

### 6.1 (a) Wind, 3 storeys, 30 m x 20 m, V = 50 m/s, Exposure C

Givens: enclosed, rigid (na for a steel moment frame 8.58 / 10.5^0.8 = 1.31 Hz >= 1), Kzt = Ke = 1,
Kd = 0.85, G = 0.85, levels at 3.5, 7.0, 10.5 m, h = 10.5 m, wind normal to the 30 m face, so B = 30 m,
L = 20 m, L/B = 0.667, leeward Cp = -0.5. Exposure C: alpha 9.8, zg 2460 ft = 749.808 m, 2/alpha =
0.204082. q = 0.613 Kz V^2 = 1532.5 Kz Pa. Windward p = q_z x 0.85 x 0.85 x 0.8 = 0.578 q_z. Leeward
p = q_h x 0.85 x 0.85 x (-0.5) = -0.36125 q_h.

| Level z (m) | z (ft) | Kz | q_z (Pa) | windward p (Pa) | net p = windward - leeward (Pa) | band (m) | height (m) | F = net x 30 x height (kN) |
|---|---|---|---|---|---|---|---|---|
| 3.5 | 11.48 (< 15, use 15) | 2.41 (15/2460)^0.204082 = 0.8512 | 1304.4 | 753.9 | 1312.3 | 1.75 to 5.25 | 3.50 | 137.79 |
| 7.0 | 22.97 | 0.9285 | 1422.9 | 822.4 | 1380.8 | 5.25 to 8.75 | 3.50 | 144.98 |
| 10.5 | 34.45 | 1.0086 | 1545.6 (= q_h) | 893.4 | 1451.7 | 8.75 to 10.50 | 1.75 | 76.21 |

Leeward p = -0.36125 x 1545.6 = -558.4 Pa at every level. Case 1 total = 358.99 kN (the band 0 to 1.75 m
goes straight into the base). Check by hand for level 2: ln(22.966/2460) = -4.6739; x 0.204082 =
-0.95386; e^ = 0.38524; x 2.41 = 0.9285; q = 1532.5 x 0.9285 = 1422.9; F = (822.4 + 558.4) x 30 x 3.5 /
1000 = 144.98 kN. Case 2: 0.75 F = 103.34, 108.74, 57.16 kN with MT = +/- 0.75 F x 0.15 x 30 = 465.04,
489.31, 257.23 kN m. Case 3: 0.75 F on both axes. Case 4: 0.563 F on both axes with the two torsions.
GCpi cancels in these net storey forces. Applying them to the app: the force at a level is shared among
the columns reaching it (the solver today takes a lateral point load at one column's top, section 8).
Method choice recorded: pressure at the level's height over its band. Integrating the Kz profile over each
band instead gives 138.01, 144.83 and 75.38 kN (+0.16 %, -0.10 %, -1.1 %), measured here with a 2,000-step
midpoint sum; a test must fix which method it expects.

### 6.2 (b) Live load reduction, office, Lo = 2.40 kPa, 8 m x 8 m bays

| Member | KLL | AT (m2) | KLL AT | 0.25 + 4.57/sqrt(KLL AT) | floor | L (kPa) | L x AT (kN) |
|---|---|---|---|---|---|---|---|
| interior column under 2 floors | 4 | 128 | 512 | 0.45197 | 0.40 | 1.0847 | 138.8 |
| interior column under 1 floor | 4 | 64 | 256 | 0.53563 | 0.50 | 1.2855 | 82.3 |
| interior beam, 8 m span at 4 m | 2 | 32 | 64 | 0.82125 | 0.50 | 1.9710 | 63.1 |
| interior beam, 4 m span at 4 m | 2 | 16 | 32 < 37.16 | none | | 2.4000 | 38.4 |
| interior column under 5 floors | 4 | 320 | 1280 | 0.37774 | 0.40 governs | 0.9600 | 307.2 |
| storage 7.18 kPa, column under 2 floors | 4 | 128 | | heavy: 20 % only | | 5.7440 | 735.2 |
| assembly lobby 4.79 kPa | | | | not reducible | | 4.7900 | |

Imperial cross-check (ENERCALC, 7-22): Lo 80 psf, KLL 4, AT 570 ft2, one floor: 80 (0.25 + 15/sqrt(2280))
= 45.131 psf, above 0.5 Lo = 40. Roof: Lo 20 psf, At 570 ft2, 5:12: R1 0.63, R2 0.95, 11.97 -> 12 psf.

## 7. Edges

- **z below 15 ft (4.572 m; the SI table may print 4.6 m):** use Kz at 15 ft; at 4.572 m vs 4.6 m Exposure C
  differs by 0.001. Exposure B in chapter 28 only: 0.70 below 30 ft.
- **z above zg:** Kz = 2.41 up to 3280 ft (1000 m); B's zg is 1000 m, so ordinary buildings never reach it.
- **Exposure D tabulated vs formula:** up to +0.015 for the formula (H7); the formula is the conservative
  choice.
- **Exposure changes by direction:** exposure is decided per wind direction from upwind roughness
  (7-22 26.7; ICC Part 2 slide 39 notes about 80 % of buildings are B, NAHB). The app needs one exposure per
  direction, not one per site (S for the rule, U for the 80 %).
- **L/B interpolation:** leeward Cp linear between 1 (-0.5), 2 (-0.3) and 4 (-0.2); -0.5 below 1, -0.2 above 4
  (7-02 note 2, P). Wind on the 20 m face of the example: L/B = 1.5 gives -0.4.
- **Rigid vs flexible:** n1 < 1 Hz makes G a calculation (Gf); the approximate na is allowed only for
  h <= 300 ft and h < 4 Leff.
- **Ke:** 1.00 is always allowed (conservative); Denver at 5,280 ft gives 0.83 by the formula, 0.82 in the
  branch deck (table interpolation).
- **Kd placement:** a 7-16 tool puts Kd in q; the 7-22 q is larger by 1/0.85, p is the same.
- **Live load reduction exceptions:** Lo > 4.79 kPa (100 psf), passenger garages, note-a occupancies
  (assembly, public rooms of hotels and multifamily, dining, yards, roof assembly), KLL AT < 37.16 m2, one-way
  slab AT cap, roofs by 4.8. A member supporting one floor never below 0.5 Lo, two or more never below 0.4 Lo.
- **Units:** psf x 0.04788 = kPa; mph x 0.44704 = m/s; ft x 0.3048 = m; ft2 x 0.0929 = m2. The ASCE tool
  converts mph to m/s before rounding: RC II Denver 106.977 mph shows 107 mph or 48 m/s (47.8).
- **Special wind regions and hurricane-prone regions:** the mapped V is not the answer there; the app must
  say so (tool's `isSpecialWindZone`).

## 8. What the app already has

- `src/js/engine/structure/analytical-model.js` 160-210: `BIM_LOAD_KINDS` line (kN/m, down), point (kN, down),
  lateral at top (kN); `bimLoadProblem` accepts only cases `D` and `L` and lateral loads only on columns along
  X or Z; `bimStructLoads` puts a lateral load on the member's top node. Wind needs a new case `W` and the
  ASCE 7-22 2.3.1 combinations that carry it (1.2D + 1.0W + L + 0.5Lr, 0.9D + 1.0W), which the registry
  (`src/js/engine/standards/registry.js` 209-212, 993-998) does not hold yet.
- `src/js/engine/structure/tributary-loads.js` 6-19: Voronoi tributary areas per level, takedown of column
  axial loads, D and L in kPa from Levels; it says live load reduction is not included. AT and the count of
  floors above are both available there, which is what 4.7.2 needs.
- `src/js/engine/structure/analysis-properties.js` 131-132: per-level Dead (kPa) and Live (kPa, unreduced)
  inputs. An occupancy list from 3.1 can fill Live.
- Y is up, kN and m; the wind directions the solver accepts are X and Z.

## 9. Risks and threats to validity

- ASCE 7-22's own text was not read: every 7-22 number is S. The B and C fit (88 values) makes the Kz
  constants very likely right; the Cp and load cases rest on 7-02's text plus "no change" evidence.
- Section numbers of 7-22 for frequency (26.11.x) and minimum loads (27.1.5) are U.
- The Ke exponential is from one implementation (Oasis) and a fit; the table is from a 7-16 deck.
- The ASCE ArcGIS service may change or close without notice, and using it may conflict with ASCE's
  commercial terms (none were found for it either way).
- The Exposure D discrepancy (H7) is unresolved.

## 10. Still open (U)

1. ASCE 7-22 text itself (sold): Table 4.3-1, 4.7, 4.8, 26.5 to 26.13, Fig. 27.3-1 and 27.3-8; the SI Table
   26.11-1 values in metres; Table 26.10-1 column D. Needs the owner's copy or the second reader's sources.
2. Ke formula form in 7-22 (only the 7-16 table and one code copy read).
3. Minimum MWFRS wind load (16 psf walls, 8 psf roof) and its 7-22 section.
4. Section numbers of the approximate frequency equations in 7-22.
5. Appendix D torsional exemptions in 7-22.
6. CSI's documentation for auto wind (wiki unreachable as a script, manuals 404).
7. EN 1991-1-1 recommended Table 6.2 values and the alpha_A / alpha_n formulas (only the Danish NA read).
8. Refused hosts: codes.iccsafe.org (403), www.fema.gov PDF (403), archive.org (403), windspeed.atcouncil.org
   (tunnel closed); CSI wiki redirects to an SPA.

## 11. The owner's decisions

1. Basic wind speed: (a) the user enters V (with Risk Category), the app links to the ASCE Hazard Tool; or
   (b) the app also calls ASCE's undocumented ArcGIS service (keyless, CORS-open, works today, no published
   terms for direct use, serves a paid product). Recommendation (a), with (b) only after asking ASCE.
2. Exposure D: use the 7-22 formula (conservative, up to +1 %) or a tabulated column once the text is read.
3. Scope of the first wind phase: MWFRS directional procedure, enclosed, rigid, Case 1 only, or Cases 1 to 4
   (Case 2 and 4 need torsion as a moment at each level, which the solver does not take today).
4. Live load reduction on by default in the takedown and the frame, or as a switch (the takedown says
   leaving it out is conservative).

## 12. References (all read 2026-11-21)

| Source | URL | What was read | Level |
|---|---|---|---|
| ASCE 7-02, Minimum Design Loads for Buildings and Other Structures (CFR incorporation by reference copy) | https://law.resource.org/pub/us/cfr/ibr/003/asce.7.2002.pdf | Table 4-1, 4.8, Table 4-2, Fig. 6-5, 6-6 and notes, 6-9, Eq. 6-15, 6.5.8.1, C6.5.10, Table C3-1 | P (7-02) |
| City of Seattle, 2021 Seattle Building Code, chapter 16 (IBC 2021 with amendments) | https://www.seattle.gov/documents/Departments/SDCI/Codes/SeattleBuildingCode/2021SBCChapter16.pdf | 1607.1 to 1607.14, Tables 1607.1, 1607.12.1 | P (Seattle), S (IBC 2021) |
| NYC 2022 Building Code, chapter 16 | https://www.nyc.gov/assets/buildings/codes-pdf/cons_codes_2022/2022BC_Chapter16_StructuralDesignWBwm.pdf | 1607.11.1 equation, limits, KLL, heavy loads | P (NYC), second copy |
| ICC, Demystifying Loads for Building Officials, 2024 IBC and ASCE/SEI 7-22, Part 1 | https://www.iccsafe.org/wp-content/uploads/DemystifyingLoads_24IBC_ASCE7-22_EC-85122-Part1.pdf | live load slides 25-29, partitions | S |
| ICC, same, Part 2 | https://www.iccsafe.org/wp-content/uploads/DemystifyingLoads_24IBC_ASCE7-22_EC-85122-Part2.pdf | slides 30-55 (wind changes, Kd, Kz table, GCpi, Example 5.12), 113-118 | S |
| S.K. Ghosh, Ever-changing Structural Provisions of our Building Codes - Wind (ICC, 2023) | https://iccsafe.org/wp-content/uploads/Ever-changing-Structural-Provisions-of-our-Building-Codes-Wind.pdf | slides 105-114, 140-144 | S |
| Chamberlain, SPRI 2023 Wind Design Symposium, ASCE 7 | https://www.spri.org/wp-content/uploads/2023/10/2-2023-WDS-ASCE-7_Chamberlain.pdf | slides 15, 27-28 (Ke) | S |
| ASCE Northeast Texas Branch, ASCE 7-16 presentation (2021) | https://branches.asce.org/northeasttexas/sites/branches.asce.org.northeasttexas/files/ASCE7-16_PPT_2021.pdf | ground elevation slides | S |
| T.L. Smith, A revised approach to wind load calculations, Professional Roofing, May 2023 | https://www.professionalroofing.net/Articles/A-revised-approach-to-wind-load-calculations--05-01-2023/5225 | Kz and Kd paragraphs (fetch tool digest) | S |
| Florida Building Commission, Wind Loads - Impacts from ASCE 7-22 (June 2024) | https://www.floridabuilding.org/fbc/thecode/2023_Code_Development/2023_Code_Resources/ASCE-7-22_Wind_Loads_Fact_Sheet.pdf | pages 1-2 | S |
| ENERCALC, Live Load Reduction Verification Example V1 2026 | https://assets.enercalc.com/uploads/2026/03/04170504/Live-Load-Reduction-Verification-Example-V1-2026.pdf | both problems | S |
| Trimble, Tekla Structural Designer 2025, ASCE 7 live and roof live loads | https://help.trimble.com/doc/tekla-structural-designer/2025/asce7_live_and_roof_live_loads | page (fetch tool digest) | S |
| SkyCiv, ASCE 7-22 wind load calculations | https://skyciv.com/docs/load-generator/wind/asce-7-22-wind-load-calculations/ | page (fetch tool digest) | S |
| Bentley RAM Structural System help, Eurocode eccentric load cases | https://docs.bentley.com/LiveContent/web/RAM%20Structural%20System%20Help%20Complete-v5/en/GUID-476E0247-79A3-4084-95AE-B21259265387.html | page (digest) | S |
| ASCE Hazard Tool, API page; Terms; API documentation PDF | https://www.asce.org/publications-and-news/asce-hazard-tool/api ; .../terms ; https://www.asce.org/-/media/asce-images-and-files/publications-and-news/hazard-tool/hazard-tool-api-documentation.pdf | key, pricing, sample output; terms text; wind section | P |
| ASCE Hazard Tool web app code | https://ascehazardtool.org/app/js/config/config.js, /app/js/standards.config.js, /app/js/stores/queries/wind.js, /app/js/utils/windUtil.js, /app/js/utils/Utilities.js | wind services, RC to MRI, rounding, conversion | P |
| ASCE ArcGIS REST services | https://gis.asce.org/arcgis/rest/services/ASCE722?f=json and the identify calls in 4.3 | service list, answers, headers | P (as tested) |
| ATC Hazards by Location | https://hazards.atcouncil.org/ | closure notice | P |
| USGS building codes web service | https://earthquake.usgs.gov/ws/designmaps/asce7-22.json | response and headers | P |
| EN 1991-1-4:2005+A1:2010 (public.resource copy hosted by ULB) | https://structuraldynamics.ulb.be/DOS/en.1991.1.4.2005.pdf | 4.3.2, Table 4.1, 4.4, 4.5, 6.2, 7.1.2, 7.2.2, Table 7.1 | P |
| DS/EN 1991-1-1 DK NA:2013 | https://www.ds.dk/media/mv5dsp34/ds-en-1991-1-1-dk-na-2013-english.pdf | Table 6.2, 6.3.1.2(10), (11) | P (Denmark) |
| Oasis Engineering, ASCE-7-22 Door/Window Wind Pressure Calculator (MIT) | https://raw.githubusercontent.com/oasiseng/ASCE-7-22-Door-Window-Wind-Pressure-Calculator/HEAD/index.html | constants block, computeKz, Ke | P (its code) |
| ibuilder/massing, services/api/src/aec_api/loads.py (MIT) | https://raw.githubusercontent.com/ibuilder/massing/HEAD/services/api/src/aec_api/loads.py | whole file | P (its code) |
| clay-good/anvilate, src/anvilate/analysis/building_loads.py (MIT) | https://raw.githubusercontent.com/clay-good/anvilate/HEAD/src/anvilate/analysis/building_loads.py | wind and LLR functions | P (its code) |
| Pointers only (search summaries, not sources) | GAF and Carlisle blogs, Dlubal, Engineers Edge, eng-tips, scribd copies, Penn State theses | | U |

## After the independent check (2026-11-21)

`independent-check.md` re-read the sources behind W1 to W7 and L1, L2. Changes to this note:

- **Exposure D (H7 reversed).** Ghosh's deck, slide 145, prints the ASCE 7-22 Exposure D column, and it
  equals the 7-22 formula to rounding in all 22 rows (1.04 at 0 to 15 ft, 1.44 at 100 ft, 1.90 at 500 ft).
  The ICC deck's D column is the unchanged 7-16 one. So the formula and the 7-22 table agree; owner
  decision 2 above is no longer needed.
- **Ke's formula is U** (one copy, the Oasis code, plus a fit to a 7-16 table; SPRI's slide says Ke comes
  from "interpolation or another formula"). The code does not use it: Ke = 1.0, always permitted, or the
  user's value.
- **Counter-evidence recorded:** SPRI's 2023 slide still writes the 7-22 q_z with Kd inside it. The
  pressure p is the same either way; the code follows the 7-22 placement.
