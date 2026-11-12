# One paper space: Pages and Boards as one layout (research, 2026-11-12)

Under `docs/research/research-protocol.md`. Levels: **P** read in the primary source (the vendor's own page, or the
app's code), **S** a dependable secondary source with the gap said, **U** a search summary, kept out of the code.
Written from two working notes in `docs/research/research-one-paper-space/`:

| Working note | Side | Written by |
|---|---|---|
| `app-code-audit.md` | the app's Pages and Boards side by side, by file and line | the main session |
| `practice.md` | AutoCAD, Revit, Archicad, Vectorworks, SketchUp LayOut, Rhino 8, Figma, Autodesk Forma Board: 36 sources, a search log, counter-evidence | research agent 1 |

The owner asked (2026-11-12): "whats the difference between page and board i feel like they are overlapping. the
ortho grid snap also present mode should share those with model layout also like autocad right?", then "it should
be one but u check first".

## 1. Abstract

**The answer: yes, one, with one condition.** Every drawing tool read has one kind of sheet: AutoCAD's Layout,
Revit's Sheet, Archicad's Layout, Vectorworks's sheet layer, LayOut's Page, Rhino's Layout (P). Text, images,
legends, tables and a title block go on that one sheet, beside the scaled views; Revit's help puts images on sheets
"for presentation" and Vectorworks calls sheet layers the "presentation version" of the drawing (P). None of them
has a second paper space for presentation inside the drawing tool.

**The condition (the counter-evidence).** Where a board-like canvas with live analyses exists, it is a separate
product beside the drawing tool, not a second kind of sheet inside it: Autodesk Forma Board (frames, shapes, notes,
live analyses, a presentation mode, Revit sheets brought in), Graphisoft BIMx, Figma Slides (P). And no drawing
tool's pages showed charts or live numbers as sheet content (an absence in what was read, not proof). So merging
puts the app's boards' features (figures, live values, charts, indicators) onto drawing sheets, which no tool read
here does. That is a product choice the app can make; it is not practice.

**Drafting aids are one set everywhere** in every tool read: AutoCAD's and Rhino's one status bar serves model and
layouts; Revit's snaps are session-wide; Vectorworks uses the same grids on design and sheet layers (P). The app
already has one set (`A3D_SNAP`), but hides it on a sheet and ignores it when a viewport is dragged (P, the code).

**Present** is built in only in LayOut among drawing tools, and it presents the same pages, with a page hidden from
it when wanted (P). The app already has one Present for the set; its status-bar "Pres" is a different thing with a
name that sounds the same.

## 2. The question and the hypotheses

The question: should the app's two paper spaces, Pages (sheets) and Boards, become one kind of layout; and should
Snap, Grid, Ortho and Present be shared between the model and the layouts?

| | Hypothesis, written before the searches | Outcome |
|---|---|---|
| H1 | Professional drawing tools have one kind of sheet for drawings and presentation | **Holds** for all six read (practice Q1, P) |
| H2 | Text, images, legends and tables go on that sheet beside the views | **Holds** (practice Q2, P) |
| H3 | Snap, grid and ortho are one set across model and paper | **Holds**, with a nuance: AutoCAD keeps grid and snap spacing per viewport, and Archicad lets each window have its own grid (S, an old page) |
| H4 | Presentation canvases with live data are a separate kind somewhere in practice | **Holds**, as separate products (Forma Board, BIMx, Figma Slides), not inside the drawing tool |
| H5 | The app's two kinds already overlap enough to be one | **Holds**: a board with a page has a sheet's size, title block and viewports since V174 (app audit 2) |

## 3. Method

The app's code read by file and line (app audit). Practice read by a research agent on the vendors' own help pages,
36 sources, each with its URL and date, a search log, a table per question, and a deliberate search for
counter-evidence (practice parts 2 to 5). No experiment was needed: no number in this note goes into the code.
The second reader (the protocol's independent check) is left for the build's spec, where the facts the code uses
are fixed; here the decisions rest on the vendor statements quoted in `practice.md`.

## 4. Findings

### 4.1 What the app has (app audit, P, high)

- **Page** (`A3D.sheets`): number (A101), name, size, viewports (plan, elevation, section at a scale, or a schedule
  as a table), a title block drawn from the project's fields, a layout tab beside Model, model space through a
  viewport, vector (SVG) print. Drawn on a canvas by the model's own renderer.
- **Board** (`A3D.pres.boards`): figures (the site analysis's charts and cards), objects on the one layer table
  (shapes, text, images, title block, frame, map frames, legend, north arrow, scale bar, live text and numbers,
  schedules, indicators, result charts), Properties, align, distribute, stacks, a page size. Drawn as HTML and SVG.
  No number, no layout tab, no sections.
- **Joined already** by one set (`bimPresSeq`), one Present, one Print set (`viewports.js:854`).
- **Split** by two editors, two toolbars, two ways to place a view at a scale (a viewport, a map frame), two title
  blocks, two page-size paths, two renderers.
- **Drafting aids:** one `A3D_SNAP`; hidden on a sheet (`.a3d-onsheet #a3d-snapgrp{display:none}`), ignored by a
  viewport's drag, and shown a second time on the board's own bar.

### 4.2 Practice (practice Q1 to Q4, P unless said)

| | One kind of sheet? | Drawings and presentation on it | Drafting aids | Present |
|---|---|---|---|---|
| AutoCAD | Layout | Viewports, title block, text, tables, images | One status bar, model and layouts; grid look per space | None (VSLIDE is legacy) |
| Revit | Sheet | Views, schedules, legends, text, images "for presentation" | Session-wide snaps | Not found |
| Archicad | Layout (Layout Book, Master Layouts) | Drawings, PDFs; images and text open (practice 7) | Grid per window (S, an old page) | BIMx, a separate app |
| Vectorworks | Sheet layer, "the presentation version" | Viewports, graphic legends (only on sheet layers), text | The same grids on design and sheet layers | Saved views stepped through |
| LayOut | Page, "documents and presentations" | Viewports, text, images, tables, shapes | Object snap confirmed; grid snap open | Start Presentation, the same pages, a page can be hidden |
| Rhino 8 | Layout | Detail viewports, title block, text | One status bar | None |
| Figma | Frames; Slides a separate file kind | Design | One canvas | In Slides |
| Forma Board | A separate product | Frames, shapes, notes, live analyses, Revit sheets brought in | Its own | Its own presentation mode |

### 4.3 What it means for the app

1. One kind of layout is practice, and it is what the owner asked for.
2. Putting live analyses, charts and figures on that one layout goes past practice: the tools that have them keep
   them in a separate product. For this app, a separate product is not on offer (one file, one app), so the choice
   is between one layout that can hold everything, and two kinds kept apart. Nothing read says the first is wrong;
   the risk is a toolbar and a Properties panel that grow too long, which a clear split of the menus answers.
3. A layout needs from today's Page: its number, its tab, sections and schedules as viewports, model space through
   a viewport, vector print. It needs from today's Board: the object model (layers, Properties, align, stacks), the
   design objects, the live values. The board side is the larger and newer (4,976 lines against 2,015), so the
   one layout is best built on the board's object model, with the viewport as one of its objects (the map frame
   already is one), not the other way round.

## 5. The alternatives compared

Criteria first: (1) one place to learn (the owner's ask); (2) what a construction sheet needs (number, tab,
sections, vector print) kept; (3) what a board does today kept; (4) old projects open unchanged; (5) work and risk;
(6) practice.

| | (a) Keep two kinds | (b) One layout, built on the sheet | **(c) One layout, built on the board's objects** | (d) One list, two editors |
|---|---|---|---|---|
| 1 | No | Yes | **Yes** | Half: one list, still two editors |
| 2 | Yes | Yes | Yes, once viewports of every kind and SVG print are objects | Yes |
| 3 | Yes | Only after rebuilding the object model on the sheet | **Yes, already there** | Yes |
| 4 | Yes | A board converts to a sheet, lossy until objects exist | **A sheet converts to a layout of viewport objects; a board is one already** | Yes |
| 5 | None | Large: the object model again | **Large but one-way: viewports, numbering, tabs, SVG** | Small |
| 6 | Against (two kinds) | Practice | **Practice, plus live content no tool has on sheets** | Against |

**Recommended: (c)**, in steps, each one usable:
1. **The quick fixes, now** (no merge needed): Snap, Grid and Ortho shown on a layout in the status bar and obeyed
   when a viewport is dragged; the board's own copies of the buttons removed; "Pres" renamed so it does not sound
   like Present.
2. **One list and one tab row:** every page of the set (sheet or board) gets a layout tab and a number, and "+
   Page" and "+ Board" become one "+ Layout" with a choice of what it starts with (an empty sheet with a title
   block, or a site analysis board).
3. **One editor:** a sheet's viewports become objects on the board's object model (a viewport of a plan, an
   elevation, a section or a schedule, at a scale; model space through it), so the Draw menu, Properties, layers
   and align work on a drawing sheet too; the sheet bar's actions (Sheet Setup, Title Block, Export, Print,
   Present) move onto the one bar.
