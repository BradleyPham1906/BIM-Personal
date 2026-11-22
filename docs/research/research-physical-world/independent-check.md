# Independent check of the four physical-world notes (protocol step 9)

Second reader, 2026-11-21. Notes checked: `loads-wind-gravity.md`, `seismic-dynamics.md`,
`member-checks-cracking.md`, `formfinding-runoff.md`; scripts in
`docs/research/experiments/physical-world/`. Every source below was downloaded again by this reader
into `/tmp/claude-0/dl-check2/` (read as text, never run) or fetched with the fetch tool; nothing was
taken from the first agents' download folders. Numbers were re-derived with fresh code, not by
re-running the notes' arithmetic. Levels as in `research-protocol.md`: P primary, S secondary, U
unverified.

## Result in one line

33 facts checked: **32 CONFIRMED, 0 NOT CONFIRMED, 1 UNREACHABLE** (W7, the Ke exponential's text).
Seven corrections to the notes and one to a script label follow; none changes a number the code
would compute, but one (Exposure D, below) reverses a hypothesis and removes an owner decision.

## The facts

| Id | What was checked | Source read by this reader | Level | Verdict | Note |
|---|---|---|---|---|---|
| W1 | 7-22 q_z = 0.00256 Kz Kzt Ke V^2 (SI 0.613), no Kd; p = q Kd G Cp - qi Kd (GCpi) | ICC, Demystifying Loads Part 2: slide 38 "Kd moved from velocity pressure to wind pressure calculations", Eq. 27.3-1 `p = q Kd GCp - qi Kd (GCpi)`; slide 46 `qz = 0.00256 Kz Kzt Ke V2 (26.10-1)`; Oasis code ("no Kd in qh per Eq. 26.10-1"); ASCE 7-02 6.5.10 and C6.5.10 (0.613 in SI = 1/2 x 1.225 kg/m3) | S (7-22), P (0.613, 7-02) | CONFIRMED | Counter-evidence: SPRI 2023 slide 27 prints "ASCE 7-22: qz = 0.00256 Kz Kzt Ke Kd V^2 x 0.6" (an ASD roofing shorthand; it does not follow the equation). The note should record it. |
| W2 | Kz = 2.41 (z/zg)^(2/alpha), z floored at 15 ft (4.572 m), 2.41 for zg <= z <= 3280 ft; Table 26.11-1 B 7.5/3280 ft, C 9.8/2460 ft, D 11.5/1935 ft | Ghosh (ICC 2023) slides 141-142 (formula with 2.01 struck to 2.41, table old/new); Oasis `computeKz` (`min(max(h, 15), zg)`, same constants). Fit by this reader of Ghosh slides 143-145 (22 rows each of B, C, D, 7-16 and 7-22 columns): every 7-22 column within 0.005 of the 7-22 formula, every 7-16 column within 0.005 of the 7-16 formula | S | CONFIRMED | SI zg 1000 / 750 / 590 m are conversions (3280 ft = 999.7 m, 2460 ft = 749.8 m, 1935 ft = 589.8 m); 7-22's SI table not read. See correction 1 on Exposure D. |
| W3 | Kd 0.85, G 0.85 (rigid), GCpi +/-0.18 enclosed | ICC Part 2 slides 38 and 46 (Kd 0.85, GCpi +/-0.18 in the 7-22 example); Oasis (`KD: 0.85`, enclosed 0.18, partially enclosed 0.55); ASCE 7-02 6.5.8.1 (G 0.85), Fig. 6-5 (+/-0.18, +/-0.55) | S (7-22), P (7-02) | CONFIRMED | |
| W4 | Wall Cp: windward 0.8 with q_z; leeward -0.5 (L/B 0-1), -0.3 (2), -0.2 (>= 4) with q_h, linear interpolation; side -0.7 with q_h | ASCE 7-02 Fig. 6-6 (the "Use With" column; note 2 permits linear interpolation between values of the same sign) | P (7-02), S for 7-22 (no source reports a change) | CONFIRMED | |
| W5 | Case 2: 75 % with MT = 0.75 (PW + PL) B e, e = +/-0.15 B; Case 3 75 % both axes; Case 4 0.563 | ASCE 7-02 Fig. 6-9, text and formulas (`MT = 0.75 (PWX+PLX) BX eX`, `eX = +/-0.15 BX`, `0.563`) | P (7-02) | CONFIRMED | 7-22 figure number 27.3-8 not read. |
| W6 | Worked example 6.1 | Re-derived: Kz 0.8512 / 0.9285 / 1.0086; q 1304.4 / 1422.9 / 1545.6 Pa; F = 137.79, 144.98, 76.21 kN; total 358.99 kN; Case 2 MT 465.04 / 489.31 / 257.23 kN m | own code | CONFIRMED | Leeward uses q_h (-558.4 Pa) at all levels, as 7-02 Fig. 6-6 says. |
| W7 | Ke = exp(-0.000119 zg), zg in m | Conversion right: 0.0000362 / 0.3048 = 0.00011877. The exponential itself: Oasis code only (`e^(-0.0000362 z)`, ft); SPRI slide 28 (7-16 Table 26.9-1 notes: Ke = 1.00 always permitted; Ke "determined using interpolation or from another formula"); Ghosh slide 114 table (7-16) fits the formula within 0.006. A web search found no second copy of the formula's text | S (table, one code) | UNREACHABLE | The formula's wording in 7-22 was not found in any second source. Use Ke = 1.0 (always permitted) or interpolate the table until the note is read. |
| L1 | L = Lo (0.25 + 4.57 / sqrt(KLL AT)), KLL AT >= 37.16 m2; 0.50 Lo one floor, 0.40 Lo two or more; KLL table; > 4.79 kPa not reduced except 20 % for 2+ floors (never below L); garages same; assembly not reduced | Seattle 2021 Building Code ch. 16 (IBC 2021): 1607.12.1, Eq. 16-7 and its SI form, Table 1607.12.1 in full (interior columns 4; exterior columns without cantilever slabs 4; edge columns with cantilever slabs 3; corner columns with cantilever slabs 2; edge beams without cantilever slabs 2; interior beams 2; others 1), 1607.12.1.1-3, Table 1607.1 note a "Live load reduction is not permitted"; ENERCALC 2026 (7-22 Table 4.7-1, KLL 4, 45.131 psf) | P (Seattle), S (7-22) | CONFIRMED | 15 / sqrt(10.764) = 4.572; 400 ft2 = 37.16 m2. NYC 2022 copy: 403 to this reader. |
| L2 | Table 3.1 occupancies | Seattle Table 1607.1, every row the note lists (offices 50; lobbies and first-floor corridors 100; corridors above first floor 80; residential private 40, public 100; attics/sleeping 30; classrooms 40; patient 40 / OR, labs 60; reading 60 / stack 150; assembly 60 / 100; dining 100; retail 100 / 75; storage and manufacturing 125 / 250; garages 40; roofs 20, assembly roofs 100; partitions 15 psf, 1607.5) and 1 psf = 0.04788 kPa | P (Seattle), S (7-22) | CONFIRMED | |
| S1 | Two-period spectrum branches, T0 = 0.2 SD1/SDS, TS = SD1/SDS, TL | FEMA P-2082-1 (2020 NEHRP) Part 1, 11.4.5.2, Eqs. 11.4-3 to 11.4-5; USGS answer at LA (ts 0.479 = 0.70/1.46, t0 0.0958) | P (NEHRP), S (7-22) | CONFIRMED | |
| S2 | Cs forms and bounds; which method is which | Rudra and Ghosh (ICC): 7-22 12.8 "permits two methods": **Method 1** Cs = Sa/(R/Ie) from the multi-period design spectrum, using the peak Sa for T below the peak's period (Eq. 12.8-2); **Method 2** Cs = SDS/(R/Ie), need not exceed SD1/(T R/Ie) for T <= TL, SD1 TL/(T^2 R/Ie) for T > TL (Eq. 12.8-3), "remains permitted", "the standard does not restrict the use of either method"; lower bounds for both: 0.044 SDS Ie >= 0.01, and where S1 >= 0.6, 0.5 S1/(R/Ie). P-2082-1 21.4: mapped S1 in Eq. 12.8-6. FEMA P-2192 ch. 4 example (same forms; writes "S1 > 0.6g") | S | CONFIRMED | The note has it right: Method 2 is the 7-16 form kept, with SDS and SD1 redefined by 21.4; Method 1 is new. Neither is required over the other where the multi-period spectrum exists. |
| S3 | Ta = Ct hn^x; Ct/x; SI Ct; Cu table | P-2192 (cites 7-22 Table 12.8-2): steel MRF 0.028 / 0.8, all other 0.02 / 0.75, EBF/BRBF 0.03 / 0.75; IISEE table 5 (older ASCE 7): 0.028/0.8, 0.016/0.9, 0.030/0.75, 0.020/0.75; IISEE table 4 Cu: >= 0.4 1.4, 0.3 1.4, 0.2 1.5, 0.15 1.6, 0.1 1.7, <= 0.05 1.7; P-2192 Cu 1.4 at SD1 0.65 citing 7-22 Table 12.8-1. SI: 0.028 x 3.28084^0.8 = 0.0724, 0.016 x 3.28084^0.9 = 0.0466, 0.030 x 3.28084^0.75 = 0.0731, 0.020 x 3.28084^0.75 = 0.0488 | S | CONFIRMED | Concrete MRF 0.016 / 0.9 was re-read only in IISEE (older edition); the ICC/SEAOC sample the note cites was not re-read. IISEE's metric column (0.068, 0.044, 0.070, 0.055) is not the conversion: do not use, as the note says. |
| S4 | k = 1 (T <= 0.5), 2 (T >= 2.5), linear between; Cvx = wx hx^k / sum | P-2192 ch. 6, quoting 7-22 12.8.3 and Eq. 12.8-12 (Cvx) | S | CONFIRMED | Re-derived the note's E2 table (k 1.0491, Fx 476.4 / 352.3 / 230.2 / 111.3 kN). |
| S5 | Steel SMF R 8, Cd 5.5, Omega0 3; Ie 1.0 / 1.25 / 1.5 | ATC 154 steel SMF archetype report (AISC Steel Solutions Center, designed to ASCE 7-22): "R = 8, Omega_o = 3, Cd = 5.5"; P-2192 (R 8.0, Omega0 3.0 citing 7-22 Table 12.2-1; Ie 1.0 RC II, 1.25 RC III, 1.5 cited to 7-22 Table 1.5-2) | S | CONFIRMED | Cd 5.5, U in the note, is now S (two sources: ATC 154 report and the search-pointed calculator; one read). |
| S6 | Table 12.12-1 values; Delta = Cd delta / Ie | P-2082-1 Part 1 Table 12.12-1 (0.025/0.020/0.015; 0.010; 0.007; 0.020/0.015/0.010 hsx; note b, moment frames SDC D-F to 12.12.1.1) and 12.8.6; ATC 154 report (allowable elastic drift = 0.02 Ie / Cd) | P (NEHRP), S (7-22) | CONFIRMED | |
| S7 | MRSA forces scaled to 100 % of ELF V | P-2082-1 Part 2 C12.9.1.4.1 ("scaling to 100% of the ELF base shear", against the former 15 % reduction); ATC 154 report ("after scaling") | S | CONFIRMED | 7-22's 12.9.1.4.1 text itself not read. |
| S8 | CQC rho with r = wj/wi | OpenSeesPy example `CQC()` (general unequal-damping form, as in the note); arithmetic: rho(0.9, 5 %) = 0.4730 recomputed | S | CONFIRMED | The OpenSeesPy call passes eigenvalues (w^2) as `lambdas`: confirmed, the note's counter-evidence holds. Der Kiureghian 1981 not re-read. |
| S9 | Newmark average acceleration (Chopra Table 5.4.2 form) and Rayleigh a0, a1 | OpenSees `Newmark.cpp` (c2 = gamma/(beta dt), c3 = 1/(beta dt^2), a1 = 1 - gamma/beta, a2 = dt (1 - gamma/(2 beta)), a3 = -1/(beta dt), a4 = 1 - 1/(2 beta)): the same recurrences in total form; Rayleigh solved by hand from zeta_n = a0/(2 wn) + a1 wn/2 at wi, wj | P (code), algebra | CONFIRMED | Chopra's book: UNREACHABLE here; the table values in the note remain the script's. |
| S10 | USGS service fields, 200-with-error, CORS | Tested now (curl, through the proxy): LA lat 34 lon -118 C II: ss 2.15, s1 0.75, sds 1.46, sd1 0.7, tl 8, ts 0.479, t0 0.0958, sdc D; ACAO `*` on a miss with Origin; lat 30 lon -140: HTTP 200, `request.status: "error"`, "Location [-140, 30] out of bounds"; OPTIONS 405; same URL first without Origin (miss) then with Origin: `Hit from cloudfront` and **no** ACAO | P (tested) | CONFIRMED | The unique `title` per request is necessary. |
| M1 | fr = 0.62 lambda sqrt(f'c), Ec = 4700 sqrt(f'c), Mcr = fr Ig / yt | StructurePoint 318-14 to 318-19 (quotes 24.2.3.5 Mcr = fr Ig / yt); concretedesignpy `serviceability.py` (cites 19.2.2.1(b) p. 394, 19.2.3.1 p. 395, Eq. 24.2.3.5 p. 499); edurev sheet (both unit forms) | S | CONFIRMED | ACI text unreachable (xe.berkeley.edu 502 again). |
| M2 | 318-19 Ie = Icr / (1 - ((2/3) Mcr/Ma)^2 (1 - Icr/Ig)) for Ma > 2/3 Mcr, else Ig | StructurePoint (R24.2.3.5: Bischoff and Scanlon adopted, Branson removed); concretedesignpy (Table 24.2.3.5, p. 499); SAEngine `deflection.py`; davidhansonc notebooks; RISA blog (Ie depends on Ma against 2/3 Mcr) | S | CONFIRMED | Counter: Bentley RAM Concept's page prints a fourth-power Bischoff form (search digest only) and stabileo's CIRSOC version omits 2/3; neither is ACI 318-19. |
| M3 | Singly reinforced cracked section: b (kd)^2/2 = n As (d - kd); Icr = b (kd)^3/3 + n As (d - kd)^2 | concretedesignpy `icr()` (same, plus compression steel term); equilibrium of the transformed section; recomputed kd 125.77 mm, Icr 9.683e8 mm4 | S | CONFIRMED | Yau et al. (jase.tku.edu.tw): connection reset this time. |
| M4 | beta1 0.85 (f'c <= 28), -0.05 per 7 MPa, min 0.65; phi Mn = 0.9 As fy (d - a/2) | libdenavit `ACI_strain_compatibility.py` (SI branch of 318-19 Table 22.2.2.4.3, exactly as stated); edurev (phi 0.90 tension-controlled); a = As fy/(0.85 f'c b) | S | CONFIRMED | 0.9 only when eps_t >= eps_ty + 0.003 (318-19); the note says so. |
| M5 | AISC 360-22 E3: Fn = 0.658^(Fy/Fe) Fy for Lc/r <= 4.71 sqrt(E/Fy) (Fy/Fe <= 2.25), else 0.877 Fe; phi 0.90 | libdenavit `wide_flange.py` (2016 and 2022 classes, `Fy/Fe <= 2.25`, phi 0.9) | S | CONFIRMED | aisc.org 403 again. |
| M6 | H1-1a/b | xc `ASTM_materials.py` (ratioN >= 0.2: N + 8/9 (Mz + My); else N/2 + (Mz + My)) in three places | S | CONFIRMED | |
| M7 | F2: Lp = 1.76 ry sqrt(E/Fy); Lr = 1.95 rts (E/0.7Fy) sqrt(Jc/(Sx ho) + sqrt((Jc/(Sx ho))^2 + 6.76 (0.7 Fy/E)^2)); F2-2 | libdenavit (both lines verbatim, phi 0.9) | S | CONFIRMED | W10x49 recomputed: Lp 2734 mm (8.97 ft), Lr 9631 mm (31.6 ft). |
| M8 | Worked numbers, section 6 | Re-derived independently: Ec 25 743, fr 3.3959, Mcr 42.45 kN m, n 7.769, kd 125.77, Icr 9.683e8, beta1 0.8357, a 51.72, c 61.88, eps_t 0.0188, Mn 167.81, phi Mn 151.03, As,min 450; Ie(60) 1.1439e9, Ie(120) 1.0070e9 (Branson 1.732e9, 1.064e9); Vc(c) 78.8 kN; W10x49: Fe 513.5, Fn 260.4, phi Pn 2178, Mp 341.5, Mn(4 m) 318.5, phi Mn 286.6, Mn(8 m) 245.7, phi Vn 454, H1 0.769 / 0.708 / 1.074 | own code | CONFIRMED | The psi-form Vc 79.7 kN differs from 78.8 mainly because lambda_s with d in inches is 0.8495 against 0.8452 with d in mm (see correction 6). |
| F1 | FDM: (Ci^T Q Ci) x = p_free - Ci^T Q Cf x_fixed per axis | compas_fd `fd_numerical_data.py` lines 74-82 (`Ai = Ci.T Q Ci`, `Af = Ci.T Q Cf`), `fd_numpy.py` lines 76-79 (`b = p[free] - Af.dot(xyz[fixed])`, `spsolve`); jax_fdm `models.py` (`c_free.T @ (q * c_free)`) | P (code), S (Schek 1974 refused) | CONFIRMED | |
| F2 | Barnes fictitious mass m_i = lam dt^2/2 k_i (dt = 1), largest term for membranes; kinetic damping | Rodriguez et al. 2011 eqs. 4-5 (as stated); compas 1.17.10 `dr.py` (M = sum 0.5 dt^2 q; viscous A = (1 - c/2)/(1 + c/2), B = (1 + A)/2, c 0.1, tol1 1e-3, tol2 1e-6); Oasys GSA 10.2 theory (kinetic energy watched; at the peak, motion stopped, nodes repositioned to the maximum, restarted at zero velocity; parabolic peak estimate) | S, P (code) | CONFIRMED | Oasys does state a mass rule ("2 x sum of translational stiffness of the elements connected"): see correction 7. The position correction formula itself stays U (Barnes 1999 not read). |
| F3 | D8 with sqrt(dx^2 + dy^2) for diagonals; Priority-Flood+epsilon | Whitebox `d8_pointer.rs` 233-295 (`diag_cell_size`, steepest positive slope, else 0); arXiv 1511.04463 (Barnes, Lehman, Mulla, Computers & Geosciences 62, 2014), Algorithm 3 with NextAfter | P | CONFIRMED | |
| F4 | Q = C i A / 360 SI; Table 4.1; 80 ha | HEC-22 4th ed. FHWA-HIF-24-006 (Feb 2024), Kentucky copy: Eq. 4.1 (Ku 1.0 CU, 360 SI), p. 23 "smaller than 200 ac (80 ha)" (HDS-2), Table 4.1 p. 26 (every value the note lists matches) | P | CONFIRMED | Example 4.3 prints 19.3 and 31.4 ft3/s (seen). |
| F5 | Kirpich SI | TxDOT HDM ch. 4 s. 11: K 0.0078 (ft) / 0.0195 (m), t in min, S dimensionless, Kerby-Kirpich 0.25 to 150 mi2, +0.0005 below S 0.002 (page text); the equation image of the worked example reads `t_ch = 0.0078 (5,280 - 500)^0.770 (0.0095)^-0.385` | P | CONFIRMED | 0.0078 x 3.28084^0.77 = 0.01948. |
| F6 | NOAA PFDS keyless, no CORS | Tested now: `hdsc.nws.noaa.gov/cgi-bin/new/fe_text_mean.csv` Philadelphia, english intensity PDS: 200, `text/html` with `Content-Disposition: attachment`, NOAA Atlas 14 Volume 2 Version 3, 10-yr 5-min 6.47, 10-min 5.17 in/h; no Access-Control-Allow-Origin with an Origin header; OPTIONS 500 | P (tested) | CONFIRMED | |

## Scripts, re-run here (`python3 -I`, Python 3, this container, 2026-11-21)

| Script | Exit | Asserts | Result |
|---|---|---|---|
| `wind_loads.py` | 0 | 13 | "All checks passed"; example forces as in W6 |
| `e02_gravity.py` | 0 | 0 | prints only (no checks to pass) |
| `seismic.py` | 0 | 10 | all pass; E2 V 1170.2 kN (Method 2), 1043.9 kN (Method 1); Newmark table as in the note |
| `member_checks.py` | 0 | 5 | "all asserts passed" |
| `formfinding.py` | 0 | 2 | pass; centre -9/8, kinetic DR 81 / 62 iterations |
| `runoff.py` | 0 | 1 | pass; Q 0.3333 m3/s; timings this run 111 / 96 / 21 ms (they vary by run) |
| `e01_eigen_speed.mjs` (node 22) | 0 | none | runs; Jacobi relative errors 4e-15 to 9e-12 |

## Corrections the notes need

1. **loads-wind-gravity.md, H7, 4.1 check 1, section 7 (Exposure D), section 9, 10.1, 11.2.** Ghosh's
   deck (slide 145) gives Exposure D old and new columns; the new column matches the 7-22 formula
   (2.41, 1935 ft, alpha 11.5) to rounding in all 22 rows (1.04 at 0-15 ft, 1.44 at 100 ft, 1.90 at
   500 ft), and the old column the 7-16 formula. ICC Part 2 slide 41's D column (1.03, 1.43, 1.89)
   is simply the 7-16 column left unchanged. So H7 **holds** (S), the tabulated 7-22 D values equal
   the formula, and owner decision 2 is no longer needed.
2. **loads-wind-gravity.md 3.5 (Ke).** The exponential stays a single implementation's (Oasis) plus a
   7-16 table fit: level U for the formula, not S; code should use Ke = 1.0 or table interpolation
   until the 7-22 note is read. Add SPRI slide 28 ("interpolation or another formula").
3. **loads-wind-gravity.md 3.5 counter-evidence.** Record SPRI 2023 slide 27, which still writes 7-22
   q_z with Kd (an ASD roofing shorthand), against the ICC deck's marked code change.
4. **seismic-dynamics.md 4.1 and 4.2.** Steel SMF Cd 5.5 moves from U to S (ATC 154 steel SMF report,
   AISC Steel Solutions Center, to ASCE 7-22: R 8, Omega0 3, Cd 5.5).
5. **seismic-dynamics.md H2 and 4.1 (equation numbers).** P-2192 cites Ta as "ASCE/SEI 7-22 Eq.
   12.8-7" and Cvx as "Eq. 12.8-12"; the note gives Ta 12.8-8, Fx 12.8-12, Cvx 12.8-13. Rudra and
   Ghosh number Method 1 12.8-2 and Method 2 12.8-3. Equation numbers are not settled: keep them out
   of labels and the registry (U) until 7-22's text is read.
6. **member-checks-cracking.md 6(a), Vc row.** Say why the psi form gives 79.7 kN against 78.8: with d
   in inches lambda_s = sqrt(2/(1 + 17.72/10)) = 0.8495, against 0.8452 by the SI form with d in mm; the
   0.66 against 8/12.04 rounding adds little. The two lambda_s forms are not exact conversions.
   Script label: `member_checks.py` prints "Lb = 8 m, Cb = 1.0 (elastic LTB)", but 8 m < Lr = 9.63 m,
   so it is inelastic LTB by F2-2 (the note's table says F2-2 correctly).
7. **formfinding-runoff.md A.2.** Oasys GSA does state its mass rule: "Fictitious mass of a node =
   2 x sum of translational stiffness of the elements connected to the node" (its own time step
   convention), not "no formula". It is a different scaling from Barnes's lam dt^2/2 k with dt = 1;
   record both. The position-correction formula stays U as the note says.

## Not re-checked here (outside the list, or refused)

ASCE 7-22, ACI 318-19 and AISC 360-22 texts (sold, or aisc.org 403, xe.berkeley.edu 502); Chopra's
book; Der Kiureghian 1981; Schek 1974; Barnes 1999; NYC 2022 code (403 to this reader); Yau et al.
(connection reset). Facts resting only on them keep the levels shown above.

## Sources read by this reader (2026-11-21)

ASCE 7-02 (law.resource.org CFR copy); ICC Demystifying Loads Parts 1 and 2 (iccsafe.org); Ghosh,
Ever-changing Structural Provisions - Wind (iccsafe.org); SPRI 2023 Chamberlain deck; Oasis ASCE 7-22
calculator `index.html` (raw.githubusercontent.com); anvilate `building_loads.py`; Seattle 2021
Building Code ch. 16; ENERCALC LLR example 2026; FEMA P-2082-1 (nibs.org); FEMA P-2192-V1 (nibs.org);
Rudra and Ghosh, Method 2 versus Method 1 (iccsafe.org); IISEE ASCE 7 tables 3-5; NIST GCR 16-917-41;
ATC 154 steel SMF High D archetype report (femap2343.atcouncil.org, via the fetch tool); USGS
`ws/building-codes/asce7-22/calculate` (tested); OpenSeesPy response spectrum example; OpenSees
`Newmark.cpp`; StructurePoint 318-14 to 318-19 changes; concretedesignpy `serviceability.py`; GitHub
code search results for the Bischoff form (SAEngine, davidhansonc, stabileo); RISA blog and Bischoff
2020 abstract (fetch tool digests); edurev formula sheet; libdenavit-py `wide_flange.py` and
`ACI_strain_compatibility.py`; xc `ASTM_materials.py`; compas_fd `fd_numpy.py`,
`fd_numerical_data.py`; jax_fdm `models.py`; compas 1.17.10 `dr.py`; Rodriguez et al. 2011 preprint;
Oasys GSA 10.2 dynamic relaxation page (fetch digest); Whitebox `d8_pointer.rs`; arXiv 1511.04463;
HEC-22 4th ed. (Kentucky copy); TxDOT HDM ch. 4 s. 11 page and its equation images; NOAA PFDS CSV
(tested).
