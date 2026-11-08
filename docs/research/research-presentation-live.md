# V175 Presentation P2: live elements (research, 2026-11-08)

Under `docs/research/research-protocol.md` ("Research as a scientist does it"). Levels: **P** read in the primary
source (the vendor's own page, the code read as text, the app's code, or measured here), **S** a dependable secondary
source with the gap said, **U** a search summary or an unchecked single copy, kept out of the code. This note is
written from five working notes in `docs/research/research-presentation-live/`, each with its own search log,
findings, levels and references:

| Working note | Side | Written by |
|---|---|---|
| `practice-bim.md` | Archicad, SketchUp LayOut, Revit, AutoCAD fields and data links, Vectorworks, Rhino 8 | research agent 1 |
| `practice-design-gis.md` | ArcGIS Pro dynamic text, QGIS print layouts, Figma, Penpot (code), InDesign, Word and PowerPoint, Canva | research agent 2 |
| `invalidation.md` | the app's change paths, four invalidation strategies, experiments E1 to E4, overrides as data, token syntax, edges | research agent 3 |
| `app-code-audit.md` | what the app already has, item by item of the row, by file and line | the main session |
| `independent-check.md` | the second reader's re-check of every fact the design rests on | research agent 4 (part 3a) |

## 1. Abstract

The question: how should a board's objects stay connected to the model and its analyses, so that a plan, a schedule,
a chart, a number or a line of text on a board always says what the model says; and how should an edit made on the
board be kept, marked and undone?

The answer has six parts.

1. **Half of it is already there.** Since V122 every model change moves one revision counter (`A3D_REV`, in
   `saveSoon`), and five draw caches key on it. V174d's map frames, legends, north arrows and scale bars, V172b's
   figures and V174c's title block are drawn from the model each time the revision moves. What is missing is text
   fields, single numbers, schedules, single KPI cards and result charts as board objects, and the override.
2. **Practice splits into two update models** (P, six BIM and CAD tools, four GIS and design tools). Cheap sources are
   always live and carry no stale mark: Revit, ArcGIS, QGIS labels, Archicad's autotext, Rhino fields. Slow sources
   wait for a trigger and say they are stale: Archicad's Manual drawings, LayOut's references, Vectorworks's rendered
   viewports, AutoCAD's fields at chosen events. The app's analyses are slow sources (a Ladybug run is minutes); its
   numbers and text are cheap ones.
3. **The override is per property, with Reset per property and Reset all,** as LayOut's viewports (per group of
   settings, each with its own Reset, and Reset All) and Figma's instances do; Penpot's code adds three rules (mark a
   key only when the value really changes, only on a linked copy, never when the refresh itself writes). A separate,
   one-way Unlink turns a live object into a plain one, as every tool with links offers (Convert to graphics, Convert
   to Static, detach, Ctrl+Shift+F9).
4. **The failures in practice are three, and each shapes the design:** LayOut users break viewports with overrides they
   never see (the mark must be on the object, not only in a panel); LayOut 2023 silently re-attaches a lost label to the
   nearest component (a lost link is marked, never guessed); LayOut's table update discards local edits (a refresh never
   overwrites an override).
5. **The counter is the right mechanism, measured.** A revision compare costs 0.6 ns; hashing a 2,000-wall model costs
   2.5 ms, more than recomputing a simple sum (0.04 ms); the costly case is the same source computed 20 times, so each
   source is computed once per revision (a runtime memo). A board of 80 objects with 20 live ones is built in 0.1 ms
   (Node). Two gaps were found in the app as it is: opening a project does not move the counter, and the project's
   display units are saved nowhere.
6. **A text field is `{{key}}`,** with an optional precision (`{{gfa|1}}`), looked up in a fixed table and never
   evaluated, inserted from a menu; an unknown key stays as typed and is marked. Numbers keep the app's own units
   (m², m³): `Intl.NumberFormat` has no square or cubic metre.

Sixteen decisions for the owner close the note (part 11).

## 2. The question and the hypotheses

