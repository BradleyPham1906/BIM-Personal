# V174 research: page sizes and map surround elements (research agent 2)

Part of the V174 research ("Presentation P1: boards"). This working note covers one side of the phase: the
page gallery (ISO, ANSI and Architectural sizes, portrait and landscape, with their frames and title blocks)
and the elements that surround a map frame (the frame itself, a live legend, a north arrow and a scale bar).
It follows `docs/research/research-protocol.md`, "Research as a scientist does it". No code under `src/` was
changed. Downloaded files were kept in the session scratchpad (`dl-map/`), outside the repository, read as
text only; none was run. Open-source code (QGIS, GPL-2.0-or-later) was read as text; what is taken from it
is the method, credited, never its code.

Date: 2026-11-08. Levels: **P** read in the primary source itself (the standard's text, a vendor's own
manual, the code read as text, or measured here); **S** a dependable secondary source, with the gap said;
**U** a search summary or a single weak copy, to confirm, never used by code. Confidence: high, medium,
low, with the reason.

Experiments (our own ES5, Node 22.23.4, each run once, deterministic):

- `docs/research/experiments/v174-pages/pages.js` (output `pages-out.txt`): ISO 216 computed from its rule
  under three rounding rules and compared with the published table; the inch series converted and compared
  with QGIS and with the app.
- `docs/research/experiments/v174-scalebar/scalebar.js` (output `scalebar-out.txt`): a 1-2-5 scale-bar
  chooser against QGIS's "Fit segment width" method re-stated from the reading, 240 cases.
- `docs/research/experiments/v174-scalebar/convergence.js` (output `convergence-out.txt`): UTM grid
  convergence three ways (spherical formula, Krueger's series as Karney gives it, QGIS's finite difference).

## 1. Abstract

Question: what page sizes should New Layout's gallery offer, with what frame and title block, and how
must a map frame's legend, north arrow and scale bar follow the map so they stay true? Answer: the ISO A
and B sizes are a published table (ISO 216:2007) that the "nice" rule does not reproduce by plain rounding:
it is reproduced exactly by halving the rounded size before and rounding down, so the app should store the
table, not compute it. ANSI A to E (ASME Y14.1-2020) and Architectural A to E1 are exact inch sizes; the
app's existing "ANSI D (24x36 in)" is in fact Arch D and must be renamed. ISO 5457 fixes the frame (20 mm
left, 10 mm elsewhere, A0 to A3 landscape only, A4 portrait only, title block bottom right) and ISO 7200 the
title block's fields (180 mm wide; seven mandatory fields). In both professional tools the legend, north
arrow and scale bar are bound to one map frame and redraw from it; a legend follows the visible layers (and
optionally only what is inside the extent), the north arrow adds the frame's rotation to the map's and,
for true north on a projected map, the convergence at the frame's centre; a scale bar picks a round
division length. QGIS's "nice" lengths use any leading digit (3, 4, 6, 7, 9 appear in half the cases);
a 1-2-5 ladder, as the app's two board scale bars already use, is the recommendation. The app's model is a
local plane turned by one True North angle, not a projected grid, so its north arrow needs no convergence
unless a frame is drawn in UTM.

## 2. The question and the hypotheses

