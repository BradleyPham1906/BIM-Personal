# Member design checks and cracking (US codes): research note

One of four parallel research notes for the physical-world question (2026-11-21). This side: where a
member is overstressed and where concrete cracks, from the app's linear frame solve, by ACI 318
(concrete) and AISC 360 (steel). No nonlinear analysis. Method: `docs/research/research-protocol.md`.
Worked examples: `docs/research/experiments/physical-world/member_checks.py` (pure Python, every
number below is printed and asserted there; run `python3 -I member_checks.py`).

## 1. Abstract

**Question.** From the forces the frame solve already gives (N, Vy, Vz, My, Mz, T along each member,
kN and m), can the app honestly show (1) a code check ratio for steel and concrete members and (2)
where a concrete member is cracked, and what does it need that it does not have?

**Answer.** Yes for a first, linear, clearly labelled check, with limits. Cracking is a direct
comparison: the service moment Ma against Mcr = fr Ig / yt with fr = 0.62 lambda sqrt(f'c) MPa; a
member is "cracked" where |Ma| > Mcr, and ACI 318-19's effective inertia (Bischoff's form with
2/3 Mcr) tells how much stiffness it lost. A steel member gets the AISC 360-22 H1-1 unity ratio from
E3 (compression), F2 (flexure of compact doubly symmetric I shapes) and G2.1 (shear). A concrete beam
gets phi Mn / Mu and phi Vc / Vu from ACI 318-19 22.2 and Table 22.5.5.1. What the app cannot show
honestly: a crack width (ACI 318 gives none; it limits bar spacing instead), crack patterns beyond
"flexural cracks on the tension face over this length", and anything for slender or noncompact steel
sections, which it must refuse rather than guess. **The app is missing the inputs these checks need:**
f'c, fy (rebar), Fy (steel), the reinforcement (As, cover, bar size, stirrups), effective length
factors and unbraced lengths, and the steel section's tabulated properties (Zx, Sx, ry, J, Cw, rts,
ho). Its Concrete card's E (32 GPa) also does not match any f'c the app could be given (it implies
f'c = 46.4 MPa by 19.2.2.1(b)).

**Recommendation.** Build in this order: (1) cracking map for concrete beams under the service
combination (D+L, already in the registry), needing only f'c and lambda; (2) the steel unity check for
compact W shapes, with Lb, Lc (K L) and Cb from the model and the catalogue's tabulated properties;
(3) concrete beam flexure and shear once the owner decides how reinforcement is entered. Colour the
ratio in bands with 1.0 as the hard edge (practice below). Every result carries "ACI 318-19 / AISC
360-22, linear first-order, not a design" and its level.

## 2. The question and the hypotheses

Question: what must the app compute, from which code clauses, with which inputs, so that a colour on a
member means "overstressed" or "cracked" in the codes' own sense, and where does it have to stop?

| # | Hypothesis (falsifiable) | Outcome |
|---|---|---|
| H1 | ACI 318-19 replaced Branson's Ie with Bischoff's form using a reduced cracking moment 2/3 Mcr, Ie = Ig for Ma <= 2/3 Mcr | **Held (S).** StructurePoint's 14-to-19 change note quotes R24.2.3.5 (Bischoff and Scanlon adopted, Branson removed); Bischoff's ACI abstract; Yau et al. (JASE) print the table's form; four independent open implementations agree. Counter-evidence: calcs.com's "ACI 318-19" beam calculator still documents Branson's cube form; one 318M-25 implementation tests Ma <= Mcr before the 2/3 Mcr branch. Both recorded, neither changes the finding. |
| H2 | ACI 318-25 is out and changes neither fr, Mcr, the Ie table, nor the one-way shear Vc equations | **Partly failed.** 318-25 is out (concrete.org, 2025-01-22, P). Per StructurePoint (S): it adds a lower bound on Vc against the combined lambda_s and rho_w reduction (its coefficient not read, U), drops the 318-19 commentary's two-thirds-depth simplification for rho_w, restores full fr for slabs with fy > 80 ksi, and limits phi in the transition region. No source reports a change to Mcr or the Ie table (absence, medium confidence). |
| H3 | AISC 360-22's E3, F2 (compact doubly symmetric I), G2.1 (rolled I, Cv1 = 1) and H1-1 are unchanged in substance from 360-16 | **Held (S), with renamings.** 360-22 renames Fcr to Fn in Chapter E and uses Lc for the effective length (SDC Verifier's comparison); F2 changed only a user note; G2 was reorganised; H1-1 unchanged, H3-6 revised (biaxial). Denavit's code has separate 2016 and 2022 classes with identical E3/F2/G2.1 equations, and notes F6's minor-axis 0.69 became 0.7 in 2022. |
| H4 | The app's frame results carry what the checks need (N with sign, both moments, shear, samples along the member) | **Held for forces, failed for inputs.** Forces: yes (frame-solve.js:246-286). Inputs: f'c, fy, Fy, As, cover, Lb, K, Cb and tabulated steel properties are absent (section 8). |
| H5 | Professional tools colour the ratio with bands ending at 1.0, and the bands are user-set | **Held (P for the documents read).** CSI ETABS: five user-set increasing values, may exceed 1.0; SkyCiv: green < 1, orange 0.95 to 1, red > 1, grey not checked; STAAD: user-set ranges, passed members green; Tekla Structural Designer: up to 10 user divisions. ETABS's default band values (0.5/0.7/0.9/1.0) were **not** confirmed (U). |

## 3. Method

### Search log (2026-11-21)