**The question** is above. A good answer must decide what kinds of object can be live; when each is brought up to date;
how an out-of-date or missing source is shown; what an override is and how Reset works; the syntax of a field in text;
how numbers are formatted; and what is saved.

The hypotheses were written before the searches. Each is followed by its outcome.

| # | Hypothesis | Outcome | Evidence |
|---|---|---|---|
| H1 | Archicad and LayOut bring a linked drawing up to date automatically, by default, without a command | **Partly fails.** Archicad's Auto drawings update "when the layout is activated" and Manual ones stay frozen until Update; LayOut's references update on demand, with an option to check at open. Only document text is always live | practice-bim 3.1, 3.2 (P) |
| H2 | Their text fields update by themselves and cannot be edited in place without breaking the link | **Holds for the first half** (Archicad's autotext is "automatically updated to follow any changes", P); the second half is U for Archicad, and holds for AutoCAD (Convert Field to Text, one way) and Vectorworks (Not Link) | practice-bim 3.1, 3.4, 3.5 |
| H3 | LayOut's override is per property, not the whole viewport, and Reset brings back only the overridden ones | **Holds, at group grain:** camera, style, effects, tags, each tag's dashes and visibility, each with Reset, plus Reset All | practice-bim 3.2 (P) |
| H4 | Every surveyed tool marks a stale linked item visibly | **Fails.** Always-live tools have nothing to mark (ArcGIS, QGIS labels, Revit, Rhino); Word shows its last result unmarked. Tools with triggered updates do mark it, on screen only | practice-design-gis 4; practice-bim 4 |
| H5 | Figma and Penpot keep overrides per property (Penpot per attribute group); Reset per property and for all | **Holds,** with one nuance: Penpot's interface resets all groups at once | practice-design-gis 3.3, 3.4 (P, code) |
| H6 | `A3D_REV` catches every change a live object depends on | **Mostly holds.** 243 functions call `saveSoon`; all 29 `pushUndo` callers reach it. Two gaps: opening a project (`bimLoadProjectRecord`) does not move it; inputs outside the project record (the date, tiles loaded, images arriving, appearance, plot) need their own part in the key | invalidation 3, E1, E3 (P) |
| H7 | Drawing every live object from its source on every draw costs under 16 ms for 80 objects, 20 live | **Holds for markup** (0.1 ms, Node); **fails without a memo** when 20 objects share a 3 ms source (60 ms); holds with one compute per source per revision (3 ms) | invalidation E2, E2b (measured) |
| H8 | Analyses are too slow to rerun on change, so a live object bound to one shows its kept value and says when it is out of date | **Holds.** Ladybug studies run for minutes (`BIM_LB_STUDY_MS` 600000); CUTFILL is a command; V172c already keeps "out of date and why" | app-code-audit 2 (P) |
| H9 | A field syntax exists that is easy to type on a phone, needs no escaping in prose and is never evaluated | **Partly holds.** Mustache's `{{key}}` is never evaluated and seldom collides with prose; QGIS and Rhino evaluate; ArcGIS's XML is hard to type; phone typing of braces is not tested here (U) | invalidation 7 |
| H10 | Storing the binding and the overrides, never the resolved value, adds under 2 KB to an undo snapshot for 20 live objects | **Holds:** +1,380 bytes (69 B each). A stored resolved value would add 78 B each, 78 KB over 50 steps: size is not the reason to keep it out, correctness is (part 4.5) | invalidation E4 (measured) |

Two more were proposed by agent 2 during the search, and both held: an override survives a source update and only the
overridden part stops following (wherever tools have overrides); every tool with links also offers a one-way freeze.

## 3. Method

- **Sources by kind.** About 35 vendor pages read as text (Graphisoft for Archicad 22 to 27, help.sketchup.com,
  Autodesk for Revit 2016 to 2023 and AutoCAD 2025 and 2026, Vectorworks 2024 to 2026, Rhino 8); ArcGIS Pro 3.4 and
  QGIS 3.44 help; Figma's help centre and plugin typings; Microsoft's Word field pages; code read as text: Penpot
  (`component.cljc`, `logic/libraries.cljc`, `container.cljc`, MPL-2.0), QGIS (`qgslayoutitemlegend.cpp`,
  `qgslayoutitemlabel.cpp`, `qgsexpression.cpp`, GPL: the method only), Preact signals, MobX; the paper Mokhov,
  Mitchell and Peyton Jones (2018), "Build systems a la carte"; ECMA-402 and MDN's browser-compat-data; seven SketchUp
  forum threads read in full as practice (S); the app's code at e1e3a31.
- **Search logs:** practice-bim part 2 (30 searches), practice-design-gis part 2 (42), invalidation part 2.
- **Refused hosts** (status): community.graphisoft.com and helpcenter.graphisoft.com 403; forums.autodesk.com 403;
  forum.vectorworks.net 403; helpx.adobe.com 403 (three pages); canva.com/help 403; ArcGIS Pro's "latest" help moved
  and gave 404 (3.4 read instead). forums.sketchup.com refuses its HTML pages but answers `/t/<id>.json` (200): worth
  reusing.
- **Experiments:** `docs/research/experiments/v175-invalidation/` (E1 to E4, part 6), Node only.
- **The independent check:** part 3a.

### 3a. The independent check

Research agent 4 re-read 63 facts at their sources (`independent-check.md`, with pinned commits: Penpot `904cdd97`,
QGIS `91d4a333`, ecma402 `3691634`, browser-compat-data `82daeeb`, Preact signals `30a797e`, MobX `2a97ff6`,
snowleopard/build `43b18b9`): **61 confirmed** (4 of them from forum posts only, S), **2 not confirmed**, none
unreachable. Both failures are corrected here, and neither is a fact the code uses:
- AutoCAD's stored field code closes with `%>%`: `%<\AcVar Date \f "M/d/yyyy"%>%` (Autodesk's ActiveX and LISP examples).
- ArcGIS's help does not say dynamic text is "evaluated when drawn"; it says "Dynamic elements update in response to
  changes in the data or the map extent". The practical reading (always live) stands; the wording is the vendor's.

