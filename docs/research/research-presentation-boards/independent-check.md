# V174 research: independent second reading

Date: 2026-11-08. Reader: an independent agent that did not write `practice.md`, `map-elements-and-pages.md`,
`compositing.md`, `layout.md` or `app-code-audit.md`. This is step 9 of `docs/research/research-protocol.md`: every
fact that code or a default will rest on is re-read in its source, or re-measured, and recorded as confirmed or not.
A fact that fails goes back to U.

## Method

- The five notes were read in full. Every fact that a line of V174 code, a stored default or a registry record would
  rest on was listed (each note's "what the code would depend on" list, and the facts behind its recommendations).
  Facts that only describe practice and that no code uses (Canva, Adobe, Revit, Archicad, SketchUp LayOut,
  Vectorworks, Procreate, the touch survey, the Firefox and WebKit bug reports, the timings of exp. c and d) were not
  re-checked; they are listed at the end.
- Each source was fetched again on 2026-11-08 with curl through the session proxy, into an empty directory of the
  session scratchpad (`dl-check/`), and read as text only (HTML stripped by a small script; PDFs through
  `pdftotext -layout`). No quotation in the notes was trusted. What was fetched:
  - W3C TR: `compositing-1` (CRD 2024-03-21), `css-masking-1` (CRD 2021-08-05), `filter-effects-1`,
    `SVG2/render.html`, `SVG11/filters.html`.
  - raw.githubusercontent.com: whatwg/html `main` `source`; w3c/csswg-drafts `main` `css-flexbox-1/Overview.bs`;
    figma/plugin-typings `master` `plugin-api.d.ts` (package 1.142.0); mdn/browser-compat-data `main`
    `api/CanvasRenderingContext2D.json`; penpot/penpot at `904cdd97...` (`types/shape.cljc`, `files/helpers.cljc`,
    `types/shape/layout.cljc`, `flex_layout/layout_data.cljc`, frontend `ui/shapes/{group,mask,frame}.cljs`,
    `main/snap.cljs`); excalidraw/excalidraw at `701b901a...` (`snapping.ts`, `distribute.ts`, `align.ts`, LICENSE);
    tldraw/tldraw at `69f4395` (`options.ts`, `SnapManager.ts`, `BoundsSnaps.ts`); qgis/QGIS `master`
    (`qgspagesizeregistry.cpp`, `qgslayoutnortharrowhandler.cpp/.h`, `qgsbearingutils.cpp`,
    `qgsscalebarsettings.h/.cpp`, `qgslayoututils.cpp`, `qgslayoutitemscalebar.cpp`, `qgslayoutitemlegend.cpp`,
    `qgslayoutitempicture.cpp`); qgis/QGIS-Documentation `master` (`general_tools.rst`, layout item pages).
  - gitlab.com inkscape `master` `src/actions/actions-object-align.cpp`.
  - opensource.adobe.com `PDF32000_2008.pdf` (22.5 MB).
  - help.figma.com through its Zendesk article API (JSON bodies of 16 articles: 360040667874, 360040450253,
    4404575206295, 360040449873, 360041003694, 360041098433, 360040451373, 31289464393751, 360039956914, 360041596573,
    360041112614, 360039832054, 360039957734, 360040450133, 27378154668951, 360041539473).
  - pro.arcgis.com 3.5: `north-arrows`, `scale-bars`, `work-with-a-legend`, `add-a-legend`,
    `work-with-layout-elements`, `layout-contents-pane`, `apply-visual-effects`. help.penpot.app layers page.
  - cdn.standards.iteh.ai previews of ISO 216:2007 and ISO 5457:1999 (French); law.resource.org IS 11665:2009
    (identical adoption of ISO 7200:2004); Wikipedia raw wikitext of "Paper size", "ANSI/ASME Y14.1",
    "Transverse Mercator projection"; Kuhn's ISO paper page; arXiv 1002.1417 (Karney 2011).
  - geodesy.noaa.gov NCAT API (`/api/ncat/llh`, NAD83(2011)), as an outside reference for UTM convergence.
  - No host refused this reader. iso.org, helpx.adobe.com and canva.com were not tried again (no code rests on them).
- Re-run independently, with scripts written for this check in the scratchpad (`check/`), not the notes' scripts:
  - `iso216_check.py`: ISO 216 A0-A10 and B0-B10 from the rule, three rounding rules, against the tables re-read.
  - `convergence_check.js`: UTM grid convergence by the spherical formula and by a Krueger series coded here from
    Karney (2011), against five NGS NCAT values.
  - `blend_check.js`: nine blend modes drawn on opaque colours in Chromium 153.0.8010.12 headless (Playwright 1.63.0,
    `chromium.launch()`, nothing installed), compared with an implementation of W3C sections 10.1 and 10.2 written
    here; also keyword read-back, `globalAlpha` setter behaviour, and group opacity by per-child alpha against an
    offscreen canvas.
  - `flex_check.js`: three flexbox claims in the same Chromium (wrap at exact fit, overflow fallbacks, Fill shares).
- The app-code audit's file:line claims were checked by reading each range in `src/` at the working copy (HEAD
  47a501a); `grep -rn` was used for the "nowhere else" claims.
- Verdicts: CONFIRMED (the source says it, or the re-run gives it); NOT CONFIRMED (the source says something else,
  or does not say it); COULD NOT CHECK (the source did not load). "CONFIRMED as S" keeps a secondary level.

## Table

Abbreviations: Pr = practice.md, M = map-elements-and-pages.md, Co = compositing.md, L = layout.md,
A = app-code-audit.md.

### Compositing: W3C, WHATWG, Chromium

