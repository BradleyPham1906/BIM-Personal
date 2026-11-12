# One paper space or two: practice in professional tools

Part of the research on merging Pages and Boards into one paper space.
Read on 2026-11-12. Every URL below was read on that date.

Levels:
- P: read on the vendor's own help page (fetched, not a search summary).
- S: dependable secondary source, gap stated.
- U: search-engine summary only. Recorded as a pointer, not used as a fact.

The facts are in our own words. Quotes are short.

## 1. The question

In professional CAD/BIM and layout tools, are construction drawing sheets and
presentation boards one kind of paper space or two?

Hypotheses, each falsifiable by one vendor page:
- H1. Each drawing tool has one kind of sheet, used for both construction
  documents and presentation. Falsified by a tool with two sheet kinds inside
  one application.
- H2. Drafting aids (snap, grid, ortho, object snap) are one set of controls in
  one place, used in the model and on sheets alike. Falsified by a tool that
  has a separate, sheet-only set of aids.
- H3. Where a tool has a present mode, it presents its sheets. Falsified by a
  present mode that shows something other than sheets.

## 2. Search log

| # | Query (WebSearch, standard) | What came back |
|---|---|---|
| 1 | AutoCAD help "About Layouts" paper space viewports title block | Autodesk "About Layouts" pages, 2015 to 2025 editions; tutorials (not used). |
| 2 | Revit help presentation boards sheets views on sheets images | Autodesk "Use Images" page; tutorials and blogs (not used). |
| 3 | Archicad help Layout Book layouts drawings master layout | Graphisoft "The Layout Book" pages, AC19 to AC27. |
| 4 | Vectorworks help sheet layers design layers viewports presentation | Vectorworks "Layers overview" and "Presenting the project" pages, 2015 to 2025. |
| 5 | LayOut help center presentation mode pages SketchUp model viewport grid snap | SketchUp "Presenting Your LayOut Document" and interface pages. |
| 6 | AutoCAD help GRIDMODE system variable "Saved in" viewport | GRIDMODE page; "Commands for Grid and Grid Snap" page. |
| 7 | AutoCAD help ORTHOMODE system variable | ORTHOMODE page. |
| 8 | AutoCAD 2024 help "The Status Bar" model space layout tools | Status bar pages, 2018 and 2024. |
| 9 | AutoCAD help GRIDDISPLAY system variable layout paper space | GRIDDISPLAY and GRIDSTYLE pages. |
| 10 | Revit help Snaps dialog settings apply all files session | Revit "Snaps Dialog" and "About Snaps" pages. |
| 11 | Revit help "About Sheets" title block views schedules legends images | Revit "About Sheets" and "Sheets" pages. |
| 12 | Revit help "Snap settings apply to all files open in the session" | Revit "About Snaps" 2026. |
| 13 | Archicad help Layout place drawings figures images text | "Place Drawing on Layout" AC26. |
| 14 | Archicad help Grids and Background dialog snap grid layout window | AC18 "Grid System" and "Grids & Background", AC24 "Set up Snap Grid". |
| 15 | Archicad help BIMx Hyper-model layouts publish presentation | AC27 "Publish BIMx Hyper-Model: Publisher method". |
| 16 | Vectorworks help snapping grid sheet layer | "Snapping to the grid" 2024. |
| 17 | Vectorworks help slide show saved views presentation | Saved views pages; no slide show feature found. |
| 18 | Vectorworks "slide show" saved views help | "Viewing saved views" 2024; a vendor blog (not used). |
| 19 | Vectorworks help sheet layer images worksheets graphic legend title block | "Graphic legends" 2023; title block border pages. |
| 20 | help.sketchup.com LayOut Grid Document Setup Grid Snap Object Snap | "Document Setup", "Marking Dimensions", "Creating a Scaled Drawing". |
| 21 | help.sketchup.com LayOut tables insert spreadsheet | "Adding Tables to a Document". |
| 22 | docs.mcneel.com rhino 8 status bar Grid Snap Ortho Osnap | "The Rhino window", "Snap", user's guide chapter 5. |
| 23 | Figma help Presentation view prototype frames / Slides presenter view | "Play your prototypes"; Slides pages. |
| 24 | Revit presentation boards InDesign or sheets forum | Forums and blogs; found Autodesk "Forma Board" page. |
| 25 | Archicad layouts presentation boards vs InDesign community forum | Graphisoft community threads, blogs. |
| 26 | AutoCAD help VSLIDE command slide file display | "About Slides" page. |