Smaller corrections taken: LayOut's per-section Resets (Camera, Style, Effects) are confirmed from the forum only (S);
its help names Reset All, the Tags Reset and the per-tag resets (P). Penpot's comment that geometry "never triggers
touched" is contradicted by its code, which marks geometry on a copy's edit unless told not to; the code is the rule
read here, and "geometry is layout" stays our own choice. Word's Ctrl+Shift+F9 moves from U to P. The benchmark,
re-run, agreed within 25 per cent on 22 of 23 timings (the revision compare: 0.34 ms against 0.62 ms). Canva's
help page answered 200 on the re-check; its facts were not re-read and stay U.

## 4. Findings, by topic

### 4.1 What is live today (app-code-audit, P, high)

| Item of the row | Today |
|---|---|
| Model views | Live: a V174d map frame, its picture cached on `A3D_REV` (`board-map.js:62-78`); a deleted level shows "Level no longer exists" |
| Schedules | Live on sheets (`sheets.js:142-146`), filtered out of boards' map frames (`board-map.js:36`) |
| Legends | Live, not editable (`board-map.js:102-114`) |
| The boards' charts and KPI cards | Live as whole figures (`board-figures.js:20-110`); a single card cannot be placed; nothing overridable |
| A result layer's chart | Not on boards (`results-layers.js`) |
| Sun hours, solar | Kept as result layers or Ladybug studies, "out of date and why" (`results-layers.js:46-56`, `ladybug/studies.js:61-71`) |
| Cut and fill | Kept on the proposed surface by CUTFILL (`grading.js:312-336`), not rerun |
| GBA, site area | Computed on demand: `bimLevelAreas(id).gross` (`schedules.js:177`), `bimZnCalc().lot / .achievable` (`zoning-envelope.js:251-322`) |
| Text bound to project data | The title block only (`board-design.js:153-162`); text objects are plain |
| Overrides | None; the nearest is ByLayer (`board-objects.js:56-57`) |