| # | Fact | Note | Source re-read | Verdict | Remark |
|---|---|---|---|---|---|
| 1 | Compositing and Blending 1 is the CRD of 21 March 2024; editor Chris Harrelson; former editors Cabanier, Andronikos | Co 4.1 | TR header | CONFIRMED | |
| 2 | `<blend-mode>` = normal, darken, multiply, color-burn, lighten, screen, color-dodge, overlay, soft-light, hard-light, difference, exclusion, hue, saturation, color, luminosity (16) | Co 4.1, Pr H-a, Pr 10.1 | 3.4.1 | CONFIRMED | Grammar order as listed. |
| 3 | Canvas `globalCompositeOperation` takes `<blend-mode> \| <composite-mode>`; the 12 operators clear ... xor, lighter; initial source-over; `destination` removed | Co 4.1 | section 4; changes list | CONFIRMED | The removal is listed among changes "relative to the CR of 20 February 2014", so it was published in the 2015 CR, not in 2014 as the note says. No code rests on the date. |
| 4 | Cr = (1 - ab) Cs + ab B(Cb, Cs), and the source-over expansion ao Co = as(1 - ab)Cs + as ab B + (1 - as) ab Cb | Co 4.1 | section 10 | CONFIRMED | |
| 5 | Blending must not use premultiplied values; the mixing result is clamped | Co 4.1 | section 10 | CONFIRMED | |
| 6 | Separable formulas, including dodge (0 if Cb = 0, else 1 if Cs = 1, else min(1, Cb/(1 - Cs))), burn (1 if Cb = 1, else 0 if Cs = 0, else 1 - min(1, (1 - Cb)/Cs)), hard-light, overlay = HardLight(Cs, Cb), soft-light with D(Cb) | Co 4.1 | 10.1.1-10.1.12 | CONFIRMED | |
| 7 | Non-separable: Lum = 0.3 R + 0.59 G + 0.11 B, ClipColor, SetLum, Sat, SetSat, and the four modes | Co 4.1 | 10.2 | CONFIRMED | |
| 8 | Isolated group: initial backdrop transparent black; non-isolated: the group backdrop; default groups invariant; isolation, a non-normal mode or a non-source-over operator can break it | Co 4.1 | 8, 8.1, 8.2 | CONFIRMED | |
| 9 | In SVG, opacity, filters, 3D transforms, blending and masking isolate a group; in CSS every stacking context is isolated; an SVG mask always makes an isolated group | Co 4.1, 4.5 | 3.2, 3.3 | CONFIRMED | |
| 10 | An isolated group whose bottom element uses a backdrop-dependent operator composites to nothing | Co 4.1, 7 | 9.2 | CONFIRMED | |
| 11 | Order: filter, then clipping, masking, blending, compositing | Co 4.1 | 3.1 | CONFIRMED | |
| 12 | Blending time must not depend on pixel values (timing attacks) | Co 4.1 | security section | CONFIRMED | |
| 13 | `lighter` is Porter-Duff plus, Fa = Fb = 1, so it adds alpha too | Co 7, Pr H-e | 9.1.13 | CONFIRMED | Hence not Figma's linear dodge. |
| 14 | `globalAlpha` setter returns on infinite, NaN or outside 0.0-1.0; initial 1.0 | Co 4.2 | WHATWG `source`, CanvasCompositing | CONFIRMED | Re-measured: 1.5 and NaN ignored; `null` gives 0. |
| 15 | `globalCompositeOperation` setter: a value not identical to a grammar value is ignored, so the match is case-sensitive and untrimmed | Co 4.2, 6e | the same | CONFIRMED | Re-measured: `Multiply`, ` screen`, `plus-lighter`, `linear-burn`, `destination` each left `multiply` in place; `lighter` accepted. |
| 16 | The getter returns the operator as set, so `normal` should read back `normal`; Chromium reads back `source-over` | Co H3, 7 | the same; Chromium | CONFIRMED | Reproduced. Store the keyword, never trust the read-back. |
| 17 | Drawing model: render to A, convert to the colour space, multiply by global alpha, filter to B, shadow C composited with the current operator within the clip, then B within the clip | Co 4.2 | WHATWG "Drawing model" | CONFIRMED | So shadows take the shape's blend mode, and every operator acts over the whole clipping region. |
| 18 | Chromium's opaque blend results match the W3C formulas within about 1 unit of 8 bits (2 for exclusion) | Co H1, 6a | own pixel test, 9 modes | CONFIRMED | multiply 0.78, screen 0.43, color-dodge 0, color-burn 0, soft-light 0.38, exclusion 1.25, hue 0.46, luminosity 0.30, overlay 0.65 units (max over the channels). |
| 19 | Dodge of white over black gives 0 and burn of black over white gives 255 in Chromium (the W3C reading) | Co 4.4, 6a | own pixel test | CONFIRMED | 0,0,0 and 255,255,255. |
| 20 | Per-child `globalAlpha` is not group opacity; an offscreen canvas drawn with `globalAlpha` is | Co H4, 5.1 | own test | CONFIRMED | Red then green squares at 0.5 over white: per child 127,191,63; offscreen group 126,255,126 (W3C 127.5,255,127.5). |
| 21 | BCD: `ctx.filter` Chrome 52, Firefox 49, Safari 18 only behind the "Canvas Filters" preference; `globalAlpha` and `globalCompositeOperation` Chrome 1, Firefox 1.5, Safari 2 | Co 4.3 | BCD `main`, `api/CanvasRenderingContext2D.json` | CONFIRMED | Read on `main` today, not at 8.1.8. Edge and the CSS rows of the table were not re-read. |

### Compositing: PDF, SVG and CSS