| # | Where | Query or URL | Result | Kept / set aside |
|---|---|---|---|---|
| 1 | curl | aisc.org (steel-standards page, a360-22w.pdf, shapes database v16) | 403 (refused, as on 2026-10-18) | Refused host recorded |
| 2 | WebFetch | aisc.org a360-22w.pdf | 403 | Refused |
| 3 | curl | concrete.org home; 318-19 preview PDF | 200; preview is front matter and contents only | Kept for edition, dates, 318-19 superseding 318-14 |
| 4 | curl | concrete.org news f=51745596; concrete.org/aci318 | 200 | Kept: 318-25 released 2025-01-22 (P) |
| 5 | curl | concrete.org store product page for 318-25 | proxy: tunnel closed mid-exchange | Set aside |
| 6 | curl | xe.berkeley.edu CE-123 ACI 318-19 PDF | 502 / timeout, twice | Unreachable, recorded |
| 7 | WebSearch | ACI 318-25 changes, Ie, size effect | pointers to StructurePoint 318-25 PDF, ACI webinar | Read both (rows 8, 9) |
| 8 | curl | structurepoint.org ACI-318-25 revisions PDF | 200, 8 pages | Kept (S) |
| 9 | curl | concrete.org ws_F25_LucasLaughery.pdf | 200 | Kept: lambda_s SI form sqrt(2/(1+d/250)) (S, ACI-hosted slide) |
| 10 | curl | iccsafe.org S. K. Ghosh 318-14 to 318-19 changes | 200; equations are images | Kept for scope of the Vc change (S) |
| 11 | WebSearch | Table 24.2.3.5 Bischoff 2/3 Mcr | pointers | Followed (12-16) |
| 12 | curl | concrete.org ICA abstract 51718072 (Bischoff 2020) | 200 | Kept (P for the abstract) |
| 13 | curl + REST | idecad.atlassian.net pages (immediate deflection, effective stiffness, one-way shear, materials, flexure, phi) via Confluence REST | 200; equations as images, tables as text | Kept: Table 6.6.3.1.1(a), beta1, phi, Es (S) |
| 14 | curl | structurepoint.org TA Cracking Coefficient (ACI 19) | 200 | Kept: Table 6.6.3.1.1(a) (S) |
| 15 | curl | structurepoint.org changes 318-14 to 318-19 | 200 | Kept: quotes 24.2.3.5 Mcr, R24.2.3.5, 22.5.5.1.1-3, 8.3.1.1 reduced fr (S) |
| 16 | curl | jase.tku.edu.tw Yau et al. 2022 | 200 | Kept: Ie table form, Icr (S); its Ec = 3750 sqrt(f'c) is Taiwan's, not ACI's (counter-evidence noted) |
| 17 | curl | support.tekla.com ACI 318-19 pages | 202 (bot check), then 301 to help.trimble.com, 404 | Refused, recorded |
| 18 | curl | erikssonsoftware.atlassian.net (REST, id decoded from tiny link) | 200; equations as images | Set aside |
| 19 | curl | dlubal.com KB 001666; docs.bentley.com RAM ACI 318-19 notes (two) | 200 | Kept: Table 22.5.5.1 (a)(b)(c), 22.5.5.1.1-3 (S) |
| 20 | curl | eng.auburn.edu ACI CRC 2020 report | 200 | Kept: Vc (c) and lambda_s (S) |
| 21 | curl | blog.risa.com 318-19 slab deflection | 200 | Kept: practice, 318-19 Ie drops fast past 2/3 Mcr (S) |
| 22 | curl | calcs.com ACI 318-19 beam docs | 200 | Counter-evidence: documents Branson's form under a 318-19 label |
| 23 | WebSearch + curl | edurev concrete formula sheet | 200 | Kept as second source for fr, Ec, beta1, lambda values (S, low weight) |
| 24 | WebSearch + curl | aspirebridge.com crack control (2015) | 200 | Kept: Frosch's spacing equation replaced Gergely-Lutz; fs may be 2/3 fy (S) |
| 25 | WebSearch | Table 24.3.2 spacing | Tekla, StructureMag, Eng-Tips pointers | Spacing rule S via Tekla's doc digest and ASPIRE |
| 26 | gh search code | `Icr / (1`, `2/3*Mcr` | 8+ repositories | Kept as implementations (corroboration, read as text) |
| 27 | raw.githubusercontent | arisa-chan aci318m25_slab.py | 200 | Kept: 318M-25 Ie same form; its Ma <= Mcr early return is a bug (counter-evidence on implementations) |
| 28 | raw | robbievanleeuwen/concrete-properties (MIT): concrete_section.py, as3600.py, results.py | 200 | Kept: Mcr from the E-weighted transformed section; AS3600 f'ct.f = 0.6 sqrt(f'c) |
| 29 | raw | fib-international/structuralcodes (Apache-2.0): MC2010 fctm, EC2 7.3 crack control | 200 | Kept: the only open crack-width model found is Eurocode's |
| 30 | gh search code | `W10X49` `60.4` | 15+ copies of the AISC shapes table | Kept: W10x49 properties, several independent copies agree (S) |
| 31 | raw | denavit/libdenavit-py (MIT) wide_flange.py | 200 | Kept: E3, F2, F6, G2.1, B4.1 limits for AISC 2016 and 2022 (P for the code, S for the standard) |
| 32 | raw | youandvern/efficalc (MIT) steel_beam_moment_strength.py | 200 | Kept: F2 equation numbers; its F2-4 line has `+` where `*` belongs (implementation bug, noted) |
| 33 | raw | xcfem/xc ASTM_materials.py (licence file 404; read as method only) | 200 | Kept: H1-1a/b, tension not implemented there |
| 34 | raw | Sompote/pondus steel.rs (AGPL-3.0, method only) | 200 | Kept: Cb F1-1 from quarter points, capped at 3.0 (the cap is a 360-05 relic, U) |
| 35 | curl | iccsafe.org AISC 360-22 change list and summary of revisions; Oregon State UDSS 4th ed updates; sdcverifier.com 360-10 vs 360-22 | 200 | Kept: Fcr to Fn, Lc, H3-6 (S) |
| 36 | curl | CSI ETABS Output Colors; RISA results view; Bentley RAM code check colours; STAAD custom colours; SkyCiv integrated design | 200 | Kept (P for each document) |
| 37 | curl | web.wiki.csiamerica.com (two pages) | 202 bot check | Refused |
| 38 | curl | awc.org (NDS 2024) | 403 | Refused; timber deferred anyway |
| 39 | raw | JWock82/Pynite README; svortega/steelpy README | 200 | PyNite: analysis only; steelpy README empty, not read further |

Downloads: `/tmp/claude-0/dl-check/member-checks/` (read as text, never run).

### Sources by kind

- Standard text: ACI 318-19 and 318-25 are sold; AISC 360-22 is free but aisc.org refuses this
  environment. No primary standard text was read. Every code value is S: two or more independent
  secondary sources, or one secondary source plus open implementations read as text.
- Publishers' own pages (P): concrete.org (edition, release date, Bischoff abstract), the vendors'
  help pages for colouring.
- Practitioners' documents (S): StructurePoint, ideCAD, Bentley RAM, Dlubal, Tekla (digest), RISA.
- Papers (S): Yau et al. 2022 (JASE), the ACI CRC 2020 Auburn report, ASPIRE 2015.
- Open implementations (P as code, S as evidence for the standard): libdenavit-py, efficalc, xc,
  pondus, concrete-properties, structuralcodes, several ACI 318-19 Ie implementations.

### Experiments

`member_checks.py` computes both worked examples (section 6) and cross-checks: fr in psi against MPa,
Vc (c) in psi units against SI coefficients, Ie by 318-19 against Branson, the app's sharp-corner W
section against the table. Environment: Python 3, this container, one run (deterministic).

