# V174 research: practice and prior art in the design tools (layer tree, blending, masks, layout aids)

Part of the V174 research ("Presentation P1: boards"). Research agent 1, 2026-11-08. This note covers how the
design tools and the AEC/GIS layout tools build a board's element tree, compositing, masks and layout aids, read in
their own documentation, and, where open source, in their code read as text (licence first, never run). It replaces
part 1 of `docs/research/research-presentation-panels.md`, whose "16 blend modes" for Figma does not hold (H-a below).
No code was written; nothing under `src/` was touched.

Levels: **P** read in the primary source itself (the vendor's help page, its API reference, the specification, the
code); **S** a dependable secondary source, gap stated; **U** a search summary or an inference, to confirm. U facts must
not reach the code. All pages were fetched 2026-11-08. Downloads are in
`/tmp/claude-0/-home-user-BIM-Personal/1be3f05d-4086-5c3b-a6c0-0d472f37bc60/scratchpad/dl-practice/` (session scratch,
not committed), read as text only.

## 0. The question and the hypotheses

**Question.** What element model (tree, containers, clipping, z-order, lock, hide, selection), what compositing
(opacity, blend modes, isolation, masks) and what layout aids (align, distribute, spacing, rows and columns) do the
professional tools give a designed page, and which of them can a zero-dependency canvas or SVG/HTML board copy
faithfully on phone, tablet and desktop and still export to PDF or print?

**What a good answer must decide.** (1) The exact blend mode list and its names; (2) whether groups isolate or pass
through; (3) what a mask clips; (4) frame versus group semantics (clip, size, constraints); (5) the selection rules
(click, double-click, deep select) and their touch equivalents; (6) align/distribute/smart-spacing rules and nudge
amounts; (7) how far AEC/GIS layout tools go, and why.

| # | Hypothesis (falsifiable) | Outcome |
|---|---|---|
| H-a | Figma has exactly 16 layer blend modes plus pass through, matching the W3C Compositing list | **Fails.** Figma has 18 modes plus Pass through (19 values): the W3C 16 (Normal included) plus **Plus darker** and **Plus lighter**. The W3C `<blend-mode>` list is 16 including Normal. P, high |
| H-b | Figma's mask clips only the siblings above it within the same parent | **Holds, refined.** It clips the siblings above it until another mask, the end of the parent, or a frame with clip content. In practice "Use as mask" wraps mask and masked layers in a mask group. P, high |
| H-c | No mainstream AEC layout tool offers per-element blend modes | **Fails for GIS, holds for BIM.** QGIS print layout items each have a blending mode (13 modes) and opacity; ArcGIS Pro blends map layers (inside map frames). No BIM tool read (Revit, Archicad, SketchUp LayOut, Vectorworks) documents blend modes; Vectorworks has opacity per object and per layer. P for what is documented; the BIM absence is medium (absence of evidence) |
| H-d | Penpot's model is a board(frame)-group-shape tree with per-shape blend mode and opacity | **Holds.** Shape types frame, group, bool, rect, path, text, circle, svg-raw, image; every shape may carry `:opacity` and `:blend-mode` from exactly the W3C 16; no pass-through value. P, high |
| H-e (added) | Canvas 2D can draw every Figma mode | **Fails for one.** `globalCompositeOperation` has the W3C 16 plus Porter-Duff `lighter` (additive, the analogue of Plus lighter); there is no plus-darker / linear burn. P (MDN, W3C); the numeric match to be measured by the browser agent |
| H-f (added) | The Figma mobile/iPad app can edit design files | **Fails.** It views, comments, mirrors and presents; it cannot edit Figma Design files or Slides. Only FigJam boards are editable on iPad. P, high |
| H-g (added) | The tools agree on what "align" aligns to | **Fails.** Figma aligns to the selection's bounds (or to the parent for one layer); ArcGIS Pro aligns to the first selected element by default; Penpot to the edge-most element. P, high |

## 1. Search log