"The V157 dashboard" names no phase in the repository: V157 is Site context C2 (roads, rail, trees). The nearest
are V159's climate board, built on ArcGIS Dashboards' indicator practice, and V162's boards as pages. The Notion task
says the same words. Read here as the boards' figures and KPI cards; asked as D13.

### 4.2 When a live element is brought up to date (practice-bim 3, 4; practice-design-gis 3, 4)

| Model | Tools | Fits here |
|---|---|---|
| Always live, drawn from the source | Revit's views, schedules and labels ("Revit updates all sheets", P); Archicad autotext (P); ArcGIS dynamic text, which "update[s] in response to changes in the data or the map extent" (P); QGIS labels (P); Rhino fields (P); Vectorworks wireframe viewports and linked text (P) | Numbers, text, schedules, legends, views: all are cheap here (E2) |
| On a trigger, with a stale mark | Archicad Auto (when the layout is activated) and Manual (frozen until Update); LayOut references (Update, or check at open); Vectorworks rendered viewports (Update); AutoCAD FIELDEVAL (open 1, save 2, plot 4, eTransmit 8, regen 16, default 31) | Analyses: Ladybug studies, sun hours, solar, cut and fill |

Confidence high: the two models are documented by the vendors themselves, and agree across tools.

**The stale mark** is on screen and is not printed: AutoCAD's grey field background is "not plotted" (P); LayOut's red
label (S); Vectorworks's red Update button and an optional striped border, with a prompt at print time (P). Archicad's
Drawing Manager lists statuses: OK, Modified (the source changed), Missing, Embedded, Needs Checking (P). LayOut's own
"Modified" means the opposite: changed on the page, away from the source. The two states need two names here.

### 4.3 The override (practice-bim 3.2, 3.3; practice-design-gis 3.3 to 3.6, 5)

