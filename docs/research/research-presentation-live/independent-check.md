# V175 independent check (research agent 4, second reader)

Written 2026-11-08 under `docs/research/research-protocol.md`, part "Research as a scientist does it", item 9.
I re-read every fact listed below at its cited primary source. I did not take a fact from the working notes or
from a search summary. The notes checked are `practice-bim.md` (note 1), `practice-design-gis.md` (note 2) and
`invalidation.md` (note 3; the coordinator added it to the scope). Pages were fetched with `curl -sL -A "Mozilla/5.0
(research check)"` and stripped to text by a small script. The downloads stayed in a temporary folder outside the
repository. Code was read at pinned commits through raw.githubusercontent.com.

Verdicts:

- **CONFIRMED**: the source says what the note says.
- **NOT CONFIRMED**: the source says something else; the table gives what it says.
- **UNREACHABLE**: the host refused, with its status.

A row confirmed only at level S (a forum) is marked "CONFIRMED (S)".

## 1. Results

| # | Fact | Note | Source re-read | Verdict | What the source says |
|---|---|---|---|---|---|
| 1 | Archicad drawing Update Type Auto: "updated automatically when the layout is activated" | 1 | AC25 Drawing Settings, https://help.graphisoft.com/AC/25/INT/_AC25_Help/150_UserInterfaceToolSettings/150_UserInterfaceToolSettings-28.htm | CONFIRMED | "Auto: Drawing will be updated automatically when the layout is activated." For a drawing from another source, Archicad checks whether it needs updating. |
| 2 | Archicad Manual: frozen as placed; Store Drawing checked automatically for Manual | 1 | same | CONFIRMED | "The Drawing is frozen in the state its source view or file was in when placed on the layout." "Store Drawing in the Project File: Checked automatically for Manual-update Drawings." |
| 3 | An Automatic drawing updates as soon as its layout or window is activated | 1 | AC24 Drawing Manager, https://help.graphisoft.com/AC/24/INT/_AC24_Help/130_UserInterfaceDialogBoxes/130_UserInterfaceDialogBoxes-76.htm | CONFIRMED | "(A Drawing set to Automatic update will be updated as soon as you activate its Layout or window.)" |
| 4 | Drawing statuses OK, Modified, Missing, Embedded, Needs Checking, with the quoted meanings | 1 | same | CONFIRMED | OK "Drawing is updated."; Modified "Source has been modified. Click the Update button..."; Missing "The source of the linked drawing cannot be found."; Embedded "This Drawing's link has been broken and cannot be updated."; Needs Checking: the quick-check "cannot determine definitively". Not Accessible, To be Updated and Updating are on the page as well. |
| 5 | Autotext "is automatically updated to follow any changes in the model, layout or drawing" | 1 | AC27 Autotext, https://help.graphisoft.com/AC/27/INT/_AC27_Help/070_Documentation/070_Documentation-66.htm | CONFIRMED | The page says it word for word, with the same five places autotext can be used. |
| 6 | Missing autotext data shows placeholder text, which updates when the data appears | 1 | AC27 How to Insert Autotext, .../070_Documentation-67.htm | CONFIRMED | "If the referenced information is not available, you will see a placeholder text. When the missing information becomes available, the placeholder text is immediately updated..." |
| 7 | AC27 keys `<PROJECTNAME>`, `<LAYOUTNUMBER>`, `<DRAWINGSCALE>`, `<SITEGROSSAREA>`, `<PROJECT_ID>`, `<CURRENTTRANSMITTALSETDATE>` | 1 | AC27 Autotext Keywords, .../070_Documentation-69.htm | CONFIRMED | All six strings are in the page's keyword table. |
| 8 | LayOut "treats the viewport changes as overrides of the SketchUp model settings"; tag overrides can be pushed to the model | 1 | Working with Dashes, https://help.sketchup.com/en/layout/styling-sketchup-linework | CONFIRMED | Word for word: "...or update the SketchUp model with the tag overrides changes." |
| 9 | Reset All (Viewport section) reverts all; Reset (Tags section) reverts tags; per tag: Reset All, Reset Dashes, Reset Visibility | 1 | same | CONFIRMED | "To revert to all SketchUp model settings, including those for linework, click Reset All in the Viewport section. To revert only tag settings, click Reset in the Tags section." The per-tag list is as quoted. |
| 10 | Reset per section for Camera, Style and Effects; a changed section turns dark grey; Reset All at the top | 1 | forums.sketchup.com threads 160597 and 146169 (Discourse `.json`) | CONFIRMED (S) | DaveR: "Reset All will show in the top section of the SketchUp Model panel and Reset will show up in the section where you've made changes... The dark background for the section will also indicates it's been modified." The help page names only the Viewport and Tags resets. The Camera, Style and Effects resets come from the forum only, as the note says. |
| 11 | Updating a table reference overrides local changes, including local formatting | 1 | Adding Tables, https://help.sketchup.com/en/layout/adding-tables-document | CONFIRMED | "Warning: When you update a table reference, you override any local changes you made to the data in LayOut." Excel formatting is reimported and "overrides any local formatting". |
| 12 | Auto-text tags are typed as `<PageNumber>`; SceneName is a supported tag; Date Published shows "Unpublished" | 1 | Automating Title Block Text, https://help.sketchup.com/en/layout/automate-titleblocks | CONFIRMED | "type the tag name, such as <PageNumber>, into a text box and press Enter". SceneName is in the tag list. "Unpublished displays if it hasn't been exported or printed." |
| 13 | References update on demand (Update); an option checks them at open; a missing or outdated one shows red | 1 | Managing Changes, https://help.sketchup.com/en/layout/managing-model-references | CONFIRMED | "Update – Replaces an outdated file with its latest version." "Check references when loading this document ... each time you open a document." "If a reference is missing or outdated, its status is in red." |
| 14 | Viewport overrides survive a relink or update; styles sometimes reset | 1 | forum thread 255744 (`.json`) | CONFIRMED (S) | DaveR: relinking or updating "should not change those settings back. I have seen the styles get reset once in a while." |
| 15 | The red label warning does not print or export | 1 | forum thread 262449 (`.json`) | CONFIRMED (S) | Poster endlessfix: the red "broken reference" warning "does not print or export". One practitioner only. |
| 16 | LayOut 2023 reconnects a label to a different component by default | 1 | forum thread 243365 (`.json`) | CONFIRMED (S) | Poster adam: "a side effect of LayOut's efforts to automatically reconnect labels ... We now assume it is okay to connect to a different component by default". The JSON's `staff` flag is false, as the note says. |
| 17 | FIELDEVAL bitcode: 0 not updated, 1 open, 2 save, 4 plot, 8 ETRANSMIT, 16 regeneration; initial value 31; the Date field is not updated by FIELDEVAL | 1 | AutoCAD 2025 FIELDEVAL, https://help.autodesk.com/cloudhelp/2025/ENU/AutoCAD-Core/files/GUID-EF5D2DDE-A170-4BB4-8F76-7F3FAFE30E56.htm | CONFIRMED | Exactly that table; "Saved in: Drawing Initial value: 31"; the Date note as quoted. |
| 18 | FIELDDISPLAY: grey background, 1 on and 0 off; the background is not plotted | 1 | AutoCAD 2025 FIELDDISPLAY, .../GUID-99DB691B-9E11-4BD5-AFFE-BC1312F3281A.htm | CONFIRMED | "Initial value: 1 The background is not plotted." Saved in the registry, not in the drawing. |
| 19 | "----" for a field with no value; "####" for an invalid field | 1 | About Using Fields in Text, .../GUID-B9ADAE6A-2DD1-4C44-B126-CF3FF92EBC68.htm | CONFIRMED | "A field for which no value is available displays hyphens (----)" (example: a blank Author). "An invalid field displays pound signs (####)" (example: CurrentSheetName in model space). |
| 20 | The Field dialog contradicts row 19: it shows "----" when the value is invalid, and "####" when a sheet set field's source is inaccessible | 1 | Field Dialog Box, .../GUID-1B6DD22B-10D1-44ED-BAA2-E6D79FE52327.htm | CONFIRMED | "displays an empty string (----) if the field value is invalid"; "...the value for the field will be displayed as '####'." The contradiction is in Autodesk's own pages, as the note says. |
| 21 | The field code string is `%<\AcVar Date \f "M/d/yyyy">%` (delimiters `%<` and `>%`) | 1 | AutoCAD 2016 ActiveX FieldCode, https://help.autodesk.com/cloudhelp/2016/ENU/AutoCAD-ActiveX/files/GUID-FE0C5004-B723-4AE8-888A-7DF11C765C89.htm | **NOT CONFIRMED** | The VBA literal is `"%<\AcVar Date \f ""M/d/yyyy""%>%"`, which is the string `%<\AcVar Date \f "M/d/yyyy"%>%`. The LISP example agrees. The page's string closes with `%>%` after the format's closing quote, not `">%`. The 2025 Field dialog, FIELD and To Insert a Field pages contain no field code string, so they settle nothing. |
| 22 | Revit: editing project-specific title block values on a sheet updates all sheets; sheet-specific values apply to that sheet only | 1 | Revit 2022 Add Custom Fields to a Title Block, https://help.autodesk.com/cloudhelp/2022/ENU/Revit-DocumentPresent/files/GUID-5641C187-D1CC-494F-B20D-E01C46489DE8.htm; Revit 2021 Enter Project-Specific Information, .../2021/.../GUID-183531FC-83D3-4C75-B912-3877142DA319.htm | CONFIRMED | 2022: "You can change these values in that dialog or on a sheet. Whenever you change project-specific information, Revit updates all sheets in the project with the changes." "These changes apply only to the individual sheet." 2021: "Enter the information directly on a sheet ... Revit updates all sheets in the project with the new information." The note gives this wording under 2021 and 2022; the exact quote is on the 2022 page. |
| 23 | Vectorworks: an out-of-date viewport shows red text on the Update button and, optionally, a red and white striped border | 1 | VW2024 Viewport status, https://app-help.vectorworks.net/2024/eng/VW2024_Guide/Viewports2/Viewport_status.htm | CONFIRMED | As quoted, with the border set in Document preferences: Display tab. Red "X" for an empty viewport; red broken-link icon for an unlinked marker. |
| 24 | Vectorworks: printing a layer with an out-of-date viewport prompts to print it as is or update first; wireframe viewports update automatically | 1 | VW2024 Updating viewports, .../Viewports2/Updating_viewports.htm | CONFIRMED | "If a layer with an out-of-date viewport is printed, a message prompts you either to print the viewport as an out-of-date viewport or to update the viewport before printing." The wireframe sentence is as quoted. |
| 25 | Rhino 8 text fields use `%<...>%` and show `####` when a formula cannot be evaluated | 1 | https://docs.mcneel.com/rhino/8/help/en-us/information/text_fields.htm | CONFIRMED | "All text fields are in the syntax of %< field and options >%. When a formula cannot be evaluated an error string of #### is displayed." |
| 26 | ArcGIS Pro tag syntax `<dyn type="mapFrame" name="..." property="scale"/>` | 2 | ArcGIS Pro 3.4 Add and modify dynamic text, https://pro.arcgis.com/en/pro-app/3.4/help/layouts/add-and-modify-dynamic-text.htm | CONFIRMED | `<dyn type="mapFrame" name="My Map" property="scale"/>`, with project, layout and other types on the page. |
| 27 | `decimalPlaces`, `emptyStr`, `preStr` and `postStr` attributes; an empty bounding box when a tag parses to nothing | 2 | same | CONFIRMED | Each attribute is quoted with examples. "If a text element contains nothing but a dynamic text tag that currently parses to nothing, an empty bounding box appears". |
| 28 | A tag remembers its map frame through a rename but keeps showing the old name | 2 | same | CONFIRMED | "the tag remembers the map frame it references, but the tag does not update to reflect the map frame's new name." |
| 29 | Export tags are blank until the layout is exported | 2 | same | CONFIRMED | "the text on the page is blank until the layout is exported." |
| 30 | Dynamic text is "evaluated when drawn" and always current (note 2, sections 4 and 6; the coordinator's "evaluated at draw") | 2 | same; and 3.4 Work with layout elements, .../layouts/work-with-layout-elements.htm | **NOT CONFIRMED** | The dynamic text page states no refresh rule; no sentence says the text is evaluated when drawn. The layout elements page says only: "Dynamic elements update in response to changes in the data or the map extent. Static elements remain the same regardless of changes in the data." Note 2 section 3.1 already calls this "implied, not stated" (medium). Section 6 states it as fact, and the source does not support that. |
| 31 | QGIS: dynamic parts of a label are written between `[%` and `%]` | 2 | QGIS label, https://docs.qgis.org/latest/en/docs/user_manual/print_layout/layout_items/layout_label.html | CONFIRMED | "Dynamic parts of a label need to be surrounded by [% and %]". |
| 32 | QGIS Convert to Static replaces the dynamic parts with their current values | 2 | same | CONFIRMED | "Any dynamic parts of the label's contents will be evaluated and replaced with their current values. You can then manually tweak the resulting text". |
| 33 | QGIS legend: Auto update checked keeps it current; unchecked allows edits; Update All | 2 | QGIS legend, .../layout_items/layout_legend.html | CONFIRMED | "The legend will be updated automatically if Auto update is checked. When Auto update is unchecked this will give you more control over the legend items". "But these customization can only be done with Auto update disabled." Update All is described. |
| 34 | In the code, Auto update maps to AllProjectLayers and Manual; switching to Manual clones the project layer tree; switching back drops the custom tree | 2 | QGIS @91d4a333d5de2a0b6b572edbe0d008c346983102, `src/core/layout/qgslayoutitemlegend.cpp` 436-471 | CONFIRMED | `setAutoUpdateModel` calls `setSyncMode(autoUpdate ? AllProjectLayers : Manual)`. AllProjectLayers and VisibleLayers call `setCustomLayerTree(nullptr)`. Manual calls `resetManualLayers`, which clones `layerTreeRoot()`. |
| 35 | `replaceExpressionText`: a parse or evaluation error leaves the raw `[% %]` text in place; a null gives an empty string | 2 | same commit, `src/core/expression/qgsexpression.cpp` | CONFIRMED | On `hasParserError()` and on `hasEvalError()`, the original slice of text is appended and the loop continues. The result string is set only when the result is not null. |
| 36 | Figma: Reset > Reset [property]; Reset > Reset all changes; only changed properties are listed | 2 | https://help.figma.com/hc/en-us/articles/360039150733-Apply-overrides-to-instances | CONFIRMED | Three sentences, word for word. |
| 37 | A Figma override stops following the main for that property only; other properties still follow | 2 | Figma blog 2018, https://www.figma.com/blog/figma-feature-highlight-component-overrides/ | CONFIRMED | "the instance still updates accordingly, except for whatever property you manually changed ... will stay green even if you edit the master component to be red. However, if you change the stroke weight ... the instance will reflect those changes". The source dates from 2018, as the note says. |
| 38 | Plugin API: `overrides` lists directly overridden fields; `resetOverrides` is deprecated for `removeOverrides` | 2 | https://developers.figma.com/docs/plugins/api/InstanceNode/ | CONFIRMED | "Returns an array of all of the fields directly overridden on this instance. Inherited overrides are not included." "DEPRECATED: Use removeOverrides instead." |
| 39 | Penpot `sync-attrs` puts each attribute in a group; a modified attribute marks its group `:touched`, and a sync then leaves that group alone | 2 | Penpot @904cdd97163dc77c0d875f509ccab9ff234d7bae, `common/src/app/common/types/component.cljc` 42-53 | CONFIRMED | The comment and map are as described (`:name-group`, `:fill-group`, `:content` split into `:geometry-group`/`:content-group`, and so on). One wording difference: the comment says "in a shape inside a component", where the note says "in a copy". The copy-only rule is in row 41. |
| 40 | A group is touched only when the value changes; geometry is compared within 1 px | 2 | same commit, `common/types/container.cljc`, `set-shape-attr` 639-711 | CONFIRMED | `equal?` uses `close-attrs?` with tolerance 1 for geometry and `close-attrs?` otherwise; `touched?` needs `(not equal?)`. |
| 41 | A group is touched only on a copy | 2 | same | CONFIRMED | The update of `:touched` runs only when `in-copy?` (`ctk/in-component-copy?`). |
| 42 | A group is not touched during a sync | 2 | same, and `common/logic/libraries.cljc` 1896-1907 | CONFIRMED | `ignore?` is true when `ignore-touched` is passed. Every sync write goes through `add-update-attr-operations`, which sets `:ignore-touched true`. `position-data` never touches. |
| 43 | A geometry edit touches `:geometry-group` unless `ignore-geometry` is passed; width and height are outside that exemption | 2 | `container.cljc` 653-711 | CONFIRMED, with a tension | The logic is as the note reads it. The inline comment on `(= group :geometry-group)` says "never triggers touched by itself", which can be read against it. In the code as written, a geometry change in a copy, without `ignore-geometry`, does add the group. |
| 44 | Reset (FORCED SYNC) copies everything and clears touched; INVERSE SYNC pushes to the main and clears touched; NORMAL SYNC copies only untouched groups | 2 | `libraries.cljc` 708-728; `update-attrs` 1937-1942 | CONFIRMED | The comment block is as quoted. `update-attrs` skips touched groups "If omit-touched? is true", and `omit-touched?` is `(not reset?)` (966). |
| 45 | Penpot UI: "Overrides are modifications made in a specific copy..."; "Reset overrides" | 2 | https://help.penpot.app/user-guide/components/ | CONFIRMED | Both sentences are on the page. |
| 46 | InDesign `LinkedPageItemOption`: `preserveAppearance`, `preserveSizeAndShape`, `preserveInteractivity`, `preserveFrameContent`, `preserveOthers`, `warnOnUpdateOfEditedPageItem`, `updateLinkWhileSaving` | 2 | https://developer.adobe.com/indesign/uxp/dom/api/l/linked-page-item-option/ | CONFIRMED | All seven property names are on the page. |
| 47 | Word updates fields when a document opens | 2 | https://support.microsoft.com/en-us/word/insert-edit-and-view-fields-in-word | CONFIRMED | "By default, Word automatically updates fields when a document is opened." |
| 48 | Ctrl+F11 locks a field; Ctrl+Shift+F11 unlocks it | 2 | same | CONFIRMED | "To lock a field so that field results are not updated, click the field, and then press Ctrl+F11." Unlock: Ctrl+Shift+F11. |
| 49 | Ctrl+Shift+F9 unlinks a field (the note has it as U) | 2 | Microsoft, Keyboard shortcuts in Word, https://support.microsoft.com/en-us/office/keyboard-shortcuts-in-word-95ef89dd-7142-4b50-afb2-f762f663ceb2 | CONFIRMED, upgrade U to P | "Ctrl+Shift+F9: unlinks the current field." The same page has "Ctrl+F11: locks the current field." |
| 50 | DOCPROPERTY syntax `{ DOCPROPERTY "Name" }`, switch `\* Upper`; Alt+F9 toggles | 2 | https://support.microsoft.com/en-us/word/field-codes-docproperty-field | CONFIRMED | "{ DOCPROPERTY " Name " }"; the example `{ DOCPROPERTY Manager \* Upper }`; Alt+F9 toggles field codes and results. |
| 51 | ECMA-402 sanctioned units: 45, with lengths, `acre` and `hectare`; no `square-meter` or `cubic-meter` | 3 | tc39/ecma402 @3691634ebc1794f2af74cb26e59824b21090c3ad, `spec/locales-currencies-tz.html` | CONFIRMED | The table lists 45 units, among them acre, hectare, meter, centimeter, millimeter and kilometer. The file has no `square-meter` or `cubic-meter` anywhere. |
| 52 | Node throws `RangeError` for `unit:'square-meter'` | 3 | run here (Node v26, this machine) | CONFIRMED | "RangeError Invalid unit argument for Intl.NumberFormat() 'square-meter'". `hectare` formats as "2 ha". |
| 53 | BCD: Intl.NumberFormat constructor in Chrome 24, Firefox 29, Safari 10, IE 11, Edge 12; `maximumFractionDigits` the same | 3 | mdn/browser-compat-data @82daeebf5a7073d55223a8cdb8aa54fb9416e27d, `javascript/builtins/Intl/NumberFormat.json` | CONFIRMED | The constructor is {chrome 24, firefox 29, safari 10, ie 11, edge 12}. `options_maximumFractionDigits_parameter` is {24, 29, 10}. |
| 54 | Unit style: Chrome 77, Firefox 78, Safari 14.1 | 3 | same | CONFIRMED | `options_unit_parameter` and `options_unitDisplay_parameter` are {chrome 77, firefox 78, safari 14.1}. BCD records it under the `unit` option, not under a `style:'unit'` key. |
| 55 | `formatToParts`: Chrome 64, Safari 13 | 3 | same | CONFIRMED | {chrome 64, firefox 58, safari 13, edge 12; no IE}. |
| 56 | Preact signals: a module-level `globalVersion` (line 161) as a fast path before per-source checks (`needsToRecompute`, 504-530); "Cycle detected" at 464 and 754 | 3 | preactjs/signals @30a797e962c76cc2e623e84f4194a00b9f0c5c8f, `packages/core/src/index.ts` | CONFIRMED | `let globalVersion = 0;` is at 161. In `Computed._refresh`: `if (this._globalVersion === globalVersion) return true;` (661), then `needsToRecompute` walks `_sources` comparing `_version`. "Cycle detected" is thrown at 464 and 754, and also at 927. |
| 57 | MobX 7 needs `Proxy` and has no ES5 fallback | 3 | mobxjs/mobx @2a97ff69a8bb4d6c3c8582da07ffd1c53c6612db, `docs/configuration.md` 14-20; `packages/mobx/package.json` | CONFIRMED | "MobX requires Proxy support to make arrays and plain objects observable." "MobX 7 does not include the older ES5 fallback implementation and no longer supports configure({ useProxies })." The package version at this commit is 7.1.5. |
| 58 | Mokhov, Mitchell, Peyton Jones 2018 model Excel as a restarting scheduler with a dirty bit | 3 | PDF, https://www.microsoft.com/en-us/research/uploads/prod/2018/03/build-systems.pdf (pdftotext); snowleopard/build @43b18b9 `src/Build/System.hs` | CONFIRMED | Table 1: "Excel: Dirty cells, calc chain, Restarting". Section 4.2.1: "Excel models the dirty bit approach most directly". Section 5: "Our model of Excel uses the restarting scheduler and the dirtyBitRebuilder". System.hs line 64: `excel = restarting dirtyBitRebuilder` (also `shake = suspending vtRebuilder`, `bazel = restarting2 ctRebuilder`). |
| 59 | `saveSoon` bumps `A3D_REV` at `src/js/engine/bim/region-regenerate.js:104`; the source comment says every model mutation passes through it | 3 | the file, read here | CONFIRMED (one line off) | Line 104 is `setA3D_REV(A3D_REV+1);   /* __acad3dV122 */`. The comment "every model mutation passes through here" is at 99-100, not 98-99 as note 3 says. |
| 60 | `A3D_REV` is declared at `core/objects-save.js:48` with its setter at 82, in memory only | 3 | the file | CONFIRMED | `var A3D_REV=0;` (48); `function setA3D_REV(v)` (82). |
| 61 | `bimLoadProjectRecord` (`ui/project-tabs.js:185`) neither calls `saveSoon` nor bumps the revision | 3 | the file, 185-199 | CONFIRMED | The function resets to the defaults, calls `bimApplyStoredState`, ensures types and buildings, clears the selection and refreshes. It has no `saveSoon` and no `setA3D_REV`. |
| 62 | `A3D_UNITS` is not persisted: declared at `properties/palette.js:53`; the comment at 49 names `bimUnitState`/`bimApplyUnitState`, which do not exist; it is in neither `bimProjectRecord` (`objects-save.js:53`) nor the undo snapshot (`plan-mode-sketch.js:293`) | 3 | the files; `grep -rn` over `src/` | CONFIRMED | `var A3D_UNITS={key:'m',dp:null};` is at 53. The only match in `src/` for `bimUnitState`/`bimApplyUnitState` is that comment. Neither `objects-save.js:53` nor `drawing/plan-mode-sketch.js:293` mentions units. |
| 63 | The bench numbers (`bench-output.json`) | 3 | re-ran `node docs/research/experiments/v175-invalidation/bench.mjs` once (output to a temporary file; the committed JSON was not touched) | CONFIRMED (same order of magnitude) | Same model (2000 objects, 943284 JSON bytes). Of 23 medians, 22 are within 25% of the recorded value. Examples: `stringify_plus_fnv_2000` 2.46 against 2.45 ms; `narrow_fingerprint_2000` 0.506 against 0.497; `Intl_new_each_200` 2.48 against 2.64; `snapshot_time_2000` 1.546 against 1.542. The exception is `rev_compare_1e6`, 0.62 against 0.34 ms (1.8 times), which is still sub-millisecond for a million compares. |

**Facts not re-checked.** These are on no one's priority list, or the notes already record them as U. They are
listed so that "every fact" is accounted for. A design that rests on one of them should check it first.

- Note 1:
  - Archicad: the Autotext Reference Drawing rule; the AC22 keyword table; the Drawing Titles sentence.
  - LayOut: Rendering Auto and Render; the label red highlight and Reconnect to Model; the SketchUp 2026.0 C API
    function names.
  - Revit: "Each view can be placed on one sheet only" (Add Views to a Sheet, 2023); the change engine sentence.
  - AutoCAD: DATALINKNOTIFY values 1 and 2; DATALINKUPDATE Write Data Link; data link locking; the table formula
    rules; Convert Field to Text (AutoCAD Architecture 2016).
  - Vectorworks: title block Link Value; the data tag `#Record#.#Field#` syntax; worksheet Recalculate.
  - Rhino: the function list.
- Note 2:
  - ArcGIS: the legend's Synchronize with map and Convert to graphics; table and chart frames; the map series page
    tags.
  - QGIS: tables (Refresh Table Data, empty table modes); `format_number`'s signature; that VisibleLayers is the
    default sync mode.
  - Figma: variables (bindable properties, detach).
  - Word: linked objects; PowerPoint Break Link.
- Note 3: the Excel recalculation document (MicrosoftDocs @eedbd61); the app-code rows about `pushUndo` and the
  drag path (H1); the 243 `saveSoon` callers (E1).

## 2. Discrepancies

1. **The AutoCAD field code delimiter (row 21).** Note 1, sections 3.4 and 4 and H5, gives
   `%<\AcVar Date \f "M/d/yyyy">%`. Autodesk's ActiveX example string is `%<\AcVar Date \f "M/d/yyyy"%>%`, which
   closes with `%>%`. Whichever form AutoCAD itself writes, the source cited does not show `">%`. Quote the
   source's string, or say the grammar is undocumented. The design does not take AutoCAD's syntax, so nothing
   downstream breaks.
2. **ArcGIS "evaluated when drawn" (row 30).** Note 2, section 6 (H4) and the comparison table say ArcGIS dynamic
   text is always live or evaluated at draw. No ArcGIS page read says so. The vendor's sentence is "Dynamic
   elements update in response to changes in the data or the map extent." H4's verdict for ArcGIS should cite that
   sentence and keep the "medium, implied" confidence that section 3.1 gives.
3. **Penpot's geometry comment (row 43).** The code touches `:geometry-group` on a copy's geometry edit unless
   `ignore-geometry` is passed. An inline comment says the group "never triggers touched by itself". The note's
   reading of the code is right. The phase note should not quote the comment as the rule.
4. **The Penpot comment's wording (row 39).** The source says "inside a component"; the note says "in a copy". The
   code's `in-copy?` test supports the note's meaning. This is a quotation accuracy point only.
5. **Revit quote attribution (row 22).** The "You can change these values in that dialog or on a sheet..." sentence
   is on the 2022 Add Custom Fields page, not on the 2021 page. The 2021 page says the same thing in other words.
6. **Word Ctrl+Shift+F9 (row 49).** Note 2 marks it U. It is on Microsoft's own keyboard shortcut page, so it
   moves to P.
7. **The line number in note 3 (row 59).** The `saveSoon` comment is at `region-regenerate.js:99-100`, not
   `98-99`.
8. **Canva's host.** Note 2 recorded https://www.canva.com/help/import-to-charts/ as 403. Today it answered 200 to
   the same curl user agent. The page is reachable, so the Canva facts in note 2 (still U) could be read at P. I
   did not re-check them: they are not on the priority list.
9. **LayOut per-section Reset (row 10).** It is confirmed only at level S (forum). The help page names only Reset
   All (Viewport section), Reset (Tags section) and the per-tag resets. Note 1 labels it this way, so this is a
   reminder, not an error: the phase note should not call the Camera, Style and Effects resets P.

## 3. Search log

| # | Where | What was fetched | Status | Use |
|---|---|---|---|---|
| 1 | help.graphisoft.com | AC24 Drawing Manager (-76), AC25 Drawing Settings (-28), AC27 pages -66, -67, -69 | 200 each | Rows 1 to 7 |
| 2 | help.sketchup.com | managing-model-references, automate-titleblocks, adding-tables-document, styling-sketchup-linework | 200 each | Rows 8, 9, 11 to 13 |
| 3 | forums.sketchup.com | `/t/160597.json`, `/t/146169.json`, `/t/255744.json`, `/t/262449.json`, `/t/243365.json` | 200 each | Rows 10, 14 to 16 |
| 4 | help.autodesk.com | AutoCAD 2025 FIELDEVAL, FIELDDISPLAY, About Using Fields, Field Dialog, FIELD, To Insert a Field; 2016 ActiveX FieldCode | 200 each | Rows 17 to 21 |
| 5 | help.autodesk.com | Revit 2021 GUID-183531FC, Revit 2022 GUID-5641C187 | 200 each | Row 22 |
| 6 | app-help.vectorworks.net | VW2024 Viewport_status, Updating_viewports | 200 each | Rows 23, 24 |
| 7 | docs.mcneel.com | Rhino 8 text_fields | 200 | Row 25 |
| 8 | pro.arcgis.com | 3.4 add-and-modify-dynamic-text, 3.4 work-with-layout-elements | 200 each | Rows 26 to 30 |
| 9 | docs.qgis.org | `latest` layout_label and layout_legend (the manual was read at `latest`, not 3.44) | 200 each | Rows 31 to 33 |
| 10 | raw.githubusercontent.com, qgis/QGIS @91d4a333 (master on 2026-11-08, from `git ls-remote`) | `qgslayoutitemlegend.cpp`, `qgsexpression.cpp` | 200 each | Rows 34, 35 |
| 11 | help.figma.com, figma.com/blog, developers.figma.com | Apply overrides; 2018 blog; InstanceNode | 200 each | Rows 36 to 38 |
| 12 | raw.githubusercontent.com, penpot/penpot @904cdd97 (develop on 2026-11-08, from `git ls-remote`) | `types/component.cljc`, `logic/libraries.cljc`, `types/container.cljc` | 200 each | Rows 39 to 44 |
| 13 | help.penpot.app | user-guide/components | 200 | Row 45 |
| 14 | developer.adobe.com | linked-page-item-option | 200 | Row 46 |
| 15 | support.microsoft.com | insert-edit-and-view-fields-in-word; field-codes-docproperty-field; keyboard shortcuts in Word | 200 each | Rows 47 to 50 |
| 16 | raw.githubusercontent.com, tc39/ecma402 @3691634 | `spec/locales-currencies-tz.html` | 200 | Row 51 |
| 17 | local Node | `new Intl.NumberFormat('en',{style:'unit',unit:'square-meter'})` | RangeError | Row 52 |
| 18 | raw.githubusercontent.com, mdn/browser-compat-data @82daeeb | `javascript/builtins/Intl/NumberFormat.json` | 200 | Rows 53 to 55 |
| 19 | raw.githubusercontent.com, preactjs/signals @30a797e | `packages/core/src/index.ts` | 200 | Row 56 |
| 20 | raw.githubusercontent.com, mobxjs/mobx @2a97ff6 | `docs/configuration.md`, `packages/mobx/package.json` | 200 each | Row 57 |
| 21 | microsoft.com research; raw.githubusercontent.com snowleopard/build @43b18b9 | build-systems.pdf (728559 bytes, 29 pages, pdftotext); `src/Build/System.hs` | 200 each | Row 58 |
| 22 | this repository | `region-regenerate.js` 96-110, `objects-save.js` 48/53/82, `project-tabs.js` 185-199, `palette.js` 47-55, `plan-mode-sketch.js` 293; `grep -rn` for the unit-state names | read | Rows 59 to 62 |
| 23 | this repository | `node docs/research/experiments/v175-invalidation/bench.mjs` (stdout to a temporary file) | exit 0 | Row 63 |
| 24 | refused-host probe, one curl each | community.graphisoft.com, forums.autodesk.com, forum.vectorworks.net, helpx.adobe.com/indesign/using/graphics-links.html, canva.com/help/import-to-charts/ | 403, 403, 403, 403, **200** | None of the priority facts depended on the four refused hosts. Canva: discrepancy 8. |

No priority fact was UNREACHABLE: every source the checked facts cite answered 200. The facts the notes take from
the four refused hosts are U in the notes and stay U; no row above depends on them.

## 4. Summary

- 63 facts re-checked: 61 CONFIRMED, 4 of them at level S (forum) only; 2 NOT CONFIRMED; 0 UNREACHABLE.
- NOT CONFIRMED:
  - Row 21: the AutoCAD field code. The source's string is `%<\AcVar Date \f "M/d/yyyy"%>%`, not `..."M/d/yyyy">%`.
  - Row 30: ArcGIS dynamic text "evaluated when drawn". No page says so; the source says dynamic elements "update
    in response to changes in the data or the map extent".
- Minor corrections: discrepancies 3 to 9.