| # | Fact | Note | Source re-read | Verdict | Remark |
|---|---|---|---|---|---|
| 22 | PDF blend names: Normal, Compatible, Multiply, Screen, Overlay, Darken, Lighten, ColorDodge, ColorBurn, HardLight, SoftLight, Difference, Exclusion (Table 136); Hue, Saturation, Color, Luminosity (Table 137) | Co 4.4, Pr 2.8 | ISO 32000-1:2008, 11.3.5 | CONFIRMED | |
| 23 | The 2008 ColorDodge has only "cs < 1" and "cs = 1" cases, ColorBurn only "cs > 0" and "cs = 0": no Cb = 0 or Cb = 1 case | Co 4.4, 7 | Table 136 | CONFIRMED | So the W3C and PDF 2008 disagree at those two corners, as the note says. |
| 24 | SoftLight D(x) for x > 0.25 reads "x" in the extracted text (the radical lost) | Co 4.4 | Table 136, this reader's own extraction | CONFIRMED as S | The same extraction also drops Difference's absolute-value bars ("cb - cs"), a second sign that glyphs are lost. sqrt rests on the W3C text. |
| 25 | `BM` is a name or an array; the first mode in the array that the reader recognises is used | Co 4.4 | Table 58; 11.6.3 | CONFIRMED | 11.6.3 adds "or Normal if it recognizes none". |
| 26 | Setting a soft mask replaces the previous one, it does not intersect | Co 4.4 | Table 58, `SMask` | CONFIRMED | |
| 27 | Soft-mask dictionary: `S` required, Alpha or Luminosity, no default; `G` required; `BC` default black (only for Luminosity); `TR` default Identity | Co H7, 4.4 | Table 144 | CONFIRMED | |
| 28 | Outside the group's bounding box the mask is TR(0) for Alpha, and TR of the BC backdrop's luminosity for Luminosity | Co 4.4 | 11.6.5.2 | CONFIRMED | |
| 29 | For DeviceRGB the soft-mask luminosity is Y = 0.30 R + 0.59 G + 0.11 B, on device values, no gamma | Co 4.4, 4.5, 7 | 11.5.3 | NOT CONFIRMED as a rule | The normative text says a device colour is converted to grey "by implementation-defined means", with no gamma compensation. The 0.30/0.59/0.11 formula is given only in NOTE 3 as an example. For a CIE-based group colour space, Y of CIE XYZ is used. So a PDF reader is not bound to these weights. |
| 30 | Transparency group attributes: `/S /Transparency`, `/CS`, `/I` default false, `/K` default false | Co 4.4 | Table 147 | CONFIRMED | |
| 31 | Difference and Exclusion are the only separable modes that are not white-preserving | Co 4.4 | 11.7.4.2, NOTE 2 | CONFIRMED | |
| 32 | `mask-type: luminance \| alpha`, initial luminance | Co H7, 4.5 | CSS Masking 1, 9.2 | CONFIRMED | |
| 33 | Luminance mask: to linearRGB only when `color-interpolation` says so, then the feColorMatrix luminance-to-alpha coefficients on non-premultiplied values, times alpha | Co 4.5 | CSS Masking 1, 7.10.1 | CONFIRMED | Masking cites the coefficients "as defined in ... [SVG11]", which are 0.2125, 0.7154, 0.0721 (SVG 1.1 filters page, re-read); Filter Effects 1 gives 0.2126, 0.7152, 0.0722. Both as the note says; the difference is below 0.0003. |
| 34 | A clip path is a 1-bit silhouette "with the possible exception of anti-aliasing along the edge" | Co 4.5 | CSS Masking 1, 6.1 | CONFIRMED | |
| 35 | SVG 2: group opacity is rendered into an RGBA offscreen image | Co 4.5 | SVG 2 render.html | CONFIRMED | |

### Figma, Penpot and the other open implementations

