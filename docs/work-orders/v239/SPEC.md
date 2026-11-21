# V239 spec: Floor loads from the place

Research: `docs/research/research-physical-world.md` (part 4.1) and `docs/research/research-physical-world/loads-wind-gravity.md`; the independent check in `docs/research/research-physical-world/independent-check.md`. The owner's decisions: as the research recommends (part 11 of the note; the owner, 2026-11-21: "Do your research first, properly. And then develop the work orders"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-21.

## 1. The decisions this spec follows

- Live loads by occupancy from IBC 2021 Table 1607.1 (mirroring ASCE 7-22 Table 4.3-1), kept in the registry as data with their edition (V167), not in code.
- Live load reduction by ASCE 7-22 4.7 / IBC 1607.12.1, as a switch per project, off by default (decision 5): leaving it out is conservative.
- Roof live load by 4.8 for ordinary roofs (Lo 0.96 kPa), held between 0.58 and 0.96 kPa.
- Floor dead and live loads reach the frame as line loads on beams from their tributary strips (Claude's wiring), so the solver takes floors for the first time.

## 2. What it does for the user

Properties, Structure: each level's occupancy (Office, Residential, Assembly ...) fills its live load from the registry; Analyze, Structure includes the floors' dead and live loads on the beams, with live load reduction when the switch is on, and the summary no longer says "Not included: Floor loads".

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/structure/floor-loads.js` | new, after `js/engine/structure/frame-solve.js` in `src/index.html` (header done) | 3 pure functions (part 5) | Cline, WO-01 to WO-03 |
| `docs/work-orders/v239/v239.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, C-04, C-05 |

## 4. Units

kPa for loads, m2 for areas; KLL a number; the number of floors a member supports a whole number; slope rise over run (0.25 for 3 in 12).

## 5. Functions, `src/js/engine/structure/floor-loads.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file. A later function may use an earlier one of this file, as its task says.

- **WO-01 `bimLiveKll(kind)`**: the live load element factor of Table 4.7-1 by the member's kind, a string: 'interior column' 4, 'exterior column' 4, 'edge column cantilever' 3, 'corner column cantilever' 2, 'edge beam' 2, 'interior beam' 2; anything else (another string, '', undefined, and names such as 'toString' that objects carry) 1. Example: bimLiveKll('edge beam') is 2.
- **WO-02 `bimLiveReduce(Lo, KLL, AT, floors, rule)`**: {error: 'bad input'} unless Lo >= 0, KLL > 0 and AT >= 0. rule 'none' (assembly and the other rows of the table that are never reduced): {L: Lo, rule: 'none'}. rule 'garage', or Lo above 4.79 kPa: {L: 0.8 Lo when floors >= 2 else Lo, rule: 'garage' or 'heavy'}. KLL AT below 37.16 m2: {L: Lo, rule: 'small'}. Otherwise f = 0.25 + 4.57 / sqrt(KLL AT), L = Lo times f held between the lower limit (0.5 for one floor, 0.4 for two or more) and 1: {L, rule: 'reduced'}. Example: (2.40, 4, 128, 2) gives L 1.0847, 'reduced'; (2.40, 2, 16, 1) gives {L: 2.40, rule: 'small'}.
- **WO-03 `bimRoofLive(Lo, At, slope)`**: NaN unless Lo >= 0, At >= 0 and slope >= 0. F = 12 slope (inches of rise per foot). R1 = 1 for At <= 18.58 m2, 1.2 - 0.011 At below 55.74 m2, 0.6 from 55.74 m2. R2 = 1 for F <= 4, 1.2 - 0.05 F below 12, 0.6 from 12. Returns Lo R1 R2 held between 0.58 and 0.96. Example: (0.96, 30, 0.5) gives 0.96 x 0.87 x 0.9 = 0.75168.

## 6. Order of the work

WO-01 to WO-03 in order. Then Claude: **C-04** the registry's live loads by occupancy (IBC 2021 Table 1607.1 with its reducibility notes), an occupancy on each level in Properties filling Live, the reduction switch; beams' line loads from their tributary strips (one-way: half the spacing each side) in `bimStructLoads`; the takedown using `bimLiveReduce` with its AT and floors; the summary's "Not included" line; the test to tests/unit/; npm run modules; **C-05** the records.

## 7. Not in this phase

Concentrated live loads; partitions as a separate case; snow; pattern loading of live load; one-way slab AT caps (the takedown's Voronoi areas stand).