Pages that would not load: Rhino 8 "status_bar.htm" returned HTTP 403.
The LayOut "Arranging" page did not show a Grid Snap sentence in the part read.

## 3. Sources read (P unless marked)

| Id | Tool | URL | What it says (our words) | Level |
|---|---|---|---|---|
| A1 | AutoCAD | https://help.autodesk.com/cloudhelp/2021/ENU/AutoCAD-LT/files/GUID-93E88E2A-3BA8-40C1-8BF5-9A50B716EB34.htm | A layout is a 2D environment for making drawing sheets; its area is paper space. On it: viewports showing scaled model views, a title block, tables and schedules, notes and dimensions. Many layout tabs, each with its own page setup. No sub-kinds of layout. | P |
| A2 | AutoCAD | https://help.autodesk.com/cloudhelp/2022/ENU/AutoCAD-Core/files/GUID-EB16BD83-E8A5-41D7-95DD-E8FE8028B8FD.htm | GRIDMODE: grid on or off; saved in the drawing. | P |
| A3 | AutoCAD | https://help.autodesk.com/cloudhelp/2021/ENU/AutoCAD-Core/files/GUID-CF142B68-675B-452F-B3A8-7831DDB71BD0.htm | ORTHOMODE: constrains the cursor to perpendicular; saved in the drawing. | P |
| A4 | AutoCAD | https://help.autodesk.com/cloudhelp/2022/ENU/AutoCAD-Core/files/GUID-A2271613-3585-439F-9C7C-9341F3F3CB85.htm | Grid and snap variables. GRIDUNIT, SNAPMODE, SNAPUNIT and the other snap variables are described as applying to "the current viewport". GRID shows its pattern in the current viewport. | P |
| A5 | AutoCAD | https://help.autodesk.com/cloudhelp/2021/ENU/AutoCAD-Core/files/GUID-30FC52C7-A734-43EE-A08D-96717A4B4959.htm | GRIDSTYLE (saved in the registry) sets dotted or lined grid separately for model space, the Block Editor, and "sheets and paper space layouts". So the grid exists in layouts; only its look is set per space. | P |
| A6 | AutoCAD | https://help.autodesk.com/cloudhelp/2018/ENU/AutoCAD-Core/files/GUID-E3B34B0A-EA98-45E9-937A-BF5FEF4152DB.htm | One status bar with Grid, Snap, Ortho, Polar, Object Snap, Object Snap Tracking. It also has the Model/Paper toggle; lineweight shows differently in model and layouts; viewport scale shows only when a viewport is selected. Nothing says the drafting aids differ between Model and layout tabs. | P |
| A7 | AutoCAD | https://help.autodesk.com/cloudhelp/2020/ENU/AutoCAD-LT/files/GUID-1ADDF421-BC80-4530-BD0C-2A5C9D1CF026.htm | A slide is a read-only snapshot image, not a drawing; one use is presentations inside the application, shown one by one with VSLIDE or in sequence by a script. | P |
| R1 | Revit | https://help.autodesk.com/cloudhelp/2021/ENU/Revit-DocumentPresent/files/GUID-6D569C3B-B473-4AA9-BB2F-B93088D7D9A9.htm | One sheet view per sheet of the construction set; drawings and schedules placed on it become viewports; a title block. | P |
| R2 | Revit | https://help.autodesk.com/cloudhelp/2020/ENU/Revit-DocumentPresent/files/GUID-3F663CC2-A83E-409F-94F8-ACE7737AE59C.htm | Sheets hold views, schedules, legends, note blocks, title blocks, external text, spreadsheets and images; guide grids align views across sheets. | P |
| R3 | Revit | https://help.autodesk.com/cloudhelp/2023/ENU/Revit-Model/files/GUID-E992A02F-E0B4-4E64-9A3A-391D23F4145F.htm | Images can be imported "directly on sheets for presentation", or into drafting and model views (not 3D or perspective). | P |
| R4 | Revit | https://help.autodesk.com/cloudhelp/2026/ENU/Revit-Customize/files/GUID-A3947840-1F30-41D7-AF75-B61687952A07.htm | Snap settings apply to all files open in the session and are not saved with the project. | P |
| R5 | Revit | https://help.autodesk.com/cloudhelp/2025/ENU/Revit-Customize/files/GUID-3C6FDBDC-8FCC-4CEA-A887-C1FDD189D81C.htm | One Snaps dialog (Manage tab): Snaps Off, length and angle increments, object snaps, temporary overrides. No per-view or per-sheet set. | P |
| R6 | Revit / Forma | https://help.autodesk.com/cloudhelp/2026/ENU/Revit-HaveYouTried/files/GUID-83314CAC-DC20-49B0-B5AF-30FF2B2CA8B2.htm | Forma Board: a separate digital whiteboard for AECO teams. It pulls Revit sheets, proposals and analyses (static or live) from Autodesk Docs; adds pen strokes, text, arrows, shapes, sticky notes and comments; arranges content in frames; has a presentation mode. It does not replace Revit sheets, and marks on the board do not change the sheets. | P |
| G1 | Archicad | https://help.graphisoft.com/AC/25/INT/_AC25_Help/070_Documentation/070_Documentation-89.htm | One Layout Book per project: Subsets, Layouts, Master Layouts (size, shared items such as a logo), Drawings placed on Layouts. No other sheet kind. | P |
| G2 | Archicad | https://help.graphisoft.com/AC/26/INT/_AC26_Help/070_Documentation/070_Documentation-94.htm | A Drawing on a Layout can be a view of this project, a view of another Archicad project, or an external file such as PDF. Images are not named on this page. | P |
| G3 | Archicad | https://help.graphisoft.com/AC/18/INT/AC18Help/02_Interaction/02_Interaction-67.htm | Grids can be defined separately for the Floor Plan and each Section/Elevation/IE, 3D Document, Detail/Worksheet or Layout window. Archicad 18 edition; not re-checked on a current edition. | P (old edition) |
| G4 | Archicad | https://help.graphisoft.com/AC/24/INT/_AC24_Help/030_Interaction/030_Interaction-49.htm | Snap grid set in View > Grid & Editing Plane Options > Grids & Background. Does not state scope. | P |
| G5 | Archicad / BIMx | https://help.graphisoft.com/AC/27/INT/_AC27_Help/100_Visualization/100_Visualization-16.htm | A BIMx Hyper-model is published from a Publisher Set holding Layouts or Subsets plus 3D views; camera-path gallery items can be combined into a presentation in BIMx (a separate app). | P |
| V1 | Vectorworks | https://app-help.vectorworks.net/2022/eng/VW2022_Guide/Structure/Concept_Layers%20overview.htm | Two layer kinds: design layers (draw and model, at scale) and sheet layers (always 1:1, "presentation versions" of the drawing: viewports, title block borders, notes, annotations). One sheet kind. | P |
| V2 | Vectorworks | https://app-help.vectorworks.net/2021/eng/VW2021_Guide/Viewports1/Presenting_the_project.htm | Sheet layer viewports show design layers, clip cubes or Renderworks cameras, each with its own scale, render mode and visibility; sheet layers keep their own print settings. | P |
| V3 | Vectorworks | https://app-help.vectorworks.net/2023/eng/VW2023_Guide/Annotation2/Graphic_legends.htm | The Graphic Legend tool works on sheet layers only, not design layers. | P |
| V4 | Vectorworks | https://app-help.vectorworks.net/2024/eng/VW2024_Guide/Basic2/Snapping_to_the_grid.htm | Snap and reference grids help drawing "on both design and sheet layers"; grid snap can be set in document setup; Snap to Grid is a tool in the snapping set. | P |
| V5 | Vectorworks | https://app-help.vectorworks.net/2024/eng/VW2024_Guide/Structure/Viewing_saved_views.htm | Saved views can be stepped through in order (Navigation palette order, or alphabetical). Not a sheet slideshow. | P |
| S1 | LayOut | https://help.sketchup.com/en/layout/creating-documents-layout | LayOut makes "documents and presentations" of SketchUp models; templates hold settings, titles and elements reused across presentations. | P |
| S2 | LayOut | https://help.sketchup.com/en/layout/presenting-your-layout-document | View > Start Presentation fills the screen with the document's pages; arrows move page to page; a page can be hidden from the presentation; models can be orbited and animations played; Freehand annotations can be saved to a new layer. | P |
| S3 | LayOut | https://help.sketchup.com/en/layout/document-setup | Document Setup holds Paper (size, margins) and Grid (lines or points, major and minor spacing, print grid, clip to margins, grid on top). Auto-Text drives title block text. | P |
| S4 | LayOut | https://help.sketchup.com/en/layout/marking-dimensions | Object Snap is toggled in the Arrange menu. | P |
| S5 | LayOut | https://help.sketchup.com/en/layout/adding-tables-document | Table tool; Excel or CSV can be inserted as a linked table. | P |
| S7 | LayOut | https://help.sketchup.com/en/layout/introducing-layout-interface | The document window is where you add SketchUp models, images and text; a Pages menu manages pages. | P |
| S6 | LayOut | https://help.sketchup.com/en/layout/creating-scaled-drawing | Grid settings live in Document Setup and work during scaled Draw Mode. | P |
| H1 | Rhino 8 | https://docs.mcneel.com/rhino/8/help/en-us/commands/layout.htm | A layout is the printable sheet. Detail viewports show model views at their own scale; borders, title blocks, text, dimensions, notes, bills of materials, scale bars. Images and tables not named. | P |
| H2 | Rhino 8 | https://docs.mcneel.com/rhino/8/help/en-us/user_interface/rhino_window.htm | One status bar with Grid Snap, Ortho, Planar, Osnap, SmartTrack panes; each model and layout viewport has a tab. Does not say the panes differ in layouts. | P |
| H3 | Rhino 8 | https://docs.mcneel.com/rhino/8/help/en-us/commands/snap.htm | Snap spacing can apply to the active viewport or all viewports; spacing also in Document Properties > Grid. | P |
| F1 | Figma | https://help.figma.com/hc/en-us/articles/360040318013-Play-your-prototypes | Present opens presentation view in a new tab; only content inside frames can be presented; order comes from frame position or prototype links. | P |
| F2 | Figma | https://help.figma.com/hc/en-us/articles/24170630629911-Create-a-slide-deck | Slide decks are a distinct file kind in Figma Slides (own icon in the file browser), built and presented there. | P |
| C1 | Forums | https://archinect.com/forum/thread/15946/illustrator-or-indesign ; https://community.graphisoft.com/t5/Dokumentation/layout-in-indesign/m-p/433833 | Practitioners often make presentation boards in InDesign or Illustrator, linking PDFs exported from Revit or Archicad. Threads are old (about 2003 to 2011 for Archinect). | S (forum opinion, dated, not a survey) |

