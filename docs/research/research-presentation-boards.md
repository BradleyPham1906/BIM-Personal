# V174 Presentation P1: boards (research, 2026-11-08)

Under `docs/research/research-protocol.md` ("Research as a scientist does it"). Levels: **P** read in the primary
source (the standard, the vendor's own document, the code read as text, the app's code, or measured here), **S** a
dependable secondary source with the gap said, **U** a search summary or an unchecked single copy, kept out of the code.
This note is written from six working notes in `docs/research/research-presentation-boards/`, each with its own
search log, findings, levels and references:

| Working note | Side | Written by |
|---|---|---|
| `practice.md` | Figma's layer model, Penpot and Excalidraw as open code, Canva and Adobe, QGIS and ArcGIS Pro layouts, BIM layout tools, touch | research agent 1 |
| `map-elements-and-pages.md` | ISO 216, ISO 5457, ISO 7200, ASME Y14.1, Architectural sizes; map frames, legends, north arrows, scale bars; experiments | research agent 2 |
| `compositing.md` | W3C Compositing and Blending, the canvas 2D spec, browser support, PDF 32000-1, SVG and CSS, masks; six browser experiments | research agent 3 |
| `layout.md` | Figma's auto layout, css-flexbox-1, Yoga and Penpot; align, distribute, tidy up; smart spacing; experiments | research agent 4 |
| `app-code-audit.md` | What the app already has, by file and line | the main session |
| `independent-check.md` | The second reader's re-check of every fact the code uses | research agent 5 (part 3 says where it stands) |

## 1. Abstract

The question: how should the app let a person design a board, a page of the set, the way Figma designs a frame? That
means one layer tree (frames, groups, lock, hide, reorder), opacity and a blend mode on every element, masks, shapes,
text and images, align, distribute and smart spacing, and rows and columns that space their children. It also means
the drawing-office pieces: a New Layout gallery of standard pages, and map frames with a live legend, north arrow and
scale bar. All of it within an ES5, zero-dependency app whose boards are HTML today and whose sheets are a canvas.

The answer has six parts.

1. **The element model is the one PDF and SVG define,** and Figma and Penpot share it. Each element has a mode, an
   opacity, and group isolation (pass through or isolated); a mask is alpha, vector or luminance.
2. **The blend modes are the 16 of W3C Compositing and Blending Level 1,** under Figma's names. Figma itself has 18
   plus Pass through, not 16. Its two extra modes (linear burn and linear dodge, shown as Plus darker and Plus
   lighter) exist in neither canvas nor PDF. Canvas, CSS, SVG and PDF all carry the 16. In Chromium 153, canvas
   agreed with our own implementation of the W3C formulas within 1 unit of 8 bits on opaque colours, and SVG
   matched canvas pixel for pixel.
3. **Groups and masks have fixed rules.** A group with opacity or a mode must be composited on its own, or
   overlapping children show through each other (64 units of error measured). A luminance mask needs pixel work
   once, then an alpha mask.
4. **Light auto layout is about 11 KB of our own ES5,** written from Figma's documented rules. It matched Chromium's
   flexbox in 39 of 39 comparable cases. Fill follows css-flexbox-1's freeze loop, not Yoga's or Penpot's variants.
5. **Smart spacing fits a pointer-move budget.** Equal-gap snaps cost 0.5 ms at 1000 boxes, and a board holds 80.
6. **Page sizes are a table per standard,** in the V167 registry. ISO 216's sizes are not reproduced by plainly
   rounding its rule (12 of 22 wrong). The app's "ANSI D (24x36 in)" is in fact Arch D; ANSI D is 22 x 34 in.
   The legend, north arrow and scale bar are bound to one map frame and redraw from it. The app's local plane needs
   only its one true north angle, no grid convergence.

The largest choice is not in the sources but in the app (part 5): whether a designed board is drawn as HTML and SVG,
as the boards are today, or on a canvas, as the sheets are. The recommendation is HTML and SVG, with map frames as
canvases inside them. Twenty decisions for the owner close the note (part 11).

## 2. The question and the hypotheses

**The question.** What element model, compositing, layout aids and map surround do the professional tools give a
designed page? Which of them can the app copy faithfully, in ES5 with no dependencies, on phone, tablet and desktop?
And can it then export them (V176) without changing how they look?

A good answer decides:
- the blend list and its names;
- what a group and a mask do;
- frame against group;
- the selection rules;
- the layout subset and Fill's arithmetic;
- the snap rules;
- the page sizes and their source;
- what each map surround element follows;
- the drawing surface.