| # | Fact | Note | Source re-read | Verdict | Remark |
|---|---|---|---|---|---|
| 36 | `BlendMode` has 19 values: PASS_THROUGH, NORMAL, DARKEN, MULTIPLY, LINEAR_BURN, COLOR_BURN, LIGHTEN, SCREEN, LINEAR_DODGE, COLOR_DODGE, OVERLAY, SOFT_LIGHT, HARD_LIGHT, DIFFERENCE, EXCLUSION, HUE, SATURATION, COLOR, LUMINOSITY | Co H6, Pr H-a | plugin-api.d.ts 5536-5555 (package 1.142.0) | CONFIRMED | |
| 37 | Help lists the modes in that order with the names Plus darker and Plus lighter; Pass through is the default for layers, Normal for fills and effects; Pass through cannot be set on fills or effects; Normal on a parent stops the children's modes at the parent | Pr 2.2, 10.1 | help 360040667874 (updated 2026-11-03) | CONFIRMED | |
| 38 | A blend mode applies to a layer, to each fill or stroke fill, and to inner shadow, drop shadow and noise effects, one per item; not to fills that use a colour style | Pr 2.2 | the same | CONFIRMED | |
| 39 | Layer opacity and fill opacity are separate | Pr 2.2, 10.2 | typings `MinimalBlendMixin.opacity` ("as shown in the Layer panel"); `SolidPaint.opacity` (default 1) | CONFIRMED | |
| 40 | A mask sits below what it masks and applies to every sibling above it until another mask or mask object, the end of its parent frame or group, or a frame or component with clip content | Pr 2.3, 10.3; Co 4.6 | help 360040450253 (updated 2026-11-06); typings `isMask` ("masks its subsequent siblings") | CONFIRMED | |
| 41 | Mask types Alpha, Vector, Luminance; default Alpha; a black luminance mask reveals nothing; Use as mask creates a mask group; masks move and resize independently (siblings) | Pr 2.3 | the same; typings `MaskType`, `maskType` default "ALPHA" | CONFIRMED | |
| 42 | Small nudge 1, big nudge 10, in points; arrows use the small nudge, Shift the big one | Pr 2.4, 10.8 | help 4404575206295; 360039956914 | CONFIRMED | The nudge article gives the values only; the Shift binding is in the alignment article. |
| 43 | Align: one layer aligns to its parent; several to one another; Shift-click aligns them as a group to the parent frame | Pr 2.4, 10.7; L 17 | help 360039956914 | CONFIRMED | |
| 44 | Distribute needs more than one layer, keeps the outermost objects, one axis at a time; up to 1 px of rounding with pixel snapping, decimals (7.5) without | Pr 2.4; L 18, 10.9 | the same | CONFIRMED | Which box is "outermost" for a wide box is not stated, as the note says (stays U). |
| 45 | Tidy up uses the most common spacing (the mode) and arranges from the selection's top-left | Pr 2.4; L 19 | the same | CONFIRMED | |
| 46 | Snap to objects aligns "the centers and outermost points"; a red guide shows; Control suspends snapping | Pr 2.4; L 23 | the same | CONFIRMED | No equal-spacing snap or threshold is documented (U, as the notes say). |
| 47 | Selection: a click selects the parent; double-click or Enter one level down; Shift+Enter the parent; Cmd/Ctrl-click deep select; selecting a top-level frame keeps the selection to top-level layers | Pr 2.1, 10.5 | help 360040449873 | CONFIRMED | |
| 48 | Lock: no move or interaction on the canvas, still selectable in the Layers panel and the Select layer menu (padlock); locking a parent locks its children, which cannot be unlocked alone | Pr 2.1, 5 | help 360041596573 | CONFIRMED | |
| 49 | Hide: not selectable on the canvas, not even through Select layer; selectable and editable in the Layers panel | Pr 2.1 | help 360041112614; 360040449873 | CONFIRMED | |
| 50 | Groups take their children's combined dimensions and follow them; the first click selects the whole group | Pr 2.1, 10.4 | help 360039832054 | CONFIRMED | |
| 51 | Constraints default to Top and Left | Pr 2.1 | help 360039957734 | CONFIRMED | |
| 52 | Frame "Clip content" hides what extends beyond the frame | Pr 2.1, 10.4 | help 360041539473 | CONFIRMED | Its default for a new frame is still not stated (U). |
| 53 | Text: a single click gives Auto width, click-and-drag gives Fixed size; resizing by hand sets Fixed | Pr 2.1, 10.10 | help 27378154668951 | CONFIRMED | |
| 54 | Image fill modes: Fill, Fit, Crop, Tile (four) | Pr 2.1, 10.10 | help 360041098433 | CONFIRMED | |
| 55 | Star point count from 3 to 60 | Pr 2.1, 10.11 | help 360040450133 | CONFIRMED | |
| 56 | A Fill child makes a Hug parent Fixed on that axis | L 6, 10.2; Pr 2.4 | help 360040451373, note under resizing | CONFIRMED | |
| 57 | Auto gap Between, Evenly, Around "match" space-between, space-evenly, space-around; with too-large objects the gap stops at 0 | L 2, 10.3 | help 31289464393751 | CONFIRMED | |
| 58 | A frame can no longer be sized smaller than its own padding | L 4, 10.4 | the same | CONFIRMED | |
| 59 | A hidden layer leaves the auto layout; use 0 % opacity to keep its gap | L 8, 10.5 | the same | CONFIRMED | |
| 60 | Negative spacing: the last object is on top by default; `itemReverseZIndex` puts the first on top | L 3, 10.6 | the same; typings | CONFIRMED | |
| 61 | `counterAxisSpacing` must be positive; `itemSpacing` may be negative | L 2, 10.6 | typings 8114; help 31289464393751 | CONFIRMED | The typings say "must be positive" for the counter axis only; negative main spacing is documented in the help, not in the typings. |
| 62 | `layoutGrow` takes only 0 and 1 | L 6 | typings 8542 | CONFIRMED | |
| 63 | `primaryAxisAlignItems` MIN, MAX, CENTER, SPACE_BETWEEN, SPACE_EVENLY, SPACE_AROUND; `counterAxisAlignItems` MIN, MAX, CENTER, BASELINE | L 5 | typings 7966, 8049 | CONFIRMED | |
| 64 | `layoutWrap` only on HORIZONTAL or VERTICAL; `counterAxisAlignContent` AUTO (stretch only if every child stretches) or SPACE_BETWEEN (tracks sized by their largest child) | L 1, 7, 10.7 | typings 7873-7879, 8050-8060 | CONFIRMED | |
| 65 | Penpot shape types: frame, group, bool, rect, path, text, circle, svg-raw, image | Pr 2.5 | `shape.cljc` 71-80 | CONFIRMED | |
| 66 | Penpot blend modes: exactly the W3C 16, no pass-through | Pr 2.5, 10.1 | `shape.cljc` 82-98 | CONFIRMED | |
| 67 | Penpot has `:opacity`, `:blend-mode`, `:masked-group`, `:show-content`, `:fill-opacity`, grow types auto-width, auto-height, fixed | Pr 2.5 | `shape.cljc` 115, 278-306, 366, 648 | CONFIRMED | |
| 68 | Penpot mask: a group with `:masked-group`; its first child (the bottom) is the mask, the rest are masked; the mask filter floods white `in` the source graphic (alpha mask) | Pr 2.5, 10.3 | `helpers.cljc` 62-65; `group.cljs` 24-31; `mask.cljs` 80-86 | CONFIRMED | |
| 69 | Penpot frames clip unless `:show-content` | Pr 2.5 | `frame.cljs` 34-36 | CONFIRMED | |
| 70 | Penpot help: constraints default Scale; align moves to the edge of the top-most element; the lowest layer becomes the mask | Pr 2.5 | help.penpot.app layers | CONFIRMED | |
| 71 | Penpot `snap-accuracy 10`, `snap-distance-accuracy 20`, both divided by zoom; the final pick is `(reduce min ##Inf snap-list)` | L 26 | `snap.cljs` 25, 27, 98, 146, 208 | CONFIRMED | Whether that is a defect was not run. |
| 72 | Excalidraw `SNAP_DISTANCE = 8`, divided by zoom; gap list capped at 99 999 per axis; MIT | L 24, Pr 2.6 | `snapping.ts` 41, 45, 49; LICENSE | CONFIRMED | |
| 73 | Excalidraw distribute: sort by centre; step = (extent - span)/(n - 1); a negative step switches to centres | Pr 2.6 | `distribute.ts` 23-55 | CONFIRMED | |
| 74 | tldraw `snapThreshold: 8` (options.ts 346), divided by zoom (SnapManager.ts 61); gap snaps `gap_center` and `gap_duplicate` | L 25 | the files at 69f4395 | CONFIRMED | Method only (licence). |
| 75 | Inkscape align targets last, first, biggest, smallest, page, page margin, page bleed, drawing, selection (default selection); distribute needs 2 or more; "gap" mode sorts by centre and spans first min to last max | L 20 | `actions-object-align.cpp` 51-132, 293-390 | CONFIRMED | |

