# V175 research, agent 3: when a live element is drawn again (invalidation)

Working note for V175, "Presentation P2: live elements". Written 2026-11-08 by research agent 3, from the app's code
at `v175-research` (e1e3a31), sources read as text, and experiments run here. Evidence levels are those of
`docs/research/research-protocol.md`: P primary, S secondary, U unverified. The note is not yet re-read by an
independent second reader (protocol step 9); that check is still owed.

**Short answer.** The app already has a global revision counter: `A3D_REV`, moved by `saveSoon`
(`src/js/engine/bim/region-regenerate.js:104`). Boards, map frames, pages, thumbnails and the slideshow already
keep the revision they drew at. Live elements should use the same counter, with three additions:
- a composite key for inputs that change without a save: the day for a date token, tiles loaded, the
  appearance and plot state, the project units;
- a memo per source and revision, so 20 elements bound to one number compute it once;
- an explicit bump in the two load paths that do not save.

Per-source fingerprints and reactive signals cost more code, and on this app's plain-JSON state they buy little
or nothing: re-hashing the inputs costs about as much as recomputing the value. The measured numbers are in part 5.

## 1. The question and the hypotheses

**Question.** When the model changes, how does a live board element (a number, a token, a schedule, a legend, a
chart, a view, an analysis result) know it must be drawn again? It must never show a stale value, and must not
make drawing or editing slower than a person can see.

A good answer has to decide four things: where the change signal comes from; what each element keeps; what goes
into the project record (and so into 50 undo copies); and which inputs need a key of their own.

| # | Hypothesis (falsifiable) | Outcome |
|---|---|---|
| H1 | A global revision counter bumped at the undo push (`pushUndo`) catches every model change | **Failed.** `pushUndo` runs before the change, not after it (`plan-mode-sketch.js:297-302`, called before the mutation in, for example, `objects-save.js:15` and `:33`). A drag takes one undo step and then mutates on every frame (`gizmo-handles.js:931-932` takes the step; `:710-721` mutates and saves per frame). Fetched data, camera moves and title-block edits save without an undo step (`map/data-layers.js:115-120`, `presentation-panel.js:711`, `ui/build-ui.js:906-916`). Ladybug analyses and studies do take one, but inside their promise after the run, not at the request (`ladybug/analyses.js:55`, `ladybug/studies.js:134`). Measured: `pushUndo()` alone does not move `A3D_REV` (part 5, E3). |
| H2 | A counter bumped in `saveSoon` catches every change a live element can show | **Mostly held, with named gaps.** 243 functions call `saveSoon` directly (scan, E1); undo and redo call it after the restore (`plan-mode-sketch.js:338-349`); units call it (`palette.js:105`, measured, E3). Gaps: (a) `bimLoadProjectRecord` does not call it (`ui/project-tabs.js:185-198`), and two callers add only `paint()`: the read-only tab's refresh (`core/tab-lock.js:138`) and the load from the browser's database (`core/project-store.js:156`); `paint()` measured not to move the counter; (b) inputs that are not the record: the date, tiles arriving, images arriving from IndexedDB, the appearance, plot state. |
| H3 | Fingerprinting a source's inputs (FNV-1a over JSON) is much cheaper than recomputing the value | **Failed for the cheap sources.** For 2,000 walls: `JSON.stringify` plus FNV-1a takes 2.46 ms (median); a narrow fingerprint of only the fields a gross area uses takes 0.51 ms. Recomputing a sum over the same walls takes 0.04 ms, and the app's `bimLevelAreas` takes 0.14 to 3.0 ms (E2). It held only for expensive sources (a viewport render, a Ladybug run), which the revision already guards. |
| H4 | Storing the resolved value in the board object bloats the undo snapshots enough to matter | **Failed on size; held on correctness.** 20 cached values add 1,560 bytes per snapshot (78 KB over 50 undo steps), which is 0.16 % of a snapshot of a 2,000-wall model (E4). They should still stay out of the record, for correctness reasons (part 6). |
| H5 | No circular binding is possible if bindings resolve only against the model, never against board objects | **Held, by reading.** No registered schedule reads `A3D.pres` or board objects (`structure/analysis-properties.js:233-251`, 18 schedules, all built from `A3D.objs` and analysis results). A chain (one live element bound to another) is the only way to make a cycle, and the design forbids it (part 8). |

## 2. Search log

