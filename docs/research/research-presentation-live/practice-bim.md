# V175 research, agent 1: how professional BIM and CAD tools keep board elements live

Working note for phase V175 "Presentation P2: live elements". Written 2026-11-08 by research agent 1
(practice in BIM/CAD tools). It follows `docs/research/research-protocol.md`: evidence levels P, S, U;
a search log; three or more sources per topic where they exist; a search for counter-evidence;
confidence per finding. It is one of the phase's parallel notes. The phase note is written from it and
from the others, and a second reader checks it.

## 1. The question

**The question.** When paper space shows something drawn from the model (a view, a schedule, a number,
a line of text bound to project data), how do the professional tools keep it current, and what do they
do when the user edits it there? The answer has to settle six design points for V175's board elements:

1. What kinds of thing are linked.
2. When a linked element updates: always, when its page opens, on demand, or on save, plot or export.
3. How a stale element is shown, and whether that mark prints.
4. What an override is, and what it covers (the whole element, or one group of properties).
5. How Reset works, and whether an update keeps an override or discards it.
6. What the element shows when its source is deleted, and what token syntax the autotext uses.

**Hypotheses** (each one a claim the evidence could prove wrong):

- H1. Every tool that has linked views also offers a frozen or manual mode, not only a live one.
- H2. Staleness is shown by a mark on screen that does not print.
- H3. An override is held per group of properties (camera, style, layers), and each group has its own
  Reset, rather than one Reset for the whole element.
- H4. When a source goes missing, the tools show a visible placeholder or error string rather than a
  blank or a silently wrong value.
- H5. Autotext uses a delimited token that the user can type by hand: `<...>`, `%<...>%` or `#...#`.
- H6. Updating from the source keeps the user's overrides.

The outcomes are in section 3.7.

## 2. Method and search log

**Sources by kind.** The vendors' own help pages (Graphisoft, Trimble SketchUp, Autodesk Revit and
AutoCAD, Vectorworks, McNeel), read as text. Vendor release notes (SketchUp 2026.0). One vendor API
reference (AutoCAD ActiveX). Practitioner forum threads, for counter-evidence: forums.sketchup.com, read
through its Discourse JSON. Other forums refused a script, and only their search summaries were seen.
Those summaries are recorded as U.

**How the pages were read.** Each page was fetched with `curl` and stripped to text by a small Python
script, then read. The scripts and downloads were temporary, kept in `/tmp/v175r/` outside the
repository, and are not committed. No experiment was needed: no claim here is about behaviour that can
be measured from this machine, because none of these products runs here.

**Refused hosts (2026-11-08):**

| Host | Result | What was done instead |
|---|---|---|
| community.graphisoft.com | 403 to curl and to WebFetch | Search summaries only (U) |
| helpcenter.graphisoft.com/knowledgebase/41618 | 301, redirected to community.graphisoft.com, then 403 | Search summary only (U) |
| forums.autodesk.com | 403 to curl and to WebFetch | Search summaries only (U) |
| forum.vectorworks.net | 403 to curl | Search summaries only (U) |
| forums.sketchup.com, HTML pages | 403 to WebFetch | **The Discourse endpoint `/t/<id>.json` answers curl with 200.** Threads were read in full that way. Worth reusing in later research. |
| app-help.vectorworks.net, `Dimensions_Notes/Data_tags.htm` and `Creating_data_tags.htm` | 403 (probably wrong paths) | `Annotation2/Data_tag_settings.htm` read instead (200) |
| help.sketchup.com, `/en/layout/inserting-sketchup-models-layout` | 404 | Not needed |
| help.autodesk.com, 2026 AutoCAD-Core "About Using Formulas in Table Cells" | 404 | The 2026 AutoCAD-LT-MAC copy of the same GUID was read (200) |

**Search log** ("WS" is the web search tool; "curl" is a direct read of the page):

| # | Where | Query or URL | What came back | Kept or set aside, and why |
|---|---|---|---|---|
| 1 | WS, help.graphisoft.com and community | Archicad Drawing Manager update type Auto Manual drawing status | AC24 Drawing Manager, AC25 Drawing Settings, 8 community threads | Kept the two help pages (read: P). Threads are counter-evidence leads only (host refused). |
| 2 | WebFetch | AC24 Drawing Manager page | The status list, the Update and Check Status commands | Kept, P (AC24) |
| 3 | WebFetch | AC25 Drawing Settings page | Update Type Auto and Manual; Store Drawing in Project File | Kept, P (AC25) |
| 4 | WS, help.graphisoft.com | Archicad 27 autotext dialog categories | AC27 Autotext, How to Insert Autotext, Text/Autotext Label | Kept |
| 5 | curl | AC27 pages 066, 067, 068, 069 (keywords), 072; AC22 page 073 | The full text of each | Kept, P. The AC27 keyword table is used; the AC22 table only as a check of change over time. |
| 6 | WS, help.graphisoft.com | Archicad drawing title "linked properties" autotext | The AC22 keywords page, Drawing Settings in AC19, linked section markers | "Linked properties" not found. Left open (U). |
| 7 | WS, help.sketchup.com | LayOut Update Reference out of date References | The "Managing Changes" page and Document Setup | Kept |
| 8 | curl | 7 LayOut help pages (managing references, selecting scenes, auto-text, labels, tables, dashes, typing text) | Article text, 0.6 to 16 kB each | Kept, P |
| 9 | WS, open web | LayOut viewport scene "(Modified)" reset scene camera override | About 18 forum threads | Read 6 threads through the JSON endpoint (S as practice). No help page names "(Modified)". |
| 10 | WS, help.sketchup.com | LayOut "tag overrides" viewport revert | The "Working with Dashes" page, forum tips | Kept the help page (P) |
| 11 | WebFetch | SketchUp Desktop 2026.0 release notes | The C API override functions; table reference bugs | Kept, P |
| 12 | curl JSON | forums.sketchup.com threads 225138, 160597, 146169, 255744, 275627, 243365, 262449 | Full posts | Kept as practice and counter-evidence (S) |
| 13 | WS, help.autodesk.com | Revit label title block parameter project information | 10 Revit help pages, 2013 to 2025 | Kept the 2021 and 2022 pages (read: P) |
| 14 | WS, help.autodesk.com | Revit views on sheets one sheet only, schedules | Add Views to a Sheet (2023), and others | Kept, P |
| 15 | WS, help.autodesk.com | Revit change engine, bidirectional associativity | Revit LT 2023 GetStarted page; a patent | Kept the help page (P). The patent was set aside: not the vendor's documentation. |
| 16 | WS, open web | Revit title block label "?" for an empty parameter | Autodesk forum threads | Host refused; summary only (U) |
| 17 | WS, help.autodesk.com | AutoCAD FIELDEVAL bitcode | FIELDEVAL pages, 2016 to 2026, several languages | Kept the 2025 page (curl: P). The LT 2022 for Mac copy reads bit 8 as "Not used". Recorded as a version difference. |
| 18 | curl | AutoCAD 2025: About Using Fields, FIELDDISPLAY, DATALINKNOTIFY, About Linking a Table, DATALINKUPDATE, Field dialog, FIELD, Update Fields, UPDATEFIELD, To Insert a Field | The full text of each | Kept, P |
| 19 | WS, open web | "Convert Field to Text" AutoCAD | AutoCAD Architecture 2016 help; nanoCAD | Kept the AutoCAD Architecture page (P, for that product) |
| 20 | WS, then curl | "%<\AcVar" field code | Forum and CAD-tip sites; the AutoCAD ActiveX FieldCode page | Kept the ActiveX page: Autodesk's own example of the field code string (P). The tip sites were set aside. |
| 21 | WS, then curl | AutoCAD "About Using Formulas in Table Cells" | 2026 LT-MAC copy | Kept, P |
| 22 | WS, open web | AutoCAD field not updating, FIELDEVAL, publish | Autodesk forum threads | Host refused; summary only (U), counter-evidence |
| 23 | WS, then curl | Vectorworks viewport out of date red border update | Pages from 2016 and 2024 | Kept the 2024 "Updating viewports" and "Viewport status" pages (P) |
| 24 | WS, then curl | Vectorworks title block text linked to data records | 2025 page | Kept, P |
| 25 | WS, then curl | Vectorworks data tag field definition | 2025 "Data tag settings" | Kept, P |
| 26 | WS, then curl | Vectorworks worksheet recalculate | 2026 "Worksheet window" | Kept, P |
| 27 | WS, forum.vectorworks.net | Vectorworks data tag orphaned or disassociated | Forum threads | Host refused; summary only (U) |
| 28 | WS, then curl | Rhino 8 text fields | docs.mcneel.com Rhino 8 "Text fields" | Kept, P |
| 29 | WS, open web | Archicad autotext not updating, drawing title wrong | Graphisoft community threads | Host refused; summary only (U), counter-evidence |
| 30 | WS, forums.sketchup.com | LayOut auto-text label wrong value after update | 10 threads | Two read in full through JSON (S) |