### Layout: CSS flexbox

| # | Fact | Note | Source re-read | Verdict | Remark |
|---|---|---|---|---|---|
| 76 | 9.7: clamp min and max; total violation zero freezes all, positive freezes the min violators, negative the max violators; repeat | L 11, 10.1 | `Overview.bs` 4163-4190 | CONFIRMED | |
| 77 | 9.3: collect items until the next would not fit; a first item that does not fit goes alone; zero-sized items join the previous line even when it is exactly full | L 12, 10.8 | `Overview.bs` 3834-3855 | CONFIRMED | Re-measured: four 100 px boxes in 300 px wrap 3 + 1. |
| 78 | space-between falls back to safe flex-start, space-around (and space-evenly) to safe center, when free space is negative | L 13 | `Overview.bs` 2997, 3018 | CONFIRMED | Re-measured: first of three 60 px boxes in 150 px at x = 0 for between, around, evenly and safe center; -15 for center. The fallback also applies to a single item, so a single child under space-around or space-evenly is centred in CSS, while Figma puts one child in an Auto stack at the start: the app must follow Figma's rule in code, not CSS's. |
| 79 | Fill as `flex: 1 1 0`: [min 100, free] in 300 gives 150, 150; [free, max 110, max 50] gives 140, 110, 50 | L 6a, H3 | own Chromium run | CONFIRMED | Figma's own arithmetic stays U, as the note says. |

### Pages: ISO, ANSI, Architectural

| # | Fact | Note | Source re-read | Verdict | Remark |
|---|---|---|---|---|---|
| 80 | ISO 216:2007, second edition, cover date 2007-09-15, replaces ISO 216:1975 | M 4.1 | iTeh preview, cover and foreword | CONFIRMED | The stage 90.20 status was not re-read (S). |
| 81 | A0 has area 1 m^2, x = 0.841 m, y = 1.189 m; the B series is the geometric means of adjacent A sizes | M 4.1 | clauses 4.3, 4.4 | CONFIRMED | |
| 82 | Table 1: A0 841 x 1189 ... A10 26 x 37, 2A0 1189 x 1682, 4A0 1682 x 2378; Table 2: B0 1000 x 1414 ... B10 31 x 44 | M 4.1, 11 | Tables 1 and 2 | CONFIRMED | All 24 values as in the note. |
| 83 | No rounding rule is stated in clauses 1-6 | M 4.1 | clauses 4-6 | CONFIRMED | Kuhn says only "a rounded number of millimeters". |
| 84 | Rounding A0 and B0 to the mm, then each next size = (floor(long/2), short), reproduces all 22 table sizes; plain rounding of the exact sizes gets 6 A and 6 B wrong; halving rounded to the nearest gets 10 A and 8 B wrong | M H1, 6.1 | own script | CONFIRMED | With round-half-up. Under round-half-even, B8's exact short side 62.5 rounds to 62 and matches, so plain rounding gets 5 B wrong. The note's script used half-up; say so if the count is quoted. |
| 85 | ISO 5457: 20 mm margin on the left including the frame (a filing margin), 10 mm on the others; frame a continuous 0.7 mm line | M 4.2, 11 | ISO 5457:1999 (FR) 4.2 | CONFIRMED | |
| 86 | Title block per ISO 7200; A3 to A0: bottom right of the drawing space, landscape only; A4: on the short (bottom) side, portrait only; the drawing reads as the title block; size designation at the right of the bottom margin | M 4.2, 7, 11 | 4.1; text after Figure 2 | CONFIRMED | |
| 87 | Drawing spaces A0 821 x 1159, A1 574 x 811, A2 400 x 564, A3 277 x 390, A4 180 x 277 (plus or minus 0.5); untrimmed A0 880 x 1230 ... A4 240 x 330 (plus or minus 2) | M 4.2, 11 | Table 1 | CONFIRMED | |
| 88 | Centring marks: four, symmetric within 1 mm, recommended 0.7 mm lines from the sheet's edge to 10 mm past the frame | M 4.2 | 4.3 | CONFIRMED | |
| 89 | Grid: 50 mm fields from the centring marks; letters top to bottom without I and O, numbers left to right, on opposite sides (A4: top and right only); 3.5 mm characters, 0.35 mm lines; remainder to the edge fields; Table 2 A0 24 x 16, A1 16 x 12, A2 12 x 8, A3 8 x 6, A4 6 x 4 | M 4.2, 11 | 4.4; Table 2 | CONFIRMED | |
| 90 | IS 11665:2009 is identical with ISO 7200:2004 | M 4.3 | IS 11665 foreword | CONFIRMED | |
| 91 | ISO 7200 Tables 1-3: the fields, their subclauses, recommended characters and obligations as in the note's table | M 4.3, 11 | IS 11665 Tables 1, 2, 3 | CONFIRMED | Every row and figure in the note's table matches. |
| 92 | "seven mandatory fields" | M 1 (abstract) | IS 11665 Tables 1-3 | NOT CONFIRMED | There are eight: legal owner, identification number, date of issue, segment/sheet number, title, approval person, creator, document type. The note's own table marks these eight; only the abstract's count is wrong. |
| 93 | The title block is 180 mm wide, to fit A4 with a 20 mm left and 10 mm right margin | M 4.3, 11 | IS 11665, text by Figures 1-2 | CONFIRMED | |
| 94 | Revision index A to Z, then AA, AB ..., or 1, 2, 3; avoid I and O; scale and projection symbol are shown outside the title block, only when used | M 4.3 | IS 11665 5.1.4, 5 | CONFIRMED | |
| 95 | ANSI A 8.5 x 11, B 11 x 17, C 17 x 22, D 22 x 34, E 34 x 44 in, halving with ratios 1.2941 and 1.5455 | M 4.4, 11 | Wikipedia ANSI/ASME Y14.1 table; QGIS `qgspagesizeregistry.cpp` 48-52 (215.9 x 279.4 ... 863.6 x 1117.6 mm) | CONFIRMED as S | ASME Y14.1 itself not read (sold). |
| 96 | Arch A 9 x 12, B 12 x 18, C 18 x 24, D 24 x 36, E 36 x 48, E1 30 x 42 in; QGIS stores E2 660 x 965 and E3 686 x 991 mm | M 4.4, 11 | Wikipedia "Paper size" (citing sizes.com); QGIS registry 53-60 | CONFIRMED as S | Exact mm in QGIS for A to E1. Which standard defines them stays U. |
| 97 | JIS B0 1030 x 1456, B4 257 x 364, B5 182 x 257 | M 4.6, 11 | Wikipedia JIS B table; Kuhn | CONFIRMED as S | Kuhn gives JB4 and JB5 and the 1.5 m^2 area, not JB0's sides: B0 rests on Wikipedia alone. |
| 98 | QGIS's page registry: A6-A0, B6-B0, Legal, Letter, ANSI A-E, Arch A-E3, three pixel screen sizes, all stored portrait; no A7-A10, B7-B10 | M 4.7 | `qgspagesizeregistry.cpp` 32-63 | CONFIRMED | |
| 99 | The app's `ANSI-D` and `ANSI-D-L` (609.6 x 914.4) are Arch D; ANSI D is 558.8 x 863.6 mm | M H3, 6.1; A 2 | `sheets.js` 41, 44; rows 95, 96 | CONFIRMED | |

