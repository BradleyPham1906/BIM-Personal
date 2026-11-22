# V244 spec: Steel members: AISC 360-22 checks

Research: `docs/research/research-physical-world.md` (part 4.5) and `docs/research/research-physical-world/member-checks-cracking.md`; the independent check in `docs/research/research-physical-world/independent-check.md`. The owner's decisions: as the research recommends, answered 2026-11-22 (standard and scalable; 4, 9 and 11 amended) (part 11 of the note; the owner, 2026-11-21: "Do your research first, properly. And then develop the work orders"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-21.

## 1. The decisions this spec follows

- AISC 360-22 LRFD for compact, doubly symmetric I shapes: E3 compression, F2 flexure about the major axis (Lp, Lr, Cb), F6 minor axis as min(Fy Zy, 1.6 Fy Sy), H1-1 interaction in compression; E = 200 GPa for the checks whatever the card says.
- Section properties through one source that prefers a published table (AISC's Shapes Database once its licence is read) and falls back to the profile's plates (`bimStIProps`, no fillets: within 1.4 % of the table, J 6.9 % low, which errs safe), labelled with where they came from (decision 11, amended 2026-11-22).
- Lb = the member's length, K = 1, Cb = 1 by default, each with an override per member (decision 11).
- Refused as "not checked", with the reason: noncompact or slender plates, HSS, pipes, channels, members in tension (H1.2 not read), concrete, timber.

## 2. What it does for the user

Properties, Material: Fy for steel. Properties, member: Lb, K, Cb. Analyze, Structure, Check: each steel member coloured by its H1 ratio, with phi Pn, phi Mn, the equation used and what governs in its Properties.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/structure/steel-checks.js` | new, after `js/engine/structure/rc-checks.js` in `src/index.html` (header done) | 7 pure functions (part 5) | Cline, WO-01 to WO-07 |
| `docs/work-orders/v244/v244.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, C-08, C-09 |

## 4. Units

mm and MPa inside the functions; Pn in kN, Mn in kN m.

## 5. Functions, `src/js/engine/structure/steel-checks.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file. A later function may use an earlier one of this file, as its task says.

- **WO-01 `bimStIProps(d, bf, tf, tw)`**: {error: 'bad input'} unless every argument is positive, 2 tf < d and tw <= bf. h = d - 2 tf, ho = d - tf; A = 2 bf tf + h tw; Ix = (bf d^3 - (bf - tw) h^3) / 12; Iy = (2 tf bf^3 + h tw^3) / 12; Zx = bf tf (d - tf) + tw h^2 / 4; Zy = bf^2 tf / 2 + h tw^2 / 4; Sx = Ix / (d/2); Sy = Iy / (bf/2); rx, ry = sqrt(I / A); J = (2 bf tf^3 + ho tw^3) / 3; Cw = Iy ho^2 / 4; rts = sqrt(sqrt(Iy Cw) / Sx). Returns {A, Ix, Iy, Zx, Zy, Sx, Sy, rx, ry, J, Cw, ho, rts, h}.
- **WO-02 `bimStCompact(bf, tf, h, tw, Fy, E)`**: {error: 'bad input'} unless every argument is positive. s = sqrt(E / Fy), lf = bf / (2 tf), lw = h / tw. flange: 'compact' when lf <= 0.38 s, 'noncompact' when lf <= s, else 'slender'; web: 'compact' when lw <= 3.76 s, 'noncompact' when lw <= 5.70 s, else 'slender'; flangeComp: 'nonslender' when lf <= 0.56 s, else 'slender'; webComp: 'nonslender' when lw <= 1.49 s, else 'slender'. Returns {flange, web, flangeComp, webComp}.
- **WO-03 `bimStPhiPn(A, r, Lc, Fy, E)`**: {error: 'bad input'} unless every argument is positive. slender = Lc / r; Fe = pi^2 E / slender^2; Fn = 0.658^(Fy/Fe) Fy when slender <= 4.71 sqrt(E/Fy), else 0.877 Fe; Pn = Fn A / 1000 (kN); phiPn = 0.9 Pn. Returns {slender, Fe, Fn, Pn, phiPn}. Example: the W10x49 (A 9290 mm2, ry 64.5 mm), Lc 4000, Fy 345 gives phiPn 2177.5 kN.
- **WO-04 `bimStLpLr(ry, rts, J, Sx, ho, Fy, E)`**: {error: 'bad input'} unless every argument is positive. Lp = 1.76 ry sqrt(E/Fy); with t = J / (Sx ho) and u = 0.7 Fy / E (c = 1), Lr = 1.95 rts (E / (0.7 Fy)) sqrt(t + sqrt(t^2 + 6.76 u^2)). Returns {Lp, Lr} in mm. Example: the W10x49 gives 2733.9 and 9631.3.
- **WO-05 `bimStPhiMn(o)`**: o {Zx, Sx, Fy, E, Lb, Lp, Lr, Cb (1 when not finite), rts, J, ho}. {error: 'bad input'} unless Zx, Sx, Fy, E, Lp are positive, Lb >= 0 and Lr > Lp. Mp = Fy Zx. Lb <= Lp: Mn = Mp, zone 'plastic'. Lb <= Lr: Mn = min(Cb (Mp - (Mp - 0.7 Fy Sx)(Lb - Lp)/(Lr - Lp)), Mp), zone 'inelastic'. Else s = Lb / rts, Fcr = Cb pi^2 E / s^2 sqrt(1 + 0.078 J / (Sx ho) s^2), Mn = min(Fcr Sx, Mp), zone 'elastic'. Returns {Mp, Mn, phiMn = 0.9 Mn, zone}, moments in kN m (N mm / 1e6). Example: the W10x49 at Lb 4000, Cb 1 gives phiMn 286.61.
- **WO-06 `bimStCb(Mmax, MA, MB, MC)`**: 12.5 |Mmax| / (2.5 |Mmax| + 3 |MA| + 4 |MB| + 3 |MC|), MA, MB, MC the moments at the quarter, middle and three-quarter points of the unbraced segment; 1 when the denominator is 0. Example: (1, 0.25, 0.5, 0.75) gives 1.6667.
- **WO-07 `bimStH1(Pr, Pc, Mrx, Mcx, Mry, Mcy)`**: {error: 'bad input'} unless Pc, Mcx and Mcy are positive. p = |Pr| / Pc, m = |Mrx| / Mcx + |Mry| / Mcy; when p >= 0.2 {ratio: p + 8/9 m, eq: 'H1-1a'}, else {ratio: p / 2 + m, eq: 'H1-1b'}. Example: (1000, 2177.54, 100, 286.61, 0, 100) gives 0.7694, 'H1-1a'.

## 6. Order of the work

WO-01 to WO-07 in order. Then Claude: **C-08** Fy on steel materials (default 345 MPa for W shapes), Lb, K, Cb on members, the check after a solve (Pr, Mrx, Mry from the member results along its length; Cb from `bimStCb` when the user asks), the minor axis by F6, the colours with `bimCheckBand`, the refusals; the test to tests/unit/; npm run modules; **C-09** the records.

## 7. Not in this phase

Noncompact and slender sections (F3 to F5, E7); HSS, pipes, channels, angles; tension (D, H1.2); shear (G2); connections; second-order effects (C2, B1 and B2); an AISC shapes table (licence first).
