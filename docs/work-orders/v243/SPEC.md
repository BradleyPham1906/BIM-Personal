# V243 spec: Concrete members: cracking and strength

Research: `docs/research/research-physical-world.md` (part 4.5) and `docs/research/research-physical-world/member-checks-cracking.md`; the independent check in `docs/research/research-physical-world/independent-check.md`. The owner's decisions: as the research recommends (part 11 of the note; the owner, 2026-11-21: "Do your research first, properly. And then develop the work orders"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-21.

## 1. The decisions this spec follows

- ACI 318-19 (318-25 changes shear and phi, not these): Ec = 4700 sqrt(f'c), fr = 0.62 lambda sqrt(f'c), Mcr = fr Ig / yt, Ie by Table 24.2.3.5 (Bischoff; Branson's equation is gone).
- Cracking shown in three states: uncracked up to 2/3 Mcr, reduced (318-19 lowers Ie, though the section has not cracked) up to Mcr, cracked above; no crack widths.
- f'c on the material card; the solve keeps the card's E and a mismatch with 4700 sqrt(f'c) is shown (decision 11).
- Reinforcement per beam type: bottom and top bars, cover; only singly reinforced rectangles are checked; columns, deep beams (ln/h < 4) and anything else are "not checked" with the reason.
- Ratio bands: none (grey), low < 0.5, mid < 0.9, high <= 1.0, over (decision 12). One-way shear Vc is left out (its SI coefficients are U).

## 2. What it does for the user

Properties, Material: f'c and lambda for concrete; Properties, beam type: bars and cover. Analyze, Structure, Check: each concrete beam coloured by its cracking state or by Mu / phi Mn, with Mcr, Ie and phi Mn in its Properties.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/structure/rc-checks.js` | new, after `js/engine/structure/modal.js` in `src/index.html` (header done) | 6 pure functions (part 5) | Cline, WO-01 to WO-06 |
| `docs/work-orders/v243/v243.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, C-07, C-08 |

## 4. Units

mm and MPa inside the functions (N mm moments returned as kN m); the app's kN and m converted by Claude's wiring.

## 5. Functions, `src/js/engine/structure/rc-checks.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file. A later function may use an earlier one of this file, as its task says.

- **WO-01 `bimRcMat(fc, lambda)`**: lambda is 1 when not finite. {error: 'bad input'} unless fc > 0 and 0 < lambda <= 1. Ec = 4700 sqrt(fc), fr = 0.62 lambda sqrt(fc), beta1 = 0.85 for fc <= 28, 0.65 for fc >= 55, else 0.85 - 0.05 (fc - 28) / 7. Returns {Ec, fr, beta1}. Example: 30 gives {25742.96, 3.39588, 0.83571}.
- **WO-02 `bimRcSection(b, h, d, As, Es, Ec, fr)`**: {error: 'bad input'} unless every argument is positive and d < h. Ig = b h^3 / 12, yt = h / 2, Mcr = fr Ig / yt / 1e6 (kN m), n = Es / Ec; kd is the positive root of b kd^2 / 2 = n As (d - kd), that is (-n As + sqrt((n As)^2 + 2 b n As d)) / b; Icr = b kd^3 / 3 + n As (d - kd)^2. Returns {Ig, yt, Mcr, n, kd, Icr}. Example: (300, 500, 450, 942, 200000, 25742.96, 3.39588) gives Mcr 42.448, kd 125.774, Icr 9.68303e8.
- **WO-03 `bimRcIe(Mcr, Ma, Ig, Icr)`**: with M = |Ma|: NaN unless Mcr > 0, Ig > 0, 0 < Icr <= Ig and M is finite; Ig when M <= 2/3 Mcr; else Icr / (1 - ((2/3) Mcr / M)^2 (1 - Icr / Ig)). Example: (42.4485, 60, 3.125e9, 9.683e8) gives 1.1439e9.
- **WO-04 `bimRcState(Ma, Mcr)`**: with M = |Ma|: 'none' unless Mcr > 0 and M is finite; 'uncracked' when M <= 2/3 Mcr; 'reduced' when M <= Mcr; else 'cracked'.
- **WO-05 `bimRcFlexure(b, d, As, fy, fc, Es)`**: {error: 'bad input'} unless every argument is positive. beta1 as in WO-01 (written here again: no call); a = As fy / (0.85 fc b); c = a / beta1; {error: 'over-reinforced: the neutral axis is below the steel'} when c >= d; epst = 0.003 (d - c) / c; ety = fy / Es; phi = 0.9 when epst >= ety + 0.003, 0.65 when epst <= ety, else 0.65 + 0.25 (epst - ety) / 0.003; Mn = As fy (d - a/2) / 1e6 (kN m). Returns {a, c, epst, phi, Mn, phiMn}. Example: (300, 450, 942, 420, 30, 200000) gives phiMn 151.03.
- **WO-06 `bimCheckBand(r)`**: 'none' for null, undefined, a value that is not finite or below 0; 'low' below 0.5; 'mid' below 0.9; 'high' up to and including 1; 'over' above 1.

## 6. Order of the work

WO-01 to WO-06 in order. Then Claude: **C-07** f'c and lambda on concrete materials, bars and cover on beam types, the check run after a solve (Ma from the member's largest moment, the section from its type), the colours, the Properties rows, the refusals; the test to tests/unit/; npm run modules; **C-08** the records.

## 7. Not in this phase

Columns (P-M interaction); shear (Vc, stirrups); doubly reinforced and T sections; crack widths; deflection by Ie inside the solve; prestressed members; 318-25.