4. **One renderer for print:** the layout's vector print (SVG) covers the design objects as well as the viewports.

What would change it: if the owner wants drawing sheets kept plain (no live values on a construction set), (c) still
holds, with the live and site-analysis objects simply not offered on a layout marked "drawing sheet".

## 6. Edges

| Case | With (c) |
|---|---|
| An old project with sheets | Each sheet opens as a layout whose viewports are viewport objects; its number and tab kept |
| An old project with boards | Each board opens as a layout as it is; a board without a page keeps flowing until given one |
| A board's map frame and a sheet's viewport | One kind of object, a viewport, with the map frame's data layers and basemap as its options |
| Two title blocks | One title block object, ISO 7200 or the US strip, from the project's fields |
| Numbering | Every layout gets a number (A101 style for sheets; the owner may want another prefix for boards: a decision) |
| Present | Unchanged: the set's order, one slideshow; a layout can be left out of it, as LayOut allows |
| Print set | Unchanged in what it prints; one renderer after step 4 |
| Phone | The board's phone layout (stacks shown as columns) applies to every layout |

## 7. Risks and threats to validity

- **Practice is read, not tried:** the agent read help pages; the tools were not run here.
- **Absence of charts on sheets** is what the pages read did not show, not proof that no tool allows them.
- **Archicad's grid per window** rests on an Archicad 18 page (S); Revit's and Archicad's in-app present modes
  were not found, not proven absent.