### Map surround: north arrow, scale bar, legend, convergence

| # | Fact | Note | Source re-read | Verdict | Remark |
|---|---|---|---|---|---|
| 100 | ArcGIS: a north arrow takes the last selected map frame; Map North, True North (by the map's coordinate system at the frame's centre), Magnetic North (World Magnetic Model); Calibration Angle positive counterclockwise, negative clockwise; read-only Calculated Angle | M 4.10, 11 | pro 3.5 north-arrows | CONFIRMED | |
| 101 | QGIS: arrow rotation = map rotation + map item rotation; Grid north (enum 0, the default) adds nothing; True north adds the bearing found by moving the point 0.000001 degree north; then the offset is added | M 4.10, 11 | `qgslayoutnortharrowhandler.cpp` 50-81, `.h` 40, 110; `qgsbearingutils.cpp` 49 | CONFIRMED | |
| 102 | ArcGIS scale bar: by default the scale at the equator; Compute at center; five fitting strategies (adjust division value, adjust number of divisions, adjust divisions and division value, adjust width, fixed bar width) | M 4.11 | pro 3.5 scale-bars | CONFIRMED | |
| 103 | QGIS scale bar defaults: 2 segments right, 0 left, 1 subdivision, Fixed size mode, fit range 50 to 150 mm, height 3 mm | M 4.11 | `qgsscalebarsettings.h` 641-650 | CONFIRMED | |
| 104 | QGIS `calculatePrettySize`: returns 0 when max < min; nextNice and prevNice at d = 1, 10, 100 ... until one falls in [min, max]; the larger if it fits; the comment's 4573.23 examples | M 4.11, 6.2 | `qgslayoututils.cpp` 452-492 | CONFIRMED | |
| 105 | ArcGIS legend sync: Layer visibility on, Layer order off, New layer on, Reference scale on, by default; "Display only when populated" | M 4.9, 11 | pro 3.5 work-with-a-legend | CONFIRMED | |
| 106 | QGIS legend: `default-legend-sync-mode` defaults to Visible layers; Visible layers uses the map's `layersToRender`; `setAutoUpdateModel` maps to All project layers or Manual | M 4.9 | `qgslayoutitemlegend.cpp` 110, 393-438 | CONFIRMED | |
| 107 | Spherical convergence gamma = atan(tan(dlon) sin(lat)) | M 4.10, 11 | Wikipedia "Transverse Mercator projection", Convergence | CONFIRMED as S | |
| 108 | Karney (2011): gamma = gamma' + gamma'', gamma' = atan(tau'/sqrt(1 + tau'^2) tan(lambda)), gamma'' = atan(q'/p'), the bearing of grid north clockwise from true north | M 4.10, 11 | arXiv 1002.1417, forward convergence equations | CONFIRMED | |
| 109 | e03's values; the spherical formula is within 0.05 arcsec of the ellipsoidal one | M 4.10, 6.3 | own script against NGS NCAT | CONFIRMED | NGS (NAD83(2011), zone 18): 40 N 72 W 1.929408 deg; 60 N 2.598672; 80 N 2.954506; 39.9524 N 75.1636 W -0.105056; 39.9526 N 74 W 0.642192. Own Krueger series within 0.005 arcsec of NGS; spherical within 0.04 arcsec. The note's "39.95 N, 1 degree east" row is at 39.9526 N (at exactly 39.95 N, NGS gives 0.642158). |
| 110 | Convergence changes about 27 arcsec across 1 km east-west at Philadelphia | M H7, 4.10 | arithmetic: 1 km / (6 378 137 cos 40) x sin 40 | CONFIRMED | 27.1 arcsec. |