## 4. Tables per question

### Q1. One kind of sheet or two?

| Tool | Sheet kind(s) | Name | Evidence |
|---|---|---|---|
| AutoCAD | One | Layout (paper space) | A1 |
| Revit | One | Sheet (sheet view) | R1, R2, R3 (images on sheets "for presentation") |
| Archicad | One | Layout, in the Layout Book; Master Layout is its template | G1, G2 |
| Vectorworks | One sheet kind (the other layer kind is the model) | Sheet layer; the help itself calls it the presentation version | V1, V2 |
| SketchUp LayOut | One | Page (of a LayOut document), for documents and presentations | S1, S2 |
| Rhino 8 | One | Layout | H1 |
| Figma | Two products: frames in Figma Design; slides in Figma Slides | Frame / slide deck | F1, F2 |
| Autodesk Forma | A separate whiteboard beside Revit sheets | Forma Board | R6 |

H1 holds for every drawing tool read. Inside each drawing application there is one
sheet kind. The second kind appears only as a separate product (Forma Board,
BIMx, Figma Slides, InDesign).

### Q2. What can be placed on the sheet?

Y = the vendor page read says so. "not named" = the page read does not mention it
(it may still exist; see open items).

| Tool | Scaled model viewports | Title block | Text | Images | Shapes / 2D graphics | Schedules / tables | Legends | Charts |
|---|---|---|---|---|---|---|---|---|
| AutoCAD | Y (A1) | Y (A1) | Y notes (A1) | not named | Y, any 2D object in paper space (A1: notes, dimensions) | Y tables (A1) | not named | not named |
| Revit | Y (R1) | Y (R1) | Y (R2) | Y (R2, R3) | not named | Y schedules, note blocks (R2) | Y (R2) | not named |
| Archicad | Y Drawings (G1, G2) | Y via Master Layout (G1) | not named on pages read | PDF and drawing files (G2) | not named | not named | not named | not named |
| Vectorworks | Y (V1, V2) | Y title block border (V1) | Y notes (V1) | not named | not named | worksheets mentioned only in passing (U) | Y graphic legend, sheet only (V3) | not named |
| LayOut | Y SketchUp models, orbit-able (S1, S2) | Y via template and Auto-Text (S1, S3) | Y (S1) | Y (S7) | Y drawing tools (S1) | Y, with linked Excel/CSV (S5) | not named | not named |
| Rhino 8 | Y detail viewports at scale (H1) | Y (H1) | Y (H1) | not named | Y (H1: hatches, borders) | bills of materials (H1) | not named | not named |
| Forma Board | sheets and models from Docs (R6) | inside the sheets it pulls | Y (R6) | not named | Y shapes, arrows, sticky notes (R6) | not named | not named | live analyses (R6) |