## 3. Findings by tool

Level: P is the vendor's own page, read here; S is a dependable secondary source (for practice, several
independent practitioners agreeing); U is a search summary only. Confidence is high, medium or low.

### 3.1 Archicad (Graphisoft)

**What is linked.** A Drawing placed on a Layout is linked to a source: a view of the project (plans,
sections, schedules and the rest, through the View Map) or an external file. Autotext fills text from
the project, the layout, the drawing, a chosen reference drawing, or the system. Labels can carry
autotext about the element they point at, for example "Fire Rating:" followed by that element's fire
rating (AC27, "Text/Autotext Label Content"). P, high.

**Update type, and when updates run.** Drawing Settings (AC25) gives two choices:

- **Auto:** "Drawing will be updated automatically when the layout is activated."
- **Manual:** "The Drawing is frozen in the state its source view or file was in when placed on the
  layout."

"Store Drawing in the Project File" is "Checked automatically for Manual-update Drawings" (AC25, P).
The Drawing Manager page (AC24) adds: "A Drawing set to Automatic update will be updated as soon as you
activate its Layout or window." An Auto drawing therefore does not redraw while its layout is out of
sight. It redraws when someone opens the layout. P, high, though the pages are AC24 and AC25 and the
AC27 copy of these two pages was not read.

**Status: how staleness is shown.** The Drawing Manager (AC24, P, high) lists a status for each drawing:

- **OK:** "Drawing is updated."
- **Modified:** "Source has been modified. Click the Update button to update the drawing."
- **Missing:** "The source of the linked drawing cannot be found."
- **Not Accessible:** the user has no access to the source (Teamwork rights).
- **To be Updated:** temporary, while the drawing waits in a set being updated.
- **Updating:** temporary, while the drawing is being updated.
- **Embedded:** "This Drawing's link has been broken and cannot be updated." The former source is shown
  for information only.
- **Needs Checking:** the background quick-check "cannot determine definitively whether the drawing needs
  an update or not". The Check Status command settles it.

Archicad's word "Modified" means the source has changed and the drawing is stale. LayOut uses the same
word for the opposite case: the board has been changed away from its source (section 3.2). V175 should
name the two states differently.

**Source deleted.** "Missing" is the status for a source that cannot be found. No page read here says
in so many words that deleting the source view produces Missing. "Embedded" is the state once the link
is broken on purpose. The drawing keeps its last image in both cases. P for the statuses; the step from
"deleted" to "Missing" is U, medium.

**Overrides.** A placed drawing has its own settings (scale, frame, title, pens and colours), set in
Drawing Settings. A Manual drawing is the override at whole-drawing level: it is frozen until the user
updates it. No partial override of the kind LayOut has (camera only, layers only) was found in the
pages read. P for Manual; the absence of partial overrides is not proven (U).

**Autotext** (AC27, P, high).

- **What it is.** "An Autotext is a text element containing a definition filled in automatically by the
  program." Its data "is automatically updated to follow any changes in the model, layout or drawing."
  Autotext is always live. No update setting was found for it.
- **Where it can be used.** In any text, in Text/Autotext Labels, in GDL objects including markers, in
  Publisher item names, and in the IDs of interior elevation viewpoints.
- **How it is inserted.** Through the Insert Autotext button in the Formatting Palette, or the right-click
  menu in the Text Editor. The dialog lists categories with a preview. Static text and any number of
  autotexts can be mixed in one block.
- **Missing data.** "If the referenced information is not available, you will see a placeholder text.
  When the missing information becomes available, the placeholder text is immediately updated with the
  relevant data." Also: "File-dependent system autotexts will be undefined until you save your project
  file at least once." The exact wording of the placeholder is not given.
- **Sources** ("How to Insert Autotext"): project information (File > Info > Project Info); the layout
  (name or ID, subset, number of layouts); the drawing (name, scale, magnification); an Autotext
  Reference Drawing; and the system (file name, path, dates).