- **Size of the work:** step 3 changes 23 callers of `bimSheetOnScreen()` and the 16 sheet suites (V110 to V122);
  it needs its own spec and work orders, and the browser check on drawing sheets as well as boards.

## 8. What is still open (U)

Archicad's layout content beyond drawings and PDFs; LayOut's grid snap toggle; Rhino's status bar page (403);
whether Vectorworks saved views include sheet layers (practice part 7). None is a fact the code will use.

## 9. The owner's decisions

**Answered 2026-11-12: the owner accepts all eight as recommended** ("looks good to me"). D3's quick fixes are built
in V175c (below); the merge itself (steps 2 to 4) is the next phase, before V176, with its own spec and work orders.

| # | Question | Evidence | Recommended |
|---|---|---|---|
| D1 | One kind of layout for drawing sheets and presentation boards? | 4.2, H1 | **Yes** |
| D2 | Built on the board's object model, with the viewport as an object (alternative c)? | 4.3, part 5 | **Yes** |
| D3 | The quick fixes first, on their own: Snap, Grid and Ortho shown and obeyed on every layout; the board bar's copies removed; "Pres" renamed (to "Presentation style")? | 4.1, H3 | **Yes, now** |
| D4 | Live values, figures, schedules, indicators and charts allowed on every layout, drawing sheets included? | 4.3 (2) | **Yes**, with a per-layout "drawing sheet" option that hides them from the Draw menu |
| D5 | Every layout numbered and given a tab beside Model; one "+ Layout" in place of "+ Page" and "+ Board"? | part 5, steps 2 | **Yes** |
| D6 | Numbering: one series (A101, A102 ...) for all, or a second prefix for presentation layouts (P101 ...)? | part 6 | **One series**; the prefix is editable per layout |
| D7 | The name in the app: "Layout" (AutoCAD, Archicad, Rhino), "Sheet" (Revit) or "Page" (LayOut)? | 4.2 | **Layout** |
| D8 | When: the quick fixes now, then the merge as the next phase before V176 (its report is built of layouts)? | part 5 | **Yes** |

## 10. References

Every source with its URL, what was read, the date and its level is in `practice.md` part 3 (36 sources) and the
app's code in `app-code-audit.md`. The sources the decisions rest on most:

| Source | Read | Level |
|---|---|---|
| Autodesk AutoCAD help: layouts, paper space, status bar, drafting settings | one Layout; one status bar for model and layouts | P |
| Autodesk Revit help: sheets, images on sheets, snaps | one Sheet; images "for presentation"; session-wide snaps | P |
| Graphisoft Archicad help: Layout Book, Master Layouts, BIMx | one Layout; presenting in BIMx | P |
| Vectorworks help: sheet layers, viewports, graphic legends | sheet layers as "the presentation version" | P |
| SketchUp LayOut help: pages, presentation mode | "documents and presentations"; Start Presentation | P |
| McNeel Rhino 8 help: layouts, detail views | one Layout | P |
| Autodesk Forma Board help | a separate board product with live analyses | P |
| The app at 961fc20 | `app-code-audit.md` | P |
