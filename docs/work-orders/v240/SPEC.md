# V240 spec: Wind loads from the place

Research: `docs/research/research-physical-world.md` (part 4.2) and `docs/research/research-physical-world/loads-wind-gravity.md`; the independent check in `docs/research/research-physical-world/independent-check.md`. The owner's decisions: as the research recommends (part 11 of the note; the owner, 2026-11-21: "Do your research first, properly. And then develop the work orders"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-21.

## 1. The decisions this spec follows

- ASCE 7-22 directional procedure (chapters 26 and 27) for an enclosed, rigid building's main wind force resisting system; q without Kd, Kd in the pressure (the 7-22 change).
- Terrain constants of 7-22 Table 26.11-1 (B 7.5 / 3280 ft, C 9.8 / 2460 ft, D 11.5 / 1935 ft); the formula equals the tabulated values (independent check).
- Basic wind speed V typed by the user with its Risk Category; a link to the ASCE Hazard Tool; no undocumented service (decision 3).
- Ke is given (1.0 unless the user sets it): its exponential formula has one source only and stays out of the code (independent check W7).
- Case 1 applied to the frame in X and Z; cases 2 to 4 computed and listed, applied once V242's rigid floors take a torsion (decision 4).
- The approximate frequency tells the user whether the rigid G = 0.85 applies (n1 >= 1 Hz); flexible buildings are refused for now.

## 2. What it does for the user

Properties, Site: wind speed V, Risk Category, exposure (B, C, D) by direction, Kzt and Ke (default 1). Analyze, Structure: a new load case W, each level's wind force in X and Z applied at the level, the table of storey forces and the four cases, the combinations 1.2D + 1.0W + L and 0.9D + 1.0W.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/structure/wind-loads.js` | new, after `js/engine/structure/floor-loads.js` in `src/index.html` (header done) | 6 pure functions and the table BIM_WIND_EXP (part 5) | Cline, WO-01 to WO-06 |
| `docs/work-orders/v240/v240.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, C-07, C-08 |

## 4. Units

m for heights and plan sizes, m/s for V, Pa for q and p, kN for storey forces, kN m for torsions, Hz for frequency.

## 5. Functions, `src/js/engine/structure/wind-loads.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file. A later function may use an earlier one of this file, as its task says.

- **WO-01 `bimWindKz(z, exp)`**: with BIM_WIND_EXP just above it, {B: [7.5, 3280], C: [9.8, 2460], D: [11.5, 1935]} (alpha, zg in ft): NaN for another exposure or a z that is not finite. zg in m = zg ft x 0.3048; z below 4.572 m is taken as 4.572; at or above zg, 2.41; else 2.41 (z/zg)^(2/alpha). Example: (7, 'C') gives 0.9285.
- **WO-02 `bimWindQz(z, exp, V, Kzt, Ke)`**: 0.613 x bimWindKz(z, exp) x Kzt x Ke x V^2, in Pa; Kzt and Ke are 1 when not finite. Example: (7, 'C', 50) gives 1422.9.
- **WO-03 `bimWindCpLee(r)`**: the leeward wall Cp for r = L/B: NaN unless r >= 0; -0.5 up to 1; -0.5 + 0.2 (r - 1) up to 2; -0.3 + 0.05 (r - 2) up to 4; -0.2 above. Example: 1.5 gives -0.4.
- **WO-04 `bimWindStoreys(o)`**: o {levels: [heights of the floor levels above the base, m, rising], B (width across the wind, m), L (depth along it), V, exp, Kzt, Ke, Kd (0.85 when not finite), G (0.85 when not finite)}. {error: 'bad input'} unless there is at least one level, B, L and V are positive and exp is B, C or D; {error: 'levels must rise above 0'} unless each level is above the one before (the first above 0). qh = bimWindQz at the top level; the leeward pressure pl = qh Kd G bimWindCpLee(L/B) for every level. Level i's band: from halfway to the level below (z0/2 for the first) to halfway to the level above (the top level's band ends at its height). For each level {z, Kz, qz (bimWindQz at z), pw = qz Kd G 0.8, pl, lo, hi, F = (pw - pl) B (hi - lo) / 1000 kN}. Returns {levels: [...], qh, total: the sum of F}. Internal pressure cancels in F. Example: levels [3.5, 7, 10.5], B 30, L 20, V 50, 'C' gives F 137.79, 144.98, 76.21 kN.
- **WO-05 `bimWindCases(Fx, Fz, Bx, Bz)`**: the four load cases of ASCE 7-22 Figure 27.3-8 from the case 1 storey forces in X (Fx, wind along X, the building's width across it Bx) and Z (Fz, Bz), arrays of the same levels (a missing value is 0; the length is the longer one's). For each level {c1x: Fx, c1z: Fz, c2x: 0.75 Fx, c2z: 0.75 Fz, mt2x: 0.75 Fx 0.15 Bx, mt2z: 0.75 Fz 0.15 Bz, c3x: 0.75 Fx, c3z: 0.75 Fz, c4x: 0.563 Fx, c4z: 0.563 Fz, mt4: 0.563 (Fx 0.15 Bx + Fz 0.15 Bz)}. Example: Fx 137.79, Bx 30 gives mt2x 465.04 kN m.
- **WO-06 `bimWindNa(system, h)`**: the approximate natural frequency in Hz from the height h in m, with hf = h / 0.3048: 'steel-mrf' 22.2 / hf^0.8, 'concrete-mrf' 43.5 / hf^0.9, 'other' 75 / hf; NaN for another system or h not positive. Example: ('steel-mrf', 10.5) gives 1.308.

## 6. Order of the work

WO-01 to WO-06 in order. Then Claude: **C-07** the load case W: `bimLoadProblem` and `bimStructLoads` accept W, lateral loads at every column top of a level shared by the columns there; the 2.3.1 combinations with W (1.2D + 1.0W + L, 0.9D + 1.0W) in the registry; the Site fields (V, Risk Category, exposure per direction, Kzt, Ke) and the link to the ASCE Hazard Tool; the refusal when n1 < 1 Hz; the storey table and the four cases in Analyze; the test to tests/unit/; npm run modules; **C-08** the records.

## 7. Not in this phase

Components and cladding; roofs' MWFRS pressures; flexible buildings (Gf); the envelope procedure (chapter 28); topographic Kzt calculation; Ke's formula; ASCE's map server.
