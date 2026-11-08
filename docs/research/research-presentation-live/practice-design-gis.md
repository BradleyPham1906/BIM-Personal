# V175 working note 2: practice in GIS layouts, design tools and office tools

Research agent 2, 2026-11-08. Under `docs/research/research-protocol.md`. Levels: **P** read in the vendor's own page
or the code read as text; **S** a dependable secondary source, gap said; **U** a search engine's summary or a forum
post only, never for code. Licences: QGIS is GPL-2.0-or-later (method only, nothing copied); Penpot is MPL-2.0 (method
only here, nothing copied either). Quotes are short and exact; everything else is in our own words.

## 1. The question

How do the tools a designer or GIS user already knows keep an object on a page linked to its source, bring it up to
date, show that it is stale or that its source is gone, and keep an edit made on the page (an override) apart from
what the source supplies, with a way back (Reset)? What must V175 decide from this: what is bound, when it refreshes,
how staleness is marked, the grain of an override (whole object, property, attribute group), Reset (one, all), the
missing-source state, the token syntax in text, and number formatting.

Hypotheses this note can test (numbering of the main note, `research-presentation-live.md`):

- **H4.** Every surveyed tool marks a stale linked item visibly on the page or in a list.
- **H5.** Figma and Penpot keep overrides per property (Penpot: per attribute group); their Reset is per property and
  for all.
- **H9.** A field syntax exists that is easy to type on a phone, needs no escaping in prose, and is never run as code.
- Proposed by note 2, **H-n2-1.** In every surveyed tool an override survives a source update, and only the overridden part
  stops following the source.
- Proposed by note 2, **H-n2-2.** Every surveyed tool offers a one-way "freeze" (convert to static) distinct from a reversible
  override.

## 2. Search log