Question: which sizes, frames and fields the gallery offers, and which rules the map surrounds follow, as
data with editions (V167's registry) and as behaviour the code can test.

| # | Hypothesis (falsifiable) | Outcome | Evidence |
|---|---|---|---|
| H1 | ISO 216's sizes are the exact rule (A0 area 1 m^2, ratio sqrt 2) rounded to the nearest millimetre | **Falsified.** Plain rounding gets 6 of 11 A sizes and 6 of 11 B sizes wrong. Halving the rounded size before and rounding down reproduces all 22. The standard's text gives the table, not a rounding rule | e01; ISO 216:2007 clauses 4.3, 6.1, 6.2 (P) |
| H2 | ASME Y14.1 defines both the ANSI series and the Architectural series | **Not settled (U).** ANSI A to E are in it (two secondary sources agree). That ARCH sizes are "defined in the same standard" is said only by Wikipedia, citing sizes.com; the standard is sold and not read | 3.2 |
| H3 | The app's existing sheet sizes match their names | **Falsified.** `ANSI-D` and `ANSI-D-L` are 24 x 36 in, which is Arch D; ANSI D is 22 x 34 in | e01; `sheets.js` 41, 44 |
| H4 | QGIS's fitted scale bar uses 1-2-5 numbers | **Falsified.** Its nice number is any single significant digit times a power of ten; in 240 cases 126 segment lengths had a leading digit other than 1, 2 or 5 (3, 4, 6, 7, 9) | e02; `qgslayoututils.cpp` (P) |
| H5 | A north arrow on the app's plan needs grid convergence | **Falsified for the plan as the app stores it.** The model is a local plane turned by `A3D.site.trueNorth`, converted to latitude and longitude with the ellipsoid's radii (no projection), so true north is one angle. Convergence enters only for a frame drawn in a projected grid (UTM, as the CityJSON export writes) | `map-tiles.js` 52-74; `cityjson.js` 24-42; e03 |
| H6 | Both tools' legends show only the layers visible in the map, by default | **Held for ArcGIS Pro** (Layer visibility sync on by default). **Mixed for QGIS:** the item's member defaults to all project layers, but QGIS 4's setting for new legends defaults to visible layers | 3.6 |
| H7 | One convergence value per map frame is enough for a site board | **Held.** At Philadelphia the convergence changes 27 arcsec across 1 km; both tools compute it once, at the frame's centre | e03; ArcGIS north arrow page; `qgslayoutnortharrowhandler.cpp` |

## 3. Method

### 3.1 Search log

| # | Where | Query or address | What came back | Kept / set aside |
|---|---|---|---|---|
| 1 | app code | `grep -rn "ARCH\|A1\|Letter\|Tabloid\|ANSI" src/js/engine/sheets/ src/js/engine/standards/` | `SHEET_SIZES` in `sheets.js` 34-49; no paper size in the registry | Kept (P) |
| 2 | app code | `grep -rni "truenorth\|north\|utm\|mercator"` | `bimTrueNorthDeg`, `bimSetTrueNorth`, `bimModelToGeo`, `bimUtmFwd`, two board north arrows and scale bars | Kept (P) |
| 3 | raw.githubusercontent.com | QGIS master `src/core/layout/qgspagesizeregistry.cpp` | 29 sizes incl. ANSI A-E, Arch A-E3, B0-B6 | Kept (P) |
| 4 | raw.githubusercontent.com | QGIS `qgslayoutitempicture.cpp`, `qgslayoutnortharrowhandler.cpp/.h`, `qgsbearingutils.cpp` | Grid/true north, offset, finite-difference bearing | Kept (P) |
| 5 | raw.githubusercontent.com | QGIS `qgslayoutitemscalebar.cpp`, `qgsscalebarsettings.h/.cpp`, `qgsscalebarrenderer.cpp`, `layout/qgslayoututils.cpp` | Fixed / FitWidth; defaults; calculatePrettySize | Kept (P) |
| 6 | raw.githubusercontent.com | QGIS `qgslayoutitemlegend.cpp/.h`, `qgis.h`, `CMakeLists.txt` | LegendSyncMode (since 4.0), filter by map, defaults; master is 4.3 | Kept (P) |
| 7 | raw.githubusercontent.com | QGIS-Documentation master `print_composer/composer_items/*.rst` | 404 | Moved |
| 8 | curl | docs.qgis.org latest composer_map.html | Redirect page to `print_layout/layout_items/` (3.44) | Pointer |
| 9 | raw.githubusercontent.com | QGIS-Documentation `docs/user_manual/print_layout/layout_items/layout_{map,legend,scale_bar,image}.rst`, `overview_layout.rst` | Manual text | Kept (P). Commit hash not readable (the GitHub API is closed to this session); master on 2026-11-08 |
| 10 | curl | pro.arcgis.com 3.5 `add-a-layout-to-your-project`, `add-and-modify-map-frames`, `customizing-your-map-extent`, `work-with-a-map-on-a-layout`, `north-arrows`, `scale-bars`, `add-a-legend`, `work-with-a-legend`, `work-with-legend-items`, `layout-fitting-strategies` | Manual text | Kept (P) |
| 11 | curl | pro.arcgis.com 3.5 `add-and-modify-layouts`, `legends`, `legend-properties`, `work-with-legends`, `layout-units-and-page-setup`, `map-frames` | 404 (guessed names) | Set aside |
| 12 | WebSearch | ArcGIS Pro New Layout gallery sizes | No list of the gallery's entries; an Esri Ideas post names an "ISO - Landscape" section | Ideas post read (S, thin); the list stays U |
| 13 | WebSearch / curl | ASME Y14.1-2020 | asme.org product page (Y14.1-2020, 40 pages, ISBN 9780791873625); NSAI store (current, 18-12-2020, supersedes 2012) | Kept (P for the edition) |
| 14 | curl | Wikipedia raw wikitext: Paper size, ANSI/ASME Y14.1, ISO 7200, Transverse Mercator projection | Tables, edition history (with a self-contradiction), convergence formula | Kept (S) |
| 15 | curl | Markus Kuhn, "International standard paper sizes" (cl.cam.ac.uk) | Rule, table, tolerances, JIS B | Kept (S) |
| 16 | curl / WebFetch | iso.org standard pages 36631, 29017, 35446 | 403 to both curl and WebFetch | Refused |
| 17 | WebSearch / curl | iTeh previews: ISO 216:2007 (EN), ISO 5457:1999 (FR), ISO 5457:1980 via SIST, ISO 7200:2004; iTeh catalogue pages | Clauses 1-6 of ISO 216 with Tables 1 and 2; ISO 5457 clauses 3-5 with Tables 1 and 2; ISO 7200 front matter; statuses | Kept (P, the standards' own text in ISO's previews, partial) |
| 18 | curl | law.resource.org IS 11665:2009 (identical adoption of ISO 7200:2004) | Full text of Tables 1-3 and the 180 mm title block | Kept (P for the text, through an identical national adoption) |
| 19 | curl | nationalcadstandard.org, csiresources.org NCS page | NCS V6 current, V7 in development (2022 notice); UDS Module 2 "preferred sheet sizes", no values | Kept (P for status); sizes not public |
| 20 | WebSearch / curl | open-exam-prep.com ARE study guide | Right-hand title block strip, ARCH D and E1 as examples | S, weak (a study guide) |
| 21 | curl | wbdg.org VHA National CAD Standard Application Guide (2006) | "Architectural F size (30" x 42")" title block | Kept (P for VA's own usage; a naming conflict) |
| 22 | curl / WebFetch | webarchive.library.unt.edu A/E/C CADD Standard R3.0 | curl: TLS certificate not verifiable through the proxy (not bypassed); WebFetch: 503 | Refused |
| 23 | curl | apps.dtic.mil ADA576185 | 403 | Refused |
| 24 | curl | pubs.usgs.gov Snyder, PP 1395 (397 pages) | Convergence defined, then "not discussed further in this work" (p. 24 of the text) | Kept (P, negative) |
| 25 | curl | geodesy.noaa.gov NOAA Manual NOS NGS 5 (Stem, SPCS 83) | Definition of the convergence angle, sign conventions, TM procedure | Kept (P; its formula pages OCR poorly) |
| 26 | curl | arxiv.org 1002.1417 (Karney 2011) | Eq. (24): gamma = gamma' + gamma'' | Kept (P) |
| 27 | curl | ncei.noaa.gov World Magnetic Model | WMM2025, released 2024-12-17, valid to late 2029, public domain | Kept (P) |
| 28 | curl | jisc.go.jp | 502 | Refused; JIS from two secondary sources |

### 3.2 Sources by kind

- Standards' own text: ISO 216:2007 (preview, clauses 1-6), ISO 5457:1999 (preview, French, clauses 3-5),
  ISO 5457:1980 (preview, through SIST), ISO 7200:2004 (through IS 11665:2009, identical), Karney (2011),
  NOAA Manual NOS NGS 5. Sold and unread: ASME Y14.1-2020, NCS V6 / UDS Module 2, JIS P 0138.
- Vendors' manuals: ArcGIS Pro 3.5 help (ten pages), QGIS user manual (print layout, five pages).
- Open implementations read as text: QGIS master (4.3) layout code, eleven files.
- Practitioners and secondary: Kuhn's page, Wikipedia (four articles' wikitext), the VA guide, an ARE study
  guide, the NSAI and ASME store pages.

### 3.3 Independent check

Not yet done. Before any number below reaches the code, a second reader re-reads the sources behind the
facts in section 11 ("what the code would depend on") and marks each confirmed or not.

## 4. Findings

### 4.1 ISO 216: the A and B series (P, high)

- Edition: ISO 216:2007, second edition (the preview's cover says 2007-09-15; the iTeh catalogue says
  published 2007-08-28), replacing the 1975 first edition; ISO/TC 6; "under periodical review" (stage
  90.20, July 2026). ISO's own page refused this environment (403). (P for the text; S for the status, from
  iTeh's catalogue.)
- The rule (clauses 4.1-4.4): every size halves into two of the next (halving), all sizes are similar
  (similarity), so the sides are in the ratio sqrt 2 : 1; A0's area is 1 m^2, giving x = 0.841 m and
  y = 1.189 m; B sizes are the geometric means of adjacent A sizes. (P)
- The table (Tables 1 and 2), mm: A0 841 x 1189, A1 594 x 841, A2 420 x 594, A3 297 x 420, A4 210 x 297,
  A5 148 x 210, A6 105 x 148, A7 74 x 105, A8 52 x 74, A9 37 x 52, A10 26 x 37; the rarely used 2A0
  1189 x 1682 and 4A0 1682 x 2378. B0 1000 x 1414, B1 707 x 1000, B2 500 x 707, B3 353 x 500, B4 250 x 353,
  B5 176 x 250, B6 125 x 176, B7 88 x 125, B8 62 x 88, B9 44 x 62, B10 31 x 44. (P; QGIS's registry and
  Kuhn agree for every size they list.)
- **No rounding rule is stated** in clauses 1-6. Kuhn says only that the sizes are "a rounded number of
  millimeters". e01 shows the table is what you get by rounding A0 (and B0) to the millimetre, then taking
  each next size as (floor(long/2), short) of the rounded size before; plain rounding of each exact size
  fails at A1 (595, not 594). So the table, not a formula, is the data. (P, measured)
- Tolerances: plus or minus 1.5 mm up to 150 mm, 2 mm from 150 to 600 mm, 3 mm above 600 mm (Kuhn; clause
  7 is beyond the preview). (S, one source; not needed by the code)
- The C series (envelopes) is ISO 269, withdrawn in 2009 (Wikipedia). Not for drawing sheets. (S)

### 4.2 ISO 5457: the drawing sheet, its frame and grid (P, high)

ISO 5457:1999 "Technical product documentation - Sizes and layout of drawing sheets", with Amendment 1:2010;
confirmed (stage 90.93, September 2026). Read in the French preview of the 1999 text; the 1980 first edition
read for comparison.

- Sheets A0 to A4, trimmed (T) sizes equal to ISO 216; drawing space (Table 1, plus or minus 0.5 mm):
  A0 821 x 1159, A1 574 x 811, A2 400 x 564, A3 277 x 390, A4 180 x 277. Untrimmed (U) sheets: A0 880 x 1230,
  A1 625 x 880, A2 450 x 625, A3 330 x 450, A4 240 x 330 (plus or minus 2). (P)
- Margins (4.2): 20 mm on the left edge, frame included, usable as a filing margin; 10 mm on every other
  edge. The frame round the drawing space is a continuous 0.7 mm line. (P) The drawing spaces in Table 1
  follow from this: 841 - 30 = 811, 594 - 20 = 574. (checked by hand)
- Title block (4.1): its size and layout from ISO 7200. For A3 to A0 it sits in the bottom right corner of
  the drawing space, and **only landscape sheets are allowed**; for A4 it sits on the short (bottom) side and
  **only portrait is allowed**. The drawing reads the way the title block reads. The size designation goes at
  the right of the bottom margin. (P)
- The 1980 edition was looser: borders "recommended" at least 20 mm for A0 and A1 and 10 mm for A2 to A4,
  and both landscape (type X) and portrait (type Y) sheets were allowed, with the title block in the bottom
  right either way. (P) The 1999 rule is stricter; this is the edition the registry should name.
- Centring marks (4.3): four, at the ends of the two axes of symmetry, symmetric within 1 mm, recommended as
  0.7 mm lines from the sheet's edge to 10 mm past the frame. (P)
- Grid reference (4.4): fields 50 mm long measured from the centring marks, letters top to bottom (no I or
  O), numbers left to right, on opposite sides (A4: top and right only), 3.5 mm characters, 0.35 mm lines;
  the remainder goes to the fields at the edges. Fields (Table 2), long side x short side: A0 24 x 16,
  A1 16 x 12, A2 12 x 8, A3 8 x 6, A4 6 x 4. (P)
- Elongated sizes (A1.0, A2.0, A3.1 and so on) are in ISO 5457 too (Wikipedia; the preview's Figure 3 is a
  drawing only). (S; not proposed for the gallery)

### 4.3 ISO 7200: the title block's fields (P, high)

ISO 7200:2004, second edition, "Technical product documentation - Data fields in title blocks and document
headers", replacing ISO 7200:1984 ("Technical drawings - Title blocks"); confirmed (stage 90.93, August
2026). Read in full through IS 11665:2009, which the Bureau of Indian Standards adopted as identical.

