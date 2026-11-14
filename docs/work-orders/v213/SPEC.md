# V213 spec: Generators: massing, parking, lots

Notion: Later: Generators. Research: `docs/research/research-later-generators.md`, `docs/research/research-giraffe.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Massing fills V160's zoning envelope to the achievable area: the smaller of the plates the coverage allows times the levels and the FAR limit, plate by plate from the ground up, tagged by usage.
- Storeys from the envelope's height and a floor-to-floor the owner sets (3.5 m by default).
- Parking by ratios the owner enters (none shipped as law); 90-degree stalls 2.6 by 5.5 m on 7.2 m aisles by default.
- Lots by a target frontage, equal widths; never claimed as a legal subdivision.

## 2. What it does for the user

Generate a massing that fills the zoning envelope with its plates, a parking layout that meets the entered ratios, and lots along a street.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/site-tools/generators.js` | new, after `js/engine/site-tools/capacity.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v213/v213.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 5. Functions, `src/js/engine/site-tools/generators.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimGenAchievable(lot, far, cov, levels)`**: plateCap = lot cov, capacity = plateCap levels, farLimit = lot far, achievable = the smaller; plates filled from the ground, each the smaller of plateCap and what is left (never under 0). {plateCap, capacity, farLimit, achievable, plates}.
- **WO-02 `bimGenStoreys(h, ftf)`**: ftf 3.5 unless positive; {storeys: floor(h / ftf + 1e-9), top: storeys ftf}; {0, 0} when h is not positive.
- **WO-03 `bimGenStalls(needs)`**: needs [{qty, per, ratio}] (ratio stalls per 'per' of qty): ceil(sum of qty / per ratio - 1e-9), lines with per or qty not positive left out; 0 (never -0) when the sum is 0.
- **WO-04 `bimGenParking(w, d, stall, aisle)`**: stall {w 2.6, d 5.5} and aisle 7.2 unless positive; perRow = floor(w / stall.w + 1e-9); a double module is 2 stall.d + aisle deep; doubleModules = floor(d / module + 1e-9); singleRows 1 when the rest is at least stall.d + aisle; stalls = perRow (2 doubleModules + singleRows).
- **WO-05 `bimGenLots(frontage, target)`**: [] unless both positive; n = max(1, floor(frontage / target + 1e-9)) lots of frontage / n.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** wiring into the app; **WO-07** the records.

## 7. Not in this phase

Optimisation; angled parking; irregular parking fields.