### Independent check

**Not done in this note.** Step 9 of the protocol needs a second reader to re-read the sources behind
every fact in section 4 marked "code uses". Until then those facts stay at their stated level and
must not be called checked.

## 4. Findings

Units: MPa and mm unless said. "Code uses" marks what an implementation would compute with.

### 4.1 Concrete, ACI 318-19 (and 318-25)

| Fact | Value | Source, section | Level | Confidence |
|---|---|---|---|---|
| Edition | ACI 318-19 adopted 3 May 2019, published June 2019, supersedes 318-14; reapproved 2022 | concrete.org 318-19 preview, front matter | P | High |
| Newer edition | ACI CODE-318-25 released 22 January 2025 (digital), print later in 2025; offered in inch-pound and SI | concrete.org news f=51745596; concrete.org/aci318 | P | High |
| Ec (code uses) | Ec = 4700 sqrt(f'c) for normal weight (19.2.2.1(b)); Ec = wc^1.5 x 0.043 sqrt(f'c) for wc 1440 to 2560 kg/m3 (19.2.2.1(a)) | ideCAD materials page names Eq. 19.2.2.1.b; edurev formula sheet gives both forms | S | High (long-standing values) |
| fr (code uses) | fr = 0.62 lambda sqrt(f'c) MPa = 7.5 lambda sqrt(f'c) psi (19.2.3.1) | edurev; concrete-properties' AS3600 uses 0.6 sqrt(f'c) (comparable); ACI 435 preview lists fr | S | High |
| lambda | 1.0 normal weight; 0.85 sand-lightweight; 0.75 all-lightweight (Table 19.2.4.2, by composition; also a wc-based form) | edurev; ideCAD one-way shear page names 19.2.4.3 | S | Medium (the wc-based alternative not read) |
| Mcr (code uses) | Mcr = fr Ig / yt, Ig of the gross concrete neglecting steel, yt to the tension face (24.2.3.5) | StructurePoint 14-to-19 PDF quotes it; ideCAD notation | S | High |
| Ie (code uses) | Nonprestressed, Table 24.2.3.5: Ie = Ig when Ma <= (2/3) Mcr; Ie = Icr / (1 - ((2/3) Mcr / Ma)^2 (1 - Icr/Ig)) when Ma > (2/3) Mcr | StructurePoint quoting R24.2.3.5 (Bischoff and Scanlon adopted, Branson removed); Yau et al. eq. 15; RISA blog; four open implementations | S | High |
| Ie, continuous spans | May be the average of Table 24.2.3.5 at the critical positive and negative sections (24.2.3.6); for prismatic members, the value at midspan (simple and continuous) or at the support (cantilever) (24.2.3.7) | ideCAD immediate deflections page | S | Medium |
| Icr, singly reinforced rectangle (code uses) | n = Es/Ec; kd from b (kd)^2 / 2 = n As (d - kd); Icr = b (kd)^3 / 3 + n As (d - kd)^2 | Yau et al. eqs 13-14 (with compression steel); textbook mechanics | S | High |
| Es | 200 000 MPa (29 000 000 psi) | ideCAD materials page | S | High |
| Stiffness modifiers | Table 6.6.3.1.1(a): columns 0.70 Ig; walls uncracked 0.70 Ig, cracked 0.35 Ig; beams 0.35 Ig; flat plates and flat slabs 0.25 Ig; area 1.0 Ag | StructurePoint TA note; ideCAD effective stiffness page | S | High |
| Modifiers' scope | Applies to analysis under factored loads (strength); service-level lateral uses larger values (1.4 times, 6.6.3.2.2) | Not read in any source here | U | - |
| beta1 (code uses) | 0.85 for 17 <= f'c <= 28; 0.85 - 0.05 (f'c - 28)/7 for 28 < f'c < 55; 0.65 for f'c >= 55 (Table 22.2.2.4.3) | ideCAD flexure page (psi form); edurev (both forms) | S | High |
| Flexure, singly reinforced (code uses) | a = As fy / (0.85 f'c b); Mn = As fy (d - a/2); c = a / beta1; eps_t = 0.003 (d - c)/c | ideCAD flexure page; edurev | S | High |
| phi (code uses) | Table 21.2.2: eps_t >= eps_ty + 0.003, 0.90; eps_t <= eps_ty, 0.65 (tied); between, 0.65 + 0.25 (eps_t - eps_ty)/0.003, eps_ty = fy/Es. Shear 0.75 | ideCAD phi page | S | High |
| 318-25 phi | 318-25 caps phi in the region 0.1 f'c Ag <= Pn <= Pn,bal (interpolation 0.90 to phi_cc) | StructurePoint 318-25 PDF | S | Medium |
| As,min (code uses) | 9.6.1.2: greater of 0.25 sqrt(f'c)/fy bw d and 1.4/fy bw d (SI); waived where As provided >= 4/3 As required (9.6.1.3) | ideCAD reinforcement limits page names both clauses; the SI coefficients are the standard conversion | S (clauses), U (the SI coefficients read only as conversion) | Medium |
| Vc, nonprestressed (code uses) | Table 22.5.5.1: Av >= Av,min: (a) [2 lambda sqrt(f'c) + Nu/(6Ag)] bw d or (b) [8 lambda rho_w^(1/3) sqrt(f'c) + Nu/(6Ag)] bw d; Av < Av,min: (c) [8 lambda_s lambda rho_w^(1/3) sqrt(f'c) + Nu/(6Ag)] bw d, psi. Vc <= 5 lambda sqrt(f'c) bw d (22.5.5.1.1), Nu/(6Ag) <= 0.05 f'c (22.5.5.1.2), Vc >= 0 | Dlubal KB 001666; Bentley RAM (two pages); StructurePoint 14-to-19; Auburn CRC report | S | High |
| lambda_s (code uses) | sqrt(2 / (1 + d/10)) <= 1, d in inches (22.5.5.1.3); SI sqrt(2/(1 + d/250)), d mm | StructurePoint quotes 22.5.5.1.3; Dlubal; Laughery's ACI-hosted slide gives the SI form | S | High |
| Vc SI coefficients | 0.17, 0.66 and 0.42 (for 2, 8 and 5 in psi) | Conversion by us (8 / 12.04 = 0.664); no SI source read | U | Recommend computing in psi and converting, or confirming 318M |
| sqrt(f'c) cap | sqrt(f'c) <= 100 psi (8.3 MPa) for Vc unless enhanced minimum stirrups (22.5.3.1) | ideCAD; Ghosh slides | S | High |
| 318-25 shear | Vc lower bound added (except net tension and two seismic clauses); rho_w's two-thirds-depth commentary removed; pile caps / mats with close piles: lambda_s = 1 for two-way | StructurePoint 318-25 PDF | S (coefficient of the lower bound U) | Medium |
| Foundations | Size effect may be neglected for one-way shallow foundations and some footings and mats (13.2.6.2, 318-19) | StructurePoint 14-to-19; Bentley RAM | S | High |
| Slabs fy > 80 ksi | 318-19 8.3.1.1: deflection with reduced fr = 5 sqrt(f'c) psi; removed in 318-25 | StructurePoint (both PDFs) | S | High |
| Crack control (US) | 318 gives no crack width. Table 24.3.2 limits the spacing of bars nearest the tension face: s <= 15 (40 000/fs) - 2.5 cc and <= 12 (40 000/fs), inches and psi; fs may be taken as 2/3 fy | ASPIRE 2015 (Frosch's equation, adopted by ACI, replaced Gergely and Lutz); Tekla's doc (digest); StructureMag | S | Medium (the table read only through others) |
| Crack width elsewhere | Eurocode 2 (2004) 7.3.4: wk = sr,max (eps_sm - eps_cm), with sr,max from cover, bar size and rho_p,eff | structuralcodes (Apache-2.0) `_section_7_3_crack_control.py`, read as text | P (code), S (EC2) | High for what the code does |

### 4.2 Steel, AISC 360-22

All S: aisc.org refused; the equations are read in three or more open implementations that agree,
plus the practitioners' comparisons for what changed since 360-16.

| Fact | Value | Where read | Confidence |
|---|---|---|---|
| Edition | ANSI/AISC 360-22; Chapter E's Fcr renamed Fn, effective length Lc (K L one way to get it) | SDC Verifier comparison; UDSS 4th ed updates | High |
| E3 (code uses) | Fe = pi^2 E / (Lc/r)^2; Fn = 0.658^(Fy/Fe) Fy when Lc/r <= 4.71 sqrt(E/Fy) (equivalently Fy/Fe <= 2.25), else Fn = 0.877 Fe; Pn = Fn Ag; phi_c = 0.90 | libdenavit (2016 and 2022 classes), efficalc HSS example (E3-2), rectangle_shape.py | High |
| B4.1a, compression (code uses) | Rolled I flange b/t = bf/2tf nonslender <= 0.56 sqrt(E/Fy) (case 1); doubly symmetric I web h/tw <= 1.49 sqrt(E/Fy) (case 5) | libdenavit | High |
| B4.1b, flexure (code uses) | Flange (case 10): compact <= 0.38 sqrt(E/Fy), noncompact <= 1.0 sqrt(E/Fy); web (case 15): compact <= 3.76 sqrt(E/Fy), noncompact <= 5.70 sqrt(E/Fy) | libdenavit; efficalc cites B4.1b(10) and (15) | High (5.70 from libdenavit only, plus our recall) |
| F2 (code uses) | Mp = Fy Zx (F2-1); Lb <= Lp: Mn = Mp; Lp < Lb <= Lr: Mn = Cb [Mp - (Mp - 0.7 Fy Sx)(Lb - Lp)/(Lr - Lp)] <= Mp (F2-2); Lb > Lr: Mn = Fcr Sx <= Mp (F2-3), Fcr = Cb pi^2 E/(Lb/rts)^2 sqrt(1 + 0.078 (J c/(Sx ho))(Lb/rts)^2) (F2-4); Lp = 1.76 ry sqrt(E/Fy) (F2-5); Lr = 1.95 rts (E/(0.7 Fy)) sqrt(J c/(Sx ho) + sqrt((J c/(Sx ho))^2 + 6.76 (0.7 Fy/E)^2)) (F2-6); c = 1 for doubly symmetric I (F2-8a); rts^2 = sqrt(Iy Cw)/Sx (F2-7); phi_b = 0.90 | libdenavit; efficalc (equation numbers); buddyd16 steel_calculator (Lr, Fcr) | High |
| Cb | F1-1: Cb = 12.5 Mmax / (2.5 Mmax + 3 MA + 4 MB + 3 MC), quarter-point absolute moments of the unbraced segment; in 360-22 a separate subsection F1(c) | pondus (formula); SDC Verifier (F1(c)) | High (formula); the 3.0 cap is not in 360-10 on, U |
| F6, minor axis | Mn = min(Fy Zy, 1.6 Fy Sy) for compact flanges; noncompact/slender flange: 2022 uses 0.7 E / lambda^2 where 2016 had 0.69 | libdenavit 2016 vs 2022 classes | Medium |
| G2.1 (code uses) | Rolled I with h/tw <= 2.24 sqrt(E/Fy): Cv1 = 1.0, phi_v = 1.00; Vn = 0.6 Fy Aw Cv1, Aw = d tw; otherwise phi_v = 0.90 and Cv1 from kv = 5.34 | libdenavit (both editions) | High |
| H1-1 (code uses) | Pr/Pc >= 0.2: Pr/Pc + 8/9 (Mrx/Mcx + Mry/Mcy) <= 1 (H1-1a); Pr/Pc < 0.2: Pr/(2 Pc) + (Mrx/Mcx + Mry/Mcy) <= 1 (H1-1b); Pc = phi Pn, Mc = phi Mn. In tension (H1.2) the same with Pc = phi_t Pn tension | xc; steelsnakes; franalli; SDC Verifier (H unchanged except H3-6) | High (compression); Medium (tension form, H1.2 not read) |
| E | 200 000 MPa (29 000 ksi) | AISC convention, every implementation read | High |
| W10x49 (W250x73) | A 14.4 in2, d 10.0, bf 10.0, tw 0.340, tf 0.560, kdes 1.06, bf/2tf 8.93, h/tw 23.1, Ix 272 in4, Zx 60.4 in3, Sx 54.6 in3, rx 4.35 in, Iy 93.4 in4, Zy 28.3 in3, Sy 18.7 in3, ry 2.54 in, J 1.39 in4, Cw 2070 in6, rts 2.84 in, ho 9.44 in | AISC Shapes Database values as copied in libdenavit-py, hypar-io/Elements, OpenSees scripts and others (agree to the digit) | S, High |

### 4.3 Timber

NDS 2024 (AWC) is noted for later; awc.org refused (403). Nothing here is for code.

### 4.4 Prior art: how tools check and show it

| Tool | What it does | Source | Level |
|---|---|---|---|
| CSI ETABS / SAP2000 | Steel design ratios coloured by five user-set increasing values; the top may exceed 1.0; a member whose design procedure does not match is drawn in the background's opposite colour; SAP shows "P-M Ratios Colors & Values" | docs.csiamerica.com Output Colors; SAP Colors | P (defaults' values U) |
| CSI, concrete | Reduces default fr for slab deflection to 4 sqrt(f'c) psi after ACI 435R-95 | Search digest of CSI wiki; the wiki refused | U |
| SkyCiv | Green < 1, orange 0.95 to 1, red > 1, grey "not checked" (unsupported shape, custom section, missing material) | skyciv.com integrated design docs | P |
| STAAD.Pro | User-set ranges for utilisation; passed members green | Bentley STAAD AD.2006.2.2 | P |
| RAM Structural System | Members redrawn coloured by degree of over- or under-stress; legend dialog | Bentley RAM Code Check Colors | P |
| RISA-3D | Colour basis "code check" or stress; key in the corner; per combination | RISA help, Results View Settings | P |
| Tekla Structural Designer | Up to 10 user divisions with colours; below the lowest band is N/A; ratios above 1.0 allowed | Tekla article (digest) | S |
| RISA / ADAPT | Report Ie/Ig per 318-19; show it falls fast past 2/3 Mcr | RISA blog | S |
| concrete-properties (MIT) | Mcr from the **transformed** E-weighted section (not ACI's gross concrete); cracked properties by removing tensile concrete; no Ie (Bischoff/Branson) | concrete_section.py | P |
| structuralcodes (Apache-2.0) | MC2010 fctm = 0.3 fck^(2/3) (fck <= 50); EC2 7.3 crack width and spacing | source | P |
| PyNite (MIT) | Analysis only, no member design | README | P |

The common practice is not the 0-0.5-0.9-1.0 split as a standard: every tool makes the bands
user-set, and the one documented default read here (SkyCiv) is green / orange from 0.95 / red above
1.0 / grey unchecked. A grey "not checked" state is the practice the app needs most, since many
members will have missing inputs.

## 5. The alternatives compared

Criteria (set before comparing): honest to the code; needs only inputs the owner can give; no new
library; fits the linear solve; says what it cannot do.

| Option | Honest | Inputs | Fits | Verdict |
|---|---|---|---|---|
| A. Cracked / uncracked only (|Ma| vs Mcr, service D+L), plus Ie/Ig as a stiffness loss | Yes: exactly what 24.2.3.5 defines | f'c, lambda | Yes | **First** |
| B. A + concrete flexure and shear ratio | Yes, for singly reinforced rectangles | + As, d (cover, bar), fy, stirrups or none | Yes | Second, after the owner's reinforcement decision |
| C. Steel H1 unity for compact W | Yes, for the covered shapes; refuse others | Fy, Lc (K), Lb, Cb from moments, tabulated Zx, Sx, ry, J, rts, ho | Yes | Second, in parallel |
| D. Crack widths by EC2 7.3 | Not US code; needs bar layout | Cover, bar size, spacing | Partly | Later, as a labelled non-US estimate |
| E. Re-run the solve with cracked stiffness (Ie or 6.6.3.1.1 modifiers) | Linear but iterative; changes force distribution | As above | Changes the solve | Later; the 0.35/0.70 modifiers are a cheap first step for strength runs |
| F. Nonlinear FEA | Out of scope | | | Refused |

## 6. Worked examples (from `member_checks.py`)

### (a) RC beam 300 x 500 mm, d = 450, f'c = 30 MPa, 3 bars 20 mm (As = 942 mm2), fy = 420, Es = 200 000

| Step | Arithmetic | Result |
|---|---|---|
| Ec | 4700 sqrt(30) | 25 743 MPa |
| fr | 0.62 x 1.0 x sqrt(30) | 3.3959 MPa (7.5 sqrt(psi) gives 3.4110, 0.45 % apart) |
| Ig | 300 x 500^3 / 12 | 3.1250e9 mm4 |
| yt | 500 / 2 | 250 mm |
| Mcr | 3.3959 x 3.125e9 / 250 | 42.45 kN m |
| n | 200 000 / 25 743 | 7.7691 |
| kd | 150 x^2 + 7318.5 x - 3 293 330 = 0 | 125.77 mm (k = 0.2795) |
| Icr | 300 x 125.77^3 / 3 + 7.7691 x 942 x 324.23^2 | 9.6830e8 mm4 (Icr/Ig = 0.310; compare beams' 0.35 Ig) |
| beta1 | 0.85 - 0.05 (30 - 28)/7 | 0.8357 |
| a, c | 942 x 420 / (0.85 x 30 x 300); a / beta1 | 51.72 mm; 61.88 mm |
| eps_t | 0.003 (450 - 61.88)/61.88 | 0.0188 >= 0.0021 + 0.003: tension-controlled, phi = 0.90 |
| Mn, phi Mn | 942 x 420 x (450 - 25.86) | 167.81 kN m; 151.03 kN m |
| As,min | max(0.25 sqrt30/420, 1.4/420) x 300 x 450 | 450 mm2 (942 provided) |
| Ie at Ma = 20 kN m | 20 <= (2/3) 42.45 = 28.30 | Ig = 3.1250e9 (uncracked) |
| Ie at Ma = 60 kN m | 9.683e8 / (1 - (28.30/60)^2 x 0.6901) | 1.1439e9 mm4 (Ie/Ig 0.366; Branson 0.554) |
| Ie at Ma = 120 kN m | 9.683e8 / (1 - (28.30/120)^2 x 0.6901) | 1.0070e9 mm4 (Ie/Ig 0.322; Branson 0.340) |
| Vc, no stirrups (c) | lambda_s = sqrt(2/(1 + 450/250)) = 0.8452; rho_w = 0.00698; 0.66 x 0.8452 x 0.1911 x sqrt30 x 135 000 | 78.8 kN (79.7 kN by the psi form); phi Vc = 59.1 kN |
| Vc, with Av,min (a) / (b) | 0.17 sqrt30 x 135 000; 0.66 x 0.1911 x sqrt30 x 135 000 | 125.7 kN / 93.3 kN (either may be used) |

Reading: at 60 kN m the beam is cracked (60 > 42.45) and has lost 63 % of its gross stiffness under
318-19, against 45 % under Branson: the 318-19 change matters most just past cracking, as RISA's blog
and Bischoff's abstract say.

### (b) W10x49 (W250x73) column, L = 4 m, K = 1, Fy = 345 MPa, E = 200 000 MPa

| Step | Arithmetic | Result |
|---|---|---|
| A, rx, ry | 14.4 in2, 4.35 in, 2.54 in | 9290 mm2, 110.5 mm, 64.5 mm |
| Compactness | bf/2tf 8.93 <= 0.38 sqrt(E/Fy) = 9.15; h/tw 23.1 <= 3.76 sqrt(E/Fy) = 90.5; compression 8.93 <= 13.48, 23.1 <= 35.9 | compact, nonslender |
| Lc/r | 4000/110.5 = 36.2; 4000/64.5 = 62.0 (governs) | <= 4.71 sqrt(E/Fy) = 113.4 |
| Fe | pi^2 x 200 000 / 62.0^2 | 513.5 MPa |
| Fn | 0.658^(345/513.5) x 345 | 260.4 MPa |
| Pn, phi Pn | 260.4 x 9290; x 0.90 | 2419 kN; 2178 kN |
| Mp | 345 x 989 780 | 341.5 kN m |
| Lp, Lr | 1.76 x 64.5 x sqrt(579.7); F2-6 with J, Sx, ho, rts, c = 1 | 2734 mm; 9631 mm (Lp 8.97 ft and Lr 31.6 ft, matching our recall of Manual Table 3-2, U) |
| Mn at Lb = 4 m, Cb = 1.0 | 341.5 - (341.5 - 0.7 x 345 x 894 730) x (4000 - 2734)/(9631 - 2734) | 318.5 kN m; phi Mn = 286.6 kN m |
| Mn at Lb = 4 m, Cb = 1.67 | capped at Mp | 341.5 kN m |
| Mn at Lb = 8 m, Cb = 1.0 | F2-2, still <= Lr | 245.7 kN m |
| Cb | uniform 1.000; linear 0 to M 1.667; simple span, uniform load 1.136 | |
| Vn | h/tw 23.1 <= 2.24 sqrt(E/Fy) = 53.9: 0.6 x 345 x (254 x 8.636) x 1.0 | phi Vn = 454 kN |
| H1, Pr 1000 kN, Mrx 100 kN m | 1000/2178 = 0.459 >= 0.2: 0.459 + 8/9 x 100/286.6 | **0.769** (H1-1a) |
| H1, Pr 200, Mrx 150, Mry 20 | 0.092 < 0.2: 0.046 + 150/286.6 + 20/(0.9 x min(345 Zy, 1.6 x 345 Sy)) | 0.708 (H1-1b) |
| H1, Pr 1800, Mrx 60, Mry 10 | | 1.074 (H1-1a, fails) |
| App's own section | sharp corners from nominal d, bf, tf, tw (section-profiles.js:26-54) | A 98.7 %, Iz 99.1 %, ry 100.9 % of the table: close for stiffness; Zx, Sx, J, Cw, rts, ho must come from the table |

## 7. Edges

- **f'c units.** fr is 0.62 sqrt(f'c) with f'c in MPa, 7.5 sqrt(f'c) with f'c in psi; mixing them is
  a factor of 12. The app's stresses are kPa; convert to MPa once, at the check.
- **The app's E versus f'c.** Concrete's card says 32 GPa; with f'c = 30 MPa, ACI gives 25.7 GPa. Use
  one or the other: either derive Ec from f'c (and say so), or keep the card's E and derive nothing
  from it. n = Es/Ec changes with the choice (6.25 against 7.77).
- **lambda for lightweight.** 0.75 and 0.85 multiply fr and every sqrt(f'c) term in Vc; the app has
  no lightweight flag (density 2400 only).
- **Ma at or below 2/3 Mcr.** Ie = Ig exactly; between 2/3 Mcr and Mcr the section is **not yet
  cracked** but 318-19 already reduces Ie (the reduced cracking moment covers restraint and
  shrinkage). Show "uncracked" up to Mcr and the stiffness loss separately, or the map will call
  sound beams cracked.
- **Zero moment.** Ma = 0 gives Ie = Ig, no division by Ma needed (guard Ma > 2/3 Mcr first).
- **Sign of moment.** Hogging moments crack the top face: Mcr is the same for a symmetric
  rectangle, but Icr needs the top steel; with only bottom bars known, negative-moment Icr is unknown.
- **Members in tension.** Steel: H1.2 with the tensile strength (not read here, U). Concrete: axial
  tension lowers the cracking moment (fr - N/A) and Vc (Nu negative in Table 22.5.5.1, Vc >= 0);
  a tie may crack through. The basic Mcr = fr Ig/yt ignores N.
- **Columns.** Concrete columns need a P-M interaction diagram, not this note's beam checks; the app
  must refuse a concrete column ratio until that exists. Cracking of a column can be shown by
  fr - N/A + M yt/I > 0 as an indication only (U for code backing).
- **Very short members, deep beams.** ln/h < 4 is a deep beam in ACI (strut-and-tie, Chapter 23);
  the beam checks do not apply: refuse. For steel, Lb <= Lp gives Mp, Lc/r small gives Fn -> Fy:
  fine.
- **Slender sections.** Steel: flange bf/2tf > 0.38 sqrt(E/Fy) (noncompact, F3) or web > 3.76
  sqrt(E/Fy) (F4/F5), and compression-slender elements (E7): refuse, grey "not checked". HSS, pipe
  and channel shapes in the catalogue need F7, F8, F2 for channels; refuse until done.
- **Size effect.** lambda_s <= 1 and bites only for d > 10 in (254 mm); at d = 1000 mm it is 0.63.
  It applies only without minimum stirrups (equation c). Footings may omit it (13.2.6.2).
- **sqrt(f'c) cap** of 100 psi (8.3 MPa) in Vc above f'c = 69 MPa.
- **phi transition.** eps_t between eps_ty and eps_ty + 0.003 needs the interpolated phi; heavily
  reinforced beams leave 0.90.
- **Cb from the samples.** Needs moments at the quarter points of each unbraced segment, not of the
  member; with Lb unknown, use Cb = 1.0 and the whole member (conservative).
- **Steel E.** The app's Steel card is 210 GPa (Eurocode); AISC uses 200 GPa. The strength checks use
  200 GPa regardless of the card.
- **Units of the solve.** N from `bimFrameAt` is positive in tension (analysis-display.js:202).
- **Which moment is major.** Mz is labelled "major" in the tables; for a column, local y is the type's
  width direction, so a steel column rotated 90 degrees swaps the axes. The check must use the profile's
  axes, not the label.

## 8. What the app already has (file:line)

| Need | Present | Where |
|---|---|---|
| Axial, shear, moments, torsion per member, extremes and 21+ samples per element | Yes: N [min, max], V (resultant), Mz and My with location, T, dmax, drel; samples carry s, N, Mz, My, Vy, d (not Vz, not T) | `src/js/engine/structure/frame-solve.js:246-286`, `bimFrameAt` :221-242 |
| Sign of N | Positive tension | `src/js/engine/structure/analysis-display.js:202` |
| Service combination | D+L (and D, L) beside 1.2D+1.6L and 1.4D | `src/js/engine/standards/registry.js:995-998`; default combo `src/js/engine/structure/analytical-model.js:164` |
| Section properties | A, Iz, Iy, J, zc only, computed from the outline without fillets | `src/js/engine/bim/section-profiles.js:26-54` |
| Shapes | rect, circle, hss, pipe, ibeam, channel | `src/js/engine/bim/section-profiles.js:13-24` |
| Steel catalogue | W8x31 ... W24x76, IPE, C, HSS, Pipe: nominal d, bf, tf, tw only; no Zx, Sx, ry, J (tabulated), Cw, rts, ho, kdes | `src/js/engine/bim/type-instance-params.js:58-70, 93-104` |
| Materials | name, kind, density, youngsModulus, poissonRatio, colour, hatch; **no f'c, fy, Fy, Fu, lambda** | `src/js/engine/core/state.js:27-33` |
| E parsed | '210 GPa' to kPa | `src/js/engine/structure/analytical-model.js:16-21` |
| Member material | own, else type's, else Concrete | `src/js/engine/structure/analytical-model.js:23-30` |
| Section of a member | type profile, else rectangle | `src/js/engine/structure/analytical-model.js:40-44` |
| Structural settings per member | support (columns), ends rigid/pinned (beams) | `src/js/engine/structure/analysis-properties.js:63-67`; `analytical-model.js:62-64` |
| Stiffness | gross E A, E I, G J; no cracked modifiers | `src/js/engine/structure/frame-solve.js:5-16` |
| Reinforcement | none; the Rebar command is listed as not implemented | `src/js/engine/ui/discipline-tabs.js:96` |
| Registry records for the codes | aci318 and aisc360 present but "not read", U | `src/js/engine/standards/registry.js:513-518` |
| Results tables | member forces with tension / compression / shear / moments / deflection / span ratio | `src/js/engine/structure/analysis-properties.js:245` |

**Missing for the checks:** f'c, lambda (or concrete density class) and fy for rebar; reinforcement
(As bottom and top, bar size, cover or d, stirrups Av/s or "none"); Fy (and Fu) for steel; the
tabulated W properties (Zx, Sx, Zy, Sy, rx, ry, J, Cw, rts, ho, bf/2tf, h/tw); per member the
effective length factor K (or Lc) about each axis and the unbraced length Lb for LTB; a "not
checked" result state; and the edition of each code in the registry (records at registry.js:513-518
can be filled from this note at level S).

## 9. Risks and threats to validity

- No primary text of either standard was read; every code value is S. The SI coefficients of Table
  22.5.5.1 are our conversion (U). A transcription error common to secondary sources would pass.
- Open implementations have bugs (efficalc's F2-4 `+`; a 318M-25 slab script's Ma <= Mcr early
  return; libdenavit's 2016 `if` for `elif`, harmless): they corroborate formulas, they do not prove
  them. Our script recomputes everything and agrees with the Manual values we recall (U) for W10x49.
- 318-25's changes are from one practitioner (StructurePoint); the absence of a change to Ie is
  inferred from silence.
- The colour-band defaults of ETABS, RISA and Tekla were not read.
- Linear first-order forces: no P-delta (B1, B2 of Appendix 8 / Chapter C), so the steel H1 ratio
  understates sway and slender columns. Concrete columns' slenderness (6.6.4) not covered.

## 10. Still open (U)

- ACI 318-19 text itself (sold; Berkeley's copy unreachable, 502): Table 24.2.3.5 exact wording,
  Table 22.5.5.1 SI coefficients (0.17, 0.66, 0.42), 9.6.1.2's SI form, 24.3.2's table.
- ACI 318-25: the Vc lower-bound coefficient; whether Table 24.2.3.5 changed (no source says so).
- AISC 360-22 text (aisc.org 403): equation numbers and limits are from implementations and
  comparisons; H1.2 (tension) and the Cb cap; Manual Table 3-2 values for W10x49 (our recall).
- 6.6.3.2.2's 1.4 factor for service-level lateral analysis.
- CSI's default ratio band values; CSI's fr = 4 sqrt(f'c) slab default (wiki refused).
- NDS 2024 (awc.org 403).
- The independent second reader (protocol step 9) has not run.

## 11. The owner's decisions (to ask together with the other three notes)

1. **Reinforcement input:** per type (a beam type carries "3 bars 20 mm bottom, 2 top, cover 40,
   stirrups 10 mm at 200") or per member, or a ratio rho only? Without it only the cracking map
   (option A) is possible.
2. **Concrete strength:** add f'c (and lambda) to the material card, and derive Ec from it
   (changing the solve's stiffness), or keep the card's 32 GPa and use f'c only for checks?
3. **Steel:** add Fy (default 345 MPa for W shapes, A992) and the tabulated AISC properties to the
   catalogue, and use them in the solve as well (they differ by about 1 % from the outline's)?
4. **Unbraced and effective lengths:** defaults Lb = member length, K = 1, Cb = 1 (conservative), with
   per-member override?
5. **Cracked stiffness in the solve:** leave gross (as now), apply Table 6.6.3.1.1(a) modifiers for
   strength runs, or iterate with Ie for service runs?
6. **Colours:** bands and colours (suggest: grey not checked; < 0.5, 0.5-0.9, 0.9-1.0, > 1.0), and
   for cracking: uncracked / between 2/3 Mcr and Mcr / cracked.
7. **Refusals:** confirm the list in section 7 is shown as "not checked: reason".

## 12. References (all read 2026-11-21)

| Source | URL | What was read | Level |
|---|---|---|---|
| ACI 318-19 preview (front matter, contents) | https://concrete.org/Portals/0/Files/PDF/Previews/318-19_preview.pdf | edition, adoption and publication dates, supersedes 318-14, chapter list | P (edition only) |
| ACI news, 318-25 released | https://www.concrete.org/newsandevents/news/newsdetail.aspx?f=51745596 | release 2025-01-22, scope | P |
| ACI 318 portal | https://www.concrete.org/aci318 | 318-25 in inch-pound and SI | P |
| Bischoff (2020), ACI Structural Journal 117(1), abstract | https://www.concrete.org/publications/internationalconcreteabstractsportal/m/details/id/51718072 | 318-19 Ie with a reduced cracking moment | P (abstract) |
| StructurePoint, impact of changes 318-14 to 318-19 (Apr 2019) | https://www.structurepoint.org/pdfs/StructurePoint_Software_Impact_of_changes_from_ACI_318-14_to_ACI-318-19.pdf | 24.2.3.5, R24.2.3.5, 22.5.5.1.1-3, 8.3.1.1, 13.2.6.2 | S |
| StructurePoint, ACI 318-25 code revisions (Feb 2026) | https://www.structurepoint.org/pdfs/ACI-318-25-Code-Revisions-Impact-on-StructurePoint-Software.pdf | all 7 pages | S |
| StructurePoint, cracking coefficient (ACI 19) | https://www.structurepoint.org/publication/pdf/TA-Cracking-Coefficient-and-Effective-Flexural-Stiffness-ACI-19.pdf | Table 6.6.3.1.1(a), (b) | S |
| Laughery et al., ACI Fall 2025 slides | https://www.concrete.org/portals/0/files/pdf/webinars/ws_F25_LucasLaughery.pdf | lambda_s SI form | S |
| S. K. Ghosh, changes 318-14 to 318-19 (ICC) | https://iccsafe.org/wp-content/uploads/An-Overview-of-Changes-from-ACI-318-14-to-ACI-318-19.pdf | one-way shear slides 97-105 | S |
| ideCAD knowledge base (Confluence REST) | https://idecad.atlassian.net/wiki/spaces/IKP/pages/2084700227 and pages 2328264781, 1547764956, 1547764884, 1557692823, 1547732277, 1529447242 | Ie clauses, Table 6.6.3.1.1(a), Vc notation, Es, beta1, phi tables, As,min clauses | S |
| Dlubal KB 001666 | https://www.dlubal.com/en/support-and-learning/support/knowledge-base/001666 | Table 22.5.5.1 (a)-(c), 22.5.5.1.3 | S |
| Bentley RAM, ACI 318-19 notes (wall; foundation) | https://docs.bentley.com/LiveContent/web/RAM%20Structural%20System%20Help%20Complete-v5/en/GUID-A88C2CE4-4308-4B60-A1C8-30846B13CFE5.html ; .../GUID-68ADDBE3-DCE6-4838-8A4D-FC99F6D7EA26.html | Vc (a), (c), limits, lambda_s | S |
| ACI CRC 2020 report (Auburn) | https://eng.auburn.edu/files/centers/hrc/aci-crc2020p0040-final.pdf | Vc (c), lambda_s | S |
| Yau, Lee, Chen (2022), JASE 26(1) | https://jase.tku.edu.tw/jase/wp-content/uploads/2026/04/14_2021_0723_V26i1.pdf | eqs 13-15, 17, 19 | S |
| RISA blog (2021) | https://blog.risa.com/post/why-does-my-slab-deflection-increase-using-aci-318-19 | 318-19 Ie in practice | S |
| calcs.com ACI 318-19 beam docs | https://calcs.com/docs/calculators/us/beams/concreteBeamRectangularUSAACI318-19 | uses Branson's form (counter-evidence) | S |
| edurev concrete formula sheet | https://edurev.in/t/516228/Formula-Sheet-Concrete-Design | Ec, fr, lambda, beta1 | S (low weight) |
| ASPIRE, Control of flexural cracking (2015) | https://aspirebridge.com/magazine/2015Summer/CBT-ControlOfFlexuralCracking.pdf | Frosch 1999, ACI spacing equation, fs = 2/3 fy | S |
| concrete-properties (MIT) | https://raw.githubusercontent.com/robbievanleeuwen/concrete-properties/master/src/concreteproperties/concrete_section.py ; design_codes/as3600.py | cracking moment, cracked properties, 0.6 sqrt(f'c) | P (code) |
| structuralcodes (Apache-2.0) | https://raw.githubusercontent.com/fib-international/structuralcodes/main/structuralcodes/codes/ec2_2004/_section_7_3_crack_control.py ; mc2010/_concrete_material_properties.py | EC2 crack width, fctm | P (code) |
| arisa-chan rc-design-collection-web | https://raw.githubusercontent.com/arisa-chan/rc-design-collection-web/HEAD/aci318m25_slab.py | Ie lines 444-463 | P (code) |
| libdenavit-py (MIT) | https://raw.githubusercontent.com/denavit/libdenavit-py/main/src/libdenavit/section/wide_flange.py ; database/aisc.py (via search) | E3, F2, F6, G2.1, B4.1, 2016 vs 2022; W10x49 | P (code), S (standard) |
| efficalc (MIT) | https://raw.githubusercontent.com/youandvern/efficalc/main/examples/steel_beam_moment_strength.py | F2 equation numbers, B4.1b cases | P (code) |
| xc | https://raw.githubusercontent.com/xcfem/xc/master/python_modules/materials/astm_aisc/ASTM_materials.py | H1-1a/b (method only) | P (code) |
| pondus (AGPL-3.0, method only) | https://raw.githubusercontent.com/Sompote/pondus/main/core/src/steel.rs | Cb F1-1 | P (code) |
| AISC shapes copies | hypar-io/Elements W.csv; NHERI-SimCenter Steel2d.tcl; wcfrobert/fkit AISC.csv (via GitHub code search) | W10x49 row | S |
| SDC Verifier, AISC 360-22 vs 360-10 | https://sdcverifier.com/?p=58183 | Chapters E-H | S |
| ICC, AISC 360-22 public review change list and summary | https://www.iccsafe.org/wp-content/uploads/FS101-21-Humble-AISC_360_2022_Change-List_Section_12_PRONE-DRAFT.pdf ; ...Summary-of-Revisions.pdf | B4.1 text, summary | S |
| UDSS 4th edition updates (Oregon State) | https://web.engr.oregonstate.edu/~liujud/UDSS_4ed_updates.pdf | 360-22 terminology (nominal stress) | S |
| CSI ETABS Output Colors | https://docs.csiamerica.com/help-files/etabs/Menus/Options/Graphics_Colors/Output_Colors.htm | steel ratio colours | P |
| SkyCiv integrated design | https://skyciv.com/docs/skyciv-member-design/general/integrated/ | colours | P |
| Bentley STAAD AD.2006.2.2; RAM Code Check Colors | https://docs.bentley.com/LiveContent/web/STAAD.Pro%20Help-v13/en/GUID-05986488-6CD0-4679-A02F-EA1B912736AC.html ; .../GUID-94E6A0B7-DC3D-4BAB-8B18-7FEAA05E0A33.html | colours | P |
| RISA-3D Results View Settings | https://help.risa.com/risahelp/risa3d/Content/GraphicViewSettings/ResultsViewSettings-Members.htm | colour basis | P |
| PyNite README | https://raw.githubusercontent.com/JWock82/Pynite/main/README.md | scope | P |
| Refused or unreachable | aisc.org (403), xe.berkeley.edu (502), support.tekla.com / help.trimble.com (202, 404), web.wiki.csiamerica.com (202), awc.org (403), concrete.org store (tunnel closed) | - | - |
