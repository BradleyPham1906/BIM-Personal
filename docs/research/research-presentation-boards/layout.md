# V174 research: layout algorithms for boards (auto layout, align and distribute, smart spacing)

Date: 2026-11-08. Research agent 4 of V174 "Presentation P1: boards". Scope: the algorithms behind "align,
distribute, smart spacing; rows and columns that space their children (a light auto layout)" on boards,
with the app's Snap, Grid and Ortho. It follows `docs/research/research-protocol.md`. Levels: **P** primary
(the vendor's own document, the specification, the code read as text, or measured here); **S** secondary,
with the gap said; **U** a search summary, a forum post or our own reading without a check, never used by
code until confirmed.

Experiments: `docs/research/experiments/v174-layout/` (our own ES5: `autolayout.js`, `align.js`,
`spacing-snap.js`; the runners `compare-chromium.js`, `probe-overflow.js`, `fill-variants.js`,
`run-align.js`; their output in the `.txt` files beside them). Downloaded upstream files were kept in the
session scratchpad (`dl-layout/`), read as text only; none was run.

## 1. Abstract

The question: what minimal layout model should boards get so that rows and columns space their figures,
and align, distribute and equal-spacing snaps behave as designers expect from Figma, without breaking the
build contract (ES5, no dependencies) or the board's print and phone views? The answer: a Figma-like
subset (row or column, wrap, numeric or auto gap, padding, main and cross alignment, Fixed, Hug and Fill
with min and max, hidden and absolute children) is about 11 KB of ES5, deterministic, and on 39 of 39 cases
where Figma's documented rule and CSS flexbox should agree it matched Chromium 153's flexbox to 0.01 px;
the two cases where Figma documents a different rule (a Hug frame with a Fill child) differ as expected.
Fill must follow css-flexbox-1's freeze loop, not Yoga's two passes (they differ by 15 px on a measured
case) and not Penpot's grow-from-min (differs whenever a min applies). Align and distribute work on
axis-aligned bounding boxes; "equal gaps" has two readings that part when one box is much wider than the
others, and the board should keep the outermost edges (our reading of Figma). An Excalidraw-style
equal-gap snap costs a median 0.02 ms per pointer move at 200 boxes and 0.5 ms at 1000 (4-core Xeon,
Node 22), well inside a 16 ms frame; boards hold at most 80 figures. Recommendation: alternative 1 below.

## 2. The question and the hypotheses

Question: which layout rules, written in our own ES5, give boards a light auto layout, align, distribute
and smart spacing that match professional practice, stay exact in print, and run on a phone?

- **H1** A Figma-documented subset of auto layout gives the same boxes as CSS flexbox wherever Figma's text
  does not state a different rule. **Held**: 39 of 39 cases agree with Chromium 153 to 0.01 px (section 6a).
- **H2** Figma's Fill is CSS `flex: 1 1 0` (equal shares from a basis of 0, then min and max). **Held for
  CSS, not proven for Figma**: Chromium agrees with our rule; Figma's own output for these cases was not
  measured here (no Figma account in this environment). Supported by Figma's statement that wrap breaks a
  Fill row only with a min width (forum, U) and by Dev Mode emitting `flex: 1 0 0` (one secondary blog, U).
- **H3** Yoga and Penpot share space among Fill children as the specification does. **Falsified**: Yoga
  v3.2.2's two passes (its own comment says it "deviates from the spec") leave 15 px unshared on
  [free, max 110, max 50] in 300 px; Penpot's distribute-space differs on any case where a min applies
  ([min 100, free] in 300: Penpot 200/100, spec 150/150) (section 6, `fill-variants.txt`).
- **H4** "Distribute horizontal spacing" has one definition. **Falsified**: Inkscape sorts by centre and
  spans first-min to last-max, which moves the outermost box when a wide box's centre is not last;
  Figma says the outermost objects keep their positions. Same answers on ordinary rows (section 6b).
- **H5** An equal-gap snap search over every pair of boxes fits a pointer-move budget (4 ms on a desktop
  core, so a phone at 4 to 8 times slower stays under a frame) up to 1000 boxes. **Held**: p95 0.75 ms at
  1000 boxes, gap index built once per drag in 14 to 53 ms (section 6c).
- **H6** The board's Snap can take equal-gap snaps without a new threshold. **Held** (design): the board
  already converts the drawing's 12 px `pxThreshold` into column units at the current zoom
  (`board-edit.js` line 105); Excalidraw (8 px), tldraw (8 px) and Penpot (10 px point, 20 px distance)
  all divide a screen-pixel threshold by zoom the same way.

## 3. Method

### Search log

| # | Where | Query or path | Result | Kept |
|---|---|---|---|---|
| 1 | help.figma.com | 360040451373 "Guide to auto layout in Figma" | 200 (via 301) | read in full |
| 2 | help.figma.com | 31289464393751 "Use the horizontal and vertical flows in auto layout" | 200 | read in full |
| 3 | help.figma.com | 5731482952599, 31289469907863 (toggle, grid) | 200 | grid set aside (out of scope) |
| 4 | raw.githubusercontent.com | figma/plugin-typings master `plugin-api.d.ts` (1.142.0), LICENSE (MIT) | 200 | auto layout fields read |
| 5 | web search | Figma dev mode "fill container" "flex: 1 0 0" | one blog (zenn.dev), others differ | U only |
| 6 | web search | Figma wrap "fill container" "min width" | forum posts | U only |
| 7 | help.figma.com | 360039956914 alignment, distribution, tidy up | 200 | read |
| 8 | help.figma.com | 360039956974 measure distances; 360040450233 smart selection | 200 | read |
| 9 | web search | Figma smart guides red lines spacing | pointers to #8 and forum | forum set aside |
| 10 | www.w3.org | TR/css-flexbox-1 (CR, dated 14 October 2025 in the page) | 200 | edition noted |
| 11 | raw.githubusercontent.com | w3c/csswg-drafts main `css-flexbox-1/Overview.bs` | 200 | 9.3 line collection, 9.7, justify-content read |
| 12 | api.github.com, gh | facebook/yoga tags; penpot, tldraw | 403 (session not bound to these repos) | refused; used `git ls-remote` |
| 13 | git ls-remote | facebook/yoga tags; excalidraw, penpot, tldraw HEAD | latest semver tag v3.2.2; heads 701b901, 904cdd9, 69f4395 | pinned |
| 14 | raw.githubusercontent.com | yoga v3.2.2 `yoga/algorithm/{CalculateLayout.cpp, FlexLine.cpp, Align.h, BoundAxis.h}`, LICENSE (MIT) | 200 | read |
| 15 | raw.githubusercontent.com | penpot 904cdd9 `common/src/app/common/geom/shapes/flex_layout/{layout_data,positions,bounds,modifiers}.cljc`, `frontend/src/app/main/snap.cljs`, `.../viewport/snap_distances.cljs`, LICENSE (MPL-2.0) | 200 (one path 404) | layout_data and snap read |
| 16 | raw.githubusercontent.com | excalidraw 701b901 `packages/excalidraw/snapping.ts`, LICENSE (MIT) | 200 | read |
| 17 | raw.githubusercontent.com | tldraw 69f4395 LICENSE.md, `packages/editor/src/lib/editor/managers/SnapManager/{SnapManager,BoundsSnaps}.ts`, `options.ts` | 200 | licence read first; method only |
| 18 | gitlab.com raw | inkscape master `src/actions/actions-object-align.cpp` (GPL-2+) | 200 | method only |
| 19 | inkscape-manuals.readthedocs.io | align-and-distribute (Beginners' Guide 1.3) | 200 | read; thin |
| 20 | helpx.adobe.com | Illustrator and InDesign align and distribute pages (curl, WebFetch, headless Chromium) | 403 every time | refused |
| 21 | creativepro.com | align-to-key-object | 403 | refused |
| 22 | web search | Illustrator "Align to Key Object" "Distribute Spacing" | summaries of Adobe's page and forums | U only |

Refused hosts on 2026-11-08: helpx.adobe.com (403 to curl, to WebFetch and to a headless Chromium),
creativepro.com (403), api.github.com for repositories not attached to this session (403; raw files and
`git ls-remote` worked).

### Sources by kind

- Vendor documents: Figma's help centre (four articles) and its Plugin API typings (MIT).
- Specification: css-flexbox-1, W3C Candidate Recommendation as published (page dated 2025-10-14), and its
  editor's source on GitHub.
- Open implementations read as text: Yoga v3.2.2 (MIT), Penpot 904cdd9 (MPL-2.0), Excalidraw 701b901
  (MIT), tldraw 69f4395 (tldraw licence: not open source, production use needs a key; method only, no
  code taken), Inkscape master (GPL-2+, method only).
- Practitioner accounts: forum posts and blogs found by search (U; none used for code).
- Measurements: Chromium 153.0.8010.12 (Playwright's build in `/opt/pw-browsers/chromium-1243`) and
  Node v22.23.4 on a 4 vCPU Intel Xeon @ 2.10 GHz.

### Independent check

Not yet done. The facts in section 10 ("facts the code depends on") are the ones a second reader must
re-read before code.

## 4. Findings, by topic

### 4.1 Auto layout (Figma, as documented)

1. **Flows and wrap.** Horizontal, vertical and grid; wrap for horizontal and vertical only; a vertical
   wrap "behaves like CSS flexbox with flex-direction: column and flex-wrap: wrap" and is not masonry.
   `layoutWrap` can be set only on HORIZONTAL or VERTICAL frames. P (help 31289464393751; typings), high.
2. **Gap.** A number, or Auto with Between (default), Evenly, Around, which Figma says "match CSS property
   values space-between, space-evenly, and space-around". "If the objects in the frame are too large to fit
   with positive spacing, the gap will stop at 0 rather than going negative". One child in an Auto stack
   sits at the start (left or top). With wrap, one value is the gap in a row and a second the gap between
   rows (`counterAxisSpacing`, "must be positive"; `itemSpacing` may be negative). P, high.
3. **Negative gap and stacking.** Negative spacing overlaps children; the last is on top unless "First on
   top" is chosen (`itemReverseZIndex`); the layers panel order does not change. P, high.
4. **Padding.** Per side; "A frame can no longer be sized smaller than its own padding". P, high.
5. **Alignment.** One alignment for all children, set on the frame: nine positions with a numeric gap;
   with Auto gap only the cross axis (three). `primaryAxisAlignItems`: MIN, CENTER, MAX, SPACE_BETWEEN,
   SPACE_EVENLY, SPACE_AROUND; `counterAxisAlignItems`: MIN, CENTER, MAX, BASELINE (baseline on horizontal
   frames only). P, high.
6. **Resizing.** Hug (frames only), Fill (children only), Fixed, plus min and max on any auto layout frame
   or child. "If any child objects within an auto layout frame are set to Fill container, the parent frame
   will no longer hug contents and become Fixed for the axis." `layoutGrow` takes only 0 and 1, so Fill
   has no weights. P, high.
7. **Wrapped tracks.** `counterAxisAlignContent` AUTO: tracks stretch only if every child stretches,
   otherwise each track is as tall as its tallest child and the tracks align by the cross alignment
   ("like flexbox align-content: start | center | end"); SPACE_BETWEEN spreads the tracks, never below 0.
   CSS's default `align-content: normal` stretches the lines instead, so the comparison page sets
   align-content explicitly. P, high.
8. **Ignore auto layout** (formerly absolute position): the child leaves the flow, keeps its x and y and
   takes constraints. **Hidden** children leave the flow ("Toggling a layer ... visibility will hide it from
   an auto layout frame"; for a gap keep the layer at 0% opacity). P, high.
9. **Fill's exact arithmetic is not documented by Figma.** The typings say only "Object fills all available
   space". Our rule is CSS's `flex: 1 1 0` with the 9.7 freeze loop. Supporting evidence is U (a blog on Dev
   Mode's `flex: 1 0 0`; forum answers that a Fill row wraps only with a min width, which is what basis 0
   predicts, and our case "wrap fill without min stays one line" shows). Medium confidence; to confirm in
   Figma (open item).
10. **Text baseline alignment** needs font metrics; board figures have none that matter (cards with a
    heading). Left out of the subset. P for the option existing; the decision is ours.

### 4.2 CSS flexbox and the two implementations

11. **The specification's flexible lengths** (css-flexbox-1 section 9.7): targets start at the flex base
    size; free space is shared by flex factor; min and max violations are clamped; if the total violation
    is positive the min-violators freeze, if negative the max-violators, if zero all; repeat. P, high.
12. **Line breaking** (9.3): collect items until the next item's outer hypothetical main size "would not
    fit"; a first item that does not fit goes alone; zero-sized items join the previous line even when it is
    exactly full. Exact fit stays on the line (measured: four 100 px boxes in a 300 px frame give 3 on
    the first line and 1 on the second, the third ending exactly at 300). P, high.
13. **Overflow fallbacks**: space-between falls back to safe flex-start, space-around and space-evenly to
    safe center. Measured in Chromium 153: all three put the first item at x = 0 when three 60 px boxes
    overflow a 150 px line, as does `safe center`; plain `center` puts it at -15. So "safe center" on
    overflow is the start, and Figma's "gap stops at 0", the specification and Chromium agree. P (spec,
    measured), high.
14. **CSS gap cannot be negative** (css-align-3; not re-read here, S); the comparison page used negative
    margins for Figma's negative gap and agreed. Figma's negative gap is ours to implement directly.
15. **Yoga v3.2.2** resolves flexible lengths in exactly two passes (`resolveFlexibleLength`,
    `CalculateLayout.cpp` lines 900 to 972, comment: "This two pass approach for resolving min/max
    constraints deviates from the spec"); its first pass also lowers the total grow factor inside the loop,
    so the result depends on child order. Display-none and absolute children are skipped when lines are
    collected (`FlexLine.cpp`). Its fallback for space-around and space-evenly is flex-start (`Align.h`,
    with a TODO naming "safe center"). P (read), high for the text; the 15 px difference is from our
    transcription (medium: Yoga not run).
16. **Penpot 904cdd9** (`layout_data.cljc`): absolute children removed; lines broken when the running
    minimum width would exceed the layout width, with a 0.5 px tolerance (`mth/close?`); Fill children
    start at their min and take equal shares, capped at max, repeated (`distribute-space`); with Auto
    spacing the numeric gap is a floor (`max layout-gap-col ...`); wrap is off when the frame hugs that
    axis. No handling of hidden children in these files. P (read), high for the text; medium for the
    effect (not run).

### 4.3 Align, distribute, tidy up

17. **Figma align**: one layer aligns to its parent; several align to one another (or, with Shift, as a group
    to the parent). Six buttons (left, horizontal centres, right, top, vertical centres, bottom). P, high.
18. **Figma distribute**: needs more than one layer; "Figma will retain the position of the outermost
    objects"; one axis at a time. Equal spacing only (no distribute-by-centres in the panel). With pixel
    snapping it allows up to 1 px of rounding; without, decimals (7.5). P, high. Which box counts as
    "outermost" when a wide box spans past the last centre is not stated: U (our reading: least min edge
    and greatest max edge).
19. **Figma tidy up**: one dimension, sorted along the axis the boxes overlap on, "the most common spacing
    in the selection" (the mode) as the space between; two dimensions build a grid from the selection's
    top-left. Smart selection requires equal distances and overlap on an axis. P, high.
20. **Inkscape** (method only): "Relative to" Last selected, First selected, Biggest, Smallest, Page, Page
    margin, Page bleed, Drawing, Selection (default selection); align moves each item by its preferred
    bounding box; distribute needs 2 or more items; by edges or centres the first and last anchors stay and
    the rest step equally; "make gaps equal" sorts by centre and spaces from the first's min to the last's
    max (`object_distribute`). P (read), high.
21. **Illustrator and InDesign**: align to Selection, Key Object or Artboard (Illustrator; InDesign adds
    margins, page and spread); Distribute Spacing with a value needs a key object; "Use Preview Bounds"
    switches between geometric and visual (stroke) bounds. U only: helpx.adobe.com refused every client.
    Nothing in the code depends on them; the key-object idea is P in Inkscape (Last/First selected).
22. **Rotated objects**: Figma measures and aligns by "the bounding box that surrounds an object" and keeps
    x, y on the unrotated top-left (P); Inkscape uses the item's desktop bounding box (P). Board figures
    are never rotated today (`bimBrdFigsValid` keeps x, y, w, h only, P), so this is an edge for later.

### 4.4 Smart guides and smart spacing

23. **Figma** documents red measurement lines between bounding boxes (Alt or Option while hovering), red
    snap guides for "Snap to objects" (centres and outermost points), pink smart-selection handles, and
    Ctrl to suspend snapping. It does not document an equal-spacing snap, its markers or a threshold in the
    help centre: U for any Figma number.
24. **Excalidraw** (MIT, 701b901, `snapping.ts`): `SNAP_DISTANCE = 8`, divided by zoom; reference
    elements are the visible, unselected ones; gaps are every pair, sorted by x (or y), with the first's
    far edge before the second's near edge and overlapping ranges on the other axis, capped at 99 999 per
    axis; computed once and cached for the drag (`SnapCache`). Per move: point snaps to corners and centres,
    then for each gap whose overlap meets the moving box: a centre snap if the gap is wider than the box,
    else an equal gap after the gap's end box or before its start box. Ties are kept for drawing; the
    nearest offset wins; Ctrl or Cmd toggles snapping. P, high.
25. **tldraw** (method only; its licence forbids production use without a key, so no code is taken):
    threshold `snapThreshold: 8` divided by zoom (`options.ts` line 346, `SnapManager.ts` line 61); gap
    snaps of two kinds, "the center of a gap" and "a new gap of equal size to another gap", with adjacent
    equal gaps chained for the indicator (`BoundsSnaps.ts` lines 61 to 155). P (read), high.
26. **Penpot** (MPL-2.0, `snap.cljs`): `snap-accuracy 10` and `snap-distance-accuracy 20`, both divided by
    zoom; distance snaps through a range tree of the gaps among shapes to either side, with a middle snap of
    half the difference. Its final choice is `(reduce min ##Inf snap-list)`, the most negative offset rather
    than the smallest magnitude: possibly a defect, not run. P (read), medium.
27. **The app's board snap today** (P): see section 8. It snaps edges only (no centres, no gaps), 12 px
    at the board's zoom, Grid to whole columns and rows, Ortho by the larger of dx and dy.

## 5. The alternatives compared

Criteria, stated first: (a) ES5, no dependency (the build contract); (b) the same boxes on screen, in
Present and in print, and in any later SVG or PDF export (positions must be numbers we own, not a
browser's layout); (c) deterministic, so a saved board reopens identically and unit tests in Node can
check it; (d) size and the work to keep it; (e) phone (the board's narrow view is reading order);
(f) matches what designers know (Figma).

| | 1. Figma-like subset in ES5 (ours) | 2. Real CSS flexbox in hidden DOM, read back | 3. Port Yoga | 4. No auto layout: align and distribute only |
|---|---|---|---|---|
| (a) ES5, no dependency | yes (11 KB unminified, `autolayout.js`) | yes (the browser does it) | a port of about 2400 C++ lines to ES5; MIT allows it | yes (5 KB, `align.js`) |
| (b) same boxes everywhere | yes: plain numbers stored or recomputed | only where a DOM exists; Node tests and SVG export would need a browser | yes | yes |
| (c) deterministic | yes; Node unit tests run it | browser-dependent rounding and fonts; not in `npm test` without a browser | yes, but Yoga departs from the spec (H3) | yes |
| (d) cost | about 250 lines and tests; rules each sourced | small code, but every edit is a layout pass in the page; the app already does this once for default boards (`bimBrdMeasureDefault`) | large, much unneeded (RTL, aspect ratio, baseline, measure functions) | smallest |
| (e) phone | the narrow view keeps reading order; a row frame becomes a column there | same | same | nothing new |
| (f) Figma parity | documented rules, Hug-with-Fill included | flexbox, so Hug with Fill differs from Figma (6a) | flexbox with Yoga's deviations | no rows or columns that respace |
| Verdict | **recommended** | a test oracle, not the engine | no | falls short of the scope |

The recommendation follows from (b) and (c): positions are the board's own data, saved and reopened,
printed and later exported, and must be computed the same way in Node and in every browser. Chromium's
flexbox is kept as the oracle for the cases where the rules agree (the comparison script). What would
change it: if the owner wanted Figma's grid flow or text baselines, alternative 2 would grow more
attractive, since CSS grid and baselines are much larger to write.

## 6. The experiments

Environment: Node v22.23.4, linux x64, 4 vCPU Intel Xeon @ 2.10 GHz; Chromium 153.0.8010.12 headless via
the playwright package already present (`chromium.launch()`, nothing installed).

**(a) Light auto layout against Chromium's flexbox** (`node compare-chromium.js`, output
`compare-chromium.txt`). 41 cases built from the edges; each drawn as CSS in Chromium, boxes read with
`getBoundingClientRect` and compared with ours to 0.01 px.

- Expected to agree: **39 of 39 agree.** They include: row and column with gap and padding; nine-way
  alignment; Hug both axes; Figma's own example (a 40 px text with 10 px side padding hugs to 60 px);
  two Fill children sharing 290 px as 145/145 (after a 10 px gap); Fill beside fixed children; Fill with
  min 100 (150/150) and min 200 (200/100); Fill with max 50 and 110 in either order (50/110/140 and
  140/110/50); min greater than max (min wins: 120/180); Fill when fixed children already overflow (Fill
  0 wide); cross-axis stretch, with a max of 40 and centred; a hidden child; an absolute child at
  (270, -10); zero children (hug gives the padding, 10 x 8; a 10 x 10 fixed frame with 20 padding gives
  40 x 40); Auto gap between, evenly, around; one child in an Auto stack at the start; Auto overflow,
  flush (between and around); numeric gap centred and overflowing (first item at -15); wrap with 10/20
  gaps (2 lines); wrap with a 400 px child in a 300 px frame (3 lines, the long child alone); exact fit
  (four 100 px boxes in 300 px: 3 on the first line, 1 on the second); wrap skipping a
  hidden child; wrap of Fill children with min 120 (2 lines) and without min (1 line); wrapped tracks
  centred and spread; a column wrap; Hug with a min width larger than its content; a negative gap of -20
  (CSS drawn with margins); a nested Hug frame.
- Expected to differ: **2 of 2 differ, as Figma documents.** A Hug frame (width 300) with a Fill child:
  ours turns Fixed and gives the Fill child 240 px; CSS `width: max-content` gives a 60 px frame and a 0
  px child. A Hug-height frame (height 100) with a stretch child: ours 100 (Fixed), CSS 30.
- The whole run took about 230 ms including the browser start.

**Fill variants** (`node fill-variants.js`, `fill-variants.txt`), inner 300 px:

| Case | spec (and Chromium where drawn) | Yoga v3.2.2 (our transcription) | Penpot (our transcription) |
|---|---|---|---|
| two Fill | 150, 150 | same | same |
| min 100, free | 150, 150 | same | 200, 100 |
| min 200, free | 200, 100 | same | 250, 50 |
| max 50, max 110, free | 50, 110, 140 | same | same |
| free, max 110, max 50 | 140, 110, 50 | 125, 110, 50 (15 px unshared) | same as spec |
| min 120 x 3 | 120 x 3 (overflows 60) | same | same |
| min 120 > max 80, free | 120, 180 | same | 80, 220 |
| min 60, min 60, max 40 | 130, 130, 40 | same | same |
| free, min 140, min 170 | 0, 140, 170 | same | same |

**Overflow probe** (`node probe-overflow.js`, `probe-overflow.txt`): first item x for three 60 px boxes in
150 px: space-between 0, space-around 0, space-evenly 0, center -15, safe center 0.

**(b) Align and distribute** (`node run-align.js`, `run-align.txt`), boxes x,y,w,h:

- Row (0,10,40,20), (70,0,30,50), (150,25,50,10), (260,5,40,30): align top to selection, all y = 0;
  vertical centres to the selection (0 to 50, centre 25): y = 15, 0, 20, 10; bottom to key object #2
  (bottom 35): y = 15, -15, 25, 5 (the key stays).
- One box (10,10,40,20) "to selection" aligns to its parent (0,0,400,300): right gives x = 360.
- Distribute by centres: x = 0, 91.667, 168.333, 260 (step 86.667). By equal gaps: x = 0, 86.667,
  163.333, 260 (gap 46.667). Two boxes: unchanged (both are outermost).
- A wide box (60,0,300,20) between (0,0,40,20) and (250,30,40,20): Inkscape's reading moves the wide box
  to x = -5 (gap -45; the selection's span changes from 0..360 to -5..295); our Figma reading keeps 0 and
  360 and gives x = 0, 60, 30 (gap -10). Overlapping boxes (widths 100 at 0, 50, 120): gap -40, x = 0,
  60, 120.
- Rotation: a 100 x 20 box at 90 degrees is 20 x 100 by its bounds (x 40, y -40); at 45 degrees
  84.853 x 84.853; aligning left with a plain box moves the plain box to x = 7.574. Floating error shows
  (20.000000000000007): results must be rounded as the board does (1e-4).
- Tidy up: gaps 20, 20, 19, 35 give the mode 20 and x = 0, 70, 140, 210, 280.
- Board units: three figures 4 columns wide at 0, 4.5, 8 on a 12-column board: gap 0, x = 0, 4, 8 (the
  12 px gutter is inside each figure's width, see section 8).

**(c) Equal-gap snap timing** (`node spacing-snap.js`, three runs, `spacing-snap.txt`). Boxes 120 to 200 by
90 to 150 px in rows of six on a 1408 px board, jittered; 500 random moves after 50 warm-up moves;
threshold 12 px. Correctness checks: three boxes 100 apart give 3 horizontal gaps (100, 100, 250); a box
at 455 snaps -5 to "after" the 100 gap; a box at 352 snaps -2 to the edge at 350.

| n | gaps (H, V) | build, 5 runs (ms, min to max over 3 runs) | per move median (ms) | p95 (ms) | max (ms) |
|---|---|---|---|---|---|
| 50 | 120, 176 | 0.32 to 1.77 | 0.0028 to 0.0042 | 0.072 to 0.091 | 0.24 to 0.54 |
| 200 | 495, 3201 | 0.55 to 2.12 | 0.0197 to 0.0215 | 0.029 to 0.033 | 0.06 to 0.20 |
| 1000 | 2493, 82668 | 14.3 to 53.3 | 0.49 to 0.53 | 0.67 to 0.75 | 0.75 to 9.16 |

What it shows: the per-move cost is far inside a 16 ms frame even at 1000 boxes; the one-off build is the
larger cost at 1000 and belongs at drag start. The vertical gap count grows with the square of a column's
length because every pair counts, not only neighbours; and almost every move found a snap (498 to 500 of
500), so with many boxes a 12 px threshold over all pairs snaps nearly everywhere. A board should limit
gaps to neighbouring pairs (no box between them) or to what is on screen, as Excalidraw limits to visible
elements and tldraw shows only the smallest matching gap. Boards hold at most 80 figures
(`bimBrdFigsValid`, board-figures.js line 73), so n = 50 to 200 is the realistic range. Phones were not
measured here; a 4 to 8 times slower core still leaves the 1000-box p95 under 6 ms (S: an estimate).

## 7. Edges

- A Hug frame with a Fill child (Figma: Fixed on that axis; CSS: content size).
- Fill children: basis 0, so in a wrap row they never wrap without a min; min beats max; free space after
  clamping is shared again (the loop), and a child order must not change the result (Yoga's does).
- Fixed children never shrink (Figma has no shrink); Fill children shrink to their min, never below 0.
- Auto gap: one child at the start; overflow gives gap 0 and the start (Figma, spec and Chromium agree).
- Numeric gap with centre alignment and overflow: overflow on both sides (first item -15 in 6a).
- A negative main gap is valid; a negative gap between wrapped tracks is not.
- Exact fit stays on the line; a first item larger than the line goes alone; zero children: Hug is the
  padding; a frame is never smaller than its padding.
- Hidden children leave the flow and take no wrap slot; absolute children keep x, y.
- Distribute with fewer than three boxes changes nothing; overlapping boxes give a negative equal gap;
  a wide box can make the two "outermost" readings part.
- Rotated boxes use their bounding box (not present on boards today).
- Board units: positions in columns of 118.33 px (1420/12) with the 12 px gutter inside a figure's width,
  so a gap of 0 columns already shows 12 px; snaps and gaps must be computed in the same units the board
  draws.

## 8. What the app already has

- `src/js/engine/sheets/board-edit.js` lines 19 to 27: the board's Edit; "Snap catches an edge on another
  figure's edge or the board's, within the same 12 px (pxThreshold); failing that, Grid puts the edges on
  the board's 12 columns and on rows of the same step; Ortho keeps a drag straight".
- `board-edit.js` lines 104 to 133, `bimBrdSnap(mode, F0, dx, dy, others, z)`: threshold
  `A3D_SNAP.pxThreshold/(BIM_BRD_P0*(z||1))` in column units (line 105); Ortho zeroes the smaller of dx and
  dy (line 106); candidate edges are the board's 0 and 12 and every other figure's left, right, top and
  bottom (lines 105, 107); `near()` takes the nearest moving-edge/target pair within the threshold (lines
  109 to 113); a move snaps both its edges (lines 116 to 118), a resize its right and bottom (124 to 126);
  Grid rounds to whole units where no object snap caught (lines 120, 128); results are clamped to the
  board (x in 0..12-w, w at least 1, h at least 0.25) and rounded to 1e-4 (lines 121, 129, 131). Guides
  are drawn as divs (`bimBrdGuides`, lines 135 to 145). No centre snaps, no gap snaps.
- `src/js/engine/drawing/plan-mode-sketch.js` line 41: `A3D_SNAP={point:true,grid:false,gridSize:0.5,
  ortho:false,pxThreshold:12}`, shared with the drawing (F3, F9, F8).
- `src/js/engine/sheets/board-figures.js` line 20: `BIM_BRD_W0=1408, BIM_BRD_G=12,
  BIM_BRD_P0=(1408+12)/12` (118.33 px a column); lines 70 to 88 `bimBrdFigsValid`: at most 80 figures, w
  1..12, x 0..12-w, h 0.25..400, y 0..4000, 4-decimal rounding; lines 154 to 168 `bimBrdBands`, the reading
  order used on a phone; lines 171 to 179 `bimBrdOverlaps`; line 202, a figure drawn at
  `left:x*P; width:w*P-G`.
- `board-figures.js` lines 343 to 367: `bimBrdMeasurer` and `bimBrdMeasureDefault` already measure a
  default board in a hidden DOM at 1440 px and read the figures' boxes back into column units: prior art
  in the app for alternative 2, used once per revision, not on every edit.
- Board figures are positioned absolutely; there is no frame or group to lay out yet, so the auto layout
  needs a container record (a frame with children) that the board's list does not have today.

## 9. Risks and threats to validity

- Figma's own output was not measured: every Figma rule is as its help and typings state; Fill's exact
  sharing (H2) rests on CSS and U evidence. A designer may find a case where Figma differs.
- One browser (Chromium 153) was the oracle; Firefox and Safari not run here. The cases avoid text and
  fractional pixel snapping, where engines differ most.
- Yoga's and Penpot's differences come from our transcriptions, not from running them.
- Timing is on one desktop CPU in Node; a phone browser was not available.
- The Figma help centre changes often (Evenly and Around were "rolling out" on the day read); the
  wording read is dated 2026-11-08.
- Adobe's documents were refused; the Illustrator and InDesign definitions remain U.

## 10. What is still open (U), and the facts the code would depend on

Open (U): Figma's Fill arithmetic with min and max (measure in Figma); Figma's choice of "outermost" when
a wide box spans past the last centre; any Figma equal-spacing snap threshold or marker; Illustrator and
InDesign's align and distribute (helpx.adobe.com refused); Firefox and Safari agreement.

Facts the code would depend on, for the second reader (all P unless marked):
1. Fill: flex 1 1 0 with the 9.7 freeze loop (spec 9.7; Chromium measured); Figma's equivalence is U.
2. Hug with a Fill child becomes Fixed on that axis (Figma guide, "Hug contents" note).
3. Auto gap modes and "stops at 0"; one child at the start (Figma flows article).
4. A frame is never smaller than its padding (Figma flows article).
5. Hidden and ignore-auto-layout children leave the flow (Figma guide and flows article).
6. Negative main gap allowed, cross gap positive; last on top by default (typings, flows article).
7. Wrapped tracks sized by their tallest child, aligned by the cross alignment, or spread (typings).
8. Wrap breaks before the item that would not fit; exact fit stays (spec 9.3; Chromium measured).
9. Distribute keeps the outermost objects, more than one layer needed; tidy up uses the mode gap (Figma
   alignment article).
10. Snap thresholds are screen pixels divided by zoom (Excalidraw 8, tldraw 8, Penpot 10 and 20; the board
    already does it with 12).
11. The board's units, gutter, 80-figure cap and current snap (board-edit.js, board-figures.js, as cited).

## 11. The owner's decisions (asked together at the end of V174's research)

1. Auto layout scope: the subset above (row, column, wrap, gap with Auto, padding, alignment, Hug, Fill,
   Fixed, min and max, hidden, ignore auto layout), without Figma's grid flow and text baselines?
2. Fill: CSS's rule (equal shares from 0, then min and max), which Chromium measures and Dev Mode is said
   to emit, rather than Penpot's grow-from-min?
3. Distribute's "outermost": keep the least left edge and the greatest right edge (our Figma reading), not
   Inkscape's by-centre order?
4. Smart spacing: equal-gap snaps among neighbouring figures only, at the existing 12 px (the drawing's
   threshold), drawn with the board's guides; or Figma-like 8 px as Excalidraw and tldraw use?
5. Does a frame on a phone become a column in reading order (as the board's figures do today)?

## 12. References

- Figma, "Guide to auto layout in Figma", help.figma.com/hc/en-us/articles/360040451373. Whole article
  (flows, padding and gap, resizing table, Hug note, Fill, Fixed, min and max, ignore auto layout, nesting,
  constraints). Read 2026-11-08. P.
- Figma, "Use the horizontal and vertical flows in auto layout", help.figma.com/hc/en-us/articles/
  31289464393751. Wrap, resizing note (padding), alignment, single child, gap, auto spacing and its
  CSS equivalence, overflow at 0, padding, baseline, strokes, canvas stacking, hiding. Read 2026-11-08. P.
- Figma, "Adjust alignment, rotation, position, and dimensions", help.figma.com/hc/en-us/articles/
  360039956914. Alignment, snap settings, distribution, tidy up, position of rotated layers. Read
  2026-11-08. P.
- Figma, "Measure distances between layers", .../360039956974, and "Arrange layers with Smart selection",
  .../360040450233. Read 2026-11-08. P.
- Figma, plugin-typings 1.142.0 (MIT, Copyright 2021 Figma, Inc.), github.com/figma/plugin-typings,
  `plugin-api.d.ts`: layoutMode, padding, primaryAxisSizingMode, counterAxisSizingMode,
  strokesIncludedInLayout, layoutWrap, primaryAxisAlignItems, counterAxisAlignItems,
  counterAxisAlignContent, itemSpacing, counterAxisSpacing, itemReverseZIndex, layoutAlign, layoutGrow,
  layoutPositioning, layoutSizingHorizontal/Vertical, minWidth to maxHeight. Read 2026-11-08. P.
- W3C, CSS Flexible Box Layout Module Level 1, Candidate Recommendation, www.w3.org/TR/css-flexbox-1/
  (page dated 14 October 2025), and its source github.com/w3c/csswg-drafts `css-flexbox-1/Overview.bs`
  (main, 2026-11-08): justify-content values and fallbacks, 9.3 line collection, 9.7 resolving flexible
  lengths. Read 2026-11-08. P.
- W3C, CSS Box Alignment Level 3 (gap values): not re-read here. S.
- Yoga v3.2.2 (MIT, Meta), github.com/facebook/yoga tag v3.2.2: `yoga/algorithm/CalculateLayout.cpp`
  (steps 1 to 11, distributeFreeSpaceFirstPass/SecondPass, resolveFlexibleLength, justifyMainAxis),
  `FlexLine.cpp`, `Align.h`, `BoundAxis.h`. Read 2026-11-08. P.
- Penpot (MPL-2.0, Kaleidos), github.com/penpot/penpot at 904cdd9: `common/src/app/common/geom/shapes/
  flex_layout/layout_data.cljc` (init-layout-lines, distribute-space, add-line-spacing,
  add-children-resizes, calc-layout-data), `frontend/src/app/main/snap.cljs` (snap-accuracy,
  snap-distance-accuracy, calculate-snap). Read 2026-11-08. P.
- Excalidraw (MIT), github.com/excalidraw/excalidraw at 701b901: `packages/excalidraw/snapping.ts`
  (SNAP_DISTANCE, SnapCache, isSnappingEnabled, getVisibleGaps, getGapSnaps, snapDraggedElements). Read
  2026-11-08. P.
- tldraw (tldraw licence, not open source: production use needs a licence key; method read only),
  github.com/tldraw/tldraw at 69f4395: LICENSE.md, `packages/editor/src/lib/options.ts` (snapThreshold 8),
  `.../managers/SnapManager/SnapManager.ts`, `BoundsSnaps.ts`. Read 2026-11-08. P for the method.
- Inkscape (GPL-2+, method only), gitlab.com/inkscape/inkscape master, `src/actions/actions-object-align.cpp`
  (ObjectAlignTarget, object_align, object_distribute). Read 2026-11-08. P for the method.
- Inkscape Beginners' Guide 1.3 (CC BY-SA), inkscape-manuals.readthedocs.io, "Align and Distribute". Read
  2026-11-08. P (thin).
- Adobe, Illustrator and InDesign help on aligning and distributing (helpx.adobe.com): refused (403) on
  2026-11-08. Search summaries only. U.
- zenn.dev/ncdc/articles/8cd9a7d2166379 (Dev Mode emits `flex: 1 0 0` for Fill), via search; forum.figma.com
  threads on wrap with min width, via search. Not read in full. U.
- The app: `src/js/engine/sheets/board-edit.js`, `src/js/engine/sheets/board-figures.js`,
  `src/js/engine/drawing/plan-mode-sketch.js` (lines as cited in section 8). Read 2026-11-08. P.
