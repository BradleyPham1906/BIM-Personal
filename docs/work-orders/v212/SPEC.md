# V212 spec: Survey control, traverses and closure

Notion: Later: Survey control. Research: `docs/research/research-later-survey-control.md`, `docs/research/research-survey-check.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Observations are kept as the field recorded them, with their units, separate from computed coordinates (an observation ledger), so nothing calculated is mistaken for a measurement.
- A closed loop or a link to a known end is assessed; an open traverse is 'not assessable', never a pass.
- The compass (Bowditch) rule first, labelled a closure diagnostic, not a weighted network adjustment; least squares later.
- Raw total-station formats are parsed only from real files the owner provides, one format at a time.

## 2. What it does for the user

Enter a traverse (azimuths in DMS or decimal degrees, distances): the app gives its linear and angular misclosure, its precision ratio and the compass-adjusted coordinates, into V138's checks.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/survey/traverse-control.js` | new, after `js/engine/survey/survey-arithmetic.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v212/v212.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 5. Functions, `src/js/engine/survey/traverse-control.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimSvDms(s)`**: a number as it is (null when not finite); a string 'D-M-S' or 'D M S' (minutes and seconds optional, seconds decimal, a leading minus) as D + M/60 + S/3600 with the sign; null for anything else or minutes or seconds of 60 or more.
- **WO-02 `bimSvLatDep(legs)`**: legs [[azimuth degrees from north clockwise, distance]]: {lat: d cos az, dep: d sin az (each per leg), sumN, sumE, perimeter}.
- **WO-03 `bimSvClosure(legs, kind, start, end)`**: 'open': {status: 'not assessable', why: 'an open traverse has no independent closure'}; 'link' without start or end: 'not assessable', 'a link traverse needs its known end'; else {status: 'computed', east, north (the sums, or start + sums - end for a link), misclosure, perimeter, ratio: perimeter / misclosure (Infinity at 0)}.
- **WO-04 `bimSvCompass(legs, start)`**: the start [E, N], then each point after a leg moved by its departure and latitude less sumE d / perimeter and sumN d / perimeter.
- **WO-05 `bimSvAngular(angles)`**: the sum of the interior angles less (n - 2) 180; null for fewer than 3.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** wiring into the app; **WO-07** the records.

## 7. Not in this phase

Least-squares networks; levelling; gnss; raw file parsers before the owner's files.