- **LayOut** (P for Reset All and the tags' resets; S, forum, for the Camera, Style and Effects resets): per group of a viewport's settings, each group with its own Reset, and Reset All; tag overrides can
  be pushed back to the model; overrides are kept when the model reference updates (S) and copied with the viewport.
- **Figma** (P): per property of an instance; an overridden property no longer follows the main component while the
  rest do; reset one property, or Reset all changes.
- **Penpot** (P, code): per attribute group, a `:touched` set; a group is marked only when the value changes, only on a
  copy, and not while syncing; the interface resets all groups.
- **InDesign** (P, scripting reference): five "preserve" groups chosen per link.
- **Revit** (P): no override; editing a label on the sheet writes the parameter, everywhere.
- **Whole-element freezes** (P): QGIS's legend with Auto update off, ArcGIS's Convert to graphics, Word's Ctrl+F11
  lock and Ctrl+Shift+F9 unlink.

The models compared against criteria stated first (no silent loss of a board edit; everything else keeps following;
Reset of one and of all; small to save; clear on a phone; ES5) are in practice-design-gis part 5. Per property wins on
every criterion but the smallest store, where Penpot's groups win. Confidence high.

### 4.4 Counter-evidence that changes the design (practice-bim 5; practice-design-gis 6)

1. **Overrides nobody sees** (S, four LayOut threads): viewports that "won't update" because the camera was overridden
   unnoticed; the panel's dark grey section is too subtle. The mark goes on the object itself, in edit mode.
2. **A lost link re-attached to a guess** (S, LayOut 2023 thread 243365): labels joined to the nearest component after
   an update. A lost source is marked missing; nothing is ever rebound by guess.
3. **A refresh that discards edits** (P): LayOut's Update Table Reference "override[s] any local changes".
4. **Stale at publish** (U, refused forums): Archicad Auto drawings and AutoCAD fields stale after PUBLISH when the
   plot bit was off. Event-driven freshness fails when the events are configured off; drawn-from-source is safer.
5. **Bindings by name break** (U, Figma forum): renamed layers lose their tracking; deleted variables leave stale
   bindings. Bind by stable id.

### 4.5 What is saved (invalidation 6; practice-design-gis 5)

- `bind`: what it shows (kind, source key, its id, field, format), never the value.
- `ov`: the properties set by hand, with their values. Absent means everything follows the source.
- `ovAt`: for overridden keys only, the source's value when the override was made. When it differs from the source's
  value now, the Properties row says "the source has changed since this was set", with Reset and Keep. This is a
  three-way compare; Figma's help says nothing of a warning when the main component changes (S).
- **Not saved:** the resolved value. It lives in a runtime memo beside `A3D_BMAP` and `A3D_BRD`. Agents 2 and 3
  disagreed here: agent 2 recommended storing the last value so a missing source shows it (Word, InDesign, AutoCAD's
  sheet set fields keep theirs); agent 3 showed that writing it at draw time is either a mutation that moves the
  revision again (a loop that also marks the file changed) or a silent write the save path does not know of, and that a
  cached value restored by undo can disagree with the model restored with it. Size is not the reason (E4). The choice
  is D7, with agent 3's reading recommended: a missing source says what it was bound to ("Source removed: Level 2"),
  and the binding is kept, so undo brings both back.

### 4.6 Fields in text (practice-bim 3; invalidation 7)

| Tool | Form | Evaluates? |
|---|---|---|
| Archicad | `<PROJECTNAME>`, `<LAYOUTNUMBER>`, `<DRAWINGSCALE>`, `<SITEGROSSAREA>`, from a picker; its keys changed between AC22 and AC27 | No |
| LayOut | `<PageNumber>`, `<SceneName>`, `<Ratio( to )>`, any component attribute; Sequence tags | No |
| AutoCAD | `%<\AcVar Date \f "M/d/yyyy"%>%`, written by a dialog | Some fields are formulas |
| Rhino 8 | `%<Area("id","Unit")>%`, with arithmetic and Python | Yes |
| QGIS | `[% expression %]` | Yes |
| ArcGIS Pro | `<dyn type="..." property="..." decimalPlaces="..."/>` | No |
| Mustache | `{{key}}`; unknown key gives "" | No; no re-interpolation |

Recommended: `{{key}}` and `{{key|dp}}` (H9), looked up by `hasOwnProperty` in a fixed table (no `eval`, no
`Function`), the result never re-scanned; an unknown key stays as typed and is marked in edit mode (an empty result
hides a typing error on a printed board); inserted from a menu (Insert field), as Archicad, LayOut, ArcGIS and AutoCAD
all offer; no escape syntax (Convert to static covers the rare literal). Angle brackets are set aside: they collide with
"< 5 m" in prose and with the board's own HTML. Keys are versioned by keeping old names as aliases (Archicad's key set
changed between versions). Confidence medium: the syntax is a product choice, and phone typing is U.

**Numbers** use the app's `bimDispNum` and `bimDispLen` (`palette.js:59-71`) and its unit labels. `Intl.NumberFormat`
can group digits (one formatter per format: a new one per value is 30 times slower, E2), but `style:'unit'` needs
Chrome 77 and Safari 14.1, and ECMA-402 sanctions no square or cubic metre (`RangeError`, measured).

## 5. The alternatives compared

### 5.1 When to redraw (invalidation 4)

Criteria first: (1) a stale value is never drawn, on screen, in Present or in print; (2) cost per edit; (3) cost per
draw; (4) ES5 code size; (5) risk of a missed signal; (6) fit to the app's plain JSON state, replaced on undo.

| | (a) Recompute on every draw | (b) The revision counter, plus a memo per source | (c) Fingerprints of each source's inputs | (d) Dependency tracking, signals |
|---|---|---|---|---|
| 1 | Always right | Right once its two gaps are closed and volatile inputs join the key | Right if the fingerprint covers every input | Right if every read is tracked |
| 2 | 0 | One increment, already paid | 0 | Dirty marks |
| 3 | 60 ms for 20 elements on a 3 ms source | 0.6 ns per compare, 3 ms per source per revision | 0.5 to 2.5 ms of hashing per source | Near 0 |
| 4 | Smallest | About 30 lines | A fingerprint per source kind, kept in step | Large: MobX needs `Proxy` |
| 5 | None | The two load paths (found) | A forgotten field | Any of the 139 functions writing `A3D` directly |
| 6 | Fits | **What the app does since V122** | Nothing in the app uses it | Poor: undo and load replace the state, losing subscriptions |