| # | Where | Query or URL | What came back | Kept / set aside, why |
|---|---|---|---|---|
| 1 | pro.arcgis.com | `/latest/help/layouts/dynamic-text.htm` | 301 to doc.esri.com, which then 404 | Set aside; the "latest" path moved |
| 2 | Web search | ArcGIS Pro dynamic text tags "dyn type" mapFrame scale decimalPlaces | Version pages 2.6 to 3.4 of "add and modify dynamic text" | Kept the 3.4 page as P |
| 3 | pro.arcgis.com | `/3.4/help/layouts/add-and-modify-dynamic-text.htm` | Full tag list and attributes | Kept, P |
| 4 | pro.arcgis.com | `/3.4/help/layouts/dynamic-text.htm`, `/3.4/help/layouts/table-frames.htm` | 404 both | Set aside |
| 4b | pro.arcgis.com | `/3.4/help/layouts/use-dynamic-text-with-map-series.htm` (latest gave 301) | Page tags | Kept, P |
| 5 | Web search (pro.arcgis.com, doc.esri.com) | table frame chart frame layout updates | add-and-modify-table-frames, charts, work-with-layout-elements | Kept the pages, read each |
| 6 | pro.arcgis.com | `/3.4/help/layouts/add-and-modify-table-frames.htm`, `/charts.htm`, `/work-with-layout-elements.htm` | Dynamic table frames, chart frames, dynamic vs static elements | Kept, P |
| 7 | pro.arcgis.com | `/3.4/help/layouts/work-with-a-legend.htm` | "Synchronize with map", Convert to graphics | Kept, P |
| 8 | pro.arcgis.com | `/3.4/help/layouts/work-with-legend-items.htm` | Legend item order, patches | Kept, P (little on overrides) |
| 9 | docs.qgis.org | legend, label pages (old `print_composer` paths redirect) | layout_legend, layout_label | Kept, P |
| 10 | docs.qgis.org | layout attribute table page, two guessed paths | 404 | Found via search: tables are in `layout_tables.html` |
| 11 | docs.qgis.org | `/3.44/.../layout_items/layout_tables.html` (curl, after a 302 from latest) | Refresh Table Data, Empty table, filters | Kept, P |
| 12 | docs.qgis.org | `/3.44/.../expressions/functions_list.html` | format_number, item_variables, layout variables | Kept, P |
| 13 | github.com/qgis/QGIS (raw) | `src/core/layout/qgslayoutitemlegend.cpp` | setAutoUpdateModel, setSyncMode, resetManualLayers | Kept, P, method only (GPL) |
| 14 | github.com/qgis/QGIS (raw) | `src/core/layout/qgslayoutitemlabel.cpp` | currentText, refresh, convertToStaticText | Kept, P, method only |
| 15 | github.com/qgis/QGIS (raw) | `src/core/expression/qgsexpression.cpp` | replaceExpressionText: errors and nulls | Kept, P, method only |
| 16 | help.figma.com | Apply overrides to instances (360039150733) | Overridable list, Reset menu | Kept, P |
| 17 | help.figma.com | Create and insert component instances; Review and accept library updates; Edit main components | Propagation, no override rule | Kept as P for propagation |
| 18 | Web search | figma instance override main component changes | Forum threads only | Set aside as U; used as counter-evidence |
| 19 | Web search (help.figma.com, figma.com) | override main component propagate | Figma blog 2018 "Component overrides" | Kept, P (vendor's own, old) |
| 20 | figma.com/blog | figma-feature-highlight-component-overrides | Green/red rule | Kept, P, dated 2018 |
| 21 | developers.figma.com | plugins/api/InstanceNode (after 301) | overrides, resetOverrides, removeOverrides, detachInstance | Kept, P |
| 22 | help.figma.com | Apply variables to designs; Overview of variables | Bindable properties, detach | Kept, P |
| 23 | Web search | Figma deleted variable bound layers | Forum threads, "Detach deleted variables" | U, counter-evidence |
| 24 | github.com/penpot/penpot (raw) | `common/src/app/common/types/component.cljc` | sync-attrs, touched helpers, licence | Kept, P |
| 25 | github.com/penpot/penpot (raw) | `common/src/app/common/logic/libraries.cljc` | three sync kinds, update-attrs | Kept, P |
| 26 | github.com/penpot/penpot (raw) | `common/src/app/common/types/container.cljc` | set-shape-attr: when a group is touched | Kept, P |
| 27 | help.penpot.app | user-guide/components | Reset overrides, Update main, Detach | Kept, P |
| 28 | helpx.adobe.com | indesign/using/graphics-links.html; text-variables.html; link-and-update-content (au) | **403 Forbidden**, all three | Refused host, recorded; not worked around |
| 29 | Web search | InDesign Links panel modified missing Update Link Relink | helpx summaries, community threads | U |
| 30 | Web search | InDesign text variables Convert Variable to Text ... | helpx summaries, Peachpit | U |
| 31 | Web search | InDesign "Preserve local edits while updating object links" | manuals, scripting reference, community bugs | Pointer to the next row |
| 32 | developer.adobe.com | indesign/uxp/dom/api/l/linked-page-item-option | preserve* flags, warnOnUpdateOfEditedPageItem | Kept, P (Adobe's own scripting reference) |
| 33 | support.microsoft.com | update-a-linked-or-embedded-object... (guessed id) | 404 | Set aside |
| 34 | Web search | Word lock field Ctrl+F11 unlink Ctrl+Shift+F9 F9 | Microsoft page, tips sites | Kept the Microsoft page |
| 35 | support.microsoft.com | word/insert-edit-and-view-fields-in-word | update on open, F9, lock/unlock | Kept, P |
| 36 | support.microsoft.com | word/field-codes-docproperty-field | syntax, \* Upper | Kept, P |
| 37 | Web search | "Error! Unknown document property name" | third-party pages | U |
| 38 | Web search, then support.microsoft.com | powerpoint/link-or-embed-a-powerpoint-slide-in-a-word-document | linked vs embedded, manual update, Break Link | Kept, P |
| 39 | Web search | PowerPoint linked Excel chart Update Links Edit Links to Files | tutorials, Microsoft Q&A threads | U, counter-evidence |
| 40 | canva.com | help/import-to-charts/ | **403 Forbidden** | Refused host, recorded; search summary only (U) |
| 41 | Notion / Google smart chips | not searched | | Set aside for time; optional in the brief |

Refused hosts: helpx.adobe.com (403, three pages), canva.com/help (403). A browser user agent through curl was not
tried: the session's safety check refused it as bot-check circumvention, which is right; the refusals stand.

## 3. Findings by tool

### 3.1 ArcGIS Pro (3.4 help)

Source: pro.arcgis.com/en/pro-app/3.4/help/layouts/add-and-modify-dynamic-text.htm (P).

- **Syntax.** Tags in XML form inside a text element: `<dyn type="mapFrame" name="MapFrameName" property="scale"/>`.
  Types read on the page: system (`computer`, `date`, `time`, `user`), `project` (`name`, `path`, `dateSaved`, unit
  settings, `metadata` with `attribute="title"` and others), `layout` (`name`, `dateExported`, `datePrinted`,
  `serviceLayerCredits`, metadata), `mapFrame` (`scale`, `rotation`, `mapUnits`, `mapName`, `referenceScale`,
  `credits`, camera parts, `sr` with `srProperty="name"`/`wkid`/`datum`..., extent points such as `center`,
  `lowerLeft`, time). Map series page tags (pro.arcgis.com/en/pro-app/3.4/help/layouts/use-dynamic-text-with-map-series.htm,
  P): `<dyn type="page" property="name"/>`, `property="number"`, `"index"` with `"count"` (Page 3 of 12), and
  `<dyn type="page" property="attribute" field="<Field Name>" domainlookup="true"/>` (coded-value description by
  default; `domainlookup="false"` shows the raw code). The table attribute tag is on another page, not read (section 7).
  Confidence high.
- **Number formatting.** Attributes on the tag: "You can modify the number of decimal places used by tags that return
  numeric values using the decimalPlaces attribute"; `units` (`dd`, `dms`, `ddm`), `padDecimal`, `showPlusSign`,
  `preStr`/`postStr` ("Pre and post string attributes can be used to add text before or after a tag"), dates by
  `format="short|long"`. No thousands-separator attribute on that page. Confidence high.
- **Source missing.** `emptyStr` sets the text when a tag "parses to null"; with nothing set, the text is blank and a
  selected element shows an empty box. A renamed map frame: "the tag remembers the map frame it references, but the
  tag does not update to reflect the map frame's new name" (so the binding is by identity, the tag's text keeps the old
  name). Deletion of the frame is not documented. Confidence high for rename and null, low for delete.
- **Refresh.** Live with the document; export tags are "blank until the layout is exported". No stale marker: dynamic
  text is always current. Confidence medium (implied, not stated as a rule).
- **Table and chart frames are live.** Table frames "can be dynamic—updating whenever the map frame extent is
  changed"; on field changes "the table frame updates automatically on the layout"; "Display only when populated" hides
  an empty one; they "can only point to data that exists in a map frame on the layout". Chart frames: "Changes to chart
  elements automatically update on the layout", with "Only show chart data that is visible in the map frame".
  Work-with-layout-elements: "Dynamic elements update in response to changes in the data or the map extent." Confidence
  high.
- **Legend: sync options and a one-way freeze.** Under "Synchronize with map": new layer ("A new item is added to the
  legend when a new layer is added to the map") and layer visibility; a removed layer's item is removed, "This is done
  automatically." Convert to graphics: "once a legend is converted to graphics, it loses all connection to the map";
  "Any changes to layer symbology, or added and removed layers, will not be reflected in the legend." No Reset back.
  Confidence high.
- **Override model.** Element properties (font, frame, legend item text visibility) are set on the element and are not
  "overrides" of a source; the only edit that overrides data is to convert to graphics, whole element, one way. Legend
  patches always come from the layer's symbology. Confidence medium.

### 3.2 QGIS print layouts (3.44 manual, master source)

- **Label syntax.** "Dynamic parts of a label need to be surrounded by `[%` and `%]`"; the dialog adds them. Any
  expression: `[% @project_title %]`, `[% map_get( item_variables('Map 0'), 'map_scale') %]`, `[% @layout_page %]` of
  `[% @layout_numpages %]` (variables listed in functions_list: "layout_page The page number of the current item in the
  layout", "project_title The title of current project"). Labels can render as HTML. Confidence high (P).
- **Number formatting.** By function, not by attribute: `format_number(number, [places:=0], [language],
  [omit_group_separators:=false], [trim_trailing_zeroes:=false])`, locale aware; dates by `format_date(d, 'yyyy-MM-dd')`.
  Confidence high (P).
- **How the label refreshes (code, method only).** The label stores only the template text. Its `draw()` calls
  `currentText()`, which replaces `$CURRENT_DATE`, builds the expression context, and calls
  `QgsExpression::replaceExpressionText`; nothing evaluated is stored. Layout items draw through a render cache, and
  `refresh()` invalidates that cache and rebuilds the expression context, so the label is evaluated whenever the item
  is redrawn and `refresh()` forces that. Whether every source change triggers a redraw was not traced. Confidence
  medium (P, `qgslayoutitemlabel.cpp`).
- **Source missing or bad (code).** In `replaceExpressionText`, a parse error or an evaluation error leaves the raw
  `[% ... %]` text in place, visible on the page; a null result becomes an empty string. So a broken field shows its own
  source text, a missing value shows nothing. Confidence high (P, `qgsexpression.cpp`).
- **Freeze.** "Convert to Static" replaces the dynamic parts with their current values; in code,
  `convertToStaticText()` sets the template to the evaluated text: one way, not an override. Confidence high.
- **Attribute table.** Sources: a layer, the current atlas feature, relation children; filters "Show only visible
  features within a map", "Filter with". "The button Refresh Table Data can be used to refresh the table when the
  actual contents of the table has changed": a manual command exists, so the table is not guaranteed live for every
  data change. Empty result: "Draw headers only", "Hide entire table", or "Show set message" with a message "like 'No
  result'". Confidence high (P).
- **Legend Auto update = a frozen, editable copy.** Manual: "When Auto update is unchecked this will give you more
  control over the legend items": reorder, add or remove groups/layers/classes, rename, restore removed items, change
  labels and columns. "Update All" adapts the legend after symbology changes. In code (method only),
  there are three sync modes, AllProjectLayers, VisibleLayers (the default setting) and Manual; the Auto update
  checkbox maps to AllProjectLayers on, Manual off. `setAutoUpdateModel(false)` sets Manual; `resetManualLayers` then **clones the project's layer tree** into a
  custom tree that the legend owns. Turning auto back on drops the custom tree (`setCustomLayerTree(nullptr)`), which
  discards the edits. So QGIS's override is whole-element: copy the source once, edit the copy, and turning sync back on
  is the Reset of everything. There is no per-item Reset. Confidence high (P, code and manual).
- **Data-defined overrides.** Many item properties have a "Data defined override button to override the selected
  setting": the reverse direction (a property bound to an expression instead of a typed value). Per property.
  Confidence high (P).

### 3.3 Figma

- **What can be overridden on an instance** (help.figma.com 360039150733, P): "Figma lets you change text, fill,
  stroke, and effect properties"; text properties "including font, weight, size, line height, letter spacing, and
  resizing"; fill or stroke "including the fill type, value, and opacity"; effects; layout guides; nested instance
  swaps; export settings; layer name. Not overridable: layer order, position (including in auto layout),
  constraints, text layer bounds; for those, detach. Confidence high.
- **An override stops following the main; others still do.** Figma's own blog (2018, P but old): "the instance still
  updates accordingly, except for whatever property you manually changed"; "the instance will stay green even if you
  edit the master component to be red"; a stroke weight change still reaches it. The current help says only "When you
  make changes to the main component, Figma will apply any changes you apply to any linked instances." Confidence
  medium (rule is from a 2018 post; current help does not state it, but no source contradicts it).
- **Reset.** "Select Reset > Reset [property] to reset a specific property"; "Select Reset > Reset all changes to reset
  all properties for that layer"; "Figma only lists properties that have changes applied." Plugin API: `overrides`
  "Returns an array of all of the fields directly overridden on this instance", `resetOverrides()` deprecated for
  `removeOverrides`. So Figma stores overrides as a set of field names per layer of the instance. Confidence high.
- **How overrides are marked.** No on-canvas mark is documented; the Reset menu listing is the only documented marker.
  Confidence medium (absence in the help page).
- **Detach.** `detachInstance()` "Detaches the given instance from its component", returning a plain frame: the one-way
  freeze. Confidence high.
- **Variables bound to properties** (help.figma.com 15343107263511, P): string variables bind "text content, font
  family, and font weight and style"; number variables bind sizes, padding, radius, opacity and more; boolean binds
  visibility; color binds fills and strokes. Detach: the "Detach variable" icon, or for numbers by deleting in the
  field; dragging padding on canvas also detaches. Binding is per property; typing a new value detaches it, i.e. an
  edit replaces the binding rather than sitting beside it. Text content is bound whole: Figma has no inline token
  inside a sentence. Confidence high.
- **Deleted source.** Not in the help. Forum (U): a "Variable was deleted" note on affected layers and a "Detach deleted
  variables" quick command; layers keep showing a value. Confidence low.

### 3.4 Penpot (MPL-2.0; code read as text, develop branch, 2026-11-08)

- **The touched set** (`common/types/component.cljc`, P). A map `sync-attrs` assigns each shape attribute to a sync
  group: `:name` to `:name-group`, `:fills` to `:fill-group`, `:content` to `:geometry-group` for paths and
  `:content-group` for text, `:hidden` to `:visibility-group`, `:opacity` to `:layer-effects-group`, `:shadow` to
  `:shadow-group`, and so on: about twenty groups (`:stroke-group`, `:radius-group`, `:text-font-group`,
  `:text-display-group`, `:blur-group`, `:mask-group`, `:constraints-group`, `:exports-group`, layout groups...). The
  comment: when one attribute of a shape in a copy is modified, "the corresponding group is marked as :touched. Then, if
  the shape is synced with the remote shape in the main component, none of the attributes of the same group is
  changed." The shape carries `:touched`, a set of group keywords; helpers add a group and test one. Swapped nested
  copies are recorded in the same set as a `swap-slot-<uuid>` entry. Confidence high.
- **When a group becomes touched** (`common/types/container.cljc`, `set-shape-attr`, P). Only inside a component copy;
  only when the new value differs from the old (geometry compared within 1 px, to ignore rounding); a geometry edit
  does touch `:geometry-group` unless the caller passes `ignore-geometry` (width and height are kept out of that
  exemption), and `libraries.cljc` then keeps a copy's geometry when that group is touched (`geometry-kept?`); derived
  attributes (`position-data`) never touch; and a change made by the sync itself passes `ignore-touched` so it marks
  nothing. Confidence high.
- **Three kinds of sync** (`common/logic/libraries.cljc`, P). "NORMAL SYNC": attributes changed in the component
  "whose attr group has not been touched" are copied. "FORCED SYNC": the "reset" command copies all and "the touched
  flags are cleared". "INVERSE SYNC": "update component" pushes the copy's changes into the main and clears touched.
  `update-attrs` loops over every syncable attribute and skips one whose group is touched when `omit-touched?`. A text
  special case: letters and styling share `:content`, so when only one of them is touched the other still updates.
  Confidence high.
- **UI** (help.penpot.app user-guide/components, P): "Overrides are modifications made in a specific copy that are not
  in its main component"; "Reset overrides" returns a copy to the main; "Update main component" pushes; "Detach
  instance" (Ctrl+Shift+K) unlinks into a group. Reset is whole-shape (all groups), not per group, in the UI read.
  Confidence high for the UI named; medium that no per-group reset exists (not found).

### 3.5 Adobe InDesign (helpx refused; scripting reference read)

- **Refused.** helpx.adobe.com returned 403 for the Links, Text variables and Linked content pages. What follows from
  helpx is U (search summaries only).
- **Links panel (U).** A modified link (yellow triangle) is updated with Update Link; a missing link (red stop sign) is
  restored with Relink; "Search for Missing Links in This Folder"; Update All Links in the panel menu. Status is shown
  per link in a list, and a placed graphic keeps its last preview while missing. Confidence medium (many independent
  summaries and old manuals agree; primary page unread).
- **Linked content, override by attribute group (P).** Adobe's scripting reference for `LinkedPageItemOption`:
  `preserveAppearance` ("appearance edits will be preserved during update"), `preserveSizeAndShape`,
  `preserveInteractivity`, `preserveFrameContent`, `preserveOthers` ("text wrap, hyperLinks, text frame options, object
  export settings"), `warnOnUpdateOfEditedPageItem` ("a warning will be shown if the update link operation will
  override local edits"), `updateLinkWhileSaving`. This is the same idea as Penpot's touched groups, set per link: five
  attribute groups, each kept or overwritten when the source updates, and a warning before local edits are lost.
  Story status shows "Text Modified" when edited locally (U). Confidence high for the flags (P), medium for UI words.
- **Text variables (U).** Types: Chapter Number, Creation Date, Modification Date, Output Date, File Name, Last Page
  Number, Running Header (paragraph or character style, first or last on the page), Custom Text, Metadata Caption.
  They update as the document reflows. "Convert Variable To Text" freezes one instance; Define > Convert To Text all;
  deleting a definition asks whether to replace instances by another variable, by text, or delete them. Confidence
  medium (several summaries agree; primary refused).

### 3.6 Microsoft Word and PowerPoint

- **Word fields** (support.microsoft.com, insert-edit-and-view-fields-in-word, P): "By default, Word automatically
  updates fields when a document is opened"; otherwise "clicking in a field and then pressing F9"; Ctrl+A then F9 for the
  body (headers and footers separately). Lock: "To lock a field so that field results are not updated, click the field,
  and then press Ctrl+F11"; unlock Ctrl+Shift+F11. Switches "govern the format of the field results". A field stores
  both its code and its last result: the result is shown, and is stale until updated. Confidence high.
- **DOCPROPERTY** (P): `{ DOCPROPERTY "Name" }`, switch `\* Upper`. Alt+F9 toggles codes and results. A missing
  property shows "Error! Unknown document property name." (U, third-party). Numeric picture `\# "#,##0.00"` is the
  usual number format (U here, not read on a Microsoft page this session).
- **Unlink** Ctrl+Shift+F9 turns a field into plain text for good (U: tips sites agree; Microsoft page not read for it).
  So Word has three states: live (updates on open / F9), locked (reversible freeze, keeps the last result), unlinked
  (one-way). Confidence medium.
- **Linked objects** (support.microsoft.com, link-or-embed-a-powerpoint-slide-in-a-word-document, P): "By default,
  linked objects are updated automatically"; per link, "Update method for selected link" can be manual; Word option
  "Update automatic links at open"; "Break Link" makes a static picture: "you can no longer edit the object". On
  opening a presentation with links, a security bar offers "Update Links" (U, tutorials). Change Source for a moved
  file (U). The linked object keeps its last picture when the source is gone (U). Confidence high for P parts.

### 3.7 Canva

- canva.com/help refused (403). Search summary (U): a chart connected to a Canva Sheet in the same design syncs live
  with no refresh button; a chart from an external source (Google Sheets) is refreshed by hand; import limit 1000 rows
  by 100 columns. Third-party guides disagree on the name of the button and on scheduled sync. Confidence low.

### 3.8 Notion, Google Docs smart chips

Not researched (optional, time). Left open.

## 4. Comparison table

| Tool | Bound kinds | Refresh trigger | Stale mark | Override granularity | Reset | Source gone | Syntax | Number format |
|---|---|---|---|---|---|---|---|---|
| ArcGIS Pro | Text tags (project, layout, map frame, map series page, system); table frames; chart frames; legend; scale bar | Live with the document; table/chart on extent or data; export tags at export | None (always live) | Element properties only; data edit only by Convert to graphics (whole, one way) | None for converted; legend sync options toggle | Rename keeps binding by identity; null shows `emptyStr` or blank; layer removed: legend item removed | `<dyn type="..." name="..." property="..." .../>` | Tag attributes: `decimalPlaces`, `units`, `padDecimal`, `preStr`/`postStr`, date `format` |
| QGIS | Label expressions; attribute table; legend; map item variables; data-defined properties | Label when redrawn (`refresh()` forces it); table needs Refresh Table Data for content changes; legend on symbology when Auto update | None | Legend: whole element (manual copy of the layer tree); data-defined override per property | Turning Auto update on (drops all edits); none per item | Bad expression shows raw `[% %]`; null shows empty; empty table: header, hide, or message | `[% expression %]` with `@variables` and functions | Functions: `format_number(n, places, lang, omit_group, trim_zeros)`, `format_date` |
| Figma | Component instances; variables on properties (string text content, numbers, colors, booleans) | Same file: immediate; library: publish then accept | Library update badge (not per property) | Per property (field list per layer) | Per property and all | Variable deleted: forum says a note and a "Detach deleted variables" command (U) | No inline token; whole-property binding | Not applicable (variable value as typed) |
| Penpot | Component copies | On main change (normal sync) | Not found | Per attribute group (~20 groups); `:touched` set | Reset overrides (all groups); Update main (push) | Detach turns copy into a group | Not applicable | Not applicable |
| InDesign | Placed files; linked page items and stories; text variables | Modified links wait for Update Link (or on save if set); variables live | Links panel icons: modified, missing (U) | Linked items: 5 attribute groups kept or overwritten per link (P) | Update Link overwrites unkept groups; warning option (P) | Missing icon, last preview kept, Relink (U) | Variables inserted by menu, no typed syntax (U) | Date format in variable definition (U) |
| Word | Fields (DOCPROPERTY and others); linked objects | Fields on open and F9; links automatic or manual per link | None on the page; result shown until updated | Whole field (lock) | Unlock then F9 | "Error! ..." text (U); linked object keeps picture (U) | `{ DOCPROPERTY "Name" \* Upper }` | Switches, `\#` picture (U) |
| PowerPoint | Linked Excel charts and objects | Automatic or manual per link; "Update Links" bar on open (U) | Security bar on open (U) | Whole object | Update Now | Change Source (U) | None | From Excel |
| Canva | Charts on Canva Sheets or imported data (U) | Live for Canva Sheets; manual for external (U) | Not found | Not found | Not found | Not found | None | Not found |

## 5. The override models compared

Criteria, set before the comparison: (a) a board edit is never lost silently when the model changes; (b) everything not
edited keeps following the model; (c) Reset of one property and of all; (d) small to save (undo keeps 50 snapshots);
(e) simple to show in the Properties panel on a phone; (f) fits ES5 and the existing board object records.

| Model | Seen in | (a) | (b) | (c) | (d) | (e) | (f) |
|---|---|---|---|---|---|---|---|
| Whole element: freeze a copy, edit it | QGIS legend manual mode; ArcGIS convert to graphics; Word lock; Figma detach | Yes, but the object stops updating at all | No | Reset all only (and QGIS's Reset discards edits) | Large: the copy is saved | Simple: one switch | Easy |
| Per property: a set of overridden property keys | Figma instances (`overrides` field list) | Yes | Yes | Yes, one and all | Small: key names plus the values | Clear: mark each field, Reset beside it | Easy: an object of keys |
| Per attribute group: touched groups | Penpot `:touched`; InDesign `preserve*` flags | Yes | Yes, at group grain (an edit to font size also freezes font family) | Penpot: all; InDesign: chosen per link | Smallest | Fewer marks, but the user must learn the groups | Easy, needs a key-to-group table |
| Binding replaced by a value | Figma variables (typing detaches); ArcGIS/QGIS (editing tag text) | Edit wins | Only the unedited properties stay bound | Rebind, no Reset | Small | Clear | Easy |

**Recommendation for V175.** Per property, with Penpot's two refinements:

1. Each live board object stores `bind` (what it is linked to: kind and source id, plus parameters such as the view,
   the schedule, the measure, the format) and `ovr`, a set of overridden property keys (`{"title":1,"fill":1}`). The
   values on the object are what is drawn; the source writes only into keys not in `ovr`. This is Figma's model and
   Penpot's NORMAL SYNC rule ("not touched" are copied), at property grain, which a Properties panel can mark row by row.
2. Like Penpot's `set-shape-attr`: an edit marks a key only when the value really changes (numbers compared within a
   tolerance), only on a bound object, and never when the refresh itself writes (an `ignoreTouched` flag on the
   writer). Our own design choice, not taken from Penpot (which does touch geometry): moving or resizing the frame on
   the board is layout, not an override; only the content keys are overridable.
3. Where one source property drives several drawn ones (a text field's words and its styling, Penpot's text special
   case), keep them as separate keys so styling a live number does not freeze its value.
4. Reset per key (delete it from `ovr`, refresh) and Reset all (empty `ovr`, Penpot FORCED SYNC). A separate one-way
   "Unlink" (Figma detach, QGIS Convert to Static, ArcGIS Convert to graphics, Word Ctrl+Shift+F9) drops `bind` and
   keeps the values. Optional, not required: a group table for a "keep this group" choice as InDesign offers; not
   needed at this scale.
5. Store the last resolved value with the object (Word's field result, InDesign's preview) so a missing source can show
   the last known value with a "source missing" mark rather than an empty box (ArcGIS) or raw code (QGIS). This bears on
   H10: the store is binding + overrides + one cached value, not the binding alone.

What would change it: if the owner wants a legend or schedule edited row by row (rename a row, hide a row), the
override keys become paths (`rows.<id>.label`), still per property; QGIS's whole-copy model would only be preferable
if row edits must survive the rows themselves being restructured.

**Text fields.** Token syntax: QGIS's `[% ... %]` is the closest precedent for text inside prose but runs an expression
language; ArcGIS's XML tag is hard to type on a phone; Word's braces need a special key. A brace or bracket token naming
a field from a fixed list (looked up, never evaluated) meets H9; on a parse failure show the token as typed (QGIS) and
mark it, on a null show `emptyStr` or a dash (ArcGIS). Formatting per token, like ArcGIS attributes or QGIS
`format_number(places, omit_group_separators, trim_trailing_zeroes)`: places, grouping, units.

## 6. Counter-evidence and limits

- **H4 fails.** Not every tool marks staleness. ArcGIS dynamic text and QGIS labels are evaluated when drawn, so they
  carry no stale mark; Word shows a stale field result with no mark until F9; QGIS tables need Refresh Table
  Data and show no stale mark. Only InDesign's Links panel (U) and PowerPoint's open-time bar (U) mark it.
- **H5 holds with a nuance.** Figma: per property, Reset one and all (P). Penpot: per attribute group, but its UI Reset
  is all groups at once; no per-group Reset found.
- **H-n2-1 holds where there are overrides** (Figma, Penpot, InDesign), but QGIS's manual legend does not follow the
  source at all, and in ArcGIS there is no override, only conversion.
- **H-n2-2 holds.** Every tool with links has a one-way freeze: ArcGIS Convert to graphics, QGIS Convert to Static, Figma
  detach, Penpot detach, InDesign Convert Variable To Text (U), Word unlink (U), PowerPoint Break Link (P).
- **Figma overrides are not always reliable** (forum, U): nested icon swaps stop receiving main-component fills; slot
  overrides mark a whole slot as overridden; renamed layers break override tracking (overrides matched by layer name).
  Lesson: key overrides by a stable id, never by a display name.
- **InDesign preserve options misbehave** (community, U): colour changes not registered as local edits, "preserve
  local edits" greyed out, children reverting to the parent. Lesson: the group a property belongs to must be explicit
  and tested.
- **PowerPoint linked charts fail to refresh** (Microsoft Q&A, U), even with Automatic Update on; the links dialog
  changes one link at a time. Lesson: a visible "refresh all" and a per-object state.
- **Figma ghost variables** (forum, U): deleted variables linger on layers. Lesson: a missing source must be found and
  listed, not only drawn.
- **Old sources.** Figma's override rule is from a 2018 blog post; ArcGIS pages are 3.4 (latest moved hosts and its
  pages 404'd here); QGIS 3.44 manual; Penpot and QGIS code from the default branches on 2026-11-08.

## 7. Open (U, to confirm before the code relies on it)

- ArcGIS table attribute dynamic text syntax; what a tag shows when its map frame is deleted.
- InDesign Links panel icon names and missing-link behaviour; text variable list and the Define dialog choices
  (helpx 403).
- Word: "Error! Unknown document property name." wording; `\#` numeric picture; Ctrl+Shift+F9 on a Microsoft page.
- PowerPoint: "Update Links" bar and Change Source wording on a Microsoft page.
- Canva linked chart refresh (canva.com 403).
- Figma: state of a layer whose variable was deleted; any on-canvas mark for overrides.
- Penpot: whether a per-group Reset exists anywhere in the UI.
- Notion / Google Docs smart chips: not searched.

## 8. References (all read 2026-11-08)

| URL | What was read | Level |
|---|---|---|
| https://pro.arcgis.com/en/pro-app/3.4/help/layouts/add-and-modify-dynamic-text.htm | Tag types, attributes, rename, null | P |
| https://pro.arcgis.com/en/pro-app/3.4/help/layouts/use-dynamic-text-with-map-series.htm | Page tags, attribute tag, domainlookup | P |
| https://pro.arcgis.com/en/pro-app/3.4/help/layouts/add-and-modify-table-frames.htm | Dynamic table frames, display when populated | P |
| https://pro.arcgis.com/en/pro-app/3.4/help/layouts/charts.htm | Chart frames update | P |
| https://pro.arcgis.com/en/pro-app/3.4/help/layouts/work-with-layout-elements.htm | Dynamic vs static elements | P |
| https://pro.arcgis.com/en/pro-app/3.4/help/layouts/work-with-a-legend.htm | Synchronize with map; Convert to graphics | P |
| https://pro.arcgis.com/en/pro-app/3.4/help/layouts/work-with-legend-items.htm | Item order, patches | P |
| https://docs.qgis.org/latest/en/docs/user_manual/print_layout/layout_items/layout_label.html | `[% %]`, Convert to Static | P |
| https://docs.qgis.org/latest/en/docs/user_manual/print_layout/layout_items/layout_legend.html | Auto update, Update All | P |
| https://docs.qgis.org/3.44/en/docs/user_manual/print_layout/layout_items/layout_tables.html | Refresh Table Data, empty table | P |
| https://docs.qgis.org/3.44/en/docs/user_manual/expressions/functions_list.html | format_number, item_variables, layout variables | P |
| https://docs.qgis.org/latest/en/docs/user_manual/print_layout/create_output.html | Data defined override button | P |
| https://raw.githubusercontent.com/qgis/QGIS/master/src/core/layout/qgslayoutitemlegend.cpp | Sync modes, manual tree clone (GPL, method only) | P |
| https://raw.githubusercontent.com/qgis/QGIS/master/src/core/layout/qgslayoutitemlabel.cpp | currentText, refresh, convertToStaticText (GPL) | P |
| https://raw.githubusercontent.com/qgis/QGIS/master/src/core/expression/qgsexpression.cpp | replaceExpressionText error and null handling (GPL) | P |
| https://help.figma.com/hc/en-us/articles/360039150733-Apply-overrides-to-instances | Overridable list, Reset | P |
| https://help.figma.com/hc/en-us/articles/360038665934-Edit-main-components | Propagation | P |
| https://help.figma.com/hc/en-us/articles/360039234193-Review-and-accept-library-updates | Library updates | P |
| https://www.figma.com/blog/figma-feature-highlight-component-overrides/ | Override survives main edit (2018) | P (old) |
| https://developers.figma.com/docs/plugins/api/InstanceNode/ | overrides, resetOverrides, detachInstance | P |
| https://help.figma.com/hc/en-us/articles/15343107263511-Apply-variables-to-designs | Bindable properties, detach | P |
| https://help.figma.com/hc/en-us/articles/14506821864087-Overview-of-variables-collections-and-modes | String variables, aliasing | P |
| https://forum.figma.com/ (threads 36817, 54395, 51686, 28137 and others in log rows 18, 23) | Override and variable failures | U |
| https://raw.githubusercontent.com/penpot/penpot/develop/common/src/app/common/types/component.cljc | sync-attrs, touched helpers, MPL-2.0 header | P |
| https://raw.githubusercontent.com/penpot/penpot/develop/common/src/app/common/logic/libraries.cljc | Normal, forced, inverse sync; update-attrs | P |
| https://raw.githubusercontent.com/penpot/penpot/develop/common/src/app/common/types/container.cljc | set-shape-attr touched rules | P |
| https://help.penpot.app/user-guide/components/ | Reset overrides, Update main, Detach | P |
| https://helpx.adobe.com/indesign/using/graphics-links.html | Refused, 403 | - |
| https://helpx.adobe.com/indesign/using/text-variables.html | Refused, 403 | - |
| https://helpx.adobe.com/au/indesign/desktop/automation-and-scripting/document-automation/link-and-update-content-across-documents.html | Refused, 403 | - |
| https://developer.adobe.com/indesign/uxp/dom/api/l/linked-page-item-option/ | preserve* flags, warn on update | P |
| Search summaries of helpx and community.adobe.com (log rows 29 to 31) | Links icons, text variables, preserve bugs | U |
| https://support.microsoft.com/en-us/word/insert-edit-and-view-fields-in-word | Update on open, F9, lock/unlock | P |
| https://support.microsoft.com/en-us/word/field-codes-docproperty-field | DOCPROPERTY syntax | P |
| https://support.microsoft.com/en-us/powerpoint/link-or-embed-a-powerpoint-slide-in-a-word-document | Linked objects automatic/manual, Break Link | P |
| https://learn.microsoft.com/en-us/answers/questions/5182442/powerpoint-does-not-update-linked-tables-charts-pr | Linked charts not refreshing | U |
| https://www.canva.com/help/import-to-charts/ | Refused, 403; search summary only | U |