### The app's code (`src/`, read at HEAD 47a501a)

| # | Fact | Note | Source re-read | Verdict | Remark |
|---|---|---|---|---|---|
| 111 | `SHEET_SIZES` at `sheets.js` 34-48 (eleven keys), `SHEET_NEW_SIZE = 'ANSI-B-L'` at 50 | A 2; M 8 | `sheets.js` | CONFIRMED | M's "34-49" includes the closing brace. |
| 112 | `SHEET_SCALES` 1:1 to 1:5000, 16 steps, at 54-59; 3 px/mm on screen, 6 for export at 60 | A 1, 2 | `sheets.js` | CONFIRMED | |
| 113 | `bimNewSheet` at 63-68 gives `{id, number, name, sizeKey, w, h, viewports[]}` | A 1; M 8 | `sheets.js` 63-67 | CONFIRMED | |
| 114 | `A3D.pres = {boards[], order[]}`; a board `{id, kind, figs?, off?, name?}` | A 1 | `boards.js` 28-38 (`bimPresValid`); `board-figures.js` 90-101 (`bimBrdKeep`) | CONFIRMED | A's range "board-figures.js:63-101" is wider than needed; the fields are set at 90-101. |
| 115 | The board grid is 1408 px wide, gutter 12, column (1408 + 12)/12 | A 1 "board-figures.js:19"; L 8 "line 20" | `board-figures.js` | CONFIRMED (value); A's line NOT CONFIRMED | The declaration is at line 20, as L says; line 19 is the end of a comment. |
| 116 | A catalogue of 33 figures at 25-46 | A 1 | `bimFigCat` 25-49 | CONFIRMED | 32 figures and `text`. |
| 117 | `bimBrdFigsValid`: at most 80 figures; w 1 to 12, x 0 to 12 - w, h 0.25 to 400, y 0 to 4000, 4 decimals; figure `{k, f, x, y, w, h, o}` | A 1; L 8 | `board-figures.js` 61, 70-88 | CONFIRMED | |
| 118 | `bimBrdBands` 154-168, `bimBrdOverlaps` 171-179, a figure drawn at `left:x*P; width:w*P-G` (202), `bimBrdMeasurer` and `bimBrdMeasureDefault` 343-367 | L 8 | `board-figures.js` | CONFIRMED | |
| 119 | `board-edit.js` 19-27, the Edit header (12 px, Grid, Ortho, phone reading order); `bimBrdOrder` at 38 | A 1, 6; L 8 | `board-edit.js` | CONFIRMED | |
| 120 | `bimBrdSnap` 104-133: threshold `A3D_SNAP.pxThreshold/(BIM_BRD_P0*(z\|\|1))` (105); Ortho zeroes the smaller of dx, dy (106); nearest pair within the threshold (109-113); move snaps both edges, resize the right and bottom; Grid rounds where no snap caught; clamps and 1e-4 rounding (121, 129, 131) | L 8; A 6 | `board-edit.js` | CONFIRMED | Detail: horizontal targets are 0, 12 and other figures' edges; vertical targets are 0 (the board's top) and other figures' edges only, no board bottom. |
| 121 | `bimBrdGuides` 135-145; pointer, key and nudge handling 147-224 | A 1; L 8 | `board-edit.js` | CONFIRMED | `bimBrdDown` 147 to `bimBrdKey` 210-225. |
| 122 | `A3D_SNAP={point:true,grid:false,gridSize:0.5,ortho:false,pxThreshold:12}` | L 8; A 6 | `plan-mode-sketch.js` 41 | CONFIRMED | |
| 123 | `UNDO_MAX = 50`; `bimSnapshotState` is one `JSON.stringify` of the project state including `sheets` and `pres` | A 6 | `plan-mode-sketch.js` 289-298 | CONFIRMED | |
| 124 | The image note refuses files over 4 MB and reads a data URL | A 6 | `annotation-overlay.js` 230-240 | CONFIRMED | |
| 125 | `bimDrawTitleBlock` at 367: min(90 mm, 42 % W) by min(28 mm, 22 % H); `bimBuildTitleBlockSVG` at 738 | A 3 | `sheets.js` 367-370; `viewports.js` 736-761 | CONFIRMED | The SVG twin ends at 761, not 764. |
| 126 | `bimRenderSourceToCanvas` 250-297 sets `A3D.sheetCapture` and restores it; `bimCompositeViewport` 327-366 | A 4 | `sheets.js` 250, 281, 287, 327 | CONFIRMED | |
| 127 | viewports.js: wheel 121, drag 205-262, New Sheet dialog 274-306, PNG 489, SVG 765-824, print 826-910, `bimPrintSetHtml` 848; `pages-display.js` 83-128 | A 1, 2 | the files | CONFIRMED | Function starts as stated. `present.js` 154 is `bimSlideshowBoard`. |
| 128 | Site layers stop under `sheetCapture` or a plot: `find-open-data.js` 321-323, `colour-lens.js` 201, `layer-cake.js` 77, `map-tiles.js` 265 and 304 (plot only), `model-analyses.js` 32 | A 4 | the files | CONFIRMED | |
| 129 | `drawNorthArrow` draws only in plan, turning (sin tn, -cos tn) through the camera | A 4, 5 | `property.js` 130-150 (133-134) | CONFIRMED | |
| 130 | `bimTrueNorthDeg` at `survey-arithmetic.js` 5-8; `bimSetTrueNorth` at `alignment-profile.js` 650-658: one undo step, normalised to (-180, 180] | A 5; M 4.10, 8 | the files | CONFIRMED | M says "kept in -180 to 180"; the code keeps +180 and maps -180 to 180. |
| 131 | `bimModelToGeo` rotates by true north and converts with the meridian and prime-vertical radii (a local tangent plane) | M H5, 4.10, 8 | `map-tiles.js` 59-65 | CONFIRMED | Lines are 59-65, not 57-64. |
| 132 | CityJSON writes UTM (k0 0.9996, Krueger series) | M 4.10, 8 | `cityjson.js` 24-42 | CONFIRMED | |
| 133 | Zoning board scale bar: ladder 1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000 m, the largest within maxW, called with W/4; north arrow from true north at 778-780 | A 5; M 4.11, 8 | `zoning-envelope.js` 607-613, 778-781 | CONFIRMED | A's "606-612" is one line early (606 is the comment). |
| 134 | Access board scale bar: "25 to 5000 m", the largest under a fifth of the width, km from 1000; `bimAccNorth` a fixed glyph at 73 | A 5; M 4.11, 8 | `access-board.js` 66-73 | CONFIRMED, with a detail | The ladder is 25, 50, 100, 200, 250, 500, 1000, 2000, 5000: it includes 250, which matters to the 1-2-5 versus 2.5 question (M owner decision 4). Lines 66-72; A's "65-71" is one line early. |
| 135 | Legend row builders: `bimDataSwatch` 106, `bimDataLegendHtml` 116 ("and N more" past `BIM_LENS_MAX_ROWS`), `bimDataLegendTitle` 128; `bimResSwatch` 39, `bimResLegendHtml` 46; `bimTerrainLegend` 508 | A 5; M 8 | `data-symbology.js`, `analysis-data-rows.js`, `breaklines.js` | CONFIRMED | |
| 136 | Compositing today: `globalAlpha` for layer transparency (`dimensions.js` 141), `destination-out` in `model-layers.js` 246-254; "No blend modes anywhere (`grep globalCompositeOperation`, `mix-blend-mode`: those two files only)" | A 6 | `grep -rn` over `src/` | NOT CONFIRMED as stated | No blend mode is used anywhere (right). But `globalCompositeOperation` appears in two files, neither of them `dimensions.js`: `site-analysis/model-layers.js` 246, 254, 420-424 and `site/shadows.js` 86-90 (both `destination-out` then back to `source-over`). `dimensions.js` uses `globalAlpha` only; no `mix-blend-mode` in `src/`. |
| 137 | File sizes: `viewports.js` 928, `presentation-panel.js` 819, `board-edit.js` 491, `sheets.js` 470, `board-figures.js` 389 lines | A 7 | `wc -l` | CONFIRMED | |
| 138 | The standards registry has no paper sizes yet; records carry `eds` with `src` and `v` | M 8 | `registry.js` grep | CONFIRMED | |