**Recommended: (b).** Prior art agrees: Preact signals puts a global version in front of per-source versions; Excel is
dirty bits plus restarting (Mokhov et al., P); AutoCAD evaluates fields at events. What would change it: a source that
costs tens of milliseconds and changes rarely would justify a fingerprint for that one source.

### 5.2 The override (practice-design-gis 5)

| Model | Seen in | Keeps following the rest | Reset one / all | Store | On a phone |
|---|---|---|---|---|---|
| Freeze the whole element | QGIS legend, ArcGIS convert, Word lock | No | All only | Large (a copy) | One switch |
| **Per property** | Figma; LayOut by group | Yes | Yes / yes | Key names and values | A mark per row, Reset beside it |
| Per attribute group | Penpot, InDesign | Yes, at group grain | Penpot all only | Smallest | Groups to learn |
| Binding replaced by a value | Figma variables, ArcGIS and QGIS tag text | Unedited only | Rebind, no Reset | Small | Clear |

**Recommended: per property**, with Penpot's three rules, two of our own (moving or resizing the object is layout, not
an override; a text's words and its styling are separate keys, so making a live number bold does not freeze it), and a
separate one-way Unlink. What would change it: row-by-row edits of a legend or schedule make the keys paths
(`rows.<id>.label`), still per property.

### 5.3 The stale analysis (practice-bim 4)

| | Rerun on change | **Kept, marked out of date, Run again in Properties** | Frozen until Update (Archicad Manual) |
|---|---|---|---|
| Truth on the board | Always current, minutes late | The kept value, marked with why | The kept value, unmarked unless checked |
| Cost | A Ladybug run per edit: not possible | None | None |
| Fits | No | V172c's pattern, already in the app | A second state to learn |

**Recommended: the middle column.**

## 6. The experiments (invalidation 5)

Node v26.13.0, AMD Ryzen 7 8845HS, Windows 11 Pro, 2026-11-08; no browser (Playwright not installed here); 5 warm-up
and 41 timed runs, medians (p95 in the working note). The app's own functions through `tests/unit/helpers/engine.mjs`.

| Measure | Median |
|---|---|
| Revision compare, 1,000,000 times | 0.623 ms |
| `JSON.stringify` of 2,000 walls (943 KB) plus FNV-1a | 2.460 ms |
| A narrow fingerprint of the same | 0.506 ms |
| Recomputing a sum over them | 0.044 ms |
| `bimLevelAreas`, 40 / 200 / 400 edges | 0.204 / 0.944 / 3.002 ms; beyond 400, `gross:null` with a note |
| 200 numbers through `bimDispNum` | 0.022 ms |
| `Intl.NumberFormat`, 200 values, reused / new each | 0.074 / 2.483 ms |
| A board of 80 objects, markup (`bimBdsHtml`, 23.5 KB) | 0.077 ms |
| Resolving 20 live values from one source | 0.040 ms |
| Undo snapshot, 20 bindings added | +1,380 bytes |
| ... plus stored resolved values | +1,560 bytes more |

E3: `saveSoon` and `bimSetUnits` move the revision; `pushUndo` alone, `paint` and an empty undo do not. E1: 243 of the
app's 4,079 named functions call `saveSoon`; the 17 that write `A3D` and reach it by no name are helpers (lazy getters,
ensure functions).

What they show: formatting and markup are negligible; the cost that matters is one source computed many times, which the
memo removes. Not measured: the browser's parse and layout of the board's HTML, a phone, Safari and Firefox.

## 7. Edges (invalidation 8)