- **The reference drawing.** One drawing can be set as the Autotext Reference ("Set as Autotext
  Reference"). Autotext can then refer to a drawing other than the one the text sits beside. "If you
  later define a different drawing as Autotext Reference, earlier Autotexts referring to the original
  drawing will remain unchanged." A binding is captured when it is made, not re-pointed later. That is a
  useful precedent for V175.

**Token syntax** (AC27 "Autotext Keywords", P, high). In GDL scripts autotext is written as an
upper-case keyword in angle brackets. In the Text Editor it is picked from the dialog. The categories
and some keys:

| Category | Keys (examples) |
|---|---|
| Project Details | `<PROJECTNAME>`, `<PROJECT_DESCRIPTION>`, `<PROJECT_ID>`, `<PROJECT_CODE>`, `<PROJECTNUMBER>`, `<PROJECTSTATUS>`, `<KEYWORDS>`, `<NOTES>`; Project Custom, "created dynamically" |
| Site Details | `<SITE_NAME>`, `<SITE_ID>`, `<SITEFULLADDRESS>`, `<SITECITY>`, `<SITECOUNTRY>`, `<SITEGROSSPERIMETER>`, `<SITEGROSSAREA>`; Site Custom |
| Building Details | `<BUILDING_NAME>`, `<BUILDING_DESCRIPTION>`, `<BUILDING_ID>`; Building Custom |
| Contact Details | `<CONTACT_FULLNAME>`, `<CONTACT_ROLE>`, `<CONTACTCOMPANY>`, `<CONTACTEMAIL>`, `<CAD_TECHNICIAN_FULLNAME>` and others |
| Client Details | `<CLIENT_FULLNAME>`, `<CLIENTCOMPANY>`, `<CLIENTFULLADDRESS>` and others |
| Layout | `<LAYOUTID>`, `<LAYOUTNAME>`, `<LAYOUTNUMBER>`, `<NUMOFLAYOUTS>`, `<SUBSETID>`, `<SUBSETNAME>`, `<MASTERLAYOUTNAME>`, `<MASTERLAYOUTWIDTH>`, `<LAYOUTNUMBERINCURRENTSUBSET>` |
| Layout Revision | `<CURRENTREVISIONID>`, `<CURRENTTRANSMITTALSETDATE>`, `<CURRENTTRANSMITTEDBY>` |
| Drawing | `<DRAWINGID>`, `<DRAWINGNAME>`, `<DRAWINGSCALE>`, `<MAGNIFICATION>`, `<ORIGINALSCALE>`, `<RENOVATIONFILTER>` |
| Reference | `<DRAWINGNAME_R>`, `<LAYOUTNAME_R>` and others ("_R" suffix) |
| System | `<LONGDATE>`, `<SHORTDATE>`, `<FILENAME>`, `<FILEPATH>`, `<LASTSAVEDAT>`, `<LASTSAVEDBY>`, `<TIME>`, `<YEARLONG>` |

Two details are design-relevant:

- **Area is a named key.** "Site Gross Area" (`<SITEGROSSAREA>`) is a named autotext in Archicad, so a
  project area number belongs among the keys.
- **The table changes between editions.** Between AC22 and AC27 it gained `<PROJECT_ID>`, `<SITE_ID>`,
  `<BUILDING_ID>` and the subset and master-layout keys, and the revision keys were renamed (AC22
  `<CURRENTISSUEDATE>`, AC27 `<CURRENTTRANSMITTALSETDATE>`). A token set changes over time, so stored
  tokens need a version or an alias table. P, high.

**Can autotext be overridden?** Nothing read says so. The user can delete the autotext and type static
text, and that is all the pages describe. U.

**Drawing titles.** "Drawing Titles can be applied only to Drawings which are placed on Layouts" (AC25,
P). The drawing name is chosen by method ("By View: Name only", "By View: ID + Name", "Custom"; AC19
help, seen in a search summary only, U). The "Linked properties" of drawing titles were not found in any
page read. U.

### 3.2 SketchUp LayOut (Trimble)

**What is linked.** LayOut "imports SketchUp models by reference, linking the viewport and associated
model". Other links: images and imported files ("inserted images and imported files become
references"); Excel and CSV tables ("Update Table Reference"); labels with auto-text that read entity
data (scene name, scale, areas, lengths, component attributes); and document auto-text (page, file,
dates, custom). P, high ("Managing Changes and Updates", "Adding Tables", "Labeling Items").

**When updates run.**

- **Model references update on demand.** Document Setup > References has Update, Relink, Unlink, Edit
  and Purge. "Update – Replaces an outdated file with its latest version." P.
- **Check on load.** "Selecting the Check references when loading this document check box causes LayOut
  to check all referenced files each time you open a document. If there are missing or outdated files,
  the Document Setup dialog appears with the References section selected." P, high.
- **Synced updates.** When a model is opened in SketchUp from LayOut and saved, "the LayOut viewport
  reflects the changes". P.
- **Rendering is separate.** In the viewport's panel, "Selecting Auto tells LayOut to render all model
  entities as you make changes. If you don't have Auto selected, a Render option appears." The control
  then says "Rendered" once it is current. P ("Rendering Models").
- **Labels follow the reference.** "LayOut can update a label's Auto-Text if the referenced SketchUp
  model changes. You just have to keep the SketchUp model reference up to date in LayOut." P.
- **Document auto-text.** Custom Text "updates in your document if you change the Auto-Text definition".
  Date Created "only changes if you select File > Save As". Date Published shows "Unpublished" until
  the document has been exported or printed. P, high.

**How staleness is shown.**

- **References.** "If a reference is missing or outdated, its status is in red in the list of files." P.
- **Labels.** "When a label is highlighted in red, LayOut is letting you know that the label's
  connection to the model viewport might be incorrect." The causes listed include "Deleting the geometry
  to which the label is attached" and exploding a component. Two fixes are given: drag the red dot, or
  "Reconnect to Model", which "also removes the red alert on a label that you know is correct". P, high.
- **Clipped text.** A red down arrow appears when text in a label or text box is clipped. It can be
  hidden under View > Warning Symbols. P.
- **The red label warning does not print.** A practitioner says it "does not print or export" (forum
  thread 262449, S, medium). The View > Warning Symbols menu (P) is consistent with that: it is a screen
  display setting.

**Overrides, the closest model for V175** (P where it says so).

- **The model.** "LayOut treats the viewport changes as overrides of the SketchUp model settings." The
  user can revert the settings or push the overrides back: one can "update the SketchUp model with the
  tag overrides changes" ("Working with Dashes", P).
- **Reset controls** (P):
  - **Reset All** in the Viewport section reverts all SketchUp model settings, linework included.
  - **Reset** in the Tags section reverts only the tag settings.
  - For one tag, **Reset Dashes**, **Reset Visibility** and **Reset All** revert that tag's line styling
    overrides.
- **The API.** SketchUp 2026.0 added C API functions "for SketchUp Model Camera and Viewport Overrides",
  `LOSketchUpModelSetViewportOverridesOnModel()` and `LOSketchUpModelResetViewportOverridesOnModel()`
  (release notes, P). Overrides are first-class, stored state, with their own reset.
- **How the mark looks** (S, medium: no help page read describes it; several independent practitioners
  agree across 2020 to 2024 threads):
  - Each section of the SketchUp Model panel (Camera, Style, Effects, Tags) that has been changed away
    from the scene turns a dark grey and shows its own Reset button. Reset All appears at the top.
  - The scene name in the panel is shown as modified.
  - What triggers an override: "changing style, visibile tags, double clicking into the viewport to move
    the camera, manually ticking the Ortho check box, manually selecting a standard view" (thread
    160597).
  - Not every setting counts. "Setting the scale for Parallel Projection scenes and Preserve Scale on
    Resize don't make the Camera section go dark and don't prevent the scene from changing" (thread
    146169).
  - The literal label "(Modified)" was not seen in any help page. A forum summary says the word is shown
    with the scene name (U). H3 holds on P evidence; the exact look is S.