No drawing tool's page read names charts or live numbers as sheet content. The only
"live analysis" content found is on Forma Board, the separate whiteboard.

### Q3. Drafting aids: one global set or separate per space?

| Tool | Where toggled | Scope found | Separate sheet-only set? | Evidence |
|---|---|---|---|---|
| AutoCAD | One status bar; F7 grid, F8 ortho, F9 snap, F10 polar | ORTHOMODE and GRIDMODE saved in the drawing; grid and snap spacing per current viewport; grid look set per space (GRIDSTYLE) | No. The same buttons work on the Model tab and layout tabs. | A2 to A6 |
| Revit | Snaps dialog, Manage tab | Session-wide, all open files, not saved with project | No | R4, R5 |
| Archicad | View > Grid & Editing Plane Options | Grids defined per window, Layout windows included (AC18) | Settings are per window, but it is the same set of controls | G3, G4 |
| Vectorworks | Snapping tool set (Snap to Grid tool) | Document settings; same grids on design and sheet layers | No | V4 |
| LayOut | Grid: View menu and Document Setup; Object Snap: Arrange menu | Per document (LayOut is only paper space) | Not applicable | S3, S4, S6 |
| Rhino 8 | Status bar panes | Snap spacing per active viewport or all; grid in Document Properties | No. Each model and layout viewport has a tab under one status bar. | H2, H3 |