| Case | With this design |
|---|---|
| Source deleted | "Source removed: Level 2" in edit mode, an em dash on paper; the binding kept, so undo brings both back; never rebound by guess |
| Not computed yet (an analysis never run) | "Not computed: run Sun hours" in edit, an em dash on paper; never computed on draw |
| Over a source's limit | `bimLevelAreas` beyond 400 edges gives its note, never 0 |
| Circular binding | Not possible: bindings resolve only against model sources, never another board object; a re-entry flag turns a future mistake into a warning |
| Present mode | The slideshow's key is the board and `A3D_REV`; a date field across midnight needs the day in the key |
| Print and `sheetCapture` | Resolvers take explicit ids, never the active level: `bimRenderSourceToCanvas` swaps the active level, camera and section while it draws a viewport |
| Units change | Moves the revision; the key carries the units |
| Units across reload | Lost today: `A3D_UNITS` is in neither the project record nor the snapshot, and the comment at `palette.js:49` names functions that do not exist (D10) |
| Undo of a model edit | Undo then `saveSoon`: the value follows; bindings and overrides undo with the board (`A3D.pres` is in the snapshot) |
| Opening a project, the read-only tab's refresh | The revision does not move today (`project-tabs.js:185`): pages and boards can stay stale now, before V175. A one-line fix (D11) |
| An old project | No `bind`: every object stays as it is; nothing to migrate |
| An older build opening a V175 project | `bimBobOne` drops `bind`, `ov`, `ovAt`: it shows the text as typed (D9) |
| Orbit, zoom, rotate | Each frame moves the revision (they save the camera); the memo bounds the cost to one compute per source per frame |

## 8. What the app already has

`app-code-audit.md`, by file and line: the counter and its five users (part 1), each item of the row (part 2), and the
constraints (part 3): `bimBobOne`'s whitelist, undo's whole-state snapshots, `A3D_PLOT.on`, `bimDispNum`, the one layer
system and the Properties panel (`board-design-props.js:61-127`), and the files already over 400 lines.

## 9. Risks and threats to validity

- **Node only.** The browser's DOM cost, a phone and Safari's and Firefox's behaviour are not measured.
- **Forum evidence.** The counter-evidence that changes the design rests on SketchUp forum threads (S), and the
  Archicad and AutoCAD complaints on refused forums (U); none of it is used as a number in the code.
- **Versions.** Archicad's drawing pages were read in AC24 and AC25 copies, its autotext in AC27; LayOut's override
  groups from its 2026 help.
- **The load-path gap** is from reading the code; the load path runs out of memory in the Node stand-in.
- **17 writers** of `A3D` were judged helpers by reading, not traced to every caller (medium).
- **Refused hosts:** Adobe and Canva (part 3), so InDesign's and Canva's details stay U.

## 10. What is still open (U)

- Archicad: whether autotext can be overridden; its placeholder text; whether a deleted view shows as Missing; the
  "Linked properties" of drawing titles.
- LayOut: the literal "(Modified)" label; what auto-text shows when its entity is gone.
- Revit: the "?" in a title block for a missing parameter.
- AutoCAD: "----" against "####" (its pages disagree); Convert Field to Text in core AutoCAD.
- ArcGIS: what a tag shows after its map frame is deleted. Figma: the deleted-variable state. Penpot: a per-group Reset.
- InDesign's Links icons and text variables; PowerPoint's Update Links bar; Canva's chart refresh (hosts refused).
- Typing `{` and `}` on a phone's keyboard (not tested here).
None of these is a fact the code will use.

## 11. The owner's decisions

Asked together, each with the evidence and a recommendation.