## Summary of verdicts

- 138 facts listed.
- CONFIRMED: 134 (rows 1-28, 30-91, 93-114, 116-135, 137-138). Of these, rows 24, 95, 96, 97 and 107 are confirmed
  as S and stay S. Rows 18-20, 79, 84 and 109 were confirmed by re-running, not only by reading. Rows 101, 104 and
  106 were confirmed by reading code, not by running QGIS.
- NOT CONFIRMED: 3 (rows 29, 92, 136).
- Split: 1 (row 115: the value is confirmed, the audit's line number is not).
- COULD NOT CHECK: 0.

Smaller corrections inside confirmed rows (no change of level): the year `destination` left the canvas grammar
(row 3, 2015 not 2014); the half-up rounding needed for "6 B wrong" (row 84); the latitude of e03's second case
(row 109, 39.9526 N); a single item under space-around or space-evenly is centred in CSS, not at the start as in
Figma (row 78); the access board's ladder includes 250 m (row 134); several app line ranges off by one or two
(rows 125, 131, 133, 134).

## Facts that go back to U

1. "For DeviceRGB the PDF soft-mask luminosity is 0.30 R + 0.59 G + 0.11 B" (Co 4.4, 4.5, 7), as a rule of PDF.
   ISO 32000-1 11.5.3 leaves device-space luminosity implementation-defined (no gamma compensation) and gives that
   formula only in an informative note. Consequence: a `/Luminosity` mask exported to PDF is not guaranteed to match
   the board in any reader; pre-baking to `/Alpha` (Co owner decision 4) is the only exact route.
2. "ISO 7200 has seven mandatory fields" (M 1). It has eight; the note's own table is right and is what code should
   use.
3. "Compositing in the app: `globalAlpha` in `dimensions.js` and `destination-out` in `model-layers.js`, those two
   files only" (A 6). `globalCompositeOperation` is also used in `site/shadows.js` 86-90. The conclusion that no blend
   mode is used anywhere stands.
4. "The board grid is at `board-figures.js:19`" (A 1). It is line 20.

## Not re-read (outside this check's list)

Canva, Adobe (refused in the notes), Revit, Archicad, SketchUp LayOut, Vectorworks, Procreate and Affinity (Pr 2.7,
2.8 except PDF, 2.11, 2.12); the Illustrator scripting constants (Pr 2.8, S); Skia's and pdf.js's code (Co 4.7, 4.6);
the Mozilla and WebKit bug reports (Co 4.7); BCD's CSS rows and MDN's prose (Co 4.3); exp. c, d and f of Co (mask,
cost and SVG parity timings) and exp. b's numbers over the blue band; Yoga v3.2.2 and Penpot's flex arithmetic
(L 15, 16, the Fill variants table); the timings of L 6c; ISO 5457:1980 and the stage statuses on iTeh; ASME's and
NSAI's store pages, NCS, the VA guide and the ARE study guide (M 4.4, 4.5); NOAA NGS 5 and Snyder (M 4.10); the WMM
page; ArcGIS's map frame and constraint pages and QGIS's manual pages for map items (M 4.8); QGIS's legend filter
by map and its scale-bar initial units (M 4.9, 4.11). If code is to rest on any of them, they need a reading of
their own.
