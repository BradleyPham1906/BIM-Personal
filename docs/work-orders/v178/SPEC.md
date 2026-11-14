# V178 spec: Presentation P3, the report (Site Analysis and DA), styles, export

Research: `docs/research/research-notion-v178-presentation.md`, with `research-da-report-reference.md` and
`research-archimap-site-report.md`. The owner's decisions, 2026-11-14, all as recommended: (1) all three output
families are kept (the eight Site Analysis boards, the six DA sheets, the archiMap additions), sharing figures;
(2) boards stay live while edited, and an export is bound to a frozen manifest of one model revision; (3)
components sync explicitly, keep per-field overrides and can be detached, local to the project for now (no
cross-project library); (4) PowerPoint as editable text and shapes with maps and effects as pictures, each picture
listed; (5) partial data makes a marked report, never a blocked one, and a missing value never shows as zero;
(6) readers, resolution and tolerances are set from measurements in WO-14, not guessed. Implementation target:
local `main`. Written by Claude, 2026-11-14.

## 1. What it does for the user

In Present, "New report" makes the Site Analysis report (eight boards in a fixed order) and, when asked, the DA
set (six sheets) as ordinary layouts in the one paper space of V175c, each figure, map and number live. Every
number on a report shows its state: a value, "(partial)", "(out of date)", "Not available" or "Failed", never a
blank zero; hovering shows its source, vintage, method and licence. A title block, a legend style or a colour set
made once is a component: change it, press Sync, and every board takes the change except what was overridden on
that board. Export writes PDF (the browser's print, vector where it can), PNG per board, and later PowerPoint,
each export stamped with the model revision it was made from and marked out of date when the model moves on.
Legends never drop classes silently: "and 3 more" when they do not fit.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/sheets/report-model.js` | new, after `live-sources.js` (header done) | twelve pure functions (part 4) | Cline, WO-01 to WO-12 |
| `docs/work-orders/v178/v178.test.mjs` | new | their tests | Claude (done) |
| `sheets/boards.js`, `board-figures.js`, `board-map.js`, `live-sources.js`, `present.js`, `presentation-panel.js` | changed | the report built on them | Claude, WO-13 to WO-15 |

## 3. Data

**A datum** `{value, unit, state, source, vintage, retrieved, method, license}`: `value` a finite number, a
non-empty string or `null`; `state` one of `available`, `partial`, `stale`, `unavailable`, `failed`; the other
fields strings (`''` when not known). A live field's outcome (`live-sources.js`: `ok`, `stale`, `gone`, `none`)
maps to `available`, `stale`, `failed`, `unavailable`.

**A plan entry** `{id: 'SA-01', family: 'sa'|'da', title, n}`; the Site Analysis boards SA-01 Location and
context, SA-02 Zoning summary, SA-03 Landform and water, SA-04 Climate, SA-05 Access, SA-06 Risks, SA-07
Constraints and opportunities, SA-08 Buildable area and yield; the DA sheets DA-01 Context plan, sun and wind,
DA-02 Site coverage, GFA and FSR, DA-03 Model and shadow studies, DA-04 Buildings and schedule, DA-05 Sections and
elevations, DA-06 Perspectives. `n` counts from 1 across the families asked for.

**A manifest** `{id, revision, generated, boards: [ids], data: {key: datum}}`, keys in sorted order, every datum a
copy made by `bimRptDatum`.

**A component definition** `{id, version, props: {...}}`; **an instance** `{id, defId, version, overrides: {...}}`.

## 4. Functions, `src/js/engine/sheets/report-model.js`

- **WO-01 `bimRptFromLive(st)`**: `'ok'` `available`, `'stale'` `stale`, `'gone'` `failed`, anything else
  `unavailable`.
- **WO-02 `bimRptDatum(raw)`**, with the list `BIM_RPT_STATES` above it: a new datum (part 3) from any value. An
  unknown state is `unavailable`. A value that is not a finite number or a non-empty string is `null`; a `null` value
  with state `available`, `partial` or `stale` makes the state `unavailable`; `unavailable` and `failed` always
  carry `null`. Fields that are not strings become `''`. Extra fields are dropped. `null` gives the blank datum.
- **WO-03 `bimRptText(d, digits)`**: `'Not available'` for no datum or `unavailable`; `'Failed'` for `failed`;
  else a number by `toFixed(digits)` (digits a number 0 to 6, floored; otherwise 0) or the string as it is, then
  `' ' + unit` when there is one, then `' (partial)'` or `' (out of date)'` for those states.
- **WO-04 `bimRptRings(radiiKm)`**: the positive finite numbers, once each, smallest first, as
  `{km, label: 'Within ' + km + ' km', cumulative: true}`; `[]` for anything not array-like.
- **WO-05 `bimRptPlan(families)`**, with the tables `BIM_RPT_SA` and `BIM_RPT_DA` above it: the SA boards when
  `families.sa`, then the DA sheets when `families.da`, numbered `n` from 1.
- **WO-06 `bimRptIssue(data)`**: each value of the object through `bimRptDatum`; `counts` of each of the five
  states (all five keys, in the order of part 3); `marked` the keys whose state is not `available`, sorted;
  `status` `'marked'` when any, else `'complete'`.
- **WO-07 `bimRptManifest(report, revision, when)`**: part 3, from `report.id` (a string, else `''`),
  `report.boards` (strings only, in order) and `report.data` (keys sorted, each by `bimRptDatum`).
- **WO-08 `bimRptStale(manifest, revision)`**: true when there is no manifest or its revision is not `revision`.
- **WO-09 `bimRptLegend(rows, max)`**: `max` a number 1 or more, floored, else 12; `{rows: the first max rows,
  more: how many were left out}`; no rows, `{rows: [], more: 0}`.
- **WO-10 `bimCompResolve(def, inst)`**: a new object of `def.props`, each overridden by `inst.overrides[k]` when
  the definition has `k`; overrides the definition lacks are ignored.
- **WO-11 `bimCompSync(inst, def)`**: `{id: inst.id, defId: def.id, version: def.version, overrides}`, keeping only
  the overrides whose key the new definition still has; the old instance is not changed.
- **WO-12 `bimCompDetach(def, inst)`**: `{id: inst.id, props: bimCompResolve(def, inst)}`.

## 5. Order of the work

WO-01 to WO-12 in order (WO-03, WO-06 and WO-07 use WO-02; WO-11 and WO-12 use WO-10). Then Claude:

- **WO-13** the report on the boards: "New report" builds the plan's layouts from SA1 to SA5's figures and live
  fields; every number through `bimRptText`; `board-map.js`'s legend through `bimRptLegend` (its fixed 12 now says
  "and N more"); `board-map.js`'s cache key made to include the tiles' identities (the research's suspected stale
  hit, tested first); components on boards with Sync and Detach; one browser check of the new interface.
- **WO-14** export: PDF by the browser's print of the layouts and PNG per board, each with its manifest; a canvas
  that cannot be read (a map provider without CORS) is named in the export's message, never silently left blank;
  the measurements decision 6 waits for.
- **WO-15** the archiMap additions as their own work orders (rings with `bimRptRings`, street context, lots, heights
  and coverage within 200 m, business mix), each with its free source and licence checked, and PowerPoint (decision
  4) after a library is researched under the library rule.

## 6. Not in this phase

Cross-project component libraries; nested components; regulated determinations (zoning and flood stay labelled
with their source and status, never a finding); Open-Meteo in the report (its free terms are non-commercial: the
report uses the weather file the owner opens).