| # | Question | Evidence | Recommended |
|---|---|---|---|
| D1 | What is new in V175: text fields, single numbers, schedules, single KPI cards and result charts as board objects (model views, legends and figures are live already)? | 4.1 | **Yes, all five** |
| D2 | Cheap sources (numbers, text, schedules, views, legends) always drawn from the model, with no Manual or frozen mode? | 4.2, 5.1 | **Yes** |
| D3 | Analyses (sun hours, solar, Ladybug, cut and fill) never rerun by a board: the kept value, marked out of date with why, and Run again in Properties? | H8, 5.3 | **Yes** |
| D4 | The marks (out of date, source removed, overridden) on screen and in edit mode, not printed; Print lists what is out of date in a message before it prints? | 4.2, 4.4 | **Yes** |
| D5 | The override per property (`ov`), with Reset per property and Reset all; moving and resizing are layout, not overrides; a text's words and its style separate keys? | 4.3, 5.2 | **Yes** |
| D6 | Unlink, one way: the object keeps what it shows and is no longer live (separate from Reset)? | H-n2-2 | **Yes** |
| D7 | Keep the source's value at the time of an override (`ovAt`), so a row can say "the source has changed since this was set", with Reset and Keep? | 4.5 | **Yes** |
| D8 | The resolved value never saved: a removed source says what it was bound to, rather than showing its last value? | 4.5 | **Yes** |
| D9 | What an older build shows for a field: the text as typed with its `{{key}}` (honest), or the last value written at save? | 4.5, part 7 | **The text as typed** |
| D10 | The project's display units made a saved project field (today they return to metres on reload), rather than each number carrying its own unit? | part 7 | **A project field** |
| D11 | Opening a project moves the revision (a fix the app needs before V175: read-only tabs can show stale pages today)? | H6 | **Yes** |
| D12 | Camera moves stop moving the revision (they are view state)? A wider change, beyond V175 | part 7 | **Not in V175**; recorded |
| D13 | "The V157 dashboard" read as the boards' figures and their KPI cards (V159, V162)? | 4.1 | **Yes** |
| D14 | Fields as `{{key}}` and `{{key|dp}}`, from a fixed list, never evaluated, from an Insert field menu; an unknown key left as typed and marked; old key names kept as aliases? | 4.6 | **Yes** |
| D15 | The overridden mark on the object itself (a corner tick in edit mode), not only in the Properties panel? | 4.4 (1) | **Yes** |
| D16 | The build in two parts: V175a (fields, numbers, overrides, Reset, Unlink, the two fixes), V175b (schedules, single KPI cards, result charts as board objects), one PR each? | this note | **Yes** |

## 12. References

Every source, with its URL, what was read, the date and its level, is in the working notes: `practice-bim.md` part 7
(37 references), `practice-design-gis.md` part 8, `invalidation.md` part 10, and the app's code in `app-code-audit.md`.
The sources the design rests on most:

| Source | Read | Level |
|---|---|---|
| Graphisoft Archicad help (AC24, AC25, AC27): Drawing Manager, Update Type, Autotext | statuses, Auto and Manual, autotext keys | P |
| SketchUp LayOut help (2026): viewport overrides, References, Auto-Text, tables | override groups and Reset, Update Reference, tags, the table warning | P |
| Autodesk AutoCAD 2025 and 2026 help: FIELD, FIELDEVAL, FIELDDISPLAY, data links | the bit values, the grey background, "----" and "####" | P |
| Autodesk Revit help: sheets, labels, schedules | "Revit updates all sheets" | P |
| Vectorworks 2024 to 2026 help: viewports, linked text, worksheets | Update, the striped border, the print prompt | P |
| McNeel Rhino 8 help: text fields | `%<...>%`, "####" | P |
| ArcGIS Pro 3.4 help: dynamic text, table and chart frames, legends | the tags, their attributes, `emptyStr` | P |
| QGIS 3.44 manual and source (GPL, method only) | `[% %]`, the legend's Auto update, Refresh | P |
| Figma help centre and plugin typings | instance overrides, reset, variables | P |
| Penpot source (MPL-2.0), `component.cljc`, `logic/libraries.cljc` | `:touched`, sync rules, reset | P |
| Microsoft Word fields, DOCPROPERTY | lock, unlink, update | P |
| SketchUp forum threads 146169, 160597, 225138, 243365, 255744, 275627 | overrides unnoticed; the 2023 rebinding | S |
| Mokhov, Mitchell, Peyton Jones (2018), Build systems a la carte, ICFP | Excel as dirty bit and restarting | P |
| Preact signals source; MobX 7 | the global version; `Proxy` | P |
| ECMA-402; MDN browser-compat-data | sanctioned units; `Intl.NumberFormat` support | P |
| The app at e1e3a31 | `app-code-audit.md`, `invalidation.md` part 3 | P |