| # | Hypothesis (falsifiable) | Outcome | Evidence | Level |
|---|---|---|---|---|
| H1 | Figma has exactly 16 blend modes plus pass through, the W3C list | **Failed.** 18 plus Pass through: the W3C 16 (Normal included) plus linear burn and linear dodge, shown as Plus darker and Plus lighter | practice H-a; compositing H6 (Figma plugin typings) | P |
| H2 | Canvas `globalCompositeOperation` takes exactly the W3C 16 (plus the 12 Porter-Duff operators) and Chromium computes them as the formulas say | **Held.** 28 keywords accepted. Opaque error at most 1.0 (exclusion 1.99) over 12,800 pairs a mode, in gamma-encoded sRGB, not linear | compositing exp. a | P (measured) |
| H3 | Translucent colours match as closely | **Failed in part.** Within 2.8 units in 13 modes; up to 21 for color-dodge, 11 color-burn, 8 saturation near their singular points | compositing exp. a | P (measured) |
| H4 | Per-child alpha is not group opacity; an offscreen group is | **Held.** Overlap differs by 64 units naive against isolated | compositing exp. b | P (measured) |
| H5 | A default group drawn through an offscreen canvas is pixel-identical to drawing its children directly | **Held** at integer offsets (0 of 7,200 pixels differ); at half a pixel it is resampled | compositing exp. b | P (measured) |
| H6 | PDF's soft mask defaults to luminosity | **Failed.** `S` is required in PDF (Table 144); it is CSS `mask-type` whose initial value is luminance | compositing H7 | P |
| H7 | SVG and CSS blend, isolation and mask render as canvas does | **Held** in Chromium: opaque identical in all 16 modes, translucent within 5 | compositing exp. f | P (measured) |
| H8 | Figma's mask clips only the siblings above it in the same parent | **Held, refined:** up to the next mask, the end of the parent or a clipping frame; Alpha by default, Vector and Luminance optional. Penpot's differs (the group's bottom child masks the whole group, alpha only) | practice H-b | P |
| H9 | No mainstream AEC layout tool has per-element blend modes | **Failed for GIS, held for BIM.** QGIS print layout items each have a blend mode (13) and opacity; ArcGIS Pro blends map layers. Revit, Archicad, LayOut, Vectorworks document none (absence of evidence) | practice H-c | P; the BIM side medium |
| H10 | A Figma-documented auto layout subset gives the same boxes as CSS flexbox where Figma states no other rule | **Held.** 39 of 39 to 0.01 px; the 2 Hug-with-Fill cases differ as Figma documents | layout exp. a | P (measured) |
| H11 | Yoga and Penpot share space among Fill children as the specification does | **Failed.** Yoga v3.2.2 leaves 15 px unshared on one order; Penpot 200/100 against the spec's 150/150 with a min | layout H3 | P (code read, measured) |
| H12 | "Distribute spacing" has one definition | **Failed.** Inkscape's by-centre span moves the outermost box; Figma keeps the outermost | layout H4 | P |
| H13 | An equal-gap snap over every pair fits a pointer move at 1000 boxes | **Held** (p95 0.75 ms); but every-pair matching snapped on almost every move, so neighbours only | layout exp. c | P (measured) |
| H14 | ISO 216's sizes are its rule rounded to the millimetre | **Failed.** 12 of 22 wrong; halving the rounded size and rounding down reproduces all 22; the standard gives the table, not a rule | map e01 | P |
| H15 | The app's page sizes match their names | **Failed.** `ANSI-D` and `ANSI-D-L` are 24 x 36 in, Arch D | map e01; `sheets.js:41, 44` | P |
| H16 | QGIS's fitted scale bar uses 1-2-5 numbers | **Failed.** Any leading digit: 126 of 240 cases had 3, 4, 6, 7 or 9 | map e02 | P (code read, measured) |
| H17 | The app's north arrow needs grid convergence | **Failed** for the plan as stored: a local plane turned by `A3D.site.trueNorth`; convergence only for a frame drawn in UTM | map H5, e03 | P |
| H18 | A map frame can show the site's layers with the existing viewport machinery as it is | **Failed.** Data layers, the colour lens, the layer cake and the analysis legend return early under `A3D.sheetCapture`; map tiles under a plot | audit 4 | P |

## 3. Method

- **Search logs:** practice (in its part 1), map elements (3.1), compositing (3.1) and layout (3), each with every
  query, where it was run, what came back and what was kept.
- **Sources by kind.**
  - Specifications and standards: W3C Compositing and Blending Level 1, the WHATWG canvas section,
    css-flexbox-1 section 9, PDF 32000-1:2008 (Adobe's published text), ISO 216:2007 (ISO's preview), ISO 5457
    and ISO 7200 (through IS 11665:2009, identical), and ASME Y14.1-2020 (sold; two secondary sources).
  - Vendors' own documents: Figma's help centre and plugin typings, ArcGIS Pro 3.5 layout help, and the QGIS user
    manual.
  - Open code read as text, licence first: Penpot (MPL-2.0), Excalidraw (MIT), tldraw (method only: its licence
    is not OSI), Yoga v3.2.2 (MIT), QGIS's layout code (GPL: method only), and pdf.js's blend mapping.
  - MDN's browser-compat-data, and the Chromium and WebKit bug trackers.
  - The app's own code.
- **Experiments**, our own code; no downloaded code was run.
  - `docs/research/experiments/v174-blend/`: canvas blend modes against the W3C formulas, group opacity, masks,
    cost, keywords, SVG parity; Chromium 153 headless, SwiftShader.
  - `docs/research/experiments/v174-layout/`: auto layout against Chromium's flexbox, align and distribute, the
    snap search; Node 22.
  - `docs/research/experiments/v174-pages/` (ISO 216 from its rule, the inch series).
  - `docs/research/experiments/v174-scalebar/` (the 1-2-5 chooser against QGIS's fit, grid convergence against
    Karney 2011).
- **Independent check:** `independent-check.md`, a fifth agent that wrote none of the notes. It re-fetched the
  sources and re-ran the ISO rounding, the convergence and three blend checks with its own scripts. Part 3a below
  records its result.

### 3a. The independent check

Done 2026-11-08 (`independent-check.md`). A fifth agent listed 138 facts that code or a default rests on, re-fetched
every source and re-ran three measurements with its own scripts: ISO 216's halve-then-floor rule, the convergence
formula, and blend pixels in Chromium.

- **134 confirmed.** Five of them stay S (the inch sizes among them).
- **3 not confirmed, now corrected here and in the working notes:**
  - PDF's 0.30, 0.59, 0.11 luminosity is an informative note, not a rule. ISO 32000-1 11.5.3 leaves device-space
    luminosity implementation-defined, so a `/Luminosity` mask is not guaranteed to match in every reader (back to
    U; it supports D6's Alpha).
  - ISO 7200 has eight mandatory fields, not seven: document type is the eighth.
  - `globalCompositeOperation` is also used in `site/shadows.js:86-90` (`destination-out`). No blend mode is used
    anywhere still holds.
- **1 split:** the board grid's line is `board-figures.js:20`, not 19.
- **0 could not be checked.**
- **Smaller corrections,** with no change of level:
  - in CSS a single item under space-around or space-evenly is centred, not at the start as in Figma;
  - `destination` left the canvas grammar in 2015;
  - a few app line ranges were off by one or two.

The sources the check did not re-read are listed in its last part. Code that rests on any of them needs that reading
first.

## 4. Findings, by topic

### 4.1 The element tree (practice 2.1, 2.5, 2.10, 2.11; audit 1)

- **Tree order is drawing order,** the top of the list in front. Bring forward, Bring to front, Send backward and
  Send to back act within the parent. Shortcuts: Figma's Ctrl+] and Ctrl+[ (with Shift for to front and to back),
  the same in QGIS. P, high.
- **Frames and groups differ.**
  - A **frame** has its own size and may clip its content (an option). It may carry auto layout, and its children
    take constraints.
  - A **group** has no size of its own: it is its children's bounds, and its children take no constraints.
  - Penpot's tree is the same: board, group, then shapes (rect, path, text, circle, image, svg-raw, bool).
  - P, high.
- **Selection.**
  - A click selects the outermost unlocked, visible ancestor below the board.
  - Double-click or Enter goes one level down; Shift+Enter goes up; Ctrl-click (Cmd on a Mac) selects deep.
  - A "layers here" list picks among stacked layers.
  - Locked and hidden layers are not picked on the canvas but can be selected in the tree.
  - Lock and hide cascade to children.
  - P, high (Figma; Penpot agrees).
- **Nudge** is 1 unit, and 10 with Shift. P, high.
- **Shapes:** rectangle, line, arrow, ellipse, polygon, star (3 to 60 points). **Text:** auto width, auto height or
  fixed size. **Image fill:** fill, fit, crop, tile. P, high.
- **Touch.** Figma's mobile app cannot edit design files (it views, comments, mirrors and presents). Procreate's
  documented gestures are the touch prior art:
  - tap-and-hold picks up a layer to drag it up or down;
  - a swipe from right to left reveals Lock, Duplicate and Delete;
  - "Layer Select" lists every layer under the finger, the touch form of Figma's "layers here";
  - a two-finger tap undoes.

  On touch, the app needs visible buttons for Figma's Enter and Shift+Enter, and Up and Down steps (as V173's data
  rows already have). Affinity's gesture sheet is an image-only PDF, so it stays U. P for Figma; Procreate P;
  Affinity U.
- **The app today has no tree** (audit 1). Sheets hold viewports, and boards hold figures in a 12-column reading
  order. The tree is new.

### 4.2 Opacity, blend modes, isolation (practice 2.2; compositing 4.1 to 4.5)

- **Layer opacity is separate from fill opacity** in Figma's API and in Penpot's `:opacity` and `:fill-opacity`.
  V174 needs layer opacity, and fill opacity belongs to a shape's fill. P, high.
- **The 16 modes, by Figma's names in Figma's order:** Normal, Darken, Multiply, Color burn, Lighten, Screen,
  Color dodge, Overlay, Soft light, Hard light, Difference, Exclusion, Hue, Saturation, Color, Luminosity.
  - **Canvas** keywords are the W3C keywords (`color-dodge` and the rest). `normal` is accepted, but in Chromium it
    reads back as `source-over`, so the app stores its own value and never trusts the read-back.
  - **PDF** names them Normal, Multiply, Screen, Overlay, Darken, Lighten, ColorDodge, ColorBurn, HardLight,
    SoftLight, Difference, Exclusion, Hue, Saturation, Color, Luminosity (Tables 136 and 137).
  - P, high.
- **Pass through and Normal.** Figma's frames and groups default to **Pass through**: their children blend with
  whatever lies beneath. A group set to Normal is **isolated**. Penpot has no pass through, while PDF and SVG have
  both, as `/I` on a transparency group and as CSS `isolation`. P, high.
- **Blending happens on gamma-encoded sRGB,** not linear, in canvas, CSS and PDF alike. Measured in Chromium. P,
  high.
- **Where the specifications disagree.**
  - PDF 2008 and W3C differ at two dodge and burn edge colours (dodge with backdrop 0 and source 1, burn with 1
    and 0); Chromium follows W3C.
  - The luminance weights differ. SVG and CSS masks use 0.2126, 0.7152, 0.0722. PDF leaves device-space luminosity to
    the reader (11.5.3) and gives 0.30, 0.59, 0.11 only as an example in a note (the independent check, row 29).
  - P, high. This matters to V176's export.
- **Unknown modes are ignored** and the previous mode kept, and `globalAlpha = null` silently becomes 0. The renderer
  validates both before drawing. P (measured).

### 4.3 Masks (practice 2.3; compositing 4.6, 5.2)

- **Figma's rule.** The bottom layer of a run masks the siblings above it in the same parent, up to the next mask,
  the end of the parent or a clipping frame. Alpha is the default type, with Vector and Luminance as options. P,
  high.
- **On canvas:**
  - **vector** masks by `clip()`, which is anti-aliased in Chromium, not hard-edged;
  - **alpha** masks by `destination-in` inside an offscreen canvas;
  - **luminance** masks need `ctx.filter` (behind a flag in Safari) or a pixel loop, baked once to an alpha
    canvas and re-baked only when the mask changes.
  - P (measured).
- **Never on the board itself.** `source-in`, `destination-in`, `copy` and `destination-atop` clear everything
  outside the shape within the clip, so they are used only inside an offscreen mask canvas. P (measured).

### 4.4 Layout: rows and columns, align, distribute, smart spacing (layout 4.1 to 4.4)

- **The auto layout subset:**
  - direction: row, column or wrap;
  - gap: a number, or Auto, which spreads the children and never goes below 0;
  - padding;
  - main and cross alignment;
  - each child Fixed, Hug or Fill, with a min and a max;
  - hidden children and those set to ignore auto layout leave the flow.
  - P, high (Figma's guide and flows article).
- **Rules where Figma departs from CSS.**
  - A Hug frame with a Fill child becomes Fixed on that axis.
  - A frame is never smaller than its padding.
  - A row's gap may be negative; the gap between wrapped rows may not.
  - Wrap breaks before the first item that would not fit, and an exact fit stays on the line.
  - P, high.
- **Fill** is `flex: 1 1 0` with css-flexbox-1's freeze loop (9.7). Chromium agrees. That Figma does the same is U:
  Figma was not measured here (no account in this environment). P for CSS; U for Figma.
- **Align** uses the selection's bounds, or the parent for one element (Figma). The tools disagree here: ArcGIS
  Pro aligns to the first element selected, Penpot to the outermost. P, high.
- **Distribute** needs three or more elements and keeps the outermost two, spacing the rest in equal gaps.
  Excalidraw uses centres when items overlap. **Tidy up** uses the most common gap. P, high for Figma's statement;
  "outermost" with a wide box is U (part 7).
- **Snaps** are a screen-pixel threshold divided by the zoom: 8 in Excalidraw and tldraw, 10 and 20 in Penpot. The
  board already does this with the drawing's 12 px (`board-edit.js:105`). P, high.
- **Equal-gap snap** cost: 0.02 ms per pointer move at 200 boxes, 0.5 ms at 1000 (p95 0.75 ms). Building the gap
  index once per drag takes 14 to 53 ms. Snaps are limited to neighbours, because every-pair matching snapped on
  almost every move. P (measured).

### 4.5 Pages: the New Layout gallery (map elements 4.1 to 4.7)

- **ISO 216:2007's A and B tables,** A0 841 x 1189 to A10 26 x 37 and B0 1000 x 1414 to B10 31 x 44 mm, are stored
  as published. P, high.
- **ISO 5457:1999 (with Amd 1:2010), the drawing sheet:**
  - margins of 20 mm on the left and 10 mm elsewhere, inside a 0.7 mm frame line;
  - the title block at the bottom right;
  - A0 to A3 landscape only, A4 portrait only;
  - grid fields 50 mm.
  - The amendment's content is U.
  - P, high.
- **ISO 7200:2004, the title block:** 180 mm wide, with eight mandatory fields (legal owner, identification number,
  date of issue, sheet number, title, approval person, creator, document type) and optional ones. P, through IS 11665:2009, which
  is identical.
- **ANSI A to E** (8.5 x 11, 11 x 17, 17 x 22, 22 x 34, 34 x 44 in), from ASME Y14.1-2020. S: two independent
  copies agree, and the standard is sold.
- **Architectural A to E and E1** (9 x 12, 12 x 18, 18 x 24, 24 x 36, 36 x 48, and 30 x 42 in). S: two agree. Which
  document defines them (Y14.1 or the NCS) is U.
- **Inch sizes are converted exactly** (x 25.4): 22 x 34 in is 558.8 x 863.6 mm. P (arithmetic).
- **The app has 11 sizes, one of them misnamed** (H15). The gallery is new: the New Sheet dialog is a select list
  (`viewports.js:274-306`).

### 4.6 Map frames and their surround (map elements 4.8 to 4.11; audit 4, 5)

- **A map frame** is a viewport onto a map with an extent, a scale (which may be locked) and a rotation. Each
  surround element is bound to one frame. P, high (ArcGIS Pro; QGIS).
- **Legend.**
  - In ArcGIS Pro it follows the map's visible layers by default, and adds new layers.
  - "Only show features visible in the map extent" is an option.
  - QGIS 4 is mixed: new legends default to visible layers, while the item itself starts with all layers.
  - The app's own legend rows (`bimLensRows`, `bimDataLegendHtml`, `bimResLegendHtml`) are the source that keeps it
    in step with the Layers tab.
  - P, high.
- **North arrow.**
  - Its angle is the frame's rotation, plus the map's, plus the true north correction, plus a typed offset.
    ArcGIS's offset is counter-clockwise positive; QGIS's is clockwise positive.
  - For the app's plan the true north correction is `A3D.site.trueNorth` alone.
  - Grid convergence, atan(tan(dlon) * sin(lat)), within 0.05 arcsec of Karney's exact series, enters only for a
    frame in a projected grid. It changes by 27 arcsec across 1 km at Philadelphia, so one value per frame is
    enough.
  - P, high (code read, measured).
- **Scale bar.**
  - Its length is a round number. ArcGIS lets the user choose what stays fixed: the division value, the number of
    divisions, or the width. QGIS fits to a width range with any leading digit.
  - A 1-2-5 ladder, the largest that fits between about 15 % and 40 % of the frame's width, fitted 240 of 240
    cases from 1:1 to 1:50,000,000.
  - It shows 2 divisions (QGIS's default), m to km at 1000 m and ft to mi at a quarter mile.
  - The app's two board scale bars already use fixed ladders (`zoning-envelope.js:606`, `access-board.js:65`).
  - P for the tools' rules; ours measured.

## 5. The alternatives compared

### 5.1 The drawing surface (audit 1; compositing 5, exp. f; layout 5)

Criteria, stated before the comparison: (a) every element can have opacity, the 16 modes, isolation and masks;
(b) V172b's figures (HTML cards of SVG and tables) and V175's live elements stay live and crisp; (c) print, Present
and V176's PDF, PNG and SVG export look as the board does; (d) phone and tablet: pan, zoom, reading order; (e) the
code it reuses and the code it adds; (f) cost per frame with 80 elements.

| | A. HTML and SVG board (as boards are today), map frames as canvases inside | B. One canvas, as sheets are | C. Canvas for the board, HTML figures rasterised onto it |
|---|---|---|---|
| (a) compositing | CSS `mix-blend-mode`, `opacity`, `isolation`, `clip-path`, `mask`: the same 16 and pass through by default (CSS groups do not isolate unless told); measured equal to canvas in Chromium (exp. f, for SVG) | `globalCompositeOperation`, offscreen groups, `destination-in` masks (measured) | as B |
| (b) figures | Native: the cards are HTML already | Every figure redrawn in canvas: 33 figures rewritten | Rasterised through SVG `foreignObject`; tainting and fonts U |
| (c) export | Print is HTML already; SVG export is close to the DOM; PDF through the print path, where blend fidelity is U | PNG direct; SVG through a second writer (the sheet's two writers today) | as B, figures as images |
| (d) phone | The board's narrow view exists (reading order) | The page's fit and zoom exist | as B |
| (e) code | Reuses `board-edit.js` drag, snaps and figures; adds a tree, an element renderer, the surround | Reuses the sheet's canvas and viewports; rewrites figures | Least reuse of either |
| (f) cost | The browser composites; not measured here with 80 elements | 9 to 23 ms for 200 elements (exp. d) | as B, plus rasterising |

**Recommendation: A.** It keeps every figure live and crisp at no rewrite, the compositing is the same model (H7),
and the map frame, the one element that needs the model's renderer, is a canvas inside it, drawn by the viewport
machinery. What would change it:
- printing (or V176's PDF) losing blend modes in Chrome's print path; that is the first thing to test when building
  (part 10);
- the owner preferring one renderer for sheets and boards alike, in which case B.

### 5.2 The blend list (practice 3; compositing 5)

| | Figma's 18 and Pass through | **The W3C 16 and Pass through** | QGIS's 13 | Opacity only |
|---|---|---|---|---|
| Canvas and CSS | 17 of 18 (no linear burn) | all 16 | Addition and Subtract are not W3C | trivial |
| PDF | the two linear modes rasterised | all 16 native | partial | native |
| Figma parity | exact | the 16 under Figma's names | no | no |

**Recommendation:** the W3C 16 under Figma's names, with Pass through the default for frames and groups and Normal
isolating them. PIPELINE's "the same 16 modes as Figma" is corrected to say so.

### 5.3 Groups and masks (compositing 5.1, 5.2)

The renderer follows from the measurements: pass through when the group is default, an isolated offscreen sized to
the group's box otherwise, never one the size of the board (about 98 ms with 20 groups); vector masks by clip, alpha
by `destination-in`, luminance baked once. In option A the same rules hold through CSS (`isolation: isolate` on a
group that has a mode or opacity below 1; `mask-type`), and the map frame's canvas follows them internally.

### 5.4 Layout (layout 5)

| | **Figma-like subset in ES5** | CSS flexbox in hidden DOM, read back | Port Yoga | Align and distribute only |
|---|---|---|---|---|
| Deterministic, Node-testable | yes | no (needs a browser) | yes, but departs from the spec (H11) | yes |
| Same boxes in print and export | yes (numbers the board owns) | only where a DOM exists | yes | yes |
| Size | about 11 KB, 250 lines | small | about 2400 C++ lines to port | 5 KB |
| Scope | full | full, but Hug with Fill differs from Figma | full | short of the scope |

**Recommendation:** the subset, with Chromium kept as the test oracle in the experiments. In option A the positions
are still computed by our code and written as absolute positions, so print and export do not depend on the browser's
flexbox.

### 5.5 Page sizes (map elements 5.1) and the scale bar (5.2)

Page sizes are registry records, each size stored once (short by long side) and turned by an orientation flag, with
the editions ISO 216:2007, ISO 5457:1999+A1:2010, ASME Y14.1-2020 and ISO 7200:2004. The V116 keys stay readable:
`ANSI-D` and `ANSI-D-L` become Arch D under their true name, keeping their size. The scale bar is the 1-2-5 ladder by
default, with ArcGIS's choice of what stays fixed.

## 6. The experiments

All are our own code; the raw outputs sit beside the scripts.

| Experiment | What | Result |
|---|---|---|
| v174-blend a | 16 modes, 12,800 colour pairs each, opaque and translucent, against our W3C implementation | Opaque within 1.0 (exclusion 1.99); translucent within 2.8 in 13 modes, 21 color-dodge, 11 color-burn, 8 saturation |
| v174-blend b | Group opacity: per-child alpha against an offscreen | 64 units apart in the overlap; offscreen at integer offsets identical to direct (0 of 7,200) |
| v174-blend c | Masks on 2000 x 1400, median of runs | No mask 2.0 ms; clip 3.9; alpha 15.4; luminance each frame 37 (pixels) or 34 (filter); luminance baked 16 |
| v174-blend d | 200 elements | Normal 9 ms; random modes 16; non-separable 17 to 23; 20 isolated groups 9 to 21 sized to the group, about 98 board-sized; 200 isolated elements 76 ms on one shared scratch canvas, 28 ms with one canvas each |
| v174-blend e | Keywords | 28 accepted; unknown ignored; `normal` reads back `source-over` |
| v174-blend f | SVG `mix-blend-mode`, `isolation`, `mask` against canvas | Opaque identical in 16 modes; translucent within 5 |
| v174-layout a | 41 cases against Chromium's flexbox | 39 of 39 comparable agree to 0.01 px; the 2 Hug-with-Fill differ as documented |
| v174-layout b | Align and distribute | Two "outermost" readings part with a wide box (Inkscape's gives x = -5) |
| v174-layout c | Equal-gap snap, 50 to 1000 boxes | Median 0.02 ms at 200, 0.5 ms at 1000, p95 0.75 ms; index 14 to 53 ms per drag at 1000 |
| v174-pages | ISO 216 from its rule; inch series | Plain rounding 12 of 22 wrong; halve-then-floor 22 of 22 |
| v174-scalebar | 1-2-5 against QGIS's fit, 240 cases; convergence | Both fit 240 of 240; 126 of QGIS's lengths not 1-2-5; convergence within 0.05 arcsec of Karney's series |

Environment: Chromium 153 headless on SwiftShader (no GPU), and Node 22. Firefox, Safari and phones were not
available here; for them the notes rely on MDN's compatibility data and the bug trackers.

## 7. Edges

- **Blend modes:**
  - a blended child inside a pass-through group blends with the board beneath;
  - an isolated group whose first element is `destination-in` composites to nothing;
  - a shadow under a multiply element is multiplied too;
  - an offscreen drawn at a half pixel is resampled;
  - two clips meeting on a pixel boundary leave alpha 192, not 255.
- **Masks:** a mask with nothing above it; a mask inside a clipping frame; a luminance mask with transparent pixels
  (its luminance times its alpha).
- **Auto layout:**
  - Hug with Fill;
  - Fill children with min greater than max (min wins);
  - zero children (Hug is the padding);
  - a first item larger than the line goes alone;
  - Auto gap with one child, or with overflow (gap 0, start);
  - centre alignment with overflow (overflows on both sides).
- **Distribute:** fewer than three boxes changes nothing; overlapping boxes give a negative gap; a wide box makes the
  two "outermost" readings part.
- **Pages:**
  - A0 to A3 in portrait, or A4 in landscape, is not to ISO 5457 and is marked;
  - Custom sizes have no frame standard;
  - an old sheet keyed `ANSI-D` keeps 24 x 36 in.
- **Map surround:**
  - a rotated map frame;
  - a legend with no visible layer (hidden, or a line saying so: an owner's choice);
  - a scale bar at 1:1 and at 1:50,000,000;
  - feet against metres;
  - a frame in UTM (convergence) against the local plane (none).
- **Phone:** a frame with auto layout on a phone (a row becomes a column in reading order?); drag by a handle, as
  the board's figures do (`board-edit.js:147-160`).

## 8. What the app already has (audit, with file and line)

- **Two machines.** Sheets are canvas: `sheets.js:327-449`, with viewports by `bimRenderSourceToCanvas`
  (`sheets.js:250-297`). Boards are HTML on a 12-column grid: `board-figures.js:20`; edited in `board-edit.js:104-224`.
- **Sizes:** `SHEET_SIZES` at `sheets.js:34-48`, 11 sizes, with `ANSI-D` and `ANSI-D-L` 24 x 36 in. Only the select
  list of the New Sheet dialog (`viewports.js:274-306`).
- **The title block:** fixed, at the bottom right (`sheets.js:367-394`, `viewports.js:738-764`).
- **Layers that stop at paper:** data layers (`map/find-open-data.js:321-323`), the colour lens
  (`map/colour-lens.js:201`), the layer cake (`map/layer-cake.js:77`), map tiles in a plot (`map/map-tiles.js:265,
  304`), and the analysis legend (`site-analysis/model-analyses.js:32`).
- **North and scale:**
  - `A3D.site.trueNorth` (`site/alignment-profile.js:650-658`, `survey/survey-arithmetic.js:5-8`);
  - the plan's north arrow (`site/property.js:130-150`);
  - the two scale bar ladders (`zoning-envelope.js:606-612`, `access-board.js:65-71`);
  - a fixed board north glyph (`access-board.js:73`).
- **Legend rows:** `map/data-symbology.js:105-133`, `layers/analysis-data-rows.js:39-60`.
- **Snaps:** `A3D_SNAP` (`drawing/plan-mode-sketch.js:41`), the board's edge snap (`board-edit.js:104-133`).
- **Undo** snapshots the whole state, sheets and boards included, up to 50 steps (`plan-mode-sketch.js:289-300`). So
  images go by reference into IndexedDB, never inline (a 4 MB image is 50 copies).
- **Files over 400 lines:** `viewports.js` 928, `presentation-panel.js` 819, `board-edit.js` 491. V174's code goes
  into new files.

## 9. Risks and threats to validity

- **One engine measured.** Chromium 153 headless on SwiftShader; a real GPU would change the timings and could change
  rounding. Safari's `destination-in` slow path (WebKit 209802) and Firefox's numbers are not measured here.
- **Figma itself was not run** (no account in this environment). Its Fill arithmetic, its "outermost" and any
  equal-spacing snap threshold are from its documents, or U.
- **The BIM tools' lack of blend modes is absence of evidence** from their help.
- **Sold standards.** ASME Y14.1-2020 and the NCS were not read; their inch sizes rest on two agreeing copies.
- **Print and PDF fidelity of CSS blend modes in Chrome's print path** is not measured: it decides 5.1.
- **Memory on phones:** an isolated offscreen of 2000 x 1400 is 11.2 MB; sized to the group, far less, but not
  measured on a phone.
- **Hosts refused,** so Canva's and Adobe's editor facts stay U (part 10).

## 10. What is still open (U)

- **Figma** (not measured here):
  - Fill with min and max;
  - "outermost" with a wide box;
  - the equal-spacing marker and its threshold;
  - the Clip content default;
  - whether a first click inside a top-level frame selects the child.
- **Canva's editor** (canva.com 403); **Adobe's** Illustrator, InDesign and Express transparency and alignment
  (helpx.adobe.com and adobe.com 403); **Affinity's** iPad gestures (image-only PDF).
- **Standards:**
  - whether ASME Y14.1-2020 defines the Arch sizes;
  - the NCS V6 sheet sizes and title block;
  - ISO 5457 Amendment 1:2010;
  - ISO 216's tolerances;
  - ISO 32000-2's dodge and burn.
  - Refused: iso.org, webstore.ansi.org, apps.dtic.mil, the UNT web archive, jisc.go.jp.
- **ArcGIS Pro:** which sizes its New Layout gallery lists in each section, and how it rounds a scale bar's division.
- **The browser:**
  - each canvas keyword's support by browser (BCD lacks per-value data; WPT's `2d.composite` results not read);
  - Safari's and Firefox's numeric agreement;
  - CSS blend modes in print and in Chrome's PDF;
  - SVG `foreignObject` on a canvas (option C only).
- **The first build step should measure** CSS blend modes printed to PDF in Chrome and Edge, and a 2000 x 1400 board
  of 80 elements on a phone.

## 11. The owner's decisions

Asked together, each with the evidence and a recommendation. **Answered 2026-11-08: all twenty as recommended** (the
owner: "just go for it", after the research merged in PR #80).

| # | Question | Evidence | Recommended |
|---|---|---|---|
| D1 | The drawing surface: HTML and SVG with canvas map frames (A), one canvas (B), or canvas with rasterised figures (C)? | 5.1; H7; audit 1 | **A** |
| D2 | Blend modes: the W3C 16 under Figma's names, or also Figma's linear burn and dodge (no canvas or PDF operator)? | H1, 5.2 | **The 16**, and correct PIPELINE's wording |
| D3 | Groups: Pass through by default and Normal to isolate, as Figma; or always isolate a group with any setting? | 4.2; compositing 5.1 | **As Figma** |
| D4 | Images: kept once in IndexedDB by reference (a hash), never inline in the board, with a size limit (the 4 MB of the plan's image note)? | audit 6 | **Yes**, 4 MB per image |
| D5 | Masks in V174: alpha and vector only, or luminance too (baked, re-baked when the mask changes)? | 4.3; exp. c | **All three**, Alpha the default |
| D6 | V176's export of luminance masks: PDF `/Luminosity` with PDF's weights, or pre-baked to `/Alpha` so PDF and SVG match the board exactly? | 4.2 | **Pre-baked to Alpha** |
| D7 | Auto layout scope: row, column, wrap, gap with Auto, padding, alignment, Fixed, Hug, Fill, min and max, hidden, ignore auto layout; no grid flow or text baselines? | 4.4; layout 5 | **Yes** |
| D8 | Fill: CSS's freeze loop (Chromium-measured), not Penpot's grow-from-min? | H11 | **CSS's** |
| D9 | Distribute's "outermost": keep the least left edge and the greatest right edge (our Figma reading)? | H12 | **Yes** |
| D10 | Smart spacing: equal-gap snaps among neighbours at the drawing's 12 px, or Figma-like 8 px? | 4.4; H13 | **12 px**, one threshold for the whole app |
| D11 | On a phone, does a row frame become a column in reading order, as the board's figures do today? | audit 1 | **Yes** |
| D12 | Page sizes as registry records with editions, and `ANSI D` renamed Arch D (old sheets keep their size)? | H14, H15; 5.5 | **Yes** |
| D13 | Families in the gallery: ISO A0 to A4, ANSI A to E, Arch A to E1; ISO B on request; JIS B not? (A5?) | 4.5 | **As listed**, no A5 |
| D14 | Title blocks: an ISO 5457/7200 one (bottom right, 180 mm) and a US right-hand strip one, by family; portrait A0 to A3 allowed but marked "not to ISO 5457"? | 4.5 | **Yes and yes** |
| D15 | Scale bar numbers: 1-2-5, or 1-2-2.5-5 to match the zoning board's 25 m? | 4.6; H16 | **1-2-5** |
| D16 | North arrow: plan north and true north (`trueNorth`), with a typed offset for magnetic declination; no magnetic model in V174? | 4.6; H17 | **Yes** |
| D17 | Legend: follow visible layers and new layers, layer order on, extent filter off, hidden when empty? | 4.6 | **Yes** (order on, because the Layers tab already orders them) |
| D18 | Map frames on paper: let data layers, analyses and their legends draw under `sheetCapture` in a map frame (V173 kept them off paper), and map tiles in a plot with their credit printed on the page? | H18; audit 4 | **Yes**, the credit always printed |
| D19 | Old boards: open each V172b figure as one element of the new tree (columns converted to millimetres), so a board made before V174 looks the same? | audit 8 | **Yes** |
| D20 | V174's split into parts (a: the tree, elements and compositing; b: layout, align, distribute and snaps; c: the gallery and title blocks; d: map frames and their surround), one PR each as V173 was? | this note | **Yes** |

## 12. References

Every source, with its URL, what was read, the date and its level, is listed in the working notes' references:
`practice.md` part 9, `map-elements-and-pages.md` part 13, `compositing.md` part 12, `layout.md` part 12. The app's
code is cited by file and line in `app-code-audit.md`. The sources the code will rest on most:

| Source | Read | Level |
|---|---|---|
| W3C Compositing and Blending Level 1 (Candidate Recommendation), w3.org/TR/compositing-1 | sections 5 to 10: the blend formulas, groups, isolation | P |
| WHATWG HTML, the canvas 2D context (html.spec.whatwg.org) | `globalCompositeOperation`, `globalAlpha`, the drawing model | P |
| PDF 32000-1:2008 (Adobe's published copy) | 11.3.5 blend modes (Tables 136, 137), 11.6.5 soft masks (Table 144), 11.4.5 groups | P |
| W3C CSS Flexible Box Layout Level 1 | section 9, the layout algorithm, 9.7 resolving flexible lengths | P |
| Figma help centre and plugin API typings (help.figma.com; @figma/plugin-typings) | layers, blend modes, masks, auto layout, alignment | P |
| Penpot (github.com/penpot/penpot, MPL-2.0) | the shape schema, blend modes, masks, flex layout, snaps | P (code read) |
| Excalidraw (MIT), tldraw (method only), Yoga v3.2.2 (MIT) | snapping, distribution; the flex algorithm | P (code read) |
| ISO 216:2007 (ISO's preview); ISO 5457:1999 and ISO 7200:2004 (through IS 11665:2009) | the A and B tables; the sheet frame; the title block fields | P |
| ASME Y14.1-2020 (sold) | ANSI and Arch sizes, from two agreeing copies | S |
| ArcGIS Pro 3.5 layout help (pro.arcgis.com) | map frames, legend, north arrow, scale bar | P |
| QGIS user manual and source (github.com/qgis/QGIS, GPL: method only) | print layout items, blend modes, the legend, `qgslayoutnortharrowhandler.cpp`, `qgslayoututils.cpp` | P |
| Karney, C. F. F. (2011), "Transverse Mercator with an accuracy of a few nanometers", J. Geodesy 85 | the convergence series | P |
| MDN browser-compat-data (github.com/mdn/browser-compat-data) | canvas and CSS blend support | P |