H2 holds: no tool read has a second, sheet-only set of drafting aids. AutoCAD and
Rhino keep one status bar for model and layouts. Some values are stored per
viewport or per window (AutoCAD snap spacing, Archicad grids), but the controls
are the same ones.

### Q4. One present mode, and does it present sheets?

| Tool | Present mode | Presents sheets? | Evidence |
|---|---|---|---|
| AutoCAD | No modern present mode found. Legacy slides (VSLIDE, scripts) show read-only snapshots. | No; slides are images, not layouts | A7 |
| Revit | None found on pages read | Not applicable | R1, R2 (open item) |
| Archicad | Not in Archicad on pages read; BIMx (separate app) presents gallery items; layouts can be published into it | Layouts go to BIMx; the presentation is of gallery items | G5 |
| Vectorworks | No slideshow found; saved views can be stepped in order | Not shown to include sheet layers | V5 |
| LayOut | Yes, one: View > Start Presentation | Yes, the document's pages; pages can be hidden | S2 |
| Figma | Design: presentation view of frames. Slides: a separate deck product | Frames, or slides | F1, F2 |
| Forma Board | Yes, presentation mode of the board | Presents board frames holding sheets and analyses | R6 |

H3 holds where a present mode exists inside the drawing tool (LayOut): it presents
the same pages used for drawings.

