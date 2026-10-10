# One Analyze, and the boards as pages of the set (V162)

The owner, after V161: "you are splitting the analysis and site analysis on 2 different layers. they
should be just one ... for the report/ dashboard, it should be on the presentation layer not its own
thing. im trying to make everything consistent not sprawling everywhere". Asked how, they chose:

- **Analyze, by the ten categories.** One list: the stages and Define at the top, then the ten
  categories, each holding its analyses, its data and its findings, and Model at the end. One search.
- **Boards, as pages in the set.** Each board is a page in the Presentation list beside the sheets,
  with its thumbnail. It opens in the main view with the panel still showing. Present shows it and
  Print set prints it. There is a + Board button. Analyze only gets the data and links to the board.

This note is how other tools do the two things, and what V162 takes from them.

## 1. One place for the analysis tools, grouped by what they answer

- **ArcGIS Pro** has one place for its analysis tools, the Geoprocessing pane. It has one search over
  every tool, by name or by what it does (Esri's example is "proximity"), with Favorites and the
  toolboxes beside the search. The Analysis tab's Tools gallery shows a few common tools grouped in
  categories, and opens out to show the rest. The lesson: one entry point and one search, with
  grouping as a way of browsing, not a second place to look.
- **The site analysis standard** (V158, `research-site-analysis-process.md`) already sorts the work into ten
  categories: location, legal, landform, water, climate, ecology, environmental risk, access, utilities,
  people. It also sorts it into seven stages, from Define to Report. A finding goes in a category, so
  the tool that produces the finding belongs in the same category. Slope and aspect are Landform,
  rain flow is Water, sun hours are Climate. The person reads one category and has the question, the
  tools, the data, the findings and the checklist together.
- **What reads the model itself is not site analysis.** Colour by, areas by usage, the LOD check,
  statistics and the frame analysis answer questions about the design, not the site. They are
  grouped at the end as Model, the way the Geoprocessing pane keeps general-purpose toolboxes apart
  from domain ones.

**V162:**
- One list in this order: the stages, red flags, Define, the ten categories, then Model.
- Each category holds its data block (Location the site context, Legal zoning, Climate the climate
  and risk data, Access the access and people data), then its analyses, then its findings and
  checklists.
- Risk and People share data fetched by Climate and Access. They say so and link to it rather than
  repeat it.
- One search over everything:
  - A category matched by its own words (its name, its question, its data, its findings, its
    checklist) shows whole, opened.
  - Otherwise only the analyses in it that match are shown, so "cut fill" shows Grading alone, inside
    Landform.
  - Text is read node by node, so a label and its value are not run together into one word.

## 2. A report is a page of the deliverable, not a window of its own

- **ArcGIS Pro** keeps reports and layouts as project items, each in its own category in the Catalog
  pane. Both are exported to PDF, and several layouts can be exported at once with Export Layouts. A
  report is part of what the project hands over, not a separate window.
- **Tableau's stories** are a sequence of story points. Each point is a worksheet or a whole
  dashboard. A dashboard is a page in the presentation like any chart, presented and shared in the
  story's order.
- **Revit** puts schedules on sheets to print them, and prints the set of sheets as one job. V122
  followed it: the set is the sheets, Present shows them, and Print set prints them in one go.
- **Before V162, a board was a dialog over the whole app.** It was opened from Analyze, printed with
  the browser's own print, and absent from the set. That made it a second, separate deliverable.

**V162 makes a board a page of the set:**
- **Where it shows:**
  - It is in the Presentation panel, numbered in the set's order, with a thumbnail of the board as it
    prints. It can be dragged, stepped up or down, and taken out of the set.
  - It opens in the main view with the rail, the panel and Properties beside it.
  - It lays out by the width of the main view, not of the window.
- **How it presents and prints:**
  - Present shows it as on screen. The wheel scrolls the board to its end, then moves to the next
    page.
  - Print set prints it on A3 landscape pages of its own, between the sheets in the set's order. Its
    own Print opens it alone in a print window.
- **How it is reached:** Analyze fetches the data and says *Show in Presentation*, which puts the
  board in the set if it is not there yet, opens it and shows its page. The ACCESS, CLIMATE and
  ZONINGBOARD commands do the same.
- **How it is kept:** with the project, in the file, in History and in an undo step. There is one
  board of each kind; a board's data stays in Analyze when the board leaves the set.

## 3. Decisions, and what was not done

- **The order of the set.** The sheets keep their own order among themselves, which is the layout
  tabs. A board keeps its place among them:
  - The set's order is a list of ids. Each place it gives a sheet is filled by the sheets in their own
    order, and a sheet that is new to the list comes last.
  - Dragging a sheet past a board reorders the sheets, so the tabs follow.
  - With no board in the set, every move is the sheet move it always was.
- **Boards are not sheets.** A sheet is a vector drawing the sheet renderer draws and the PDF writer
  writes; a board is an HTML document. A board in `A3D.sheets` would put a non-sheet in front of every
  sheet consumer (the tabs, the browser, the title block, numbering, the renderer). They stay apart;
  the set's order is what joins them.
- **The thumbnail is a frame, not a copy of the board in the page.** A second copy of the board in
  the page would duplicate its classes and confuse what finds the board. A frame is its own document,
  holding the board in its print look, scaled to the column. It is written again when the model moves
  and the board's markup with it.
- **Keys.** While a board's page is on screen it owns the keys, as a sheet's page does:
  - Esc gives the main view back.
  - The model's keys do not reach the model behind it, so Delete does not delete an unseen selection,
    and the arrows and Space scroll the board.
  - Ctrl, Alt and the function keys pass, and so does a field being typed in, in a panel beside the
    board.
- **A refresh waits for a field being typed in.** With the site analysis in Analyze's one list, the
  list is redrawn more often, for every analysis that changes. A redraw while a finding's field is
  being typed in would lose the words, so it waits until the field is left.
- **Not done:**
  - A board for every category. Three boards exist; the categories link to them.
  - A board's figures as separate pages. A board is one page that runs over as many sheets of paper
    as it needs, the way a long report does.
  - Thumbnails of the boards in the dark theme. The thumbnail is the print look, white paper like
    the sheets'.

## Sources

- Esri, ArcGIS Pro: [Find a geoprocessing tool](https://pro.arcgis.com/en/pro-app/help/analysis/geoprocessing/basics/find-geoprocessing-tools.htm) (the Geoprocessing pane, its search, the Analysis Tools gallery).
- Esri, ArcGIS Pro: [Export Layouts](https://doc.esri.com/en/arcgis-pro/latest/tool-reference/data-management/export-layouts.html) (several layouts in one export).
- Esri, ArcGIS Pro: [Reports in ArcGIS Pro](https://pro.arcgis.com/en/pro-app/2.6/help/reports/reports-in-arcgis-pro.htm) (reports as project items in the Catalog pane, exported to PDF).
- Tableau, Stories: help.tableau.com, "Stories" in Tableau Desktop's help. It could not be reached from here when this note was written; the description above is the common one of the guides that quote it.
- This repository: `reference/research-site-analysis-process.md` (V158, the ten categories and the stages) and V122's Presentation (the set, Present, Print set).