| Field (subclause) | Mandatory | Recommended characters |
|---|---|---|
| Legal owner (5.1.2) | yes | unspecified |
| Identification number (5.1.3) | yes | 16 |
| Revision index (5.1.4) | no | 2 |
| Date of issue (5.1.5) | yes | 10 |
| Segment/sheet number (5.1.6) | yes | 4 |
| Number of segments/sheets (5.1.7) | no | 4 |
| Language code (5.1.8, ISO 639) | no | 4 per language |
| Title (5.2.2) | yes | 25 (30 for two-byte scripts) |
| Supplementary title (5.2.3) | no | 2 x 25/30 |
| Responsible department, technical reference (5.3.2-3) | no | 10, 20 |
| Approval person (5.3.4) | yes | 20 |
| Creator (5.3.5) | yes | 20 |
| Document type (5.3.6) | yes | 30 |
| Classification/key words, document status, page number, number of pages, paper size (5.3.7-11) | no | unspecified, 20, 4, 4, 4 |

- The title block is 180 mm wide, to fit an A4 sheet with its 20 mm left and 10 mm right margins
  (Figures 1 and 2, compact and with an extra line for names). (P)
- Revision index: A to Z, then AA, AB...; or 1, 2, 3; avoid I and O. (P)
- Scale, projection symbol and the like are not title block fields: they are shown "dynamically", outside
  it, only when used. (P) For a map board this means the scale bar and north arrow are elements, not fields.

### 4.4 ANSI and Architectural sizes (inch series)