| # | Where | Query / address | What came back | Kept / set aside |
|---|---|---|---|---|
| 1 | curl | help.figma.com article 360040667874 (blend modes) | Full article, 19 modes with descriptions | Kept (P) |
| 2 | WebSearch | Figma masks Use as mask alpha vector luminance | Pointer to 360040450253 and the plugin MaskType page | Pointers only; both read (P) |
| 3 | WebSearch | Figma frames groups sections | Mostly SEO pages; one Figma video page | Set aside; Figma's own pages found by #5 |
| 4 | WebSearch | Figma deep select; tidy up smart selection | Pointers to 360040449873, 360039956914, 360040450233 | Read (P) |
| 5 | curl | help.figma.com/api/v2/help_center/articles/search.json (Zendesk API), 14 queries | Article ids and titles | Kept as the index; bodies fetched by id |
| 6 | curl | Zendesk article JSON for 20 ids (frames, groups, sections, fills, image, text, nudge, shapes, layers, lock, hide, auto layout, measure, constraints, mobile app, effects, grid and flows) | Bodies with update dates | Kept (P) |
| 7 | curl | developers.figma.com BlendMode, MaskType, node-properties | Enum lists and property notes | Kept (P) |
| 8 | curl | www.w3.org/TR/compositing-1/ (CRD 21 March 2024) | `<blend-mode>`, isolation, Porter Duff, separable/non-separable formulas | Kept (P). raw.githubusercontent for fxtf-drafts `Overview.bs` 404 (moved); the TR page answered |
| 9 | raw.githubusercontent | mdn/content globalCompositeOperation, mix-blend-mode | Canvas value list; CSS list incl. plus-darker/plus-lighter | Kept (P for MDN's reading of the specs) |
| 10 | curl | opensource.adobe.com PDF32000_2008.pdf (ISO 32000-1 as published by Adobe) | Tables 136, 137; isolated and knockout groups | Kept (P) |
| 11 | git (sparse, depth 1) | github.com/penpot/penpot at 904cdd97 (2026-11-07) | `common/.../types/shape.cljc`, `shape/layout.cljc`, `shape_tree.cljc`, `files/helpers.cljc`, frontend `ui/shapes/{mask,group,frame}.cljs`, `data/workspace/groups.cljs`, `sidebar/layer_item.cljs` | Kept (P, read as text; MPL-2.0 read in LICENSE) |
| 12 | curl | help.penpot.app/user-guide/designing/layers/ | Boards, select, hide, lock, mask, align, constraints, blend list | Kept (P) |
| 13 | git (sparse) | github.com/excalidraw/excalidraw at 701b901a (2026-11-05) | `packages/element/src/{align,distribute}.ts`, `packages/excalidraw/snapping.ts` | Kept (P, read as text; MIT read in LICENSE) |
| 14 | WebSearch, curl, WebFetch | canva.com/help (layers, transparency, lock, group, align, smart guides) | **403** to curl and to WebFetch (a "Canva" stub page) | Refused; recorded |
| 15 | curl | www.canva.cn/en/help/layer-group-align/ | Connection reset | Refused |
| 16 | curl | www.canva.dev/docs/apps/design-editing/ | Canva's Design Editing API guide | Kept (P for the API model; S for the editor) |
| 17 | curl, WebFetch | helpx.adobe.com (Illustrator transparency, layers, clipping masks, smart guides; InDesign transparency) | **403** to both | Refused; recorded |
| 18 | curl | adobe.com/express learn page | 403 | Refused |
| 19 | git (sparse) | github.com/docsforadobe/illustrator-scripting-guide at 714dc133 | `docs/jsobjref/scripting-constants.md`, BlendModes | Kept (S: a community transcription of Adobe's scripting reference) |
| 20 | git (sparse) | github.com/qgis/QGIS-Documentation master at 83f9bab8 | `print_layout/overview_layout.rst`, `layout_items/*.rst`, `create_output.rst`; `introduction/general_tools.rst` (raw) | Kept (P) |
| 21 | WebSearch, curl | ArcGIS Pro 3.5 apply-visual-effects, layout-contents-pane, work-with-layout-elements | Full pages | Kept (P) |
| 22 | WebSearch, curl | Revit "About the Draw Order of Details" (2026 cloudhelp) | Full page | Kept (P) |
| 23 | WebSearch, curl | Archicad 28 help "Display Order" | Full page | Kept (P) |
| 24 | WebSearch, curl | help.sketchup.com/en/layout/using-layers | Full page (updated 29 Sep 2026) | Kept (P); prod-aws-help.sketchup.com refused (502 at the proxy) |
| 25 | WebSearch, curl | Vectorworks 2024 viewport layer properties; 2021 Opacity attributes | Full pages | Kept (P) |
| 26 | curl | help.procreate.com handbook: layers-interface, layers-organize, layers-blend, layers-mask | Full pages | Kept (P) |
| 27 | WebSearch, curl | affinity.help designer2ipad; affin.co/designer2gestures | Index page; gesture sheet is an image-only PDF (no text); guessed page paths 403 | Not usable; recorded |
| 28 | WebSearch | Graphisoft community on display order in layouts; SketchUp forum on Send to Back across layers | Forum answers | Not used for code (U); the official pages (#23, #24) agree |

## 2. Findings by topic

### 2.1 Figma: the layer tree

- **Layer order.** "Any layers at the top of the layers panel appear above any layers below them in the canvas." The
  Layers panel is the z-axis; there is no z field. Shortcuts: Bring forward Cmd/Ctrl+], Bring to front
  Cmd+Opt+] (Ctrl+Shift+] on Windows), Send backward Cmd/Ctrl+[, Send to back Cmd+Opt+[. Inside an auto layout frame,
  order works "the opposite way" and changes position in the flow, because auto layout does not expect overlap. (P,
  high; 26584819173271, 360039956914)
- **Frames.** Containers whose size you set; they can nest; a frame on the canvas is a top-level frame, shown bold in
  the panel with its name on the canvas. Frame properties: corner radius, **Clip content** ("hide any objects within
  the frame that extend beyond the frame's bounds"), layout guides, auto layout, fill, stroke, effects. Only frames
  give constraints, layout guides, auto layout and prototyping. Frame presets include Paper and Presentation. Frame
  selection: Opt+Cmd+G / Ctrl+Alt+G. The default of Clip content for a new frame is not stated in the pages read (U).
  (P, high; 360041539473)
- **Groups.** "By default, groups take on the combined dimensions of their children"; their bounds follow the
  children as they move; groups nest; Cmd/Ctrl+G, ungroup Shift+Cmd/Ctrl+G. Constraints cannot be set on a group:
  "If you apply constraints to a group, Figma applies constraints to the individual layers." (P, high; 360039832054,
  360039957734)
- **Sections.** Top-level canvas areas with a title, fill and stroke; they can contain any layer type, including
  sections, but "cannot be contained within frames or groups". Deleting a section with Cmd/Ctrl+Delete keeps its
  contents. Sections carry the "Ready for dev" status; they are organisation, not composition. (P, high; 9771500257687)
- **Lock.** A locked layer cannot be moved or interacted with on the canvas, but it can be selected in the Layers
  panel (and through the right-click Select layer menu) and its properties edited. Locking a frame or group locks its
  children; a child cannot be unlocked while its parent is locked. Shift+Cmd/Ctrl+L; drag across the padlocks to lock
  several. (P, high; 360041596573)
- **Hide.** A hidden layer cannot be selected on the canvas, not even through Select layer; it can be selected in the
  panel and still moved or edited there. Shift+Cmd/Ctrl+H; hiding a group or frame hides its children. (P, high;
  360041112614)
- **Selection rules.** Clicking an object inside a group or frame "we'll select the parent by default". Double-click or
  Enter goes one level down; Shift+Enter selects the parent; Tab / Shift+Tab move between siblings. **Deep select**:
  hold Cmd/Ctrl and click to select the innermost nested layer (or the top-level frame). Right-click > Select layer
  lists every layer under the cursor in Layers-panel order, with locked layers marked by a padlock. A marquee from
  empty canvas selects; Cmd/Ctrl+marquee selects nested layers; "If you select a top-level frame, only other top-level
  layers will be selected." In the panel: Shift-click selects a range, Cmd/Ctrl-click toggles. Esc clears;
  Shift+Cmd/Ctrl+A inverts. (P, high; 360040449873) Practitioners report that a child of a top-level frame is selected
  on the first click, as on an artboard; the help text read says only "parent by default" (U, to confirm in the app).
- **Shapes.** Rectangle (R, per-corner radius), Line (L, dash and gap), Arrow (Shift+L, end caps), Ellipse (O, arc
  tool for pies and rings), Polygon (default triangle; its bounding box stays the regular-polygon box until flattened),
  Star (default 5 points, 10 sides; count 3 to 60; ratio; radius). Shift constrains, Opt/Alt draws from the centre.
  (P, high; 360040450133)
- **Text.** Three resizing modes: **Auto width** (set by a single click; grows horizontally and breaks only at Return),
  **Auto height** (fixed width, grows down), **Fixed size** (set by click-and-drag; resizing the box by hand also sets
  Fixed). The Scale tool changes box and font size together and can leave fractional sizes. (P, high; 27378154668951)
- **Images are fills.** Fill types: Solid, Gradient, Pattern, Image, Video. Image fill modes: **Fill** (cover, may
  clip), **Fit** (contain, may leave space), **Crop** (non-destructive, like a mask), **Tile** (percentage of the
  image's own size). Rotate 90 degree steps; adjustments: exposure, contrast, saturation, temperature, tint,
  highlights, shadows. A layer can carry several fills, each with its own opacity, visibility and blend mode, reordered
  by drag. (P, high; 360041003694, 360041098433)
- **Constraints.** Horizontal Left, Right, Left and right, Center, Scale; vertical Top, Bottom, Top and bottom,
  Center, Scale. Default **Top and Left**. Only on layers inside a frame, not in an auto layout frame; hold Cmd/Ctrl
  while resizing to ignore them. (P, high; 360039957734)

### 2.2 Figma: opacity, blend modes, isolation

- **Where a blend mode applies.** On the whole layer (Appearance section), on each fill or stroke fill (colour
  picker), and on inner shadow, drop shadow and noise effects. One mode per layer, fill or effect. Fills that use a
  colour style cannot take one. (P, high; 360040667874)
- **Opacity is two things.** Layer opacity (`opacity`, 0 to 1, "as shown in the Layer panel") and fill opacity (the
  field beside each fill swatch). (P, high; plugin API node properties; 360041003694)
- **The list, in Figma's order and names:** Pass through, Normal, Darken, Multiply, Plus darker, Color burn, Lighten,
  Screen, Plus lighter, Color dodge, Overlay, Soft light, Hard light, Difference, Exclusion, Hue, Saturation, Color,
  Luminosity. The API's 19 values are the same, with Plus darker = `LINEAR_BURN` and Plus lighter = `LINEAR_DODGE`.
  Paints and effects take every value but `PASS_THROUGH`. (P, high; help article and `BlendMode` reference)
- **Pass through versus Normal (isolation).** Pass through is the default for layers; on a frame or group it lets the
  children's blend modes reach the content below the parent. **Normal on a parent** stops them at the parent, that
  is, the parent becomes an isolated group. Normal is the default for fills and effects; Pass through cannot be set on
  them. This is the W3C model: a non-isolated group versus an isolated one (W3C section 10.3: in an isolated group the
  children composite onto an empty backdrop). (P, high)
- **Formulas.** Figma's descriptions match the W3C ones for the 16 (e.g. Multiply: black gives black, white keeps the
  colour; Overlay is Multiply or Screen by the base colour). Plus darker: "Blending with white produces no effect";
  Plus lighter: "Blending with black produces no effect", which is linear burn (a + b - 1) and linear dodge (a + b) as
  ArcGIS Pro writes them (2.10). (P for the texts; the equivalence is S, medium)

### 2.3 Figma: masks

- **What a mask clips.** "Masks are positioned below masked layers on the z-axis. The mask applies to all siblings
  above it until it reaches: another mask or mask object; the mask's parent frame or group; a frame or component with
  clip content on." A mask above an image does not mask it. Masks are siblings of what they mask, so they move and
  resize independently. Any layer can be a mask: shapes, text, images with alpha, groups. (P, high; 360040450253)
- **Making one.** Place the mask lowest, select it with the layers to mask, More options > Use as mask
  (Ctrl+Cmd+M / Ctrl+Alt+M). "Figma will create a mask group with all selected layers." Drag layers into the mask
  group to add them. View > Mask outlines shows mask bounds in green. (P, high)
- **Three types, default Alpha.** **Alpha**: the mask's opacity per pixel decides what shows (blurs, shadows,
  gradients and PNG alpha all count). **Vector**: any area above 0 % opacity counts as 100 %, so the outline is the
  mask. **Luminance**: brightness decides; black reveals nothing. API: `maskType` ALPHA / VECTOR / LUMINANCE, default
  ALPHA; `isMask` "masks its subsequent siblings". The mask types post-date the original mask (one search pointer says
  2023; date U). (P, high for behaviour)

### 2.4 Figma: align, distribute, tidy up, smart selection, snapping, nudge

- **Align.** One layer selected: align to its parent. Several: to one another (the selection's bounds), or, with
  Shift-click on the control, as a group to the parent frame. Alt+A/D/W/S left/right/top/bottom, Alt+H/V centres.
  (P, high; 360039956914)
- **Distribute.** Equal space between layers; the outermost two stay put (left and right for horizontal, top and
  bottom for vertical). One axis at a time. (P, high)
- **Tidy up.** Arranges into a row, a column or a grid, anchored to the selection's top-left; the spacing shown is the
  **mode** (most common gap) of the selection, with up to 1 px of rounding when snapping to the pixel grid. "You can
  think of tidy up as distribute with some extra logic"; its purpose is to produce a smart selection. (P, high)
- **Smart selection.** Two or more layers, equally spaced and overlapping on one axis (1D) or both (2D). Handles: a
  pink ring at each layer's centre (filled when marked), pink spacing handles between layers that drag the gap (tooltip
  in px), a space-between field in the panel; drag a marked layer to reorder (Cmd/Ctrl swaps); duplicate and delete
  reflow the rest; rearranging does not change the Layers panel order. (P, high; 360040450233)
- **Snapping.** Snap to geometry (vector edit only), Snap to objects ("the centers and outermost points"), Snap to
  pixel grid; a red guide shows a snap; hold Control to suspend. The equal-spacing snap that practitioners call "smart
  guides" (pink gap marks while dragging) is not described in the pages read (U). (P, high for what is described)
- **Measure.** Opt/Alt with a selection, hover another object: a red line and the horizontal and vertical distances
  between bounding boxes (strokes, text baselines and odd-sided polygons are not measured to their visual edge).
  Cmd+Opt / Ctrl+Alt reaches nested layers. (P, high; 360039956974)
- **Nudge.** Arrow keys move by the small nudge, **1**; Shift+arrows by the big nudge, **10**, both in points, both
  settable in Preferences. (P, high; 4404575206295)
- **Rows and columns (auto layout).** Flows: Vertical, Horizontal, Grid; Wrap for horizontal and vertical. Padding
  (uniform, per axis or per side) and gap (a number, or Auto with Between, Around, Evenly). Sizing: **Hug contents**
  (frame shrinks to children plus padding), **Fill container** (child takes the free space; not for top-level frames),
  **Fixed**. A child set to Fill makes the parent Fixed on that axis. **Ignore auto layout** (formerly absolute
  position) takes a child out of the flow and gives it constraints. Shift+A adds auto layout. (P, high; 360040451373)

### 2.5 Penpot (MPL-2.0), the same ideas in open code

Read at commit `904cdd97163dc77c0d875f509ccab9ff234d7bae` (main, 2026-11-07), files under
`common/src/app/common/types/` unless noted.

- **Shape types** (`shape.cljc:71-80`): `:frame :group :bool :rect :path :text :circle :svg-raw :image`. The UI calls a
  frame a **board**. Group, frame, bool and svg-raw hold `:shapes`, a vector of child ids. (P, high)
- **Per-shape attributes** (`shape.cljc:262-300`): `:blocked`, `:locked`, `:hidden`, `:collapsed`, `:masked-group`,
  `:fills`, `:opacity`, `:blend-mode`, `:constraints-h`/`-v`, `:proportion-lock`, radii `r1`..`r4`, strokes, exports.
  Frames add `:show-content` (clip off when true), `:hide-fill-on-export`, `hide-in-viewer`. Text `grow-types` are
  `:auto-width :auto-height :fixed`, Figma's three. (P, high)
- **Blend modes** (`shape.cljc:82-98`): exactly the W3C 16, `:normal` to `:luminosity`. No pass-through, no plus modes.
  The help page lists the same ("Opacity and blend: Set the overal opacity for layers and their blend mode"). (P, high)
- **Z-order.** Index 0 in `:shapes` is the bottom; the Layers panel draws children in reverse, so the top of the list
  is the front (`sidebar/layer_item.cljs:457, 493`). In a flex/grid board a `:layout-item-z-index` can override the
  index (`shape_tree.cljc:219-235`). (P, high)
- **Masks are a group flag.** `mask-shape?` is a group with `:masked-group` (`files/helpers.cljc:62-65`). The renderer
  takes the **first child (the bottom)** as the mask and every other child as masked (`ui/shapes/group.cljs:24-31`);
  the help says "The shape that is at the lowest level at the layer list will be used as a mask". So Penpot masks the
  whole rest of the group, not "until the next mask" as Figma does. (P, high)
- **One mask type, alpha.** The mask is drawn inside an SVG `<mask>` through a filter that floods white `in` the
  source graphic (`ui/shapes/mask.cljs:80-86, 111`), so the mask's alpha, not its colour, decides; text masks get a
  white fill instead (`set-white-fill`, a Firefox workaround). A `<clipPath>` of the mask's outline is added so hidden
  parts do not catch pointer events, and mask and clip are on separate `<g>` because of a Firefox bug. (P, high; the
  Firefox notes are the authors' comments, not checked here)
- **Frames clip** unless `:show-content` is set (`ui/shapes/frame.cljs:31-36, 52`). (P, high)
- **Constraints** default to **Scale** in Penpot (help page), against **Top and Left** in Figma. (P, high)
- **Flex and grid layout** (`shape/layout.cljc:17-140`): `:layout` `:flex`/`:grid`; flex direction row, row-reverse,
  column, column-reverse; gap `{row-gap, column-gap}`; padding p1..p4; wrap; justify-content and align-content with
  start, center, end, space-between, space-around, space-evenly, stretch; align-items start, end, center, stretch;
  child sizing `:fill :fix :auto` (Figma's Fill, Fixed, Hug), min/max width and height, margins, `:layout-item-absolute`
  (Figma's Ignore auto layout); grid tracks `:percent :flex :auto :fixed` and cells with spans. This is CSS flexbox and
  grid as data. (P, high)
- **Selection** (help): click selects; double-click enters a group; Ctrl/Cmd click ignores groups (deep select);
  right-click Select layer lists layers under the cursor. First-level boards with content are selected by their name or
  Ctrl/Cmd click, so a click on the board's area reaches the content. Hidden layers can still be selected in the panel;
  locked layers are selectable in the panel and editable there. **Align** moves layers relative to "the edge of the
  top-most element" (for Align top), i.e. the selection's extreme. (P, high)

### 2.6 Excalidraw (MIT): alignment, distribution and snapping as code

Read at commit `701b901a0f1ba3d0b390d9cdf63d112e25abac4b` (2026-11-05).

- **Align** (`packages/element/src/align.ts`): position start, center or end on axis x or y, to the **common bounding
  box of the selection**; each group in the selection moves as one. (P, high)
- **Distribute** (`distribute.ts:20-119`): only "space between". Groups are sorted by centre; step = (selection
  extent - sum of extents) / (n - 1). When the step is **negative** (the items overlap more than the span), it
  distributes **centres** instead, keeping the two boxes that touch the selection's ends still. The outermost items
  stay put. (P, high) This is the edge case Figma's help does not describe and ArcGIS Pro handles differently
  (2.10: it widens the span so nothing overlaps).
- **Snapping** (`packages/excalidraw/snapping.ts`): `SNAP_DISTANCE = 8` screen px, divided by the zoom, so the
  tolerance is constant on screen. Two snap kinds: **point** snaps (corners and centre; edge midpoints for ellipses
  and diamonds) and **gap** snaps (`center_horizontal`, `center_vertical`, `side_left`, `side_right`, `side_top`,
  `side_bottom`): the dragged box centres in an existing gap wider than itself, or repeats an existing gap to the side.
  A gap counts only between boxes that overlap on the other axis. Ctrl/Cmd inverts the snapping setting while
  dragging; a lone arrow does not snap (binding has priority). (P, high) This is the "smart spacing" the scope asks
  for, written down: measure visible gaps between neighbours that overlap on the cross axis, offer equal-gap targets,
  draw the gap marks.

### 2.7 Canva

- canva.com/help refused this environment (403 to curl and to the fetch tool) and canva.cn reset the connection, so
  Canva's editor help could not be read (U for every editor claim: the Layers panel, Position > Arrange, lock, smart
  guides, the transparency slider, any blend options).
- **Canva's own Design Editing API guide** (canva.dev) describes the element model: a page holds a flat, ordered
  collection of elements; `insertAfter(undefined, el)` adds at the end, "making it appear on top"; elements are moved
  with `insertBefore/insertAfter/moveBefore/moveAfter`. Element types exposed: embeds, **groups**, **rects**, shapes,
  text; "images and videos are handled as rects with fills. This is more aligned with how Canva works under the hood."
  All elements share top, left, width, height, rotation, **transparency** and **locked**; pages can be locked; a page
  has a background fill. No blend mode property is listed. (P for the API, S for the editor, medium)

### 2.8 Adobe (Illustrator, InDesign, Express)

- helpx.adobe.com and adobe.com/express refused this environment (403 to curl and to the fetch tool). The Transparency
  panel's Isolate Blending, Knockout Group and opacity masks could not be read at the source (U).
- **Illustrator's scripting constants** (docsforadobe transcription, S): `BlendModes` = Color, Color Burn, Color
  Dodge, Darken, Difference, Exclusion, Hard Light, Hue, Lighten, Luminosity, Multiply, Normal, Overlay, Saturation,
  Screen, Soft Light: **the W3C 16 exactly**. (S, high: a community copy of Adobe's reference; agrees with PDF below)
- **PDF itself** (ISO 32000-1:2008 as Adobe publishes it, 11.3.5): Table 136, separable: Normal, Compatible (an old
  synonym of Normal), Multiply, Screen, Overlay, Darken, Lighten, ColorDodge, ColorBurn, HardLight, SoftLight,
  Difference, Exclusion; Table 137, non-separable: Hue, Saturation, Color, Luminosity. Section 11.4 defines **isolated**
  and **knockout** transparency groups. So the W3C 16 export to PDF natively, as do group opacity and isolation; Plus
  darker / Plus lighter / Linear modes do not. (P, high)

### 2.9 QGIS print layouts (the strongest counter-evidence for H-c)

Read in QGIS-Documentation master at `83f9bab8`.

- **Items panel.** Every item, groups included, in a list synced with the canvas selection (useful "to select an item
  placed behind another one"); per item: visibility, **lock position**, Z order by drag ("The upper item in the list
  will be brought to the foreground"; new items go to the front), rename by double-click. Shift range, Ctrl toggle.
  (P, high; `overview_layout.rst:744-766`)
- **Actions.** Group Ctrl+G, Ungroup Ctrl+Shift+G, Raise Ctrl+], Lower Ctrl+[, Bring to Front Ctrl+Shift+], Send to
  Back Ctrl+Shift+[, Lock Selected Ctrl+L, Unlock All Ctrl+Shift+L, Align Items, Distribute Items. Guides, a snapping
  grid and **Smart Guides** ("uses other layout items as guides to dynamically snap to"), Ctrl+Alt+;. (P, high)
- **Align/distribute.** Align left/right/top/bottom/centres; Distribute left edges, right edges, top, bottom,
  horizontal centres, vertical centres equidistantly, and **Distribute horizontal / vertical spacing equally**: two
  different notions of "distribute" (edges or centres at equal steps, versus equal gaps). (P, high;
  `layout_items_options.rst:163-200`)
- **Rendering per item:** **Blending mode**, **Opacity**, **Exclude item from exports**, a Geospatial PDF group. The
  13 blend modes: Normal, Lighten, Screen, Dodge, Addition, Darken, Multiply, Burn, Overlay, Soft light, Hard light,
  Difference, Subtract (no Hue/Saturation/Color/Luminosity, no Exclusion). Layers in a group "rendered as a group" also
  get clipping modes: Masked By Below, Mask Below, Inverse Masked By Below, Inverse Mask Below, Paint Inside Below,
  Paint Below Inside: masks expressed as compositing operators. (P, high; `general_tools.rst` blend-modes section)
- **The export cost.** "Always export as vectors: some rendering options require items to be rasterized"; and a layer
  opacity below 100 % "forces a rasterized rendering of those objects during PDF exports", which can make the PDF
  large. (P, high; `create_output.rst:194-257`)
- **Live map surround.** Legend linked to a map, synchronised to all project layers or to visible ones, "Only show
  items inside linked maps", feature counts, Auto update (customisation only with Auto update off). North arrow = a
  picture item with **Sync with map** rotation, Grid north or True north, and a declination offset. Scale bar linked to
  a map, segments left and right, **Fixed width** or **Fit segment width** (resized to stay within a mm range as the
  scale changes). Page presets A4, B0, Legal, Letter, ANSI A, Arch A and their families, portrait or landscape, or
  custom. (P, high)

### 2.10 ArcGIS Pro layouts

- **Layout Contents pane.** Lists every element and every map layer inside map frames. Check boxes show or hide
  elements (Ctrl-click toggles all); **Lock** prevents selecting, moving or resizing on the page but not editing in the
  Element pane; Filter by type (graphics, groups, legends, map frames, north arrows, scale bars, text) and search.
  **List By Drawing Order** (default, top draws on top, drag to reorder, subitems of maps, legends and tables
  reorderable), by Element Type, by Map Frame (surround elements tied to a frame), by Map Series pages. Order commands
  Bring To Front / Forward / Send Backward / To Back; **inside a group they apply within the group** and do not take
  the element out. Groups move, resize and lock together. (P, high)
- **Align and distribute.** Elements align "to the edge of the **first selected element** by default"; Align to Page
  aligns to the page. Distribute Horizontally/Vertically = equal **gaps** between edges, and "If there is not enough
  space ... the distribution space is expanded so all elements fit without overlapping"; Distribute Horizontal/Vertical
  Centers = equal steps between centres, ends fixed. Make Same Size/Width/Height; fit to margins. **Nudge 5 points** from
  the context menu. (P, high)
- **Blending.** Layer transparency (0 to 100 %, to a tenth) and **Layer Blend** on any 2D layer of a map or scene, plus
  **Feature Blend** (features in one layer blend with each other). Modes, grouped: Normal; Lightening: Screen, Color
  Dodge, Lighten, Linear Dodge; Darkening: Multiply, Color Burn, Darken, Linear Burn; Comparison: Difference,
  Exclusion; Divergent: Overlay, Hard Light, Soft Light, Linear Light, Pin Light, Vivid Light; Color combination:
  Luminosity, Saturation, Hue, Color. Esri warns that Linear Dodge, Linear Burn, Linear Light, Pin Light and Vivid
  Light "are not supported in the specification for PDF or AIX documents and will be rasterized on export", and marks
  the four colour-combination modes rasterized too, although PDF defines them (2.8): an implementation limit, not a
  PDF one. The layout-elements page read lists no blend mode for layout elements themselves. (P, high)

### 2.11 BIM layout tools: Revit, Archicad, SketchUp LayOut, Vectorworks

- **Revit.** Draw order exists only among **detail** elements in a view (detail components, insulation, detail
  lines, detail groups, repeating details, filled regions): Bring to Front, Bring Forward, Send Backward, Send to Back
  on Modify > Arrange. "Details always appear on top of model geometry. You cannot send a detail behind model
  geometry." No layer tree, blend mode or mask is documented for sheets. (P, high for draw order; medium for the
  absence)
- **Archicad.** Stacking is by **element class** (Annotation over 2D artwork over Library Parts over 3D structures over
  2D Fills over Zones over Figures) and **14 stack levels** (1-4 and 11-14 empty by default); Edit > Display Order
  Bring Forward / to Front / Send Backward / to Back / Reset Default Order; Tab cycles through overlapping elements in
  one class. A rule-based z-order, not a free tree. No blend modes in the page read. (P, high) Forum answers say the
  display order is not saved per view on a layout (U).
- **SketchUp LayOut.** The Layers panel is the z-order: "Entities on a top layer are displayed over top of entities on
  a lower layer"; layers are **regular** or **shared** (shown on every page, a master layer); visibility is per page,
  lock is document-wide; groups exist (moving a group moves its entities to the layer). Forum users note that Send to
  Back only works within one layer (U, consistent with the help). No blend modes documented. (P, high)
- **Vectorworks.** **Opacity on any 2D object**, separately for fill and pen (linkable), or by class; layer opacity;
  in a sheet-layer viewport, per-viewport overrides of layer visibility (visible, invisible, grey), **stacking order**
  (with a "Stacking Override" flag and Revert), opacity or "transfer mode", and colours. 3D needs a transparency
  shader. No blend modes in the pages read. (P, high)
- **Why the BIM tools stop at opacity (inference).** They print to plotters and to PDF/DWF where pens, lineweights and
  overprint matter; QGIS and Esri both document that non-normal compositing or even opacity forces rasterisation on
  PDF export. The reason is plausible but no BIM vendor page states it (U).

### 2.12 Touch: phone and tablet

- **Figma mobile and iPad**: view, comment, present prototypes, **mirror** frames selected on the desktop; "It's not
  possible to edit Figma Design files or Figma Slides decks using the mobile app." FigJam boards are editable on iPad
  (Apple Pencil drawing, shapes, connectors). Viewing gestures: drag to pan, pinch to zoom, long-press to comment,
  two-finger press-and-hold for the prototype menu. (P, high; 1500007537281) **Figma itself offers no touch editing of a
  layer tree**, so its desktop rules (double-click, Cmd-click) have no touch equivalent to copy.
- **Procreate (iPad)**: tap a layer to make it the Primary (active) layer; **swipe right** on a layer to add it as a
  Secondary selection (many allowed); **tap-and-hold to pick up** a layer or group and drag it up or down to reorder;
  moving the Primary moves the Secondaries with it; **swipe right-to-left** reveals Lock, Duplicate, Delete; tap the
  small letter at the right of a layer for blend mode and opacity (Normal shows "N"); press-and-hold the visibility box
  for solo visibility; two-finger tap is Undo. **Layer Select**: touch the canvas to highlight the layer under the
  finger, and a pop-up lists every layer there when several overlap: the touch form of Figma's "Select layer" menu.
  Procreate's 25 or so modes include many outside the W3C list (Shade, Linear Burn, Darker Color, Add, Lighter Color,
  Vivid Light, Linear Light, Pin Light, Hard Mix ...). (P, high)
- **Canva mobile, Affinity on iPad**: not readable here (Canva 403; Affinity's gesture sheet is an image-only PDF and
  its page paths 403). (U)
- **What follows for the app (inference, medium).** On touch, the desktop modifiers need visible replacements: an
  "Enter group" / "Select parent" pair (Figma's Enter / Shift+Enter) as buttons; a "layers here" list on long-press
  (Procreate's Layer Select, Figma's Select layer); reorder by press-and-hold drag in the tree or Up/Down buttons (the
  app's V173 data rows already step Up and Down for touch); swipe or a row menu for lock/hide.

## 3. The alternatives compared: which compositing model the board should copy

Criteria, set before the comparison: (a) what V174's scope names (Figma's model, opacity and blend on every element,
masks); (b) drawable with canvas 2D and with SVG/CSS without dependencies; (c) exports to PDF/print without forced
rasterisation; (d) understandable to an architect.

| Option | (a) scope | (b) canvas / SVG | (c) PDF / print | (d) clarity | Notes |
|---|---|---|---|---|---|
| A. Figma's 18 + Pass through | Full | 17 of 18 in canvas (`lighter` for Plus lighter; no Plus darker); CSS has plus-darker/plus-lighter but support varies (browser agent) | Plus modes are not PDF modes: rasterise those | Two extra modes few architects use | Exact Figma parity |
| B. The W3C/PDF 16 + Pass through (Penpot, Illustrator, PDF) | Full for "16 modes"; isolation via Pass through/Normal as Figma | All 16 in canvas and CSS | All 16 native in PDF, isolated groups native | Same names as Figma | Recommended |
| C. QGIS's 13 | Partial | Addition/Subtract are not W3C modes | Partial | GIS names (Dodge, Burn) | Not a design-tool model |
| D. Opacity only (BIM tools) | Fails the scope | Trivial | Opacity still rasterises in some exporters (QGIS) | Clearest | The AEC baseline |

**Recommendation (for the main note).** B: offer the 16 W3C/PDF modes under Figma's names in Figma's order (Normal,
Darken, Multiply, Color burn, Lighten, Screen, Color dodge, Overlay, Soft light, Hard light, Difference, Exclusion, Hue,
Saturation, Color, Luminosity), plus **Pass through** as the default for frames and groups and Normal meaning
"isolate". The PIPELINE line "the same 16 modes as Figma" should read "the 16 W3C modes, as in Figma (which adds Plus
darker and Plus lighter)". What would change it: the owner asking for strict Figma parity (then add Plus lighter via
`lighter` and accept a raster fallback for Plus darker), or the browser agent finding a W3C mode missing in a target
browser's canvas.

## 4. Prior art table

| Tool | Tree | Clip container | Mask | Blend modes | Opacity | Lock / hide | Align to | Distribute | Rows/columns | Level |
|---|---|---|---|---|---|---|---|---|---|---|
| Figma | Sections > frames > groups/shapes, any depth | Frame with Clip content | Siblings above, until next mask/parent end; Alpha (default), Vector, Luminance | 18 + Pass through, on layer, fill, some effects | Layer and fill | Locks cascade; hidden not selectable on canvas | Selection bounds; parent for one | Equal gaps, ends fixed; Tidy up uses the mode gap | Auto layout (vertical, horizontal, wrap, grid; hug/fill/fixed) | P |
| Penpot | Boards > groups/bools > shapes | Board unless show-content | Bottom child masks the rest of its group; alpha only | W3C 16 | Layer and fill | Lock/hide; selectable in panel | Extreme element's edge | Equal distances | Flex and grid as CSS data | P (code + help) |
| Excalidraw | Flat with group ids | none | none | none read | per element | lock | Selection bounds | Equal gaps; centres when overlapping | none | P (code) |
| Canva | Page > flat ordered elements, groups | Image fills crop to their rect | not read | not in API | "transparency" | locked elements, locked pages | not read | not read | not read | P (API) / U (editor) |
| Illustrator | Layers > sublayers > groups | Clipping masks (U) | Opacity masks (U) | W3C 16 | object, group, layer (U) | yes (U) | U | U | U | S for modes |
| QGIS layout | Items list, groups | Map frames clip | Clipping blend modes inside group-rendered layer groups | 13 | per item | per item visibility, lock position | Align commands | Edges, centres, or equal spacing | none | P |
| ArcGIS Pro layout | Elements, groups, map frames with layers | Map frame | not in pages read | Layer and feature blend (23 modes), on map layers | layer transparency | check box, lock | First selected (default) or page | Gaps (widened to avoid overlap) or centres | none | P |
| Revit sheet | Viewports; detail draw order only | Viewport crop | none | none | none documented for sheets | n/a | n/a | n/a | n/a | P (draw order) |
| Archicad | Classes and 14 stack levels | Drawing frame | none | none read | none read | layers | n/a | n/a | n/a | P (display order) |
| SketchUp LayOut | Layers (regular, shared) > groups > entities | Viewport | clipping masks exist (U) | none | not read | per-page visibility, document-wide lock | not read | not read | not read | P (layers) |
| Vectorworks | Sheet layers > viewports; classes | Viewport crop | none read | none | fill and pen per 2D object; layer | class/layer visibility; viewport overrides | not read | not read | not read | P |
| Procreate (iPad) | Layers > groups | Clipping mask (U) | Layer masks (page fetched, not used) | ~25 (many non-W3C) | per layer | lock, solo visibility | n/a | n/a | n/a | P |

## 5. Edges (where the answer changes)

- **Pass through versus Normal on a group** gives different pixels whenever a child has a non-normal mode: a Multiply
  child darkens the board under a Pass-through group but only its siblings under a Normal one (Figma, W3C 10.3). A
  group with opacity below 100 % must be isolated (rendered offscreen then faded), or overlapping children show
  through each other; in CSS, opacity below 1 creates a stacking context and isolates (W3C 3.4.2). (P)
- **Mask scope differs between tools**: Figma stops at the next mask; Penpot masks the whole group; QGIS masks the
  layer below only. A board copied from Figma with two masks in one group renders differently in Penpot. (P)
- **Vector versus alpha mask** differ only where the mask has partial opacity or soft edges (gradients, blur, PNG
  alpha). (P)
- **Distribute with overlap**: Excalidraw switches to centres; ArcGIS widens the span; Figma's help is silent (U).
  **Distribute "spacing" versus "centres"** differ when items have different sizes (QGIS and ArcGIS offer both). (P)
- **Align reference**: selection bounds (Figma, Excalidraw), first selected (ArcGIS), or the parent when one layer is
  selected (Figma). (P)
- **Tidy up's gap is the mode** of the current gaps, not the mean; with all gaps different, the result is not defined
  in the help (U).
- **Snap tolerance in screen pixels** (Excalidraw 8 px / zoom) versus in page units: at high zoom a page-unit tolerance
  becomes huge on screen. (P for Excalidraw)
- **Text that resizes**: an Auto width text inside a Hug row changes the row's size; a Fixed text can overflow and
  overlap in a row (Figma's own warning). (P)
- **PDF**: Plus darker / Plus lighter / Linear modes have no PDF equivalent (rasterise); QGIS rasterises any opacity
  below 100 %; ArcGIS rasterises even PDF's own HSL modes. (P)
- **Constraints default**: Figma Top and Left versus Penpot Scale changes what happens when a board is resized to a
  new page size. (P)
- **Locked children of locked parents** cannot be unlocked alone in Figma. (P)

## 6. Counter-evidence and limits

- H-a's "16" is the W3C/PDF/Illustrator/Penpot count; Figma is the odd one out with 18. Procreate (~25) and ArcGIS (23)
  go further, so "Figma's list" is not an industry standard; the W3C/PDF list is.
- Figma's mobile app is not a touch editor (P), so the "Figma on iPad" model the scope might assume does not exist;
  touch prior art comes from Procreate (P) and, unread, Canva and Affinity (U).
- The BIM tools' lack of blend modes is absence of evidence in a handful of pages per vendor (medium). The reason
  (plotting, PDF) is our inference (U).
- The Figma help pages are living pages (each carries an update date in late October or early November 2026); the
  behaviour described may change.
- Figma's "smart guides" equal-spacing snap and the Clip content default were not found in the pages read (U).
- Plus darker = linear burn and Plus lighter = linear dodge rest on the API comments and descriptions (P) and on
  ArcGIS's formulas (P), not on a pixel test (the browser agent's experiment).

## 7. Risks and threats to validity

- Two practitioner sources (Canva editor help, Adobe help) were refused: Canva and Adobe facts are API-level (Canva,
  P) or a community transcription (Illustrator modes, S). The Adobe Transparency panel's isolate/knockout options are
  inferred from PDF's group model (P for PDF, U for Illustrator's UI).
- Penpot and Excalidraw are read at one commit each; their behaviour can move.
- No experiment was run on my side: canvas and CSS blend behaviour per browser belongs to the browser research agent.

## 8. What stayed U, and why

- Canva editor: Layers panel, Arrange, lock, transparency slider, smart guides, any blend options (canva.com 403,
  canva.cn reset).
- Adobe Illustrator/InDesign/Express: Transparency panel (Isolate Blending, Knockout Group, opacity masks), layers,
  clipping masks, smart guides (helpx.adobe.com and adobe.com 403).
- Affinity on iPad: layer gestures (image-only gesture PDF; help pages 403 at the guessed paths).
- Figma: the Clip content default; the equal-spacing snap marks; the date the mask types arrived; whether a first click
  inside a top-level frame selects the child.
- Archicad: display order per view on layouts (forum only). SketchUp LayOut: Send to Back limited to one layer (forum
  only, consistent with the help).
- Why BIM layout tools avoid blend modes (our inference).

## 9. References

| What | URL | Read | Date | Level |
|---|---|---|---|---|
| Figma, Apply blend modes to layers, fills, and effects | https://help.figma.com/hc/en-us/articles/360040667874 | whole article | 2026-11-08 | P |
| Figma, Masks | https://help.figma.com/hc/en-us/articles/360040450253 | whole article | 2026-11-08 | P |
| Figma, Frames in Figma Design | https://help.figma.com/hc/en-us/articles/360041539473 | whole article (updated 2026-11-06) | 2026-11-08 | P |
| Figma, The difference between frames and groups | https://help.figma.com/hc/en-us/articles/360039832054 | whole | 2026-11-08 | P |
| Figma, Organize your canvas with sections | https://help.figma.com/hc/en-us/articles/9771500257687 | whole | 2026-11-08 | P |
| Figma, Select layers and objects | https://help.figma.com/hc/en-us/articles/360040449873 | whole | 2026-11-08 | P |
| Figma, Layers 101: Get started; Combine layers | https://help.figma.com/hc/en-us/articles/26584819173271 ; .../26610806345623 | whole | 2026-11-08 | P |
| Figma, Lock and unlock layers | https://help.figma.com/hc/en-us/articles/360041596573 | whole | 2026-11-08 | P |
| Figma, Toggle visibility to hide layers | https://help.figma.com/hc/en-us/articles/360041112614 | whole | 2026-11-08 | P |
| Figma, Adjust alignment, rotation, position, and dimensions | https://help.figma.com/hc/en-us/articles/360039956914 | alignment, snap, distribute, tidy up, nudge, layer order | 2026-11-08 | P |
| Figma, Arrange layers with Smart selection | https://help.figma.com/hc/en-us/articles/360040450233 | whole | 2026-11-08 | P |
| Figma, Measure distances between layers | https://help.figma.com/hc/en-us/articles/360039956974 | whole | 2026-11-08 | P |
| Figma, Set small and big nudge values | https://help.figma.com/hc/en-us/articles/4404575206295 | whole | 2026-11-08 | P |
| Figma, Shape tools | https://help.figma.com/hc/en-us/articles/360040450133 | whole | 2026-11-08 | P |
| Figma, Adjust text dimensions and resizing | https://help.figma.com/hc/en-us/articles/27378154668951 | whole | 2026-11-08 | P |
| Figma, Guide to fills; Adjust the properties of an image | https://help.figma.com/hc/en-us/articles/360041003694 ; .../360041098433 | whole | 2026-11-08 | P |
| Figma, Apply constraints | https://help.figma.com/hc/en-us/articles/360039957734 | whole | 2026-11-08 | P |
| Figma, Guide to auto layout | https://help.figma.com/hc/en-us/articles/360040451373 | flows, padding, gap, sizing, ignore auto layout | 2026-11-08 | P |
| Figma, Guide to the Figma mobile app | https://help.figma.com/hc/en-us/articles/1500007537281 | whole | 2026-11-08 | P |
| Figma Help Center search API (index) | https://help.figma.com/api/v2/help_center/articles/search.json | 14 queries | 2026-11-08 | (index only) |
| Figma plugin API, BlendMode; MaskType; node properties | https://developers.figma.com/docs/plugins/api/BlendMode/ ; .../MaskType/ ; .../node-properties/ | enums; blendMode, opacity, isMask, maskType, clipsContent, locked | 2026-11-08 | P |
| W3C Compositing and Blending Level 1, CRD 21 March 2024 | https://www.w3.org/TR/compositing-1/ | 3.4.1-3.4.3, 9.1, 10.1-10.3 | 2026-11-08 | P |
| MDN, globalCompositeOperation; mix-blend-mode (source) | https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/canvasrenderingcontext2d/globalcompositeoperation/index.md ; .../web/css/reference/properties/mix-blend-mode/index.md | value lists | 2026-11-08 | P (MDN) |
| ISO 32000-1:2008 (PDF 1.7), Adobe's copy | https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf | 11.3.5 Tables 136-137; 11.4; 11.7.4 note | 2026-11-08 | P |
| Penpot source, MPL-2.0, commit 904cdd97 | https://github.com/penpot/penpot | files listed in 2.5 | 2026-11-08 | P (read as text) |
| Penpot help, Layers | https://help.penpot.app/user-guide/designing/layers/ | boards, select, hide/lock, group, mask, align, constraints, opacity and blend | 2026-11-08 | P |
| Excalidraw source, MIT, commit 701b901a | https://github.com/excalidraw/excalidraw | align.ts, distribute.ts, snapping.ts | 2026-11-08 | P (read as text) |
| Canva help (refused) | https://www.canva.com/help/finding-and-arranging-layers/ | 403 | 2026-11-08 | U |
| Canva Apps SDK, Design Editing | https://www.canva.dev/docs/apps/design-editing/ | element types, ordering, common properties, locked | 2026-11-08 | P (API) |
| Adobe help (refused) | https://helpx.adobe.com/illustrator/using/transparency-blending-modes.html | 403 | 2026-11-08 | U |
| Illustrator scripting constants (docsforadobe), commit 714dc133 | https://github.com/docsforadobe/illustrator-scripting-guide | docs/jsobjref/scripting-constants.md, BlendModes | 2026-11-08 | S |
| QGIS-Documentation, commit 83f9bab8 | https://github.com/qgis/QGIS-Documentation | print_layout/overview_layout.rst, layout_items/{layout_items_options,layout_legend,layout_image,layout_scale_bar}.rst, create_output.rst; introduction/general_tools.rst (blend modes) | 2026-11-08 | P |
| ArcGIS Pro 3.5, Apply transparency and blending modes | https://pro.arcgis.com/en/pro-app/3.5/help/mapping/layer-properties/apply-visual-effects.htm | whole | 2026-11-08 | P |
| ArcGIS Pro 3.5, Layout and the Contents pane | https://pro.arcgis.com/en/pro-app/3.5/help/layouts/layout-contents-pane.htm | whole | 2026-11-08 | P |
| ArcGIS Pro 3.5, Work with layout elements | https://pro.arcgis.com/en/pro-app/3.5/help/layouts/work-with-layout-elements.htm | arrange, align, distribute, nudge | 2026-11-08 | P |
| Revit 2026, About the Draw Order of Details | https://help.autodesk.com/cloudhelp/2026/ENU/Revit-DocumentPresent/files/GUID-0481A947-D31A-44C5-9819-5D75A1799484.htm | whole | 2026-11-08 | P |
| Archicad 28, Display Order | https://help.graphisoft.com/AC/28/INT/_AC28_Help/030_Interaction/030_Interaction-102.htm | whole | 2026-11-08 | P |
| SketchUp LayOut, Using Layers | https://help.sketchup.com/en/layout/using-layers | whole (updated 2026-09-29) | 2026-11-08 | P |
| Vectorworks 2024, viewport layer properties | https://app-help.vectorworks.net/2024/eng/VW2024_Guide/Viewports2/Changing_the_layer_properties_of_sheet_layer_or_design_layer.htm | whole | 2026-11-08 | P |
| Vectorworks 2021, Opacity attributes | https://app-help.vectorworks.net/2021/eng/VW2021_Guide/Attributes/Opacity_attributes.htm | whole | 2026-11-08 | P |
| Procreate Handbook, Layers interface; Organize; Blend modes | https://help.procreate.com/procreate/handbook/layers/layers-interface ; .../layers-organize ; .../layers-blend | whole | 2026-11-08 | P |
| Affinity Designer 2 for iPad gesture sheet | https://affin.co/designer2gestures (resources.serif.com PDF) | image only, no text | 2026-11-08 | not usable |
| Graphisoft community, display order threads; SketchUp forum, Send to Back | (search pointers in log #28) | summaries only | 2026-11-08 | U |

## 10. What the code would depend on (for the main note and the second reader)

1. The blend list: W3C 16 under Figma's names and order, Pass through as the group/frame default, Normal = isolate
   (Figma help, W3C 3.4 and 10.3, PDF Tables 136-137, Penpot `shape.cljc:82-98`). P.
2. Layer opacity and fill opacity are separate (Figma API and fills page; Penpot `:opacity` and `:fill-opacity`). P.
3. Mask rule: the bottom-most layer masks the siblings above it in the same parent, up to the next mask; default Alpha,
   optional Vector and Luminance (Figma help and API). Penpot's simpler group-wide alpha mask is the fallback model. P.
4. Frames clip (an option), groups take their children's bounds and cannot take constraints (Figma; Penpot). P.
5. Selection: click selects the outermost unlocked, visible ancestor below the board; double-click/Enter one level
   down; Shift+Enter up; Cmd/Ctrl-click deep; a "layers here" list; locked and hidden excluded from canvas picking but
   selectable in the tree; locks and hides cascade (Figma; Penpot). P.
6. Reorder: tree order is z-order, top of the list in front; Bring forward/to front/backward/to back, within the parent
   (Figma; ArcGIS; QGIS shortcuts Ctrl+] / Ctrl+[ / Ctrl+Shift+] / Ctrl+Shift+[). P.
7. Align to selection bounds (one element: to its parent); distribute equal gaps with the ends fixed, centres when
   items overlap (Figma; Excalidraw). Snapping in screen pixels (Excalidraw 8 px / zoom) with point and gap snaps. P.
8. Nudge 1 and 10 (Figma, points). P.
9. Rows and columns: direction, gap, padding, align, wrap; child sizing hug/fill/fixed; "ignore layout" per child
   (Figma auto layout; Penpot layout schema). P.
10. Text resizing auto width / auto height / fixed; image fill modes fill / fit / crop / tile. P.
11. Shapes: rectangle, line, arrow, ellipse, polygon, star (count 3 to 60). P.
12. Map surround: legend synced to the map's visible layers and filtered to its extent; north arrow synced to map
    rotation with grid or true north and an offset; scale bar fixed segment width or fitted to a mm range (QGIS). P.