- **Overrides survive an update** (S, medium). "If any scene properties are modified for the viewport in
  LayOut (there's a visible Reset button in the SketchUp Model panel) relinking or updating the SketchUp
  reference should not change those settings back" (thread 255744, 2024). The same poster has "seen the
  styles get reset once in a while". Overrides also travel with copies: "those properties will persist
  to any copied viewports in Layout, even if you change the scene" (thread 160597).
- **Tables are the opposite case** (P, high). "Warning: When you update a table reference, you override
  any local changes you made to the data in LayOut." Imported Excel formatting is re-imported the same
  way, over local formatting. Local edits to a linked table are not protected. That is the pattern
  V175 should avoid.

**Auto-text** (P, high, "Automating Title Block Text").

- **Preset tags:** Address, Author, Company, Current Date, Date Created, Date Modified, Date Published,
  File Name, Page Count, Page Name, Page Number.
- **Other supported tags:** Classifier, ComponentDefinition, ComponentDefinitionAttribute,
  ComponentDescription, ComponentInstance, ComponentInstanceAttribute, Coordinates, DynamicComponent,
  FaceArea, FaceLength, GroupName, Ratio, Scale, SceneDescription, SceneName, SectionName,
  SectionSymbol, Volume.
- **Tag types a user can create:** File Name, Page Name, Page Number, Page Count, Custom Text, Current
  Date, Date Created, Date Modified, Date Published, and **Sequence**. Sequence "automatically inserts
  alpha numeric values in set increments", with a style, a start, an increment and a format, and can be
  renumbered.
- **Syntax.** A tag name in angle brackets, typed into a text box: "type the tag name, such as
  <PageNumber>, into a text box and press Enter". Tags can take parameters: `<Ratio( to )>` displays
  "1 to 10"; `<Coordinates(x,y)>`. Any dynamic component attribute becomes a tag, as `<WindowType>`.
  Coordinates follow the unit format set in SketchUp's Model Info (Labeling page).
- **Missing source.** Only Date Published is documented ("Unpublished"). For entity labels, the red
  highlight and Reconnect to Model. What the text itself shows when its entity is gone is not documented
  in the pages read (U).

### 3.3 Revit (Autodesk)

**What is linked, and when it updates.** Everything. "Revit parametric change engine automatically
coordinates changes made anywhere – in model views, drawing sheets, schedules, sections, and plans"
(Revit LT 2023 Get Started, P, high).

- **Views on sheets.** A view on a sheet is the view itself, not a copy, so there is no stale state and
  no Update command. "Each view can be placed on one sheet only." "Legends and schedules can be placed
  on multiple sheets" ("Add Views to a Sheet", 2023, P, high). To show the same view on two sheets one
  duplicates the view.
- **Schedules on sheets.** A schedule's option to show only the elements in the views on its own sheet
  ("Filter by Sheet") was seen only in a search summary (U).

**Labels in title blocks** ("Add Custom Fields to a Title Block", 2022, and "Enter Project-Specific
Information", 2021, P, high).

- **Two kinds of placeholder.** A title block has project-specific information, which "applies to all
  sheets in the project", and sheet-specific information, which "differs for each sheet".
- **Labels are bound to parameters.** Built-in or shared ones, assigned to the Project Information
  category or the Sheets category ("Use shared parameters (not project parameters)").
- **Editing a label on the sheet edits the source.** Project-specific values: "You can change these
  values in that dialog or on a sheet. Whenever you change project-specific information, Revit updates
  all sheets in the project with the changes." Sheet-specific values: "You can change these values on
  the Properties palette or on a sheet. These changes apply only to the individual sheet."

**Override and Reset.** None. Revit has no notion of a label value that differs from its parameter. A
label cannot diverge; the user writes through it to the parameter. Plain text on a sheet is static and
not linked. P for the write-through; "no override" is our reading of these pages, high.

**Source missing.** Forum summaries say a label whose parameter is absent from the project shows "?"
(U, forum host refused).

**Token syntax.** None that a user types. Labels are built in the family editor by picking parameters.

### 3.4 AutoCAD fields and data links (Autodesk)

**What a field is.** "A field in text contains instructions to display data that you expect to change
during the life cycle of a drawing." Fields can sit "in any kind of text (except tolerances), including
text in table cells, attributes, and attribute definitions" ("About Using Fields in Text", 2025, P,
high).

**The Field dialog** (2025, P, high).

- **Field Category.** Sets which fields are listed, "for example, Date & Time, Document, and Objects".
  Only these three category names are P. The other names often quoted (Sheet Set, Plot, Linked, Other)
  are U, except that the page also describes "Options for Sheet Set and Sheet View Fields",
  BlockPlaceholder and SheetSetPlaceholder fields (P).
- **Format List.** For example a date with or without the day's name, or text in upper case or title
  case.
- **Field Expression.** "The field expression cannot be edited, but you can learn how fields are
  constructed by reading this area."
- **Objects category.** A NamedObject field (a layer, a text style), an Object field (pick an object and
  one of its properties), and Formula (Average, Sum, Count over table cells).

**Token syntax** (P, from Autodesk's own API example). The ActiveX "FieldCode" page builds a text whose
string is `%<\AcVar Date \f "M/d/yyyy">%`: the delimiters `%<` and `>%`, an evaluator (`\AcVar`), the
key (`Date`), and a format switch (`\f "..."`). The full grammar is not documented in the pages read;
forum tip sites say most codes are undocumented (U).

**When fields update: FIELDEVAL** (2025, P, high). Saved in the drawing, initial value 31, "stored as a
bitcode using the sum of the following values":

| Value | Meaning |
|---|---|
| 0 | Not updated |
| 1 | Updated on open |
| 2 | Updated on save |
| 4 | Updated on plot |
| 8 | Updated on use of ETRANSMIT |
| 16 | Updated on regeneration |

- "The Date field is updated by UPDATEFIELD, but it is not updated automatically based on the setting
  of the FIELDEVAL system variable."
- The AutoCAD LT 2022 for Mac copy reads bit 8 as "Not used" (search summary of that page; the bit
  depends on the product).
- **Manual update.** UPDATEFIELD, or right-click > Update Field. "You can update a field manually when
  you want to see the latest value. The Date field never updates automatically and must be updated
  manually" (UPDATEFIELD, P).

So AutoCAD ties freshness to events (open, save, plot, transmit, regenerate) rather than to every
change. Plot is one of the events, so what prints is current.

**How a field is marked** (P, high). "By default, fields are displayed with a light gray background that
is not plotted" (FIELDDISPLAY). FIELDDISPLAY 1 shows the grey background and 0 hides it. "The
background is not plotted." H2 holds.

**What a missing or invalid source shows.** Autodesk's own pages disagree, and both readings are
recorded:

- **"About Using Fields in Text" (2025):** "A field for which no value is available displays hyphens
  (----)", for example a blank Author. "An invalid field displays pound signs (####)", for example
  CurrentSheetName placed in model space.
- **The Field dialog (2025), Field Value:** "displays an empty string (----) if the field value is
  invalid". This uses "----" for invalid, against the page above.
- **The Field dialog (2025), on sheet set fields:** these "store the last values that were used, and
  they display these stored values if the information referenced by the sheet set field is not
  accessible". A Note just below says: "If the information referenced by sheet set field is not
  accessible, the value for the field will be displayed as '####'."

Our reading: "----" means empty and "####" means invalid or unreachable. Sheet set fields may keep the
last good value. **Keeping the last good value, marked stale,** is a real design option for V175: a
number on a board whose source is gone could keep its last value with a stale mark instead of turning
into "####". P for the quotes; the reconciliation is ours, medium.

**Override, Reset and detaching.** A field has no override. The user edits the field's definition
(double-click opens the Field dialog) or detaches it.

- **Convert Field to Text.** Right-click on the field. "This procedure cannot be reversed." This is from
  **AutoCAD Architecture 2016** help, P for that product. Not confirmed in core AutoCAD's pages read
  here.
- **Losing the link.** The Architecture page on manual properties says a converted field loses its link
  to the referenced data (search summary, U).

**Data links and tables** (2025, P, high).

- **Table cells link to Excel or CSV.** To a whole sheet, a row, a column, a cell or a range. "A table
  that contains data links displays indicators around linked cells", and hovering shows the link's
  details.
- **DATALINKUPDATE works both ways.** "Update Data Link" pulls changes from the source. "Write Data
  Link" "updates the linked data in an external file with data that has been changed in a table in your
  drawing".
- **Locking.** "By default, a data link is locked from editing to prevent undesired changes to the linked
  spreadsheet. You can lock cells from data changes, format changes, or both."
- **DATALINKNOTIFY** (initial value 2) controls the "notification for updated or missing data links".
  At 1, an icon shows in the status bar tray. At 2 it adds "a data link file change notification in the
  area of the drawing where the data link requires updating". A balloon placed at the stale element is
  a precedent for V175's stale mark.

**Table formulas** (2026 LT for Mac copy, P). Cells are addressed as A1 and ranges as A5:C10. A formula
starts with "=". Sum, average and count "ignore empty cells and cells that do not resolve to a numeric
value", while "Other formulas display an error (#) if any cell in the arithmetic expression is empty or
contains nonnumeric data". A Cell option can reference a cell in another table in the same drawing.

### 3.5 Vectorworks (Nemetschek)

**Viewports on sheet layers** (2024, P, high).

- **What updates by itself.** "Changes that affect the appearance of a viewport are automatically updated
  for a wireframe viewport. However, if changes require the viewport to be rendered again, the viewport
  will be displayed as an out-of-date viewport."
- **Statuses** ("Viewport status"):
  - **Normal.**
  - **Out of date:** "indicated by red text on the Update button on the viewport's Object Info palette.
    Optionally, an out-of-date viewport also displays with a red and white striped border (see Document
    preferences: Display tab)."
  - **Empty:** a red "X", when the design layer has no objects, they are hidden, or the layer is
    invisible.
  - **Unlinked marker:** a red broken-link icon next to a marker that is not linked to a viewport.
- **Updating.** View > Update Selected Viewports or Update All Viewports, Update in the Object Info
  palette, Update on the context menu, or Update from the Navigation palette. Updates can be cancelled.
- **Printing a stale viewport.** "If a layer with an out-of-date viewport is printed, a message prompts
  you either to print the viewport as an out-of-date viewport or to update the viewport before
  printing." This is the one tool that asks at print time.

**Title block text linked to records** (2025, P, high). Each text block in a title block border has a
Data Type:

- **Not Link:** the user types the text.
- **Link Value:** bound to a record field. "As the value in the selected data record field is edited ...
  the text block updates automatically to display the current value."
- **Custom:** fields and literal text combined. The user must enter spaces between fields.

Here the override is a choice of mode per text block (link or not), not a marked override with Reset.

**Data tags** (2025 "Data tag settings", P, high). Dynamic text on a tag shows data from the tagged
object. The field definition uses `#Record#.#Field#` tokens, as in `#Appliance Record#.#Price# +
#Appliance Record#.#Price# * 0.1`. It allows arithmetic, an IF form (`Yes@#Space#.#Area#>12:No`) and
worksheet functions wrapped as `#WS_ ... #`. Units and precision can be written into the definition,
for example `#m_2_1#`. A tag field can also write its value into a record of the object (the Data
Destination). Forum summaries report tags coming loose from their objects (U).

**Worksheets on sheets** (2026 "Worksheet window", P).

- "Recalculate automatically: Recalculates all worksheet arithmetic functions when cells are edited."
- "Recalculate Active" and "Recalculate All" ("all formulas in all worksheets, whether open or closed").
- For worksheets referenced from Excel, "Push Data to Excel File".

### 3.6 Rhino 8 layouts (McNeel): the token precedent

"Text fields are formulas that are evaluated while Rhino is running and the result is displayed in the
text. All text fields are in the syntax of `%<field and options>%`. When a formula cannot be evaluated
an error string of #### is displayed." (Rhino 8 help, "Text fields", P, high.)

- **Functions** include Area, BlockInstanceCount, BlockName, CurveLength, Date, DateModified,
  DetailScale, DocumentText, FileName, LayerName, ModelUnits, Notes, NumPages, ObjectLayer, ObjectName,
  ObjectPageName, ObjectPageNumber, PageHeight, PageNumber, PageWidth, PaperName, PointCoordinate and
  UserText.
- **Arguments** are quoted strings: `%<Area("ObjectID","Unit")>%`,
  `%<Date("dddd, MMMM dd, yyyy", "en-US")>%`, `%<DocumentText("Key")>%`.
- **Maths and formatting.** Numeric functions combine in arithmetic (`%<NumPages()-1>%`). Python and
  .NET string formatting is allowed (`%<'{:03}'.format(NumPages())>%`). That means an expression
  language inside the token, which a zero-dependency ES5 app should not copy wholesale.
- **Object references.** An object is referenced by its ID; a detail view can be referenced by name
  instead of GUID ("Use detail attribute name"). The same choice of a stable key over a fragile handle
  applies to V175.

### 3.7 Outcome of the hypotheses

- **H1 (a frozen or manual mode exists):** holds for Archicad (Manual), LayOut (update on demand),
  AutoCAD (FIELDEVAL 0, and Convert to Text in Architecture) and Vectorworks (rendered viewports wait for
  Update). It **fails for Revit**: views and labels are always live and there is no frozen mode short of
  exporting. Partly holds.
- **H2 (the stale mark does not print):** holds for AutoCAD (P) and for LayOut's red warnings (S). The
  Vectorworks border is a document display setting, and Vectorworks asks before printing a stale
  viewport, so it does not rely on the mark alone. Holds.
- **H3 (overrides per group, each with its own Reset):** holds for LayOut (P), the only tool with
  partial overrides. The other tools have no partial override. Holds for the one tool that has
  overrides.
- **H4 (a visible placeholder when the source is missing):** holds. Archicad: placeholder text and the
  Missing status. AutoCAD: "----" and "####". Rhino: "####". LayOut: red labels and "Unpublished".
  Revit: "?" (U). **Counter-case:** LayOut 2023 rebinds a label to the nearest component instead of
  marking it, which shows a wrong value silently (section 5).
- **H5 (a delimited token one can type):** holds for Archicad `<KEY>` (GDL scripts), LayOut `<Tag>`
  (typed into text), AutoCAD `%<\AcVar Key \f "fmt">%` (stored form, not normally typed), Rhino
  `%<Fn("arg")>%` (typed), and Vectorworks `#Record#.#Field#`. Revit has none.
- **H6 (updates keep overrides):** holds for LayOut viewports (S, with reports of styles reset "once in
  a while"). **Fails for LayOut tables** (P: an update overrides local changes). AutoCAD data links lock
  the cells instead, so local edits do not arise. Mixed: V175 must decide it explicitly.

## 4. Comparison across tools

| Tool | Linked kinds | Update trigger | Stale mark | Override | Reset | Source deleted | Token syntax |
|---|---|---|---|---|---|---|---|
| **Archicad** (AC24 to AC27) | Drawings of views (plans, sections, schedules), external files; autotext from project, layout, drawing, reference drawing, system; labels with element data | Drawings: Auto when the layout is activated, or Manual (frozen until Update). Autotext: always live. | Drawing Manager status column: OK, Modified, Missing, Not Accessible, Needs Checking, Embedded | Whole drawing frozen (Manual). Drawing Settings per placed drawing. No partial override found. | Update (for Manual or Modified drawings); Check Status | Status Missing; Embedded when the link is broken; autotext shows placeholder text until the data exists | `<PROJECTNAME>`, `<LAYOUTNUMBER>`, `<DRAWINGSCALE>`, `<SITEGROSSAREA>` (GDL); a picker dialog in text |
| **SketchUp LayOut** (2026) | Model viewports (scene, camera, style, tags), images and files, Excel/CSV tables, entity labels, document auto-text | References: on demand (Update), check on load (option), synced on save from LayOut. Render: Auto or Render. Document auto-text: live. | References list in red; label highlighted red (not printed, S); panel sections dark grey with Reset (S) | **Per group of viewport settings** (camera, style, effects, tags, a tag's dashes and visibility); overrides kept on update (S) and copied with the viewport | Reset per section; Reset All; per tag Reset Dashes / Visibility / All; push tag overrides to the model; C API reset (2026) | Label red, Reconnect to Model; reference "missing" in red; 2023 rebinds to the nearest component (counter-evidence) | `<PageNumber>`, `<SceneName>`, `<Ratio( to )>`, `<Coordinates(x,y)>`, `<WindowType>` (any attribute); Sequence tags |
| **Revit** (2021 to 2023) | Views, schedules, legends on sheets; title block labels bound to project or sheet parameters | Always, by the change engine | None (never stale) | None; editing a label on the sheet writes the parameter | Not applicable | Label shows "?" for an absent parameter (U) | None (labels picked in the family editor) |
| **AutoCAD** (2025) | Fields in any text (date, document properties, object properties, sheet set, formula); tables linked to Excel/CSV; table formulas | FIELDEVAL bits: open 1, save 2, plot 4, eTransmit 8, regen 16 (default 31); UPDATEFIELD; the date only manually; DATALINKUPDATE on demand | Grey field background, not plotted; data link indicators around cells; status bar icon and balloon at the stale table | None on fields; linked cells locked by default | Edit the field definition; Convert Field to Text, one way (Architecture help) | "----" no value; "####" invalid; sheet set fields keep the last value, or "####" (the pages disagree) | `%<\AcVar Date \f "M/d/yyyy">%` (stored form, built by the dialog) |
| **Vectorworks** (2024 to 2026) | Sheet layer viewports; title block text linked to records; data tags; worksheets | Wireframe viewports: automatic. Rendered viewports: on Update. Linked text: automatic. Worksheets: recalculate automatically, or on command. | Red Update button text; optional red and white striped border; prompt at print; red "X" when empty | Per text block: Not Link versus Link Value | Update; Recalculate | Empty viewport shows a red "X"; unlinked marker shows a broken-link icon; tags can come loose (U) | `#Record#.#Field#`, `#WS_...#` |
| **Rhino 8** | Text fields (page, file, date, object area and length, user text, detail scale) | Evaluated while Rhino runs (live) | None found | None | Not applicable | "####" | `%<PageNumber()>%`, `%<Area("id","Unit")>%`, `%<DocumentText("Key")>%` |

## 5. Counter-evidence

What was found when looking for complaints and failures:

1. **LayOut overrides are easy to make and hard to see** (S, high agreement). Many threads (146169,
   160597, 225138, 275627) are users whose viewports "won't update" because they overrode the camera
   without knowing. One user swore they "never" touched the camera; a failing mouse had been
   double-clicking into viewports. The experienced reply is to keep the panel visible "so you can see if
   things get modified". Lesson: an override mark seen only in a side panel is not enough. **The board
   element itself must carry the override mark.**
2. **LayOut 2023 silently rebinds labels** (S, thread 243365, 2023). After a reference update, labels whose
   geometry had changed were joined to the nearest component instead of being marked red, as LayOut 2020
   did. A poster who speaks for the design ("We now assume it is okay to connect to a different component
   by default, which in your case is wrong!") calls it "a side effect of LayOut's efforts to
   automatically reconnect labels". The forum record does not flag the poster as staff. Lesson: **never
   rebind a lost link to a guessed source. Mark it stale or missing and let the user choose.**
3. **LayOut table updates throw away local edits** (P). The vendor's own warning. Lesson: a refresh must
   not overwrite an override silently.
4. **LayOut overrides sometimes lost on relink** (S, thread 255744): "I have seen the styles get reset
   once in a while."
5. **Archicad Auto drawings needing a manual update, and autotext in custom titles showing every drawing
   on the layout** (U: Graphisoft community and help center refused). The search summaries report an AC17
   thread where Auto drawings "require a manual update", a help center article where the update must be
   "forced" by publishing or a manual update, and an AC21 bug where custom drawing titles listed all the
   drawings on a layout. Other threads (titles only) ask Graphisoft to stop defaulting to automatic
   updates, or to update Manual drawings at publish time, and complain of a constant "Modified" status.
   Lesson: on-activation updates can be slow or wrong. **Publishing should check and refresh before it
   writes.**
6. **AutoCAD fields stale at publish** (U: Autodesk forums refused). Summaries report a thread where
   FIELDEVAL dropped to 4 after PUBLISH, and others where layout-name fields refreshed only on plot until
   FIELDEVAL was set back to 31. An Autodesk support note (seen only through a summary) ties wrong field
   values in published layouts to the plot bit being off. Lesson: freshness tied to events fails when the
   events are configured off. Live, or checked at export, is safer.
7. **Vectorworks data tags come loose from their objects** under project sharing (U, forum refused;
   summary of a developer's reply calling it a known issue).
8. **Revit "?" in title blocks** puzzles users. It means the parameter is missing, or simply that no value
   has been entered (U).

None of these overturns the comparison. Items 1 to 3 change the design: a visible mark on the element,
no silent rebinding, and no silent overwrite of an override.

## 6. What is still open (U)

- Archicad's "Linked properties" of drawing titles: not found in the AC25 and AC27 pages read. The AC27
  Drawing Title pages were not read.
- Whether Archicad autotext can be overridden, other than by deleting it.
- The exact placeholder text Archicad shows for missing autotext.
- The AC27 copies of the Drawing Manager and Drawing Settings pages. The statuses and update types above
  are from AC24 and AC25.
- Whether deleting a source view in Archicad gives "Missing" or another status.
- The literal "(Modified)" next to a scene name in LayOut's SketchUp Model panel. The dark-grey section
  and its Reset button are S (forums).
- What LayOut label auto-text shows when its entity is gone: only the red highlight is documented.
- Revit's "?" for a missing or empty parameter (forum host refused).
- Revit's "Filter by Sheet" for schedules (search summary only).
- AutoCAD field categories beyond Date & Time, Document and Objects; the full field-code grammar.
- Whether core AutoCAD (not Architecture) has "Convert Field to Text" on the field's menu.
- Vectorworks data tags whose object is deleted (forum refused).
- The Graphisoft, Autodesk and Vectorworks community threads (all 403). The owner could allow those hosts
  in the environment's network settings.

None of these blocks the design. Each concerns a detail of one tool, not the pattern.

## 7. References

All read 2026-11-08. "curl" means the page was fetched and read as text here; "WebFetch" means read
through the fetch tool's digest.

| # | Source | URL | What was read | Level |
|---|---|---|---|---|
| 1 | Graphisoft, Archicad 24 help, Drawing Manager | https://help.graphisoft.com/AC/24/INT/_AC24_Help/130_UserInterfaceDialogBoxes/130_UserInterfaceDialogBoxes-76.htm | Status list, Update, Check Status, Link Drawing (WebFetch) | P |
| 2 | Graphisoft, Archicad 25 help, Drawing Settings | https://help.graphisoft.com/AC/25/INT/_AC25_Help/150_UserInterfaceToolSettings/150_UserInterfaceToolSettings-28.htm | Update Type Auto and Manual; Store Drawing; Drawing Titles (WebFetch) | P |
| 3 | Graphisoft, Archicad 27 help, Autotext | https://help.graphisoft.com/AC/27/INT/_AC27_Help/070_Documentation/070_Documentation-66.htm | Whole page (curl) | P |
| 4 | Graphisoft, Archicad 27 help, How to Insert Autotext | https://help.graphisoft.com/AC/27/INT/_AC27_Help/070_Documentation/070_Documentation-67.htm | Whole page: insertion, placeholder, sources (curl) | P |
| 5 | Graphisoft, Archicad 27 help, Autotext Reference Drawing | https://help.graphisoft.com/AC/27/INT/_AC27_Help/070_Documentation/070_Documentation-68.htm | Whole page (curl) | P |
| 6 | Graphisoft, Archicad 27 help, Autotext Keywords | https://help.graphisoft.com/AC/27/INT/_AC27_Help/070_Documentation/070_Documentation-69.htm | Whole keyword table (curl) | P |
| 7 | Graphisoft, Archicad 22 help, Autotext Keywords | https://help.graphisoft.com/AC/22/INT/_AC22_Help/070_Documentation/070_Documentation-73.htm | Whole table, compared with AC27 (curl) | P |
| 8 | Graphisoft, Archicad 27 help, Text/Autotext Label Content | https://help.graphisoft.com/AC/27/INT/_AC27_Help/070_Documentation/070_Documentation-72.htm | Whole page (curl) | P |
| 9 | Trimble, LayOut help, Managing Changes and Updates to SketchUp Files | https://help.sketchup.com/en/layout/managing-model-references | Whole article (curl) | P |
| 10 | Trimble, LayOut help, Automating Title Block Text with Auto-Text Tags | https://help.sketchup.com/en/layout/automate-titleblocks | Whole article (curl) | P |
| 11 | Trimble, LayOut help, Labeling Items in Your Document | https://help.sketchup.com/en/layout/labeling-items-your-document | Whole article (curl) | P |
| 12 | Trimble, LayOut help, Adding Tables to a Document | https://help.sketchup.com/en/layout/adding-tables-document | Manage changes to imported table data (curl) | P |
| 13 | Trimble, LayOut help, Working with Dashes in SketchUp Files | https://help.sketchup.com/en/layout/styling-sketchup-linework | Overrides and Reset (WebFetch and curl) | P |
| 14 | Trimble, LayOut help, Rendering Models | https://help.sketchup.com/en/layout/rendering-models | Auto, Render, Rendered (curl) | P |
| 15 | Trimble, LayOut help, Selecting Scenes; Viewport Camera Tools | https://help.sketchup.com/en/layout/selecting-scenes ; https://help.sketchup.com/en/layout/viewport-camera-tools | Whole articles; nothing on Modified or Reset (curl) | P |
| 16 | Trimble, SketchUp Desktop 2026.0 release notes | https://help.sketchup.com/en/release-notes/sketchup-desktop-20260 | LayOut API override functions; reference fixes (WebFetch) | P |
| 17 | SketchUp Community forum, threads 160597 (2021 to 2022), 225138 (2023), 146169 (2020 to 2023), 255744 (2024), 275627 (2024), 243365 (2023), 262449 (2024) | https://forums.sketchup.com/t/160597.json (and the same form for each id) | All posts (curl, Discourse JSON) | S (practice, several posters) |
| 18 | Autodesk, Revit LT 2023 Get Started | https://help.autodesk.com/cloudhelp/2023/ENU/RevitLT-GetStarted/files/GUID-D8835F8E-1330-4DBC-8A55-AF5941056C58.htm | The change engine sentence (WebFetch) | P |
| 19 | Autodesk, Revit 2023 help, Add Views to a Sheet | https://help.autodesk.com/cloudhelp/2023/ENU/Revit-DocumentPresent/files/GUID-D3E7FDC3-57AB-4497-AB87-D195476254C2.htm | One sheet per view; schedules and legends (WebFetch) | P |
| 20 | Autodesk, Revit 2022 help, Add Custom Fields to a Title Block | https://help.autodesk.com/cloudhelp/2022/ENU/Revit-DocumentPresent/files/GUID-5641C187-D1CC-494F-B20D-E01C46489DE8.htm | Whole page (curl) | P |
| 21 | Autodesk, Revit 2021 help, Enter Project-Specific Information for Title Blocks | https://help.autodesk.com/cloudhelp/2021/ENU/Revit-DocumentPresent/files/GUID-183531FC-83D3-4C75-B912-3877142DA319.htm | Whole page (WebFetch) | P |
| 22 | Autodesk, Revit 2016 help, Apply the Label to a Title Block | https://help.autodesk.com/cloudhelp/2016/ENU/Revit-Customize/files/GUID-70588AF5-A2A1-4FA3-8171-7C4734BCBD41.htm | Whole page (WebFetch) | P |
| 23 | Autodesk, AutoCAD 2025 help, FIELDEVAL | https://help.autodesk.com/cloudhelp/2025/ENU/AutoCAD-Core/files/GUID-EF5D2DDE-A170-4BB4-8F76-7F3FAFE30E56.htm | Whole page; the 2024 and 2026 copies fetched too (curl) | P |
| 24 | Autodesk, AutoCAD 2025 help, About Using Fields in Text | https://help.autodesk.com/cloudhelp/2025/ENU/AutoCAD-Core/files/GUID-B9ADAE6A-2DD1-4C44-B126-CF3FF92EBC68.htm | Whole page (curl) | P |
| 25 | Autodesk, AutoCAD 2025 help, FIELDDISPLAY | https://help.autodesk.com/cloudhelp/2025/ENU/AutoCAD-Core/files/GUID-99DB691B-9E11-4BD5-AFFE-BC1312F3281A.htm | Whole page (curl) | P |
| 26 | Autodesk, AutoCAD 2025 help, Field Dialog Box; FIELD; To Insert a Field in Text | https://help.autodesk.com/cloudhelp/2025/ENU/AutoCAD-Core/files/GUID-1B6DD22B-10D1-44ED-BAA2-E6D79FE52327.htm ; .../GUID-742C92C3-1284-4722-B650-C46F9191C701.htm ; .../GUID-7F254BA7-5C83-451B-A586-A78EE5D22C64.htm | Whole pages (curl) | P |
| 27 | Autodesk, AutoCAD 2025 help, UPDATEFIELD; To Work With Updating Text Fields | https://help.autodesk.com/cloudhelp/2025/ENU/AutoCAD-Core/files/GUID-2B47D62E-19D0-4CA5-9AAC-1946132D2F62.htm ; .../GUID-41B09208-E652-460A-B6EA-9B9A5FAAEB68.htm | Whole pages (curl) | P |
| 28 | Autodesk, AutoCAD 2025 help, About Linking a Table to External Data; DATALINKUPDATE; DATALINKNOTIFY | https://help.autodesk.com/cloudhelp/2025/ENU/AutoCAD-Core/files/GUID-3A038CCF-A659-4E8A-AE6E-1D88D00D3A23.htm ; .../GUID-1F8FE1F0-5229-4A5C-B69F-DA47CC9C25A9.htm ; .../GUID-DF138807-A321-4609-91A6-72DDDD10EF43.htm | Whole pages (curl) | P |
| 29 | Autodesk, AutoCAD LT 2026 for Mac help, About Using Formulas in Table Cells | https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-LT-MAC/files/GUID-7525DF79-61DA-4FCF-9383-7CA4D4DDF298.htm | Whole page (curl) | P |
| 30 | Autodesk, AutoCAD Architecture 2016 help, To Convert Fields to Text | https://help.autodesk.com/cloudhelp/2016/ENU/AutoCAD-Architecture/files/GUID-76C68393-2FC7-4203-862B-14C849E6BD4D.htm | Whole page (curl) | P (that product) |
| 31 | Autodesk, AutoCAD 2016 ActiveX reference, FieldCode Method | https://help.autodesk.com/cloudhelp/2016/ENU/AutoCAD-ActiveX/files/GUID-FE0C5004-B723-4AE8-888A-7DF11C765C89.htm | The VBA and LISP examples with the field code string (curl) | P |
| 32 | Vectorworks 2024 help, Updating viewports; Viewport status | https://app-help.vectorworks.net/2024/eng/VW2024_Guide/Viewports2/Updating_viewports.htm ; https://app-help.vectorworks.net/2024/eng/VW2024_Guide/Viewports2/Viewport_status.htm | Whole pages (curl). The 2016 Viewport Status page was read too and agrees. | P |
| 33 | Vectorworks 2025 help, Linking title block text to data records | https://app-help.vectorworks.net/2025/eng/VW2025_Guide/Setup/Linking_title_block_text_to_data_records.htm | Whole page (curl) | P |
| 34 | Vectorworks 2025 help, Data tag settings | https://app-help.vectorworks.net/2025/eng/VW2025_Guide/Annotation2/Data_tag_settings.htm | Tag field definition, syntax (curl) | P |
| 35 | Vectorworks 2026 help, Worksheet window | https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Worksheets/Worksheet_window.htm | Recalculate options (curl) | P |
| 36 | McNeel, Rhino 8 help, Text fields | https://docs.mcneel.com/rhino/8/help/en-us/information/text_fields.htm | Syntax, error string, function list (curl) | P |
| 37 | Search summaries of the Graphisoft community and help center, Autodesk forums and Vectorworks forum (all refused here) | community.graphisoft.com, helpcenter.graphisoft.com, forums.autodesk.com, forum.vectorworks.net | Search summaries only | U |