- **ASME Y14.1-2020, "Drawing Sheet Size and Format"**, 40 pages, ISBN 9780791873625 (ASME's own product
  page, P); published 2020-12-18, current, supersedes Y14.1-2012 (NSAI's store, P). It consolidated
  Y14.1 (decimal inch) and Y14.1M (metric) (Wikipedia, S). Wikipedia's article also says the standard was
  revised "in 1995, 2005, 2012 and 2022", which contradicts the 2020 consolidation it describes; ASME and
  NSAI both show 2020 as the current edition, so 2020 is taken.
- ANSI sizes, inches (sold standard; two independent secondary sources agree, Wikipedia's Y14.1 table and
  QGIS's registry; the Engineering ToolBox page agrees for D): A 8.5 x 11, B 11 x 17, C 17 x 22, D 22 x 34,
  E 34 x 44; exact millimetres 215.9 x 279.4, 279.4 x 431.8, 431.8 x 558.8, 558.8 x 863.6, 863.6 x 1117.6.
  Each halves into two of the one below (e01), with alternating ratios 1.2941 and 1.5455. (S, high)
  F 28 x 40 and the roll sizes G, H, J, K are in Wikipedia's table only. (S, one source; not proposed)
- Architectural sizes, inches (two secondary sources agree, Wikipedia via sizes.com and QGIS's registry):
  Arch A 9 x 12, B 12 x 18, C 18 x 24, D 24 x 36, E 36 x 48, E1 30 x 42 (E1 is D plus 6 in on each side,
  ratio 1.4). Exact mm: 228.6 x 304.8, 304.8 x 457.2, 457.2 x 609.6, 609.6 x 914.4, 914.4 x 1219.2,
  762 x 1066.8. QGIS also lists E2 26 x 38 and E3 27 x 39, which it stores rounded to whole mm (660 x 965,
  686 x 991, 0.4 mm short of exact). (S, high for A to E1; E2 and E3 low: Wikipedia says only that a
  printing working group's list has them.)
- Which standard defines the Arch sizes is not settled. Wikipedia says ASME Y14.1 does; nothing read here
  confirms it, and the US National CAD Standard calls them its "preferred sheet sizes" (CSI's summary of UDS
  Module 2, P for the wording, no values). (U)
- Naming conflict: the US Department of Veterans Affairs' NCS guide calls 30 x 42 in "Architectural F size"
  (P for VA's usage), where QGIS, Wikipedia and the study guide call it Arch E1. The gallery should label it
  "Arch E1 (30 x 42 in)" and keep "F" as an alias in its search text.

### 4.5 The US National CAD Standard (NCS) sheet and title block

- NCS V6 is the current version; a V7 committee was formed in 2022 (NIBS's site, P). The UDS Module 2
  ("Sheet Organization") gives the drawing area, title block and production reference areas, a coordinate
  location system and preferred sheet sizes (CSI's page, P for the scope). The module's values are sold and
  were not read. (U for the values)
- Title block: a vertical strip along the right edge of the sheet, with the drawing area divided into a
  grid of modules (rows lettered, columns numbered) (one study guide, S weak; its diagram agrees with the
  VA guide's use of one standard title block). (U to S, low)
- So, as ISO puts the title block in the bottom right corner for landscape A0 to A3, US architectural
  practice puts it in a right-hand strip running the sheet's full height. A gallery template per family is
  the consequence.

### 4.6 JIS and other national series (S, medium)

- JIS P 0138: the A series is ISO's (tolerances differ); the B series is not ISO's: JIS B sizes have 1.5 times
  the area of the A size of the same number (B0 1030 x 1456, B4 257 x 364, B5 182 x 257). Two secondary
  sources agree (Kuhn; Wikipedia). jisc.go.jp answered 502. (S)
- So "B4" is ambiguous: ISO 250 x 353, JIS 257 x 364. The gallery offers ISO B by default and, if JIS B is
  added, names it "JIS B4".
- China GB/T 148-1997 adds a D series; India's IS 10711:2001 is identical to ISO 5457 (IS 11665's foreword,
  P). Not proposed for the gallery.

### 4.7 Practice: the page galleries

- **ArcGIS Pro 3.5.** Insert > New Layout opens a gallery: "Choose from ANSI, Architectural, and ISO
  sizes", or a custom size in Layout Properties, or a page from a printer (with an option to draw the
  printer's margins as a dashed outline). The largest layout is 3600 x 3600 in. (P) The gallery's sections
  are split by orientation (an Esri Ideas post names an "ISO - Landscape" section) (S, thin). Which sizes
  each section lists was not found. (U)
- **QGIS 4.3 (master).** The page registry (`qgspagesizeregistry.cpp`) lists A6 to A0, B6 to B0, Legal,
  Letter, ANSI A to E, Arch A, B, C, D, E, E1, E2, E3, and three screen sizes in pixels (1920 x 1080,
  1280 x 800, 1024 x 768), each stored portrait; the manual says each page has an Orientation, Portrait or
  Landscape, and can be custom. (P) The registry has no A7 to A10 and no B7 to B10.
- The app (V116) has eleven entries, mixed portrait and landscape, with "ANSI D" wrong (H3).

### 4.8 Map frames (P, high)

- **ArcGIS Pro.** A map frame is a container that points to a map, a scene or nothing. Data, symbology,
  selection, layer visibility and the coordinate system are shared with every view of that map; the
  **extent is the frame's own**. Shapes: rectangle (default), polygon, lasso, circle, ellipse. A new frame
  has a 1 pt black border and the map's background. North arrows, scale bars and legends are linked to a
  frame and update when its map or extent changes. Constraints: none; fixed extent; fixed centre; fixed
  centre and scale; fixed scale; and, with more frames, linked extent, linked centre, linked centre and
  scale, linked scale (one-way); scenes take none. Navigation happens only after "Activate". (P)
- **QGIS.** The map item shows the canvas's extent and layers; it has its own Scale and Map rotation
  (clockwise degrees) and CRS; "Lock layers" freezes which layers it shows (and "Lock styles"); "Follow map
  theme" ties it to a saved theme. (P)
- Consequence for a board: a map frame stores its own centre, scale (or a "fit" mode, as the app's
  viewports already have), rotation and which layers it shows (live, or locked to a saved set); the
  surrounds read those, never the main view.

### 4.9 Legends (P, high)

- **ArcGIS Pro.** One legend references one map frame. Synchronise with map (Options tab): **Layer
  visibility** (only visible layers; on by default), **Layer order** (items follow drawing order, no manual
  reorder; off), **New layer** (a new map layer becomes an item; on), **Reference scale** (on). Per item,
  "Only show features visible in the map extent" makes it dynamic: only the classes present in the extent
  are listed, and an item with no features in the extent disappears; not available for vector tiles,
  clustered layers or colour-ramp symbology (unclassed colours). Optional feature counts. "Display only when
  populated" hides the whole legend when it has no items (otherwise title, border and background draw).
  Fitting strategies: adjust font size, adjust columns, adjust frame, adjust columns and font size, manual
  columns; with a minimum font size; an item that does not fit is dropped whole, and an overflow mark shows.
  Removing a layer from the map removes its item automatically. Convert to graphics breaks the link. (P)
- **QGIS 4.** Sync modes (since 4.0): All project layers (including unchecked ones), Visible layers (the
  checked spatial layers, "regardless of whether they are visible within the linked map's extent"), Manual
  (edit the tree; Reset to all or to visible). In the code, `layersToRender` of the linked map is used for
  Visible layers, so a map frame with locked layers lists its own set. "Only show items inside linked maps"
  filters classes by the frames' visible extent polygon (works in every mode; default off); an atlas filter;
  a filter by expression. Defaults in the code: one column, resize to contents on, filter by map off; the
  item's member starts as All project layers, while the setting `default-legend-sync-mode` defaults to
  Visible layers (where the interface applies it was not traced). Before 4.0, "Auto update" was the switch
  (`setAutoUpdateModel` maps it to All project layers or Manual). (P)
- **What a live legend must follow**, from both: (1) the frame's map and which layers that frame renders
  (its own locked set if it has one), (2) each layer's visibility, (3) its symbology classes and labels
  (the V173 classes the app already lists under each layer, `bimDataLegendHtml`), (4) optionally the
  frame's extent (rotated: QGIS uses the visible extent polygon, not the bounding box), (5) the layer order,
  optionally. And it must say what it does when nothing is left (hide, or a stated empty state).

### 4.10 North arrows (P, high)

- **Three norths.** True (geodetic) north is the direction of the meridian; grid north is the direction of
  the grid's north lines, parallel to the central meridian; magnetic north is where a compass points, which
  differs from true north by the declination of the place and date. (NGS 5 section 2.4, P; QGIS manual, P;
  ArcGIS north arrow page, P)
- **Convergence** (the angle between true and grid north) is zero on the central meridian and on the
  equator, grows toward the zone's edge and the poles. Snyder (USGS PP 1395) defines it and then states it
  "is not discussed further in this work" (P, negative). Karney (2011) eq. (24), after Krueger (1912):
  gamma = gamma' + gamma'', gamma' = atan(tau'/sqrt(1 + tau'^2) tan lambda), gamma'' = atan(q'/p'), the
  bearing of grid north measured clockwise from true north (P). On the sphere, gamma = atan(tan lambda
  sin phi) (Wikipedia, S). NGS 5 warns that convergence is not the difference between geodetic and grid
  azimuths (the arc-to-chord term) and that its sign convention changed between SPCS 27 and SPCS 83 (P).
- **ArcGIS Pro.** A north arrow is associated with one map frame (the last selected) and rotates with the
  map. Type: **Map North** (the map's rotation), **True North** (geodetic north computed by the map's
  coordinate system at the centre of the frame), **Magnetic North** (World Magnetic Model). A **Calibration
  Angle** adjusts it by hand: positive values rotate counterclockwise, negative clockwise (for declination);
  a read-only Calculated Angle shows the result. A visible scale range is optional. (P)
- **QGIS.** A picture item with "Sync with map": arrow rotation = the map's content rotation + the map item's
  own rotation; North alignment **Grid north** (the default, enum 0) adds nothing, **True north** adds the
  bearing of true north at the extent's centre, found numerically by moving the centre 0.000001 degree north
  in geographic coordinates and taking the azimuth back in the map's CRS (`QgsBearingUtils`); then an
  **Offset** is added (for declination), recomputed on map rotation, item rotation or extent change. (P)
  Note the sign: QGIS's offset adds clockwise, ArcGIS's calibration angle is counterclockwise-positive.
- **Magnetic model.** WMM2025 (NGA and DGC, with NCEI and BGS) was released 2024-12-17 and is valid to late
  2029; its code is public domain. (P) A magnetic arrow is out of V174's scope unless the owner asks; a
  declination offset typed by the user covers it.
- **The app.** True North is one angle in degrees, clockwise from the plan's up to true north
  (`A3D.site.trueNorth`, set in the True North dialog, kept in -180 to 180) (`survey-arithmetic.js` 5-8,
  `alignment-profile.js` 650-746). `bimModelToGeo` (map-tiles.js 57-64) turns a plan point into longitude
  and latitude with the meridian and prime vertical radii at the site, after rotating by that angle: a
  local tangent plane, not a projected grid. True north is therefore the same direction everywhere on the
  plan, and there is no grid north. Two boards already draw a north arrow from it (`zoning-envelope.js` 778,
  `access-board.js` 76). The CityJSON export alone writes UTM (`cityjson.js`, Krueger's third order series).
- **e03** (section 6.3): convergence at Philadelphia (zone 18) is -0.105 degrees; at a zone's edge 1.93
  (40 N) to 2.95 degrees (80 N). The spherical formula with geodetic latitude stays within 0.05 arcsec of
  the ellipsoidal value in every case; QGIS's finite difference within 0.001 arcsec. Across 1 km east-west
  it changes by 27 arcsec.

### 4.11 Scale bars (P, high)

- **ArcGIS Pro.** Bound to a map frame and updated when its scale changes. Map scales "are often averages";
  by default the scale shown is the one at the equator, with **Compute at center** to measure at the frame's
  centre. Parts: map units and label text, divisions, subdivisions (subdivision value = division value /
  subdivisions), numbers (frequency, position, rounding, thousands separators), marks (division, subdivision,
  midpoint), bar. **Fitting strategies (five):** Adjust division value (keeps the number of divisions, keeps
  the width by changing the value); Adjust number of divisions (keeps the value); Adjust divisions and
  division value (divisions first, then the value); Adjust width (keeps value and number, the bar's width
  changes; no manual resize); Fixed bar width (a set width in page units; values follow). Convert to graphics
  breaks the link. A visible scale range is optional; dual scale bars exist. (P) How Pro rounds a division
  value is not documented. (U)
- **QGIS.** Styles: single box, double box, line ticks (middle, up, down), stepped line, hollow, numeric.
  Units: map units, metres, feet, miles, nautical miles and others, with a label multiplier and label.
  Segment size mode: **Fixed** (units per segment, the default mode) or **Fit segment width** (the total
  bar kept between a minimum and maximum width in mm, default 50 and 150). Defaults in the settings: 2
  segments right, 0 left, 1 subdivision, bar height 3 mm. The scale is measured across the extent (top,
  middle, bottom, average, or at the equator for degree systems) with the project's ellipsoid. (P)
- **QGIS's "nice" length (P, read as text).** In fit mode it takes the units per segment that would give
  the minimum and maximum widths and calls `calculatePrettySize(min, max)`: `nextNice(a, d)` rounds a up to a
  multiple of 10^floor(log10 a)/d, `prevNice` rounds down; starting at d = 1 it multiplies d by 10 until one
  of the two falls inside [min, max], then takes the larger that fits. So the result is any digit times a
  power of ten (and finer when d grows), not a 1-2-5 number. Units: when first added, metres switch to km
  when a tenth of the map width exceeds 1000 m, feet to miles above 5419.95 ft; the first segment is a tenth
  of the map width, rounded by a rule that gives 0.75, 2.5, 7.5 and similar.
- **The app already** has two fixed ladders: the zoning board's 1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000
  m within a quarter of the figure (`zoning-envelope.js` 607-613) and the access board's 25 to 5000 m within
  a fifth (`access-board.js` 66-73). Both stop at a fixed end, have no feet, and the zoning one shows a
  single label; neither has a minimum.

## 5. The alternatives compared

### 5.1 How the gallery's sizes are held

Criteria, stated first: exact to the standard; editions recorded (V167's rule); orientation by choice;
works offline; no rounding drift.

| Option | Exact | Editions | Orientation | Cost | Breaks |
|---|---|---|---|---|---|
| A. Compute ISO from the rule | No: plain rounding gets 12 of 22 wrong (e01); the floor-halving rule is right but undocumented | Weak: the rule is not the standard's text | Free | Small | Trust, if the rule is wrong for a size not tested |
| B. A table per standard, in the registry, each size stored once (short x long) and turned by an orientation flag | Yes | Yes (ISO 216:2007, ISO 5457:1999+A1:2010, ASME Y14.1-2020, ISO 7200:2004) | Free | A registry record each | Nothing; the V116 keys are mapped |
| C. Keep `SHEET_SIZES` as it is, add keys | As typed | No | Duplicated (`-L` keys) | Least | Keeps "ANSI D" wrong |

**Recommendation: B.** Inch sizes are stored in inches and converted exactly (x 25.4) so 22 x 34 in is
558.8 x 863.6 mm, never a rounded number; ISO sizes as the table. The old keys stay readable: `ANSI-D` and
`ANSI-D-L` become Arch D (portrait and landscape) under their true name, and the sheets already made with
them keep their size. What would change it: the owner preferring the computed form for its brevity.

### 5.2 The scale bar's nice number

Criteria: readable round numbers; inside a stated width range at every scale from 1:1 to 1:50,000,000;
metres and feet; one rule for every board.

| Option | Numbers | Fits the range (e02) | Units | Notes |
|---|---|---|---|---|
| A. QGIS's prettySize | Any digit x 10^k (126 of 240 not 1-2-5: 3, 4, 6, 7, 9) | 240 of 240 | Any; label multiplier | Widest bar in range; "7 m" and "90 m" segments are hard to read and to halve |
| B. 1-2-5 ladder, largest in range (ours) | 1, 2, 5 x 10^k | 240 of 240 | m to km at 1000 m; ft to mi at a quarter mile | Agrees with QGIS in 78 of 240 (where QGIS's digit is 1, 2 or 5 and the larger fits) |
| C. A fixed list (the app today) | Fixed | Fails past its ends (1:1, 1:50,000,000) | m only | No minimum width |
| D. ArcGIS's strategies | Not documented | n/a | Any | Gives the user the choice of what stays fixed |

**Recommendation: B as the default, with ArcGIS's choice of what stays fixed** (division value, number of
divisions, or width) as the element's fitting option; 2 divisions by default (as QGIS), the bar between
about 15 % and 40 % of the frame's width, labels in m or km, ft or mi by the project's unit. Adding 2.5
(1, 2, 2.5, 5) would match the app's zoning ladder (25 m) and is an owner's choice.

## 6. The experiments

### 6.1 e01: ISO 216 from its rule, and the inch series

Environment: Node 22.23.4 on Linux; one run (deterministic). Raw output in `v174-pages/pages-out.txt`.

- R1 (round each exact size): A wrong at A1 595 x 841, A2 420 x 595, A5 149 x 210, A6 105 x 149, A8 53 x 74,
  A9 37 x 53; B wrong at B3, B4, B5, B6, B8, B9 (each 1 mm long).
- R2 (round A0 and B0, then each next = floor(long/2) x short of the rounded size before): **all 11 A and
  all 11 B match** the published tables.
- R3 (the same, halving rounded to the nearest): 10 A and 8 B wrong.
- Exact A0 840.896 x 1189.207 mm, area 1.000000000 m^2; exact B0 1000.000 x 1414.214 mm. The table's
  worst departure from exact: 0.651 mm (A), 0.777 mm (B). The table's long/short ratios run from 1.4054
  (A9) to 1.4231 (A8, A10), so the small sizes are not quite sqrt 2.
- Inch series: every ANSI and Arch A to E1 size, converted exactly, equals QGIS's registry; Arch E2 and E3
  differ by 0.40 mm (QGIS rounds them). ANSI and Arch both halve exactly at every step.
- The app: ANSI-A and ANSI-B match; **ANSI-D (609.6 x 914.4 mm) is Arch D, not ANSI D**.

### 6.2 e02: scale bars, ours against QGIS's fit

240 cases: metres and feet; 20 scales from 1:1 to 1:5,000,000; frame widths 60 to 800 mm; bar 50 to 150 mm
(QGIS's defaults), 2 segments. Raw output in `v174-scalebar/scalebar-out.txt`.

- Ours: a 1-2-5 bar inside the range in 240 of 240. QGIS fit: inside in 240 of 240, but leading digits
  {1: 78, 2: 36, 3: 42, 4: 18, 6: 24, 7: 36, 9: 6}: 126 of 240 are not 1, 2 or 5.
- Examples at 1:100: ours 5 m x 2 = 100 mm, QGIS 7 m x 2 = 140 mm; at 1:1250: ours 50 m (80 mm), QGIS 90 m
  (144 mm); in feet at 1:25,000: ours 1 mi x 2 (128.7 mm), QGIS 6000 ft (146.3 mm).
- With a fixed width range the bar does not depend on the frame's width, only on the scale (both methods).
- QGIS's default on insert gives a leading digit 1, 2 or 5 in 129 of 240 (others 7.5, 2.5, 0.75).
- Our re-statement of QGIS's nextNice and prevNice reproduces the examples in its source comment exactly
  (4573.23 -> 5000, 4600, 4580, 4574 and 4000, 4500, 4570, 4573), a check on the reading.
- Edges: 1:1 in a 60 mm frame gives 0.01 m x 2 = 20 mm; 1:50,000,000 gives 500 km x 2 = 20 mm; 1:1200
  (1 in = 100 ft) gives 200 ft x 2 = 101.6 mm; 1:63,360 (1 in = 1 mi) gives 2 mi x 2 = 101.6 mm; QGIS with
  minimum above maximum returns 0 (no bar).

### 6.3 e03: grid convergence

Raw output in `v174-scalebar/convergence-out.txt`. Degrees; differences in arcsec.

| Case | Spherical | Karney/Krueger | Finite difference | (b)-(c) | (a)-(b) |
|---|---|---|---|---|---|
| Philadelphia City Hall, zone 18 | -0.105057 | -0.105057 | -0.105056 | -0.001 | 0.000 |
| 39.95 N, 1 degree east of the CM | 0.642192 | 0.642192 | 0.642193 | 0.000 | -0.002 |
| 40 N, zone edge | 1.929397 | 1.929410 | 1.929410 | -0.001 | -0.044 |
| 60 N, zone edge | 2.598670 | 2.598673 | 2.598673 | 0.000 | -0.011 |
| Equator, 3 degrees off | 0 | 0 | 0 | 0 | 0 |
| 60 N on the CM | 0 | 0 | 0 | 0 | 0 |
| 80 N, 3 degrees off | 2.954505 | 2.954505 | 2.954505 | 0.001 | 0.000 |
| 33.9 S, 2 degrees east | -1.115802 | -1.115807 | -1.115807 | 0.000 | 0.016 |

All three agree within 0.05 arcsec; for a north arrow (drawn to a fraction of a degree) the spherical
formula is enough, and the app's own Krueger series gives the exact value if wanted.

## 7. Edges

- **A rotated map frame.** Arrow angle = frame (element) rotation + map rotation inside the frame + (for
  true north on a projected map) convergence at the centre + a user offset, as QGIS sums them. In the app,
  the map rotation of a plan frame is the view's rotation relative to plan up, and true north is
  `trueNorth` from plan up, so a plan frame's arrow = frame rotation + view rotation + trueNorth (clockwise,
  screen y down, as the zoning board draws it). The legend's extent filter uses the rotated frame's polygon,
  not its bounding box (QGIS's `visibleExtentPolygon`).
- **Sign conventions.** ArcGIS's calibration angle is counterclockwise-positive, QGIS's offset is
  clockwise-positive, the app's True North is clockwise from plan up; NGS changed the convergence sign
  between SPCS 27 and 83. One convention, stated in the element's label, and a test at +30 degrees.
- **Very small and very large scales.** 1:1 to 1:50,000,000 all give a bar in range with the ladder (e02).
  A frame narrower than the minimum bar width (20 mm at 1:500 gave 5 m x 2 = 20 mm only because the
  defaults scale with the frame) must shrink the bar or drop to one division, not overflow.
- **Unit switching.** m to km at 1000 m; ft to mi: QGIS at 5419.95 ft per initial segment; ours at a quarter
  mile of bar. The label unit and the division value change together, and a division in miles is a 1-2-5
  number of miles, not of feet (1 mi, not 5280 ft).
- **A legend with no visible layers.** ArcGIS: "Display only when populated" hides it, otherwise title and
  frame draw empty. QGIS: not documented (U). The app should hide the items and show a one-line note on the
  board while editing ("No visible layers in Map 1"), and draw nothing in output.
- **A legend item with classes outside the extent.** ArcGIS drops the classes, and the whole item when none
  is in the extent; colour-ramp (unclassed) layers are exempt.
- **Overflow.** ArcGIS drops a whole item that does not fit and marks the overflow; silently clipping is not
  acceptable.
- **Portrait and landscape title blocks.** ISO 5457:1999 allows A0 to A3 only landscape and A4 only
  portrait, title block bottom right (A4: along the bottom). A portrait A1 is outside ISO 5457 (allowed in
  1980); the gallery can offer it (QGIS and ArcGIS do) but its ISO frame template is then "not to ISO 5457",
  said. US architectural sheets use a right-hand vertical strip in either orientation.
- **"B4" and "E" are ambiguous**: ISO B4 vs JIS B4; ANSI E (34 x 44) vs Arch E (36 x 48) vs Arch E1 / VA's
  "F" (30 x 42).
- **Rounded inch sizes.** Arch E2 and E3 rounded to mm in QGIS (0.4 mm short); store inches.
- **The equator scale.** ArcGIS's default scale bar measures at the equator for a map in a projection whose
  scale varies; on a Web Mercator map at 40 N that is off by 1/cos 40 = 1.305. The app's plan is local
  metres, so its scale is the same everywhere; a frame showing a basemap in Web Mercator must measure at
  the site, not at the equator.
- **Untrimmed and printer margins.** ISO's U sizes and ArcGIS's printer margins: the board is the trimmed
  page; a printer's margin is a print setting, not a page size.

## 8. What the app already has

- `src/js/engine/sheets/sheets.js` 34-49: `SHEET_SIZES` (eleven keys, ANSI-D wrong), `SHEET_NEW_SIZE`
  `'ANSI-B-L'`; 54-59 `SHEET_SCALES` 1:1 to 1:5000; 63-68 `bimNewSheet` copies w and h onto the sheet.
- `src/js/engine/sheets/viewports.js` 46-90, 372-416: a viewport's scale (standard scales or "fit"), pan and
  fit, the model of a map frame's scale and centre.
- `src/js/engine/survey/survey-arithmetic.js` 5-8: `bimTrueNorthDeg`; `src/js/engine/site/alignment-profile.js`
  650-746: `bimSetTrueNorth` (one undo step, -180 to 180) and its dialog.
- `src/js/engine/map/map-tiles.js` 47-74: `bimMapOrigin`, `bimGeoRadii`, `bimModelToGeo`, `bimGeoToModel`
  (local tangent plane); 75-84 Web Mercator tile maths.
- `src/js/engine/map/cityjson.js` 24-50: UTM zone, Krueger's third order forward and inverse (could give
  gamma via p' and q' if a UTM frame is ever wanted).
- `src/js/engine/site-analysis/zoning-envelope.js` 607-613 (scale bar ladder) and 778-780 (north arrow from
  trueNorth); `src/js/engine/site-analysis/access-board.js` 66-76 (scale bar ladder, fixed north arrow).
- `src/js/engine/map/data-symbology.js` 116-131: `bimDataLegendHtml` and `bimDataLegendTitle`, the classes
  under a data layer (at most `BIM_LENS_MAX_ROWS`, "and N more"): the rows a map legend would draw.
- `src/js/engine/standards/registry.js`: records `{id,title,pub,kind,area,use,eds:[{id,name,pub,st,where,
  adopt,src:{t,w,u,lv,read},v:[{n,v,u,say}]}]}`; no paper sizes yet.

## 9. Risks and threats to validity

- ASME Y14.1, UDS Module 2 and JIS P 0138 were not read: their values rest on secondary sources (two
  agreeing for ANSI and Arch A to E1, two for JIS B; one weak for the NCS title block).
- ISO 5457 was read in the French preview; the English text and Amendment 1:2010 were not read. What the
  amendment changed is unknown (U); the iTeh catalogue lists it, its content was not in the preview.
- QGIS was read on master (4.3, 2026-11-08); a released 3.x behaves differently for legends (no sync modes).
  ArcGIS Pro was read in 3.5's help; 3.6 and 3.7 were not compared page by page.
- Our QGIS scale-bar re-statement could differ from QGIS in a corner (floating point at exact powers of ten);
  the source comment's examples match, which lowers the risk.
- e03 tested 8 points; the app's model plane being a tangent plane means its "true north" drifts from the
  meridian by roughly (distance east / Earth's radius) x tan(latitude): about 0.008 degrees per km at 40 N
  (worked out, not measured; U). Negligible for a site board.

## 10. What is still open (U)

- Which sizes ArcGIS Pro's New Layout gallery lists in each section (the help names the families only).
- Whether ASME Y14.1-2020 defines the Arch sizes; the NCS V6 (UDS Module 2) sheet sizes and title block
  dimensions (sold; nationalcadstandard.org gives no values; the A/E/C CADD Standard copy refused, TLS and
  503; dtic.mil 403).
- ISO 5457 Amendment 1:2010's content; ISO 216's clause 7 tolerances (one secondary source).
- How ArcGIS Pro rounds a scale bar's division value; what QGIS draws for an empty legend; where QGIS applies
  its default legend sync setting.
- Hosts refused on 2026-11-08: iso.org (403, curl and WebFetch), webstore.ansi.org (403), apps.dtic.mil
  (403), webarchive.library.unt.edu (TLS not verifiable through the proxy; WebFetch 503), jisc.go.jp (502).

## 11. What the code would depend on (for the second reader)

| Fact | Value | Level |
|---|---|---|
| ISO A0..A10, B0..B10 | the tables in 4.1 | P (ISO 216:2007 Tables 1, 2) |
| ISO 5457 margins, frame, title block position, orientation | 20 mm left, 10 mm others; 0.7 mm frame; bottom right; A0-A3 landscape only, A4 portrait only | P (ISO 5457:1999 4.1, 4.2) |
| ISO 5457 drawing spaces and grid fields | Table 1 and Table 2 in 4.2; fields 50 mm | P |
| ISO 7200 fields | Tables 1-3 in 4.3; 180 mm wide | P (via IS 11665:2009, identical) |
| ANSI A-E | 8.5x11, 11x17, 17x22, 22x34, 34x44 in | S (two agree; ASME Y14.1-2020 sold) |
| Arch A-E, E1 | 9x12, 12x18, 18x24, 24x36, 36x48, 30x42 in | S (two agree) |
| JIS B (if offered) | B0 1030x1456 ... B4 257x364, B5 182x257 | S (two agree) |
| Convergence | gamma = atan(tan dlon sin lat) (sphere); Karney eq. 24 exact; at the frame's centre | P (Karney); S (sphere); measured e03 |
| North arrow composition | frame rotation + map rotation + true-north correction + offset | P (QGIS code; ArcGIS help) |
| Legend sync | visible layers on, new layers on, order off by default (ArcGIS); extent filter optional | P |
| Scale bar ladder | 1-2-5 x 10^k, largest within [min, max]; m/km at 1000 m; ft/mi | ours, measured e02 |

## 12. The owner's decisions (to be asked together with the other researchers' questions)

1. Hold page sizes as registry records with editions (5.1 option B), and rename the app's "ANSI D" sizes to
   Arch D? (Recommended: yes.)
2. Which families in the gallery: ISO A0-A4 (plus A5?), ISO B, ANSI A-E, Arch A-E1; JIS B too? (Recommended:
   ISO A0-A4, ANSI A-E, Arch A-E1; ISO B on request; JIS B not.)
3. Title block templates: an ISO 5457/7200 one (bottom right, 180 mm) and a US right-hand strip one, chosen
   by family? And a portrait A0-A3 allowed but marked "not to ISO 5457"? (Recommended: yes and yes.)
4. Scale bar numbers: 1-2-5, or 1-2-2.5-5 to match the zoning board's 25 m? (Recommended: 1-2-5.)
5. North arrow modes: plan north (the view) and true north (trueNorth), with a typed offset for magnetic
   declination; no WMM in V174? (Recommended: yes.)
6. Legend defaults: follow visible layers and new layers, layer order on, extent filter off, hide when
   empty? (Recommended: as ArcGIS, but layer order on, because the app's Layers tab already orders them.)

## 13. References

| What | URL | Read | Date | Level |
|---|---|---|---|---|
| ISO 216:2007 preview (EN) | https://cdn.standards.iteh.ai/samples/36631/c0883203ea25445c9992bb09343620c5/ISO-216-2007.pdf | clauses 1-6, Tables 1, 2 | 2026-11-08 | P |
| ISO 216:2007 catalogue (iTeh) | https://standards.iteh.ai/catalog/standards/iso/9dd0b580-41ec-468f-884f-e5c4c81f9c2c/iso-216-2007 | status | 2026-11-08 | S |
| ISO 5457:1999 preview (FR) | https://cdn.standards.iteh.ai/samples/29017/18ae933e25804736af953d3c92e76c4d/ISO-5457-1999.pdf | 3, 4.1-4.5, 5, Tables 1, 2 | 2026-11-08 | P |
| ISO 5457:1999 catalogue (iTeh) | https://standards.iteh.ai/catalog/standards/iso/cda39033-c87c-4173-a875-365a3e33753f/iso-5457-1999 | status, Amd 1:2010 | 2026-11-08 | S |
| ISO 5457:1980 preview (SIST ISO 5457:1995) | https://cdn.standards.iteh.ai/samples/11505/ac9a58640d44446ebdc5aa5229e84fd6/SIST-ISO-5457-1995.pdf | 5, 6, 7 | 2026-11-08 | P |
| ISO 7200:2004 preview and catalogue | https://cdn.standards.iteh.ai/samples/35446/d3b0887cb4fa47f49f8718807d3b8903/ISO-7200-2004.pdf ; https://standards.iteh.ai/catalog/standards/iso/cda0743a-d12c-45c6-87fd-4e96ffda6041/iso-7200-2004 | front matter; status | 2026-11-08 | P / S |
| IS 11665:2009 (identical to ISO 7200:2004) | https://law.resource.org/pub/in/bis/S01/is.11665.2010.pdf | foreword, clauses 1-5, Tables 1-3, Figures 1-2 | 2026-11-08 | P |
| ISO pages 36631, 29017, 35446 | https://www.iso.org/standard/36631.html (and 29017, 35446) | refused, 403 | 2026-11-08 | none |
| ASME Y14.1-2020 product page | https://www.asme.org/codes-standards/find-codes-standards/drawing-sheet-size-and-format | edition, pages, ISBN | 2026-11-08 | P |
| NSAI store, ASME Y14.1:2020 | https://shop.standards.ie/en-ie/standards/asme-y14-1-2020-138878_saig_asme_asme_2907891 | status, date, supersedes | 2026-11-08 | P |
| Wikipedia, ANSI/ASME Y14.1 (wikitext) | https://en.wikipedia.org/wiki/ANSI/ASME_Y14.1 | tables, history | 2026-11-08 | S |
| Wikipedia, Paper size (wikitext) | https://en.wikipedia.org/wiki/Paper_size | ISO table, Architectural sizes, ISO 5457, JIS B | 2026-11-08 | S |
| Wikipedia, ISO 7200 | https://en.wikipedia.org/wiki/ISO_7200 | editions | 2026-11-08 | S |
| Wikipedia, Transverse Mercator projection | https://en.wikipedia.org/wiki/Transverse_Mercator_projection | Convergence | 2026-11-08 | S |
| Kuhn, International standard paper sizes | https://www.cl.cam.ac.uk/~mgk25/iso-paper.html | rule, table, tolerances, JIS B | 2026-11-08 | S |
| NIBS National CAD Standard | https://www.nationalcadstandard.org/ncs6/ | V6, V7 committee | 2026-11-08 | P (status) |
| CSI, National CAD Standard | https://www.csiresources.org/standards/ncs | UDS modules' scope | 2026-11-08 | P (scope) |
| VHA National CAD Standard Application Guide (2006) | https://www.wbdg.org/FFC/VA/VACAD/VHACADAppGuide.pdf | Title Block | 2026-11-08 | P (VA usage) |
| OpenExamPrep ARE 17.1 | https://open-exam-prep.com/study-guides/are/ch17-pdd-documentation-specifications/pdd-sheet-organization-title-blocks | sheet zones | 2026-11-08 | S (weak) |
| A/E/C CADD Standard R3.0 (UNT web archive) | https://webarchive.library.unt.edu/web/20090109033133/https:/www.nwp.usace.army.mil/ec/docs/AEC_CADD_Standard_R3.0.pdf | refused (TLS; 503) | 2026-11-08 | none |
| ArcGIS Pro 3.5, Add a layout to a project | https://pro.arcgis.com/en/pro-app/3.5/help/layouts/add-a-layout-to-your-project.htm | whole page | 2026-11-08 | P |
| ArcGIS Pro 3.5, Add and modify map frames | https://pro.arcgis.com/en/pro-app/3.5/help/layouts/add-and-modify-map-frames.htm | whole page | 2026-11-08 | P |
| ArcGIS Pro 3.5, Map frame constraints | https://pro.arcgis.com/en/pro-app/3.5/help/layouts/customizing-your-map-extent.htm | whole page | 2026-11-08 | P |
| ArcGIS Pro 3.5, Work with a map on a layout | https://pro.arcgis.com/en/pro-app/3.5/help/layouts/work-with-a-map-on-a-layout.htm | whole page | 2026-11-08 | P |
| ArcGIS Pro 3.5, North arrows | https://pro.arcgis.com/en/pro-app/3.5/help/layouts/north-arrows.htm | whole page | 2026-11-08 | P |
| ArcGIS Pro 3.5, Scale bars | https://pro.arcgis.com/en/pro-app/3.5/help/layouts/scale-bars.htm | whole page | 2026-11-08 | P |
| ArcGIS Pro 3.5, Add a legend; Work with a legend; Work with a legend item; Legend fitting strategies | https://pro.arcgis.com/en/pro-app/3.5/help/layouts/add-a-legend.htm ; .../work-with-a-legend.htm ; .../work-with-legend-items.htm ; .../layout-fitting-strategies.htm | whole pages | 2026-11-08 | P |
| Esri Ideas, screen ratios in the New Layout gallery | https://community.esri.com/t5/arcgis-pro-ideas/add-common-screen-ratios-to-the-insert-layout-s/idi-p/939497 | the post | 2026-11-08 | S (thin) |
| QGIS source, master (4.3) | https://raw.githubusercontent.com/qgis/QGIS/master/src/core/layout/ (qgspagesizeregistry.cpp, qgslayoutitempicture.cpp, qgslayoutnortharrowhandler.cpp/.h, qgslayoutitemscalebar.cpp, qgslayoutitemlegend.cpp/.h, qgslayoututils.cpp), src/core/scalebar/qgsscalebarsettings.h/.cpp, src/core/qgsbearingutils.cpp, src/core/qgis.h | the functions named in 4.7-4.11; GPL-2.0-or-later | 2026-11-08 | P |
| QGIS user manual, print layout | https://raw.githubusercontent.com/qgis/QGIS-Documentation/master/docs/user_manual/print_layout/ (layout_items/layout_map.rst, layout_legend.rst, layout_scale_bar.rst, layout_image.rst; overview_layout.rst) | the sections named | 2026-11-08 | P |
| Snyder, Map Projections: A Working Manual, USGS PP 1395 (1987) | https://pubs.usgs.gov/pp/1395/report.pdf | convergence paragraph; TM chapter 8 | 2026-11-08 | P |
| Stem, State Plane Coordinate System of 1983, NOAA Manual NOS NGS 5 (1989) | https://geodesy.noaa.gov/library/pdfs/NOAA_Manual_NOS_NGS_0005.pdf | 2.4, 2.5, 3.23 | 2026-11-08 | P |
| Karney, Transverse Mercator with an accuracy of a few nanometers, J. Geodesy 85 (2011) | https://arxiv.org/pdf/1002.1417 | eqs. 11-25 | 2026-11-08 | P |
| NOAA NCEI, World Magnetic Model | https://www.ncei.noaa.gov/products/world-magnetic-model | WMM2025 release, validity, licence | 2026-11-08 | P |
| The app | `src/js/engine/sheets/sheets.js`, `viewports.js`; `survey/survey-arithmetic.js`; `site/alignment-profile.js`; `map/map-tiles.js`, `cityjson.js`, `data-symbology.js`; `site-analysis/zoning-envelope.js`, `access-board.js`; `standards/registry.js` | lines named in 8 | 2026-11-08 | P |