## 5. Counter-evidence (searched for on purpose)

1. Autodesk Forma Board (R6, P). Autodesk ships a separate whiteboard beside
   Revit sheets: frames, shapes, sticky notes, live analyses, presentation mode.
   It does not replace sheets and does not write back to them. This is the
   closest match to the app's Boards, and it is a second kind, kept apart from
   the sheet set. The reason given is collaboration and early design narrative,
   not documentation. It is a separate cloud product, not a sheet type in Revit.
2. Archicad and BIMx (G5, P). Layouts stay one kind in Archicad, but the
   interactive presentation lives in BIMx, a separate app fed with layouts and
   3D views.
3. Figma (F1, F2, P). A design tool with frames on a canvas still made slide
   decks a separate file kind (Figma Slides).
4. Practice (C1, S). Many practitioners build presentation boards outside the
   drawing tool (InDesign, Illustrator), linking PDFs exported from Revit or
   Archicad. Reasons given: typography, multi-page layout, lighter files.
   Gap: forum opinions, mostly old, not a survey.
5. Vectorworks (V1, P) is not counter-evidence: its two layer kinds are model
   and sheet, not two kinds of sheet. Its help calls the one sheet kind the
   "presentation version".

So the counter-evidence is about separate products for boards and
collaboration, not about a second sheet type inside a drawing application.
Users' complaints found were about tool choice (Revit or InDesign), not about
having one or two sheet kinds in one app. No complaint of either kind was found
at level P or S beyond C1.

## 6. Confidence

| Finding | Confidence | Why |
|---|---|---|
| Each drawing tool read has one sheet kind | High | Six vendor pages agree; none shows a second sheet kind. |
| Drafting aids are one set shared by model and sheets | High for AutoCAD, Revit, Vectorworks; medium for Rhino (pages do not say so outright); medium for Archicad (per-window grids, AC18 page) | See Q3. |
| Board-like canvases with live data exist as separate products | High | Forma Board, BIMx, Figma Slides pages. |
| Charts and live numbers are not normal sheet content in drawing tools | Medium | Absence on pages read is not proof. |

## 7. Open items

- Revit and Archicad: no in-app present or slideshow mode found; a direct search
  of their help indexes was not done.
- Archicad: per-window grid scope read only on the AC18 page; re-check on AC27 or AC28.
- Archicad: images, text and figures on layouts not confirmed on a page read.
- Vectorworks: whether saved views can step through sheet layers; worksheets on
  sheet layers not read on a vendor page (U only).
- LayOut: Grid Snap toggle not found in the text read (S4 confirms Object Snap only).
- Rhino 8: status bar page returned 403; whether Ortho and Osnap state is global
  is implied, not stated.
- AutoCAD and Rhino: images and charts on layouts not read on a vendor page.
- No survey of users; forum evidence is level S and old.