| # | Where | Query or path | What came back | Kept / set aside |
|---|---|---|---|---|
| 1 | App code (grep) | `pushUndo`, `undoSuspend`, `saveSoon`, `A3D_REV`, `bimPageSig`, `sheetCapture`, `A3D_UNITS`, `titleBlock` | The undo, save and revision paths, with file:line in part 3 | Kept (P) |
| 2 | App code (script E1) | Every named function under `src/js/engine`: does it call `pushUndo`, `saveSoon`, or write a project field? | 219 files, 4,079 functions; 29 call `pushUndo` without `saveSoon` in their own body; 33 write a project field with neither | Kept as pointers. All 29 reach `saveSoon` through a callee by name; 17 writers do not. These are helpers (ensure, lazy getters) whose callers save, so they are not proven faults. |
| 3 | Engineering log | `canvas_v10_STATUS.md`, "A3D_REV", "revision" | Lines 9921 and 10013: V122 introduced `A3D_REV`; "a view switch calls `saveSoon`", so pages redraw identically, "a cost, not a wrong page" | Kept (P, the project's own record) |
| 4 | GitHub, preactjs/signals @30a797e (MIT) | `packages/core/src/index.ts` | A global version (`globalVersion`, line 161) as a fast path in front of per-source versions (`needsToRecompute`, 504-530); a `RUNNING` flag throws "Cycle detected" (464, 754) | Kept: the method (P) |
| 5 | GitHub, mobxjs/mobx @2a97ff6 (MIT) | `packages/mobx/src/core/computedvalue.ts`, `docs/computeds.md`, `docs/configuration.md`, `src/errors.ts` | Computeds are cached only while observed (or `keepAlive`); a cycle throws error 32; MobX needs `Proxy` ("MobX 7 does not include the older ES5 fallback") | Kept (P) |
| 6 | GitHub, solidjs/solid @bc50fe5 (MIT) | Repository and licence only | Same family as 4; its code was not read | Set aside: Preact's code covers the method |
| 7 | GitHub, MicrosoftDocs/office-developer-client-docs @eedbd61 | `docs/excel/excel-recalculation.md` | Dependency tree, calculation chain, dirty cells, transitive dirtying, circular-reference warning, volatile functions recalculated every time | Kept (P, the vendor's document) |
| 8 | microsoft.com research | Mokhov, Mitchell, Peyton Jones 2018, the PDF (text by `pdftotext`) | Definition 2.1 (minimality); the dirty bit (4.2.1), verifying traces (4.2.2), constructive traces (4.2.3); Excel modelled as restarting plus dirty bit; volatility as depending on a "RealWorld" key | Kept (P) |
| 9 | cambridge.org | The JFP 2020 extended version | Title block and abstract only; the full text is behind a login | Set aside: the 2018 paper was read instead |
| 10 | GitHub, snowleopard/build @43b18b9 (MIT) | `src/Build/System.hs` | `excel = restarting dirtyBitRebuilder`, `shake = suspending vtRebuilder`, `bazel = restarting2 ctRebuilder` | Kept (P, the paper's executable model) |
| 11 | GitHub, mdn/browser-compat-data @82daeeb (CC0) | `javascript/builtins/Intl/NumberFormat.json` | The constructor: Chrome 24, Firefox 29, Safari 10, IE 11, Edge 12; `maximumFractionDigits`: the same versions; `style:'unit'`: Chrome 77, Firefox 78, Safari 14.1; `formatToParts`: Chrome 64, Safari 13 | Kept (P) |
| 12 | GitHub, tc39/ecma402 @3691634 | `spec/locales-currencies-tz.html`, the sanctioned units | 45 units. Lengths and `acre` / `hectare` are in; no `square-meter` and no `cubic-meter`. Node gives `RangeError` for `square-meter` (run here) | Kept (P) |
| 13 | GitHub, mustache/spec @e8ec001 (MIT) | `specs/interpolation.yml` | `{{name}}`, HTML-escaped; `{{{ }}}` and `&` unescaped; a context miss gives "" (empty); "No Re-interpolation" | Kept (P) |
| 14 | GitHub, qgis/QGIS-Documentation @83f9bab | `docs/user_manual/print_layout/layout_items/layout_label.rst` | Dynamic parts in `[% %]`, which are expressions; "Convert to Static" | Kept (P); its licence was not read (the API gives none), and none of its text is used |
| 15 | help.autodesk.com (2022, AutoCAD LT) | FIELDEVAL | Bits 1 open, 2 save, 4 plot, 8 eTransmit, 16 regeneration; default 31; saved in the drawing; the Date field updates only by UPDATEFIELD | Kept (P). The first URL tried (2025) gave 404. |
| 16 | docs.mcneel.com, Rhino 8 | `information/text_fields.htm` | `%<...>%`; functions take object IDs; arithmetic and Python formatting are allowed; an unevaluable field shows "####" | Kept (P, as the fetch tool's digest: S) |
| 17 | doc.esri.com, ArcGIS Pro (latest) | `add-and-modify-dynamic-text.html` (via a 301 from pro.arcgis.com) | `<dyn type="..." property="..."/>`; `decimalPlaces`, `preStr`, `postStr`, `emptyStr`; a renamed map frame keeps its reference but its name in the tag does not update | Kept (S, the digest) |
| 18 | help.sketchup.com, LayOut | `layout/automate-titleblocks` | `<PageNumber>` typed or picked from Text > Insert Auto-Text; Current Date "updates on a daily basis"; Date Published shows "Unpublished" until exported | Kept (S, the digest). The page's last 56 k characters were not read. |
| 19 | help.figma.com | `Apply-changes-to-instances` | Reset one property or all changes; nothing on a warning when the main component changes | Kept as weak prior art (S) |
| 20 | Web search (4 queries: FIELDEVAL, Rhino fields, ArcGIS dyn, LayOut) | | Summaries pointing to 15 to 18 | Pointers only (U); every fact used was read at 15 to 18 |

**Hosts refused or not reached:** cambridge.org (full text behind a login); help.autodesk.com (the 2025 GUID gave
404, and the 2022 page was used). Playwright is not available here: there is no `/opt/pw-browsers`, the Python
package is absent, and `npx playwright` would need a download. Every experiment is Node only.

## 3. The app's change paths (all P, read in the code at e1e3a31)

| Path | Where | What it does |
|---|---|---|
| Undo push | `src/js/engine/drawing/plan-mode-sketch.js:291-302` | `UNDO_MAX=50`; `bimSnapshotState()` is one `JSON.stringify` of 20 fields (objs, levels, grids, layers, counts, views, types, sheets, titleBlock, buildings, site, classifications, resultLayers, pres, ...). Skipped while `undoSuspend` or `bimUndoHold`. **It runs before the mutation.** |
| Undo restore | `plan-mode-sketch.js:303-337`, `doUndo` / `doRedo` 338-349 | The restore replaces `A3D.objs` and the other fields with new parsed objects, so object identity is never kept. It calls `refresh*`, `paint`, `bimPresPanelRefresh`, `bimBrdRestored`; then `doUndo` calls `saveSoon`. |
| Not in the snapshot | `plan-mode-sketch.js:293` against `core/objects-save.js:53` | `cam`, `seq`, `dataFeatures`, `history` and `activeViewId` are in the project record but not in the undo snapshot. `A3D_UNITS` (`properties/palette.js:53`) is in neither (see part 8). |
| **The save, and the revision** | `bim/region-regenerate.js:96-110` | `saveSoon`: adopts layers, sweeps orphan tags and footing hosts, regenerates regions, **`setA3D_REV(A3D_REV+1)` (104)**, `bimFileTouch`, `bimPagesStale` (a 250 ms debounce, `sheets/pages-display.js:256-263`), then a 300 ms timer to `save3d`. The source comment at 98-99 says "every model mutation passes through here". |
| The counter | `core/objects-save.js:45-48`, setter 82 | `var A3D_REV=0`. Kept in memory only, never saved, and starts at 0 on every load. |
| Who keys on it today | `sheets/pages-display.js:94-96` (`bimPageSig`); `sheets/present.js:165` (slideshow board); `sheets/presentation-panel.js:152` (board thumbnails); `sheets/board-map.js:66` (map frame); `sheets/board-edit.js:35` (measured board layout) | Every one is a composite key. `bimPageSig` = rev + present mode + `JSON.stringify(sheet)` + `JSON.stringify(titleBlock)` + project label. The map frame = rev + source + size + density + pan + **tiles loaded** + plot or screen + appearance. |
| Render request | `map/terrain-3d.js:338` `paint()` | It draws and does not move the revision (measured, E3). It is not a change signal. |
| The record | `core/objects-save.js:53` `bimProjectRecord`, 62-79 `save3d` | What is saved. Also `io/file-save.js:111,240,274`, which compare `A3D_REV` to know whether the file is up to date. |
| Load | `ui/project-tabs.js:185-198` `bimLoadProjectRecord` | It resets to the defaults, applies the stored state, and refreshes. **No `saveSoon` and no bump.** Callers: `ui/project-tabs.js:245` (a tab switch, followed by `bimActivateView`, which saves per STATUS:10013); `core/project-store.js:156` (+ `paint`); `core/tab-lock.js:84` and `:138` (+ `paint`, `bimDocsNotify`). |
| Over-bumping (cost, not error) | `sheets/presentation-panel.js:711` (orbit, per pointer move), `:811` (zoom); `gizmo/gizmo-handles.js:721` (rotate, per frame); view switches (STATUS:10013) | The camera is in the record, so moving it saves and moves the revision. A live element on an open board recomputes on each one. |
| Changes outside undo, or with a late undo step | `ladybug/analyses.js:55-61` and `ladybug/studies.js:130-140` (the result is written after `pushUndo` inside the promise, then `saveSoon`); `map/data-layers.js:115-120` (`dataFeatures`, saved, and not in the snapshot); `ui/build-ui.js:906-916` (project name and client: `saveSoon`, no undo); `site/sun-position.js:187-191` (sun: undo and save) | All of them move the revision. Undo does not bring back fetched data. |
| Board objects | `sheets/board-objects.js:47-110` `bimBobOne` | This validator keeps only known fields, so a new `bind` field must be added here, or it is dropped on load. An old project has no such field. |
| Title block already "live" | `sheets/board-design.js:153-162` | It reads `A3D.titleBlock`, `bimProjectLabel()` and `bimPresSeq()` at draw time; `dt` is stored once, at creation (`board-design-tools.js:108`), and is not live. |
| Capture swaps state | `sheets/sheets.js:252-297` `bimRenderSourceToCanvas` | It sets `A3D.activeLevel`, `cam`, `section`, `sel` and `sheetCapture=true` for one viewport, then restores them. A value resolved during a capture would read the captured view's state. |
| Number format | `properties/palette.js:43-71` (`BIM_UNITS` m/cm/mm; `bimDispLen`, `bimDispNum`, `bimTrimNum`); `gizmo/gizmo-handles.js:365` `bimFmtLen`; `structure/analysis-properties.js:291` `bimFmtScheduleValue` (`toFixed`) | The app's one format: the unit in the label, trailing zeros trimmed, an em dash for no value. Schedule columns are in metres whatever the project unit (their labels are fixed, "Width (m)", 233-251). |

**Is there one place a global revision can be bumped reliably?** Yes: `saveSoon`. It is already there, and 243
functions call it directly; the transitive scan (E1) finds no `pushUndo` caller that fails to reach it. It is not
perfect, for four reasons:
- the load paths above do not reach it;
- name-based reachability over-approximates: `paint` "reaches" `saveSoon` by name through conditional branches,
  yet measured it does not move the counter;
- non-record inputs never pass through it;
- it moves on camera moves.

The fix for the first is one line: `setA3D_REV(A3D_REV+1)` at the end of `bimLoadProjectRecord`, not a
`saveSoon`, so loading does not mark the file changed.

That bump is safe for the file state, read in `io/file-save.js`:
- "unsaved" is set by `bimFileTouch` (64-74), which `saveSoon` calls, and never by the counter;
- the counter is used only so that a save knows whether an edit came while it was being written
  (`bimFileMark`, 105-112, with `rev` taken at 240 and 274);
- an open marks the file with `rev=null` (368), so it is clean whatever the counter says;
- a switch changes `A3D_DOCS.active`, which `bimFileMark` checks first. Confidence: high for the paths read, medium for the load
gap. The load paths could not be run here (E3), and that finding rests on reading the code.

## 4. Strategies compared

The criteria, stated before the comparison:

1. **Correctness:** a stale value is never drawn, on screen, in Present or in print.
2. **Cost per edit:** what every model change pays, including drag frames.
3. **Cost per draw:** what a board draw pays when nothing changed.
4. **Code size in ES5,** with no dependencies.
5. **Risk of a stale display through a missed signal.**
6. **Fit:** how well it matches this app's plain JSON state (replaced wholesale on undo), its existing composite
   keys, and the one-function build.

| | (a) Recompute every live element on every board draw | (b) Global revision + per-element cache `{rev, value}` | (c) Per-source fingerprints (hash of inputs) | (d) Dependency tracking / signals (Preact, MobX, Excel's chain) |
|---|---|---|---|---|
| 1 Correctness | Always right, at draw time | Right whenever every change moves the counter; wrong for inputs outside the record unless they join the key | Right if the fingerprint covers every input; a forgotten input is silently stale | Right if every read is tracked; a read the tracking misses is silently stale |
| 2 Per edit | 0 | One integer increment (already paid today) | 0 at edit; the hash is paid at draw | Mark dirty transitively (Excel), or bump the source's version (Preact) |
| 3 Per draw, unchanged | Full recompute: 20 GFA numbers at 3.0 ms each = 60 ms (E2) | One compare per element: about 0.6 ns (E2: 1e6 compares in 0.62 ms) | A hash per source: 0.5 to 2.5 ms for 2,000 walls (E2), as much as or more than recomputing a cheap source | Close to 0 (a version compare per source) |
| 4 ES5 code | Smallest | Small: a key function and a memo map (about 30 lines) | Medium: a fingerprint function per source kind, which must be kept in step with the source's code | Large: wrapping state needs `Proxy` (MobX 7 needs it; P) or getters on every field; or explicit dependency lists per source |
| 5 Stale risk | None | A missed bump (two load paths found); a volatile input not in the key | A fingerprint that misses a field | A mutation outside the tracked API. In this app every module writes `A3D` directly (139 writer functions, E1). |
| 6 Fit | Fits, but drag-rate redraws (orbit, rotate) pay the full cost each time | **The app already does this** (5 sites in part 3) | Undo replaces the objects wholesale, so content hashes do survive it (an advantage over identity); otherwise nothing in the app uses this | Poor: the state is replaced by `JSON.parse` on undo and load, so every subscription to the old objects is lost; and it is a second state system |

**Prior art, mapped to the table.**
- Excel is (d) with a static over-approximation: dirty bits plus a calc chain, restarting (Mokhov et al. 4.2.1;
  `excel = restarting dirtyBitRebuilder`, P). It reports circular references, and recalculates volatile functions
  every time (Microsoft, P).
- Preact signals is a hybrid of (b) and (d): a global version as a fast path, then per-source versions (P).
- Shake and Ninja are (c): verifying traces, which store hashes of their dependencies (4.2.2, P).
- AutoCAD fields are (a), at chosen events: open, save, plot, eTransmit, regeneration (FIELDEVAL, default 31, P).
  It is closest to this app's need, and it says the event set is a user's choice.
- LayOut's Current Date is a volatile input with a day key: it "updates on a daily basis" (S).

**Recommendation: (b) as the app already uses it, made explicit as one key function, plus a source memo.** It
follows from the table: (b) wins criteria 2, 3, 4 and 6 and matches (a) on 1 once its two named gaps are closed.
(c) loses on 3 for exactly the cheap sources live numbers are (H3 failed). (d) loses on 4 and 6. A sketch, in ES5:

    /* one key for a live value: the model's revision, the source, and the inputs that change without a save */
    function bimLiveKey(bind){
      return A3D_REV+'|'+bind.k+'|'+(bind.src||'')+'|'+(bind.id||'')+'|'+A3D_UNITS.key+(A3D_UNITS.dp===null?'':A3D_UNITS.dp)+
        (bimLiveVolatile(bind)?'|'+bimBdsToday():'');
    }
    /* each source computed once per key, shared by every element bound to it (20 GFA = 1 compute) */
    var A3D_LIVE={memo:{}};   /* runtime only: never in the record, never in a snapshot */

- The memo is cleared when `A3D_REV` moves (one compare on read), so it holds one revision's values.
- An element's text is resolved at draw time from the memo. The board's HTML is already rebuilt only when its
  own key moves (`present.js:165`, `presentation-panel.js:152`), so no new per-element cache is needed.
- Map frames and views keep their own keys (`board-map.js:66`).

**What would change this.**
- A live source that costs tens of milliseconds and changes rarely (a schedule over a large model) would justify
  a narrow fingerprint for that one source kind: (c) applied locally, not as the whole design.
- Making camera moves stop moving the revision (they are view state) would help every keyed draw. That is a
  change beyond V175, and an owner decision.

**Counter-evidence searched.**
- Missed bumps: found two (the load paths), with one-line fixes.
- Mutation outside the choke point: 17 writer functions do not reach `saveSoon` themselves. All read as helpers
  called from saving paths. Each of the 33 was not traced to its callers, which stays a medium-confidence point.
- Over-invalidation: found (orbit, zoom, rotate, view switches). Its cost is bounded by the memo (E2: one source
  compute per revision).
- A monotonic counter never returns to an old value, so after undo it recomputes values it once had. This is a
  cost, not an error (under 3 ms per source, E2).
- Preact's own code needs a global version and per-source versions together. This confirms that a global counter
  alone over-invalidates, which is acceptable here.

Confidence in the recommendation: **high**. Threats: the experiments are Node only, not a browser or a phone; the
load-path gap is from reading, not measured.

## 5. Experiments

Scripts in `docs/research/experiments/v175-invalidation/`: `scan-change-paths.mjs` (E1, output `scan-output.txt`),
`bench.mjs` (E2 and E4, output `bench-output.json`), `bench-level-areas.mjs` (E2b, output
`bench-level-areas-output.json`), `rev-on-paths.mjs` (E3, output `rev-on-paths-output.json`), `reach.mjs` (E1, output `reach-output.txt`).

**Environment.** Node v26.13.0; AMD Ryzen 7 8845HS (16 logical cores); Windows 11 Pro 10.0.26200; 2026-11-08. No
browser: Playwright is not installed here. Each timing: 5 warm-up runs, then 41 timed runs (`process.hrtime.bigint`);
the median and p95 are given (E2b: 31 runs). The app's own functions were called through
`tests/unit/helpers/engine.mjs`: `bimBuildWallGeometry`, `bimSnapshotState`, `bimDispLen`, `bimDispNum`,
`bimBdsHtml`, `bimLevelAreas`, `bimPageSig`, `saveSoon`, `bimSetUnits`. `buildWallSolid`, `bimLoadProjectRecord`
and `bimRestoreState` ran out of memory in the Node stand-in, through their UI refresh calls. The walls were
therefore built from `bimBuildWallGeometry` plus the object literal `buildWallSolid` writes
(`bim/import-compliance.js:179-192`).

**E1, the change paths (static).** 219 files and 4,079 named functions. 219 call `pushUndo()`, 243 call
`saveSoon()`, and 139 write a project field of `A3D`. 29 call `pushUndo` without `saveSoon` in their own body; all
29 reach it through a callee by name (layers through `bimLayerChanged`, `select-change.js:162-166`). 33 write a
field with neither; 16 of them reach `saveSoon` through a callee, and 17 do not (ensure helpers, lazy getters such
as `bimSa`, `bimStdW`, `bimLbData`, the WebGPU stress model). The list is in `scan-output.txt`. Limits: names
only, no control flow, and callers are not traced.

`reach.mjs` (output `reach-output.txt`) answers the same question for one name. It gives `bimLoadProjectRecord`
true and `paint` true, by name only, through conditional branches. E3 measured that `paint()` does not move the
counter, so the name-based answer over-approximates, and the load paths rest on reading.

**E2, the cost of each strategy (2,000 walls, 943,284 bytes of JSON).**

| Measure | Median ms | p95 ms |
|---|---|---|
| Revision compare, 1,000,000 times | 0.623 | 0.630 |
| `JSON.stringify(objs)` | 1.516 | 2.777 |
| FNV-1a over that string | 0.995 | 2.494 |
| stringify + FNV-1a | 2.460 | 2.588 |
| Narrow fingerprint (id + centerline + thickness + level per wall) + FNV-1a | 0.506 | 0.638 |
| Recompute: sum of wall length x thickness | 0.044 | 0.072 |
| `bimSnapshotState()` (one undo step) | 1.546 | 1.877 |

E2b, `bimLevelAreas('lvl-0')` (the app's gross and net area) on closed rectangular rooms:

| Rooms | Edges | Median ms | p95 ms | Gross m² |
|---|---|---|---|---|
| 10 | 40 | 0.204 | 0.397 | 438.9 |
| 50 | 200 | 0.944 | 2.516 | 2194.5 |
| 100 | 400 | 3.002 | 4.763 | 4389.0 |
| 101 | 404 | 0.014 | 0.015 | null: "Too much geometry to trace here (404 edges, limit 400)" |

On 2,000 open walls (E2), the function returned at once with the same note, at 2,000 edges.

Formatting (one call per value, 200 values of about 176 to 35,273):

| Measure | N=50 median ms | N=200 median ms |
|---|---|---|
| `bimDispLen` | 0.0092 | 0.0228 |
| `bimDispNum(v,2)` | 0.0078 | 0.0224 |
| `toFixed(2)` | 0.0043 | 0.0136 |
| `Intl.NumberFormat`, one formatter reused | 0.0195 | 0.0739 |
| `Intl.NumberFormat`, a new one per value | 0.6315 | 2.4828 |
| Token substitution (`/<key>/` replaced from a dictionary, unknown keys left as typed) | 0.0168 | 0.0612 |

A board of 80 objects, 20 of them live text, through the app's `bimBdsHtml(B,[],{edit:false})`:

| Measure | Median ms | p95 ms |
|---|---|---|
| Markup, 80 objects (23,563 bytes) | 0.077 | 0.169 |
| Resolve 20 live values (one shared source) | 0.040 | 0.043 |
| Resolve + markup | 0.099 | 0.135 |

**What E2 shows.**
- Formatting and markup are negligible: 200 numbers in 0.02 ms; a board's markup in under 0.1 ms. Node only: the
  browser's `innerHTML` parse and layout were not measured here and are likely the larger cost.
- Hashing the model costs 10 to 50 times more than recomputing a simple sum. It costs about the same as the app's
  most expensive area function at its 400-edge limit.
- What matters is how many times a source is computed per revision, not the per-element check. 20 elements bound
  to a 3 ms source cost 60 ms if each computes on its own, and 3 ms with the memo. A new `Intl.NumberFormat` per
  value is 30 times slower than a reused one, so a formatter is made once per format.

**E3, does the counter move? (`rev-on-paths-output.json`)**

| Path | Moves the revision? |
|---|---|
| `saveSoon()` | yes, 0 to 1 |
| `bimSetUnits('mm')` | yes |
| `pushUndo()` alone | no |
| `paint()` | no |
| `doUndo()` on an empty stack | no ("Nothing to undo") |
| `bimLoadProjectRecord`, `bimRestoreState` | not measurable: out of memory in the stand-in; from reading, see part 3 |

**E4, the undo snapshot's size (`bimSnapshotState().length`, one board in `A3D.pres`).**

| | Empty model | 2,000 walls |
|---|---|---|
| Board, 80 plain objects | 11,232 | 954,514 |
| The same, 20 objects with a binding `{k,src,lvl,fmt:{u,dp}}` | 12,612 (+1,380; 69 B each) | 955,894 |
| The same, plus a stored resolved value `{v,s,rev,at}` | 14,172 (+1,560; 78 B each) | 957,454 (+0.163 %) |
| x 50 undo steps, the stored values alone | 78,000 bytes | |
| x 50 undo steps, the whole snapshot | | 45.6 MB (the model, not the board) |

The snapshot is the raw `A3D.pres` as set, not passed through `bimPresValid`.

## 6. Overrides as data

**The record (what is saved, and what goes into the 50 snapshots):**

    n.bind = {k:'num', src:'gfa', id:'lvl-0', f:'gross', fmt:{u:'m2', dp:1}}   /* what it shows: kind, source, its id, field, format */
    n.ov   = {s:'About 4,400 m²'}                                         /* the properties the person set by hand, with their values */
    n.ovAt = {s:'4,389.0 m²'}                                             /* optional: the resolved value of each overridden property when it was set */

- `bind` is the source, never the value. The kinds are `num`, `tok` (text tokens), `sched`, `legend`, `chart`,
  `view` and `res` (an analysis result); a source is named by key and id, never by expression.
- `ov` holds only the keys the person changed (text `s`, colour, size). Absent means everything follows the source.
- `ovAt` is the 3-way base, for overridden keys only. It makes "the source has changed since you overrode this"
  possible. Its states:
  - base (`ovAt`) equal to the current resolved value: the override stands, and nothing is said;
  - base different from current: the override still stands, but the Properties row says so, and offers Reset
    (back to the source) or Keep (`ovAt` is set to the current value).

  This is what a 3-way merge does with a common ancestor. It is also more than Figma's instance overrides offer:
  Figma has per-property reset, and its help page says nothing on a warning when the main component changes (S).
- **Not in the record:** the resolved value and the revision it was computed at. They live in a runtime map
  (`A3D_LIVE.memo`, keyed by `bimLiveKey`), beside `A3D_BRD` and `A3D_BMAP`, which are runtime too. E4 shows size
  is not the reason (78 KB over 50 steps). The reasons are correctness:
  1. a value written into the record on each recompute is a mutation. If it went through `saveSoon`, it would
     move the revision again: a feedback loop, which also marks the file changed (`bimFileTouch`, D2). If it did
     not, it would be a silent write the save path does not know about;
  2. a cached value restored by undo, or read from a file saved by another build, can disagree with the model
     restored with it. Recomputing from the model cannot;
  3. it would make a project file differ between two saves of the same model.
- **Before and after a build that knows `bind`:** `bimBobOne` (`board-objects.js:47`) drops fields it does not
  know, so an older build opening a V175 project keeps the text object and loses its binding. What it then shows is
  `n.s`. The owner must choose which `s` an older build should show (Q1):
  - **(i)** `s` holds the template as typed ("GFA {{gfa}}"): an older build shows the token itself;
  - **(ii)** `s` is the last resolved text, written at save time only: an older build shows the last value. This
    reintroduces a stored value, but only in the file, never in the snapshots.

  Recommendation: (i) for tokens in text, since it is honest and costs nothing; (ii) for a whole-object number.
  Confidence medium: it is a product choice.
- An old project has no `bind`. Every object stays as it is, and no migration is needed.

## 7. Token syntax compared

Criteria: escaping, typing on a phone, unknown keys, safety (the app never evaluates an expression), numbers with
units and precision.

| Syntax | Escaping | Phone typing | Unknown key | Evaluates? | Number format | Level |
|---|---|---|---|---|---|---|
| AutoCAD fields `%<\AcVar ...>%` | Written by a dialog, not typed; a field is an object in the text | Not typed | n/a (picked from a list) | Some fields are formulas | A format chosen in the dialog | FIELDEVAL P; the syntax itself is U, not read here |
| Rhino `%<Function("id")>%` | n/a | Hard: `%` `<` `(` `"` | "####" | **Yes**: arithmetic and Python (P, the digest) | Python and .NET format strings | S |
| QGIS `[% expression %]` | n/a | Hard | The expression's error | **Yes**: an expression engine | Expression functions | P |
| ArcGIS `<dyn type="" property="" decimalPlaces=""/>` | XML-like | Very hard | Empty, or `emptyStr` | No: attributes only | `decimalPlaces`, `preStr`, `postStr` | S |
| LayOut `<PageName>` | n/a | Moderate: `<` and `>` | Not said (part of the page not read) | No | Set per tag in Document Setup | S |
| Mustache `{{key}}` | `{{{ }}}` or `&` to skip HTML escaping; delimiters can be changed | Moderate: `{` `}` | **"" (empty)** | No; "No Re-interpolation" | None: the data arrives already formatted | P |

**Recommendation.**
- **Storage:** a token is a key, never an expression. Of the six, only the Rhino and QGIS forms evaluate; the app
  must never do so (no `eval`, no `Function`). Lookup is `hasOwnProperty` on a fixed table of keys, as in the
  measured `subst` (E2).
- **Text form:** `{{key}}`, Mustache's delimiters, with an optional format after a bar: `{{gfa|1}}`, 1 decimal.
  The result is never re-scanned, as Mustache specifies. Angle brackets are set aside: they collide with
  "< 5 m" written as plain text, and with the HTML the board builds. Braces seldom occur in labels.
- **An unknown key** is left as typed, and marked in edit mode. It does not become empty, as it does in Mustache:
  an empty result hides a typing error, which on a printed board is worse than a visible token. (Rhino's "####" is
  the same idea.)
- **The main way in is a menu,** not typing: Insert, then Field, the way LayOut, ArcGIS and AutoCAD all offer
  one. On a phone, `{` and `}` are on a second symbol page; that is not tested here (U).
- **Escaping:** no escape syntax. A literal `{{name}}` whose key is not in the table already stays as typed;
  for one whose key is known, Convert to static (QGIS's way, P) writes the resolved text and drops the binding.
  An escape rule (`\{{`) is one more thing to learn for a rare need, and stays an option if the owner wants it.
- **Numbers:** the app's own `bimDispNum` / `bimDispLen` (`palette.js:59-71`), plus the unit label appended by
  the app.
  - `Intl.NumberFormat` (Chrome 24, Firefox 29, Safari 10, IE 11; P, BCD) can add digit grouping, with one
    formatter reused per format (E2: 30 times faster than a new one per value).
  - Its `style:'unit'` needs Chrome 77 and Safari 14.1, and it has no square or cubic metre at all (ECMA-402's
    sanctioned list; `RangeError`, measured). Units therefore stay the app's own: m², m³, ha.
  - A token's precision defaults to the project's (`bimUnitDp`). Areas and volumes get their own default
    precision, since `bimDispNum` is not scaled by the length unit.

## 8. Edges

| Case | What happens, with this design | Source |
|---|---|---|
| Source deleted (a level, a schedule's kind, a view) | The resolver returns `{missing:true}`; the element draws "Source removed: Level 2" in edit mode, and an em dash on paper (the app's own no-value mark, `palette.js:60`); the binding is kept, so undo brings the source and the value back | `palette.js:60`; ArcGIS keeps a renamed frame's reference (S) |
| Not yet computed (an analysis never run, member forces before a solve) | `{pending:true}`: "Not computed: run Sunlight hours" in edit mode, and an em dash on paper; it never computes on draw (a Ladybug run is asynchronous and long, `ladybug/analyses.js:50-66`) | P (code) |
| Over a source's limit | `bimLevelAreas` returns `gross:null` with a note beyond 400 edges (E2b). The element shows the note, never 0 | P (measured) |
| Circular binding | Bindings resolve only against model sources, never against another board object or another live element (no chains). No schedule reads boards (`analysis-properties.js:233-251`), so the graph is one level deep and acyclic by construction. If a source that counts boards is ever added (a sheet list), its resolver must not read live values; a re-entry flag, as Preact's `RUNNING` (P), turns a mistake into a warning and an em dash instead of a loop | H5 |
| Present mode | The slideshow redraws a board when `e.b.id|A3D_REV|narrow` moves (`present.js:165`). The live key is folded into the same revision. A date token across midnight in a long presentation needs the day in the board's key too (LayOut: "updates on a daily basis", S; Excel's volatile functions, P) | P |
| Print, and `sheetCapture` | Values are resolved before drawing, outside any capture. `bimRenderSourceToCanvas` swaps the active level, camera and section for a viewport (`sheets.js:252-297`); a resolver that read "the active level" during that swap would print the viewport's level. Resolvers take explicit ids (`bind.id`), never the active state. Print and screen then show the same value at the same revision. AutoCAD's default updates fields on plot (FIELDEVAL bit 4, P); here every draw is already current, so print needs nothing extra | P |
| Units change | `bimSetUnits` saves (`palette.js:105`), so the revision moves; the key also carries `A3D_UNITS` | P (measured, E3) |
| Units across reload | `A3D_UNITS` is not in `bimProjectRecord` nor in the snapshot (`objects-save.js:53`; `plan-mode-sketch.js:293`). The comment at `palette.js:49` names `bimUnitState` / `bimApplyUnitState`, which do not exist (grep finds them nowhere else). The only callers of `bimSetUnits` are the units menu and the
precision field (`ui/shortcuts.js:389`, `:431`), and no `localStorage` key holds units. So the units return to metres on reload, and an undo does not undo a unit change. Either a live number stores its own unit in `bind.fmt.u`, or units become a project field. Owner decision Q2 | P (code); the reload behaviour is from reading, not run |
| Undo of a model edit | `doUndo` restores, then `saveSoon` (the revision moves), so the live value follows. Bindings and overrides are in `A3D.pres`, which is in the snapshot, so they undo with the model | P |
| Undo of fetched data | `dataFeatures` is not in the snapshot: an undo does not bring old features back. A live count of data features follows what is there | P |
| Opening a project, and the other tab's refresh | `bimLoadProjectRecord` does not move the revision. A read-only tab refreshed from the other tab (`tab-lock.js:138`) keeps pages, thumbnails and boards keyed on the old revision. This is a gap today, not only for V175. Fix: bump in `bimLoadProjectRecord` | P (reading), medium |
| Opening an old project (no `bind`) | Objects stay static; nothing to migrate | P |
| An older build opening a V175 project | `bimBobOne` drops `bind`, `ov` and `ovAt`; the object shows `n.s` (part 6, Q1) | P |
| Drag rate | Orbit, zoom and rotate move the revision per frame. With the memo, one compute per source per frame; a board is not drawn while it is hidden. An open board beside a model drag (a split view) pays 3 ms per area source per frame at the 400-edge worst case (E2b) | P / measured |
| Schedule units | Schedule columns are metres, whatever the project unit. A live schedule cell keeps the schedule's unit and label | P |

## 9. Open (U)

- The cost in a real browser of rebuilding a board's DOM (`innerHTML`, layout), on a desktop and on a phone. Node
  only here: no Playwright browser on this machine.
- Whether typing `{` `}` on iOS and Android keyboards is as hard as assumed (secondary symbol page). Not tested.
- AutoCAD's literal field code syntax (`%<\AcVar ...>%`) was not read at its source. Only FIELDEVAL was. The
  syntax shapes nothing in the recommendation.
- LayOut's behaviour for an unknown typed tag: not on the part of the page read.
- The load-path revision gap was found by reading, not by running: those paths run out of memory in the Node
  stand-in. A browser check would confirm it.
- The 17 writer functions that do not themselves reach `saveSoon` were not traced to every caller.
- The independent second reader (protocol step 9) has not yet re-read sources 4, 5, 7, 8, 10, 11, 12 and 13.

**The owner's decisions to ask (with the rest of V175's):**
- **Q1:** what an older build shows for a live text: the template, or the last value.
- **Q2:** project units become a saved project field, or each live number carries its own unit.
- **Q3:** should camera moves stop moving the model's revision? A wider change; it would spare redraws everywhere.

## 10. References

1. The app, `v175-research` at e1e3a31, read 2026-11-08 (P). The files and lines are in part 3, plus
   `docs/dev/canvas_v10_STATUS.md` lines 9910-9921 and 10005-10015.
2. Mokhov, A., Mitchell, N., Peyton Jones, S. (2018). Build Systems à la Carte. Proc. ACM Program. Lang. 2, ICFP,
   Article 79. https://doi.org/10.1145/3236774. PDF from
   https://www.microsoft.com/en-us/research/uploads/prod/2018/03/build-systems.pdf. Read: Definition 2.1; 2.3
   (early cutoff: "Make and Excel do not"); 4.1.2 restarting; 4.2.1 dirty bit (Excel's static over-approximation,
   INDIRECT); 4.2.2 verifying traces; 4.2.3 constructive traces; 5 (Excel = restarting + dirty bit); 6
   (volatility as a "RealWorld" key). 2026-11-08. P.
3. Mokhov, Mitchell, Peyton Jones (2020). Build systems à la carte: Theory and practice. JFP 30, e11.
   doi:10.1017/S0956796820000088. Abstract only (full text behind a login). 2026-11-08. S.
4. snowleopard/build @43b18b9a362d7d27b64679ea4122e4b8c5dfedd9, MIT, `src/Build/System.hs` lines 44-80. 2026-11-08. P.
5. preactjs/signals @30a797e962c76cc2e623e84f4194a00b9f0c5c8f, MIT (LICENSE read), `packages/core/src/index.ts`:
   lines 159-161 (`globalVersion`), 464 and 754 ("Cycle detected"), 504-530 (`needsToRecompute`), 649-695 (the
   computed's refresh). 2026-11-08. P.
6. mobxjs/mobx @2a97ff69a8bb4d6c3c8582da07ffd1c53c6612db, MIT: `packages/mobx/src/core/computedvalue.ts` 196-235;
   `src/errors.ts` 55-57 (error 32, a cycle); `docs/computeds.md` (suspended when not observed, `keepAlive`);
   `docs/configuration.md` 14-20 (Proxy required; no ES5 fallback in MobX 7). 2026-11-08. P.
7. solidjs/solid @bc50fe5649ba4fb1ef33f26643dba56c1c002b56, MIT. Repository only; not read. U, shaping nothing.
8. Microsoft, Excel Recalculation. MicrosoftDocs/office-developer-client-docs @eedbd61ca40689e7cfed5e1cfd9440a9dc3ab7a5,
   `docs/excel/excel-recalculation.md`: "Dependence, Dirty Cells, and Recalculated Cells"; "Volatile and
   Non-Volatile Functions". 2026-11-08. P.
9. mdn/browser-compat-data @82daeebf5a7073d55223a8cdb8aa54fb9416e27d, CC0,
   `javascript/builtins/Intl/NumberFormat.json`: the constructor, `format`, `formatToParts`, and the
   options_*_parameter entries. 2026-11-08. P.
10. tc39/ecma402 @3691634ebc1794f2af74cb26e59824b21090c3ad, `spec/locales-currencies-tz.html`, the sanctioned unit
    identifiers (45 units, no area or volume units but acre and hectare). 2026-11-08. P; with the `RangeError`
    run here in Node 26.
11. mustache/spec @e8ec001db7f594521e773c34866aca2b5d6b0037, MIT, `specs/interpolation.yml`: overview; "No
    Re-interpolation", "HTML Escaping", "Triple Mustache", "Basic Context Miss Interpolation". 2026-11-08. P.
12. qgis/QGIS-Documentation @83f9bab8c82bc9574a9e8ec8f4e4e65c6ebea339,
    `docs/user_manual/print_layout/layout_items/layout_label.rst` lines 37-63. Licence not read; no text used.
    2026-11-08. P.
13. Autodesk, FIELDEVAL (System Variable), AutoCAD LT 2022 help,
    https://help.autodesk.com/cloudhelp/2022/ENU/AutoCAD-LT/files/GUID-EF5D2DDE-A170-4BB4-8F76-7F3FAFE30E56.htm.
    The bit table, default 31, saved in the drawing, the Date field note. 2026-11-08. P (through the fetch tool).
14. McNeel, Rhino 8 help, Text fields, https://docs.mcneel.com/rhino/8/help/en-us/information/text_fields.htm.
    2026-11-08. S (the fetch tool's digest).
15. Esri, ArcGIS Pro, Add and modify dynamic text,
    https://doc.esri.com/en/arcgis-pro/latest/help/layouts/add-and-modify-dynamic-text.html. 2026-11-08. S (digest).
16. Trimble, SketchUp LayOut, Automating title blocks (Auto-Text), https://help.sketchup.com/en/layout/automate-titleblocks.
    The first 100,000 characters. 2026-11-08. S (digest).
17. Figma, Apply changes to instances,
    https://help.figma.com/hc/en-us/articles/360039150733-Apply-changes-to-instances. 2026-11-08. S (digest).
18. The experiments here: `docs/research/experiments/v175-invalidation/` (E1 to E4), run 2026-11-08, Node v26.13.0,
    AMD Ryzen 7 8845HS, Windows 11. P (measured).
